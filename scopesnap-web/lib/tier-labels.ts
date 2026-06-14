/**
 * Context-aware tier labels per Stage 0 v1.2.
 *
 * Same underlying tier ranking, different DISPLAY labels based on unit age.
 * Data keys (good/better/best) stay the same in the API contract; only the
 * strings shown to users change.
 *
 * When unit age is UNKNOWN (no decodable install_year — common today, and
 * ~always for PK brands), we deliberately fall back to a NEUTRAL set that makes
 * no age claim, rather than assuming the unit is new. See findings 2026-06-14.
 *
 * Refs:
 * - marketing/MBrain/SnapAI_Stage0_Output_v1.md Q4 Tier 1
 * - marketing/MBrain/SnapAI_Internal_Strategy_v1.2_Stage0_Aligned.md Act 3
 */
export type UnitAgeCategory = "young" | "midlife" | "eol";
export type TierKey = "good" | "better" | "best";

const TIER_LABEL_MAP: Record<UnitAgeCategory, Record<TierKey, string>> = {
  young: {
    good:   "Repair",
    better: "Enhanced Repair",
    best:   "System Upgrade",
  },
  midlife: {
    good:   "Quick Fix",
    better: "Smart Repair",
    best:   "Replace System",
  },
  eol: {
    good:   "Temporary Fix",
    better: "Replace Soon",
    best:   "Replace Now",
  },
};

// Neutral labels — used when the unit's age is unknown. Describe escalating
// scope of work WITHOUT implying the unit's age (do NOT assume "young").
const NEUTRAL_LABELS: Record<TierKey, string> = {
  good:   "Repair",
  better: "Enhanced Repair",
  best:   "Full Replacement",
};

/** Map age-in-years to age category. */
export function getUnitAgeCategory(years: number | null | undefined): UnitAgeCategory {
  if (years == null || years < 5) return "young";
  if (years < 12) return "midlife";
  return "eol";
}

/** Get the context-aware tier label for a known age category. */
export function getTierLabel(tier: TierKey, ageCategory: UnitAgeCategory): string {
  return TIER_LABEL_MAP[ageCategory][tier];
}

/** All three labels for a known age category (legends, tables, etc.). */
export function getTierLabelSet(ageCategory: UnitAgeCategory): [string, string, string] {
  const m = TIER_LABEL_MAP[ageCategory];
  return [m.good, m.better, m.best];
}

/**
 * Display label for a tier given the unit's age in years.
 * - Known age  -> context-aware label (young / midlife / eol).
 * - Unknown age (null/undefined) -> NEUTRAL label, no age claim.
 */
export function tierLabelForUnit(tier: TierKey, ageYears: number | null | undefined): string {
  if (ageYears == null) return NEUTRAL_LABELS[tier];
  return getTierLabel(tier, getUnitAgeCategory(ageYears));
}
