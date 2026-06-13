/**
 * Context-aware tier labels per Stage 0 v1.2.
 *
 * Same underlying tier ranking, different DISPLAY labels based on unit age.
 * Data keys (good/better/best) stay the same in the API contract;
 * only the strings shown to users change.
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

/** Map age-in-years to age category. */
export function getUnitAgeCategory(years: number | null | undefined): UnitAgeCategory {
  if (years == null || years < 5) return "young";
  if (years < 12) return "midlife";
  return "eol";
}

/** Get the context-aware tier label for display. */
export function getTierLabel(tier: TierKey, ageCategory: UnitAgeCategory): string {
  return TIER_LABEL_MAP[ageCategory][tier];
}

/** Get all three tier labels for the given age category (for legends, tables, etc.). */
export function getTierLabelSet(ageCategory: UnitAgeCategory): [string, string, string] {
  const m = TIER_LABEL_MAP[ageCategory];
  return [m.good, m.better, m.best];
}

/** Convenience: get the right label from a year number directly. */
export function tierLabelForUnit(tier: TierKey, ageYears: number | null | undefined): string {
  return getTierLabel(tier, getUnitAgeCategory(ageYears));
}
