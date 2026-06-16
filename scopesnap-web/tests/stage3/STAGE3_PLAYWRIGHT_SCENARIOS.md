# Stage 3 — Brand Decoder single-screen UX — Playwright scenarios to add

scopesnap-web has no Playwright harness yet (no @playwright/test dep, no
playwright.config.ts). When one is added, wire these scenarios. Kept as Markdown
(not a .spec.ts) so the project tsc `**/*.ts` include does not fail on missing
test-runner globals.

## Sub-PR 3A — install-date review (components/StepZeroPanel.tsx)
- High-confidence decode (>=70) pre-fills year, confidence = Sure.
- Medium-confidence decode (40-69) pre-fills year, confidence = Approximate.
- Failed/low/unknown decode leaves year BLANK with italic "Ask homeowner" hint;
  NO yellow highlight / alarm color.
- Legacy brand pre-fills computed midpoint year + "estimated from brand
  discontinue" badge, confidence = Approximate.
- Blank year on confirm proceeds with age_confidence=unknown; NO modal/checkbox.
- Confirm sends install_year + age_source + age_confidence on
  POST /api/estimates/fault-card (via sessionStorage snap_age_capture).

## Sub-PR 3B — homeowner correction (app/r/[slug]/[reportId]/ReportClient.tsx)
- "Yes, that's right" -> homeowner_age_confirmed event + confirmed banner.
- "No — actual year is ___" -> age_corrected (corrected_by=homeowner) + recompute.
- Relative-age picker (5/10/15/20+) -> year = currentYear - age, fires
  age_corrected (source=relative_age_picker).
- "Updated based on your correction" banner shows a remaining-life BAND
  (e.g. "12-16 years"), never year-exact.
- Relative-age radios keyboard-navigable inside <fieldset>/<legend>.

## Sub-PR 3C — chooser-gate + show-the-math (components/FaultResolutionScreen.tsx)
- requires_user_chooser=true shows replacement banner with "X+ years old" copy.
- "Show repair-first option" reveals the Repair (A) tier and fires
  replacement_recommendation_overridden_by_user.
- "Why this recommendation?" panel shows estimated install year + source,
  confidence, remaining-life BAND, refrigerant + 2025+ compatibility, and the
  five weighted shadow_replace_score factors with contributions.
- "Show the math" sub-toggle expands the formula text.
- Lifespans render as bands only, never exact years.

## Accessibility checks (all sub-PRs)
- WCAG AA contrast on the legacy badge + chooser-gate banner.
- Focus handling on the disclosure panels.
- Keyboard navigation across the relative-age radios.
- 44px min tap targets; legible in sunlight (high contrast, no color-alone).
