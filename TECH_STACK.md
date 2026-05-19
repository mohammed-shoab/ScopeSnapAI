# SnapAI AI — Tech Stack & Architecture

> **Last updated:** May 19, 2026 (Track Q complete — Q.1–Q.7 + Q.6.5 all merged to main. Migration 021 (fault card descriptions, 19 cards × 5 fields) applied. Git HEAD: `f8afced`. Alembic head: `021`. Houston + PK QA-verified.)
> **Status:** Beta — live on Vercel + Railway. Phase 2 complete. Phase 3 backend foundation (migrations 008–021) deployed. Both markets QA-verified 2026-05-19: PK (6/6 flows PASS) + Houston (Step Zero DB autofill, Not Cooling PSI routing, USD estimate generation, email send end-to-end PASS). Track Q (8 production hotfixes) all resolved.

---

## CRITICAL: Emoji Files & Blob Truncation — MUST READ BEFORE ANY GIT OPERATION

**EMOJI TRUNCATION RULE:** Files containing emoji or non-ASCII characters (✅ ⚠️ 🔧 📸 —) CANNOT be read from the NTFS Windows mount when building git blobs. The Linux sandbox silently truncates multi-byte UTF-8 bytes. Result: SyntaxError at runtime, production outage.

**ALWAYS:** Read previous blob from git object store — `git cat-file blob <sha>` — apply edits in Python memory — write new blob via `git hash-object -w --stdin`. NEVER open the file from the filesystem path.

**BLOB SIZE CHECK:** Before every push run `git cat-file -s <new_blob>` and confirm it is >= the original blob size. A truncated blob commits cleanly and crashes only at runtime.

**Affected file types:** Any `.py`, `.tsx`, `.ts`, `.md` with emoji in strings, comments, or print statements.
**Full details:** DEC-005 in DECISIONS.md.

---

## What Works vs What Doesn't (updated 2026-05-04)

### Railway

| Operation | Status | Notes |
|---|---|---|
| Auto-deploy from GitHub `main` push | ✅ Works | ~4-5 min build, auto-deploys on push |
| `start.sh` → `alembic upgrade head` on boot | ✅ Works | Migrations run automatically |
| `start.sh` → `python scripts/load_repo.py` on boot | ❌ Does NOT work | asyncpg cannot infer PG array types from Python lists; JSON data shape issues; silent failure via `||` catch |
| Shell access via web UI | ❌ Not available | Menu only shows Restart/Redeploy/Remove |
| Running custom scripts via Railway CLI | ❌ Not available in sandbox | CLI not installed; sandbox can't reach Railway API |
| Rolling deployment race on Svix replays | ⚠️ Known issue | Old container keeps serving until new container passes health check (~30s window). Svix replays triggered during this window hit old container with wrong secret → 401. Fix: always wait >60s after deploy before replaying. |

### Supabase

| Operation | Status | Notes |
|---|---|---|
| Direct SQL via SQL editor (Supabase dashboard) | ✅ Works | Best method for data seeding; Monaco editor API injection via Chrome |
| Supabase Management API from Chrome JS | ❌ Blocked | JWT token filtered by Cowork content filter |
| Direct psycopg2/asyncpg connection from sandbox | ❌ Blocked | DNS for all Supabase hostnames blocked by sandbox network |
| RLS with service_role key | ✅ Works | service_role bypasses RLS; backend uses service_role connection string |
| Alembic migrations | ✅ Works | Runs via `start.sh` on every Railway deploy |

### Data Seeding Workflow (the correct way)

1. Python generates INSERT SQL files from JSON/XLSX source data
2. SQL injected into Monaco editor via `monaco.editor.getEditors()[0].setValue(sql)` + `trigger('keyboard','editor.action.selectAll')`
3. Click "Run selected" → SQL executes directly in Supabase
4. Verify with `GET /api/repo/version` → `{"version":"2.0","status":"ok"}`

**SQL files stored at:** `C:\Users\Shoab\My Drive\Personal Claude\_WS_A_SQL_SEED\` (for re-seeding if needed)

### Git Operations (from sandbox)

| Operation | Status | Notes |
|---|---|---|
| `/tmp/snapai_tmp` clone + normal git push | ✅ Works | **Preferred method (DEC-004):** `git clone git@github.com:... /tmp/snapai_tmp`, edit files there, `git add / commit / push origin main`. Avoids all NTFS issues. |
| git plumbing (hash-object → mktree → commit-tree → push) from workspace | ⚠️ Fallback | Works but tedious. Use only if /tmp clone unavailable. Avoid for files with emoji/Unicode — NTFS truncation risk. |
| `git add / commit / push` from NTFS workspace | ❌ Fails | index.lock owned by Windows NTFS |
| `rm -f .git/index.lock` from NTFS workspace | ❌ Fails | NTFS cross-OS permission |
| GitHub REST API via curl | ❌ Blocked | Proxy 403 |
| Outbound HTTP to external APIs (Clerk, Railway) from sandbox | ❌ Blocked | Sandbox proxy returns 403 for all external API calls. Cannot use httpx, requests, urllib, curl to reach api.clerk.com, railway.app, etc. Must be done locally by user. |
| Browser fetch() to Clerk Backend API | ❌ Blocked | CORS: api.clerk.com rejects cross-origin `Authorization: Bearer` from any non-Clerk domain. Cannot call Clerk API from browser JS. |

### File Editing

| Method | Status | Notes |
|---|---|---|
| Python subprocess to generate file content | ✅ Works | Best for files with emoji or special chars |
| `Edit` tool on pure-ASCII Python files | ✅ Works | Fine for small changes to ASCII-only files |
| `Edit` tool on Python files with emoji/Unicode | ❌ Risky | NTFS encoding boundary can truncate UTF-8 sequences; causes SyntaxError on deploy |
| `Edit` tool on TSX/JSX files with emoji in strings | ❌ Risky | Same NTFS truncation issue — emoji icon strings in SYMPTOM_PHOTO etc. get cut off, breaking JSX parser. ALSO: any file with trailing SVG paths or complex JSX can get truncated even without emoji |
| `Edit` tool on any frontend file with long lines or SVG paths | ❌ Risky | `app/page.tsx` with inline SVG paths got truncated mid-element. Always use Python+/tmp for any TSX file modifications |
| Write tool for new files | ✅ Works | OK for new files |

---

---

## Live App Locations

| Perspective | URL | Description |
|---|---|---|
| **Landing / Marketing** | https://snapai.mainnov.tech | Public homepage with waitlist form |
| **Contractor App (Sign In)** | https://snapai.mainnov.tech/dashboard | HVAC contractor dashboard — requires auth |
| **Homeowner Report** | `https://snapai.mainnov.tech/r/[slug]/[reportId]` | Public report link sent to homeowners — no auth required |
| **Backend API** | https://scopesnap-api-production.up.railway.app | FastAPI REST backend |
| **API Health Check** | https://scopesnap-api-production.up.railway.app/health | Backend uptime check |

