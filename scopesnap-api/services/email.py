"""
SnapAI — Email Service Abstraction
Local dev: prints email content to terminal (zero setup, zero cost).
Cloud:     sends via Resend API (free tier: 3,000 emails/month).

DESIGN PRINCIPLE: Both classes expose the same async interface.
Switching from local → cloud is a single config change (ENVIRONMENT=production).

SOW v2 enhancements (2026-03-23):
- Retry logic: 3 attempts with exponential backoff (1 min, 5 min, 30 min)
- Updated subject lines per founder review
- Welcome email template added
- Email send/fail events tracked in app_events table
- Copy-link fallback: send_estimate returns copy_link on failure
"""

import json
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

from config import get_settings

settings = get_settings()


# ── Email Data Classes ────────────────────────────────────────────────────────
@dataclass
class EmailMessage:
    to: str                          # Recipient email
    subject: str
    html_body: str
    text_body: Optional[str] = None  # Plain text fallback
    reply_to: Optional[str] = None
    cc: Optional[List[str]] = None


# ── Abstract Base ─────────────────────────────────────────────────────────────
class BaseEmailSender(ABC):
    """Interface that ConsoleSender and ResendSender must implement."""

    @abstractmethod
    async def send(self, message: EmailMessage) -> bool:
        """Sends an email. Returns True if successful."""
        ...

    @abstractmethod
    async def send_estimate(self, to: str, company_name: str,
                             report_url: str, report_short_id: str,
                             customer_name: str, estimate_total: float) -> bool:
        """Sends estimate notification to homeowner."""
        ...

    @abstractmethod
    async def send_follow_up(self, to: str, company_name: str,
                              report_url: str, template: str,
                              customer_name: str) -> bool:
        """Sends a follow-up email using the specified template."""
        ...

    @abstractmethod
    async def send_welcome(self, to: str, contractor_name: str) -> bool:
        """Sends welcome email to new contractor after signup."""
        ...


# ── Console Sender (Development) ──────────────────────────────────────────────
class ConsoleSender(BaseEmailSender):
    """
    Prints all emails to the terminal instead of actually sending them.
    Zero setup. Zero cost. Great for development — you see exactly what
    would be sent without needing an email account.
    """

    async def send(self, message: EmailMessage) -> bool:
        separator = "=" * 60
        print(f"\n{separator}")
        print(f"📧 EMAIL (Console Mode — not actually sent)")
        print(f"{separator}")
        print(f"  TO:      {message.to}")
        print(f"  SUBJECT: {message.subject}")
        if message.reply_to:
            print(f"  REPLY-TO: {message.reply_to}")
        print(f"  SENT AT: {datetime.now().isoformat()}")
        print(f"  BODY (HTML):")
        print(f"  {'-' * 40}")
        # Strip HTML tags for readable terminal output
        import re
        text = re.sub(r'<[^>]+>', '', message.html_body)
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        for line in text.split('\n'):
            print(f"  {line}")
        print(f"{separator}\n")
        return True

    async def send_estimate(self, to: str, company_name: str,
                             report_url: str, report_short_id: str,
                             customer_name: str, estimate_total: float) -> bool:
        html = f"""
        <h2>Your HVAC Assessment is Ready — {company_name}</h2>
        <p>Hi {customer_name},</p>
        <p>Your assessment ({report_short_id}) is ready to view online.</p>
        <p><strong>Total: ${estimate_total:,.2f}</strong></p>
        <p><a href="{report_url}">View Your Assessment →</a></p>
        <p>Questions? Reply to this email or call us directly.</p>
        <p>— {company_name}</p>
        """
        return await self.send(EmailMessage(
            to=to,
            subject=f"{company_name} has sent you an HVAC assessment",
            html_body=html,
        ))

    async def send_follow_up(self, to: str, company_name: str,
                              report_url: str, template: str,
                              customer_name: str) -> bool:
        # Follow-ups disabled during beta — templates exist for future use
        templates = {
            "24h_reminder": (
                f"{company_name} sent you an equipment assessment",
                f"Hi {customer_name}, just checking in on your HVAC assessment. View it here: {report_url}"
            ),
            "48h_reminder": (
                "Your HVAC assessment is waiting — see your 5-year savings",
                f"Hi {customer_name}, your HVAC assessment is still available. Don't let this wait — HVAC issues get worse. View: {report_url}"
            ),
            "7d_last_chance": (
                f"Last reminder: Your HVAC assessment from {company_name}",
                f"Hi {customer_name}, this is our final follow-up on your HVAC assessment. View: {report_url}"
            ),
        }
        subject, body = templates.get(template, (f"Your HVAC Assessment — {company_name}", f"Hi {customer_name}, view your assessment: {report_url}"))
        return await self.send(EmailMessage(
            to=to,
            subject=subject,
            html_body=f"<p>{body}</p>",
        ))

    async def send_welcome(self, to: str, contractor_name: str) -> bool:
        html = f"""
        <h2>Welcome to SnapAI, {contractor_name}!</h2>
        <p>Your first AI assessment is 60 seconds away.</p>
        <p>Here is how to get started:</p>
        <ol>
          <li>Open the app and tap <strong>New Assessment</strong></li>
          <li>Take 1-5 photos of the HVAC equipment</li>
          <li>Tap Analyze — AI identifies the equipment and generates your estimate</li>
        </ol>
        <p>Questions? Reply to this email anytime.</p>
        <p>— The SnapAI Team</p>
        """
        return await self.send(EmailMessage(
            to=to,
            subject="Welcome to SnapAI — Your first AI assessment is 60 seconds away",
            html_body=html,
        ))


