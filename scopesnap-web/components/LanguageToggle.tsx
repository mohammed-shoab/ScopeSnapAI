"use client";

/**
 * LanguageToggle — Pakistan market only
 *
 * Shows a compact EN / اردو pill toggle in the sidebar and bottom nav.
 * Renders null on US market (detectMarket() !== "PK").
 *
 * Usage:
 *   <LanguageToggle />   — just drop it anywhere inside LanguageProvider
 */

import { detectMarket } from "@/lib/market";
import { useLang } from "@/lib/language-context";

export default function LanguageToggle() {
  // Only show for Pakistan market
  if (detectMarket() !== "PK") return null;

  const { lang, toggleLang } = useLang();

  const isUrdu = lang === "ur";

  return (
    <button
      onClick={toggleLang}
      aria-label={isUrdu ? "Switch to English" : "اردو میں تبدیل کریں"}
      title={isUrdu ? "Switch to English" : "Switch to Urdu"}
      className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-xs font-semibold transition-all"
      style={{
        background: isUrdu ? "#1a8754" : "#f0efea",
        color: isUrdu ? "#ffffff" : "#1a1a18",
        borderColor: isUrdu ? "#0f5c38" : "#e2dfd7",
      }}
    >
      {/* Globe icon */}
      <svg
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <circle cx="12" cy="12" r="10" />
        <line x1="2" y1="12" x2="22" y2="12" />
        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
      </svg>
      {/* Active label */}
      <span>{isUrdu ? "EN" : "اردو"}</span>
    </button>
  );
}
