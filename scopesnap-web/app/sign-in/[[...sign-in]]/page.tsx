/**
 * SnapAI â Embedded Sign-In Page
 * Uses Clerk's <SignIn /> component rendered within the SnapAI app.
 * Replaces the external Clerk hosted page (glowing-cowbird-89.accounts.dev)
 * which had a black screen rendering issue.
 *
 * Route: /sign-in (catch-all handles /sign-in/factor-one, /sign-in/sso-callback, etc.)
 */

import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
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
      }}
    >
      {/* SnapAI Logo */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          marginBottom: 32,
        }}
      >
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
        <span
          style={{
            fontWeight: 800,
            fontSize: 22,
            letterSpacing: -0.5,
            color: "#1a1a18",
          }}
        >
          Snap<span style={{ color: "#1a8754" }}>AI</span>
        </span>
      </div>

      {/* Clerk Sign-In Component */}
      <SignIn
        forceRedirectUrl="/dashboard"
        afterSignUpUrl="/dashboard"
        appearance={{
          elements: {
            rootBox: { width: "100%", maxWidth: 400 },
            card: {
              borderRadius: 16,
              boxShadow: "0 4px 24px rgba(0,0,0,.08)",
              border: "1px solid #e5e2da",
            },
            headerTitle: { fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700 },
            headerSubtitle: { fontFamily: "'Plus Jakarta Sans', sans-serif" },
            formButtonPrimary: {
              background: "#1a8754",
              fontFamily: "'Plus Jakarta Sans', sans-serif",
              fontWeight: 700,
              borderRadius: 10,
            },
            // Self-hosted Google icon — use CSS content: url() which properly
            // replaces <img> src in Chrome/Safari; avoids CSP-blocked CDN image
            providerIcon__google: {
              content: "url('/google-logo.svg')",
              width: 18,
              height: 18,
              display: "inline-block",
            },
          },
        }}
      />

      {/* Footer */}
      <p
        style={{
          marginTop: 24,
          fontSize: 11,
          color: "#a8a49c",
          fontFamily: "IBM Plex Mono, monospace",
        }}
      >
        SnapAI â Professional HVAC assessments for contractors
      </p>
    </div>
  );
}
