/**
 * Stage 3 e2e fixtures — crafted backend responses that drive each scenario
 * deterministically (no live backend, no auth). These mirror the real response
 * shapes consumed by StepZeroPanel / FaultResolutionScreen / ReportClient.
 */

// ── 3A: /api/ocr/nameplate decode shapes ───────────────────────────────────
export interface NameplateUnitFixture {
  model_number: string | null;
  serial_number: string | null;
  tonnage: number | null;
  refrigerant: string | null;
  factory_charge_oz: number | null;
  rla: number | null;
  lra: number | null;
  capacitor_uf: string | null;
  mca: number | null;
  mocp: number | null;
  voltage: string | null;
  brand_id: string | null;
  series_id: string | null;
  charging_method: string | null;
  metering_device: string | null;
  is_legacy: boolean;
  year_of_manufacture: number | null;
  r22_alert: boolean;
  confidence: number;
  notes: string | null;
}

export interface OcrResultFixture {
  outdoor: NameplateUnitFixture;
  indoor: NameplateUnitFixture | null;
  captured_at: string;
  capture_method: string;
  d7_brand_detected: boolean;
  d7_brand_name: string | null;
}

const BASE_UNIT: NameplateUnitFixture = {
  model_number: "24ABC636A003",
  serial_number: "1234567890",
  tonnage: 3.0,
  refrigerant: "R-410A",
  factory_charge_oz: 120,
  rla: 14.0,
  lra: 74,
  capacitor_uf: "45/5 MFD 370V or 440V",
  mca: 19.0,
  mocp: 30,
  voltage: "208/230",
  brand_id: "carrier",
  series_id: "carrier-infinity",
  charging_method: "subcooling",
  metering_device: "txv",
  is_legacy: false,
  year_of_manufacture: 2018,
  r22_alert: false,
  confidence: 92,
  notes: null,
};

function ocr(partial: Partial<NameplateUnitFixture>): OcrResultFixture {
  return {
    outdoor: { ...BASE_UNIT, ...partial },
    indoor: null,
    captured_at: "2026-01-15T00:00:00Z",
    capture_method: "camera",
    d7_brand_detected: true,
    d7_brand_name: "carrier",
  };
}

/** High-confidence decode (>=70) → year pre-fills, confidence = Sure. */
export const OCR_HIGH_CONFIDENCE = ocr({ year_of_manufacture: 2018, confidence: 92, is_legacy: false });

/** Low / failed decode → year stays BLANK, confidence = Unknown, no highlight. */
export const OCR_LOW_CONFIDENCE = ocr({ year_of_manufacture: null, confidence: 20, is_legacy: false });

/** Legacy (discontinued) brand → midpoint year + "estimated from brand discontinue". */
export const OCR_LEGACY_BRAND = ocr({
  year_of_manufacture: 1998,
  confidence: 55,
  is_legacy: true,
  brand_id: "intertherm",
  series_id: "intertherm-legacy",
});

// ── 3C: diagnostic / fault-card shapes ──────────────────────────────────────
export interface DiagnosticFixture {
  session_id: string;
  assessment_id?: string;
  fault: { card_id: number; name: string; confidence: "high" | "medium" | "low" };
  reasoning_chain: string[];
  action_steps: string[];
  parts_needed: string[];
  time_estimate_minutes: number | null;
  common_cause_climate: string | null;
  photo_evidence: { url: string; label?: string }[];
  alternative_diagnoses: { name: string; confidence: string }[];
  customer: { label: string | null; address: string | null };
  share_url: string;
  repair_plan?: unknown;
}

/** Chooser-gate: unknown/unconfirmed age + replacement recommendation. */
export const DIAG_CHOOSER_GATE: DiagnosticFixture = {
  session_id: "sess-chooser",
  fault: { card_id: 12, name: "Compressor failure", confidence: "high" },
  reasoning_chain: ["Compressor windings open", "No start on call for cool"],
  action_steps: ["Confirm with megohmmeter", "Quote compressor or replacement"],
  parts_needed: ["Compressor"],
  time_estimate_minutes: 180,
  common_cause_climate: null,
  photo_evidence: [],
  alternative_diagnoses: [],
  customer: { label: null, address: null },
  share_url: "https://example.com/d/chooser",
  repair_plan: {
    recommended_tier: "C",
    requires_user_chooser: true,
    unit_age_years: 16,
    tiers: [
      { key: "A", name: "Repair", total: 650, recommended: false, line_items: [] },
      { key: "B", name: "Enhanced repair", total: 1900, recommended: false, line_items: [] },
      { key: "C", name: "Full replacement", total: 8900, recommended: true, line_items: [] },
    ],
    recommendation: {
      recommended_tier: "C",
      reasoning: "16-year-old unit on phased-out refrigerant",
      age_source: "serial_decode_high",
      age_confidence: "approximate",
      reliable_age: false,
      requires_user_chooser: true,
      estimated_install_year: 2009,
      remaining_life_band: "0-3 years",
      refrigerant: "R-410A",
      refrigerant_2025_compatible: false,
      shadow_replace_score: {
        total: 0.81,
        formula:
          "score = 0.40*age + 0.25*refrigerant + 0.15*efficiency + 0.10*repair_cost + 0.10*reliability",
        factors: [
          { name: "age", weight: 0.4, value: 0.98, contribution: 0.39, label: "Unit age" },
          { name: "refrigerant", weight: 0.25, value: 0.8, contribution: 0.2, label: "Refrigerant phase-out" },
          { name: "efficiency", weight: 0.15, value: 0.6, contribution: 0.09, label: "Efficiency (SEER)" },
          { name: "repair_cost", weight: 0.1, value: 0.7, contribution: 0.07, label: "Repair cost ratio" },
          { name: "reliability", weight: 0.1, value: 0.6, contribution: 0.06, label: "Reliability history" },
        ],
      },
    },
  },
};

// ── 3B: homeowner report shape ──────────────────────────────────────────────
export interface ReportFixture {
  report_short_id: string;
  report_token: string;
  status: string;
  created_at?: string;
  company: { name?: string; phone?: string };
  property?: { address_line1?: string; city?: string; state?: string; customer_name?: string };
  equipment?: { equipment_type?: string; brand?: string; model_number?: string; install_year?: number; condition?: string };
  remaining_life?: { age_years: number; avg_lifespan: number; remaining_years: number; remaining_pct: number };
  photos: unknown[];
  issues: unknown[];
  options: unknown[];
}

/** Homeowner report showing an install year that the homeowner can confirm/correct. */
export const REPORT_WITH_INSTALL_YEAR: ReportFixture = {
  report_short_id: "rpt-0847",
  report_token: "tok-0847",
  status: "draft",
  created_at: "2026-01-15T00:00:00Z",
  company: { name: "Lone Star HVAC", phone: "713-555-0142" },
  property: { address_line1: "12 Oak Ln", city: "Houston", state: "TX", customer_name: "Jane Homeowner" },
  equipment: { equipment_type: "ac", brand: "Trane", model_number: "4TTR6", install_year: 2014, condition: "fair" },
  remaining_life: { age_years: 12, avg_lifespan: 15, remaining_years: 3, remaining_pct: 20 },
  photos: [],
  issues: [],
  options: [
    { tier: "good", title: "Repair", price: 480, recommended: false, line_items: [] },
    { tier: "better", title: "Enhanced Repair", price: 1350, recommended: true, line_items: [] },
    { tier: "best", title: "Full Replacement", price: 8200, recommended: false, line_items: [] },
  ],
};
