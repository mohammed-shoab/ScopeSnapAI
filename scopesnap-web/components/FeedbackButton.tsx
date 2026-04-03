"use client";
/**
 * ScopeSnap — Feedback Button
 * SOW Task 1.6 / BUG-01 fix: Floating feedback button for beta period.
 *
 * Opens the in-app FeedbackModal instead of a mailto: link, so it works
 * in all environments (no email client required).
 *
 * On mobile the button is hidden — feedback is accessible via SidebarNav.
 * The button auto-hides on report pages (/r/*) since those are homeowner-facing.
 */

import { useState } from "react";
import { usePathname } from "next/navigation";
import FeedbackModal from "@/components/FeedbackModal";

export default function FeedbackButton() {
  const pathname  = usePathname();
  const [open, setOpen] = useState(false);

  // Don't show on public report pages (homeowner-facing)
  if (pathname.startsWith("/r/")) return null;

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="hidden md:flex items-center gap-2 fixed bottom-6 right-6 z-50 px-4 py-2.5 rounded-full text-sm font-semibold shadow-lg transition-all hover:shadow-xl hover:scale-105 active:scale-95"
        style={{
          background: "rgba(26,135,84,.12)",
          color: "#1a8754",
          border: "1px solid rgba(26,135,84,.3)",
          backdropFilter: "blur(8px)",
          WebkitBackdropFilter: "blur(8px)",
        }}
        aria-label="Send feedback about ScopeSnap"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
        </svg>
        Beta Feedback
      </button>

      <FeedbackModal open={open} onClose={() => setOpen(false)} />
    </>
  );
}
