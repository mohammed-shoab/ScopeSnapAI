"use client";

/**
 * SnapAI — Language Context (Pakistan Phase 2)
 *
 * Provides:
 *   - lang: "en" | "ur"
 *   - toggleLang(): flips between English and Urdu
 *   - t(key): returns Urdu string if active, else the English key as-is
 *
 * Houston market: LanguageProvider is never mounted → no overhead.
 * Pakistan market: wrap the app in <LanguageProvider> from the root layout.
 */

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { getLanguage, setLanguage, Language } from "./market";
import { URDU_STRINGS } from "./urdu-strings";

interface LanguageContextValue {
  lang: Language;
  toggleLang: () => void;
  /** Translate a UI string. Returns the Urdu translation or falls back to key. */
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextValue>({
  lang: "en",
  toggleLang: () => {},
  t: (k) => k,
});

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Language>("en");

  // Initialise from localStorage on first mount
  useEffect(() => {
    const stored = getLanguage();
    setLang(stored);
    // Ensure document direction is correct on mount
    if (typeof document !== "undefined") {
      document.documentElement.dir = stored === "ur" ? "rtl" : "ltr";
      document.documentElement.lang = stored;
    }
  }, []);

  const toggleLang = () => {
    const next: Language = lang === "en" ? "ur" : "en";
    setLanguage(next); // persists to localStorage + flips dir
    setLang(next);
  };

  const t = (key: string): string => {
    if (lang !== "ur") return key;
    return URDU_STRINGS[key] ?? key;
  };

  return (
    <LanguageContext.Provider value={{ lang, toggleLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

/** Hook — use inside any component wrapped by LanguageProvider. */
export const useLang = () => useContext(LanguageContext);
