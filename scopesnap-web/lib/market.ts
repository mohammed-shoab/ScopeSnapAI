/**
 * SnapAI — Market Detection & Configuration
 *
 * Supports two markets:
 *   US  — snapai.mainnov.tech / localhost  (USD, $)
 *   PK  — pk.snapai.mainnov.tech           (PKR, ₨)
 *
 * Usage:
 *   import { detectMarket, formatCurrency, MARKET_CONFIG } from "@/lib/market";
 *   const market = detectMarket();
 *   const sym = MARKET_CONFIG[market].currencySymbol;  // "$" | "₨"
 *   const str = formatCurrency(12500);                 // "$12,500" | "₨12,500"
 */

export type Market = "US" | "PK";

export interface MarketConfig {
  /** ISO 4217 currency code */
  currency: string;
  /** Display prefix for formatted amounts */
  currencySymbol: string;
  /** BCP-47 locale for number formatting */
  locale: string;
  /** Supabase table prefix for this market's data */
  apiTablePrefix: string;
  /** Human-readable country name */
  countryName: string;
}

export const MARKET_CONFIG: Record<Market, MarketConfig> = {
  US: {
    currency: "USD",
    currencySymbol: "$",
    locale: "en-US",
    apiTablePrefix: "",
    countryName: "United States",
  },
  PK: {
    currency: "PKR",
    currencySymbol: "₨",
    locale: "en-PK",
    apiTablePrefix: "pak_",
    countryName: "Pakistan",
  },
};

/** Hostnames that map to the Pakistan market */
const PK_HOSTNAMES: string[] = [
  "pk.snapai.mainnov.tech",
  "pk.snapai.app",
];

/**
 * Detect the current market from the browser hostname.
 * Falls back to US in SSR contexts (no window) or unrecognised hostnames.
 */
export function detectMarket(): Market {
  if (typeof window !== "undefined") {
    const hostname = window.location.hostname;
    if (PK_HOSTNAMES.includes(hostname) || hostname.startsWith("pk.")) {
      return "PK";
    }
  }
  return "US";
}

// ── Language support (Pakistan only) ──────────────────────────────────────────

export type Language = "en" | "ur";

/**
 * Get the user's preferred language.
 * Pakistan market only — US always returns "en".
 */
export function getLanguage(): Language {
  if (typeof window === "undefined") return "en";
  if (detectMarket() !== "PK") return "en";
  return (localStorage.getItem("snap_lang") as Language) || "en";
}

/**
 * Persist the user's language choice and flip document direction.
 * No-op when called server-side.
 */
export function setLanguage(lang: Language): void {
  if (typeof window === "undefined") return;
  localStorage.setItem("snap_lang", lang);
  document.documentElement.dir = lang === "ur" ? "rtl" : "ltr";
  document.documentElement.lang = lang;
}

// ── Currency formatting ────────────────────────────────────────────────────────

/**
 * Format a numeric amount with the market's currency symbol.
 *
 * @param n      - Amount to format (null/undefined returns "—")
 * @param market - Market override; defaults to detectMarket()
 * @returns      - Formatted string e.g. "$12,500" or "₨12,500"
 */
export function formatCurrency(
  n: number | null | undefined,
  market?: Market
): string {
  if (n == null || isNaN(n as number)) return "—";
  const m = market ?? detectMarket();
  const { currencySymbol, locale } = MARKET_CONFIG[m];
  return (
    currencySymbol +
    Math.round(n as number).toLocaleString(locale, {
      maximumFractionDigits: 0,
    })
  );
}
