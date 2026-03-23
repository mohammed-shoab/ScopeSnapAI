/**
 * ScopeSnap — Branded 404 Not Found Page
 * Replaces the default Next.js "404: This page could not be found." plain text.
 */
import Link from "next/link";

export default function NotFound() {
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
            width: 40,
            height: 40,
            borderRadius: 10,
            background: "#1a8754",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "white",
            fontWeight: 800,
            fontSize: 20,
          }}
        >
          S
        </div>
        <span style={{ fontWeight: 800, fontSize: 20, letterSpacing: -0.5 }}>
          <span style={{ color: "#1a1a18" }}>Scope</span>
          <span style={{ color: "#1a8754" }}>Snap</span>
        </span>
      </div>

      {/* 404 illustration */}
      <div
        style={{
          fontFamily: "IBM Plex Mono, monospace",
          fontSize: 96,
          fontWeight: 800,
          color: "#e5e2da",
          lineHeight: 1,
          marginBottom: 24,
          letterSpacing: -4,
        }}
      >
        404
      </div>

      <h1 style={{ fontSize: 22, fontWeight: 800, margin: "0 0 10px", letterSpacing: -0.5 }}>
        Page not found
      </h1>
      <p style={{ fontSize: 14, color: "#7a7770", maxWidth: 320, lineHeight: 1.6, margin: "0 0 32px" }}>
        The page you&apos;re looking for doesn&apos;t exist or may have moved.
        If you received a report link, it may have expired.
      </p>

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", justifyContent: "center" }}>
        <Link
          href="/"
          style={{
            padding: "12px 24px",
            background: "#1a8754",
            color: "white",
            borderRadius: 10,
            textDecoration: "none",
            fontWeight: 700,
            fontSize: 14,
          }}
        >
          Go to Homepage
        </Link>
        <Link
          href="/dashboard"
          style={{
            padding: "12px 24px",
            background: "white",
            color: "#1a1a18",
            borderRadius: 10,
            textDecoration: "none",
            fontWeight: 700,
            fontSize: 14,
            border: "1px solid #e5e2da",
          }}
        >
          Sign In
        </Link>
      </div>

      <p style={{ fontSize: 11, color: "#b0aca4", marginTop: 40, fontFamily: "IBM Plex Mono, monospace" }}>
        ScopeSnap AI — Professional HVAC assessments for contractors
      </p>
    </div>
  );
}