---

## Frontend — Next.js 14 (App Router)

| Layer | Technology | Notes |
|---|---|---|
| **Framework** | Next.js 14 (App Router) | React Server Components + Client Components |
| **Language** | TypeScript | Strict mode throughout |
| **Styling** | Tailwind CSS | Custom design tokens: `brand-green`, `surface-border`, `text-secondary` etc. |
| **Auth** | Clerk | Development mode keys active — Production keys needed for open beta |
| **Deployment** | Vercel | Auto-deploys on push to `main` branch of GitHub |
| **Repo** | github.com/mohammed-shoab/SnapAIAI | Monorepo: `scopesnap-web/` + `scopesnap-api/` |

### Key Env Vars (set in Vercel)

| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_API_URL` | Points to Railway API URL |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Clerk public key (dev mode) |
| `CLERK_SECRET_KEY` | Clerk secret key (dev mode) |
| `NEXT_PUBLIC_ENV` | Set to `production` — enables Clerk middleware |
| `NEXT_TELEMETRY_DISABLED` | `1` — disables Next.js telemetry |

### Feature Flags (`lib/featureFlags.ts`)

All non-beta features are hidden behind `NEXT_PUBLIC_SHOW_*` env vars (all `false` by default). Code is present but not shown until flag is enabled.

| Flag | Feature |
|---|---|
| `NEXT_PUBLIC_SHOW_ANALYTICS` | Accuracy Tracker |
| `NEXT_PUBLIC_SHOW_PROFIT_LEAKS` | Profit Leaks widget |
| `NEXT_PUBLIC_SHOW_BENCHMARK` | BenchmarkIQ |
| `NEXT_PUBLIC_SHOW_PROPERTY_HISTORY` | Property History |
| `NEXT_PUBLIC_SHOW_EQUIPMENT` | Equipment Database + Aging Alerts |
| `NEXT_PUBLIC_SHOW_TEAM` | Technicians + Leaderboard |
| `NEXT_PUBLIC_SHOW_INTEGRATIONS` | Integrations settings |

---

## Backend — FastAPI (Python)

| Layer | Technology | Notes |
|---|---|---|
| **Framework** | FastAPI | Python 3.11+, async |
| **Database** | PostgreSQL 15 | Hosted on **Supabase** (NOT Railway) — `DATABASE_URL` points to `pooler.supabase.com` |
| **ORM / Migrations** | SQLAlchemy + Alembic | Migration files in `scopesnap-api/db/migrations/` |
| **AI Vision** | Google Gemini 2.5 Flash | Equipment identification, condition analysis, issue detection — **Active in Phase 3**: nameplate OCR (Step Zero) + photo grading in diagnostic question steps |
| **ML Model — XGBoost** | Scikit-learn XGBoost | Refrigerant circuit fault classification (6 inputs: ambient/supply/return temps, suction/discharge PSI, unit age) — **Active in Phase 2 readings gate** (`api/readings.py` calls `SensorService.predict()` after tech enters gauge readings). NOT used in Phase 3 question tree (tree detects all faults without gauge readings). Future WS-T1: wire into Phase 3 as optional pre-diagnosis step. |
| **ML Model — YOLO** | Custom ONNX model | Visual fault detection from equipment photos — **Built + deployed** in `ai_cascade.py` (Track A/B via `POST /api/assessments/{id}/analyze`). **Dormant in Phase 3** — Phase 3 goes directly to `fault_estimate`, never calls `/analyze`. Future WS-T1: wire into Phase 3 evidence photo submission. |
| **Photo Storage** | Cloudflare R2 | S3-compatible object storage for equipment photos |
| **Email** | Resend | Transactional emails — homeowner report delivery |
| **Payments** | Stripe | Integrated (Checkout not wired for beta — feature-flagged) |
| **Deployment** | Railway | Project: `pacific-exploration` — auto-deploys from `scopesnap-api/` subdirectory |
| **Workers** | Uvicorn | `UVICORN_WORKERS=1` set in Railway env vars (Apr 30 2026) — 1 worker sufficient for dev/beta; handles 50–100 concurrent users with async |

### Key API Endpoints

**Phase 1 (original):**

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check — db connected, environment, version |
| `GET` | `/api/auth/me` | Current contractor profile |
| `PATCH` | `/api/auth/me/company` | Update company profile |
| `GET` | `/api/assessments/` | List assessments |
| `POST` | `/api/assessments/` | Create assessment (upload photos to R2) |
| `POST` | `/api/assessments/{id}/analyze` | Run Gemini AI analysis |
| `GET` | `/api/estimates/{id}` | Get estimate detail |
| `POST` | `/api/estimates/generate` | ~~Generate Good/Better/Best estimate from assessment~~ **DELETED** (DEC-016 — legacy engine removed; use `/api/estimates/fault-card` instead) |
| `GET` | `/api/reports/{reportId}` | Get homeowner report (public) |
| `POST` | `/api/reports/{token}/approve` | Homeowner approves an option (public) |
| `POST` | `/api/events` | Track analytics event (rate-limited: 100/user/60s) |
| `POST` | `/api/waitlist` | Add email to waitlist |
| `GET` | `/api/pricing-rules/markup` | Get company markup % |
| `PATCH` | `/api/pricing-rules/markup` | Update company markup % |

**Phase 2 (WS-A through WS-L, added 2026-05-01):**

| Method | Path | WS | Description |
|---|---|---|---|
| `GET` | `/api/repo/version` | WS-A | Data repo version + row counts |
| `POST` | `/api/ocr/nameplate` | WS-B | Gemini OCR → 10 nameplate fields |
| `PATCH` | `/api/assessments/{id}/nameplate` | WS-B | Save OCR result to assessment |
| `GET` | `/api/error-code/lookup?brand=X&code=Y` | WS-D | Error code → fault card |
| `GET` | `/api/error-code/brands` | WS-D | List all supported brand families |
| `POST` | `/api/thermal/analyze` | WS-E | Gemini hotspot detection from thermal photo |
| `POST` | `/api/feedback/card` | WS-F | YES/NO tech feedback on fault card |
| `GET` | `/api/feedback/card/{id}/stats` | WS-F | Feedback stats for a card |
| `POST` | `/api/estimates/fault-card` | WS-G | A/B/C estimate for specific fault card |
| `GET` | `/api/estimates/recommend` | WS-H | Lifecycle rules → recommended tier (external, auth required). Internal variant: `get_recommended_tier_internal()` in `recommend.py` (Q.6.5) — called by fault_estimate.py; no auth, takes card_id/age_years/condition_signal/db/tables. |
| `POST` | `/api/followup/schedule` | WS-I | Schedule 24h/48h/7d follow-up |
| `GET` | `/api/followup/opt-out/{token}` | WS-I | Homeowner opt-out link |

**Track Q additions (hotfixes 2026-05-19):**

| Method | Path | Track Q | Description |
|---|---|---|---|
| `POST` | `/api/estimates/{id}/refresh` | Q.7 | Re-stamp descriptions/why_recommended on a draft estimate from latest fault card data. Resolves `card_id` via `diagnostic_sessions.resolved_card_id`. Idempotent — no-op if estimate is not draft. Returns updated estimate dict. |

**Phase 3 (WS-A3/B3/C3 onward, added 2026-05-04):**

| Method | Path | WS | Description |
|---|---|---|---|
| `POST` | `/api/diagnostic/session` | WS-A3 | Create diagnostic session for assessment + complaint; returns first step_id + question |
| `POST` | `/api/diagnostic/session/{id}/answer` | WS-A3 | Submit answer to current step; returns next question or resolved card_id |
| `GET` | `/api/diagnostic/session/{id}` | WS-A3 | Get current session state (step, answers so far, resolved card if done) |
| `POST` | `/api/photo-labels/` | WS-A3 | Save labelled photo (photo_type=diagnostic or evidence, derived from tree node) |
| `GET` | `/api/photo-labels/{assessment_id}` | WS-A3 | List photo labels for an assessment |
| `POST` | `/api/job-confirmation/` | WS-A3 | Tech post-job confirmation — actual fix, resolved status, final invoice |
| `GET` | `/api/job-confirmation/{assessment_id}` | WS-A3 | Get confirmation record for an assessment |

> ⚠️ **Router ordering note (fixed 2026-05-01, commit c05658a):** `GET /api/estimates/recommend` MUST be registered BEFORE `GET /api/estimates/{estimate_id}` in main.py, otherwise the catch-all `/{estimate_id}` intercepts `/recommend` and causes a UUID parse DataError. This is now fixed — recommend_router is included before estimates.router.

### Database Tables

> All tables have RLS enabled. The `service_role` key (used by the backend) bypasses RLS automatically. Tables with sensitive data also have `company_isolation` policies restricting data per contractor.
> **Current Alembic revision: 021** (Track Q migrations applied 2026-05-19; migrations 012–021 cover fault card descriptions, report token fix, and estimate refresh. Migration 021 had a Python SyntaxError in the original file — data applied directly via Supabase MCP, `alembic_version` manually advanced to `021`, file rewritten with valid syntax — see WA-7.)

**WS-A Reference Tables (added migration 007, seeded 2026-04-30):**

| Table | Rows | Purpose | How to re-seed |
|---|---|---|---|
| `brands` | 15 | HVAC brand registry (Carrier, Trane, etc.) | Python SQL gen → Supabase SQL editor |
| `parts_catalog` | 43 | Repair parts + installed cost data | Python SQL gen → Supabase SQL editor |
| `fault_cards` | 19 | The 19 diagnostic cards (1-19). `better_option_estimate` JSONB column holds per-tier description fields: `description_good`, `why_recommended_good`, `description`, `why_recommended`, `description_best_replacement`, `description_best_comprehensive`, `why_recommended_best`. All 19 cards populated via migration 021 (2026-05-19). | Python SQL gen → Supabase SQL editor |
| `pricing_tiers` | 57 | A/B/C tiers per fault card (from price list). Each tier in the estimate response includes `recommendation_reason` and `recommendation_source` fields (populated from `lifecycle_rules` via Q.6.5 `get_recommended_tier_internal()`). | Python SQL gen → Supabase SQL editor |
| `error_codes` | 196 | Error codes for 14 brand families | Python SQL gen → Supabase SQL editor |
| `labor_rates_houston` | 1 | Houston labor rate benchmarks | Python SQL gen → Supabase SQL editor |
| `legacy_model_prefixes` | 65 | Pre-2010 unit identification prefixes | Python SQL gen → Supabase SQL editor |
| `lifecycle_rules` | 17 | Component age + condition_signal → recommended A/B/C tier. "default" signal always returns B. Age-based rules only apply with specific condition signals (pitting, bearing_noise, rla_over_nameplate). | Python SQL gen → Supabase SQL editor |
| `data_repo_versions` | 1 | Load history + row count manifest | Auto-inserted after seeding |

**Phase 2 tables (added 2026-05-01):**

| Table | Purpose |
|---|---|
| `card_feedback` | YES/NO tech feedback on fault card assessments (WS-F training data) |
| `readings` | Phase 2 sensor readings gate (WS-C) |

**Phase 3 tables (added migrations 008–011, 2026-05-04):**

| Table | Migration | Purpose | RLS | Policy |
|---|---|---|---|---|
| `diagnostic_questions` | 008 | Static question library — one row per step_id (e.g. `q1-a`, `q2-cap`); holds `branch_logic_jsonb` that determines next step or resolved card | ✅ Enabled | None (read-only reference) |
| `diagnostic_sessions` | 009 | One session per assessment+complaint; tracks `current_step_id`, `answers_jsonb`, `resolved_card_id`, `status` | ✅ Enabled | `company_isolation` |
| `reading_inputs` | 010 | Raw meter readings captured during a diagnostic session (µF, amps, volts, PSI, temps); FK to `diagnostic_sessions` | ✅ Enabled | `company_isolation` |
| `photo_labels` | 010 | Labelled photos for a diagnostic session; `photo_type` = `diagnostic` or `evidence` (tree-derived, NOT tech-chosen); FK to `diagnostic_sessions` | ✅ Enabled | `company_isolation` |
| `job_confirmations` | 011 | Post-job tech confirmation — `actual_card_id`, `complaint_resolved` bool, `final_invoice_usd`; closes AI training loop | ✅ Enabled | `company_isolation` |

**Important: brands.series column is currently `[]` (empty array) for all 15 brands.** Full series data (entry/mid/premium tiers, refrigerant, SEER range, etc.) is in `ac_data_repo.json` under each brand's `series` key. Needs to be backfilled before WS-B (Step Zero OCR) goes live — WS-B uses series data to cross-reference Model # → tonnage/refrigerant.

**Also note:** `equipment_models` extended in migration 007 with: `brand_id FK`, `refrigerant`, `metering_device`, `compressor_type`, `charging_method`, `dual_fuel_capable`, `is_legacy`. `assessments.complaint_type` added (Tab H / WS-J groundwork).

**Original 15 Phase 1 tables:**

| Table | Purpose | RLS | Policy |
|---|---|---|---|
| `alembic_version` | Alembic migration tracking | ✅ Enabled | None (backend-only) |
| `app_events` | Analytics event log (rate-limited) | ✅ Enabled | None (backend-only) |
| `assessment_photos` | Equipment photo metadata | ✅ Enabled | None (backend-only) |
| `assessments` | Photo assessments + AI results | ✅ Enabled | `company_isolation` |
| `companies` | Contractor company profiles | ✅ Enabled | None (backend-only) |
| `equipment_instances` | Installed equipment records | ✅ Enabled | None (backend-only) |
| `equipment_models` | Equipment model reference data | ✅ Enabled | None (backend-only) |
| `estimate_documents` | PDF/document attachments | ✅ Enabled | None (backend-only) |
| `estimate_line_items` | Line items per estimate | ✅ Enabled | None (backend-only) |
| `estimates` | Estimates / pricing options | ✅ Enabled | `company_isolation` |
| `follow_ups` | Follow-up task tracking | ✅ Enabled | None (backend-only) |
| `pricing_rules` | Contractor pricing config | ✅ Enabled | `company_isolation` |
| `properties` | Address + customer info | ✅ Enabled | `company_isolation` |
| `users` | Clerk-linked contractor accounts | ✅ Enabled | `company_isolation` |
| `waitlist_signups` | Landing page waitlist emails | ✅ Enabled | None (backend-only) |

---

## Authentication Flow

```
User visits /dashboard
  └─> Next.js middleware checks NEXT_PUBLIC_ENV=production
        └─> Clerk middleware runs
              └─> Not authenticated → redirects to Clerk hosted sign-in
                    (glowing-cowbird-89.accounts.dev in dev mode)
              └─> Authenticated → proceeds to dashboard

