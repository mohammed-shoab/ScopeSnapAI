# SnapAI AI — Tech Stack & Architecture

> **Last updated:** May 24, 2026 (QA Sign-Off 2026-05-24: BUG-043/044 fixed, WA-42 through WA-47 added. DEC-082/083/084 added. Stage 7 E2E QA COMPLETE. DEC-070 ACTIVE. | Stage 8 Closeout doc written. | Stage 6 Vercel Staging Branch Rewire COMPLETE. All 3 staging domains wired to `staging` branch via domain-level gitBranch. DEC-067 SUPERSEDED by DEC-080. | Previously: Stage 4 Staging Isolation Audit COMPLETE. Clerk key prefix convention confirmed for all 4 domains. Vercel staging custom domains = Preview branch deployments (DEC-074). DEC-074/075/076/077 added. | Stage 2 Free-Tier Cost Audit complete. Stripe confirmed in Railway env vars -- likely test mode, no charges. DEC-071 added. | Full QA pass both markets. WA-28 through WA-37 added. DEC-065/066 added. | Previously: May 21, 2026 (Track F Group C + BUG-032 QA PASS. HEAD: `4743a40`. Alembic head: `032`. Both markets verified. BUG-031 OPEN (staging banner on prod PK). | **2026-05-23 patch:** Change workflow `WORKFLOW.md` + DEC-070 added.
> **Status:** Beta — live on Vercel + Railway. Both markets QA-verified 2026-05-21: Houston + PK. Build hash: `80f50c7f2d1fe88a`. See DEC-037 through DEC-042 for lessons from this session.

---

## Change Workflow (added 2026-05-23 — DEC-070)

**Canonical change workflow lives in `WORKFLOW.md`.** Read it before any change.

The 7-step loop: branch off `staging` → make change in `/tmp` clone → push and PR to `staging` → merge → Vercel/Railway staging auto-deploy → verify on staging.snapai.mainnov.tech + pk-staging.snapai.mainnov.tech → promote to main with `scripts/promote-to-prod.sh <files>` → Vercel/Railway production auto-deploy → verify on snapai.mainnov.tech + pk.snapai.mainnov.tech.

**The four absolute rules:**
1. Never edit code directly on `main` without going through `staging` first
2. Never push migrations to prod that haven't run on staging first
3. Never add env vars to prod without mirroring them on staging
4. Never test on production — testing happens on staging

**Hotfix path (production-only push):** reserved for genuine emergencies (prod outage, auth completely broken, payment generating wrong amounts). Mandatory follow-up: sync staging to match main within 24 hours, write retrospective DEC entry. Full protocol in `WORKFLOW.md` Section 9.

**Activation:** ACTIVE (Stage 7 signed off 2026-05-24). Mandatory for all changes. See WORKFLOW.md.

---


---

## Clerk Key Convention (confirmed Stage 4 audit, 2026-05-23 — DEC-077)

| Prefix | Environment | Vercel project | Railway service | Clerk app |
|--------|-------------|----------------|-----------------|-----------|
| pk_live_ / sk_live_ | Production | scope-snap-ai | scopesnap-api-production | Production app |
| pk_test_ / sk_test_ | Staging | scopesnap-web-staging | scopesnap-api-staging | firm-chamois-61 (Development) |

**The prefix in the HTML `data-clerk-publishable-key` attribute is the authoritative environment signal.**

**Vercel staging custom domain redeploy pattern (DEC-074):** After any env var change on `scopesnap-web-staging`, always trigger a staging branch Preview redeploy (not a Production environment build) to update `staging.snapai.mainnov.tech` and `pk-staging.snapai.mainnov.tech`.

---

## Front-End Content QA — Separate Gate from Backend Routing QA (added 2026-05-24)

**WA-41 — backend "PASS" does not validate displayed content.** A Stage 7-style end-to-end QA proves that the diagnostic tree routes correctly given inputs. It does NOT prove that the displayed hints, question text, tier labels, or marketing copy on the way through that flow are accurate. The two need separate QA passes:

1. **Backend routing QA** — given inputs, does the engine return the right card? (Stage 7 ran this; PASS.)
2. **Front-end content QA** — does every displayed string match the brain-file ground truth? PSI thresholds, refrigerant names, tier labels, brand voice.

**Issues surfaced by 2026-05-24 walkthrough — ALL RESOLVED:**
- DONE: Step 2 R-410A PSI hint corrected: Alembic 035 sets hint to "R-410A normal: 115-140 PSI at 95 deg F outdoor ambient." (DEC-081)
- DONE: Not Heating emoji fixed: fire to snowflake (Issue #5)
- DONE: /homeowner Best tier description corrected: "most thorough - addresses root cause" (Issue #3)
- DONE: Tier naming unified: Good/Better/Best across all surfaces (Issue #3, DEC-049 resolved)
- DONE: Homepage brand voice rewritten: honest builder positioning, Gemini/banned words removed (Issue #4)
- DONE: Dashboard indefinite loading fixed: 5s timeout + empty-state coaching (Issue #6)
- DONE: Address gate removed: complaint selection works without address (Issue #2, WA-32 resolved)

**Boundary-value testing gate (PSI - post-035 required):**
  - Suction: 80 PSI low alert | 125 PSI normal | 160 PSI high alert
  - Discharge: 210 PSI low/escalate | 250 PSI normal (Card 14) | 310 PSI high (Card 17)

**Before declaring a release ready, run both gates:** the snapai-qa skill covers backend routing; a manual click-through walkthrough is needed for front-end accuracy. This separation is permanent.


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
| `git fast-import` from workspace | ✅ Works | **Best method when /tmp clone unavailable.** `git hash-object -w <file>` → get blob SHA → pipe commit spec to `git fast-import --quiet`. Bypasses index entirely. No index.lock risk. Works even when `.git/index` is corrupt. See DEC-028 for full pattern. |
| git plumbing (hash-object → mktree → commit-tree → push) from workspace | ⚠️ Fallback | Works but tedious. `git fast-import` is simpler for file-level changes. |
| `git add / commit / push` from NTFS workspace | ❌ Fails | index.lock owned by Windows NTFS |
| `rm -f .git/index.lock` from NTFS workspace | ❌ Fails | NTFS cross-OS permission |
| GitHub REST API via curl | ❌ Blocked | Proxy 403 |
| Outbound HTTP to external APIs (Clerk, Railway) from sandbox | ❌ Blocked | Sandbox proxy returns 403 for all external API calls. Cannot use httpx, requests, urllib, curl to reach api.clerk.com, railway.app, etc. Must be done locally by user. |
| Browser fetch() to Clerk Backend API | ❌ Blocked | CORS: api.clerk.com rejects cross-origin `Authorization: Bearer` from any non-Clerk domain. Cannot call Clerk API from browser JS. |

### File Editing

| Method | Status | Notes |
|---|---|---|
| Python append script (`open(f,'a').write(content)`) | ✅ Works | **Preferred for any file with Unicode.** Bypasses Edit tool entirely. Write content in Python, no NTFS truncation. |
| `git fast-import` plumbing | ✅ Works | **Preferred for pushing.** `git hash-object -w file` → `git fast-import`. No index, no lock, no truncation. |
| Python subprocess to generate file content | ✅ Works | Also good for complex multi-file writes |
| `Edit` tool on pure-ASCII files only | ✅ Works | Only safe if zero non-ASCII bytes AND short lines. Verify line count after. |
| `Edit` tool on ANY file with non-ASCII chars | ❌ BANNED | DEC-027 (2026-05-20): NTFS truncation affects ALL file types — .py, .ts, .tsx, .md — whenever the file contains Unicode (emoji, box-drawing `──`, em-dashes `—`, Urdu text, etc.). The Edit tool silently truncates lines at ~80 chars, cutting off code mid-statement with no error. Causes SyntaxError (Python) or JSX parse failure (TSX) on deploy. **NEVER use Edit on Unicode files.** |
| `Edit` tool on pure-ASCII files with short lines | ✅ OK | Only safe if: file has zero non-ASCII bytes, AND no line exceeds ~200 chars. Verify after: `python3 -c "ast.parse(open(f).read())"` (py) or `wc -l` vs expected count. |
| `Edit` tool on TSX/JSX files with emoji in strings | ❌ BANNED | Same as above — emoji strings, SVG paths, long JSX lines all trigger NTFS truncation. |
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
| `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` | GCP project `snapai-maps` (root-matrix-497207-j4) | US address autocomplete via Google Places JS API | Set in Vercel prod + staging env vars at build time. Key restrictions: HTTP referrer restrictions restored 2026-05-23 — localhost:3000/*, snapai.mainnov.tech/*, staging.snapai.mainnov.tech/*. Never echo in assistant responses. See DEC-078, DEC-079. |
| `CLERK_SECRET_KEY` | Clerk secret key (dev mode) |
| `NEXT_PUBLIC_ENV` | Set to `production` in prod — enables Clerk middleware. Set to `staging` on Vercel staging env to show StagingBanner. Set to `development` to use X-Dev-Clerk-User-Id bypass. |
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

**Track D — Diagnosis History + Public Share (added 2026-05-20, commit 6314219):**

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/diagnostic/result/{session_id}` | ✅ Clerk JWT | Fetch full resolved diagnosis — fault, action_steps, parts_needed, alternatives, photo_evidence, share_url. Returns 404 if not found, 409 if not resolved. |
| `GET` | `/api/diagnostic/list?limit=20&cursor=` | ✅ Clerk JWT | Paginated company diagnosis history. Base64 opaque cursor on `created_at DESC`. Returns `{items, next_cursor}`. |
| `POST` | `/api/diagnostic/feedback` | ✅ Clerk JWT | Tech agreement feedback — `{session_id, agreement: "agree"/"disagree", real_fault_text?}`. Saves to `diagnosis_feedback` table (DEC-025). |
| `POST` | `/api/diagnostic/finalize/{session_id}` | ✅ Clerk JWT | Idempotent. Sets `share_token` + `confidence_level` on first call. Called fire-and-forget from frontend on resolve (DEC-026). Body: `{customer_label?}`. |
| `GET` | `/api/diagnostic/public/{share_token}` | ❌ No auth | Public share. Reads `X-Market` header (sent by frontend `detectMarket()`). Returns same shape as `/result` but `customer.label` and `customer.address` always null. |

> ⚠️ **Market routing on public endpoint:** `/api/diagnostic/public/{share_token}` uses `get_tables()` dependency to read `X-Market` header. The frontend `/d/[share_token]/page.tsx` sends this header explicitly via `headers: { "X-Market": detectMarket() }` in the raw `fetch()` call (DEC-030). Do NOT use `companies.market` — that column does not exist (DEC-029).

> ⚠️ **Router ordering note (fixed 2026-05-01, commit c05658a):** `GET /api/estimates/recommend` MUST be registered BEFORE `GET /api/estimates/{estimate_id}` in main.py, otherwise the catch-all `/{estimate_id}` intercepts `/recommend` and causes a UUID parse DataError. This is now fixed — recommend_router is included before estimates.router.

### Database Tables

> All tables have RLS enabled. The `service_role` key (used by the backend) bypasses RLS automatically. Tables with sensitive data also have `company_isolation` policies restricting data per contractor.
> **Current Alembic revision: 029** (Migrations 012–021: fault card descriptions, report token, estimate refresh. Migrations 022–025: pak_pricing_tiers + seed, pak_fault_card_descriptions, pak_fault_card_urdu_descriptions. Migration 026: fault_cards action_steps/parts_needed columns. Migration 027: diagnostic_sessions share_token/customer_label/confidence_level + diagnosis_feedback table. Migration 028: lifecycle_rules 17→44 rows. Migration 029: companies.peak_season_surcharge_percent + estimates.seasonal_modifier_pct — applied via Supabase direct (WA-7 pattern).)

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
| `lifecycle_rules` | 44 | Component age + condition_signal -> recommended A/B/C tier. Component age + condition_signal → recommended A/B/C tier. "default" signal always returns B. Age-based rules only apply with specific condition signals (pitting, bearing_noise, rla_over_nameplate). | Python SQL gen → Supabase SQL editor |
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

**Migrations 022-029 — Pakistan + Diagnosis + Seasonal (added 2026-05-19/20):**

| Table | Migration | Purpose |
|-------|-----------|---------|
| `pak_pricing_tiers` | 022 + 023 (seed) | PK fault card pricing — 45 rows (15 cards x 3 tiers), PKR amounts |
| `pak_fault_card_descriptions` | 024 | English descriptions for all 15 PK fault cards |
| `pak_fault_card_urdu_descriptions` | 025 | Urdu descriptions for all 15 PK fault cards |
| `diagnosis_feedback` | 027 | Tech feedback on resolved diagnoses — agreement, real_fault_text, created_at |
| `pak_lifecycle_rules` | — | PK recommendation config — JSONB key-value schema (NOT condition-signal-based): `id, rule_key, rule_value JSONB, created_at`. Intentionally different from US `lifecycle_rules`. |

**New columns added by migrations 026-029:**

| Table | Column | Migration | Notes |
|-------|--------|-----------|-------|
| `fault_cards` + `pak_fault_cards` | `action_steps`, `parts_needed`, `alternative_cards`, `climate_notes` | 026 | Diagnosis detail fields. All 19 US + 15 PK cards backfilled. |
| `diagnostic_sessions` | `share_token`, `customer_label`, `confidence_level`, `reasoning_chain`, `deleted_at` | 027 | Share link generation (finalize endpoint). `share_token` backfilled 2026-05-20 (62 rows via gen_random_bytes). |
| `companies` | `peak_season_surcharge_percent` | 029 | INT nullable. NULL = market default (25%), 0 = disabled, 1-100 = custom override. |
| `estimates` | `seasonal_modifier_pct` | 029 | INT NOT NULL default 0. Generation-time freeze of seasonal % applied. |

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
  "/assessments(.*)", "/diagnoses(.*)", "/settings(.*)", "/billing(.*)",
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
│   │   │   ├── assess/         # Phase 3 diagnostic flow entry point
│   │   │   ├── assessment/[id]/ # Estimate builder (REAL — always route here)
│   │   │   ├── estimate/[id]/  # DEAD CODE — app never routes here (DEC-032)
│   │   │   ├── diagnoses/      # Diagnosis history list (Track D)
│   │   │   ├── diagnoses/[session_id]/ # Fault resolution detail (Track D)
│   │   │   ├── estimates/      # Assessment list
│   │   │   ├── onboarding/     # Company setup wizard
│   │   │   ├── analytics/      # Accuracy tracker (feature-flagged)
│   │   │   ├── settings/       # Company profile, pricing, privacy
│   │   │   └── billing/        # Subscription (feature-flagged)
│   │   ├── d/[share_token]/    # PUBLIC diagnosis share link (Track D)
│   │   ├── r/[slug]/[reportId] # PUBLIC homeowner estimate report
│   │   └── page.tsx            # PUBLIC landing page
│   ├── components/
│   │   ├── SidebarNav.tsx          # Sidebar with 14 SVG icons
│   │   ├── DataConfidenceLabel.tsx # AI confidence display
│   │   ├── FaultResolutionScreen.tsx   # Fault detail + share + Mark as Solved (Track D)
│   │   ├── DiagnosisFeedbackModal.tsx  # Different-fault feedback modal (Track D)
│   │   ├── StagingBanner.tsx       # Amber fixed bar — visible only on NEXT_PUBLIC_ENV=staging (S.7)
│   │   └── diagnostic/
│   │       └── DiagnosticFlow.tsx  # Question-tree step renderer
│   └── lib/
│       ├── api.ts              # API_URL + apiFetch (requires explicit token — DEC-030)
│       ├── featureFlags.ts     # NEXT_PUBLIC_SHOW_* env vars
│       ├── offlineQueue.ts     # IndexedDB offline queue
│       ├── tracking.ts         # Fire-and-forget analytics + 8 D.13 events + 3 REC.5 events
│       └── market.ts           # detectMarket(), formatCurrency(), MARKET_CONFIG
│
├── scopesnap-api/              # FastAPI backend
│   ├── api/
│   │   ├── diagnostic.py       # All diagnostic session logic, PSI routing, fault card return
│   │   ├── fault_estimate.py   # Primary estimate engine — seasonal modifier, recommendation, markup
│   │   ├── dependencies.py     # get_tables() — dual-market routing (_US_TABLES / _PK_TABLES)
│   │   ├── estimates.py        # Estimate CRUD + send + refresh
│   │   ├── reports.py          # Homeowner report endpoints
│   │   ├── auth.py             # Clerk user sync + company profile
│   │   └── events.py           # Analytics + waitlist (rate-limited)
│   ├── services/
│   │   └── condition_signals.py  # 8-signal priority chain for recommendation engine (Track REC)
│   └── db/
│       └── migrations/         # Alembic migration files (current head: 029)
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

### Fallback — git fast-import (preferred when /tmp clone unavailable)

If the /tmp directory is not writable or the clone fails for network reasons, use `git fast-import`:

```bash
# Step 1: Hash file(s) into object store (bypasses index)
BLOB=$(git hash-object -w path/to/changed/file.py)

# Step 2: Commit via fast-import (no index touched)
MSG="your commit message"
git fast-import --quiet << EOF
commit refs/heads/main
author Claude Bot <claude@anthropic.com> $(date +%s) +0000
committer Claude Bot <claude@anthropic.com> $(date +%s) +0000
data $(echo -n "$MSG" | wc -c)
$MSG
from $(git rev-parse origin/main)
M 100644 $BLOB path/to/changed/file.py
EOF

# Step 3: Push
git push origin main
```

See DEC-028 for full pattern. `git fast-import` is immune to index corruption and NTFS lock conflicts.

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
| **Stripe** | Test mode (likely) | ⚠️ GAP | STRIPE_SECRET_KEY + STRIPE_WEBHOOK_SECRET in Railway prod env. Dashboard blocked by safety tooling. No paying customers. Manual verify: dashboard.stripe.com to confirm sk_test_ prefix. |

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

### WA-8 — git index corruption when running sequential git ops on NTFS-mounted repo (2026-05-20)

**Problem:** Running multiple sequential git commands (read-tree, update-index, stash, add) from the Linux sandbox against the NTFS-mounted workspace causes `error: bad signature 0x00000000 / fatal: index file corrupt`. Even `rm -f .git/index && git read-tree HEAD` only provides transient relief — the next operation re-corrupts it. Root cause: concurrent `.git/index.lock` creation races between sandbox git and Windows processes (VS Code, shell).

**Fix:** Use `git fast-import` to bypass the index entirely. See DEC-028 and the updated Fallback section above.

**Never do:** `git stash` → `git pull --rebase` → `git stash pop` from the sandbox. This sequence will corrupt the index 100% of the time on this repo.

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

### WA-9 -- apiFetch silent 401: every authenticated call MUST pass token explicitly (2026-05-20)

**Problem discovered (D.11 / QA audit 2026-05-20):** All 62 `diagnostic_sessions` rows had `share_token = NULL`
despite the finalize endpoint being called. Root cause chain:
1. `apiFetch` in `lib/api.ts` does NOT auto-inject the Clerk JWT. The `token?` argument is optional.
2. In production (non-dev), omitting `token:` means no `Authorization: Bearer <jwt>` header -> backend returns 401.
3. The finalize call in `assess/page.tsx` had `.catch(() => {})` (fire-and-forget) — the 401 was silently swallowed.
4. Dev mode uses `X-Dev-Clerk-User-Id` header bypass, so the bug never surfaced locally.

**Effect:** Silent data gap. Share links broken for all 62 sessions. Required SQL backfill:
```sql
UPDATE diagnostic_sessions
SET share_token = encode(gen_random_bytes(32), 'hex')
WHERE share_token IS NULL;
```

**Fix pattern for fire-and-forget calls (finalize-style):**
```typescript
getToken().then(token => {
  apiFetch(`/api/endpoint`, {
    method: "POST",
    token: token ?? undefined,
    body: JSON.stringify({...}),
  }).catch(() => {});
}).catch(() => {});
```

**Fix pattern for data-loading calls (useEffect):**
```typescript
const { getToken } = useAuth();
useEffect(() => {
  (async () => {
    const token = await getToken();
    const data = await apiFetch<MyType>("/api/endpoint", { token: token ?? undefined });
  })();
}, [getToken]);
```

**Detection:** If any page shows a generic "Could not load X" message or data silently missing (no error shown):
1. Open DevTools Network tab — check for 401 responses on `/api/` calls.
2. Check if the `apiFetch` call passes a `token:` argument.
3. In dev mode, the bug is invisible — always verify auth behavior in production/staging.

**Commit:** `53db54a` (D.11 fix — assess/page.tsx finalize call)
**Related commits:** `575f73e`, `928a476` (Track D frontend files)
**DEC reference:** DEC-030

**Prevention checklist — before shipping ANY new component:**
- [ ] Does this component call `apiFetch`? If yes, does it import `useAuth` and pass `token`?
- [ ] Are any apiFetch calls fire-and-forget with `.catch(() => {})`? If yes, wrap in `getToken().then()`.
- [ ] Does the dev mode bypass mask this? Test in staging with real Clerk tokens.

---

### WA-10 -- Edit tool + NTFS truncation: use Python replace() for all Unicode files (2026-05-20)

**Problem (D.11 fix, 2026-05-20):** The `Edit` tool was used to modify `assess/page.tsx` to fix D.11.
The file was written correctly from the Edit tool's perspective, but `git diff` showed the last 8 lines
missing — the file was truncated. The truncation point was exactly where a Unicode em-dash appeared
in a code comment.

**Detection method that caught it:**
```bash
git diff --ignore-cr-at-eol HEAD -- scopesnap-web/app/(app)/assess/page.tsx | tail -20
# Showed: "\ No newline at end of file" and ~8 lines of "- " deletions with no corresponding "+"
```

**Recovery (DEC-004 + WA-7 pattern):**
```bash
# 1. Restore the original file from the last known-good remote commit
git show origin/main:scopesnap-web/app/(app)/assess/page.tsx > /tmp/assess_clean.tsx
cp /tmp/assess_clean.tsx /tmp/snapai_tmp2/scopesnap-web/app/(app)/assess/page.tsx

# 2. Apply changes via Python string replacement (NOT Edit tool)
python3 -c "
content = open('/tmp/snapai_tmp2/.../file.tsx', 'rb').read().rstrip(b'').decode('utf-8')
content = content.replace(old_str, new_str, 1)
open('/tmp/snapai_tmp2/.../file.tsx', 'w', encoding='utf-8').write(content)
"
```

**Rule (extends DEC-027):**
> NEVER use the `Edit` tool on ANY file containing non-ASCII characters.
> This includes ALL .tsx/.ts/.py/.md files in this project (they all have Unicode in comments, strings, or content).
> ALWAYS use Python open/replace/write instead.

**How to identify if a file is at risk:**
```bash
python3 -c "
data = open('file.tsx', 'rb').read()
non_ascii = [hex(b) for b in data if b > 127]
print(f'{len(non_ascii)} non-ASCII bytes found')
"
# Any non-zero count = Edit tool unsafe
```

**Commit:** `53db54a` — fix applied via Python replace in /tmp/snapai_tmp2 clone
**DEC reference:** DEC-027

---

### WA-11 -- Task completion status never means code exists: always grep before trusting (2026-05-20)

**Problem (Track D QA, 2026-05-20):** Tasks D.1-D.9 were marked [completed] in ACTIVE_TASKS.md.
QA grep revealed only 1 of 5 expected backend routes existed in `diagnostic.py`.
Four routes (`/list`, `/feedback`, `/finalize`, `/public`) had never been written — only planned.
The AI session that "completed" them ran out of context and marked tasks done without verifying the files.

**Detection:**
```bash
# Count @router decorators in target file (should match expected route count)
grep -c "@router\." scopesnap-api/api/diagnostic.py

# Check each expected route exists by signature
grep "@router\." scopesnap-api/api/diagnostic.py | grep -E "list|feedback|finalize|public|result"

# Syntax check (catches NameError, SyntaxError introduced in edits)
python3 -c "import ast; ast.parse(open('scopesnap-api/api/diagnostic.py').read()); print('OK')"
```

**Rule:** Before closing any backend track, run the grep check above. Task list status is evidence of intent,
not evidence of implementation. Always verify the artifact (file on disk) matches the intention.
**DEC reference:** DEC-031

---

### WA-12 -- NameError inside try/except Exception silently disables features (2026-05-20)

**Problem (Track REC / R.9):** `fault_estimate.py` called `derive_condition_signal_from_assessment()`
inside a `try: ... except Exception: logger.warning("lifecycle_rules lookup failed")` block.
The function was never imported. Python raised `NameError` at runtime, which is a subclass of `Exception`,
so the except block caught it silently on EVERY estimate generation.
Result: the entire lifecycle_rules recommendation overlay was completely disabled in production
from the moment `condition_signals.py` was created until commit `e2683dd` (R.9) fixed the import.

**Detection:**
```bash
# Check import exists
grep -n "from services.condition_signals" scopesnap-api/api/fault_estimate.py
# Check function call exists  
grep -n "derive_condition_signal" scopesnap-api/api/fault_estimate.py
# Both lines must be present

# Verify module imports cleanly at startup
python3 -c "import sys; sys.path.insert(0,'scopesnap-api'); import api.fault_estimate; print('OK')"
```

**Rule:** Before shipping any function call inside a `try/except Exception` block:
1. Grep for the import in the same file — both the `from X import Y` line AND the call site must be present.
2. If the function comes from a new file (like condition_signals.py), verify the import resolves at module load time.
3. Watch for log messages like "X lookup failed" that could mask NameError — add `logger.exception()` instead of `logger.warning()` in catch blocks that wrap external calls.
**DEC reference:** DEC-034

---

### WA-13 -- Vercel dashboard is client-rendered: use javascript_tool, not get_page_text (2026-05-20)

**Problem:** When checking Vercel deployment status via `mcp__Claude_in_Chrome__get_page_text`,
the returned content was only nav shell HTML with no deployment rows — the page uses React client-side
rendering and the text tool captures pre-hydration HTML only.

**Fix:**
```javascript
// Use javascript_tool to query the rendered DOM instead
document.querySelectorAll('[data-testid="deployment-item"]').length
// Or inspect specific deployment state:
document.querySelector('[data-testid="deployment-status"]')?.textContent
```

**General rule:** If `get_page_text` returns nav/header but no body content, the page is client-rendered.
Switch to `javascript_tool` and query `document.querySelector` / `document.querySelectorAll` for the
specific data you need. This applies to Vercel, Railway, GitHub Actions, and most SaaS dashboards.

---

### WA-14 -- git safe.directory required on every fresh /tmp clone (2026-05-20)

**Problem:** On a fresh Linux sandbox session, git commands against `/tmp/snapai_tmp2`
(or any /tmp clone) fail with:
```
fatal: detected dubious ownership in repository at '/tmp/snapai_tmp2'
To add an exception for this directory, call:
  git config --global --add safe.directory /tmp/snapai_tmp2
```

**Fix (add to top of every git workflow):**
```bash
git clone "https://TOKEN@github.com/mohammed-shoab/ScopeSnapAI.git" /tmp/snapai_tmpN
git config --global --add safe.directory /tmp/snapai_tmpN
```

Or if the clone already exists from a prior step:
```bash
git config --global --add safe.directory /tmp/snapai_tmp2
```

**Note:** This is required even when the clone was created in the same bash session but
the sandbox was restarted between steps. Always add it before the first git read/write op.




### WA-15 — SQLAlchemy ORM column must be defined for every DB column set in Python (2026-05-20)

**Problem:** When a new column is added via Alembic migration, you must ALSO add the
corresponding `Mapped[type] = mapped_column(...)` line to the ORM class in `db/models.py`.
If you skip this step, SQLAlchemy 2.0 DeclarativeBase silently accepts the constructor kwarg
as a Python attribute, never persisting it to the database. No error, no warning.

**Detection:** Query the column after creating a test record:
```python
db.execute(text("SELECT new_col FROM table WHERE id = :id"), {"id": obj.id}).scalar()
# Returns server_default value instead of what Python passed? → ORM column missing.
```

**Fix template:**
```python
# In db/models.py, inside the relevant ORM class:
new_col: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
```

**Real instance:** BUG-025 — `seasonal_modifier_pct` was passed to `Estimate(...)` constructor
in `fault_estimate.py` but missing from the Estimate ORM class. Seasonal modifier was silently
dropped on every estimate creation. Fixed in commit 85c5755. See DEC-036.

---

### WA-16 — handleContinue (or any "go to estimate" button) must create estimate first (2026-05-20)

**Problem:** After the DX track refactor, navigating from a diagnosis result to the estimate
builder requires FIRST creating the estimate via `POST /api/estimates/fault-card`. Navigating
directly using `assessment_id` causes a 404 because `/assessment/[id]` expects an estimate UUID.

**Rule:** Any component that says "Continue to Estimate" must:
```typescript
const est = await apiFetch<{ id: string }>("/api/estimates/fault-card", {
  method: "POST", token, body: JSON.stringify({ card_id, assessment_id })
});
router.push(`/assessment/${est.id}`);  // ← est.id, never data.assessment_id
```

**Real instance:** BUG-026 — `FaultResolutionScreen.handleContinue` navigated to
`/assessment/${data.assessment_id}` (assessment UUID, not estimate UUID → 404).
Fixed in commit 85c5755. See DEC-037.

---


### WA-20 — pak_pricing_tiers NUMERIC columns return decimal.Decimal — always cast before arithmetic (2026-05-21)

**Problem (BUG-030):** `POST /api/estimates/fault-card` returned 503 on PK market. After adding a debug
try/except wrapper (DEC-016 technique), the real error was:
`TypeError: unsupported operand type(s) for *: 'decimal.Decimal' and 'float'`
in `_apply_surcharges` at `sea = round(base * seasonal_pct)` where `base` came from
`pak_pricing_tiers.estimate_amount` and `seasonal_pct` was a Python float.

**Root cause:** PostgreSQL `NUMERIC` columns return Python `decimal.Decimal` objects via SQLAlchemy,
NOT `int` or `float`. The Houston `pricing_tiers.estimate_amount` column is INTEGER so the bug
never appeared on US market. PK tables use NUMERIC type.

**Fix (fault_estimate.py line 267):**
```python
pricing = {row.tier: int(row.estimate_amount) for row in pt_rows.fetchall()}  # BUG-030: NUMERIC -> int
```

**Rule:** Any read of a NUMERIC/DECIMAL Supabase column via SQLAlchemy MUST be cast to `int()` or `float()`
before arithmetic. Add a comment citing BUG-030 so future readers understand why the cast is there.

**Detection:** `TypeError: unsupported operand type(s) for *: 'decimal.Decimal' and <type>` ->
grep for the column being multiplied, check PostgreSQL column type in Supabase schema, cast before use.

**Also see:** DEC-014 in DECISIONS.md for the decision record.

---

### WA-21 — Wrapping handler in try/except reveals 503-masked TypeErrors with CORS headers (2026-05-21)

**Context (BUG-030 diagnosis):** `POST /api/estimates/fault-card` returned HTTP 503 with no CORS headers.
Browser showed "Failed to fetch" (opaque error). The real error — a `TypeError` — was hidden because
the exception escaped FastAPI's ASGI middleware stack to Railway's proxy layer.

**Debug technique:** Wrap the ENTIRE handler body in `try/except Exception`:
```python
@router.post("/fault-card")
async def create_fault_estimate(...):
    try:
        # ... entire handler body as-is ...
    except Exception:
        import traceback
        raise HTTPException(status_code=500, detail=f"DEBUG: {traceback.format_exc()}")
```
HTTP 500 responses from `HTTPException` GO THROUGH FastAPI's middleware and DO include CORS headers.
The browser can now see the traceback in the response body.

**When to use:** Any endpoint returning 503 with no CORS headers and no response body.

**Remove the wrapper** after identifying the root cause — never ship debug wrappers.

**Symptom distinction:**
- `500` + JSON body + CORS headers -> caught by FastAPI; real error visible in body
- `503` + no CORS headers + no body -> escaped Railway proxy; exception bypassed FastAPI entirely

**Also see:** DEC-016 in DECISIONS.md for the decision record.

---

### WA-22 — Never add if tables.market == "PK" column branches in fault_estimate.py (2026-05-21)

**Problem (BUG-030 wrong fixes):** Two successive fix attempts added PK-specific column branches
inside `fault_estimate.py` querying column names like `pkr_est_min`, `pkr_min/max/typical`,
`pkr_attic_premium`. Both caused new errors because those column names DON'T EXIST on the views.

**The correct model:** `dependencies.py` `_PK_TABLES` uses DATABASE VIEWS that already translate
PK column names to US-compatible names:
- `pak_fault_cards_v` -> exposes `price_list_min/typical/max`, `better_option_estimate`
- `pak_labor_rates_v` -> exposes `attic_premium_min/max`, `r22_surcharge_min/max`
- `pak_replacement_costs_v` -> exposes `price_min/max/typical`

The original `fault_estimate.py` code works on BOTH markets without any market check because
the views handle all schema translation. The code reads `tables.fault_cards` which resolves to
`pak_fault_cards_v` for PK and `fault_cards` for US — same column names either way.

**Rule:** If PK data needs to appear differently:
1. Check what the VIEW currently exposes (query it in Supabase)
2. If the view is missing a column, add the column to the VIEW SQL
3. NEVER add `if tables.market == "PK"` column-name conditionals in `fault_estimate.py`

**Commits showing the wrong approach (reverted):** `43a1215` (hardcoded PK values), `57a5ae0` (pkr_* columns)
**Correct fix commit:** `cd2d58f` (int() cast only — no PK branches)

**Also see:** DEC-013 in DECISIONS.md for the decision record.

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

> **NUMERIC type hazard:** `pak_pricing_tiers.estimate_amount` is NUMERIC (not INTEGER). SQLAlchemy returns it as Python `decimal.Decimal`. Always cast `int(row.estimate_amount)` before arithmetic. See WA-20 and DEC-014.

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

**QA NOTE (2026-05-20):** Gree has ZERO inverter series in pak_brands — all 8 Gree series
(Console, Crown, Fairy, GS, GWC, GWH, Lomo, Pular) have `type: "non_inverter"`. QA spec item
"Gree Fairy Inverter — inverter badge must appear" cannot be tested against Gree.
Use Haier "Triple Inverter" or Orient "Ultron Divine" to verify inverter badge UI logic instead.
The badge code in StepZeroPanel.tsx is correct (checks `m.series_type === "inverter"`); this is
purely a seed data gap. DATA-GAP-001 SQL above will fix it.

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


---

## WA-17 — Migration chain gap after Railway platform outage (2026-05-21)

**Symptom:** `alembic_version` in DB shows `032` but a column added by migration `031`
does not exist. `GET /health` returns 200 but endpoints that read that column fail.

**Cause:** Railway was down during a GCP outage. Builds queued but never deployed.
A migration was applied via Supabase MCP `apply_migration` directly (skipping the chain).

**Detection:**
```sql
SELECT version_num FROM alembic_version;
-- Then verify the column actually exists:
SELECT column_name FROM information_schema.columns
WHERE table_name = 'diagnostic_sessions' AND column_name = 'photo_skipped';
```
If `alembic_version` shows N but a column from migration N-1 is missing, the chain has a gap.

**Fix:**
1. Read the missing migration's `upgrade()` function to get the DDL
2. Apply it via Supabase MCP `apply_migration` with `IF NOT EXISTS`:
   ```sql
   ALTER TABLE your_table ADD COLUMN IF NOT EXISTS col_name TYPE NOT NULL DEFAULT val;
   ```
3. Do NOT manually update `alembic_version` — it's already correct
4. Verify column exists after applying

**See:** DEC-037 for full explanation.

---

## WA-18 — Railway platform outage recovery protocol (2026-05-21)

**Symptom:** `GET /health` returns 502 for extended period. Railway dashboard may show
"Online" (misleading — see DEC-039). Railway status page shows "Builds are slow to progress"
or "Hobby plans paused".

**What happened (2026-05-21):** GCP outage caused Railway build queue backup. Broken commits
in the queue crashed the service. Fix commits queued but slow to deploy.

**Protocol:**
1. Check Railway status: `https://status.railway.com` — confirm platform incident vs app crash
2. Check current commit: Navigate to Railway dashboard → service → deployments tab
3. If active deployment has a Python SyntaxError: it will crash on startup — Railway shows
   "Online" but health returns 502. Fix is waiting for the queue to process the fix commit.
4. While waiting: apply any missing DB migrations via Supabase MCP directly (WA-17)
5. Do frontend-only QA in parallel (Vercel deploys are independent of Railway)
6. Only proceed with backend QA once `GET /health` returns `{"status":"ok"}`

**Vercel is independent:** Vercel deploys succeed even when Railway is down. Frontend-only
checks (button layouts, input attributes, source code verification) can proceed immediately.

**Clerk auth is independent:** Clerk authentication works even when Railway is down.
The user can log in to the Claude browser window and navigate authenticated pages on Vercel.

**See:** DEC-039, DEC-040 for related rules.

---

## WA-19 — Verify file i
---

### WA-23 -- Estimate option tiers in the DB are "A"/"B"/"C" -- not "good"/"better"/"best" (2026-05-21)

**Discovery (BUG-032):** `fault_estimate.py` creates `EstimateTier` objects with `tier="A"`,
`tier="B"`, `tier="C"`. These are stored in the `estimates` DB table as-is.

The `pak_pricing_tiers` table uses `tier="good"`, `tier="better"`, `tier="best"` — a COMPLETELY
DIFFERENT naming scheme.

`ReportClient.tsx` reads the recommended option from `estimates`, gets tier "B", and sends
`{ selected_option: "B" }` to the approve endpoint. The original approve endpoint only accepted
"good"/"better"/"best" and rejected "B" silently (422 validation error on every homeowner approval).

**Fix applied (commit 4743a40):**
```python
# reports.py line 365
if body.selected_option not in ("good", "better", "best", "A", "B", "C"):
    raise HTTPException(status_code=422, detail="selected_option must be...")
```

**Rules for all future code touching estimate option tiers:**
1. `estimates.options[].tier` in DB = "A" | "B" | "C"
2. `pak_pricing_tiers.tier` = "good" | "better" | "best" (different table, different scheme)
3. Always accept both in any validation (approve endpoint, reporting)
4. `ReportClient.tsx` TIER_LABELS `{ good: "Option A", better: "Option B", best: "Option C" }`
   is display-only and maps the pak_pricing_tiers keys to human labels -- not the actual tier stored in estimates
5. Before writing any approve/tier-selection logic, query: which table is this from?

**DEC reference:** DEC-049

---

### WA-24 -- Desktop Commander Python subprocess: reliable git for Windows-side ops (2026-05-21)

**Problem:** When local repo has unstaged changes AND remote is ahead, standard push fails.
Linux sandbox git on NTFS is banned (DEC-013). PowerShell commands with semicolons via
Desktop Commander gave no visible output.

**Reliable pattern -- write to C:\Windows\Temp\fix_NNN.py:**
```python
import subprocess

repo = r"C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI"

def git(cmd):
    result = subprocess.run(
        ["git"] + cmd.split(),
        cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace"
    )
    print(f"stdout: {result.stdout.strip()}")
    if result.stderr.strip(): print(f"stderr: {result.stderr.strip()}")
    return result

git("stash")
git("fetch origin")
git("rebase origin/main")
git("stash pop")
git("add -A")
# For commit message with spaces, pass as list (not split):
subprocess.run(["git", "commit", "-m", "your message"], cwd=repo)
git("push origin main")
```

**Why this works:** Desktop Commander's `start_process` runs in a Windows process context.
Windows git handles NTFS `.git/index` natively -- no lock issues. The NTFS locking problem
is specific to Linux sandbox git operations (DEC-013 and DEC-004).

**Key distinction:**
- Desktop Commander Python subprocess git = SAFE (uses Windows git binary)
- Linux bash sandbox git on NTFS mount = BANNED (DEC-013)
- Linux bash git on /tmp clone = SAFE (DEC-004)

**Unstaged changes + rebase:** If `git rebase` fails with "unstaged changes",
run `git stash` FIRST (before fetch), then `git stash pop` after rebase.

**DEC reference:** DEC-050

---

## WA-25 — Service/Tune-Up renders through ServiceChecklist.tsx, NOT DiagnosticFlow.tsx (2026-05-21)

**Discovery (BUG-033):** When `complaint_type = "service/tune_up"`, the app renders
`ServiceChecklist.tsx` — a completely separate component from `DiagnosticFlow.tsx`.

**Consequence:** Any UI feature added to `DiagnosticFlow.tsx` (photo skip buttons, override panels,
skip-and-branch logic, etc.) is silently absent for Service/Tune-Up flows. There is no error — the
service flow just doesn't have the feature.

**Rule:** Before adding any UI enhancement to `DiagnosticFlow.tsx`, always ask:
> "Does this also need to apply to Service/Tune-Up? If yes, ServiceChecklist.tsx needs a parallel implementation."

**Component routing by complaint_type:**
| complaint_type | Component |
|---|---|
| not_cooling, water_dripping, not_turning_on | `DiagnosticFlow.tsx` |
| service / tune_up / maintenance | `ServiceChecklist.tsx` |

**Fix pattern:** Duplicate the relevant config (e.g. `PHOTO_SKIP_CONFIG` → `SVC_PHOTO_SKIP_CONFIG`)
and render logic inside `ServiceChecklist.tsx`. No DB changes needed — step_id values from
diagnostic_questions matched config keys directly.

**DEC reference:** DEC-056

---

## WA-26 — PK model data is cached in IndexedDB with 24-hour TTL (2026-05-21)

**Discovery:** After updating `pak_brands` in Supabase (adding Gree Fairy Inverter), the new model
did not appear in the app's brand/model lookup — even after a hard page reload.

**Root cause:** `modelCache.ts` uses **IndexedDB** (not localStorage) as a persistent cache with
a **24-hour TTL**. The DB names are:
- US market: `snapai_models` (IDB store)
- PK market: `snapai_models_pk` (IDB store)

Hard reloads clear in-memory module state (`_memoryCache`) but NOT IndexedDB. The
`ensureLoaded()` function finds valid IDB data and skips the API fetch.

**When this bites you:** After seeding new models into `pak_brands` or `equipment_models`,
the change won't appear in the app until the IDB cache expires (24h) or is manually cleared.

**Force-clear pattern (run in Chrome devtools on the target domain):**
```js
await Promise.all([
  indexedDB.deleteDatabase('snapai_models_pk'),
  indexedDB.deleteDatabase('snapai_models')
]);
location.reload(true);
```

**In-app refresh:** `modelCache.ts` exports `refreshModelCache()` — if you can call it from
the page context it will clear the cache and re-fetch immediately.

**Note:** `/api/models/all` is a **public endpoint** (no Clerk JWT required). The fetch will
succeed without authentication.

**DEC reference:** DEC-057

---

## WA-27 — React-controlled inputs and buttons require __reactProps to trigger state (2026-05-21)

**Discovery:** Throughout this QA session, native DOM events (`element.click()`,
`element.dispatchEvent(new Event('change'))`) consistently failed to update React state for
controlled inputs and buttons in the SnapAI app.

**Root cause:** React uses its own synthetic event system. Controlled components read from
React state, not DOM value. Native events bypass React's reconciler entirely.

**Correct pattern for Claude's Chrome javascript_tool:**

```js
// For <input> / <select> — trigger onChange:
const rk = Object.keys(element).find(k => k.startsWith('__reactProps'));
element[rk].onChange({ target: { value: 'new value' } });

// For <button> — trigger onClick:
const rk = Object.keys(element).find(k => k.startsWith('__reactProps'));
element[rk].onClick({ preventDefault: () => {}, stopPropagation: () => {} });

// WRONG — these do NOT work for React controlled components:
element.click();                                          // ❌
element.dispatchEvent(new Event('change', {bubbles:true})); // ❌
element.value = 'new value';                              // ❌
```

**Finding the React props key:**
```js
const rk = Object.keys(element).find(k => k.startsWith('__reactProps'));
// rk will be something like '__reactProps$abc123xyz'
```

**Also important:** `await` at the top level of `javascript_tool` causes a SyntaxError.
Always wrap async code in an IIFE:
```js
(async () => {
  // your await calls here
})()
```

**DEC reference:** DEC-048 (tab group resets), WA-13 (Vercel client-rendered pages)


---

## WA-28 -- estimates table has NO updated_at column — INSERT must omit it (2026-05-22)

**Discovery (BUG-035):** `_generate_service_estimate()` was including `updated_at` in the INSERT column list for the `estimates` table. The column does not exist in the schema. This caused a silent INSERT failure — no exception raised, no row created.

**Rule:** The `estimates` table schema is: `id, assessment_id, company_id, report_token, report_short_id, options, selected_option, total_amount, deposit_amount, markup_percent, status, viewed_at, approved_at, stripe_payment_intent_id, contractor_pdf_url, homeowner_report_url, sent_via, sent_at, actual_cost, accuracy_score, created_at, seasonal_modifier_pct, market`. There is NO `updated_at`. Any INSERT or UPDATE must never reference it.

**Detection:** If an estimate INSERT appears to succeed (no exception) but no row appears in `SELECT * FROM estimates`, check the column list for `updated_at` or any other non-existent column.

**DEC reference:** DEC-059

---

## WA-29 -- POST /api/estimates/service does NOT exist — use onComplete() (2026-05-22)

**Discovery (BUG-036):** `ServiceChecklist.tsx` was calling `generateServiceEstimate()` which POSTed to `/api/estimates/service`. This endpoint was never implemented on the backend. The POST returned a 404, the error was swallowed, and the flow appeared to hang

**Fix:** Remove `generateServiceEstimate()` entirely from `ServiceChecklist.tsx`. Instead, wire the final step's "Finish" action directly to `onComplete()` -- the prop already passed from the parent. The estimate is generated by the parent's `handleServiceComplete()` handler after the checklist confirms completion. No separate POST needed.

**Rule:** `POST /api/estimates/service` does NOT exist. Never call it. Always delegate estimate creation to the parent component's `onComplete` callback.

**DEC reference:** DEC-060

---

## WA-42 -- `onSkip` prop in StepZeroPanel is declared but never called (2026-05-24)

**Discovery (QA 2026-05-24):** `assess/page.tsx` passes `onSkip={() => setPhase("complaint")}` to `StepZeroPanel`. The prop is received in `StepZeroPanel`'s interface (line 64) and destructured (line 107) but there is **no button or event in StepZeroPanel that calls it**. The skip button does not exist in the UI.

**Consequence:** Calling `onSkip` from outside has no effect because StepZeroPanel never invokes it internally. Setting `phase` via React fiber is the only QA bypass.

**QA workaround -- React fiber state injection:**
Walk `document.body.__reactFiber*` to find memoizedState where `s.memoizedState === 'step-zero'`, then call `s.queue.dispatch('complaint')`. This jumps the assess page directly to complaint selection -- use ONLY for QA automation, never in production.

**DEC reference:** DEC-082

---

## WA-43 -- Diagnostic API requires `answer` classification string, NOT raw `value` (2026-05-24)

**Discovery (QA 2026-05-24):** POST to `/api/diagnostic/session/{id}/answer` requires the body:
`{ "answer": "low" | "ok" | "high", "refrigerant_type": "R-410A" }`

Sending `{ "value": 80 }` (the raw PSI reading) returns HTTP 422 "Field required" for `answer`.

**Classification boundary (US market, R-410A suction):** < 115 PSI = "low", 115-140 PSI = "ok", > 140 PSI = "high".

**Rule:** The frontend (DiagnosticFlow.tsx) already classifies the reading before POST. Never bypass the classification step and send raw PSI directly to the API.

---

## WA-44 -- Production assess page has an extra q1 yesno step before PSI (2026-05-24)

**Discovery (QA 2026-05-24):** On **production** (`snapai.mainnov.tech`), the Not Cooling diagnostic flow starts with "Is the outdoor unit running?" (yes/no radio) BEFORE the suction PSI input. Staging skips directly to PSI.

**Consequence:** Any automated QA script that submits PSI without first answering q1=YES will stall on the yesno screen.

**Production QA pattern:** (1) Click YES on "outdoor unit running?" screen. (2) Wait for PSI input to render. (3) Submit PSI.

**Why staging differs:** The q1 yesno step exists in `diagnostic_questions` for production but is absent or in a different state on staging DB. Do not "fix" this discrepancy without confirming intent.

---

## WA-45 -- No PK DB model has 2.5T tonnage_data -- 2.5T warning requires fiber injection (2026-05-24)

**Discovery (QA 2026-05-24):** All rows in `pak_brands` have `tonnage_data` JSONB keys of `1.0`, `1.5`, and `2.0` only. No model has a `2.5` key. The tonnage buttons never show 2.5T for any PK brand.

**Commercial warning gate (StepZeroPanel.tsx lines 873-882):** `{isPK && manualUnit.tonnage === 2.5 && <amber banner>}`. Code is correct but unreachable via normal UI.

**QA verification:** Inject `manualUnit.tonnage = 2.5` via React fiber after selecting a PK brand. Confirmed 2026-05-24: amber "Commercial / Light Commercial Unit" banner appeared.

**Future:** If 2.5T PK models are ever added to `pak_brands`, the tonnage button will appear and the warning will trigger automatically -- no code change needed.

---

## WA-46 -- Vercel build errors trace to the FIRST failing commit, not the current one (2026-05-24)

**Discovery (BUG-043/044 root-cause hunt):** When Vercel shows ERROR on a deployment, the actual bug was introduced in an EARLIER commit -- subsequent commits built on the broken state and also errored.

**Tracing pattern:**
1. `git log --oneline` -- find where deployments changed from READY to ERROR.
2. `git diff <last-READY-sha>..<first-ERROR-sha> -- <file>` -- isolate the breaking diff.
3. The bug is always in that diff window, NOT in later commits.

**BUG-043 example:** Orphaned `{` in `homeowner/page.tsx` introduced in commit `a50f94a2` caused webpack syntax errors in all subsequent builds through `03c5caa`. Fix: remove the 4 orphaned lines (comment + section + div + unclosed brace).

**DEC reference:** DEC-083

---

## WA-48 — StepZeroPanel must self-source JWT via useAuth(), not rely on clerkToken prop (2026-05-26)

**Discovery (BUG-045):** The `clerkToken` prop in `StepZeroPanel` was always `null` because `assess/page.tsx` is a Server Component — it cannot call `useAuth()`. Every OCR call sent no `Authorization` header, causing 401 on every nameplate scan attempt.

**Rule:** Any client component that calls a protected API must use `const { getToken } = useAuth()` internally. Never pass a Clerk JWT as a prop from a Server Component parent.

**Fix applied:** `const { getToken } = useAuth()` added inside `StepZeroPanel`. Both `runOCR` and `handleConfirm` call `await getToken()` per fetch. See DEC-087.

---

## WA-47 -- TypeScript "Cannot find name" breaks ALL subsequent Vercel builds silently (2026-05-24)

**Discovery (BUG-044):** A TS error introduced in commit N (`Cannot find name 'isRecommended'` in `assessment/[id]/page.tsx`) caused EVERY subsequent Vercel build -- including commits touching unrelated files -- to fail with the same error.

**Why it cascades:** Next.js runs `tsc --noEmit` on every build. A TS error in ANY file fails the entire build. The error message always points to the original broken file, not the current commit's changes.

**Detection:** When ALL recent builds fail, grep the Vercel build log for TypeScript errors. If the error references a file the CURRENT commit did not touch, the bug predates the current commit -- use WA-46 pattern to find the introducer.

**Fix rule:** Always declare ALL variables used in JSX at the top of the render scope in the same file.

**BUG-044 fix:**
```typescript
const isMiddleTier = opt.tier === "better";   // drives card styling only
const isRecommended = !!(opt as { recommended?: boolean }).recommended; // drives star REC badge
const isRec = isMiddleTier;  // alias kept for card headerBg/badgeBg/priceColor
```

**DEC reference:** DEC-084

---

## 2026-06-18 — Audit framework additions

- **Observability synthetic-event filtering (in prod):** Sentry + PostHog `before_send` drop events
  during audit runs. Backend toggle = env `SNAPAI_AUDIT_MODE=1` (Railway). Frontend toggle =
  `?audit_synthetic=1` or `sessionStorage.snapai_audit_mode='1'`. Sentry replay sample rates zeroed
  when the flag is present at init. Behaviour-neutral when no flag set.
- **Audit E2E auth:** Clerk **sign-in tokens** (passwordless) + `@clerk/testing` Testing Tokens.
  Harness: `Personal Claude/SnapAI_Audit_Setup_Artifacts/clerk_e2e_auth_harness.md`. Keys/IDs in
  repo `.env.test` (gitignored). Flag must be set at page init; URL param is stripped on Clerk auth redirects.
- **Clerk audit test users:** staging `firm-chamois-61` = `ds.shoab+audit1..5@gmail.com`;
  prod `scope-snap-ai` = `ds.shoab+audit1, +audit12..15@gmail.com`.
- **CI / security:** `.github/dependabot.yml` (npm `/scopesnap-web`, pip `/scopesnap-api`, github-actions;
  weekly) + `.github/workflows/gitleaks.yml` (secret scan on push/PR) on `main`. Local dev CLIs: Semgrep,
  gitleaks. DAST: Docker + `ghcr.io/zaproxy/zaproxy:stable`.
- **Railway compute hard cap:** $15 (was $10).
- **Edge WAF status:** `mainnov.tech` is on **Hostinger DNS — NOT behind Cloudflare** (DEC-068), so no
  edge WAF on the prod app. Cloudflare Free managed/OWASP rulesets are Pro-only. Free-path migration
  runbook prepared (`SnapAI_Cloudflare_Free_WAF_Migration_Runbook.md`).
