"use client";

/**
 * DEV-ONLY test harness — mounts the real StepZeroPanel (Stage 3A install-year
 * + age-confidence review) WITHOUT the auth-gated /assess route, so Playwright
 * can drive it deterministically. A decoded unit is read from the `f` query
 * param (base64 JSON) and seeded via the test-only __testSeedUnit prop, which
 * triggers the real prefill logic. Guarded so it only renders outside production.
 */

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import StepZeroPanel from "@/components/StepZeroPanel";

function HarnessInner() {
  const params = useSearchParams();
  const raw = params.get("f");
  let seed: unknown = null;
  if (raw) {
    try {
      seed = JSON.parse(decodeURIComponent(escape(atob(raw))));
    } catch {
      seed = null;
    }
  }
  return (
    <div style={{ maxWidth: 520, margin: "0 auto" }}>
      <StepZeroPanel
        assessmentId="test-assessment"
        clerkToken="test-token"
        onConfirm={() => {}}
        onSkip={() => {}}
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        __testSeedUnit={seed as any}
      />
    </div>
  );
}

export default function StepZeroHarnessPage() {
  if (process.env.NEXT_PUBLIC_ENV === "production") return null;
  return (
    <Suspense fallback={null}>
      <HarnessInner />
    </Suspense>
  );
}