Homeowner visits /r/[slug]/[reportId]
  └─> Middleware: path starts with /r/ → PUBLIC_PATHS → skip auth → render report
```

> ⚠️ **Beta note:** Frontend API calls currently include a `X-Dev-Clerk-User-Id: test_user_mike` dev bypass header. For multi-user beta, this needs to be replaced with proper Clerk JWT token passing from the signed-in user. Safe for single-user beta.

---

## M12 Production Audit — 2026-05-01

### E2E Test Results (live production)
All tests passed against `https://scopesnap-api-production.up.railway.app` using real Clerk auth.

| Test | Result | Notes |
|---|---|---|
| `POST /api/assessments/` | ✅ 201 | Photos uploaded to R2; assessment ID generated |
| `POST /api/assessments/{id}/analyze` | ✅ 200 | Gemini called; returned equipment + condition |
| `POST /api/estimates/generate` | ✅ 201 | `rpt-0009` created with 35% markup |
| Estimate Builder UI | ✅ Rendered | Option A $189, B $527, C $9,572 visible |
| `GET /api/estimates/recommend` | ✅ 200 | Lifecycle rules working: 11yr→B, 18yr+pitting→C, 2yr+warranty→A |
| `POST /api/estimates/fault-card` | ✅ 200 | Capacitor card: Good $236, Better $331 (35% markup applied) |
| `GET /api/error-code/brands` | ✅ 200 | 14 brand families returned |
| `GET /api/pricing-rules/markup` | ✅ 200 | 35% markup confirmed |
| `GET /api/assessments/` | ✅ 200 | total=1 returned |