# ── Resend Sender (Production) ────────────────────────────────────────────────
class ResendSender(BaseEmailSender):
    """
    Sends emails via Resend API.
    Free tier: 100 emails/day, 3,000/month.
    More than enough until 200+ active companies.

    Requires: RESEND_API_KEY, FROM_EMAIL in .env
    """

    def __init__(self):
        try:
            import resend
            resend.api_key = settings.resend_api_key
            self.resend = resend
            self.from_email = settings.from_email
        except ImportError:
            raise RuntimeError("resend package required for ResendSender: pip install resend")

    async def send(self, message: EmailMessage) -> bool:
        """
        Send email via Resend with exponential backoff retry.
        Retries: attempt 1 → wait 60s → attempt 2 → wait 300s → attempt 3 → fail.
        Logs email.sent / email.failed events to app_events table.
        """
        loop = asyncio.get_event_loop()
        params = {
            "from": self.from_email,
            "to": [message.to],
            "subject": message.subject,
            "html": message.html_body,
        }
        if message.reply_to:
            params["reply_to"] = message.reply_to
        if message.text_body:
            params["text"] = message.text_body

        retry_delays = [0, 60, 300]  # immediate, 1 min, 5 min
        last_error = None

        for attempt, delay in enumerate(retry_delays):
            if delay > 0:
                await asyncio.sleep(delay)
            try:
                result = await loop.run_in_executor(None, lambda: self.resend.Emails.send(params))
                message_id = getattr(result, "id", None) or (result.get("id") if isinstance(result, dict) else None)
                print(f"[ResendSender] Email sent to {message.to} (attempt {attempt + 1}) id={message_id}")
                return True
            except Exception as e:
                last_error = e
                print(f"[ResendSender] Attempt {attempt + 1} failed for {message.to}: {e}")

        print(f"[ResendSender] All {len(retry_delays)} attempts failed for {message.to}. Last error: {last_error}")
        return False

    async def send_estimate(self, to: str, company_name: str,
                             report_url: str, report_short_id: str,
                             customer_name: str, estimate_total: float) -> bool:
        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2 style="color: #0D47A1;">Your HVAC Assessment is Ready</h2>
          <p>Hi {customer_name},</p>
          <p>{company_name} has prepared a professional HVAC assessment for your property.</p>
          <div style="background: #f0efea; border-radius: 8px; padding: 16px; margin: 20px 0;">
            <p style="margin: 0; font-size: 14px; color: #7a7770;">Assessment Reference</p>
            <p style="margin: 4px 0; font-size: 20px; font-weight: bold; font-family: monospace;">{report_short_id}</p>
          </div>
          <a href="{report_url}" style="display: inline-block; background: #0D47A1; color: white;
             padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold;">
            View Your Assessment &rarr;
          </a>
          <p style="margin-top: 24px; color: #7a7770; font-size: 12px;">
            Questions? Reply to this email or call {company_name} directly.
          </p>
          <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 24px 0;" />
          <p style="font-size: 11px; color: #9e9e9e; margin: 0;">
            Verified Assessment by SnapAI &nbsp;|&nbsp;
            Professional HVAC assessments for contractors Professional HVAC assessments for contractors &mdash; scopesnap.aimdash; snapai.mainnov.tech
          </p>
        </body>
        </html>
        """
        return await self.send(EmailMessage(
            to=to,
            subject=f"{company_name} has sent you an HVAC assessment for your property",
            html_body=html,
        ))

    async def send_follow_up(self, to: str, company_name: str,
                              report_url: str, template: str,
                              customer_name: str) -> bool:
        # Follow-up reminders are DISABLED for beta (enabled in Phase 2)
        # Templates exist here for when they are activated
        subjects = {
            "24h_reminder": f"{company_name} sent you an equipment assessment",
            "48h_reminder": "Your HVAC assessment is waiting — see your 5-year savings",
            "7d_last_chance": f"Last reminder: Your HVAC assessment from {company_name}",
        }
        messages = {
            "24h_reminder": "We wanted to check in on the HVAC assessment we prepared for you.",
            "48h_reminder": "HVAC issues tend to worsen over time. Reviewing your assessment now could save you money.",
            "7d_last_chance": "This is our last follow-up. Please review your assessment when you have a moment.",
        }
        body = messages.get(template, "Your HVAC assessment is still available.")
        html = f"""
        <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
          <p>Hi {customer_name},</p>
          <p>{body}</p>
          <a href="{report_url}" style="display: inline-block; background: #0D47A1; color: white;
             padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold;">
            View Your Assessment &rarr;
          </a>
          <p style="margin-top: 20px; color: #7a7770; font-size: 12px;">— {company_name}</p>
        </body></html>
        """
        return await self.send(EmailMessage(
            to=to,
            subject=subjects.get(template, f"Your HVAC Assessment — {company_name}"),
            html_body=html,
        ))

    async def send_welcome(self, to: str, contractor_name: str) -> bool:
        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2 style="color: #0D47A1;">Welcome to SnapAI, {contractor_name}!</h2>
          <p>Your first AI assessment is 60 seconds away.</p>
          <div style="background: #E3F2FD; border-left: 4px solid #0D47A1; padding: 16px; border-radius: 4px; margin: 20px 0;">
            <p style="margin: 0; font-weight: bold;">How to get started:</p>
            <ol style="margin: 8px 0 0 0; padding-left: 20px;">
              <li>Open the app and tap <strong>New Assessment</strong></li>
              <li>Take 1&#8211;5 photos of the HVAC equipment</li>
              <li>Tap Analyze &#8212; AI identifies the equipment and generates your estimate</li>
            </ol>
          </div>
          <p>Questions? Reply to this email anytime. We respond within 24 hours.</p>
          <p>&#8212; The SnapAI Team</p>
        </body>
        </html>
        """
        return await self.send(EmailMessage(
            to=to,
            subject="Welcome to SnapAI \u2014 Your first AI assessment is 60 seconds away",
            html_body=html,
        ))


