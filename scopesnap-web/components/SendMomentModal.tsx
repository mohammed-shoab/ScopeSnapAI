/**
 * SendMomentModal — Board Session 8, Section 7B
 *
 * Non-skippable 2-field prompt shown the FIRST TIME a tech sends an estimate
 * to a homeowner (when company phone is not yet set). Captures the tech's
 * company name and phone so the report has real contact info.
 *
 * - Appears before estimate generation in assess/page.tsx
 * - Persisted via sessionStorage so it only shows once per session
 * - PATCH /api/auth/me/company on submit
 * - Cannot be dismissed without filling name + phone
 */
"use client";

import { useState, useCallback } from "react";
import { API_URL } from "@/lib/api";

const IS_DEV = process.env.NEXT_PUBLIC_ENV === "development";
const SESSION_KEY = "snapai_send_moment_done";

interface Props {
  /** Called after the user submits (or if the modal is not needed) */
  onComplete: () => void;
  /** JWT token for API auth */
  clerkToken: string | null;
  /** Pre-fill from existing company record */
  existingName?: string;
  existingPhone?: string;
}

export function needsSendMoment(phone?: string | null): boolean {
  if (typeof window !== "undefined" && sessionStorage.getItem(SESSION_KEY)) {
    return false;
  }
  return !phone;
}

export function markSendMomentDone() {
  if (typeof window !== "undefined") {
    sessionStorage.setItem(SESSION_KEY, "1");
  }
}

export default function SendMomentModal({
  onComplete,
  clerkToken,
  existingName = "",
  existingPhone = "",
}: Props) {
  const [name, setName]     = useState(existingName);
  const [phone, setPhone]   = useState(existingPhone);
  const [saving, setSaving] = useState(false);
  const [error, setError]   = useState<string | null>(null);

  const handleSubmit = useCallback(async () => {
    if (!name.trim()) {
      setError("Company name is required so the homeowner knows who sent the report.");
      return;
    }
    if (!phone.trim()) {
      setError("Phone number is required — homeowners need a way to call you.");
      return;
    }

    setSaving(true);
    setError(null);

    try {
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (!IS_DEV && clerkToken) {
        headers.Authorization = `Bearer ${clerkToken}`;
      } else if (IS_DEV) {
        headers["X-Dev-Clerk-User-Id"] = "test_user_mike";
      }

      const r = await fetch(`${API_URL}/api/auth/me/company`, {
        method: "PATCH",
        headers,
        body: JSON.stringify({ name: name.trim(), phone: phone.trim() }),
      });

      if (!r.ok) {
        const body = await r.json().catch(() => ({}));
        throw new Error(body.detail || "Failed to save — please try again.");
      }

      markSendMomentDone();
      onComplete();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }, [name, phone, clerkToken, onComplete]);

  return (
    /* Backdrop */
    <div
      style={{
        position: "fixed", inset: 0, zIndex: 9999,
        background: "rgba(0,0,0,0.55)", backdropFilter: "blur(3px)",
        display: "flex", alignItems: "flex-end", justifyContent: "center",
        padding: "0 0 env(safe-area-inset-bottom, 0)",
      }}
    >
      {/* Sheet */}
      <div
        style={{
          width: "100%", maxWidth: 480,
          background: "white", borderRadius: "20px 20px 0 0",
          padding: "28px 24px 32px",
          boxShadow: "0 -8px 32px rgba(0,0,0,0.18)",
        }}
      >
        {/* Handle */}
        <div style={{ width: 36, height: 4, background: "#e2dfd7", borderRadius: 2, margin: "0 auto 24px" }} />

        {/* Header */}
        <div style={{ marginBottom: 20 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
            <div
              style={{
                width: 36, height: 36, borderRadius: 10,
                background: "#1a8754", display: "flex", alignItems: "center", justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <span style={{ color: "white", fontSize: 18 }}>📱</span>
            </div>
            <h2 style={{ fontSize: 18, fontWeight: 800, margin: 0, color: "#1a1a18" }}>
              Before we send this report…
            </h2>
          </div>
          <p style={{ fontSize: 13, color: "#7a7770", margin: 0, lineHeight: 1.5 }}>
            Your company name and phone appear on the homeowner&apos;s report. Add them once — they&apos;re saved for all future estimates.
          </p>
        </div>

        {/* Error */}
        {error && (
          <div
            style={{
              background: "#fef2f2", border: "1px solid #fecaca",
              borderRadius: 10, padding: "10px 14px",
              fontSize: 13, color: "#b91c1c", marginBottom: 16,
            }}
          >
            {error}
          </div>
        )}

        {/* Fields */}
        <div style={{ display: "flex", flexDirection: "column", gap: 14, marginBottom: 22 }}>
          <div>
            <label
              style={{
                display: "block", fontSize: 11, fontWeight: 700,
                color: "#7a7770", textTransform: "uppercase", letterSpacing: 1, marginBottom: 6,
              }}
            >
              Company Name
            </label>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="Your Company LLC"
              style={{
                width: "100%", boxSizing: "border-box",
                border: "1.5px solid #e2dfd7", borderRadius: 10,
                padding: "11px 14px", fontSize: 15, fontWeight: 600,
                outline: "none", color: "#1a1a18",
              }}
              onFocus={e => (e.target.style.borderColor = "#1a8754")}
              onBlur={e => (e.target.style.borderColor = "#e2dfd7")}
            />
          </div>

          <div>
            <label
              style={{
                display: "block", fontSize: 11, fontWeight: 700,
                color: "#7a7770", textTransform: "uppercase", letterSpacing: 1, marginBottom: 6,
              }}
            >
              Phone Number
            </label>
            <input
              type="tel"
              value={phone}
              onChange={e => setPhone(e.target.value)}
              placeholder="(555) 123-4567"
              style={{
                width: "100%", boxSizing: "border-box",
                border: "1.5px solid #e2dfd7", borderRadius: 10,
                padding: "11px 14px", fontSize: 15, fontWeight: 600,
                outline: "none", color: "#1a1a18",
              }}
              onFocus={e => (e.target.style.borderColor = "#1a8754")}
              onBlur={e => (e.target.style.borderColor = "#e2dfd7")}
            />
          </div>
        </div>

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={saving || !name.trim() || !phone.trim()}
          style={{
            width: "100%", padding: "14px", borderRadius: 12,
            background: saving || !name.trim() || !phone.trim() ? "#ccc" : "#1a8754",
            color: "white", fontWeight: 800, fontSize: 15,
            border: "none", cursor: saving ? "wait" : "pointer",
            transition: "background 0.15s",
          }}
        >
          {saving ? "Saving…" : "Save & Generate Report →"}
        </button>

        <p style={{ textAlign: "center", fontSize: 11, color: "#b0aca4", marginTop: 12, marginBottom: 0 }}>
          You can update these any time in Settings
        </p>
      </div>
    </div>
  );
}