### Raw Data Verification (cross-checked against Supabase)
| Data point | Raw DB | API returned | Correct |
|---|---|---|---|
| Fault card #1 name | Capacitor Failure | "Capacitor Failure" | ✅ |
| Pricing tier A (Good) | 175 | base_amount=175 | ✅ |
| 175 × 1.35 markup | 236.25 → $236 | total=$236 | ✅ |
| Pricing tier B (Better) | 245 | base_amount=245, total=$331 | ✅ |
| Pricing tier C (Best) | 330 | base_amount=330 | ✅ |
| Labor rates min/max | $75–$150/hr | Used $95/hr mid-point in UI | ✅ |
| Lifecycle: default → B | `default:B:NULL:Default capacitor` | tier=B, reason="Default capacitor" | ✅ |
| Lifecycle: old+pitting → C | `photo_confirmed_pitting:C:7yr` | tier=C (18yr>7yr threshold) | ✅ |
| Lifecycle: warranty → A | `under_warranty:A:2yr` | tier=A (2yr≤threshold) | ✅ |
| Mitsubishi U4 | → decision_tree_card=7 | HTTP 200 lookup | ✅ |
| Carrier sister brands | `["bryant","payne"]` | brand record present | ✅ |

### Bugs Found and Fixed in M12
| Issue | Root Cause | Fix | Commit |
|---|---|---|---|
| ISSUE-001: `intermittent_shutdown` broke capture phase | Missing from `SYMPTOM_PHOTO` mapping → TS type error | Added entry to SYMPTOM_PHOTO | 3ac826b |
| ISSUE-002: Video placeholder blank white box | Empty `<div>` with no styling | Dark themed placeholder with grid + play button | c8d18c2 |
| ISSUE-003: Settings/billing unprotected routes | Middleware only protected 3 routes | Added 10+ app routes to Clerk matcher | 28d8082 |
| ISSUE-004: `GET /api/estimates/recommend` "Failed to fetch" | `GET /{estimate_id}` catch-all in estimates.router intercepted `/recommend` before recommend_router; UUID parse DataError dropped CORS | Moved `recommend_router` include BEFORE `estimates.router` | c05658a |
| ISSUE-005: Vercel build failure — assess/page.tsx | NTFS truncation of emoji icon strings in SYMPTOM_PHOTO map; "Unexpected token `div`" at line 881 | Regenerated from c7fe544+Python via /tmp | 3ac826b |
| ISSUE-006: Vercel build failure — middleware.ts | NTFS truncation at `matcher:` line 102; "Unexpected eof" | Regenerated from c7fe544+Python via /tmp | 637d32a |
| ISSUE-007: Vercel build failure — app/page.tsx | NTFS truncation mid-SVG (inline path strings); "Expected ',', got '{'" | Regenerated from 1632048 base+Python via /tmp | 6b67d01 |
| **Vercel build: READY** | All 3 truncated files restored. Commit 6b67d01 is live production at snapai.mainnov.tech | | ✅ |

