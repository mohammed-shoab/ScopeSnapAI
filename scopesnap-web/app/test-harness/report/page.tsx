"use client";

/**
 * DEV-ONLY test harness — mounts the real ReportClient (Stage 3B correction
 * surface) with a fixture Report read from the `f` query param (base64 JSON) or
 * a built-in default. The production /r/[slug]/[reportId] route is SSR (server
 * fetch), so Playwright's page.route() cannot intercept it; this client-side
 * harness lets the e2e specs drive the REAL component deterministically with no
 * backend. Guarded so it only renders outside production.
 */

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import ReportClient from "@/app/r/[slug]/[reportId]/ReportClient";

const DEFAULT_REPORT = {
  report_short_id: "rpt-test",
  report_token: "tok-test",
  status: "draft",
  created_at: "2026-01-15T00:00:00Z",
  company: { name: "Test HVAC Co", phone: "555-0100" },
  property: { address_line1: "1 Test St", city: "Houston", state: "TX", customer_name: "Test Homeowner" },
  equipment: { equipment_type: "ac", brand: "Carrier", model_number: "24ABC6", install_year: 2014, condition: "fair" },
  remaining_life: { age_years: 12, avg_lifespan: 15, remaining_years: 3, remaining_pct: 20 },
  photos: [],
  issues: [],
  options: [
    { tier: "good", title: "Repair", price: 450, recommended: false, line_items: [] },
    { tier: "better", title: "Enhanced Repair", price: 1200, recommended: true, line_items: [] },
    { tier: "best", title: "Full Replacement", price: 7800, recommended: false, line_items: [] },
  ],
} as unknown as Parameters<typeof ReportClient>[0]["report"];

function HarnessInner() {
  const params = useSearchParams();
  const raw = params.get("f");
  let report = DEFAULT_REPORT;
  if (raw) {
    try {
      report = JSON.parse(decodeURIComponent(escape(atob(raw))));
    } catch {
      // fall back to default on bad fixture
    }
  }
  return <ReportClient report={report} />;
}

export default function ReportHarnessPage() {
  if (process.env.NEXT_PUBLIC_ENV === "production") return null;
  return (
    <Suspense fallback={null}>
      <HarnessInner />
    </Suspense>
  );
}
