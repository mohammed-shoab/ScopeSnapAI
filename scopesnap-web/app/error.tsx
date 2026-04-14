"use client";
/**
 * SnapAI — Global React Error Boundary
 * Catches unhandled React errors and shows a friendly recovery screen
 * instead of a blank white page.
 *
 * Next.js App Router automatically uses this as the error boundary for
 * the entire app. Place in /app/error.tsx for global coverage.
 */

import { useEffect } from "react";
import Link from "next/link";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log to console in dev; in production this is where Sentry would capture it
    console.error("[SnapAI] Unhandled error:", error);
  }, [error]);

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f2f1ec",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "'Plus Jakarta Sans', sans-serif",
        padding: "24px 16px",
        textAlign: "center",
      }}
    >
      {/* Logo */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 40 }}>
        <div
          style={{
            width: 40, height: 40, borderRadius: 10, background: "#1a8754",
            display: "flex", alignItems: "center", justifyContent: "center",
            color: "white", fontWeight: 800, fontSize: 20,
          }}
        >
          S
        </div>
        <span style={{ fontWeight: 800, fontSize: 20, letterSpacing: -0.5 }}>
          <span style={{ color: "#1a1a18" }}>Snap</span>
          <span style={{ color: "#1a8754" }}>AI</span>
        </span>
      </div>

      {/* Error icon */}
      <div style={{ fontSize: 56, marginBottom: 20 }}>
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#e5e2da"
          strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
      </div>

      <h1 style={{ fontSize: 22, fontWeight: 800, margin: "0 0 10px", letterSpacing: -0.5 }}>
        Something went wrong
      </h1>
      <p style={{ fontSize: 14, color: "#7a7770", maxWidth: 340, lineHeight: 1.6, margin: "0 0 32px" }}>
        An unexpected error occurred. Your work has been saved. Try refreshing
        or go back to the dashboard.
      </p>

      {/* Error digest for support (only shown in production if digest exists) */}
      {error.digest && (
        <p style={{ fontSize: 11, color: "#b0aca4", marginBottom: 24, fontFamily: "IBM Plex Mono, monospace" }}>
          Error ID: {error.digest}
        </p>
      )}

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", justifyContent: "center" }}>
        <button
          onClick={reset}
          style={{
            padding: "12px 24px", background: "#1a8754", color: "white",
            borderRadius: 10, border: "none", fontWeight: 700, fontSize: 14,
            cursor: "pointer", fontFamily: "inherit",
          }}
        >
          Try Again
        </button>
        <Link
          href="/dashboard"
          style={{
            padding: "12px 24px", background: "white", color: "#1a1a18",
            borderRadius: 10, textDecoration: "none", fontWeight: 700, fontSize: 14,
            border: "1px solid #e5e2da",
          }}
        >
          Go to Dashboard
        </Link>
      </div>

      <p style={{ fontSize: 11, color: "#b0aca4", marginTop: 40, fontFamily: "IBM Plex Mono, monospace" }}>
        SnapAI — Professional HVAC assessments for contractors
      </p>
    </div>
  );
}
