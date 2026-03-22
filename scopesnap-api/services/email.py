"""
ScopeSnap — Email Service Abstraction
Local dev: prints email content to terminal (zero setup, zero cost).
Cloud:     sends via Resend API (free tier: 100 emails/day).

DESIGN PRINCIPLE: Both classes expose the same async interface.
Switching from local → cloud is a single config change (ENVIRONMENT=production).
"""

import json
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
        <h2>Your HVAC Estimate is Ready — {company_name}</h2>
        <p>Hi {customer_name},</p>
        <p>Your estimate ({report_short_id}) is ready to view online.</p>
        <p><strong>Total: ${estimate_total:,.2f}</strong></p>
        <p><a href="{report_url}">View Your Estimate →</a></p>
        <p>Questions? Reply to this email or call us directly.</p>
        <p>— {company_name}</p>
        """
        return await self.send(EmailMessage(
            to=to,
            subject=f"Your HVAC Estimate from {company_name} ({report_short_id})",
            html_body=html,
        ))

    async def send_follow_up(self, to: str, company_name: str,
                              report_url: str, template: str,
                              customer_name: str) -> bool:
        templates = {
            "24h_reminder": f"Hi {customer_name}, just checking in on your HVAC estimate. View it here: {report_url}",
            "48h_reminder": f"Hi {customer_name}, your HVAC estimate is still available. Don't let this wait — HVAC issues get worse. View: {report_url}",
            "7d_last_chance": f"Hi {customer_name}, this is our final follow-up on your HVAC estimate. The estimate expires soon. View: {report_url}",
        }
        body = templates.get(template, f"Hi {customer_name}, view your estimate: {report_url}")
        return await self.send(EmailMessage(
            to=to,
            subject=f"Your HVAC Estimate — {company_name}",
            html_body=f"<p>{body}</p>",
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
        import asyncio
        loop = asyncio.get_event_loop()
        try:
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

            await loop.run_in_executor(None, lambda: self.resend.Emails.send(params))
            return True
        except Exception as e:
            print(f"[ResendSender] Failed to send email to {message.to}: {e}")
            return False

    async def send_estimate(self, to: str, company_name: str,
                             report_url: str, report_short_id: str,
                             customer_name: str, estimate_total: float) -> bool:
        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2 style="color: #1a8754;">Your HVAC Estimate is Ready</h2>
          <p>Hi {customer_name},</p>
          <p>{company_name} has prepared an HVAC estimate for your property.</p>
          <div style="background: #f0efea; border-radius: 8px; padding: 16px; margin: 20px 0;">
            <p style="margin: 0; font-size: 14px; color: #7a7770;">Estimate Reference</p>
            <p style="margin: 4px 0; font-size: 20px; font-weight: bold; font-family: monospace;">{report_short_id}</p>
          </div>
          <a href="{report_url}" style="display: inline-block; background: #1a8754; color: white;
             padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold;">
            View Your Estimate →
          </a>
          <p style="margin-top: 24px; color: #7a7770; font-size: 12px;">
            Questions? Reply to this email or call {company_name} directly.
          </p>
        </body>
        </html>
        """
        return await self.send(EmailMessage(
            to=to,
            subject=f"Your HVAC Estimate from {company_name} ({report_short_id})",
            html_body=html,
        ))

    async def send_follow_up(self, to: str, company_name: str,
                              report_url: str, template: str,
                              customer_name: str) -> bool:
        subjects = {
            "24h_reminder": f"Following up on your HVAC estimate — {company_name}",
            "48h_reminder": f"Don't let HVAC issues wait — {company_name}",
            "7d_last_chance": f"Final notice: Your estimate expires soon — {company_name}",
        }
        messages = {
            "24h_reminder": "We wanted to check in on the HVAC estimate we prepared for you yesterday.",
            "48h_reminder": "HVAC issues tend to worsen over time. We'd hate for a small problem to become a big one.",
            "7d_last_chance": "This is our last follow-up. Your estimate will expire, and pricing may change.",
        }
        body = messages.get(template, "Your HVAC estimate is still available.")
        html = f"""
        <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
          <p>Hi {customer_name},</p>
          <p>{body}</p>
          <a href="{report_url}" style="display: inline-block; background: #1a8754; color: white;
             padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold;">
            View Your Estimate →
          </a>
          <p style="margin-top: 20px; color: #7a7770; font-size: 12px;">— {company_name}</p>
        </body></html>
        """
        return await self.send(EmailMessage(
            to=to,
            subject=subjects.get(template, f"Your HVAC Estimate — {company_name}"),
            html_body=html,
        ))


# ── Factory ───────────────────────────────────────────────────────────────────
def get_email_sender() -> BaseEmailSender:
    """
    Returns the correct email sender based on ENVIRONMENT.
    Use as FastAPI dependency or call directly.
    """
    if settings.is_development:
        return ConsoleSender()
    else:
        return ResendSender()
