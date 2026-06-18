"use client";

/**
 * DEV-ONLY test harness — mounts the real FaultResolutionScreen (Stage 3C
 * chooser-gate banner + "Why this recommendation?" + "Show the math") with a
 * fixture DiagnosticResult read from the `f` query param (base64 JSON) or a
 * built-in chooser-gate default. Mounted in "public" mode so no auth/footer
 * actions are required. Guarded so it only renders outside production.
 *
 * The real public route /d/[share_token] is also exercised directly by the
 * specs via page.route() mocking; this harness gives a deterministic fallback
 * and lets axe scan the component in isolation.
 */

import { useSearchParams } from "next/navigation";
import { Suspense, useState, useEffect } from "react";
import FaultResolutionScreen, { type DiagnosticResult } from "@/components/FaultResolutionScreen";

const DEFAULT_CHOOSER_GATE: DiagnosticResult = {
  session_id: "sess-test",
  fault: { card_id: 1, name: "Low refrigerant charge", confidence: "high" },
  reasoning_chain: ["Pressures indicate undercharge", "Superheat high"],
  action_steps: ["Leak search", "Recover and weigh-in charge"],
  parts_needed: ["R-410A"],
  time_estimate_minutes: 90,
  common_cause_climate: null,
  photo_evidence: [],
  alternative_diagnoses: [],
  customer: { label: null, address: null },
  share_url: "https://example.com/d/tok",
  repair_plan: {
    recommended_tier: "C",
    requires_user_chooser: true,
    unit_age_years: 14,
    tiers: [
      { key: "A", name: "Repair", total: 450, recommended: false, line_items: [] },
      { key: "B", name: "Enhanced repair", total: 1200, recommended: false, line_items: [] },
      { key: "C", name: "Replace", total: 7800, recommended: true, line_items: [] },
    ],
    recommendation: {
      recommended_tier: "C",
      reasoning: "Old unit on R-410A nearing end of life",
      age_source: "serial_decode_high",
      age_confidence: "approximate",
      reliable_age: false,
      requires_user_chooser: true,
      estimated_install_year: 2011,
      remaining_life_band: "1-4 years",
      refrigerant: "R-410A",
      refrigerant_2025_compatible: false,
      shadow_replace_score: {
        total: 0.78,
        formula: "score = 0.40*age + 0.25*refrigerant + 0.15*efficiency + 0.10*repair_cost + 0.10*reliability",
        factors: [
          { name: "age", weight: 0.40, value: 0.95, contribution: 0.38, label: "Unit age" },
          { name: "refrigerant", weight: 0.25, value: 0.80, contribution: 0.20, label: "Refrigerant phase-out" },
          { name: "efficiency", weight: 0.15, value: 0.60, contribution: 0.09, label: "Efficiency (SEER)" },
          { name: "repair_cost", weight: 0.10, value: 0.70, contribution: 0.07, label: "Repair cost ratio" },
          { name: "reliability", weight: 0.10, value: 0.40, contribution: 0.04, label: "Reliability history" },
        ],
      },
    },
  },
} as unknown as DiagnosticResult;

function HarnessInner() {
  const params = useSearchParams();
  // React 19 hydration-safe: search params are unavailable during SSR, so render
  // nothing until mounted to keep the server and first client render identical.
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (!mounted) return null;
  const raw = params.get("f");
  let data = DEFAULT_CHOOSER_GATE;
  if (raw) {
    try {
      data = JSON.parse(decodeURIComponent(escape(atob(raw))));
    } catch {
      // fall back to default
    }
  }
  return <FaultResolutionScreen data={data} mode="public" />;
}

export default function FaultResolutionHarnessPage() {
  if (process.env.NEXT_PUBLIC_ENV === "production") return null;
  return (
    <Suspense fallback={null}>
      <HarnessInner />
    </Suspense>
  );
}
