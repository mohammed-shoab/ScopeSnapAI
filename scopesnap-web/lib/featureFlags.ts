/**
 * SnapAI — Feature Flags
 * SOW Task 1.6: Control visibility of non-essential pages during beta.
 *
 * All flags read from NEXT_PUBLIC_* env vars so they can be toggled per
 * environment in Vercel without a code deploy.
 *
 * Default: false (hidden) for everything except core beta pages.
 * Set NEXT_PUBLIC_SHOW_X=true in Vercel env vars to enable a page.
 *
 * Core beta pages (always visible, no flag needed):
 *   /dashboard, /assess, /estimates, /settings
 */

function flag(envVar: string | undefined, defaultValue = false): boolean {
  if (typeof envVar === "undefined") return defaultValue;
  return envVar === "true" || envVar === "1";
}

export const featureFlags = {
  /** /analytics — Accuracy Tracker / performance charts */
  showAnalytics: flag(process.env.NEXT_PUBLIC_SHOW_ANALYTICS, false),

  /** /intelligence/leaks — Profit Leaks widget */
  showProfitLeaks: flag(process.env.NEXT_PUBLIC_SHOW_PROFIT_LEAKS, false),

  /** /intelligence/benchmark — BenchmarkIQ */
  showBenchmark: flag(process.env.NEXT_PUBLIC_SHOW_BENCHMARK, false),

  /** /intelligence/history — Property History */
  showPropertyHistory: flag(process.env.NEXT_PUBLIC_SHOW_PROPERTY_HISTORY, false),

  /** /equipment — Equipment Database + Aging Alerts */
  showEquipment: flag(process.env.NEXT_PUBLIC_SHOW_EQUIPMENT, false),

  /** /team — Technicians & Leaderboard */
  showTeam: flag(process.env.NEXT_PUBLIC_SHOW_TEAM, false),

  /** /settings/integrations — Third-party integrations */
  showIntegrations: flag(process.env.NEXT_PUBLIC_SHOW_INTEGRATIONS, false),

  /** Intel tab in BottomNav */
  showIntel: flag(process.env.NEXT_PUBLIC_SHOW_INTEL, false),

  /** Jobs / Estimates tab in BottomNav */
  showJobs: flag(process.env.NEXT_PUBLIC_SHOW_JOBS, true),
} as const;

export type FeatureFlags = typeof featureFlags;
