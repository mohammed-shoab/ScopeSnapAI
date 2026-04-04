"use client";
/**
 * OfflineBanner — RW-06
 * Appears at the top of the screen when navigator.onLine is false.
 * Disappears immediately when connectivity returns.
 * Design: matches SnapAI brand, does not obscure nav.
 */

import { useState, useEffect } from "react";

export default function OfflineBanner() {
  const [isOffline, setIsOffline] = useState(false);
  const [justCameBack, setJustCameBack] = useState(false);

  useEffect(() => {
    // Initialise from current state
    setIsOffline(!navigator.onLine);

    function handleOffline() {
      setIsOffline(true);
      setJustCameBack(false);
    }

    function handleOnline() {
      setIsOffline(false);
      setJustCameBack(true);
      // "Back online" message fades after 3 s
      setTimeout(() => setJustCameBack(false), 3000);
    }

    window.addEventListener("offline", handleOffline);
    window.addEventListener("online", handleOnline);

    return () => {
      window.removeEventListener("offline", handleOffline);
      window.removeEventListener("online", handleOnline);
    };
  }, []);

  if (!isOffline && !justCameBack) return null;

  if (justCameBack) {
    return (
      <div
        role="status"
        aria-live="polite"
        className="fixed top-0 left-0 right-0 z-50 flex items-center justify-center gap-2 px-4 py-2 text-sm font-semibold text-white"
        style={{ background: "#1a8754" }}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        Back online
      </div>
    );
  }

  return (
    <div
      role="alert"
      aria-live="assertive"
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-center gap-2 px-4 py-2 text-sm font-semibold text-white"
      style={{ background: "#c4600a" }}
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
        strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
        <line x1="1" y1="1" x2="23" y2="23"/>
        <path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55"/>
        <path d="M5 12.55a10.94 10.94 0 0 1 5.17-2.39"/>
        <path d="M10.71 5.05A16 16 0 0 1 22.56 9"/>
        <path d="M1.42 9a15.91 15.91 0 0 1 4.7-2.88"/>
        <path d="M8.53 16.11a6 6 0 0 1 6.95 0"/>
        <line x1="12" y1="20" x2="12.01" y2="20"/>
      </svg>
      No internet connection — check your signal
    </div>
  );
}