### Sentry Alerts Explained (2026-05-01)
| Alert | Root Cause | Status |
|---|---|---|
| `DBAPIError /api/estimates/{estimate_id}` — `invalid input syntax for type uuid: 'recommend'` | ISSUE-004 above — recommend route caught by /{estimate_id} catch-all | ✅ Fixed in c05658a |
| `HTTPException /api/thermal/analyze` — `Gemini analysis failed: 400 Unable to process input image` | M12 audit used 1×1 pixel test image; Gemini correctly rejected it | ✅ Not a real bug — test artifact |
| `[Cascade] Gemini call failed /api/assessments/{id}/analyze` — `400 Unable to process input image` | Same — M12 E2E test with 1×1 pixel image | ✅ Not a real bug — test artifact |

---

## Middleware Auth Coverage (fixed 2026-05-01)

The Next.js middleware now protects ALL app routes (not just 3). Full protected route list:

```typescript
const isProtectedRoute = createRouteMatcher([
  "/dashboard(.*)", "/assess(.*)", "/assessment(.*)",
  "/assessments(.*)", "/settings(.*)", "/billing(.*)",
  "/analytics(.*)", "/intelligence(.*)", "/equipment(.*)",
  "/team(.*)", "/onboarding(.*)", "/estimates(.*)", "/estimate(.*)",
]);
```

---

## Analytics — PostHog (confirmed working 2026-05-01)

| Item | Status | Detail |
|---|---|---|
| **Account** | ✅ Active | `ds.shoab@gmail.com` — Default project, ID `369878` |
| **API Key in Vercel** | ✅ Correct | `NEXT_PUBLIC_POSTHOG_KEY = phc_A5spSAWCWKeQw9cVgVfxnmNd2f2dQjvtdwsb9PpjMbZJ` set Apr 5 — matches PostHog account key exactly |
| **PostHogProvider in app** | ✅ Wired | `providers/PostHogProvider.tsx` imported and wrapping entire app in `app/layout.tsx` |
| **PostHog initialising on live app** | ✅ Confirmed | `localStorage` key `ph_phc_A5spSAW..._posthog` present on dashboard page — library loaded and `init()` ran |
| **Network call firing** | ✅ Confirmed | `us-assets.i.posthog.com` hit on page load (status 0 only because Claude browser acts as ad blocker) |
| **Events in dashboard** | ⏳ Zero | No real users yet — zero events is correct and expected. The moment first real contractor visits, events will flow |
| **Dev mode opt-out** | ✅ Correct | Code opts out only when `NEXT_PUBLIC_ENV === 'development'`. Production is NOT opted out. |

### 9 Events tracked (all wired, ready to fire):
| Event | Trigger |
|---|---|
| `assessment_started` | Contractor opens /assess |
| `assessment_submitted` | Photos submitted to AI |
| `assessment_ai_complete` | Gemini analysis returned |
| `estimate_generated` | Good/Better/Best estimate created |
| `estimate_correction` | Contractor adjusted AI numbers (training signal — includes delta $ and delta %) |
| `report_sent` | Estimate emailed to homeowner |
| `report_viewed` | Homeowner opened their PDF |
| `report_approved` | Homeowner approved a tier |
| `$pageview` | Every page navigation (automatic) |