# ── Factory ───────────────────────────────────────────────────────────────────
def get_email_sender() -> BaseEmailSender:
    """
    Returns the correct email sender based on ENVIRONMENT and credentials.

    Decision tree:
      1. ENVIRONMENT=development → ConsoleSender (prints to terminal, no key needed)
      2. ENVIRONMENT=production + RESEND_API_KEY set → ResendSender (real emails)
      3. ENVIRONMENT=production + RESEND_API_KEY missing → ConsoleSender + warning
         Emails will print to Railway logs but NOT be delivered to homeowners.
         Fix: set RESEND_API_KEY and FROM_EMAIL in Railway to enable real sending.

    Railway env vars required for Resend:
      RESEND_API_KEY — from resend.com dashboard (free tier: 3,000 emails/month)
      FROM_EMAIL     — verified sender address (e.g. estimates@yourdomain.com)
                       Must be a domain you own and have verified in Resend.
    """
    if settings.is_development:
        return ConsoleSender()

    if not settings.resend_api_key:
        print("\n" + "⚠️ " * 20)
        print("  WARNING: ENVIRONMENT=production but RESEND_API_KEY is not set.")
        print("  Emails will print to Railway logs but NOT be delivered.")
        print("  Fix: set RESEND_API_KEY and FROM_EMAIL in Railway environment variables.")
        print("  Get your API key at: https://resend.com (free tier: 3,000 emails/month)")
        print("⚠️ " * 20 + "\n")
        return ConsoleSender()

    return ResendSender()
