# Stage 3 Playwright e2e

Executable specs for the Stage 3 Brand-Decoder single-screen UX (3A/3B/3C).

## What's covered (8 plan scenarios)
| # | Scenario | Spec | Surface |
|---|----------|------|---------|
| 1 | High-conf decode → year pre-filled, no "Ask homeowner" | `stage3a-install-year.spec.ts` | real `/assess` (mock `/api/ocr/nameplate`) |
| 2 | Low/failed decode → blank + italic "Ask homeowner", no yellow | `stage3a` | real `/assess` |
| 3 | Legacy brand → midpoint year + "estimated from brand discontinue" badge | `stage3a` | real `/assess` |
| 4 | Blank year on Next → unknown confidence, NO modal | `stage3a` | real `/assess` |
| 5 | Report correction surface renders all 3 paths | `stage3b-homeowner-correction.spec.ts` | `/test-harness/report` (real ReportClient) |
| 6 | Relative-age picker (5/10/15/20+) → current_year − n + BAND | `stage3b` | `/test-harness/report` |
| 7 | Chooser-gate banner + "Show repair-first option" reveals repair tier | `stage3c-chooser-gate.spec.ts` | real `/d/[share_token]` (mock public endpoint) |
| 8 | "Why this recommendation?" / "Show the math" → remaining-life BAND, never exact year | `stage3c` | real `/d/[share_token]` |

Plus `@a11y`-tagged axe-core + keyboard/focus checks per sub-PR.

## Why harness routes
- `/r/[slug]/[reportId]` is SSR (server-side fetch), which `page.route()` cannot
  intercept. `/test-harness/report` mounts the **real** `ReportClient` with a
  base64 fixture passed via `?f=`, so the spec drives real component code with no
  backend. The harness pages no-op when `NEXT_PUBLIC_ENV=production`.
- 3A and 3C run against the **real** production routes (`/assess`, `/d/...`) with
  API responses mocked via `page.route()`.

## Run locally (no backend, no Clerk)
```bash
npm install
npx playwright install chromium      # downloads the browser binary
# Option A — let Playwright boot the dev server itself (dummy env baked in):
npx playwright test
# Option B — point at an already-running server / staging with SSO disabled:
BASE_URL=https://staging.snapai.mainnov.tech npx playwright test
```
Boot requires `NEXT_PUBLIC_ENV=development` so `middleware.ts` is a no-op (no Clerk
gate); the `webServer` block in `playwright.config.ts` sets this automatically.

Discover without running: `npm run test:e2e:list`.
