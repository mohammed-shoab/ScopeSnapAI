/**
 * StagingBanner — S.7
 * Renders a full-width amber bar at the top of every authenticated page
 * when NEXT_PUBLIC_ENV === "staging". Invisible in production and dev.
 *
 * Rendered server-side in app/(app)/layout.tsx — no client bundle cost.
 */

const IS_STAGING = process.env.NEXT_PUBLIC_ENV === "staging";

export default function StagingBanner() {
  if (!IS_STAGING) return null;
  return (
    <div
      role="alert"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        zIndex: 9999,
        background: "#f59e0b",
        color: "#1c1917",
        textAlign: "center",
        fontSize: "0.75rem",
        fontWeight: 700,
        letterSpacing: "0.05em",
        padding: "4px 12px",
        fontFamily: "ui-monospace, monospace",
      }}
    >
      ⚠ STAGING — not production data
    </div>
  );
}
