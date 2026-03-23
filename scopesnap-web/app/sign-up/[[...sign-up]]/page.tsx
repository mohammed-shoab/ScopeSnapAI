/**
 * ScopeSnap — Embedded Sign-Up Page
 * Uses Clerk's <SignUp /> component rendered within the ScopeSnap app.
 *
 * Route: /sign-up (catch-all handles multi-step Clerk sign-up flow)
 */

import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
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
      {/* ScopeSnap Logo */}
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
          Scope<span style={{ color: "#1a8754" }}>Snap</span>
        </span>
      </div>

      {/* Clerk Sign-Up Component */}
      <SignUp
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
        ScopeSnap AI — Professional HVAC assessments for contractors
      </p>
    </div>
  );
}
