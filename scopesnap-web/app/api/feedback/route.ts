/**
 * POST /api/feedback
 * BUG-01 fix: Receives in-app feedback form submissions and forwards them
 * via Resend email to ds.shoab@gmail.com — no client mail app required.
 */

import { NextRequest, NextResponse } from "next/server";

const RESEND_API_KEY = process.env.RESEND_API_KEY;
const FEEDBACK_TO    = "ds.shoab@gmail.com";
const FEEDBACK_FROM  = "SnapAI App <noreply@mainnov.tech>";

export async function POST(req: NextRequest) {
  try {
    const { type, message, page, userAgent } = await req.json();

    if (!message || typeof message !== "string" || message.trim().length === 0) {
      return NextResponse.json({ error: "Message is required" }, { status: 400 });
    }

    const typeLabel = type === "bug" ? "Bug Report" : type === "feature" ? "Feature Request" : "General Feedback";

    const html = `
      <div style="font-family:sans-serif;max-width:600px;margin:0 auto;">
        <h2 style="color:#1a8754;">SnapAI Beta Feedback — ${typeLabel}</h2>
        <table style="width:100%;border-collapse:collapse;margin-bottom:16px;">
          <tr><td style="padding:8px;background:#f3f4f6;font-weight:600;width:120px;">Type</td>
              <td style="padding:8px;border:1px solid #e5e7eb;">${typeLabel}</td></tr>
          <tr><td style="padding:8px;background:#f3f4f6;font-weight:600;">Page</td>
              <td style="padding:8px;border:1px solid #e5e7eb;">${page ?? "unknown"}</td></tr>
          <tr><td style="padding:8px;background:#f3f4f6;font-weight:600;">User Agent</td>
              <td style="padding:8px;border:1px solid #e5e7eb;font-size:11px;color:#6b7280;">${userAgent ?? "unknown"}</td></tr>
        </table>
        <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:16px;">
          <pre style="white-space:pre-wrap;font-family:inherit;margin:0;">${message.trim()}</pre>
        </div>
      </div>
    `;

    if (!RESEND_API_KEY) {
      // Dev mode: log to console instead of sending
      console.log("[Feedback]", { type, message: message.trim(), page });
      return NextResponse.json({ ok: true, dev: true });
    }

    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: FEEDBACK_FROM,
        to:   [FEEDBACK_TO],
        subject: `[SnapAI Beta] ${typeLabel}`,
        html,
      }),
    });

    if (!res.ok) {
      const err = await res.text();
      console.error("[Feedback] Resend error:", err);
      return NextResponse.json({ error: "Email send failed" }, { status: 502 });
    }

    return NextResponse.json({ ok: true });
  } catch (err) {
    console.error("[Feedback] Unexpected error:", err);
    return NextResponse.json({ error: "Internal error" }, { status: 500 });
  }
}