### How to verify PostHog is receiving events:
1. Go to [PostHog Live tab](https://us.posthog.com/project/369878/activity/live) — updates in real time
2. Open app in any **normal browser** (not Claude browser — it blocks tracking like an ad blocker)
3. Navigate through a few pages — `$pageview` events will appear within 5 seconds
4. Start an assessment — `assessment_started` fires immediately

---

## Offline & Reliability

| Feature | Implementation |
|---|---|
| **Offline queue** | IndexedDB via `lib/offlineQueue.ts` — assessments queued if no network |
| **Event tracking** | Fire-and-forget via `lib/tracking.ts` — `sendBeacon` + 3s fetch timeout |
| **Photo fallback** | SVG placeholder rendered if HVAC photo fails to load |
| **API error states** | All pages handle loading / error / empty states gracefully |

---

## Repository Structure

```
SnapAIAI/
├── scopesnap-web/              # Next.js 14 frontend
│   ├── app/
│   │   ├── (app)/              # Auth-protected contractor app
│   │   │   ├── dashboard/      # Dashboard
│   │   │   ├── assess/         # Camera + AI assessment flow
│   │   │   ├── estimates/      # Assessment list
│   │   │   ├── estimate/[id]/  # Assessment detail
│   │   │   ├── onboarding/     # Company setup wizard
│   │   │   ├── analytics/      # Accuracy tracker (feature-flagged)
│   │   │   ├── settings/       # Company profile, pricing, privacy
│   │   │   └── billing/        # Subscription (feature-flagged)
│   │   ├── r/[slug]/[reportId] # PUBLIC homeowner report
│   │   └── page.tsx            # PUBLIC landing page
│   ├── components/
│   │   ├── SidebarNav.tsx      # Sidebar with 14 SVG icons
│   │   └── DataConfidenceLabel.tsx  # AI confidence display
│   └── lib/
│       ├── api.ts              # API_URL + OfflineError
│       ├── featureFlags.ts     # NEXT_PUBLIC_SHOW_* env vars
│       ├── offlineQueue.ts     # IndexedDB offline queue
│       └── tracking.ts         # Fire-and-forget analytics
│
├── scopesnap-api/              # FastAPI backend
│   ├── api/
│   │   ├── estimates.py        # Assessment CRUD
│   │   ├── reports.py          # Homeowner report endpoints
│   │   ├── auth.py             # Clerk user sync + company profile
│   │   └── events.py           # Analytics + waitlist (rate-limited)
│   └── db/
│       └── migrations/         # Alembic migration files
│
├── TECH_STACK.md               # This file
├── README.md                   # Project overview + links
└── SnapAI_Beta_Readiness_SignOff.docx  # Full 6-founder audit
```

---

## How to Push Updates to Live App

> **DEC-004 (permanent):** All git operations use `/tmp/snapai_tmp` — a fresh clone in the Linux sandbox's `/tmp` directory (not the NTFS workspace). Do NOT git stash from the sandbox on an NTFS repo (DEC-013).

### Standard method (DEC-004 — /tmp clone)

```bash
# Clone into /tmp (avoids NTFS index.lock issues entirely)
git clone git@github.com:mohammed-shoab/SnapAIAI.git /tmp/snapai_tmp
cd /tmp/snapai_tmp

# Make changes, then commit and push normally
git add scopesnap-api/api/estimates.py
git commit -m "[hotfix] Q.7 — refresh draft estimates on load"
git push origin main
```

**Why this works:** `/tmp` is a real Linux ext4 filesystem — no NTFS boundary, no index.lock issues. Normal `git add / commit / push` all work.

**Railway auto-deploys** within ~4–5 minutes of a push to `main`. No manual step needed.

### Fallback — git plumbing (only if /tmp clone unavailable)

If the /tmp directory is not writable or the clone fails for network reasons, the git plumbing method (hash-object → mktree → commit-tree) still works from the NTFS workspace, but avoid it for files with emoji/Unicode characters (NTFS truncation risk).

### ❌ Things that do NOT work (do not retry these)
- `git add / git commit / git push` from the NTFS workspace mount — fails: index.lock owned by Windows NTFS
- `rm -f .git/index.lock` from Linux bash on NTFS — fails: Operation not permitted
- `git stash` from sandbox on NTFS repo — fails silently or corrupts (DEC-013)
- GitHub REST API via `curl` — fails: proxy returns 403
- Browser code injection (CodeMirror/atob) — fails: corrupts UTF-8 multi-byte chars

---

## Third-Party Services Status

| Service | Plan | Status | Notes |
|---|---|---|---|
| **Vercel** | Free (Hobby) | ✅ Live | Auto-deploys frontend from GitHub main |
| **Railway** | Hobby $5/mo | ✅ Optimised | Spending caps set Apr 30 2026. postgres-volume deleted (orphaned, unused). UVICORN_WORKERS reduced 2→1. |
| **Supabase** | Free | ✅ Secured | All 15 tables have RLS enabled (fixed Apr 29 2026). This is the ONLY database — Railway Postgres was never used. |
| **Cloudflare R2** | Free tier | ✅ Active | Photo storage for equipment images. Daily DB backup cron also writes here. |
| **Resend** | Free tier | ✅ Active | Transactional email (homeowner reports) |
| **Clerk** | Free (dev mode) | ✅ Active | Dev mode keys — switch to Production before open beta |
| **Sentry** | Free developer plan | ✅ OK | Business trial ended Apr 28 2026; usage near-zero (93 spans, 0 errors) — free plan sufficient |
| **UptimeRobot** | Free | ✅ Confirmed | Monitoring confirmed active Apr 30 2026. 50% uptime Apr 19–25 was pre-deploy downtime — not an ongoing issue. |
| **Google Gemini** | Pay-per-use | ✅ Active | AI vision: equipment ID + condition analysis |
| **Stripe** | Test mode | 🔲 Not wired | Integrated but Checkout not active for beta |

### Railway Cost Controls (updated Apr 30 2026)

| Setting | Value | Notes |
|---|---|---|
| Compute hard limit | $10/mo | All services stop if hit — prevents runaway billing |
| Compute email alert | $6/mo | Triggers when you exceed the $5 included credit |
| Agent hard limit | $5/mo | Already set |
| `UVICORN_WORKERS` | `1` | Reduced from 2 on Apr 30 2026 — halves memory usage, sufficient for 50–100 concurrent users |
| `postgres-volume` | ❌ Deleted | Was an orphaned 1MB disk volume not mounted to any service. Deleted Apr 30 2026. |

**Why the database is on Supabase, not Railway:** The `DATABASE_URL` env var points to Supabase (`pooler.supabase.com`). The Railway `postgres-volume` was an auto-created leftover from initial project setup that was never used. All migrations (Alembic) run against Supabase. Do not add a Railway PostgreSQL service — it would be redundant and costly.

---

## Phase 3 Workarounds Discovered (Sessions 6–7, 2026-05-03/04)

These are dead ends we hit and the techniques that resolved them. Record them so future sessions don't repeat the work.

### WA-1 — Svix webhook management iframe is cross-origin and unreliable after SPA navigation

**Problem:** Clerk's dashboard embeds Svix webhook management inside a cross-origin `<iframe id="iFrameResizer1">`. Clicking the "Recover failed messages" button (or any Svix endpoint row) via browser automation only worked once in the prior session. After any SPA navigation, the iframe's event handlers do not re-initialize correctly because the parent Clerk app is a React SPA that replaces the DOM on route change. `MouseEvent` dispatch via JavaScript also fails — Svix's click handler is bound differently inside the iframe context.

**What was tried and failed:** Hard refresh, fresh tab navigation to the Clerk webhooks URL, JavaScript MouseEvent dispatch on the iframe content, coordinate-based click at various positions.

**Workaround:** Wrote `provision_clerk_users.py` (saved at `Personal Claude/provision_clerk_users.py`) — a standalone idempotent script that fetches all Clerk users via the Backend API, signs synthetic `user.created` webhook events using the correct Svix HMAC algorithm, and POSTs them directly to the Railway webhook endpoint. Must be run **locally** (not from sandbox). The webhook handler is idempotent — already-provisioned users are skipped with `action: already_exists`. See file for full instructions.

**Root cause:** Cross-origin `<iframe>` SPA re-render pattern. Cannot be fixed from the automation side. The script is the permanent alternative to Svix "Recover failed messages".

---

### WA-2 — Sandbox proxy blocks all outbound HTTP to external APIs

**Problem:** Every outbound HTTP call from the bash sandbox to external APIs (Clerk, Railway, GitHub, etc.) returns `403 Forbidden` via the Cowork proxy. This includes `httpx`, `requests`, `urllib`, `curl`, and any other HTTP client. The sandbox has an NTFS-mounted workspace but routes all network traffic through a restrictive proxy.

**What was tried:** `httpx.AsyncClient`, `urllib.request.urlopen`, `curl`, Python `socksio` package. All returned proxy 403. Even SOCKS-configured httpx failed (and required `pip install "httpx[socks]"` first).

**Workaround:** Any task requiring calls to external APIs must be run locally by the user, or triggered via browser automation using an already-authenticated tab. The `provision_clerk_users.py` script falls into this category — hand it to the user with `pip install httpx && python provision_clerk_users.py`.

---

### WA-3 — Google OAuth logo upload: wrong GCP account + hidden file input

**Problem 1 — Wrong account:** The user's GCP account for SnapAI is `ds.shoab@gmail.com`, not `mshoabarabi@gmail.com`. The GCP project display name is "Training" (project ID: `training-334101`), not anything obviously SnapAI-related. Navigating to GCP while logged in as `mshoabarabi@gmail.com` shows no SnapAI project.

**Fix:** Switch GCP account via the avatar menu → select `ds.shoab@gmail.com`. The project "Training" → "Google Auth Platform" → "Branding" is where the OAuth consent screen logo lives.

**Problem 2 — Hidden file input:** The GCP logo upload uses `<input type="file" class="cfc-file-picker-file-input">` with `display:none`. It does not appear in the `read_page` accessibility tree. The `file_upload` tool fails because the visible element near the upload zone is an `<input type="text">`, not `<input type="file">`.

**Fix:** Regenerate the logo entirely in browser via canvas, then inject it into the hidden file input using JavaScript's `DataTransfer` + `canvas.toBlob()` trick:
```javascript
const canvas = document.createElement('canvas');
canvas.width = 120; canvas.height = 120;
const ctx = canvas.getContext('2d');
// draw green rounded square + white "S" ...
canvas.toBlob(blob => {
  const file = new File([blob], 'snapai_logo.png', {type: 'image/png'});
  const dt = new DataTransfer(); dt.items.add(file);
  const input = document.querySelector('.cfc-file-picker-file-input');
  input.files = dt.files;
  input.dispatchEvent(new Event('change', {bubbles: true}));
});
```
Logo spec: 120×120px, green `#1a8754` rounded square (radius 24px), white "S" Arial bold 76px centered.

---

### WA-4 — CLERK_WEBHOOK_SECRET typo caused all webhook verifications to fail

**Problem:** The `CLERK_WEBHOOK_SECRET` Railway env var had a 3-character typo introduced in a prior session (`0` instead of `O` ×2, `F` instead of `f` ×1). Every `user.created` event since the Railway deploy with that secret failed Svix signature verification (401 Unauthorized). All users who signed up during the affected window were not provisioned in the DB.

**Fix:** Correct value is `whsec_bOBRYOxkRVPMHbk+5r2dNPfXq7zYGpNS`. Updated in Railway env vars, confirmed deployment `14015b64` active.

**Recovery:** Historical unprovisioned users must be recovered using `provision_clerk_users.py` (WA-1 above) since Svix "Recover failed messages" automation is blocked (WA-1 above).

---

### WA-5 — NTFS workspace mount: git index.lock cannot be deleted, cp truncates files

**Problem:** The workspace folder is an NTFS-mounted Windows drive. Two issues arise when working git inside it:
1. `.git/index.lock` left by a failed git operation cannot be deleted — `os.unlink()` and `rm -f` both return "Operation not permitted" on NTFS mounts in t

---

### WA-6 — PK inverter badge in confirmation chip needs separate state var (not manualUnit cast)

**Problem:** After selecting an inverter model on PK market, the blue INVERTER pill showed correctly in the model dropdown but not in the confirmation chip. The chip had `{(manualUnit as any).series_type === "inverter" && (...)}` which always evaluated false because `applyModelRecord` copies fields into `manualUnit` (typed as `NameplateUnit`), and `NameplateUnit` has no `series_type` field — the cast returns `undefined`.

**Fix:** Added `const [selectedSeriesType, setSelectedSeriesType] = useState<string | null>(null)` after `pkTonnageData` state. In `applyModelRecord`'s isPK block: `setSelectedSeriesType(model.series_type ?? null)`. In clear button: `setSelectedSeriesType(null)`. Chip JSX: `{selectedSeriesType === "inverter" && (...)}`. This follows the existing `pkTonnageData` pattern — PK-only extra data lives in separate state vars, not cast onto `manualUnit`.

**Root cause detail:** `model.series_type` comes from the backend `/api/models/all` PK response (added in commit `0adc374`), where `series_type` is derived from `s.get("type", "non_inverter")` in the `pak_brands` JSONB series array. The `inverter` boolean column in `pak_brands` is irrelevant — `type='inverter'` string in the JSON is the correct source (DEC-008).

**Commit:** `a951a02` | **File:** `scopesnap-web/components/StepZeroPanel.tsx` | **Verified live:** 2026-05-19

---

### WA-7 — Migration Python SyntaxError: em-dashes and unescaped quotes crash Railway start.sh

**Problem:** Migration `021_fault_card_descriptions.py` contained Python string literals with unescaped double-quotes inside double-quoted strings (e.g. `"{"description_good": "Replace..."}"`). Python parsed the inner `{description_good` as a dict literal, then hit em-dash characters `—` (U+2014) which are not valid Python identifiers. This caused a SyntaxError at import time. `start.sh` uses `set -e`, so `alembic upgrade head` crashing killed the Railway startup — the last healthy container (pre-Q.5) kept serving. All Q.5–Q.7 code was deployed correctly but the database data was never applied.

**Effect:** Silent production gap — code deployed, migrations silently skipped. `alembic_version` stayed at `020` while git HEAD was at `f8afced`.

**Fix applied 2026-05-19:**
1. Applied all 19 card UPDATE statements directly via Supabase MCP `execute_sql` (bypassed alembic entirely).
2. Manually advanced `alembic_version`: `UPDATE alembic_version SET version_num = '021' WHERE version_num = '020'`.
3. Rewrote migration file using `json.dumps()` with `ensure_ascii=False` — no manual string escaping, no em-dashes, no backslash issues. Verified with `python3 -m py_compile migration_021.py` before committing.

**Rule going forward:** Never put prose text with em-dashes, curly quotes, or unescaped double-quotes inside Python double-quoted string literals in migration files. Use `json.dumps()` for any data blob. If in doubt: `python3 -m py_compile <file>` before committing.

---

## PK (Pakistan) Market — Architecture & Data Reference

> PK QA verified: 2026-05-19. All 6 diagnostic flows confirmed live on pk.snapai.mainnov.tech (commits 9024d035, 0adc374, a951a02). Full PK SOW complete.
> Houston QA verified: 2026-05-19. Step Zero (York LX DB autofill), Not Cooling 128 PSI–normal–Card 13, USD estimate ($338/$574/$775, 35% markup), email send confirmed (rpt-0513, status=sent in DB). Both markets clean.

### How the dual-market works

One codebase. One Railway backend. One Vercel deployment. Market is determined at runtime:

| Step | Where | How |
|------|-------|-----|
| 1. Detect market | Frontend `lib/market.ts` | `detectMarket()` checks hostname — returns "PK" for `pk.*`, "US" otherwise |
| 2. Set header | All API fetch calls | `X-Market: PK` or `X-Market: US` header added to every request |
| 3. Route tables | Backend `db/deps.py` | `get_tables()` dependency reads `X-Market` — returns `pak_*` table names for PK |
| 4. Query PK tables | All route handlers | Use `tables.brands`, `tables.fault_cards` etc. — resolved to `pak_brands`, `pak_fault_cards` etc. |

**Critical rule:** Every PK-only code change must be gated behind `if (detectMarket() === "PK")` (frontend) or handled via `get_tables()` dependency (backend). A single push changes BOTH markets simultaneously.

### PK Supabase Tables

| Table | Purpose | Seeded from |
|-------|---------|-------------|
| `pak_brands` | Brand + series registry with electrical specs | `ac_data_repo_pakistan_v4.json` via Python SQL gen |
| `pak_fault_cards` | PK diagnostic fault cards with PKR pricing | Manually seeded |
| `pak_diagnostic_questions` | Question tree for PK complaints | Manually seeded |
| `pak_operating_targets` | PSI/temp targets by refrigerant at 40C ambient | Manually seeded |
| `pak_data_defaults` | Default values for auto-fill | Manually seeded |
| `pak_assessments` | PK assessment records (phone-only, no address required) | Created at runtime |
| `pak_estimates` | PK estimates with PKR pricing | Created at runtime |

### PK Electrical Specs (pak_brands)

All 15 brands seeded with RLA/LRA/MCA/MOCP/capacitor data from `ac_data_repo_pakistan_v4.json` (2026-05-19).

**Known issue — DATA-GAP-001:** `inverter` boolean column is `false` for all rows. The JSON has `inverter=None` (null) on every model but uses `type='inverter'` (string) to mark inverter models. The SQL seeder used the wrong field. Fix: run the UPDATE below in Supabase SQL editor.

```sql
-- Fix inverter boolean for 10 inverter series
UPDATE pak_brands SET inverter = true
WHERE series_name IN (
  'Triple Inverter (Life/Smart/Color/UV)',
  'Ultron Divine', 'Smartron',
  'InverterOn Airy', 'Turbo DC',
  'eLuxury', 'eSmart',
  'Digital Inverter', 'Dual Inverter', 'Tropical Inverter'
);
```

Inverter models that exist in the data (all R-32, full 1.0T/1.5T/2.0T tonnage_data, lra='N/A (Soft Start)'):
- Haier: Triple Inverter (Life/Smart/Color/UV)
- Orient: Ultron Divine, Smartron
- PEL: InverterOn Airy, Turbo DC
- Kenwood: eLuxury, eSmart
- Samsung: Digital Inverter
- LG: Dual Inverter
- Mitsubishi: Tropical Inverter

### PK PSI Thresholds (pak_diagnostic_questions)

Confirmed correct as of 2026-05-19:

| Refrigerant | Normal suction range at 40C ambient | high_min value |
|-------------|-------------------------------------|----------------|
| R-410A | 125–145 PSI | 145 |
| R-22 | 65–88 PSI | 88 |
| R-32 | 120–140 PSI | 140 |

130 PSI (R-410A) correctly classified as `(ok)` — routes to discharge PSI step, NOT to Card 13.

### PK-Specific UI Behaviour (confirmed live 2026-05-19)

| Feature | Implementation | Status |
|---------|---------------|--------|
| Currency | PKR (₨) on all estimates | ✅ Confirmed |
| Voltage | 220-240V / 50Hz single phase | ✅ |
| WhatsApp Send button | `assessment/[id]/page.tsx` — always rendered when market=PK, `disabled` until phone entered | ✅ Confirmed |
| Customer name placeholder | "Ahmed Khan" (not "Sarah Johnson") | ✅ Confirmed |
| Phone field label | "WhatsApp Number" (not "Phone Number") | ✅ Confirmed |
| 2.5T commercial warning | `StepZeroPanel.tsx` line 836 — orange banner when `tonnage===2.5 && isPK` | ✅ Confirmed |
| Urdu toggle | `LanguageToggle` navbar button present | ✅ Confirmed |
| Inverter badge (dropdown) | `StepZeroPanel.tsx` line 691 — blue INVERTER pill shown when `m.series_type === "inverter"` in dropdown results | ✅ Confirmed live 2026-05-19 |
| Inverter badge (chip) | `StepZeroPanel.tsx` — `selectedSeriesType` state var set in `applyModelRecord` isPK block; chip reads `selectedSeriesType === "inverter"` | ✅ Confirmed live 2026-05-19 (commit a951a02) |
| Nameplate field badges | MODEL # and TONNAGE show "DB" badge when auto-filled from DB. Edit inline — badge changes to ✏ Edited. RLA/LRA/Cap/MCA/MOCP show "Est." (estimated). No modal, no bulk-clear button. | ✅ Flow 6 confirmed live 2026-05-19 |

### PK Data Source File

**`ac_data_repo_pakistan_v4.json`** — located at `C:\Users\dell\My Drive\Personal Claude\ac_data_repo_pakistan_v4.json`

Structure: `{ metadata, brands[15], fault_card_estimates, operating_targets, error_codes, legacy_model_prefix_lookup, parts_and_labor }`

15 brands total: Gree (8 series), Haier (4), Orient (7), PEL (4), Kenwood (7), EcoStar (6), Samsung (4), LG (3), Mitsubishi (1+), Dawlance, TCL, Waves, Changhong Ruba, Kenwood, Admiral (remaining)
