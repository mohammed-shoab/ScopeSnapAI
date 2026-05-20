"use client";

/**
 * InstallPrompt — PWA "Add to Home Screen" banner
 *
 * Behaviour:
 *  • Android / Chrome: listens for `beforeinstallprompt`, shows a native-style
 *    banner with an "Install App" button that triggers the OS prompt.
 *  • iOS / Safari: detects standalone=false + is-iOS, shows a step-by-step
 *    instruction card (Share → Add to Home Screen) because iOS has no JS API.
 *  • Already installed (standalone mode): renders nothing.
 *  • Dismissed: stores a flag in localStorage; doesn't show again for 7 days.
 */

import { useEffect, useState } from "react";

type Platform = "android" | "ios" | null;

function detectPlatform(): Platform {
  if (typeof window === "undefined") return null;

  const ua = navigator.userAgent;
  const isIOS =
    /iPad|iPhone|iPod/.test(ua) ||
    (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  const isAndroid = /Android/.test(ua);

  if (isIOS) return "ios";
  if (isAndroid) return "android";
  return null;
}

function isStandalone(): boolean {
  if (typeof window === "undefined") return false;
  return (
    window.matchMedia("(display-mode: standalone)").matches ||
    // @ts-expect-error — iOS safari specific
    window.navigator.standalone === true
  );
}

function isDismissed(): boolean {
  try {
    const ts = localStorage.getItem("install_prompt_dismissed");
    if (!ts) return false;
    const days = (Date.now() - parseInt(ts)) / 86_400_000;
    return days < 7;
  } catch {
    return false;
  }
}

function markDismissed() {
  try {
    localStorage.setItem("install_prompt_dismissed", String(Date.now()));
  } catch {
    /* ignore */
  }
}

export default function InstallPrompt() {
  const [platform, setPlatform] = useState<Platform>(null);
  const [visible, setVisible] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState<Event | null>(null);
  const [showIOSSteps, setShowIOSSteps] = useState(false);

  useEffect(() => {
    if (isStandalone() || isDismissed()) return;

    const p = detectPlatform();
    if (!p) return;

    setPlatform(p);

    if (p === "android") {
      // Capture the native install prompt (Chrome on Android)
      const handler = (e: Event) => {
        e.preventDefault();
        setDeferredPrompt(e);
        setVisible(true);
      };
      window.addEventListener("beforeinstallprompt", handler);
      return () => window.removeEventListener("beforeinstallprompt", handler);
    }

    if (p === "ios") {
      // iOS has no event — just show the banner after a short delay
      const timer = setTimeout(() => setVisible(true), 1500);
      return () => clearTimeout(timer);
    }
  }, []);

  function dismiss() {
    markDismissed();
    setVisible(false);
  }

  async function handleInstall() {
    if (!deferredPrompt) return;
    // @ts-expect-error — BeforeInstallPromptEvent
    await deferredPrompt.prompt();
    // @ts-expect-error
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === "accepted") {
      setVisible(false);
    }
    setDeferredPrompt(null);
  }

  if (!visible) return null;

  /* ── iOS instruction banner ── */
  if (platform === "ios") {
    return (
      <div
        style={{
          position: "fixed",
          bottom: 80, // above BottomNav
          left: 12,
          right: 12,
          zIndex: 9999,
          background: "#ffffff",
          border: "1.5px solid #e5e7eb",
          borderRadius: 18,
          boxShadow: "0 8px 32px rgba(0,0,0,0.14)",
          padding: "16px 18px",
          fontFamily: "inherit",
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            {/* SnapAI icon */}
            <div
              style={{
                width: 40,
                height: 40,
                borderRadius: 10,
                background: "linear-gradient(135deg,#1a8754,#159a5e)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 20,
              }}
            >
              📸
            </div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 700, color: "#111" }}>Add SnapAI to your home screen</div>
              <div style={{ fontSize: 12, color: "#6b7280" }}>Works like a native app, offline too</div>
            </div>
          </div>
          <button
            onClick={dismiss}
            style={{
              background: "none",
              border: "none",
              cursor: "pointer",
              color: "#9ca3af",
              fontSize: 20,
              lineHeight: 1,
              padding: 4,
            }}
          >
            ×
          </button>
        </div>

        {/* Steps toggle */}
        {!showIOSSteps ? (
          <button
            onClick={() => setShowIOSSteps(true)}
            style={{
              width: "100%",
              padding: "10px 0",
              background: "#1a8754",
              color: "#fff",
              border: "none",
              borderRadius: 12,
              fontSize: 14,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            Show me how →
          </button>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {[
              { n: 1, icon: "⬆️", text: 'Tap the Share button at the bottom of Safari' },
              { n: 2, icon: "➕", text: 'Scroll down and tap "Add to Home Screen"' },
              { n: 3, icon: "✅", text: 'Tap "Add" in the top right — done!' },
            ].map(({ n, icon, text }) => (
              <div key={n} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <div
                  style={{
                    width: 26,
                    height: 26,
                    borderRadius: "50%",
                    background: "#f0fdf4",
                    border: "1.5px solid #1a8754",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 11,
                    fontWeight: 700,
                    color: "#1a8754",
                    flexShrink: 0,
                  }}
                >
                  {n}
                </div>
                <div style={{ fontSize: 13, color: "#374151" }}>
                  <span style={{ marginRight: 4 }}>{icon}</span>{text}
                </div>
              </div>
            ))}
            <button
              onClick={dismiss}
              style={{
                marginTop: 4,
                padding: "8px 0",
                background: "#f3f4f6",
                color: "#374151",
                border: "none",
                borderRadius: 10,
                fontSize: 13,
                cursor: "pointer",
              }}
            >
              Got it, thanks
            </button>
          </div>
        )}
      </div>
    );
  }

  /* ── Android / Chrome install banner ── */
  return (
    <div
      style={{
        position: "fixed",
        bottom: 80,
        left: 12,
        right: 12,
        zIndex: 9999,
        background: "#ffffff",
        border: "1.5px solid #e5e7eb",
        borderRadius: 18,
        boxShadow: "0 8px 32px rgba(0,0,0,0.14)",
        padding: "14px 16px",
        display: "flex",
        alignItems: "center",
        gap: 12,
      }}
    >
      <div
        style={{
          width: 44,
          height: 44,
          borderRadius: 12,
          background: "linear-gradient(135deg,#1a8754,#159a5e)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 22,
          flexShrink: 0,
        }}
      >
        📸
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#111" }}>Install SnapAI</div>
        <div style={{ fontSize: 11, color: "#6b7280" }}>Add to home screen — works offline</div>
      </div>
      <button
        onClick={handleInstall}
        style={{
          padding: "8px 14px",
          background: "#1a8754",
          color: "#fff",
          border: "none",
          borderRadius: 10,
          fontSize: 13,
          fontWeight: 700,
          cursor: "pointer",
          flexShrink: 0,
        }}
      >
        Install
      </button>
      <button
        onClick={dismiss}
        style={{
          background: "none",
          border: "none",
          cursor: "pointer",
          color: "#9ca3af",
          fontSize: 20,
          padding: 4,
          flexShrink: 0,
        }}
      >
        ×
      </button>
    </div>
  );
}
