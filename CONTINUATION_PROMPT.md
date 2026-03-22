# ScopeSnap AI — Continuation Prompt

I'm working on a Next.js 14 / FastAPI / PostgreSQL app called ScopeSnap (AI-powered HVAC estimation tool) running via Docker Compose on Windows. The workspace is at `C:\Users\Shoab\Documents\Claude\Projects\ScopeSnapAI`. The app runs at `localhost:3000` (web), `localhost:8000` (API), `localhost:5432` (Postgres). Dev auth uses header `X-Dev-Clerk-User-Id: test_user_mike`.

## Current state after this session

### Bugs fixed
- ✅ **`$[object Object]` savings bug** — `energy_savings` is a dict `{annual_savings, five_year_savings, ...}`, not a number. Fixed in `/app/(app)/estimate/[id]/page.tsx` — added `EnergySavings` interface and safe extraction of `annual_savings`.
- ✅ **Markup PATCH infinite loop** — `updated_options.append(option)` inside `for option in updated_options` caused the list to grow forever. Removed the errant append in `/scopesnap-api/api/estimates.py`.
- ✅ **PDF "Failed to fetch"** — WeasyPrint import failure was crashing the ASGI connection without returning any HTTP response. Fixed with:
  1. Lazy import in try/except so a failed WeasyPrint import returns a proper HTTP 200 with `pdf_warning` field
  2. PDF errors no longer block the homeowner_report_url from being set, so the Send flow still works
- ✅ **Analytics 404** — Was "User not found" (404) because `test_user_mike` wasn't provisioned. The analytics error card now only shows "Owner/admin required" text when it's actually a 403.

### New pages built (all previously 404)
- ✅ `/intelligence/leaks` — **Profit Leaks** page: live analysis of pending estimates, stalled drafts, upsell gaps, low-margin jobs, slow send time. Fetches from `GET /api/estimates/`.
- ✅ `/intelligence/benchmark` — **BenchmarkIQ** stub with Phoenix Metro pricing comparison (preview data, live Q2 2026)
- ✅ `/intelligence/history` — **Property History** page, fetches from `GET /api/properties/`
- ✅ `/equipment/database` — Coming soon stub
- ✅ `/equipment/alerts` — Coming soon stub
- ✅ `/team/technicians` — Coming soon stub
- ✅ `/team/leaderboard` — Coming soon stub
- ✅ `/settings/pricing` — Coming soon stub
- ✅ `/settings/integrations` — Coming soon stub

### Seed data script
- Created `/scopesnap-api/scripts/seed_dev_data.py`
- Run with: `docker compose exec api python scripts/seed_dev_data.py`
- Seeds 8 recent properties + estimates at various funnel stages (deposit_paid, approved, viewed, sent, estimated) + 8 historical entries for 30-90 day trend charts
- Idempotent: skips if 5+ properties already exist

## Outstanding items

### To run seed data
```
docker compose exec api python scripts/seed_dev_data.py
```
Then refresh dashboard and analytics.

### Still to build (sidebar links that are now stubs)
- `/equipment/database` — Real equipment lookup from DB (needs equipment_models table populated)
- `/equipment/alerts` — Real aging alert logic (query equipment with install_year < now-12yr)
- `/team/technicians` — CRUD for team members (`GET/POST /api/teams/technicians`)
- `/team/leaderboard` — Stats per tech from estimates table
- `/settings/pricing` — Pricing rules editor (API: `GET/POST /api/pricing-rules/`)
- `/settings/integrations` — Webhooks/OAuth placeholder

### Known remaining issues
1. WeasyPrint may still fail silently in Docker — if PDF generation is important, run `docker compose exec api pip install weasyprint` and verify system libs (libpango, libcairo) are present
2. The `/r/[slug]/[shortId]` homeowner report viewer page — check if it exists and renders properly
3. Dashboard KPIs will show 0 until seed script is run

## Key files
- `scopesnap-web/app/(app)/estimate/[id]/page.tsx` — Estimate Builder (energy_savings fix)
- `scopesnap-web/app/(app)/analytics/page.tsx` — Analytics (error message fix)
- `scopesnap-web/app/(app)/intelligence/leaks/page.tsx` — NEW: Profit Leaks page
- `scopesnap-web/app/(app)/intelligence/benchmark/page.tsx` — NEW: BenchmarkIQ stub
- `scopesnap-web/app/(app)/intelligence/history/page.tsx` — NEW: Property History
- `scopesnap-web/components/ComingSoonPage.tsx` — NEW: Reusable coming soon component
- `scopesnap-api/api/estimates.py` — Markup PATCH fix + PDF resilience
- `scopesnap-api/scripts/seed_dev_data.py` — NEW: Dev data seeder

## Prototype files (for reference)
- `ScopeSnapAI/prototypes/ScopeSnap_Prototype_Demo.html`
- `ScopeSnap_Owner_Dashboard.html`
- `ScopeSnap_Homeowner_Report.html`
- Review report: `ScopeSnapAI/scopesnap-review-report.html`
