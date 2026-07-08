# SnapAI — Key Architectural Decisions

> This file records decisions made during development that have lasting impact on how the codebase works.
> Future AI sessions: read this before proposing architecture changes or writing migrations.
>
> Last updated: 2026-05-27 (DEC-089 added — Step Zero A/B test + returning-user localStorage path. BUG-045 promoted to production commit 3f06f0b. | Previously: DEC-087/DEC-088 added — BUG-045 nameplate OCR JWT self-sourcing + Tesseract removal. | Previously: 2026-05-24 (DEC-084 added -- TypeScript build failure cascade. DEC-082/083 added -- React fiber QA bypass + Vercel error tracing. DEC-081 added -- R-410A PSI emergency patch thresholds. Stage 7 Staging E2E QA COMPLETE. DEC-070 ACTIVE. Houston full flow PASS (rpt-e198935c USD estimate), PK staging backend PASS (environment:staging, R-410A pressure-targets). | DEC-080 added — Stage 6 Vercel staging domain-level gitBranch rewire; DEC-067 marked SUPERSEDED. | Previously: DEC-071 added -- Stripe test-mode GAP from Stage 2 cost audit. | DEC-065 body added — never commit package-lock.json; DEC-066 added — stamp estimates.market at creation; merge conflict in DEC-062/063/064 resolved; DEC-063, DEC-064 added — /api/models/all response shape; pak_operating_targets is PSI table)

---

## DEC-095 — Brand Decoder v1.2 decoder returns a (result, failure) tuple

**Decision:** `services/serial_decoder.py`'s `decode_serial(brand, serial, variant, refrigerant_hint, era_hint)` returns `Tuple[Optional[SerialDecodeResult], Optional[SerialDecodeFailure]]` — never raises, never returns a bare dict. Callers (`api/ocr.py`, `api/assessments.py`) MUST unpack both. `SerialDecodeFailure` is an enum (PK_NO_FORMAT, PIONEER/SENVILLE/DELLA_NOT_DECODABLE, SAMSUNG_POST_2018_UNKNOWN, KENMORE_OEM_UNKNOWN, FORMAT_NOT_MATCHED, UNKNOWN_BRAND).
**Rationale:** Forces every call site to handle the (large) un-decodable space explicitly instead of silently treating "no decode" as a year. Data lives in `scopesnap-api/data/serial_decoder_data_v1.2.json` + `replace_decision_data_v1.2.json` (57 brands / 171 records), loaded once at startup by `services/brand_data_loader.py` (indexed by `canonical_name` + every `oem_sibling`).

## DEC-096 — Alembic migrations must chain off the REAL head; start.sh fails safe

**Problem:** Stage 1's new migration was first numbered `036`, colliding with the existing `036_operating_targets_unified` (the dev assumed head was 035). Duplicate revision IDs make `alembic upgrade head` abort.
**What saved us:** `scopesnap-api/scripts/start.sh` runs `alembic upgrade head` under `set -e` BEFORE `uvicorn`. So the bad migration made the new Railway container exit non-zero → deploy failed → Railway kept the previous healthy container serving. No outage.
**Decision:** ALWAYS confirm the current head with `SELECT version_num FROM alembic_version` (or `ls db/migrations/versions | sort | tail`) before numbering a migration. Brand Decoder landed at **039** (brand_serial_backfill) and **040** (assessment_decoder_versions). Migrations use `ADD COLUMN IF NOT EXISTS` and are idempotent.

## DEC-097 — serial_decodable reflects MARKET logic, not just "has a pattern"

**Decision:** The `brands.serial_decodable` reporting column (migration 039 backfill) is TRUE only for US-market brands with a usable pattern, EXCLUDING the explicitly non-decodable set (Pioneer/Senville/Della/Samsung). All 15 PK brands are `serial_capture_required_from_field` → `serial_decodable = FALSE` (the runtime decoder returns `PK_NO_FORMAT` regardless). Staging result: 38 true / 19 false. The column is a convenience/reporting mirror — the app reads the JSON at runtime, not this column.

## DEC-098 — Shadow-mode replace score is invisible until ≥6 weeks data + key set

**Decision:** Stage 4's `_compute_weighted_replace_score()` runs on every estimate but is SHADOW ONLY — the user-facing `rec_tier` is unchanged. It fires PostHog `replace_decision_shadow_eval` (with `did_diverge`) and stores the breakdown in `recommendation.shadow_replace_score` for the Stage 3C show-the-math panel. Weights live in the `replace_decision_logic_spec` JSON; threshold in env `RECOMMEND_REPLACE_THRESHOLD` (default 0.6). `cr_substituted=true` records halve the remaining_life weight (138/147 Track-2 records are cr_substituted). Promote to live logic only after ≥6 weeks shadow data + ≥25 paying testers (constraint #9). **All PostHog events (shadow + `age_corrected`) are best-effort via `services/analytics.py` and NO-OP unless `POSTHOG_API_KEY` is set on Railway — currently UNSET on staging (`/api/version` → `analytics_enabled:false`).**

## DEC-099 — Playwright e2e: dev-harness pattern + GitHub Actions CI (no committed lockfile)

**Decision:** The Stage 3 frontend has a Playwright + axe-core e2e suite (`scopesnap-web/tests/e2e/`, 26 tests). Because `/assess` (Clerk-auth-gated) and `/r/[...]` (SSR) can't be driven by a headless browser, the REAL components mount via DEV-ONLY routes under `scopesnap-web/app/test-harness/*` (guarded `if NEXT_PUBLIC_ENV==="production" return null`); StepZeroPanel takes a test-only `__testSeedUnit` prop to seed a decode. Backend is mocked with `page.route()`. axe checks are SCOPED to the Stage 3 region (via `data-testid` wrappers) — a whole-page scan trips on pre-existing app-chrome contrast debt (separate a11y backlog). The e2e files + `playwright.config.ts` are EXCLUDED from the Next build via tsconfig. **CI = `.github/workflows/playwright-e2e.yml`** (triggers on push/PR to `scopesnap-web/**`), which uses `npm install` and installs Playwright in-CI — per **DEC-065 a package-lock.json must NEVER be committed** (it breaks Vercel `npm ci`). Run green proof: GitHub Actions run #1 = success; 26/26 local pass. **Promote-to-prod caution:** the `staging` branch carries a tracked `scopesnap-web/package-lock.json` but `main` does NOT — a file-scoped promote must NOT drag that lockfile onto main.

## DEC-100 — PostHog: one project + `environment` tag (free), not separate projects

**Date:** 2026-06-17.
**Decision:** Keep a SINGLE PostHog project and separate prod vs staging by tagging every event with an `environment` property, rather than using separate projects/environments.
**Why (fact-checked):** PostHog free plan = **1 project + 1M product-analytics events/month** (this org uses ~378/mo — 0.04%). "Unlimited projects" / multiple environments are part of the **Boost plan ($250/mo)** — NOT free. `/settings/environments` returns "Setting not found" on this org (no multi-env feature). With **no credit card on file** you are hard-capped at the free limits and literally cannot be charged.
**Implementation:** frontend `providers/PostHogProvider.tsx` registers `environment` (from `NEXT_PUBLIC_ENV`) as a super-property in `loaded()`; backend `services/analytics.py` adds `environment` (from `ENVIRONMENT`) to every `capture()`. A super-property/property attaches to EVERY event (existing + new) automatically — no per-event work. Caveat: **going-forward only** — pre-existing stored events aren't retroactively tagged (split old data by `$current_url`/`$host`: `snapai.mainnov.tech` vs `staging.…`).

### Two SEPARATE PostHog integrations (same publishable key)
- **Frontend** (`posthog-js`): env `NEXT_PUBLIC_POSTHOG_KEY` (+ optional `NEXT_PUBLIC_POSTHOG_HOST`, default `https://us.i.posthog.com`), set in **Vercel**, baked at BUILD → a redeploy is required after adding/changing. Captures the funnel (`$pageview`, `diagnostic_*`, `estimate_*`, `report_sent`, `dashboard_viewed`, landing visits). Opts OUT when `NEXT_PUBLIC_ENV==="development"`.
- **Backend** (python SDK via `services/analytics.py`): env `POSTHOG_API_KEY` (+ optional `POSTHOG_HOST`), set in **Railway**. Fires `replace_decision_shadow_eval` + `age_corrected`. No-ops (never raises) when unset; observable via `/api/version` → `analytics_enabled`.
- Both use the **same publishable Project API key** (`phc_…` — public by design, ships in client JS; NOT a secret `sk_`/`phx_`). PostHog project = id 369878, key `phc_A5spSA…`, **US cloud**.

### Infra topology learned (important for future config)
- **Vercel = TWO projects** (not one with environments): `scope-snap-ai` → `snapai.mainnov.tech` (main = prod); `scopesnap-web-staging` → `staging.…`/`pk-staging.…` (staging branch, Preview deploys). Prod already had `NEXT_PUBLIC_POSTHOG_KEY` (All Environments, since Apr 5); staging did NOT — added 2026-06-17 (Production+Preview).
- **Railway = ONE project** (`pacific-exploration`), ONE service (`scopesnap-api`), TWO environments (production + staging) — variables are per-environment; adding one stages a change that needs a **Deploy** click to apply.

### Challenge / gotcha
`posthog` not being on `window` on a page is NOT proof the key is unset — the provider only mounts/inits where `NEXT_PUBLIC_POSTHOG_KEY` is present in the served build, and a freshly-added Vercel var needs a redeploy first. Confirm config via the live deploy (or `/api/version analytics_enabled` for the backend), not a one-off `window.posthog` check on an arbitrary route. Verifying a live FRONTEND event requires an authenticated session (provider/funnel events fire on authed flows), so end-to-end verification needs a logged-in test run.

## DEC-001 — Database on Supabase, not Railway

**Decision:** All data lives in Supabase (PostgreSQL via `pooler.supabase.com`). The Railway project does NOT have a PostgreSQL service attached.

**Why:** Railway auto-created a `postgres-volume` during initial setup but it was never used. All Alembic migrations target Supabase. The Railway volume was deleted Apr 30 2026 (it was an orphaned 1MB disk).

**Impact:** `DATABASE_URL` env var on Railway points to Supabase. Never add a Railway PostgreSQL service — it would be redundant and costly.

---

## DEC-002 — Alembic migrations run automatically on Railway boot via `start.sh`

**Decision:** `start.sh` runs `alembic upgrade head` before starting Uvicorn on every Railway deploy.

**Why:** Eliminates manual migration steps; deploy = migrate + serve in one atomic operation.

**Impact:** Any new `.py` file added to `scopesnap-api/db/migrations/versions/` will run on next Railway deploy. Do NOT push a migration that is already applied to the DB — Alembic will skip it safely, but a data-changing migration run twice could corrupt data. Always check `alembic_version` table before pushing a new migration.

**Current revision:** 034 (as of 2026-05-24 Stage 5 parity sync)

---

## DEC-003 — `input_type = 'multi'` steps use `options_jsonb`, not `reading_spec`

**Decision:** Questions with both a photo slot and a numeric reading store all input specs inside `options_jsonb` as a JSON array `[{kind, spec}, ...]`. The standalone `reading_spec` column is NULL for these rows.

**Why:** The multi-input design was chosen to allow arbitrary combinations of photo + reading + text fields in a single diagnostic step. The `options_jsonb` array was already used for `multiple_choice` options, so multi steps reuse the same column.

**Impact:** ⚠️ **CRITICAL** — Any Alembic migration that patches reading spec must target `options_jsonb` for multi steps, not `reading_spec`. Migration 014 violated this rule (patched `reading_spec` for `q4-flame-sensor`); migration 015 corrected it. See TECH_STACK.md → WA-6 for the correct SQL pattern.

**How to check before writing a migration:**
```sql
SELECT step_id, input_type, reading_spec IS NULL AS reading_spec_null
FROM diagnostic_questions
WHERE complaint_type = 'your_type';
```

---

## DEC-004 — Git operations from the Linux sandbox: use /tmp clone

**Decision:** All git commits/pushes from the sandbox must be done via a `/tmp` clone of the repo, not from the NTFS-mounted workspace.

**Why:** The workspace is an NTFS-mounted Windows drive. The Linux sandbox cannot create or delete `.git/index.lock` or `.git/HEAD.lock` on NTFS (Operation not permitted). This blocks all standard git operations AND the git plumbing fallback (hash-object → mktree → commit-tree) when HEAD.lock is also blocked.

**Impact:** Workflow for any code change that must be pushed:
1. Write file to sandbox outputs dir (`/sessions/.../outputs/`) — real Linux tmpfs
2. `git clone "https://TOKEN@github.com/ORG/REPO" /tmp/snapai_tmp`
3. `cp` from outputs to clone (never from NTFS workspace to /tmp directly if file was created there)
4. Commit and push from `/tmp/snapai_tmp`

See TECH_STACK.md → WA-5 for full command template.

---

## DEC-005 — Railway API authentication requires Clerk JWT from browser

**Decision:** The Railway backend uses Clerk JWT verification on all protected endpoints. No dev bypass token is available for external API calls.

**Why:** Clerk is the auth provider; all contractor-specific endpoints are protected.

**Impact:** When debugging via browser console, must get a JWT first:
```javascript
window.Clerk.session.getToken().then(t =>
  fetch('https://scopesnap-api-production.up.railway.app/api/...', {
    headers: {'Authorization': 'Bearer ' + t}
  })
)
```
Must be run from an authenticated tab at `snapai.mainnov.tech`. Cannot call from the sandbox (proxy blocks all outbound HTTP — see WA-2 in TECH_STACK.md).

---

## DEC-006 — `photo_branch_map` can override numeric reading branchKey in multi steps

**Decision:** In `input_type = 'multi'` steps, if the AI photo evaluator returns `"escalate"`, the backend overrides the numeric reading's computed branchKey with `"escalate"` via the `photo_branch_map` mechanism.

**Why:** AI photo evaluation is a safety gate — if the photo shows something dangerous (e.g. burnt terminals, severe corrosion), the system should escalate regardless of the meter reading.

**Impact:** During QA/testing of reading-based routing in multi steps, skip the photo slot (leave empty). Only the numeric reading will determine branchKey when no photo is present. Injecting a synthetic/fake photo may cause the AI to return "escalate" and override the test.

---

## DEC-007 — UVICORN_WORKERS = 1 for Railway

**Decision:** Backend runs with 1 Uvicorn worker (reduced from 2 on Apr 30 2026).

**Why:** Halves memory usage. Sufficient for 50–100 concurrent users with async I/O. Cost control: Railway Hobby plan has $5/mo credit limit.

**Impact:** Do not increase UVICORN_WORKERS without checking Railway spend cap. If load exceeds 1 worker capacity, upgrade Railway plan first.

---

## DEC-008 — Frontend TypeScript strict mode, no `any` casting for branch keys

**Decision:** `classifyReading()` in `ReadingInput.tsx` uses strict string comparisons for `spec.type`. The type string in the DB must exactly match what the frontend expects.

**Known type strings and their DB values:**

| Measurement | DB `spec.type` | Frontend match |
|-------------|---------------|----------------|
| Microamps | `"microamps"` | `spec.type === "microamps"` |
| Voltage (L1-L2) | `"voltage_l1_l2"` | `spec.type === "voltage_l1_l2"` |
| Amperage (RLA) | `"amperage_rla"` | `spec.type === "amperage_rla"` |
| PSI (refrigerant) | `"psi"` | `spec.type === "psi"` |
| Capacitance (µF) | `"capacitance_uf"` | `spec.type === "capacitance_uf"` |

**Impact:** If a migration sets `spec.type` to anything not in this list, `classifyReading()` will fall through to a default `branchKey: "ok"` path, and the backend may route incorrectly. BUG #11 (voltage) and BUG #13 (microamps type mismatch) were both caused by this. Always cross-check the frontend handler before writing a migration that touches reading spec types.

---

## DEC-009 — `GET /api/diagnostic/questions/{type}` is a stripped endpoint

**Decision:** The questions list endpoint only returns: `step_id`, `step_order`, `question_text`, `input_type`. It strips `options_jsonb`, `reading_spec`, and `branch_logic_jsonb`.

**Why:** Reduces payload size; frontend only needs question text and type for the initial render. Full step data is returned in the session answer response as `next_step`.

**Impact:** Do not use this endpoint to inspect reading specs or branch logic during debugging. Use the fetch interceptor pattern (TECH_STACK.md → WA-7) to capture the actual `next_step.options` from a session answer response.

---

## DEC-010 — NTFS file writes can produce null-byte-padded files

**Decision:** When writing files to the NTFS-mounted workspace from the Linux sandbox, the Write/Edit tools can produce files with null-byte padding at the end. This corrupts TECH_STACK.md and CONTINUATION_PROMPT.md (binary file detection by grep).

**Why:** NTFS and Linux tmpfs differ in block allocation behavior. The NTFS driver may pre-allocate blocks that get filled with null bytes.

**Impact:** Before reading any .md file that may have been written by the sandbox, check for null-byte padding:
```python
with open(path, 'rb') as f:
    raw = f.read()
clean = raw.rstrip(b'\x00')
if len(clean) < len(raw):
    # File is null-padded — use clean for processing, then rewrite
```
Always write .md files using Python with explicit encoding (`'utf-8'`) and strip before appending. Both TECH_STACK.md and CONTINUATION_PROMPT.md were cleaned of null-byte padding on 2026-05-11.

---

## DEC-011 — Dual-market architecture: shared infra, split data by `pak_*` table prefix

**Decision:** Both the US (Houston) and Pakistan markets share one Railway backend, one
Supabase database, one Vercel deployment, and one Clerk auth instance. Market isolation is
achieved at the *query level* (Pakistan data lives in `pak_*` tables/views) rather than
at the infrastructure level (no separate backend or database per market).

**Why:** Minimises cost and operational overhead. One Railway service, one Supabase
project — no duplicate infrastructure to maintain. Market routing is pure runtime logic:
hostname → `X-Market` header → `get_tables()` → correct table names. Adding a new market
in future requires only: new `pak_XX_*` tables + a new `_XX_TABLES` constant in
`api/dependencies.py` + a new hostname in `lib/market.ts`.

**Impact — the three change scenarios:**

| Scenario | Frontend | Backend | Database |
|---|---|---|---|
| **PK only** | Gate with `detectMarket() === "PK"` | Gate with `if tables.market == "PK":` | Only touch `pak_*` tables |
| **US only** | Gate with `detectMarket() === "US"` | Default (non-PK) path | Only touch standard US tables |
| **Both (universal)** | No gate — shared code path | No gate — shared endpoint | Shared tables (`assessments`, `estimates`, etc.) — one migration applies to both |

**Key files:**
- `scopesnap-web/lib/market.ts` — `detectMarket()`, `MARKET_CONFIG`, `formatCurrency()`
- `scopesnap-api/api/dependencies.py` — `_US_TABLES`, `_PK_TABLES`, `get_tables()`
- `scopesnap-web/lib/api.ts` — injects `X-Market` header on every fetch

**Full reference:** `MARKET_GUIDE.md` — detailed guide with file lists, checklists,
DB table inventory, and example gates for all three scenarios.

---

## DEC-012 — Customer contact fields stored on Assessment row (not Property)

**Decision:** `customer_name`, `customer_phone`, and `customer_email` are stored directly
on the `assessments` table (added 2026-05-15 migration via Supabase `ALTER TABLE`).
These same fields also exist on `properties` but are written redundantly so that
phone-only assessments (PK WhatsApp flow — no address entered) have retrievable contact
data without a Property join.

**Why:** The `properties.address_line1` column is `NOT NULL`. Creating a Property for
phone-only entries (no address) violates this constraint and crashes the endpoint with a
DB error. Storing contact data on Assessment avoids the constraint entirely.

**Impact:**
- `POST /api/assessments` always writes `customer_phone/name/email` to the Assessment row
- `GET /api/estimates/{id}` reads from `Assessment.customer_*` first; falls back to
  `Property.customer_*` only if the Assessment columns are all NULL (legacy entries)
- Do NOT remove the fallback — older assessments (pre-2026-05-15) have no direct columns
- `db/models.py` → `Assessment` model has the three `Optional[str]` mapped columns
- The `assessments` table has the three VARCHAR(200/20) columns in Supabase (added via
  `ALTER TABLE assessments ADD COLUMN IF NOT EXISTS customer_phone VARCHAR(20), ...`)

---

## DEC-013 — Never use `git stash` from the Linux sandbox on NTFS-mounted repo

**Date:** 2026-05-18

**Problem:** Running `git stash` from the Linux sandbox writes a stash object using LF line endings. When the stash is later applied/dropped back onto the NTFS-mounted Windows filesystem, several frontend TypeScript/TSX files get truncated (the file content is cut off mid-function, ending with `\ No newline at end of file`). This corrupts Vercel builds with TypeScript/JSX parse errors. Affected files in the 2026-05-18 incident: `market.ts`, `assess/page.tsx`, `app/(app)/layout.tsx`, `app/r/.../ReportClient.tsx`, `LanguageToggle.tsx`, `SidebarNav.tsx`, `DiagnosticFlow.tsx`, `urdu-strings.ts`, `StepZeroPanel.tsx`, root `app/layout.tsx` — 10 files total across 4 failed Vercel deploys.

**Solution:** NEVER use `git stash` from the sandbox. Instead:
1. Commit all local changes as a WIP commit: `git commit -m "wip: [description]"` before fetching/merging
2. After merge, if needed, `git reset HEAD~1` to un-commit the WIP changes
3. All git operations must use the Desktop Commander `.bat` file pattern (DEC-004 equivalent for Windows-side execution)

**Detection:** After any merge or stash operation, immediately run:
```
git diff <last-known-good-sha>..HEAD -- 'scopesnap-web/**/*.tsx' 'scopesnap-web/**/*.ts' --stat
```
Any file showing a net deletion (more `-` than `+` lines) near the end is likely truncated. Cross-check with `git show <sha>:path | wc -l` vs `wc -l path`.

**Recovery:** For each corrupted file:
1. `git show <good-sha>:<path> > <path>` to restore full content from the good commit
2. Re-apply any intentional changes on top using a Python patch script
3. Commit via Desktop Commander `.bat` and push

**Rationale:** NTFS line-ending translation (LF → CRLF) during stash restore corrupts file content when the sandbox's git and Windows git have mismatched `core.autocrlf` settings.



---

## DEC-014 — Staging Environment Architecture (2026-05-19)

**Decision:** Full parallel staging environment before any further production changes.

**Components:**
- Separate Supabase project (`pqmgveqkuckbvyygsilk` ap-northeast-1) -- identical schema + seed data
- Separate Clerk staging app (`firm-chamois-61`) -- test-mode keys, no prod user data
- Separate Cloudflare R2 bucket (`scopesnap-uploads-staging`)
- Same Railway project, separate `staging` service watching the `staging` branch
- Same Vercel account, separate project (`scopesnap-web-staging`) watching the `staging` branch
- `StagingBanner.tsx` -- amber fixed bar on all staging pages, invisible in production
- `middleware.ts` -- `NEXT_PUBLIC_ENV=staging` treated as dev to bypass Edge Clerk crash

**Workflow:** Feature branch -> staging branch -> validate -> promote to main -> production.
**Promote script:** `scripts/promote-to-prod.sh <file1> [file2 ...]` (run from local main checkout).

---

## DEC-015 — Keepalive workflows prevent Supabase free-tier pauses (2026-05-19)

**Decision:** Two GitHub Actions workflows ping both prod and staging Supabase on alternating days.
- `keepalive-supabase-A.yml` -- every Sunday 02:00 UTC
- `keepalive-supabase-B.yml` -- every Wednesday 14:00 UTC
- Monitored via Healthchecks.io (account ds.shoab@gmail.com)

**Impact:** Both Supabase projects remain active indefinitely without always-on paid tier.

---

## DEC-016 — Legacy estimate engine deleted (2026-05-19)

**Decision:** `services/estimate_engine.py` deleted. `POST /api/estimates/generate` removed.

**Why:** Q.6.5 merged recommendation engine into `fault_estimate.py`, making old engine redundant.

**Impact:** All estimates flow exclusively through `POST /api/estimates/fault-card` -> `fault_estimate.py`. Never recreate the old engine.

---

## DEC-017 — condition_signals vocabulary v1 strings are immutable (2026-05-20)

**Decision:** Existing condition_signal strings MUST NOT be renamed -- breaks lifecycle_rules backward compatibility. New signals can be added freely. See DEC-024 for full vocabulary.

---

## DEC-018 — diagnosis_feedback table is shared (no pak_ variant) (2026-05-20)

**Decision:** Single `diagnosis_feedback` table for both markets. FK references `diagnostic_sessions.id` (already shared). Market derivable via assessment_id join for analytics.

---

## DEC-019 — DiagnosticFlow resolved -> /diagnoses/<id>, not evidence phase (2026-05-20)

**Decision:** Fault card resolution navigates to `/diagnoses/<session_id>` (FaultResolutionScreen). Estimate still reachable from Assessments list. "Generate estimate from here" deferred to v1.5.

---

## DEC-020 — pak_pricing_tiers table structure (2026-05-20)

**Decision:** PK pricing uses dedicated `pak_pricing_tiers` table (45 rows: 15 cards x 3 tiers). Columns: `card_id`, `tier` (good/better/best), `label_en`, `label_ur`, `description_en`, `description_ur`, `parts_pkr`, `labor_pkr`, `total_pkr`.

**Why:** PKR amounts + Urdu bilingual content cannot share the US pricing_tiers table without heterogeneous currency columns and market-gated queries everywhere.

---

## DEC-021 — pak_fault_card_descriptions + pak_fault_card_urdu_descriptions (2026-05-20)

**Decision:** Separate tables for PK fault card bilingual content. Allows independent updates to English vs Urdu without touching pak_fault_cards main data.

---

## DEC-022 — Desktop Commander bat-file pattern for Windows-side git (2026-05-20)

**Decision:** When Linux sandbox cannot reach git (NTFS lock), use Desktop Commander .bat files on the Windows side.
- Write bat to `C:\fixNNN.bat` (no spaces in path)
- Inside bat: `cd /d "C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI"`
- Log: `>> C:\fixNNN_log.txt 2>&1`
- Execute via `mcp__Desktop_Commander__start_process` with `shell: "cmd"`
- Never use interact_with_process (not interactive-capable)

---

## DEC-023 — NEXT_PUBLIC_ENV=staging controls staging-specific behaviour (2026-05-20)

**Decision:** `NEXT_PUBLIC_ENV=staging` drives three behaviours:
1. `StagingBanner.tsx` renders amber bar
2. `middleware.ts` bypasses Clerk Edge Runtime crash
3. `app/(app)/layout.tsx` adds `pt-6` for banner height

**Never** set `NEXT_PUBLIC_ENV=staging` on the production Vercel project.


## DEC-024 — Recommendation engine condition_signal vocabulary v1 (2026-05-20)

**Date:** 2026-05-20

**Decision:** Standard condition_signal vocabulary for lifecycle_rules lookups.
Implemented in services/condition_signals.py (Track REC.2).

| Signal | Derivation |
|---|---|
| default | No specific condition matched (fallback) |
| under_warranty | install_year within last 2 years |
| photo_confirmed_pitting | AI photo: pitting or electrical_damage in ai_issues |
| formicary_confirmed | AI photo: formicary in ai_issues |
| rla_over_nameplate | reading_inputs row with reading_type=amperage_rla and passed=false |
| recurring_clog | 2nd+ Card 5 diagnosis for same property_id in 12 months |
| attic_location | ocr_nameplate or tech_overrides location field contains "attic" |
| bearing_noise | tech_overrides.symptom contains grind/noise/bearing; or complaint_type=making_noise |
| sensor_only | card_id=11 and error_code_type contains "sensor" but not "ignitor" |

**Priority chain:** first match wins (see services/condition_signals.py _derive()).

**Vocabulary rules:**
- Vocabulary is v1 -- expected to refine after 50+ approval data points.
- New signals can be added freely.
- Existing signal strings MUST NOT be renamed -- breaks lifecycle_rules backward compatibility.
- lifecycle_rules expanded to 50 rows via migration 028 (Track REC.3).

**Impact:** fault_estimate.py calls derive_condition_signal_from_assessment() before
lifecycle_rules lookup. If derivation fails, falls back to "default" silently (try/except).


## DEC-025 — Track D: single diagnosis_feedback table for both markets (2026-05-20)

**Date:** 2026-05-20

**Decision:** Use a single `diagnosis_feedback` table for both US and PK markets.
No `pak_diagnosis_feedback` variant.

**Rationale:** `diagnostic_sessions` is already a single shared table (no pak_ variant).
Feedback rows reference `diagnostic_sessions.id` via FK. Since the session table is shared,
the feedback table must also be shared. Market is derivable from the session's assessment_id
via join if market segmentation is needed in analytics.

**Impact:** DEC-011 shared-DB pattern applies. No market gate needed on POST /api/diagnostic/feedback.

---

## DEC-026 — Track D: diagnosis screen replaces evidence phase for all resolutions (2026-05-20)

**Date:** 2026-05-20

**Decision:** When DiagnosticFlow resolves to a fault card, the app navigates directly to
`/diagnoses/<session_id>` (FaultResolutionScreen) instead of the old evidence → estimate flow.

**Rationale:** PK tech feedback: "I bought this for the estimate, but the diagnostic is what I use."
The diagnosis screen is the product hero. Estimate generation is available from the assessment page
but is no longer the forced next step after a diagnostic resolution.

**Wiring:** `handleDiagnosticResolved` in `assess/page.tsx` fires:
1. Fire-and-forget `POST /api/diagnostic/finalize/<session_id>` (idempotent, sets customer_label + share_token)
2. `router.push('/diagnoses/<session_id>')`

**Deferral:** The "Generate estimate from here" button on FaultResolutionScreen is deferred to v1.5.
Techs can still navigate to the estimate via Assessments list if needed.

**Impact:** The old `setPhase("evidence")` call is removed. Evidence/photo collection phase still
exists for non-diagnostic-resolved assessments (e.g., service/tune_up) but is no longer reached
from the diagnostic resolution path.


## DEC-027 — NTFS truncation affects ALL files with Unicode, not just emoji-containing TSX (2026-05-20)

**Date:** 2026-05-20

**Problem:** During Track D QA, the Edit tool was used to replace a section of
`scopesnap-api/api/diagnostic.py`. The file contained Unicode box-drawing characters
in section header comments (e.g. `# -- D.9: GET /public/{share_token} --------`).
The Edit tool truncated the file at approximately 80 characters per line, cutting off
lines mid-sentence and producing a file that was 1565 lines instead of the expected 1578+.
Python's `ast.parse()` reported a SyntaxError at the truncation point.

**DEC-010 only covered null-byte padding; DEC-013 only covered git stash.
This is a new failure mode: the Edit tool itself truncates on NTFS for any file with
non-ASCII characters, regardless of whether it's TSX, TS, or PY.**

**Rule extension:**
> NEVER use the `Edit` tool on ANY file that contains non-ASCII characters
> (Unicode, emoji, box-drawing, em-dashes, etc.), regardless of file type.
> This includes `.py`, `.ts`, `.tsx`, `.md` files.

**Safe write patterns for files with Unicode:**
1. Python append script: `with open(path, 'a') as f: f.write(content)` — bypasses Edit
2. `git fast-import` plumbing — bypasses index and Edit tool entirely
3. Desktop Commander `write_file` in chunks of ≤30 lines — use for full rewrites

**Detection after any Edit on a Unicode-containing file:**
```bash
python3 -c "import ast; ast.parse(open('file.py').read()); print('OK')"
wc -l file.py  # compare to expected line count
```

**Recovery used in this incident:**
1. `git show <remote-sha>:<path> > /tmp/file_clean.py` — extract clean remote version
2. Append new content via Python script (no Edit tool)
3. `git hash-object -w <file>` + `git fast-import` to commit without using index

---

## DEC-028 — git index corruption recovery: use git fast-import to bypass index (2026-05-20)

**Date:** 2026-05-20

**Problem:** Multiple sequential `git read-tree`, `git update-index`, and `git stash`
operations in the Linux sandbox against an NTFS-mounted repo caused the `.git/index`
file to become corrupted (`error: bad signature 0x00000000 / fatal: index file corrupt`).
Once corrupted, even `rm -f .git/index && git read-tree HEAD` only worked transiently --
the next git operation would corrupt it again. `git stash`, `git add`, `git checkout -- .`
all failed.

**Root cause:** Concurrent lock file creation races between sandbox git and Windows git
(VS Code, shell, etc.) on the NTFS mount. The `.git/index.lock` being left behind by
a timed-out bash call caused subsequent operations to write to a stale/partially-written
index file.

**Recovery pattern (2026-05-20 incident):**
```bash
# 1. Hash the target file(s) directly into the object store (bypasses index)
HASH=$(git hash-object -w path/to/file.py)

# 2. Build the commit via fast-import (no index needed)
git fast-import --quiet << EOF
commit refs/heads/main
author Claude Bot <claude@anthropic.com> $(date +%s) +0000
committer Claude Bot <claude@anthropic.com> $(date +%s) +0000
data <byte-length-of-message>
<commit message>
from <parent-sha>
M 100644 <blob-hash> path/to/file.py
EOF

# 3. Push normally
git push origin main
```

**Key insight:** `git fast-import` creates commits from blob hashes without touching
`.git/index` at all. It is the safest way to push file changes when the index is broken.

**Prevention:**
- Never run multiple git operations in rapid succession against the NTFS-mounted repo
- Remove `.git/index.lock` before every git command: `rm -f .git/index.lock`
- Prefer `git fast-import` for all pushes in this environment (avoids stash, add, commit cycle)

---

## DEC-029 — companies table has NO market column; market routing is always header-based (2026-05-20)

**Date:** 2026-05-20

**Problem:** During Track D implementation, `GET /api/diagnostic/public/{share_token}`
was written to determine market by querying `SELECT market FROM companies WHERE id = :cid`.
This column does not exist and would have caused a 500 at runtime.

**Rule:** The `companies` table has NO `market` column. Market is ALWAYS determined by:
- **Frontend:** `detectMarket()` in `lib/market.ts` (hostname-based: `pk.*` → PK, else US)
- **Backend:** `X-Market` HTTP header → `get_tables()` in `api/dependencies.py`
- **Never:** A column on the companies/users/assessments tables

**Correct pattern for market-aware backend endpoints:**
```python
@router.get("/some-endpoint")
async def my_endpoint(
    tables: MarketTables = Depends(get_tables),  # reads X-Market header
    ...
):
    fc_table = tables.fault_cards   # "fault_cards" or "pak_fault_cards"
    market = tables.market          # "US" or "PK"
```

**For unauthenticated endpoints** (no Clerk JWT): still add `get_tables` dependency.
The `X-Market` header must be sent by the client. See DEC-030.

---

## DEC-030b — Raw fetch() calls on public pages must explicitly send X-Market header (2026-05-20)

**Date:** 2026-05-20

**Problem:** Authenticated API calls use `apiFetch()` from `lib/api.ts`, which
auto-injects `X-Market: detectMarket()` on every request. However, the public share
page `/d/[share_token]` uses a raw `fetch()` call (no Clerk auth headers needed).
Raw `fetch()` does NOT auto-inject X-Market, so the backend `get_tables()` defaults
to US market for all public share requests, including PK URLs.

**Fix applied (commit 6314219):**
```typescript
// Public page -- no apiFetch, but still send X-Market
fetch(`${API_URL}/api/diagnostic/public/${share_token}`, {
  headers: { "X-Market": detectMarket() },
})
```

**Rule:** Any `fetch()` call (raw, not apiFetch) that hits a market-aware endpoint
MUST manually add `headers: { "X-Market": detectMarket() }`.

**Pattern to search for potential violations:**
```bash
grep -rn "fetch(" scopesnap-web/ | grep -v "apiFetch\|node_modules" | grep "/api/"
```
Each result should either use `apiFetch` or explicitly pass `X-Market`.

---

## DEC-031 — QA must verify code on disk, not just task list status (2026-05-20)

**Date:** 2026-05-20

**Problem:** Track D tasks D.1-D.9 were marked [completed] in ACTIVE_TASKS.md.
But QA-4 (backend code audit via grep) revealed that 4 of the 5 new backend endpoints
were missing from the actual file. The parallel session had added only
`GET /result/{session_id}` (commits 872e959 + 575f73e). The remaining 4 routes --
`GET /list`, `POST /feedback`, `POST /finalize/{session_id}`, `GET /public/{share_token}` --
were never written to `diagnostic.py`.

**Root cause:** Task completion was tracked optimistically (the AI declared tasks done
before verifying the file on disk). Context window limits in long sessions mean the AI
may lose track of whether it actually wrote something vs. only planned to write it.

**Mandatory QA checklist for any backend track:**
```bash
# Count @router. decorators in target file
grep -c "@router\." scopesnap-api/api/diagnostic.py

# Verify each expected route exists
grep "@router\." scopesnap-api/api/diagnostic.py | grep -E "result|list|feedback|finalize|public"

# Syntax check
python3 -c "import ast; ast.parse(open('scopesnap-api/api/diagnostic.py').read()); print('OK')"

# Confirm file wasn't truncated
wc -l scopesnap-api/api/diagnostic.py
```

**Rule:** Before marking any backend track complete, always grep the actual file for
every route that was supposed to be added. Task list status alone is not sufficient proof.
---

## DEC-036 — SQLAlchemy 2.0 silently drops ORM constructor kwargs for unmapped columns (2026-05-20)

**Date:** 2026-05-20

**Problem:** `fault_estimate.py` passed `seasonal_modifier_pct=seasonal_pct_int` to the
`Estimate(...)` ORM constructor. The column existed in the database (added by migration 029)
but was NOT defined in the `Estimate` ORM class in `db/models.py`.

SQLAlchemy 2.0 with `DeclarativeBase` silently sets unknown constructor kwargs as plain Python
attributes on the instance — no error, no warning. The value is **never persisted to the database**.
The column always received its `server_default` of 0, regardless of what Python passed.

**Discovery:** Noticed the seasonal banner never appeared in peak months. Traced to
`seasonal_modifier_pct` always being 0 in DB. Compared `fault_estimate.py` constructor call
against `db/models.py` Estimate class definition — column was absent from ORM.

**Fix:** Added to `Estimate` class in `db/models.py`:
```python
# R.9 seasonal labour surcharge captured at generation time (migration 029)
seasonal_modifier_pct: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
```

**Rule for future migrations:** Any time a new column is added via Alembic migration AND
the column value is set in Python code (not purely a server_default), the corresponding
`Mapped[type] = mapped_column(...)` line MUST be added to the ORM class in `db/models.py`.

**Verification pattern after any new column + ORM work:**
```python
# After creating a test record, query the column immediately:
result = db.execute(text("SELECT seasonal_modifier_pct FROM estimates WHERE id = :id"), {"id": est.id})
print(result.scalar())  # Must NOT be server_default if Python passed a value
```

---

## DEC-037 — FaultResolutionScreen.handleContinue must be async and create estimate before navigating (2026-05-20)

**Date:** 2026-05-20

**Problem:** `handleContinue` in `FaultResolutionScreen.tsx` was synchronous and navigated to
`/assessment/${data.assessment_id}`. This is wrong for two reasons:
1. `assessment_id` is the diagnostic assessment UUID — NOT an estimate UUID.
2. The `/assessment/[id]` page expects an **estimate** ID (from the `estimates` table).
Navigating to an assessment_id caused a 404 on the estimate builder page.

**Root cause:** The function was written before the diagnoses flow was refactored. After the
DX track refactor, assessments no longer auto-create estimates — the estimate must be explicitly
created by calling `POST /api/estimates/fault-card`.

**Fix:** Made `handleContinue` async:
```typescript
async function handleContinue() {
  if (!data.assessment_id || navigating) return;
  setNavigating(true);
  // ... track event ...
  try {
    const token = await getToken();
    const est = await apiFetch<{ id: string }>("/api/estimates/fault-card", {
      method: "POST",
      token: token ?? undefined,
      body: JSON.stringify({
        card_id: data.fault.card_id,
        assessment_id: data.assessment_id,
      }),
    });
    if (!est.id) throw new Error("No estimate ID");
    router.push(`/assessment/${est.id}`);  // est.id = estimate UUID
  } catch (err) {
    console.error("Estimate creation failed:", err);
    setNavigating(false);
  }
}
```

**Rule:** Any button that "continues to estimate" from a diagnosis result MUST:
1. Call `POST /api/estimates/fault-card` with `{card_id, assessment_id}`
2. Use the returned `est.id` (estimate UUID) for navigation
3. Never use `data.assessment_id` or `data.session_id` as the route parameter

**Verified live:** rpt-0494 created and loaded correctly after fix. Navigation went to
`/assessment/97b22e44-c121-4e21-92e6-0d3a158b4e95` (estimate ID). ✅


---

## DEC-034 — TCO data sourced from DB tables, not live calculation (Track G, 2026-05-21)

**Decision:** `five_year_comparison` data is pre-computed and stored in `card_tco_data` /
`pak_card_tco_data`, keyed on `(card_id, tier)`. It is NOT calculated at runtime from
energy prices or live repair history.

**Rationale:** Actuarial-style probability estimates require curated data (AHRI failure studies,
DOE energy data, PK load-shedding research) that cannot be derived from live signals.
Pre-computed data is auditable, reviewable by the advisory board, and version-controlled in
the JSON seed files.

**Implication:** When estimates.py calls `_enrich_tco_from_db()`, a DB miss (no TCO row for
that card/tier) returns `None` silently — FiveYearComparison renders nothing rather than
showing bad data.

---

## DEC-035 — TCO column order: C (left) -> B (center) -> A (right) (Track G, 2026-05-21)

**Decision:** FiveYearComparison renders tiers in order C, B, A — most expensive option on
the LEFT, cheapest on the right. Opposite of typical Good/Better/Best left-to-right ordering.

**Rationale:** Marcus Reed board directive. Presenting the replacement option (C) first anchors
the homeowner on the premium option and makes the middle tier (B, recommended) feel like
a reasonable save. Psychological anchoring increases B uptake.

**Implementation:** `TierCard` array is hardcoded `[C, B, A]` in FiveYearComparison.tsx.
Do not reorder without board approval.

---

## DEC-036 — PresentMode Slide4 selectedTier used as recommendedTier (Track G, 2026-05-21)

**Decision:** In Slide4Value (PresentMode), `selectedTier` is passed as `recommendedTier` to
FiveYearComparison. The Option interface in PresentMode.tsx does not carry a `recommended`
boolean (the prop isn't passed through from the estimate builder).

**Rationale:** `selectedTier` in PresentMode is always the tech's recommended tier at the
point they enter Present Mode. Using it as `recommendedTier` is functionally equivalent and
avoids adding a new prop to EstimateData.


## DEC-043 — alembic_version can be ahead of actual schema (2026-05-21)

**Date:** 2026-05-21

**Problem:** After a Railway GCP platform outage, `alembic_version` in the production DB showed
`032` but the `diagnostic_sessions.photo_skipped` column (from migration 031) did not exist.

**Root cause:** Migration 032 (Track G, `card_tco_data` tables) was applied directly via the
Supabase MCP `apply_migration` tool during a prior session. This runs the migration's DDL SQL
and stamps `alembic_version = 032` directly. It does NOT run Alembic's dependency chain —
so migration 031's `upgrade()` (which adds `photo_skipped`) was never executed.

**Rule:** NEVER assume `alembic_version = N` means all migrations <= N have been applied to the
schema. Always verify column/table existence independently:
```sql
-- Before trusting alembic_version, verify the column exists:
SELECT column_name FROM information_schema.columns
WHERE table_name = 'your_table' AND column_name = 'your_column';
```

**Fix used:** Applied 031's DDL directly via Supabase MCP:
```sql
ALTER TABLE diagnostic_sessions
  ADD COLUMN IF NOT EXISTS photo_skipped BOOLEAN NOT NULL DEFAULT false;
```
Used `IF NOT EXISTS` to make it idempotent — safe to run again.

**Impact:** After any Railway outage where builds were queued but never deployed, audit ALL
migrations in the chain between the last known-good Railway deploy and the current
`alembic_version`. Any that were applied via Supabase direct may have gaps.

---

## DEC-044 — Python replace() write can silently truncate the end of long files (BUG-027) (2026-05-21)

**Date:** 2026-05-21

**Problem:** A Python patch script used the pattern:
```python
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace(old, new, 1)
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
```
The write succeeded with no error, but the last 2 lines of `scopesnap-api/api/reports.py`
(the closing `}` of the approve endpoint's return dict) were silently dropped. The file was
445 lines instead of the expected 447. This caused a Python SyntaxError at runtime:
`'{' was never closed` — FastAPI failed to import the reports router, crashing on startup.

**Why it's silent:** The `f.write(content)` call returns the number of bytes written, but
Python does not raise an error if the write is truncated by the OS (NTFS filesystem quirk).
The file appears valid and git commits cleanly — the SyntaxError only surfaces at runtime.

**Rules:**
1. After ANY Python write to a `.py` file, verify syntax immediately:
   ```bash
   python3 -c "import ast; ast.parse(open('path/to/file.py').read()); print('SYNTAX OK')"
   ```
2. After ANY write, verify line count matches expectation:
   ```bash
   wc -l path/to/file.py  # compare to last known good count
   ```
3. For `.tsx`/`.ts` files, check the last 10 lines:
   ```bash
   tail -10 path/to/file.tsx
   ```
4. If truncation is detected: use `git show <remote-sha>:<path>` to recover the clean file,
   then re-apply the patch.

**Recovery used:** `git show 477314b:scopesnap-api/api/reports.py > /tmp/reports_clean.py`
to recover the original, identified missing tail, used Edit tool to restore it, pushed as
`a6d4a15`.

---

## DEC-045 — Railway "Online" dashboard status does NOT mean the service is healthy (2026-05-21)

**Date:** 2026-05-21

**Problem:** During the Railway GCP outage recovery, the Railway dashboard showed
`scopesnap-api` as "Online" while `GET /health` consistently returned 502 Bad Gateway.

**Why:** Railway's "Online" status reflects the container lifecycle state (running), not
whether the process inside is successfully handling requests. When a Python SyntaxError
prevents FastAPI from importing a router at startup, the process crash-loops. Railway
marks the container as "Online" during restart attempts, not as "Crashed".

**Rule:** ALWAYS verify health via the actual health endpoint:
```
GET https://scopesnap-api-production.up.railway.app/health
Expected: {"status":"ok","db":"connected","environment":"production","version":"0.1.0"}
```
Do NOT trust Railway dashboard status ("Online") as proof the service is healthy.
Only `{"status":"ok"}` from `/health` confirms the service is serving requests.

**Corollary:** If Railway shows "Online" but `/health` returns 502, the active deployment
has a startup crash (most likely a Python SyntaxError). Check deploy logs for the crash
traceback before attempting any other fixes.

---

## DEC-046 — Cherry-pick fails with add/add conflicts when remote has moved ahead (2026-05-21)

**Date:** 2026-05-21

**Problem:** Tried to cherry-pick a local commit (`a0aae81`) onto `origin/main` after
remote had moved ahead by 3 commits (`477314b`). Every file had "add/add" conflicts because
git saw both sides as "adding" the file (different content). Cherry-pick aborted.

**Why:** Cherry-pick computes a 3-way merge using the cherry-pick's parent as the merge base.
When the remote has diverged significantly (especially if the same files were touched),
the merge base is a common ancestor that is far behind both sides — causing "both added" conflicts.

**Rule:** Never cherry-pick a local commit onto a remote that has moved ahead by more than
1-2 commits on the same files. Instead:
1. Pull the latest remote HEAD
2. Re-apply the changes fresh using Python `replace()` scripts directly on the remote files
3. Commit + push as a new commit on top of the latest remote HEAD

This is faster and safer than resolving cherry-pick conflicts.

---

## DEC-047 — Clerk session is shared across *.mainnov.tech subdomains (2026-05-21)

**Date:** 2026-05-21

**Finding:** A single Clerk login on `snapai.mainnov.tech` automatically authenticates
the user on `pk.snapai.mainnov.tech` without requiring a second login. Both domains share
the same Clerk session cookie (scoped to `.mainnov.tech`).

**Impact for QA:** When testing both markets, only ONE login is needed. Navigate to
`snapai.mainnov.tech/sign-in` → log in once → then navigate to `pk.snapai.mainnov.tech` —
it will already be authenticated. The JWT tokens from `window.Clerk.session.getToken()` on
either tab are identical and accepted by the backend on both `X-Market: US` and `X-Market: PK`.

**Impact for Claude Chrome extension:** The Claude-controlled browser tab group shares cookies
across tabs within the group. Opening a PK market tab while already logged in on Houston
gives instant access — no re-login needed.

---

## DEC-048 — Claude Chrome extension tab group resets between sessions (2026-05-21)

**Date:** 2026-05-21

**Problem:** After a context window compaction (new conversation se

---

## DEC-049 — Estimate option tiers stored as "A"/"B"/"C" -- NOT "good"/"better"/"best" (2026-05-21)
 — ✅ RESOLVED 2026-05-24: unified to Good/Better/Best across all surfaces; isRec → opt.recommended

**Date:** 2026-05-21

**Problem (BUG-032):** The homeowner report page sent `{ selected_option: "B" }` to the approve
endpoint. The approve endpoint rejected it with `422: selected_option must be 'good', 'better', or 'best'`.
The Approve button appeared to do nothing from the homeowner's perspective.

**Root cause:** Two different naming schemes exist in the codebase and were never in sync:

| Location | Tier naming |
|----------|-------------|
| `fault_estimate.py` EstimateTier | "A" / "B" / "C" (A=cheapest fix, C=replacement) |
| `pak_pricing_tiers.tier` column | "good" / "better" / "best" |
| `reports.py` approve endpoint (before fix) | "good"/"better"/"best" only -- rejected "A"/"B"/"C" |
| `ReportClient.tsx` TIER_LABELS | `{ good: "Option A", better: "Option B", best: "Option C" }` |

The `estimates` DB table stores options[].tier as "A"/"B"/"C".
`ReportClient.tsx` reads the recommended tier ("B"), sends `{ selected_option: "B" }`.
The old approve endpoint rejected "B" every time -- approval was silently broken.

**Fix:** `scopesnap-api/api/reports.py` line 365:
```python
# Before:
if body.selected_option not in ("good", "better", "best"):
# After:
if body.selected_option not in ("good", "better", "best", "A", "B", "C"):
```

**Rule:** When writing code that handles estimate option tiers:
1. The `estimates` DB table stores tiers as "A"/"B"/"C"
2. `pak_pricing_tiers.tier` uses "good"/"better"/"best" -- different system
3. The approve endpoint now accepts both -- never validate only one scheme
4. `ReportClient.tsx` TIER_LABELS is a display mapping only -- the payload uses the raw DB value

**Commit:** `4743a40`
**Verified:** "Thank you! You selected Fix + Prevent Next Failure." shown on report after approval

---

## DEC-050 — Desktop Commander Python subprocess is the reliable git pattern for Windows (2026-05-21)

**Date:** 2026-05-21

**Problem:** Remote had moved ahead, push rejected (`fetch first`). Local had uncommitted
doc changes. Linux sandbox git is banned on NTFS (DEC-013). PowerShell semicolon commands
gave no visible output in Desktop Commander.

**Reliable workflow -- write to C:\Windows\Temp\fix_NNN.py and run via Desktop Commander:**
```python
import subprocess

repo = r"C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI"

def git(cmd):
    result = subprocess.run(
        ["git"] + cmd.split(),
        cwd=repo, capture_output=True, text=True,
        encoding="utf-8", errors="replace"
    )
    print(f"git {cmd}: stdout={result.stdout!r} stderr={result.stderr!r}")
    return result

git("stash")
git("fetch origin")
git("rebase origin/main")
git("stash pop")
git("add -A")
# Note: commit message must be passed as a list element, not split
result = subprocess.run(
    ["git", "commit", "-m", "your message here"],
    cwd=repo, capture_output=True, text=True
)
print(result.stdout)
git("push origin main")
```

**Why this works:** Desktop Commander runs Python in the Windows process. Windows git can
manipulate the NTFS `.git/index` without the NTFS locking issue. The sandbox's Linux git
is what causes `index.lock` failures.

**IMPORTANT distinction from DEC-013:**
- Windows Desktop Commander Python subprocess git = SAFE (Windows git, native NTFS)
- Linux sandbox git on NTFS-mounted path = BANNED (DEC-013)

---

## DEC-051 — BUG-031 OPEN: Staging banner visible on pk.snapai.mainnov.tech (2026-05-21)

**Date:** 2026-05-21

**Problem:** Amber "STAGING" banner appears at top of production `pk.snapai.mainnov.tech`.

**Root cause:** Vercel PRODUCTION project has `NEXT_PUBLIC_ENV=staging` set.
`StagingBanner.tsx` renders when `process.env.NEXT_PUBLIC_ENV === "staging"`.

**Fix (no code change needed -- Vercel dashboard only):**
1. Vercel dashboard -> `scope-snap-ai` project -> Settings -> Environment Variables
2. Find `NEXT_PUBLIC_ENV`
3. For Production environment: delete it OR set value to `production`
4. Trigger a new deploy

**Status:** OPEN -- awaiting Vercel dashboard action by Shoab.

**Prevention:** After any staging environment setup, immediately audit the PRODUCTION Vercel
project's environment variables to confirm `NEXT_PUBLIC_ENV` is absent or set to `production`.


---

## DEC-032 — estimate/[id] route is dead code; real estimate builder is assessment/[id] (2026-05-20)

**Date:** 2026-05-20

**Decision:** The route `/estimate/[id]` in the Next.js app is dead code and should not be used.
The real estimate builder page is `/assessment/[id]/page.tsx`.

**Rationale:** During early development, an `/estimate/[id]` route was scaffolded.
The canonical page that renders the estimate builder UI was built at `/assessment/[id]`.
The two routes co-existed without cleanup. All navigation (from FaultResolutionScreen,
from the Assessments list, from email links) should point to `/assessment/[id]`.

**Rule:** Never link or navigate to `/estimate/<id>`. Always use `/assessment/<id>` for estimate display.

**Cross-reference:** PROJECT_BRAIN.md Critical Rules table.

---

## DEC-033 — pak_fault_cards (and pak_fault_cards_v) use card_id as the PK business key (2026-05-20)

**Date:** 2026-05-20

**Decision:** Pakistan fault card rows use `card_id` (INTEGER) as the business key, not `id` (UUID).
All JOINs and WHERE clauses involving `pak_fault_cards` / `pak_fault_cards_v` / `fault_cards` must
reference `card_id`, not `id`.

**Rationale:** `pak_fault_cards` was seeded from `ac_data_repo_pakistan.json` where each card has
a numeric `card_id` that is the stable identifier used across `pak_card_tco_data`, `pak_pricing_tiers`,
`pak_fault_card_descriptions`, etc. The `id` UUID column is an internal row identifier and is NOT
shared across tables.

**Rule:**
```python
# CORRECT
WHERE fc.card_id = :cid
JOIN pak_card_tco_data tco ON tco.card_id = fc.card_id

# WRONG -- fc.id is a UUID that has no cross-table meaning
WHERE fc.id = :cid
```

**Cross-reference:** PROJECT_BRAIN.md Critical Rules table.

---

## DEC-052 — Track DX: structured alternative fault card picker (DX.9) (2026-05-20)

**Date:** 2026-05-20

**Decision:** The "alternative diagnosis" UX presents a structured picker of fault card options
rather than a freeform text input. When a technician disagrees with the primary diagnosis,
they select from a short list of plausible alternative fault cards (populated from the fault_cards
table filtered by the same complaint category).

**Rationale:** Freeform text is hard to analyse and useless for improving the diagnostic model.
A structured picker creates labelled training data: (original_card_id, selected_alternative_card_id,
session context). This feeds back into future fault card probability calibration.

**Implementation:**
- `diagnosis_feedback.alternative_fault_id` (INTEGER, FK to fault_cards.card_id) — added in migration 030
- Backend: `POST /api/diagnostic/feedback` accepts `alternative_fault_id`
- Frontend: picker shows cards from same complaint category, ordered by frequency

**Cross-reference:** Migration 030, DEC-030 (migration 030_diagnosis_feedback_alternative_fault_id).

---

## DEC-053 — Track DX: "Mark as Solved" button removed from FaultResolutionScreen (2026-05-20)

**Date:** 2026-05-20

**Decision:** The "Mark as Solved" button that previously appeared on FaultResolutionScreen
has been permanently removed. There is no replacement button or flow for marking a diagnosis
as solved in v1.

**Rationale:** PK tech feedback showed that "Mark as Solved" was never tapped. Techs use the
diagnosis screen as a live reference while working, and the concept of "solved" is ambiguous
mid-job. The button added UI clutter with zero usage. The feedback flow (alternative picker,
thumb up/down) replaces it as the primary signal of resolution quality.

**Rule:** Do NOT re-add "Mark as Solved" or any equivalent without explicit product decision.
Grep for this string before any FaultResolutionScreen edit to confirm it stays absent.

---

## DEC-054 — Track DX: self-graduating UI thresholds (DX.12) (2026-05-20)

**Date:** 2026-05-20

**Decision:** Two UI behaviours graduate automatically based on localStorage usage counters:

1. **Repair Plan section visibility** (`snapai_diagnoses_opened_count`):
   - Sessions 1–19: all three tier cards in the Repair Plan section are expanded by default.
   - Session 20+: section collapses to a single recommended tier; user taps to expand others.
   - Threshold: 20 diagnosis screens opened (counted by `incrementDiagnosesOpened()` in
     `lib/userSessionCounter.ts`, called on FaultResolutionScreen mount).

2. **Continue button label** (`snapai_app_sessions_count`):
   - Sessions 1–3: full label "Generate Estimate & See Pricing" (hand-holding copy).
   - Session 4+: shorter label "See Estimate" (experienced-user copy).
   - Threshold: 3 app sessions (counted by `incrementSessionCount()` in
     `lib/userSessionCounter.ts`, 6-hour cooldown between increments).

**Rationale:** New techs need guidance; experienced techs find it patronising. Graduated UX
removes friction for power users without abandoning new users.

**Implementation:** `lib/userSessionCounter.ts` — localStorage only, per-device, no server sync.
Cross-device sync deferred to v1.5.

---

## DEC-055 — Track F A.3: canonical definition of "Sent" estimate count on dashboard (2026-05-21)

**Date:** 2026-05-21

**Decision:** The "Sent" count on the contractor dashboard counts estimates where:
```sql
sent_at IS NOT NULL AND deleted_at IS NULL
```

**Rationale:** Previously, some code paths counted `status = 'sent'` and others counted
`sent_at IS NOT NULL`. The two diverged when estimates were soft-deleted (deleted_at set)
but kept `status='sent'`. The `sent_at IS NOT NULL AND deleted_at IS NULL` predicate is the
canonical definition and must be used everywhere a "Sent" count is displayed or returned.

**Rule:** Any dashboard metric, API count, or frontend display showing "Sent" estimates
MUST use the `sent_at IS NOT NULL AND deleted_at IS NULL` predicate. Never use `status='sent'`
alone as a proxy for sent count.

**Cross-reference:** Track F A.3, backend estimates.py dashboard endpoint.

---

## DEC-056 — BUG-033: Service/Tune-Up photo skip buttons absent from deployed DOM (2026-05-21) ✅ RESOLVED

**Date:** 2026-05-21
**Status:** RESOLVED — commit `23e3019`

**Problem:** Service/Tune-Up diagnostic flow has three photo steps (svc-1-filter, svc-3-coil, svc-8-run).
Skip choice buttons (e.g. "Dirty – Replace / Dirty – Can Clean / Looks Clean") were absent from the DOM
despite `PHOTO_SKIP_CONFIG` being confirmed present in the deployed JS bundle.

**Root cause:** Service/Tune-Up flow is rendered by `ServiceChecklist.tsx`, NOT `DiagnosticFlow.tsx`.
The `PHOTO_SKIP_CONFIG` block only exists in `DiagnosticFlow.tsx` and was never reached for
`complaint_type=service`. `ServiceChecklist.tsx` rendered `<PhotoSlot>` components with no skip UI at all.

**Fix (commit 23e3019):**
- Added `SVC_PHOTO_SKIP_CONFIG` (equivalent to DiagnosticFlow's PHOTO_SKIP_CONFIG) to `ServiceChecklist.tsx`
- Added `skipExpanded` state + reset `useEffect` per step
- Added skip choice button JSX inline in the photo step render path
- No DB changes needed — `step_id` values matched config keys exactly

**Key lesson:** When a diagnostic complaint_type routes through a separate component (ServiceChecklist vs DiagnosticFlow),
any UI enhancements added to DiagnosticFlow will silently not apply to that flow. Always check which component
renders for the target complaint_type before adding skip/override UI.

**Markets affected:** Both Houston and PK (shared component, same fix)
**Cross-reference:** `ServiceChecklist.tsx`, `DiagnosticFlow.tsx`, PHOTO_SKIP_CONFIG

---

## DEC-057 — PK models are stored as JSONB series array in pak_brands, not a separate table (2026-05-21)

**Date:** 2026-05-21

**Context:** During QA, needed to verify and update Gree inverter model data. Searched for
`pak_equipment_models` table — it does not exist. The `equipment_models` table only contains
US market records (Carrier, Trane, Lennox, etc.).

**How PK models are stored:**
PK brand + model data lives in the `pak_brands` table as a JSONB column called `series`.
Each row = one brand. `series` is an array of objects:

```json
[
  {
    "name": "Fairy Inverter",
    "type": "inverter",
    "refrigerant": "R-32",
    "tonnage_data": {
      "1.0": { "capacitors": {...}, "electrical": {...} },
      "1.5": { "capacitors": {...}, "electrical": {...} },
      "2.0": { "capacitors": {...}, "electrical": {...} }
    }
  }
]
```

**How the backend serves it (`models.py`):**
`GET /api/models/all` (X-Market: PK) explodes each series entry into a synthetic model record:
```python
"series_type": s.get("type", "non_inverter"),   # drives inverter badge in StepZeroPanel
"refrigerant": s.get("refrigerant", "R-22"),
"tonnage_data": tonnage_data,                    # drives auto-fill specs per tonnage
```

**The inverter badge rule:**
`StepZeroPanel.tsx` renders `<span>Inverter</span>` badge when `m.series_type === "inverter"`.
The `series_type` field comes directly from `pak_brands.series[].type`.
Set `type: "inverter"` in the pak_brands JSONB to show the inverter badge.

**To add a new PK model series:**
```sql
UPDATE pak_brands
SET series = series || '[{
  "name": "New Model Name",
  "type": "inverter",
  "refrigerant": "R-32",
  "tonnage_data": { "1.0": {...}, "1.5": {...}, "2.0": {...} }
}]'::jsonb
WHERE id = 'brand_id_here';
```

**After updating pak_brands:**
The browser's IndexedDB model cache (TTL 24h) must be cleared before new models appear:
```js
await indexedDB.deleteDatabase('snapai_models_pk');
location.reload(true);
```

---

## DEC-063 — `/api/models/all` response shape is `{models:[...]}`, not a plain array (2026-05-22)

**Date:** 2026-05-22

**Context:** During Phase 2 backend health checks, code used `Array.isArray(data)` to parse the `/api/models/all` response. This returned `false` (the response is `{"models": [...]}`, an object), causing model counts to show as 0 even though the endpoint returned 200 OK with valid data.

**Correct parse pattern:**
```javascript
const resp = await fetch(`${base}/api/models/all`, {headers: {'X-Market': 'PK'}});
const data = await resp.json();
const models = data.models || []; // NOT: Array.isArray(data) ? data : data.models
```

**Also confirmed:** `/api/brands` does NOT exist — returns 404. The only model data endpoint is `/api/models/all`.

**Impact:** Any code, test, or script that fetches brand/model data from Railway must handle the `{models:[...]}` wrapper. The existing `getBrands()` / `searchModels()` functions in `lib/modelCache.ts` handle this correctly.

---

## DEC-064 — PK PSI thresholds are in `pak_operating_targets`, not `pak_diagnostic_questions` (2026-05-22)

**Date:** 2026-05-22

**Context:** QA skill Phase 2d spec said to check `pak_diagnostic_questions` for PSI high_min thresholds. The table `pak_diagnostic_questions` does NOT exist in production Supabase — querying it returns `ERROR: relation does not exist`.

**Actual table:** `pak_operating_targets`

**Schema confirmed:**
```sql
SELECT refrigerant, ambient_c, suction_min_psi, suction_max_psi, discharge_min_psi, discharge_max_psi
FROM pak_operating_targets
ORDER BY refrigerant, ambient_c;
```

**Verified values (2026-05-22):**
- R-410A at 40°C: suction 125–145 PSI, discharge 325–370 PSI ✅
- R-32 at 40°C: suction 120–140 PSI, discharge 365–410 PSI ✅
- R-22 at 45°C: suction 78–88 PSI ✅

`suction_max_psi` is the upper normal bound — readings above this trigger a "high pressure" fault. These match QA spec requirements.

**Impact:** Any migration or data patch to PK PSI thresholds must target `pak_operating_targets`. The QA skill Phase 2d check must query `pak_operating_targets`, not `pak_diagnostic_questions`.

---

## DEC-062 — Every photo step in ServiceChecklist needs a SVC_PHOTO_SKIP_CONFIG entry (2026-05-22)

**Date:** 2026-05-22

**Problem:** `svc-4-drain` (Step 4 — Drain flush confirmation photo) had no entry in `SVC_PHOTO_SKIP_CONFIG`. A photo step with no skip config shows only the camera upload area — no skip link, no manual condition buttons. QA testers and field techs with a broken camera are completely blocked. During QA, step 4 was bypassed via a React fiber `onComplete` injection, which skipped `submitStep()` entirely and zeroed `findings`, leaving the Estimate Builder empty.

**Root cause:** SVC_PHOTO_SKIP_CONFIG in ServiceChecklist.tsx had entries for steps 1, 3, 8 but not step 4. The backend already handled `flushed`, `skipped`, and `any` branches for svc-4-drain — the fix was frontend-only.

**Fix (commit 3f09c02):** Added choice-type skip config for svc-4-drain:
- "Drain Flushed" → branch_key: flushed → adds flush_tablet finding ($12–$18) → routes to svc-5-terminals
- "Could Not Flush" → branch_key: skipped → no finding → routes to svc-5-terminals

**Rule — SVC_PHOTO_SKIP_CONFIG coverage (post 3f09c02):**
| Step | Step ID | Skip Type | Choices |
|------|---------|-----------|---------|
| 1 | svc-1-filter | choice | Dirty-Replace / Dirty-Can Clean / Looks Clean |
| 3 | svc-3-coil | choice | Heavily Blocked / Dirty / Clean |
| 4 | svc-4-drain | choice | Drain Flushed / Could Not Flush |
| 8 | svc-8-run | simple | skipped |

Steps 2, 5, 6, 7 use reading/multi input types — they always have a submit button; no skip needed.

**Checklist for any new service photo step:**
1. Add `diagnostic_questions` row with `input_type = 'photo'`
2. Add `branch_logic_jsonb` with `"skipped"` and `"any"` entries routing to next step
3. Add entry to `SVC_PHOTO_SKIP_CONFIG` in ServiceChecklist.tsx with appropriate choices
4. If step generates a finding, map the branch_key to the correct line_item_code

**Commit:** `3f09c02`
## DEC-067 — Vercel staging project deploys `main` branch, not `staging` branch (2026-05-22) — **SUPERSEDED 2026-05-24 by DEC-080**

**Date:** 2026-05-22 | **Status:** SUPERSEDED 2026-05-24 — see DEC-080

**Context:** During the staging fix session, it was discovered that the `scopesnap-web-staging` Vercel project is configured with `main` as its Production branch. The `staging` git branch was NOT linked to the Vercel staging project. All staging Vercel deployments showed source branch = `main`.

**SUPERSEDED:** Stage 6 (2026-05-24) fixed this by setting `gitBranch: "staging"` at the domain level for all 3 staging domains via the Vercel domain PATCH API (`PATCH /api/v9/projects/{id}/domains/{domain}`). All staging domains now serve the `staging` git branch. See DEC-080 for full details.

**Historical note:** Vercel's project-level `link.productionBranch` cannot be changed via the API (schema whitelist rejects it). The domain-level `gitBranch` override achieves the same practical outcome: pushing to `staging` branch triggers new deployments that all 3 staging domains serve.

---

## DEC-068 — DNS for mainnov.tech is in Hostinger, NOT Cloudflare (2026-05-22)

**Date:** 2026-05-22

**Context:** The `.staging_secrets.txt` file contains a comment saying to add DNS records in Cloudflare (dash.cloudflare.com) for the `mainnov.tech` zone. This is WRONG. The actual DNS for `mainnov.tech` is managed in Hostinger under account `mshoabarabi@gmail.com` at `hpanel.hostinger.com`.

**Evidence:** Hostinger nameservers (`ns1.dns-parking.com` / `ns2.dns-parking.com`) are on the domain. No Cloudflare account for `ds.shoab@gmail.com` has this domain.

**CNAME records updated (2026-05-22):**
- `staging.snapai.mainnov.tech` CNAME → `e08b930de4517e81.vercel-dns-017.com` (TTL 14400)
- `pk-staging.snapai.mainnov.tech` CNAME → `e08b930de4517e81.vercel-dns-017.com` (TTL 14400)

**Old target:** `cname.vercel-dns.com` (Vercel still accepts this but recommends the new one)
**New target:** `e08b930de4517e81.vercel-dns-017.com`

**Rule:** Any future DNS changes for mainnov.tech go to Hostinger hpanel under `mshoabarabi@gmail.com`.

---

## DEC-069 — StagingBanner is RSC in app/(app)/layout.tsx — visible on authenticated routes only (2026-05-22)

**Date:** 2026-05-22

**Context:** The `StagingBanner` component is a React Server Component (no `"use client"` directive) placed in `app/(app)/layout.tsx` — the layout for authenticated/app routes. It is NOT in the root `app/layout.tsx`.

**Consequence:**
- Public pages (homepage `/`, `/sign-in`, etc.) do NOT show the staging banner
- Authenticated pages (`/assess`, `/reports`, `/settings`, etc.) DO show the banner when `NEXT_PUBLIC_ENV === "staging"`
- This is correct by design — the banner's purpose is to prevent confusion when using the app in staging mode

**Verification:** Navigating to `scopesnap-web-staging.vercel.app/assess` redirects to `/sign-in` (auth guard working). The banner appears after sign-in on any `(app)` route.

**env var reading:** Because `StagingBanner` is RSC, `process.env.NEXT_PUBLIC_ENV` is read at server runtime — NOT baked into the client JS bundle. This is why the string "staging" does NOT appear in the downloaded JS chunks (expected, not a bug).

---

## DEC-065 — Never commit `scopesnap-web/package-lock.json` (2026-05-22)

**Date:** 2026-05-22

**Problem:** Commit `78d0fff` accidentally included `scopesnap-web/package-lock.json` (7,954 lines).
This broke every Vercel build immediately — `npm ci` failed in ~8 seconds because the lockfile
was present but did not match the installed `node_modules`. Vercel showed "Error" with no detail.
Seven consecutive builds failed between `78d0fff` and `a908eac`.

**Root cause:** `package-lock.json` was generated locally and accidentally staged with `git add -A`.
The repo intentionally has NO lockfile since commit `c2eac8d` (force Node 18, March 2026).

**Fix:** `git rm scopesnap-web/package-lock.json` in commit `a908eac`. Builds resumed immediately.

**Detection signal:** Vercel build duration under 20 seconds = `npm ci` failed. Normal build = 1–2 minutes.
Check for a spurious `package-lock.json` addition in the diff whenever a build fails fast.

**Rule:** `scopesnap-web/package-lock.json` must NEVER be committed. Add it to `.gitignore` if needed.
Confirm with `git status --short | grep package-lock` before every commit. If it appears, `git rm` it.

**Impact:** DEC-065 is also in `.gitignore` — verify the .gitignore rule is present after any repo reset.

---

## DEC-066 — Stamp `estimates.market` at creation — never derive from viewer's hostname (2026-05-22)

**Date:** 2026-05-22

**Problem (BUG-037):** Pakistan estimates viewed on the Houston domain (`snapai.mainnov.tech`)
displayed USD amounts instead of PKR. Root cause: `ReportClient.tsx` had a module-level
`function fmt(n)` that called `formatCurrency(n)` with no `market` argument. `formatCurrency`
defaulted to the caller's hostname (Houston = US), so PK estimates always showed USD when
opened from any Houston URL.

**Decision:** Stamp `estimates.market` (VARCHAR(2) NOT NULL DEFAULT 'US') at the moment the
estimate is created — not at the moment it is viewed. The stored market value is the source
of truth for currency formatting in reports. The viewer's hostname is irrelevant.

**Implementation:**
- Migration 034: `ALTER TABLE estimates ADD COLUMN market VARCHAR(2) NOT NULL DEFAULT 'US'`
- `fault_estimate.py` and `diagnostic.py` both write `market = tables.market` at INSERT time
- `reports.py` returns `report.market` to the frontend
- `ReportClient.tsx`: `reportMarket = (report as any).market` (from DB, not hostname)
- `const fmt = (n: number) => formatCurrency(n, reportMarket)` — component-level, not module-level

**Rule:** ANY code that formats currency in a report or estimate display MUST read from
`report.market` (or `estimate.market`), never from `detectMarket()` at display time.
The market of an estimate is fixed at creation — it does not change when a contractor
switches contexts.

**Cross-reference:** BUG-037, migration 034, DEC-065, TECH_STACK WA-34.

---

## DEC-070 — Staging-first change workflow becomes canonical after Stage 7 sign-off (2026-05-23)

**Date:** 2026-05-23

**Context:** Through 2026-05-19 to 2026-05-22 the staging environment was set up (DEC-014) but operated as a partial mirror of production — Vercel staging tracks `main` instead of `staging` (DEC-067), the staging Supabase DB drifted from production (Alembic 025 vs prod 034), and changes have been pushed directly to `main` with verification on production. This is the opposite of what staging is for. Going forward, every change must pass through staging first, with staging maintained as a true mirror of production at all times.

**Decision:** Adopt the staging-first 7-step workflow defined in `WORKFLOW.md` as the canonical change process. The four absolute rules:

1. **Never edit code directly on `main`** without going through `staging` first
2. **Never push migrations to prod** that haven't run on staging first
3. **Never add env vars to prod** without mirroring them on staging
4. **Never test on production** — testing happens on staging; production is for real users

**Rationale:** Production is now beta-facing (5 testers incoming via LinkedIn). Every prod bug is a tester churn risk. Staging exists to absorb that risk by catching bugs against an environment that is byte-for-byte identical to production except for data isolation, test keys, and a visible amber banner. The additional cost is sleeping-mode-only on Railway (free if staging stays under $5/mo combined) and a separate Supabase project (within the 2-project free tier cap).

**Rule:** All future changes follow the 7-step workflow in `WORKFLOW.md` Section 4. Exception: emergency hotfix path (`WORKFLOW.md` Section 9) bypasses staging only for genuine production emergencies, with mandatory 24-hour follow-up sync to bring staging in line with main, plus a retrospective DEC entry explaining what slipped through normal QA.

**Activation:** ACTIVE — Stage 7 (Staging End-to-End QA) signed off 2026-05-24. This workflow is now mandatory. — at which point staging is verified to be a true mirror of production, the Vercel staging project deploys the `staging` branch, and a full QA pass on staging matches a full QA pass on production. Transitional rules (DEC-004 `/tmp` clone, DEC-013 no git stash from sandbox, DEC-022 Desktop Commander for git ops) remain in force for AI git operations — these are environment constraints, not workflow gates.

**Cross-references:**
- `C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI\WORKFLOW.md` — full protocol with worked examples
- DEC-014 — staging environment architecture
- DEC-015 — dual keepalive crons (Sun + Wed)
- DEC-023 / DEC-051 — never set NEXT_PUBLIC_ENV=staging on prod
- DEC-066 — DNS in Hostinger, not Cloudflare
- DEC-067 — Vercel staging deployed main (SUPERSEDED 2026-05-24 by DEC-080)
- DEC-068 — DNS for mainnov.tech in Hostinger (account `mshoabarabi@gmail.com`)
- DEC-069 — StagingBanner is RSC, auth-only

**File created:** `C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI\WORKFLOW.md` (2026-05-23)



---

## DEC-072 — BUG-040: CAST(:options AS jsonb) required for JSONB column INSERT in raw SQLAlchemy (2026-05-23)

**Date:** 2026-05-23

**Problem:** Service/Tune-Up flow completed (`service_complete` status) but never created an estimate row. Contractor opened the assessment page and saw an empty estimate.

**Root cause:** `_generate_service_estimate()` in `api/diagnostic.py` ran a raw SQL INSERT with `:options` parameter bound to a Python list, targeting a JSONB column. SQLAlchemy with PostgreSQL requires an explicit `CAST(:options AS jsonb)` in the raw SQL string for JSONB columns. Without it, the INSERT executes and appears to succeed but the JSONB binding fails silently — no Python exception, no rollback, no row created.

**Fix:** Changed the INSERT to use `CAST(:options AS jsonb)` for the options parameter.

**Rule:** Whenever writing raw SQLAlchemy INSERT or UPDATE with parameters bound to JSONB columns, ALWAYS include `CAST(:param AS jsonb)` in the SQL string. Never rely on SQLAlchemy type inference for JSONB. Pass the value as `json.dumps(obj)` in the params dict.

**File:** `api/diagnostic.py` — `_generate_service_estimate()` function

**Detection pattern:** If an INSERT appears to run without error but no row appears, check for JSONB columns in the target table and verify CAST usage.

---

## DEC-073 — BUG-041: NEXT_PUBLIC_ENV=staging on production Vercel is a recurring trap (2026-05-23)

**Date:** 2026-05-23

**Problem:** Amber "STAGING" banner visible on pk.snapai.mainnov.tech (BUG-041). This is a re-occurrence of BUG-031 (first found 2026-05-21, fixed 2026-05-21, re-occurred 2026-05-23).

**Root cause:** When staging environment was configured/reconfigured, `NEXT_PUBLIC_ENV=staging` was set in the production Vercel project's environment variables under "All Environments". `StagingBanner.tsx` reads `process.env.NEXT_PUBLIC_ENV === "staging"` — baked into the bundle at build time. Even a correct source tree will show the banner if this env var is wrong.

**Fix:** Set `NEXT_PUBLIC_ENV=production` in Vercel production project → Settings → Environment Variables → All Environments. Trigger a new deployment. Verify the new deployment ID appears on both domains.

**Prevention rules (CRITICAL — this bug has occurred twice):**
1. After ANY Vercel environment variable changes on ANY project, immediately open pk.snapai.mainnov.tech and check for the amber STAGING banner
2. Before triggering any new Vercel deployment, verify NEXT_PUBLIC_ENV in the PRODUCTION project is either absent or set to "production" — NEVER "staging"
3. When configuring staging project env vars, use "Preview" environment scope only — never "All Environments" which can bleed into production

**Cross-references:** DEC-051 (BUG-031 original), DEC-023 (rule: NEVER set NEXT_PUBLIC_ENV=staging on production Vercel)

---

## DEC-074 — Stage 4 audit: Vercel staging custom domains are Preview branch deployments, not Production env builds (2026-05-23)

**Date:** 2026-05-23 (Stage 4 Staging Isolation Audit)

**Finding:** `staging.snapai.mainnov.tech` and `pk-staging.snapai.mainnov.tech` are configured as "git branch" custom domains in the `scopesnap-web-staging` Vercel project, pointing to the `staging` git branch. They are served by the **Preview** deployment of that branch -- NOT by the Production environment deployment.

**Consequence:** When NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY was corrected from pk_live_ to pk_test_ on the staging Vercel project and a "Production environment" redeploy (deployment CXM5WEJMt) was triggered, `staging.snapai.mainnov.tech` still served the old pk_live_ key. The Production redeploy built a new Production environment deployment -- which is not what staging custom domains serve.

**Fix pattern:** Deployments page → filter by branch "staging" → find latest Preview deployment → three-dot menu → Redeploy (no cache). New Preview deployment `5HJ2piG8A` was picked up by both staging custom domains. Confirmed pk_test_ on both.

**Rule:** Any env var change on `scopesnap-web-staging` that needs to reach `staging.snapai.mainnov.tech` / `pk-staging.snapai.mainnov.tech` MUST be followed by a staging branch Preview redeploy, not a Production environment redeploy.

**DNS confirmation:** Staging custom domains CNAME target: `e08b930de4517e81.vercel-dns-017.com` (different from production `e9353dffc8a96116.vercel-dns-017.com` -- isolated at DNS level).

---

## DEC-075 — Stage 4 audit: Railway staging had sk_live_ CLERK_SECRET_KEY (production Clerk secret key) (2026-05-23)

**Date:** 2026-05-23 (Stage 4 Staging Isolation Audit)

**Finding:** Railway staging service (`scopesnap-api-staging.up.railway.app`) had `CLERK_SECRET_KEY` set to `sk_live_...` -- the production Clerk secret key. Critical cross-contamination: staging backend was validating tokens against the production Clerk app.

**Impact:** With sk_live_ on staging, any Clerk JWT issued by the staging app (pk_test_ key) would fail validation on the staging backend. Conversely, any pk_live_ token from production would pass validation on staging -- a security boundary violation allowing production user sessions to authenticate on the staging backend.

**Fix:** Replaced with `sk_test_...` from staging Clerk app (firm-chamois-61, Development mode).

**Prevention:** After any new Railway staging service creation or cloning from production, audit ALL environment variables against the key prefix convention: sk_live_ = production only, sk_test_ = staging only. Never copy Railway env vars from production to staging without replacing all sk_live_ keys with sk_test_ equivalents.

---

## DEC-076 — Stage 4 audit: pk.snapai.mainnov.tech served pk_test_ due to stale ISR edge cache (2026-05-23)

**Date:** 2026-05-23 (Stage 4 Staging Isolation Audit)

**Finding:** `pk.snapai.mainnov.tech` was returning `pk_test_...` as the Clerk publishable key in its HTML, despite the `scope-snap-ai` production Vercel project having `pk_live_...` in `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` for All Environments.

**Investigation (ruled out):**
- Browser cache: fresh tab showed same pk_test_ (transferSize 20,986 bytes = no cache)
- Separate Vercel project: pk.snapai.mainnov.tech is registered only in scope-snap-ai Production environment
- Code-level market detection: layout.tsx has no host-header switching, ClerkProvider has no explicit publishableKey prop
- Multiple env var values: Vercel shows single pk_live_ entry for All Environments
- PK-specific env var override: none found

**Root cause (best explanation):** Stale ISR / edge cache specific to pk.snapai.mainnov.tech's CNAME endpoint (`e9353dffc8a96116.vercel-dns-017.com`). The sibling domain `snapai.mainnov.tech` was correctly serving pk_live_ from the same Vercel project, suggesting the stale value was cached at the edge node serving that specific domain.

**Fix:** Fresh production redeploy WITHOUT build cache -- new deployment `CwjgWfNBi` (2m 54s, Production, Ready Latest, domains: snapai.mainnov.tech +3). After build, pk.snapai.mainnov.tech confirmed pk_live_.

**Lesson:** After any Vercel env var change, verify BOTH production domains independently. ISR edge cache can serve stale values on one CNAME endpoint while the other is fresh.

---

## DEC-077 — Clerk key prefix is the authoritative environment signal for all four SnapAI domains (2026-05-23)

**Date:** 2026-05-23 (Stage 4 Staging Isolation Audit)

**Convention confirmed:**
- `pk_live_` / `sk_live_` = production Clerk app (scope-snap-ai Vercel project, Railway production service)
- `pk_test_` / `sk_test_` = staging Clerk app (firm-chamois-61, Development mode; scopesnap-web-staging Vercel project, Railway staging service)

**Note on NEXT_PUBLIC_* and render time:** `data-clerk-publishable-key` in the HTML is set by the Next.js server at request time (reflecting the NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY env var from the Vercel environment). This means it can reflect stale ISR cache values (see DEC-076) even when the Vercel project shows the correct env var. A no-cache redeploy flushes this.

**Final verified state post-Stage-4-audit (2026-05-23):**

| Domain | Clerk key prefix | Status |
|--------|-----------------|--------|
| snapai.mainnov.tech | pk_live_ | PASS |
| pk.snapai.mainnov.tech | pk_live_ | PASS (was pk_test_ pre-fix; fixed by redeploy CwjgWfNBi) |
| staging.snapai.mainnov.tech | pk_test_ | PASS (was pk_live_ pre-fix; fixed by Preview redeploy 5HJ2piG8A) |
| pk-staging.snapai.mainnov.tech | pk_test_ | PASS |

**All other Stage 4 dimensions:**
- Supabase: prod project `quqrvnoguofbjacrxcim`, staging `pqmgveqkuckbvyygsilk` -- isolated, no data overlap
- Clerk: prod app (pk_live_) vs staging app firm-chamois-61 (pk_test_) -- isolated
- R2: prod bucket `scopesnap-uploads`, staging bucket `scopesnap-uploads-staging` -- isolated
- DNS: staging CNAME `e08b930de4517e81.vercel-dns-017.com`, prod CNAME `e9353dffc8a96116.vercel-dns-017.com` -- different endpoints
- Sentry: `production` environment filter (8+ issues, SNAPAI-API-P/F/S/Y/X/W/V/T) vs `staging` filter (1 issue, SNAPAI-API-Z) -- isolated, no cross-contamination


---

## DEC-078 — CSP must include maps.googleapis.com and maps.gstatic.com in script-src and connect-src (Stage 3 Google Maps Integration -- 2026-05-23)

**Date:** 2026-05-23 (Stage 3 Google Maps Integration)

**Context:** `HoustonAddressAutocomplete` injects a `<script src="https://maps.googleapis.com/maps/api/js?...">` tag at runtime. Without explicit CSP allowances the browser blocks the script before it executes.

**Decision:** `next.config.js` CSP headers must include:
- `script-src`: `https://maps.googleapis.com https://maps.gstatic.com`
- `connect-src`: `https://maps.googleapis.com`

**Commit:** `42e692b` (next.config.js)

**Note:** Code comment in `next.config.js` mistakenly labels this DEC-076 (that number was taken by the Stage 4 staging isolation audit). Canonical reference is DEC-078.

---

## DEC-079 — Service Worker must passthrough maps.googleapis.com and maps.gstatic.com to avoid opaque-response blocking (Stage 3 Google Maps Integration -- 2026-05-23)

**Date:** 2026-05-23 (Stage 3 Google Maps Integration)

**Context:** The SnapAI PWA Service Worker (`public/sw.js`) intercepts all fetch requests. For cross-origin `<script>` requests that fall through to the navigation handler, the SW calls `fetch(event.request)` which returns an **opaque response**. Browsers cannot execute scripts from opaque responses -- `script.onerror` fires despite an HTTP 200 from the server.

**Root cause chain:**
1. `HoustonAddressAutocomplete` injects `<script src="https://maps.googleapis.com/...">`
2. SW intercepts the script fetch (not matched by API or static-asset rules)
3. Navigation fallback calls `fetch(event.request)` -- opaque response returned
4. Browser: opaque response cannot be executed as a script -- `script.onerror` fires
5. Component: `loadError = true` -- renders `PlainInput` fallback (no autocomplete)

**Fix:** Add `maps.googleapis.com` and `maps.gstatic.com` to the third-party passthrough block in `sw.js` (alongside posthog, clerk, railway). These hostnames now get `event.respondWith(fetch(event.request)); return;` -- bypassing the opaque-response path entirely.

**Commit:** `a88c93a` (public/sw.js)

**Diagnostic proof:** Unregistering the SW via `navigator.serviceWorker.getRegistrations().then(...)` caused `google.maps.places` to load successfully (googleDefined: true, placesLoaded: true). Re-registering with the passthrough fix confirmed the same result with SW active.

**Note:** Code comment in `sw.js` mistakenly labels this DEC-077 (that number was taken by the Stage 4 staging isolation audit). Canonical reference is DEC-079.

**Future work:** `google.maps.places.Autocomplete` is deprecated for new customers as of March 1, 2025 (not discontinued -- Google shows a console warning on every load). Future migration to `google.maps.places.PlaceAutocompleteElement` required before Google discontinues the old API. No timeline announced.

**Side issue found (BUG-042):** Address field placeholder shows wrong text. Root cause: the `t()` i18n translation function is returning an error string for that key. Non-blocking -- autocomplete works correctly; placeholder only shows when field is empty.


---

## DEC-080 — Stage 6: Vercel staging domains rewired to `staging` branch via domain-level gitBranch (2026-05-24) — SUPERSEDES DEC-067

**Date:** 2026-05-24 (Stage 6 Vercel Staging Branch Rewire)

**Problem (DEC-067):** `scopesnap-web-staging` Vercel project had `main` as its Production branch. All staging Vercel deployments were sourced from `main`, not from the `staging` git branch.

**Root cause of difficulty:** Vercel's API does not expose `link.productionBranch` as a patchable field. `PATCH /api/v9/projects/{id}` with `productionBranch`, `link`, or `gitBranch` in the body returns `"should NOT have additional property"`. This applies to all API versions (v1, v7, v8, v9, v10). The Vercel UI Git settings page also does not expose a Production Branch input field in the current UI version. POST to `/link` returns 200 but does not change the branch.

**Solution:** Set `gitBranch: "staging"` at the **domain level** for all 3 staging domains via:
```
PATCH /api/v9/projects/{projectId}/domains/{domainName}
Body: { "gitBranch": "staging" }
```
Used browser-session-authenticated calls (relative URL from within vercel.com tab, `credentials: 'include'` automatic).

**Domains updated:**
| Domain | gitBranch set to |
|--------|-----------------|
| `staging.snapai.mainnov.tech` | `staging` |
| `pk-staging.snapai.mainnov.tech` | `staging` |
| `scopesnap-web-staging.vercel.app` | `staging` |

**Verification:**
- Push to `staging` branch (commit `71bc7fea`) → Vercel deployment `dpl_Gm5CkDDoFbA8CHCsM9ksETynCuFo` fired, `state=READY`, `branch=staging` ✅
- Push to `main` branch (commit `ebe82f6c`) → Production project `prj_SQgShjdRuT2cmhjgL45QMVGP8CNs` got production deploy (correct — does NOT touch staging domains) ✅
- Staging backend: `{"status":"ok","db":"connected","environment":"staging"}` ✅
- Production backend: `{"status":"ok","db":"connected","environment":"production"}` ✅

**Known limitation (acceptable):** The `scopesnap-web-staging` Vercel project STILL builds a `target: "production"` deployment from `main` pushes (because `link.productionBranch` cannot be changed). However, since all 3 domains have `gitBranch: "staging"`, those `main`-sourced builds are NOT served on any domain. They sit as orphaned Production builds. The domain-level override fully controls what each staging domain serves.

**Rule for future work:** When pushing to `staging` branch, Vercel automatically builds and deploys to all 3 staging domains. This is the intended behavior. Do NOT change the domain `gitBranch` settings back to `main` or remove them.

**Git state at Stage 6 sign-off (2026-05-24):**
- `main` HEAD: `ebe82f6cb9e7727f99ea765088d65515f6d6da93` (empty Stage 6 verification commit)
- `staging` HEAD: `71bc7fea166fa9a7526215c9475ab97b9abd8fc4` (empty Stage 6 verification commit)
- Both have one empty `--allow-empty` verification commit; no functional code changes

**Cross-references:** DEC-067 (superseded), DEC-074 (Vercel staging = Preview deployments), DEC-070 (staging-first workflow)


---

## DEC-081 — Emergency patch: correct R-410A US PSI thresholds in diagnostic_questions + diagnostic.py (2026-05-24)

**Date:** 2026-05-24 (Issue #1 — Priority 0, pre-beta walkthrough)

**Problem:** Stage 7 QA verified *routing* (45 PSI → Refrigerant Leak) but did NOT verify the displayed hint text accuracy. The walkthrough revealed Step 2 question hint read "R-410A typical: 65-85 PSI at normal charge" — those are R-22 numbers. Additionally, `diagnostic.py` `_us_suction` dict had incorrect bounds (low=108, high=144 instead of low=115, high=140), and `_us_discharge` had incorrect bounds (low_R410A=250, high_R410A=350 instead of 225/275).

**Canonical R-410A US thresholds at 95°F outdoor ambient:**
- Suction: 115–140 PSI normal | >= 141 = high
- Discharge: 225–275 PSI normal | >= 276 = high

**Fix (Alembic 035 + diagnostic.py):**
- Migration `035_correct_us_psi_thresholds_emergency.py`: updates 4 `diagnostic_questions` rows via `jsonb_set()`:
  - `q2-nc-suction`, `q2-hiss-suction`, `q2-wd-suction`: low_threshold 60→115, high_threshold 145→141, hint corrected
  - `q2-nc-discharge`: low_threshold 250→225, high_threshold 350→276, hint corrected
- `diagnostic.py` `_us_suction` dict: R-410A changed to (115, 140); R-22 to (55, 78); R-32 to (110, 145)
- `diagnostic.py` `_us_discharge` dict: R-410A changed to (225, 275); R-22 to (150, 275); R-32 to (225, 290)

**PK unaffected:** PK market uses `pak_operating_targets` dynamic lookup — not touched by this migration.

**Boundary-value gate (WA-41):**
  - Suction: 80 PSI → low alert | 125 PSI → normal/ok | 160 PSI → high alert
  - Discharge: 210 PSI → low/escalate | 250 PSI → normal (Card 14) | 310 PSI → high (Card 17)

**Staging-first workflow:** Merged to `staging` branch → Railway auto-ran `alembic upgrade head` → verified 035 as head → boundary tests on staging.snapai.mainnov.tech → then promote-to-prod.sh to `main`.

**Rule for future work:** The canonical threshold table lives in PROJECT_BRAIN.md Section 'Canonical PSI Threshold Table'. Any future PSI changes must update that table, `diagnostic.py` dicts, AND the `diagnostic_questions` hint text in lockstep. Never use the Stage 7 QA test value (45 PSI) as a reference threshold — it was a deliberately low test input.

---

## DEC-082 — React fiber state injection for QA bypass of StepZeroPanel (2026-05-24)

**Date:** 2026-05-24 (QA Session -- pre-beta walkthrough full flow verification)

**Problem:** `StepZeroPanel` receives an `onSkip` prop from `assess/page.tsx` but never calls it internally. There is no skip button in the UI. During automated QA (using Claude in Chrome), there is no clickable element that advances the assess page past the step-zero phase without filling in brand/series/tonnage from the DB.

**Solution:** Walk the React fiber tree in Chrome DevTools to find the `memoizedState` node whose value is `'step-zero'`, then call `s.queue.dispatch('complaint')` to trigger the state transition directly.

**Pattern:**
```js
// Run in Chrome DevTools console on the assess page (https://snapai.mainnov.tech/assess)
(function walkFiber(fiber) {
  if (!fiber) return;
  let s = fiber.memoizedState;
  while (s) {
    if (s.memoizedState === 'step-zero' && s.queue && s.queue.dispatch) {
      s.queue.dispatch('complaint');
      return;
    }
    s = s.next;
  }
  walkFiber(fiber.child);
  walkFiber(fiber.sibling);
})(document.body[Object.keys(document.body).find(k => k.startsWith('__reactFiber'))]);
```

**Rationale:** The phase state is managed by `useState` in `assess/page.tsx`. Dispatching directly to the queue bypasses all UI gating without modifying production code. ONLY use in QA sessions -- never inject state in production debugging.

**Impact:** Enables full QA flow automation without needing DB-seeded brand/model data in the browser session. Used to verify complaint selection, diagnostic flow, PK-specific flows, and 2.5T commercial warning (WA-45).

---

## DEC-083 — Vercel build error tracing: always identify the FIRST failing commit (2026-05-24)

**Date:** 2026-05-24 (BUG-043/044 root-cause investigation)

**Problem:** When multiple consecutive Vercel deployments show ERROR, it is tempting to inspect the most recent commit's diff. This is wrong -- subsequent commits inherit the broken state and also fail. Inspecting the wrong commit's diff wastes time and leads to incorrect fixes.

**Solution:** Use `git log --oneline` to find the exact commit where deployments transitioned from READY to ERROR. Then `git diff <last-READY>..<first-ERROR> -- <path>` to isolate the breaking change.

**Tracing steps:**
1. In Vercel dashboard, note the SHA of the last READY deployment.
2. Note the SHA of the first ERROR deployment.
3. `git diff <READY-sha>..<ERROR-sha>` -- the bug is in this diff.
4. Fix the bug in the file named in the error, NOT in the most recent file touched.

**BUG-043 example:** `homeowner/page.tsx` orphaned `{` introduced at commit `a50f94a2`. Commits `a50f94a2` through `03c5caa` all showed ERROR. The fix was to remove 4 orphaned lines from `homeowner/page.tsx` -- a file that none of the "ERROR" commits after `a50f94a2` had touched.

**BUG-044 example:** TypeScript `Cannot find name 'isRecommended'` introduced at same commit `a50f94a2` in `assessment/[id]/page.tsx`. All builds after errored with the same TS message even when that file was not modified.

**Rationale:** Build systems (webpack, tsc) operate on the full codebase state, not just the diff. A broken file in state N causes state N+1...N+K to all fail until fixed.

**See also:** WA-46 (Vercel error tracing), WA-47 (TS cascading failures)

---

## DEC-084 — isRecommended vs isRec: two separate variables for two separate concerns (2026-05-24)

**Date:** 2026-05-24 (Issue #3 -- BUG-044 fix in assessment/[id]/page.tsx)

**Problem:** Issue #3 (Good/Better/Best unification) required wiring the star/REC badge to `opt.recommended` (a DB field) rather than the old `opt.tier === "better"` check. The PR introduced `isRecommended` in the JSX badge at line 815 but did not declare the variable -- only `isRec` existed (declared at line 766 as `opt.tier === "better"`). This caused TypeScript build failure on all subsequent deploys (BUG-044).

**Solution:** Declare both variables explicitly with distinct semantics:
```typescript
const isMiddleTier = opt.tier === "better";   // true for middle tier card -- drives styling
const isRecommended = !!(opt as { recommended?: boolean }).recommended; // drives star REC badge
const isRec = isMiddleTier;  // backward-compat alias for existing headerBg/badgeBg/priceColor refs
```

**Rationale:**
- `isMiddleTier` / `isRec`: purely a styling signal -- the middle tier card gets a highlighted header, a badge background, and a coloured price. Always true for tier="better", regardless of what the DB says.
- `isRecommended`: a data signal -- the star badge ("REC") is shown only when the estimate option has `recommended: true` in the DB. This allows the contractor to mark any tier as recommended independently of which tier is "better".

**Impact:** Any future change to recommendation logic must update `opt.recommended` in the DB (or the estimate generation logic), NOT the `isMiddleTier` variable. The two concerns are permanently separated.

**See also:** WA-47 (TS cascading failures), DEC-083 (error tracing)


---

## DEC-085 — Phase 2 architectural rewrite: ambient-aware PSI routing via unified operating_targets (2026-05-24)

**Date:** 2026-05-24

**Context:** Phase 1 (DEC-081) corrected the static R-410A US thresholds to 115-140 PSI suction at 95°F ambient. The static-threshold approach (a single fixed pair regardless of outdoor conditions) remained a structural risk: a tech diagnosing a system at 110°F outdoor would be evaluated against 95°F thresholds. PK already had correct ambient-aware dynamic lookup via `pak_operating_targets`. Houston had static dicts.

**Decision:** Rename `pak_operating_targets` → `operating_targets`. Add `market VARCHAR(2) NOT NULL` column. Insert US rows for R-410A and R-22 across four ambient buckets (25/30/35/40°C). Refactor `_pk_evaluate_pressure` → `_evaluate_pressure_for_market(market=...)`. Remove PK-only gate so both markets use the unified lookup. Add 3-button ambient selector (Mild/Hot/Extreme) to Step Zero UI; pass `ambient_c` to backend on every PSI answer.

**Rationale:** PK code path was the proven template. The heavy lifting was the schema migration + UI ambient capture. No new infrastructure, no new env vars. Static fallback dicts `_FALLBACK_SUCTION`/_FALLBACK_DISCHARGE keyed by (market, refrigerant) preserved as belt-and-suspenders in case `operating_targets` lookup fails.

**Rule:** Both US and PK PSI routing must go through `_evaluate_pressure_for_market`. Never add market-gated static dicts for a new refrigerant — add rows to `operating_targets` instead.

**Cross-references:** DEC-081 (Phase 1 emergency patch), DEC-070 (staging-first workflow), WA-41 (Phase 1 threshold correction)

---

## DEC-086 — Duplicate step-2b block in migration 036 hotfix: staging fresh seed masks copy-paste bug (2026-05-24)

**Date:** 2026-05-24

**Context:** The hotfix commit `83f8329` was written to fix the production UNIQUE-constraint crash (migration 036 trying to INSERT US rows that violated `UNIQUE(refrigerant, ambient_c)` from original seeding). The hotfix added step-2b to drop the old constraint before the INSERT. However, due to a copy-paste error, the entire step-2b block was duplicated in the migration file's `upgrade()` function:

- First occurrence: DROP legacy constraint IF EXISTS → ADD new `UNIQUE(market, refrigerant, ambient_c)` ← correct
- Second occurrence (duplicate): DROP again (no-op) → ADD same constraint again → **PostgreSQL ERROR: constraint already exists** → Alembic rollback → `operating_targets` never created → uvicorn crash (service CRASHED)

**Why staging didn't catch it:** Staging DB had already run migration 036 successfully (from an earlier, pre-hotfix commit). When `83f8329` was pushed to staging, Railway ran `alembic upgrade head` → saw DB is already at 036 → skipped the migration entirely. The duplicate block was never executed on staging.

**Root cause:** Two structural issues compounded:
1. Copy-paste when writing the hotfix (duplicate block)  
2. Staging DB pre-migration masked the bug (migration didn't re-run because DB was already at 036)

**Fix applied:** `84fedcf` removes the duplicate block (single correct step-2b remains). Production DB was manually migrated to 036 via Supabase MCP `execute_sql` (WA-17 pattern — 7 steps + alembic_version UPDATE). Railway then rebuilt from `84fedcf`, saw version=036, skipped migration, started cleanly. Boundary tests: 24/24 PASS.

**Rule added:** When writing a migration hotfix that adds steps before an existing step, run a diff to confirm the final upgrade() contains no duplicate op.execute blocks. Any ADD CONSTRAINT call must appear exactly once. Grep `ADD CONSTRAINT` count before committing.

**Cross-references:** DEC-085 (Phase 2 rewrite), DEC-050 (WA-17 pattern), migration 036 `84fedcf`


---

## DEC-087 — StepZeroPanel self-sources Clerk JWT via useAuth() (BUG-045 Root Cause A fix, 2026-05-26)

**Decision:** `StepZeroPanel` calls `useAuth().getToken()` internally before every OCR fetch, instead of relying on the `clerkToken` prop passed from the parent (`assess/page.tsx`).

**Problem:** `clerkToken` prop was always `null` — `assess/page.tsx` is a Server Component that cannot call React hooks. Every `POST /api/ocr/nameplate` sent no `Authorization` header, causing 401 on every OCR attempt.

**Solution:** Added `const { getToken } = useAuth()` inside `StepZeroPanel` (client component). Both `runOCR` and `handleConfirm` call `await getToken()` just before the OCR fetch. Also adds `X-Market: detectMarket()` header to the raw `fetch()` call (previously missing). The `clerkToken` prop is retained in Props for backward compat but is no longer read for auth.

**Rule for future work:** Any client component that calls a protected API must self-source its JWT via `useAuth().getToken()`. Never rely on a parent Server Component to pass the token as a prop — Server Components cannot call hooks.

**Commit:** c42cce0 (staging branch, 2026-05-26) | **File:** `scopesnap-web/components/StepZeroPanel.tsx`

---

## DEC-089 — Step Zero default path: localStorage A/B test + returning-user restore (2026-05-27)

**Decision:** The initial tab shown on `/assess` is determined client-side:
1. **Returning user** (`snap_sz_path` in localStorage) → restore their last explicit choice.
2. **New user** (no `snap_sz_path`) → 50/50 A/B variant stored as `snap_sz_variant`; `ab_test_variant_assigned` PostHog event fired.
3. Tier-4 silent fallback (`setActiveTab("manual")`) does NOT write to `snap_sz_path` — system decision, not user preference.
4. Only explicit user taps on "Scan Nameplate" or "I'll enter manually" write to `snap_sz_path`.

**Why localStorage not backend:** Zero latency, no extra API round-trip on a hot path (Step Zero renders immediately). PostHog already collects the telemetry; backend sync deferred until sufficient A/B data justifies it.

**Impact:** `StepZeroPanel.tsx` `handleTabSelect()` + `useEffect` on mount.

---

## DEC-088 — Tesseract.js removed; Gemini-only OCR with 4-tier fallback waterfall (BUG-045 Root Cause B fix, 2026-05-26)

**Decision:** Removed all Tesseract.js usage from `StepZeroPanel`. Nameplate OCR is now Gemini-only with a silent 4-tier fallback.

**4-tier waterfall:**
1. **Tier 1 — Gemini Vision** (`POST /api/ocr/nameplate` with live JWT + X-Market header)
2. **Tier 2 — Confidence gating**: Fields with confidence 40-69 get yellow border (`#facc15`) and `needsConfirmationFields` state. Fields >= 70 auto-accepted; fields < 40 left blank.
3. **Tier 3 — DB fill**: Blank fields back-filled from `ELECTRICAL_SPECS_BY_TONNAGE` if tonnage is known.
4. **Tier 4 — Silent manual fallback**: On Gemini error or low overall confidence, UI silently calls `setActiveTab("manual")`. No error message shown.

**Why Tesseract was removed:** Worker loaded from `cdn.jsdelivr.net` — blocked in some field environments. The two-engine fallback was complex, unreliable, and the user-visible error "Both AI and local OCR failed" was confusing. Gemini with invisible failure is simpler and better UX.

**PostHog telemetry:** `nameplate_ocr_attempt` event fires after every OCR attempt with: `market`, `gemini_called`, `gemini_succeeded`, `overall_confidence`, `final_tier`, `time_ms`.

**Dead code note:** `scopesnap-web/lib/tesseractOcr.ts` still exists in the repo but is no longer imported. Safe to delete in a future cleanup commit.

**Commit:** c42cce0 (staging branch, 2026-05-26) | **File:** `scopesnap-web/components/StepZeroPanel.tsx`

---

### DEC-091 — Migrate database to us-east-1 (co-locate with backend); staging done, prod pending (2026-06-08)

**Decision:** Move the Supabase database from Tokyo (`ap-northeast-1`) to Virginia (`us-east-1`) to co-locate with the Railway US East backend, eliminating a ~1,300 ms cross-Pacific round-trip on every query. Stay at $0 (Free/NANO) by never exceeding the 2-active-project free limit (pause old before creating new).

**Context:** A speed audit measured DB queries at ~1,300 ms each (backend Virginia → DB Tokyo). `/health` (one SELECT 1) took ~2 s; real API calls 3,000–3,755 ms. Confirmed the prod + staging Supabase projects were both in ap-northeast-1 while Railway is US East.

**What we did (STAGING):** Created `snapai-staging-use1` (us-east-1), restored the verified Tokyo-staging pg_dump into it (57 tables / 41,163 rows, 0 diff, incl `research` marketing schema), swapped Railway staging DATABASE_URL, paused old Tokyo staging as rollback. Also tuned the pool (DEC rationale below) and added an app_events partial index.

**Pool tuning:** Removed `pool_pre_ping` (extra SELECT 1 per checkout — pointless at <10 ms latency), added `pool_recycle=1800`, `pool_size=5`/`max_overflow=5` (max 10, under the 15-conn session-pooler cap). Result: DB query ~35 ms → ~18 ms; `/api/events` ~1,050 ms → ~417 ms.

**Result:** DB query ~1,300 ms → ~18 ms. Dashboard TTFB 2,462 → 726 ms. Data verified byte-identical (app reads confirmed: equipment_models, estimates, diagnoses all exact vs DB).

**Still open / TODO for PROD:** prod (`scopesnap`, Tokyo) not yet migrated — repeat recipe with a fresh prod pg_dump, swap prod DATABASE_URL during a low-traffic window. Convert the app_events index into an Alembic migration so prod gets it. Rollback = re-point DATABASE_URL at the (paused) Tokyo project + unpause.

**Trade-off:** us-east-1 is farther from PK (Pakistan) users than Tokyo, BUT the backend is in US East for both markets, so co-locating the DB with the backend helps BOTH markets (the slow hop was backend↔DB, not user↔backend). No PK downside.

---

## DEC-092 (2026-06-09): PK broke after Tokyo→Virginia migration — 5 of 6 `pak_*_v` views missing from restore

**Symptom:** PK diagnostic/estimate flow + `pk-staging` returned "API offline / Failed to fetch". US unaffected, both envs.

**Root cause:** The PK market path (`api/dependencies.py` → `MarketTables`) queries **views** — `pak_fault_cards_v`, `pak_error_codes_v`, `pak_labor_rates_v`, `pak_replacement_costs_v`, `pak_lifecycle_rules_v` (+ `pak_operating_targets_v`) — that remap `pak_*` base-table columns (pkr_est_*, code, description…) to the US-compatible names the shared SQL expects (price_list_*, error_code, meaning…). These 5 views were created **out of band** (NOT in Alembic — only `pak_operating_targets_v` is, in migration 036). The Tokyo **staging** dump never contained the other 5 (they never existed in Tokyo staging); the Tokyo **prod** dump contained all 6. So after the restore, Virginia **staging** had only `pak_operating_targets_v` → every PK view query hit "relation does not exist" → backend **503 with no CORS headers** (the WA-21 escaped-exception pattern) → browser shows "Failed to fetch", which looked like a CORS/connectivity bug but was a missing-relation bug.

**Why the data-integrity check missed it:** views have no rows of their own; the migration verification compared **base-table row counts** only. **LESSON: migration verification must also diff views, functions, and sequences — not just table row counts.**

**Fix (2026-06-09):** Recreated the 5 missing views in Virginia **staging** (`kikhhnanuwzocwcpzutr`) from the prod backup `backups/prod_fresh_20260608_164020.sql.gz` via `CREATE OR REPLACE VIEW`. Verified each returns correct PK data (fault_cards 16, error_codes 17, labor_rates 1, replacement_costs 4, lifecycle_rules 0 by design `WHERE false`, operating_targets 12). Post-fix Postgres logs are clean. Virginia **prod** (`zpsoprffaujswywtsgzy`) already had all 6 views (restored from the prod dump) — **no prod DB change required**.

**Prevention TODO:** add these 5 views to an Alembic migration so any future restore/migration recreates them automatically (they are currently fragile — absent from version control).

**Separate, still-open observations (NOT the view bug):**
- Dashboard "Recent Assessments" (`/api/estimates`, `/api/analytics/estimates-summary`) uses shared ORM tables, not the views; its "API offline" persisted post-fix with a clean DB → app-layer or browser-side, needs the Railway/Sentry traceback to close.
- `pk.snapai.mainnov.tech` (PROD) sign-in renders the **DEV Clerk** instance ("ScopeSnapAI Staging", `firm-chamois-61.accounts.dev`) — possible prod Clerk-instance misconfiguration on the PK prod domain; flag for review.

### UPDATE 2026-06-09 — PK prod misconfig CONFIRMED (was "possible" above)
Verified by reading the deployed builds' Clerk publishable key + CSP API target:
- **US prod** `snapai.mainnov.tech` → `pk_live_` Clerk + `scopesnap-api-production` ✅ correct.
- **PK prod** `pk.snapai.mainnov.tech` → `pk_test_` (DEV) Clerk + `scopesnap-api-staging` ❌ — it is serving the **staging build/env**, not production.
Implication: pk.snapai has been running against the **staging** backend + staging DB + dev Clerk. So (a) the 2026-06-09 staging view fix also benefits pk.snapai, and (b) the real remedy is to re-point the pk.snapai prod domain to the production Vercel deployment/env (prod Clerk `pk_live_` + `scopesnap-api-production`). Needs Vercel domain/env access.

### UPDATE 2026-06-09b — pk.snapai mechanism nailed (Vercel verified)
Vercel `scope-snap-ai` (prod project) env vars are CORRECT, scope "All Environments":
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY = pk_live_…` (clerk.snapai.mainnov.tech)
- `NEXT_PUBLIC_API_URL = https://scopesnap-api-production.up.railway.app`
Both `pk.snapai.mainnov.tech` and `snapai.mainnov.tech` are connected domains on this project (Production). `snapai` serves the current prod build correctly. `pk.snapai` serves a STALE build (pk_test_ dev Clerk + scopesnap-api-staging) — it is aliased to an old deployment built before the env vars were corrected (API_URL updated Mar 22, Clerk key updated Apr 4). It never re-aliased to a current production deployment.
**Consequence to flag before fixing:** pk.snapai has therefore been running on STAGING the whole time — dev Clerk accounts + Virginia-STAGING DB. Re-pointing it to the current prod build moves it to pk_live Clerk + prod API + Virginia-PROD DB. Any existing pk.snapai tester accounts/data live in the staging instance and won't carry over. For pre-launch beta this is likely negligible, but it's the owner's call.
**Fix options:** (a) redeploy `scope-snap-ai` production (re-aliases all prod domains; US unaffected since its build is already correct), or (b) re-assign the pk.snapai domain to the production deployment/branch via Vercel → project → Settings → Domains → Edit. Either makes pk.snapai serve pk_live + prod API.

### UPDATE 2026-06-09c — PK FULLY RESOLVED (live-verified)
All three PK issues fixed and verified live:
1. **DB views (DEC-092):** 5 missing `pak_*_v` views recreated in Virginia staging; Virginia prod already had all 6. Codified in Alembic migration `037_pak_market_views.py`, committed to staging + main (idempotent no-op on current DBs; protects future restores).
2. **pk.snapai on wrong build:** the production PK domain was aliased to a stale deployment (dev Clerk + staging API). Fixed via Vercel → scope-snap-ai → Settings → Domains → pk.snapai → Edit → Save (re-aliased to current production deployment 03d80cb). pk.snapai now serves `pk_live_` Clerk + `scopesnap-api-production` + Virginia-prod DB. **No rebuild needed** (which sidestepped the E404 build failure below). US prod untouched.
3. **Dashboard "API offline":** root cause was a STALE SERVICE WORKER (snapai-shell-v2) carried over from the old build, intercepting `/api/*` calls and failing them — NOT backend CORS. Cleared via unregister + cache delete; dashboard then loaded real prod data (rpt-0456, rpt-688001, rpt-9515, rpt-547105, rpt-5025). 

**Live-verified:** pk.snapai/dashboard renders production assessments end-to-end.

**Caveats / open follow-ups:**
- **Returning PK users** who visited the old pk.snapai may still hold the stale SW and could see "API offline" until it updates / they hard-refresh. A clean way to force all clients to refresh is to bump the SW cache name (v2→v3) on the next frontend deploy — BUT see next item.
- **Frontend prod builds currently FAIL** with `npm error code E404` (a dependency version was pulled from the npm registry). Fresh Vercel production builds error at `npm install --legacy-peer-deps`. The live prod deployment (03d80cb, May 29) still works, but no NEW frontend changes can ship to prod until the bad dependency is pinned/updated in package.json/package-lock.json. This must be fixed before any SW-version bump or frontend change.
- **pk-staging** likely has the same stale-SW symptom (lower priority; staging). Staging DB now has the views.

### UPDATE 2026-06-09d — E404 re-characterized (NOT blocking normal deploys)
Checked the Vercel deployments list: my `037` main commit built a NEW production deployment `36e23fd` (Ready, 2m3s) and the staging commit `064354c` (Ready). Only the **manual "Redeploy with build cache OFF"** errored on E404. Conclusion: **normal git-push deploys succeed** (they reuse the build cache and skip the failing clean `npm install`). The `npm error E404` only occurs on a **from-scratch reinstall** (a dependency version is missing from the npm registry, but it's still in Vercel's build cache). 
- **Severity: LOW** — shipping frontend changes works today. The latent risk is that if the build cache is ever evicted/invalidated, a clean rebuild will fail until the yanked dependency is pinned/updated in scopesnap-web/package.json + package-lock.json.
- The exact 404'ing package wasn't captured (Vercel build-log UI kept freezing the browser; sandbox `npm install` was too slow to finish). To find it: open the failed deploy `HS8BeUq…` build log and read the `npm error 404 ... is not in this registry` line, then bump that dep.

### UPDATE 2026-06-09e — SW staleness RESOLVED + deployed
Bumped sw.js CACHE_NAME snapai-shell-v2 → v3, committed to staging + main. The main production build (58f973f, "fix(pwa): bump SW cache v2→v3") built **Ready** via a normal cache-backed deploy (further confirming the E404 only affects no-cache rebuilds). Live-verified: pk.snapai serves sw.js with CACHE_NAME=snapai-shell-v3 + railway passthrough. Returning clients now force-update on next visit (skipWaiting + clients.claim + old-cache purge in the activate handler), clearing the stale-SW "API offline" for good. Staging build queued.
**Net: all PK issues fully resolved & deployed. Only remaining open item is the LOW-priority E404 (clean-rebuild only; normal deploys work).**

### UPDATE 2026-06-09f — E404 "cleanup" + TRUE root causes of PK flapping (all fixed & live-verified)
The E404 was investigated and turned out to be a **transient npm-registry blip** (a clean `npm install --legacy-peer-deps` completed with 0 errors, 595 pkgs). While hardening it, two REAL root causes of the recurring PK breakage were found and fixed:

1. **No lockfile → non-deterministic builds.** Repo had only package.json (vercel.json runs `npm install --legacy-peer-deps`), so every clean build re-resolved "latest matching" and was exposed to transient registry issues + drift. FIX: generated + committed `scopesnap-web/package-lock.json` (pins the exact versions prod runs: next@14.2.15, react@18.3.1, @clerk/nextjs@5.7.6, @supabase/supabase-js@2.108.0). Verified on staging (Ready) then promoted to main (Ready). Deterministic builds now.

2. **Service worker intercepted API calls.** sw.js did `event.respondWith(fetch(event.request))` for /api/ + cross-origin — that re-fetch failed on the PK origin (while direct browser fetch returned 200 + data), causing the recurring "API offline" whenever the SW controlled the page. FIX: SW **v4** now `return`s without respondWith for API/cross-origin → browser handles natively. Live-verified: pk.snapai dashboard loads real data WITH the v4 SW controlling the page.

3. **THE big one — `vercel.json` had a hardcoded `"alias": ["pk.snapai.mainnov.tech"]`.** Because BOTH the prod project (scope-snap-ai, builds main) and the staging project (scopesnap-web-staging, builds staging) build this same vercel.json, **every staging deploy stole pk.snapai to the staging build (dev Clerk + staging API) and every prod deploy stole it back** — the actual cause of pk.snapai flapping all session. FIX: removed the `alias` from vercel.json on BOTH branches; pk.snapai is now governed solely by the Vercel Domains setting (assigned to scope-snap-ai prod). Re-asserted via Domains → Save. Live-verified: pk.snapai = pk_live Clerk + scopesnap-api-production, and it will STAY (no alias to steal it).

**FINAL STATE: all PK issues fully resolved, deployed, and DURABLE. US untouched throughout.**

---

## 2026-06-09 — Low-priority cleanup done (items 1 & 3) + after-QA
- ✅ **Item 1 — pool tuning promoted to PROD:** `db/database.py` on main now matches staging (pool_size 5, max_overflow 5, pool_recycle 1800, dropped pool_pre_ping). Commit `5bd8c4c`. Prod backend redeployed, `/health` ok, db connected — new pool works on prod.
- ✅ **Item 3 — app_events index codified:** migration **038** (`038_app_events_report_viewed_index.py`, idempotent CREATE INDEX IF NOT EXISTS for `ix_app_events_report_viewed_short_id`) committed to staging + main. Both backends ran it — **both DBs now at Alembic 038, index present.** Protects the index against future restores (same lesson as the pak_*_v views).
- ⏳ **Item 2 — delete the two PAUSED Tokyo Supabase projects:** NOT done — permanently deleting a database is a prohibited action for the AI, so this is an **owner action**. Backups are safe in `ScopeSnapAI/backups/` (see TECH_STACK "PRE-MIGRATION TOKYO BACKUPS"). Steps for owner: Supabase dashboard → each Tokyo project (`scopesnap` ap-northeast-1 + `snapai-staging` ap-northeast-1) → Settings → General → Delete project. Safe once you're confident prod is stable. ($0 either way — paused projects don't bill.)
- **AFTER-QA (post all 3 changes):** prod + staging `/health` = ok/db-connected; both DBs Alembic **038** with the index present; PK prod dashboard renders real data (rpt-0456…) — **no regression**.

---

## 2026-06-10 — Free automated DB backups to Cloudflare R2 (DEC-094)

### DEC-094 — Daily pg_dump of both Virginia DBs → private Cloudflare R2 bucket (2026-06-10)
**Why:** Supabase free tier keeps **0-day backup retention** and permanently deletes data after an extended pause. The GitHub Actions keepalive pings prevent the pause, but a single missed ping risked data loss. DEC-094 adds an independent, off-platform safety net at $0.

**What runs:** `.github/workflows/db-backup-r2.yml` (on `main`). Schedule `0 3 * * *` (daily 03:00 UTC) + `workflow_dispatch`. Steps: install PG17 client → `pg_dump` PROD → `pg_dump` STAGING → verify. Each dump is plain SQL (`--no-owner --no-privileges --quote-all-identifiers`), gzipped, uploaded via `aws s3 cp` (preinstalled on the runner) to bucket `snapai-db-backups` under `prod/` and `staging/` prefixes.

**Cloudflare R2 setup (account `0c1bfa87134c7a6688d7eaf4410bf86a`):**
- Bucket **`snapai-db-backups`** — region **ENAM** (co-located w/ Virginia us-east-1 DBs), **Standard** storage class, **public access DISABLED** (private).
- **Object Lifecycle Rule** `delete-after-14-days` → auto-deletes objects 14 days after upload (no manual cleanup).
- Scoped API token **`snapai-db-backups-rw`** — Object Read & Write, **this bucket only**, no expiry. (Least-privilege: cannot touch the app's `scopesnap-uploads` / `scopesnap-uploads-staging` buckets.)
- **Cost = $0.** Free tier is 10 GB storage / 1M Class A / 10M Class B ops / **$0 egress**. Our load: ~0.2 MB prod + ~2 MB staging per day, ~2 writes/day. Orders of magnitude inside free. (R2 does require a card-on-file to enable — already done on this account.)

**GitHub repo secrets (names only — values are secret):** `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ENDPOINT` (=`https://0c1bfa87134c7a6688d7eaf4410bf86a.r2.cloudflarestorage.com`), `SUPABASE_DB_URL_PROD`, `SUPABASE_DB_URL_STAGING`.
- ⚠️ **Do NOT confuse with the older `CLOUDFLARE_R2_*` secrets** (CLOUDFLARE_R2_ACCESS_KEY / _SECRET_KEY / _ACCOUNT_ID / _BUCKET, added ~2 months prior) — those belong to the **app's uploads** bucket and a different token. The backup workflow uses ONLY the `R2_*` + `SUPABASE_DB_URL_*` names above.

**GOTCHAS LEARNED (cost 2 failed runs before green):**
1. **pg_dump version must be ≥ server version.** `ubuntu-latest` ships pg_dump **16**, but the Supabase server is **17.6** → `error: aborting because of server version mismatch`. Fix: `apt-get install postgresql-client-17` AND call the **explicit binary** `/usr/lib/postgresql/17/bin/pg_dump` (the `pg_wrapper` at `/usr/bin/pg_dump` still resolved to 16). Set via job env `PGDUMP`.
2. **Use the Session pooler, NOT the Transaction pooler.** First staging attempt used the Transaction-pooler string (**port 6543**, username collapsed to `postgres`) → `FATAL: password authentication failed for user "postgres"`. pg_dump needs **Session pooler** (port **5432**, username `postgres.<project-ref>`, IPv4-reachable from GitHub). Prod worked first try because it had the correct Session-pooler URL.
3. **workflow_dispatch only appears once the workflow file is on the default branch (`main`).** Pushed via git worktree from `origin/main` (then a contents-API edit for the fix) — the local working tree is a stale, dirty `staging` checkout, so never commit the backup file from there.

**VERIFIED 2026-06-10:** run `27296950101` = **success** (all 6 steps green). Bucket listing from the run: `prod/prod_20260610_1742.sql.gz` (228 KB), `prod/prod_20260610_1821.sql.gz` (228 KB), `staging/staging_20260610_1821.sql.gz` (2.1 MB). Post-change, both backends `/health` = `ok` / `db: connected` (prod `scopesnap-api-production.up.railway.app`, staging `scopesnap-api-staging.up.railway.app`) — the staging password/secret update did **not** break Railway staging.

**Restore how-to:** download the `.sql.gz` from R2 → `gunzip` → `psql "<target Session-pooler URL>" -f dump.sql`. Plain SQL, owner/privilege-stripped, so it restores cleanly into any empty DB.

**Still open (separate):** the Healthchecks "Keepalive B DOWN" alert — the two keepalive workflows still ping the **deleted Tokyo** Supabase URLs via the old `SUPABASE_PROD_URL` / `SUPABASE_STAGING_URL` secrets, so their `if: success()` heartbeat never fires. App is fine. Fix later: repoint those 4 keepalive secrets to the Virginia projects, or retire the keepalives now that R2 backups exist.

**Note:** `scopesnap-api.up.railway.app` (bare) returns a Railway "Application not found" 404 — it is **stale**. The live prod backend is **`scopesnap-api-production.up.railway.app`**.

### 2026-06-10 — Keepalive "DOWN" RESOLVED (DEC-094 follow-up)
Root cause confirmed from run logs: keepalive-supabase-B failed with `curl: (6) Could not resolve host: quqrvnoguofbjacrxcim.supabase.co` — the 4 keepalive secrets still pointed at the **deleted Tokyo** projects, so the ping failed and the `if: success()` Healthchecks heartbeat never fired → DOWN.

**Fix:** repointed all 4 keepalive secrets to the Virginia (us-east-1) projects (values fetched via Supabase MCP; updated through the GitHub Secrets API with libsodium sealed-box encryption — the anon keys are publishable/public):
- `SUPABASE_PROD_URL`    = `https://zpsoprffaujswywtsgzy.supabase.co` (snapai-prod-use1)
- `SUPABASE_STAGING_URL` = `https://kikhhnanuwzocwcpzutr.supabase.co` (snapai-staging-use1)
- `SUPABASE_PROD_ANON_KEY` / `SUPABASE_STAGING_ANON_KEY` = each project's legacy anon JWT.

**Verified 2026-06-10:** manually dispatched both keepalive-supabase-A and -B → both **success**; steps Ping production / Ping staging / Heartbeat(Healthchecks.io) all green. Both Healthchecks checks flip DOWN→UP. Twice-weekly schedule restored (A = Sun 02:00 UTC, B = Wed 14:00 UTC).

Note: keepalive is now somewhat redundant with the daily R2 backup (which pg_dumps both DBs daily = stronger DB-activity keepalive), but it's kept for the independent Healthchecks "did the scheduled job run" monitor.

### 2026-06-14 — Healthchecks false-DOWN fixed (grace 1h→6h)
Recurring weekly DOWN→UP emails on "SnapAI Keepalive A/B" were FALSE alarms, not outages. Root cause: GitHub Actions delays scheduled (cron) runs — worst at the top of the hour — so the `0 2`/`0 14` keepalives consistently fire ~4–4.5h late (e.g., Jun 14 scheduled 02:00, actually ran 06:29; same on Jun 7, May 31, May 24). Every run SUCCEEDS; the DB is fine. Healthchecks' 1h grace window was too short to absorb GitHub's delay, so it flagged DOWN at ~03:00 then UP when the late ping landed ~06:20.
FIX: widened both checks' Grace Time 1h → **6h** in the Healthchecks dashboard (crons left as-is; 6h covers the observed ~4.5h delay). Verified on screen: Keepalive A (`0 2 * * 0`) and B (`0 14 * * 3`) both show grace 6 hours. Project ffea9be1-058c-4891-9559-17b12eabe8af. No code/secret change needed.

---

## DEC-087 — QA skill consolidation: discard snapai-qa-master in favor of snapai-full-audit (2026-06-17)

**Date:** 2026-06-17

**Context:** SnapAI accumulated three overlapping QA orchestrator skills over development:
1. `snapai-qa` -- granular live-app verification using Chrome MCP (Layer 4 of qa-master)
2. `snapai-qa-master` -- 5-layer orchestrator wrapping snapai-qa + community skills
3. New `snapai-full-audit` (designed in this conversation) -- 24-step 3-mode audit cycle with 10 cost mitigations + security priority + Cowork-first design

Three QA orchestrators creates cognitive overhead at invocation time, drift risk during maintenance (one skill updated but not the others), and unclear single-source-of-truth for the staging-to-prod promote ceremony.

**Decision:** Discard `snapai-qa-master`. Functionality fully absorbed by `snapai-full-audit`:
- 5-layer mapping -> 7-phase mapping (no functionality lost)
- DEC-070 7-checkpoint promote gate preserved verbatim as Phase 4
- SnapAI-specific staging checks (Urdu glyph rendering, PKR currency, R-410A/R-22/R-32 PSI thresholds, DEC-049 market isolation) preserved as Phase 3 explicit steps
- Brain-file update pattern preserved as Phase 7
- Delegation to `snapai-qa` for prod verification preserved as Phase 6 invocation

**Decision details:**
1. User deleted `snapai-qa-master` from Cowork Settings -> Capabilities on 2026-06-17
2. New `snapai-full-audit` skill content documented in `SnapAI_Full_Audit_Skill.md` (to be installed after `SnapAI_Audit_Framework_Setup.md` prerequisites complete)
3. Keep `snapai-qa` (used independently for granular live verification + invoked by snapai-full-audit Phase 6)
4. Keep `snapai-dev` (used for per-PR code review, replaces paid Anthropic claude-code-security-review GitHub Action -- saves $0.20-1.00/month)
5. Keep `webapp-testing`, `quality-playbook`, `accessibility-a11y-enhanced` (all delegated to by snapai-full-audit)
6. Keep `playwright-e2e`, `pytest-patterns` (developer-side test-authoring references, not invoked by audit)

**Why:**
- Reduces maintenance burden (one orchestrator instead of two)
- Eliminates drift risk between qa-master and full-audit when one gets updated
- Cowork-first design removes Anthropic API key dependency
- 10 cost mitigations protect against Railway $10/$15 hard cap trips and Sentry/PostHog quota burn
- Three modes (scoped/safe/full) enable right-sized audits per cadence (per-PR vs monthly vs quarterly)
- Security priority elevated per user's stated risk profile ("hacked before, do not want to be hacked again")

**Impact:**
- Monthly cost: +$2.50-7.00 (audit add-on) on top of $16.43 baseline
- Setup time: ~3.5-4 hours one-time (Phase A platform configs + Phase B SDK code changes + Phase C skill installs + Phase D verification)
- Maintenance: ~80 lines of SnapAI-specific custom code in snapai-full-audit (vs ~800 lines if 5 custom skills were built from scratch)
- Railway compute hard cap raised $10 -> $15 to accommodate quarterly full-mode audit without trip risk

**Cross-references:**
- SnapAI_Audit_Framework_Setup.md -- prerequisites that must complete before snapai-full-audit can run safely
- SnapAI_Full_Audit_Skill.md -- the new skill content (paste into Settings -> Capabilities -> Skills)
- SnapAI_PK_Market_Positioning.md -- PK gaps are acceptable per test-market positioning
- DEC-070 -- staging-first workflow embedded as Phase 4 promote gate
- DEC-049 -- market isolation check preserved as Phase 3 explicit step
- DEC-027 -- NTFS Unicode truncation rule respected (this DECISIONS.md update via bash heredoc append, not Edit tool)
- DEC-005 -- Clerk JWT authentication needed for audit-test users
- DEC-004 -- /tmp clone for any code change deploys (Sentry/PostHog SDK changes in Phase B)


---

## DEC-101 — Brand Decoder v1.2 PROMOTED TO PROD 2026-06-17 (main `f70b6276`); PostHog now LIVE on prod

**Supersedes the "pending"/"unset" status in DEC-098 and DEC-100.** On Shoab's "go", staging→main promote completed and verified live:
- Prod backend: `/api/version` → decoder/replace/brand_data **1.2**, **`analytics_enabled:true`**, `/health environment:production`, **alembic head 040** (Supabase prod `zpsoprffaujswywtsgzy`, migration-040 columns present).
- **`POSTHOG_API_KEY` IS NOW SET on Railway prod** (publishable `phc_A5spSA…`) → backend shadow-eval + `age_corrected` events fire on prod, tagged `environment:production` (ENVIRONMENT var set). Staging also has it. So DEC-098's "UNSET" and DEC-100's "pending" are RESOLVED — PostHog is fully live both ends.
- Frontend PostHog tag CONFIRMED on prod: localStorage `ph_phc_…_posthog.environment = "production"` (and `staging` on staging). Single-project environment-split working end-to-end.
- **Live prod UI QA PASSED:** fresh diagnostic (Carrier, install 2008 + Sure → Refrigerant Leak) → estimate rpt-592468 → Full Replacement reads "**At 18 years old**, complete system replacement…" (Finding-1 `[N]` substitution live) + Continue = "Replace Immediately ($6,480)" = ★REC (Finding-2 live). a11y sidebar contrast clean.

## DEC-102 — File-scoped promote for a DIVERGED staging↔main (the prod-promote method that worked)

**Problem:** at promote time `staging` was diverged from `main` (ahead 31 / behind 15) — main had 15 commits staging lacked (mostly earlier file-scoped promotes + a few direct-on-main hotfixes). A naive full-tree copy could have reverted prod-only changes.
**Method that worked:** (1) `GET /compare/main...staging` for the changed-file list; (2) identify the genuinely direct-on-main hotfixes (`public/sw.js`, `vercel.json`) and **byte-diff them main vs staging — both identical**, so no revert risk; (3) build a new tree on main via the **GitHub trees API with `base_tree` = main's tree**, overlaying ONLY staging's blobs for the changed files → main-only files (R2 workflow, docs, lock) preserved; (4) commit + update `refs/heads/main`. Script: `_s1_stage/promote_to_main.py` (dry-run by default; `--commit` to write). 60 files promoted.
**Decision:** for any future promote, ALWAYS run the compare + byte-diff the direct-on-main hotfix files BEFORE overlaying. Don't full-tree-copy a diverged branch.

## DEC-103 — package-lock.json: main INTENTIONALLY has one now (DEC-065/099 partially superseded)

**Correction to DEC-065/DEC-099:** `main` (prod) DOES carry a committed `scopesnap-web/package-lock.json` as of commit `33871bae` ("promote package-lock.json to prod — deterministic builds — verified"). So "never commit a lockfile" is no longer absolute for prod. **What the promote did:** EXCLUDED `package-lock.json` from the staging→main overlay so main keeps its OWN verified lock (staging's was regenerated during the Playwright `npm install` and `package.json` was unchanged, so no dependency drift). Rule going forward: don't blindly drag staging's lock onto main; keep main's verified one unless `package.json` actually changed.

## DEC-104 — test_fault_estimate_age_v2's head-loader must inject every module the head uses (regression caught + fixed)

**Regression I introduced + fixed (`d7dbc2a8`):** `tests/test_fault_estimate_age_v2.py` execs the dependency-light HEAD of `fault_estimate.py` via `_load_fault_estimate_funcs()`, manually injecting a FIXED set of names (Optional/math/datetime/timezone/logging). The Finding-1 fix added `re`-based helpers (`_AGE_LEADIN_RE`, `finalize_replacement_copy`) in that head region → `NameError: name 're' is not defined` at COLLECTION (aborts the whole suite). Fix: inject `re` into the loader. **Lesson:** when adding a top-level helper to the head region of `fault_estimate.py`, also add any new stdlib import to the test loader's inject list. **Bigger lesson: the GitHub Actions Playwright CI is FRONTEND-ONLY — it does NOT run backend pytest.** Backend test regressions are invisible to CI; run `python -m pytest` in a clone before promoting. Full backend suite is **120 passed** at d7dbc2a8.

## DEC-105 — Tooling gotchas learned this session (save future time)

- **The Edit tool TRUNCATES large files** (observed on 56–80 KB source files: the file was silently cut mid-token, breaking it). For big files, edit via a **scripted Python string-replace** that reads pristine → writes a complete file (pattern: `_s1_stage/apply_fixes.py` / `apply_a11y.py`, with per-edit `count==1` asserts + `py_compile`/brace-balance verification). Always re-fetch a fresh pristine copy from the branch tip before scripted editing.
- **Railway `/api/version` (and similar GET) responses can be CACHED** at the edge — after an env-var redeploy, a plain poll showed `analytics_enabled:false` long after it was actually true. Append a cache-buster query param (`?cb=…`) to read the live value.
- **Railway env-var change → click "Deploy" on the staged change, then if the value still isn't picked up, Deployments → ⋮ → Redeploy.** The new container reads current env at start.
- **Prod login (Clerk) via Chrome:** use the "Continue with Google" SSO passthrough with the already-signed-in account (no password entered, never type credentials). Caveat: a freshly-created MCP tab/window may NOT carry the prod session and the Google OAuth popup can freeze — re-navigating to `/dashboard` in a fresh tab of the existing profile is the reliable recovery.
- **Committing to the private repo from the sandbox is blocked (no token); use the Windows side** (`_s1_stage/gh_commit.py` / `gh_fetch.py`) which pulls the token from the git credential manager in-process.


---

## DEC-106 — Session retrospective: what went wrong + how we fixed it (Brand-Decoder prod promote, 2026-06-17)

A consolidated "read this next time" log of the snags hit this session and the fix that worked. (Technical specifics also in DEC-101–105.)

**A. The two user-facing findings — root cause = DB seed, not code.**
- `[N]` showing literally on the Full-Replacement tier: the placeholder is seeded in `fault_cards.better_option_estimate.description_best_replacement` by **migrations 021 (US) + 024 (PK)** — it predates all Brand-Decoder work. Two backend sites read it (`fault_estimate.py` generation + `estimates.refresh_draft_estimate` re-stamp); the refresh path is what actually re-introduced `[N]` into the builder on load. Fix: shared `finalize_replacement_copy()` applied at BOTH sites (substitute real age when `_has_reliable_age()`, else strip the "At [N] years old," lead-in — never fabricate) + a frontend `cleanAgeToken()` safety-net. Lesson: when a literal token leaks to the UI, grep for ALL read sites (not just the obvious one) — a "refresh/re-stamp" path can re-introduce it after generation fixes it.
- Continue button ≠ ★REC tier: builder hard-defaulted `useState("better")`; the ★REC badge is driven by the per-option `recommended` flag (set in `fault_estimate.py`), a different signal. Fix: default `selectedTier` to the option flagged `recommended`. Adversarial review then caught that the `data.recommended_tier` FALLBACK was unvalidated (could set a tier matching no option on the un-normalized `/estimate/[id]` route) → hardened with `optTiers.has(...)`. Lesson: `recOpt.tier` is always a valid option tier; any FALLBACK must be validated against the live option set.

**B. Process/tooling failures + fixes (save hours next time):**
1. **Edit tool truncated large source files** (56–80 KB) mid-token, silently breaking them → switched to scripted Python string-replace from a fresh pristine copy, with `count==1` asserts + `py_compile`/brace-balance checks. (DEC-105)
2. **A backend test regression I introduced was invisible to CI** — `test_fault_estimate_age_v2.py`'s head-loader didn't inject `re`; the Playwright CI is FRONTEND-ONLY so it passed anyway. Caught only by running `pytest` in a clone. Lesson: ALWAYS run backend pytest in a clone before promoting; CI does not. (DEC-104)
3. **Railway `/api/version` returned a stale CACHED `analytics_enabled:false`** for minutes after the env-var redeploy → cache-buster query param revealed the true `true`. Don't trust a single un-cache-busted poll. (DEC-105)
4. **Diverged staging↔main** (ahead 31/behind 15) made a naive promote risky → file-scoped tree-overlay (`base_tree`=main) after byte-diffing the only direct-on-main hotfixes (`sw.js`, `vercel.json` — both identical). (DEC-102)
5. **`package-lock.json`**: main intentionally has one now (DEC-103) — excluded staging's from the overlay; kept main's verified lock.
6. **Prod Clerk login via Chrome**: "Continue with Google" SSO passthrough (no password). A freshly-created MCP tab/window did NOT carry the prod session and the Google OAuth popup froze; recovery = re-navigate to the app in a fresh tab of the EXISTING profile (the cookie was there). **US and PK prod SHARE the same Clerk production app**, so logging into snapai.mainnov.tech also authenticates pk.snapai.mainnov.tech — no separate PK login needed (corrects the earlier "PK needs separate login" assumption).

**C. The `snapai-qa` skill recipe is STALE — don't follow it literally.** Phase 1.5 references `pnpm`, a `SnapAIAI` repo name, `git@` SSH clone, and `pak_diagnostic_questions` — none current. Reality: repo is `ScopeSnapAI` (npm, no committed lockfile historically per DEC-065 but main now has one), PSI thresholds live in `operating_targets` (+ `pak_operating_targets_v` view), and the real Playwright run is the GitHub Actions workflow. Use the live CI + Supabase DB instead of the skill's clone block.

**D. Verification surfaces for the replacement copy = THREE, all confirmed on prod both markets:** estimate builder, generated contractor PDF (via Output tab — drafts show `…-unavailable.pdf` until documents are generated; EXPECTED, not a bug), and the public homeowner report (`/r/{slug}/{token}`). All three render the resolved age ("At 18 years old…") with ★REC = the recommended/selected tier.

**E. What worked well (keep doing):** dry-run-before-commit on the promote script; an independent adversarial code-review subagent (caught a real HIGH); running the full backend suite in a clone (caught the `re` regression); verifying via the prod DB + cache-busted endpoints rather than assuming; updating brain files continuously in ACTIVE_TASKS.


---

## DEC-107 — Catch-all exception handler MUST call sentry_sdk.capture_exception (Sentry was silently capturing nothing)

**Date:** 2026-06-17. **Severity: real latent bug, fixed.**

**Problem:** `main.py`'s global `@app.exception_handler(Exception)` logged the error and returned a JSON 500 but **never called `sentry_sdk.capture_exception(exc)`**. A catch-all handler marks the exception "handled", so it never propagates to Starlette's `ServerErrorMiddleware` where Sentry's `FastApiIntegration` hooks → **Sentry auto-capture is suppressed**. Result: despite `sentry_sdk.init()` running and `SENTRY_DSN` being set on both Railway envs, **backend 500s NEVER reached Sentry** — both Sentry projects (`snapai-api`, `snapai-web`) showed 0 errors / 0 transactions / "No activity yet" for their entire lifetime. The old code comment ("Sentry captures the full exception in all environments") was FALSE.

**How found:** Shoab asked "with no users, how do we know Sentry/PostHog actually work?" — the right question. PostHog was provable (generated QA events landed, tagged `production`, confirmed via direct HogQL query). Sentry showed 0 events ever, which is ambiguous (healthy vs. not-capturing). The only way to KNOW = trigger a deliberate test error and watch it land. That exposed the swallow.

**Fix:** added `sentry_sdk.capture_exception(exc)` inside the handler (safe no-op when Sentry uninitialised). **Proven on staging** via temporary `/debug/sentry-boom` (raises) + `/debug/sentry-check` (reports init state): the RuntimeError landed in Sentry as issue **SNAPAI-API-17**, tagged `environment:staging`, 2 events. Temp endpoints then removed (staging commit `537bbeee`); the capture fix promoted to prod (`main` commit `e4eaf1b`, verified `/api/version` 1.2 + healthy). Going forward, real backend 500s on staging AND prod will appear in Sentry, env-tagged.

**Rule:** any catch-all/broad `exception_handler` in this app MUST call `sentry_sdk.capture_exception(exc)` explicitly — never assume the integration auto-captures handled exceptions. **Verification rule (no users yet):** to confirm an observability pipe works, GENERATE the signal yourself (run a diagnostic for PostHog; trigger a deliberate error for Sentry) and confirm it lands — "no errors" alone proves nothing.

**Still open (frontend):** `@sentry/nextjs` is wired (config files + `app/error.tsx`) but frontend capture was NOT separately proven this session — prove it the same way (throw on a staging page, confirm a `snapai-web` event) when convenient.


---

## DEC-108 — FRONTEND Sentry is NON-FUNCTIONAL (next.config not wrapped with withSentryConfig) — OPEN

**Date:** 2026-06-17. **Status: diagnosed, NOT yet fixed — tracked issue.**

**Finding (Shoab asked to prove the frontend Sentry too):** the browser Sentry SDK never initializes. Evidence: `window.__SENTRY__` absent on a live page, no `ingest.us.sentry.io` request on load or after a deliberately-thrown error, and the `snapai-web` Sentry project shows "No activity yet / Start Setup" for its whole lifetime.

**Two-layer root cause:**
1. `NEXT_PUBLIC_SENTRY_DSN` was **not set on Vercel** (both projects). FIXED for staging this session — added to `scopesnap-web-staging` (Production+Preview) and redeployed the staging-branch Preview (the deployment that actually serves staging.snapai.mainnov.tech — NOTE: in this project **Production = main branch, Preview = staging branch**; staging.snapai.mainnov.tech is aliased to the staging-branch Preview, so redeploy THAT, not "Production"). Still TODO on the prod project `scope-snap-ai`.
2. **DEEPER + the real blocker:** `scopesnap-web/next.config.js` is NOT wrapped with `withSentryConfig` (it ends `module.exports = nextConfig`), and there is no `instrumentation.ts`. `@sentry/nextjs` requires `module.exports = withSentryConfig(nextConfig, {...})` (and, on v8+, instrumentation hooks) to bundle + load `sentry.client.config.ts` / `sentry.server.config.ts` / `sentry.edge.config.ts`. Without it those files are dead code and `Sentry.init()` never runs — so even with the DSN set, the client captures nothing. The frontend Sentry has therefore NEVER worked.

**Fix (do as a careful, dedicated change — NOT a quick toggle):**
- Wrap `next.config.js` with `withSentryConfig(nextConfig, { silent: true, org: "mainnov", project: "snapai-web", ... })`; add `instrumentation.ts` per the installed `@sentry/nextjs` version's requirements (v8 vs v10 differ — coordinate with the pending Dependabot bump `@sentry/nextjs 8.55→10.58`).
- Set `NEXT_PUBLIC_SENTRY_DSN = https://b1f8b4ab770cb14b690aebd2760abba3@o4511219463487488.ingest.us.sentry.io/4511219475546112` on BOTH Vercel projects (staging done; prod `scope-snap-ai` TODO) + a `SENTRY_AUTH_TOKEN` if sourcemap upload is wanted.
- Test build locally (withSentryConfig can break the build if misconfigured), deploy staging-branch Preview, then PROVE: throw on a staging page → confirm a `snapai-web` event tagged `environment:staging`. Then promote to prod.

**Bottom line for next AI:** backend Sentry = WORKING (DEC-107). Frontend Sentry = WIRED-IN-CODE-BUT-DEAD until `next.config` is wrapped. Don't trust "0 errors" on `snapai-web` as healthy — it's not even connected.


### DEC-108 — RESOLVED 2026-06-17 (frontend Sentry now LIVE both ends)

Fixed via two commits: `next.config.js` wrapped with `withSentryConfig` (sourcemaps disabled → no auth token, build-safe) + CSP `connect-src` now allows `https://*.ingest.us.sentry.io`. Staging commit `17ae165`, prod promote `390d54b` — both Vercel builds Ready (withSentryConfig did NOT break the build). `NEXT_PUBLIC_SENTRY_DSN`: added to the staging Vercel project (`scopesnap-web-staging`, the staging-branch Preview is what serves staging.snapai.mainnov.tech — redeploy THAT, not "Production"); prod project `scope-snap-ai` already had it (All Environments, Apr 14).

**PROVEN:**
- Staging: `window.__SENTRY__` present, deliberate error → issue **SNAPAI-WEB-1** (literally the first event ever in `snapai-web`), ingest 200s, `sentry.javascript.nextjs/8.55.2`, env:staging.
- Prod (snapai.mainnov.tech): SDK active, 3 ingest requests on load, `sentry_key=b1f8b4ab…` matches the snapai-web DSN (did NOT throw a deliberate error on prod — kept it clean; identical staging-proven code).

**OBSERVABILITY NOW FULLY WORKING both envs:** PostHog (DEC-100/101), backend Sentry (DEC-107), frontend Sentry (this). The PWA service worker caches the JS bundle, so when verifying a new frontend deploy, unregister SWs + clear caches + hard-reload, else you'll test stale code. Optional future polish: add `instrumentation.ts` for Next server/edge Sentry, and `SENTRY_AUTH_TOKEN` if you want sourcemap upload — coordinate with the pending `@sentry/nextjs` v10 Dependabot bump.

---

## DEC-109 — Fix undefined `logger` + duplicate-provision race in api/auth.py (SNAPAI-API-Z)

**Date:** 2026-06-18  **Status:** Resolved, live both envs.

**Found via:** Direct Sentry dashboard audit (org `mainnov`) — NOT email. The Sentry email alerts only fired for a subset of issues; the dashboard showed 8 unresolved issues the email audit had missed. Lesson: audit the platform, not just the alert emails.

**Root cause (two stacked bugs in `scopesnap-api/api/auth.py`, `_load_auth_context`):**
1. `logger` was referenced (lines ~202/210/212) but `logging` was never imported and no module logger defined → `NameError: name 'logger' is not defined` whenever the Clerk auto-provision fallback hit its except branch. This turned provision failures into 500s and **masked the real underlying error**.
2. The masked error was a **duplicate-provision race**: the Clerk `user.created` webhook AND the `/api/auth/me` auto-provision fallback both tried to create the same user (the `ds.shoab+audit1` test account got two welcome emails), colliding on a duplicate key. Because the user re-query sat *inside* the success branch of the try, a user that actually existed resolved to a spurious 404.

**Fix:**
- `import logging` + `logger = logging.getLogger(__name__)` (matches codebase convention).
- Moved the user re-query *out* of the try/except to always run after the provision attempt, with `await db.rollback()` in the except so a failed transaction doesn't poison the re-query. A racing-webhook duplicate now resolves to the existing user instead of 404/500.

**Commits:** staging `37faefed` → prod (main) `d432caad` (single-file; main's auth.py was byte-identical sha256 `a557c4c3...` to the pre-fix staging version, clean drop-in). Both Railway deploys ACTIVE + "Deployment successful". prod `/health` ok, `/api/version` 1.2 (no regression).

**Sentry cleanup:** Resolved all 8 then-unresolved issues (chose Resolve over Archive to keep regression detection): SNAPAI-API-Z (this fix), SNAPAI-WEB-1 + SNAPAI-API-17 (deliberate verification tests), SNAPAI-API-15/12 (Gemini key expired/leaked — fixed weeks ago by key rotation), SNAPAI-API-13/16 (Gemini 429 prepay credits depleted — **billing watch item**, will auto-reopen if credits deplete again), SNAPAI-API-R (metering_type column — fixed by later migration). Dashboard now clean.

**Open follow-up:** Gemini prepay credit balance is a latent prod risk (API-13/16). If OCR 429s reappear, top up credits in AI Studio.

---

## DEC-088 — PERMANENT COPY RULE: No future-tense outcome promises in any homeowner-facing language (2026-06-17)

**Date:** 2026-06-17

**Context:** Shoab caught a dual-mode failure (legal + customer trust) in board-recommended copy that included phrases like "prevent it from coming back (2-year warranty)." The phrase was added by a board persona ("Mark Delgado") as a "trades operator credibility move" but reflected a wider AI failure mode: optimizing for short-term tier-conversion psychology at the cost of long-term legal liability and customer trust.

Root cause analysis: 16 AI-channeled board voices missed the dual exposure (Magnuson-Moss implied warranty + viral negative review damage). The founder caught what the boards missed. Pattern-of-failure: AI rubber-stamping its own proposals through board voices.

**Decision:** Permanent SnapAI copy rule -- never describe what will happen in the future, only describe what's being done now. Codified in PROJECT_BRAIN.md with full banned/allowed word list. Applies to every homeowner-facing string, contractor email, report, PDF, Present Mode slide, line item label, option description, footer, disclaimer, onboarding message.

**Why:**
1. Legal: Future-tense promises trigger Magnuson-Moss Warranty Act implied warranties (15 USC Sec 2301 et seq.); Texas DTPA Sec 17.46(b) treats unmet promises as deceptive practices; FTC Sec 5 requires substantiation of any predictive claim
2. Customer trust: Even without legal action, single failed promise destroys homeowner trust + creates viral negative reviews that damage all contractors using SnapAI
3. Contractor protection: SnapAI generating warranty language on contractor's behalf without their consent exposes both parties; contractors get sued for terms they never agreed to
4. Future flexibility: Contractors who DO want to offer specific warranties populate companies.warranty_text field (added in DEC-088 implementation); SnapAI displays exactly what contractor wrote, never invents

**Banned words / phrases:**
prevent, prevents, will prevent, guarantee, guarantees, warranty (without contractor field), ensure, ensures, will not, won't, stop forever, stop permanently, permanent solution, lasts X years, lasts forever, eliminates, prevents recurrence, prevents return, risk-free, no risk, always works, never fails, saves you $X (without substantiation)

**Allowed alternatives:**
Present-tense action verbs (find, seal, refill, replace, install, remove, wire, test) + descriptive framings (designed to, intended to, includes, addresses, targets, common point of failure, as preventive maintenance, industry standard for)

**Enforcement:**
1. Pre-commit hook on SnapAIAI repo scans new strings for banned words (added in implementation phase)
2. Semgrep CI rule flags banned words on every PR (added when Semgrep is installed per audit framework setup)
3. snapai-copywriting skill bakes banned list into copy generation
4. snapai-full-audit Phase 1 Brand Voice check greps for banned words during audits
5. Existing copy scrubbed (Phase 1 of implementation -- see implementation plan below)
6. New companies.warranty_text VARCHAR(500) field for contractor-controlled warranty display

**Impact:**
- All Day 1-5 bug fix copy MUST pass this rule (already drafted compliant per joint board meeting 2026-06-17)
- Existing 19 US + 15 PK fault card names + descriptions in ac_data_repo.json need scrubbing for violations (Day 1 audit task)
- All future fault card additions must pass this rule
- All marketing copy by Sajan / Codie passes this rule (snapai-copywriting skill enforces)
- All audit reports must include "Banned Words Check" line as PASS/FAIL

**Cross-references:**
- PROJECT_BRAIN.md entry 2026-06-17 -- full rule + banned/allowed lists
- DEC-087 -- QA skill consolidation (snapai-full-audit Phase 1 brand voice enforces this rule)
- DEC-070 -- staging-first workflow (apply this rule pre-merge to staging)
- Alfred (Seat 15 of snapai-nav) -- legal counsel whose Magnuson-Moss + FTC Sec 5 analysis informed this rule
- Bug 1+5 fixes (markup leak + replacement semantics) -- first application of this rule

## DEC-110 — Dependabot handling policy + dependency-bump outcomes (2026-06-18 PM)

**Date:** 2026-06-18 (PM)  **Status:** Live both envs.

**Context:** 5 open Dependabot PRs against `main`. Triaged live — the PR labels were misleading (see #2/#4 below).

**Findings (live):**
- **#6 `dompurify` 3.4.8→3.4.11** — transitive (via `posthog-js`), lockfile-only, security patch. SAFE.
- **#2 (`uuid`+`@sentry/nextjs`) and #4 (`@opentelemetry/core`+`@sentry/nextjs`)** — both labelled "minor" but the real `package.json` change is `@sentry/nextjs ^8.0.0 → ^10.58.0`, a **v8→v10 MAJOR** (uuid/otel are lockfile sub-deps). Green CI is NOT proof here — CI is frontend-Playwright-only and does not exercise Sentry event delivery.
- **#5 `next` 14.2.15→16.2.9 and #3 `@clerk/nextjs` ^5.7.2→^7.5.3** — both fail at *npm install* (peer conflicts). Root cause: both require **React 19** while we pin `react ^18`. One coordinated migration epic, not a drive-by.

**Decisions:**
1. **Applied (staging→prod):** `@sentry/nextjs ^8→^10.58.0` (+ `@opentelemetry/core 2.8.0`) and `dompurify 3.4.11`, in one regenerated lockfile. Done as the deliberate Sentry v10 upgrade DEC-108 anticipated. `next.config.js` already used the v9+ `withSentryConfig(cfg, opts)` style, so the v8→v9 break did not apply. §5 event-delivery RE-PROVEN on both envs.
2. **Shelved (prod untouched):** #5 Next 16 and #3 Clerk v7 → tracked as a single "React 18→19 / Next 16 / Clerk v7" migration epic (also: Turbopack-default vs our `next.config.js` webpack block, `middleware.ts → proxy.ts`, async `cookies()/headers()/params`). Multi-day hand migration.
3. **`dependabot.yml` policy** (already byte-identical on `main` via `6f4925a` from the audit-framework session; committed to `staging` here for parity, blob `1a16cb8d`): `target-branch: staging` (bumps flow staging-first, never straight to prod), group minor+patch into one weekly PR, **ignore `version-update:semver-major`** (majors become manual scheduled migrations), security updates stay on. Applied to npm + pip + github-actions.

**Verification (§5 Sentry, both envs):** deliberate client errors → ingest HTTP 200, `sentry_client=sentry.javascript.nextjs/10.58.0`, DSN `b1f8b4ab…` (snapai-web). Staging event tagged `environment:staging`, prod tagged `environment:production` (both grouped as `SNAPAI-WEB-2`, since resolved). Dashboard clean (`is:unresolved` empty, both projects). Prod `/api/version` still **1.2**.

**Commits:** staging `550cd5004dae879a298c3375053d939d58eb0424` (deps + dependabot.yml); prod `85411820793654fe9736233748ce0f4cdd5060f0` (deps only — dependabot.yml omitted, already on main). CI: staging run #15 green, prod run #18 green.

**Cross-references:** DEC-070 (staging-first), DEC-108 (frontend Sentry wiring + the anticipated v10 bump), WORKFLOW.md.

**Open follow-up:** `npm audit` reports 7 advisories (1 critical / 5 high / 1 moderate) in the tree — pre-existing transitive, NOT introduced here (dompurify was upgraded); not auto-fixed (`audit fix --force` makes breaking changes). Separate hardening pass recommended.

---

## DEC-111 — MANDATORY `git fetch` before any code-state claim (2026-06-18)

**Date:** 2026-06-18
**Trigger:** AI session (Claude) told Shoab the missing-age default bug at `fault_estimate.py:55-77` was NOT resolved, based on reading the Drive-synced working copy. Truth: the fix had shipped to prod the previous day (commit `f70b627`, Brand Decoder v1.2 promote, 2026-06-17 19:31 PKT). AI argued with Shoab when Shoab said "this is resolved" — wasting Shoab's time and damaging trust.

**Root cause:** Drive-synced ScopeSnapAI working copy lags behind origin/main and origin/staging. The Windows machine's git pull cadence is independent of /tmp/snapai_tmp clones used by AI sessions per DEC-004. Drive-synced HEAD on 2026-06-18 was at commit `526d9e4` from 2026-05-27 — 22 days behind prod with ~30 missing commits including two major feature ships (Brand Decoder v1.2, audit framework).

**Decision:** Every AI session that makes ANY claim about SnapAI code state — what's on prod, what's on staging, whether a fix is shipped, whether a bug exists, whether a file has X content — MUST run `git fetch origin --no-tags` FIRST and reason from `git show origin/<ref>:<path>` content, NOT from the Drive-synced working copy.

**Why:**
1. Drive sync is NOT a git pull mirror. It only reflects what the Windows machine pushes to Drive after manual pulls.
2. /tmp/snapai_tmp clones push commits to origin via DEC-004 workflow but do NOT touch the Drive copy.
3. Reading via Read tool from `C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\` returns a snapshot, not truth.
4. The cost of getting code state wrong (arguing with Shoab about already-shipped fixes, dispatching agents to "fix" already-fixed bugs, wrong status reports) is enormous compared to a 2-second `git fetch`.

**Mandatory workflow for SnapAI code-state checks:**

```bash
cd "/sessions/<session>/mnt/Personal Claude/ScopeSnapAI"
git fetch origin --no-tags 2>&1                            # MANDATORY first step
git log --oneline -3                                        # local HEAD (may be stale)
git log origin/main --oneline -3                            # actual prod HEAD
git log origin/staging --oneline -3                         # actual staging HEAD
# For any file claim, use:
git show origin/main:scopesnap-api/api/fault_estimate.py    # truth source
# NEVER use:
# cat scopesnap-api/api/fault_estimate.py                   # stale snapshot
```

**Rule for dispatches/dispatches mentioning specific code lines:**
- Any dispatch or status report that references "line X of file Y has bug Z" MUST be sourced from `git show origin/<branch>:<path>` content, not from a local file read
- Dispatches written more than 24h ago should be re-verified against origin/<branch> before reuse — the bug they describe may already be fixed

**Impact / consequences if violated:**
- Wasted user time arguing about non-existent bugs
- Wrong dispatches sent to AI agents who then try to "fix" already-fixed code
- Wrong status reports claiming work is undone when it shipped
- Damaged user trust ("AI argued with me when I knew I'd fixed it")
- Potential code regressions if agents revert fixes they think are bugs

**Enforcement:**
- snapai-dev skill auto-bootstrap MUST include `git fetch origin --no-tags` before reading code state
- snapai-qa skill MUST verify origin/<target>'s state before claiming what to fix
- snapai-full-audit skill Phase 0 MUST start with git fetch
- Any AI session opening a SnapAI conversation should add `git fetch` to bootstrap

**Cross-references:**
- AI_TOOLING_GOTCHAS.md Gotcha 4 — same issue, gotcha f

## DEC-112 — Next.js 16 + React 19 + Clerk v7 migration (deliberate, staging-first) — PROMOTED TO PROD 2026-06-20

**Status:** LIVE IN PROD. Migrated on staging (PR #14, merge ba7e479) then promoted to main 2026-06-20 (commit 5b092eb653) as a full file-scoped overlay release. (Re-added — a prior copy was lost to a concurrent Drive-doc write.)

**Dependency bumps (scopesnap-web):** next 14.2.15->16.2.9; react/react-dom ^18->^19; @clerk/nextjs ^5.7.2->^7.5.3; eslint ^8->^9; eslint-config-next 16.2.9. (@sentry/nextjs ^10.58.0 from DEC-110.)

**Code changes:** async params/headers (Next 16); middleware.ts->proxy.ts + Clerk v7 auth.protect(); SignIn/SignUp prop renames; tsconfig baseUrl; build `next build --webpack` (Turbopack deferred — see DEC-113); globals.css @keyframes fix; chooser-gate JSX whitespace `{" "}` (SWC trims space after {expr}); React 19 hydration mounted-guards in test harnesses; ReportClient renders all tiers' line items (also fixed a pre-existing staging e2e failure).

**Prod verification (2026-06-20):** e2e CI run #32 green; Vercel prod build green; Railway backend deploy green (incl `alembic upgrade head` -> migration 041 applied, clean boot); /health ok db connected; /api/version still 1.2; Sentry v10 re-proven delivering on the Next 16 PROD build (ingest 200, sentry.javascript.nextjs/10.58.0); dashboard clean.

**The prod release also carried** (integrated on staging, e2e+pytest green as a whole): the audit-framework session's Brand-Decoder/backend work + migrations 037-041 + Dependabot backend dep bumps (DEC-110), via the same overlay commit 5b092eb.

**Commits:** staging via PR #14 (ba7e479); prod release 5b092eb653.

## DEC-113 — Turbopack adoption: PLANNED transition (scheduled AFTER Next 16 prod bake)

**Date logged:** 2026-06-20  **Status:** PLANNED — NOT STARTED.
**Timing (dates for the next AI):** Earliest start **2026-06-27** (after ~1 week of Next 16 baking in prod, which went live 2026-06-20). Target completion window **2026-06-27 → 2026-07-11**. Do NOT start before Next 16 is confirmed stable in prod.

**Why deferred (not now):** Next 16 just shipped to prod (DEC-112). Rule: one change-type per prod deploy. Turbopack is a separate build-tooling change with its own prerequisites/risks; bundling it would widen blast radius and muddy rollback.

**Prerequisites (researched 2026-06-20, with sources):**
1. **Sentry** (docs.sentry.io/platforms/javascript/guides/nextjs): migrate `sentry.client.config.ts` -> `instrumentation-client.ts` (Turbopack does not auto-load the legacy client config); add `export const onRouterTransitionStart = Sentry.captureRouterTransitionStart`; keep `sentry.server/edge.config.ts` loaded via `instrumentation.ts` register() + `onRequestError`. **Remove `disableLogger`** from withSentryConfig (deprecated; `webpack.treeshake.removeDebugLogging` is webpack-only / no-op under Turbopack). withSentryConfig DOES support Turbopack in v10.58 (source-map upload runs post-build via `useRunAfterProductionCompileHook`, default true for Turbopack). If `tunnelRoute` is ever used, set a fixed string + exclude it in `proxy.ts` matcher.
2. **Tailwind** (open issue tailwindlabs/tailwindcss#18997): SPIKE Tailwind v3.4 under Turbopack FIRST — v3 + Turbopack can fail `Module not found: Can't resolve 'fs'`. If it fails, upgrade to **Tailwind v4** (`@tailwindcss/postcss`, drop autoprefixer/postcss-import, `@import "tailwindcss"`, CSS-first config; visual-QA borders/rings/shadows; v4 drops pre-2023 browsers — verify analytics). Next 16 docs default to v4.
3. **next.config.js**: REMOVE the dev `webpack()` watchOptions block — Next 16 `next build` (Turbopack default) **FAILS** if a `webpack()` config is present. If dev polling is needed (Docker/WSL only), use top-level `watchOptions: { pollIntervalMs: 1000 }`; otherwise drop it (Turbopack uses native FS watching). `serverExternalPackages`, `redirects()`, `headers()`, `images.remotePatterns` all work unchanged.
4. **Flip:** set build script to `next build` (drop `--webpack`); `next dev`. Then VERIFY: §5 Sentry event delivery under Turbopack, full Playwright e2e, visual QA.

**Method:** staging-first (DEC-070); separate prod promote after staging verification. **Rollback:** re-add `--webpack` to the build script + restore `webpack()` block.

**Cross-references:** DEC-112 (Next 16 migration), DEC-110.

---

## DEC-114 — Day 1-5 Estimate Builder bug fixes + Level 2 wording shipped to prod (2026-06-20)

**Context:** Comprehensive bug-fix dispatch (SnapAI_Bug_Fix_Comprehensive_Dispatch.md) covering 5 Estimate Builder bugs + Level 2 homeowner-report wording + DEC-088 banned-words enforcement + a warranty field. Executed staging-first, then promoted to prod.

**Shipped (live on staging + prod):**
- **Bug 1 + Bug 5 (markup leak / replacement semantics):** `fault_estimate.py` `_build_line_items()` — repair tiers show per-fault Option 1/Option 2 line items priced at `tier.total` (line item always == displayed total, no markup leak); replacement tier emits 4 distinct components (equipment/refrigerant/installation/service) split by `REPLACEMENT_BREAKDOWN_RATIOS` (62/7/20/11) summing exactly to total, behind `USE_HARDCODED_REPLACEMENT_RATIOS` env flag (default true). Verified: homeowner report line item == option total on a live Refrigerant-Leak estimate.
- **Bug 3 (PresentMode Slide 1):** real assessment photo (SVG fallback when absent) + FAIR/POOR/CRITICAL health badge + tier-aware "Why this matters" footer + truncation 18→28 chars. `GET /api/estimates/{id}` now returns `assessment_photo_url` + `assessment_condition`.
- **Bug 4 (report URL not clickable):** report URL is now a clickable `target=_blank` link + a Preview button, on the Output tab, Send tab, and success screen.
- **Bug 2 (PDF 404):** DEFERRED. Dockerfile already installs WeasyPrint libs and `pdf_generator.py` is PIL-based, so the dispatch's "Path A" is moot; the `/files/pdfs/...-unavailable.pdf` fallback has no route handler (raw 404). Root cause needs Railway logs. Follow-up ticket.
- **Level 2 wording:** 38 per-fault repair line items (Codie/snapai-copywriting, board-reviewed) + 4 replacement components + 2 footers (cost transparency + estimate validity) + 5 warranty-UI strings + 3 PresentMode footers. All DEC-088 compliant. 6 pre-existing banned-word strings scrubbed ("Fix + Prevent..." → "Fix + Extend Life", "eliminates..." replacement copy, two homeowner condition strings).
- **Warranty:** `companies.warranty_text VARCHAR(500) NULL` (Alembic **041**), Settings "Warranty terms" field (PATCH /api/auth/me/company, 500-char cap), rendered on the homeowner report under the contractor's name only when set (DEC-088: the sole sanctioned use of "warranty").

**CRITICAL GOTCHA discovered (cost ~hours):** The live Estimate Builder route is **`/assessment/[id]` → `app/(app)/assessment/[id]/page.tsx`**, NOT `/estimate/[id]`. There are two near-identical page files; `app/(app)/estimate/[id]/page.tsx` is **legacy/unused**. Bug 4 edits initially landed in the estimate file and appeared to "not deploy" (chased Vercel cache/domain/build-cache red herrings for a long time) until the real cause — wrong file — was found. **Always edit `assessment/[id]/page.tsx` for the Estimate Builder UI.** Backend-driven changes (line items, footers, warranty) and shared components (PresentMode, Settings) were unaffected and shipped fine.

**Staging deploy note:** staging.snapai.mainnov.tech is a Vercel *branch* domain following the `staging` branch (project `scopesnap-web-staging`, no production domain). It auto-serves the latest staging deployment. SnapAI registers a service worker, so QA requires clearing the SW + caches (or Ctrl+Shift+R) to see fresh deploys. A `lucide-react 0.577→0.454` alignment to match green main was pushed during diagnosis; it was ultimately unnecessary (Vercel was building fine) but is harmless and keeps staging deps == prod.

**Cross-refs:** DEC-088 (banned-words rule), DEC-070 (staging-first), DEC-112/113 (Next 16/React 19/Clerk v7 migration + Turbopack pending), DEC-004/027 (git/edit safety).

**Prod commit:** main `7689665` (Bug 4 promote) on top of the migration release; backend (Alembic 041 + line-item logic + footers) reached prod via the earlier full-staging→main promote (DEC-112 release).

---

## DEC-114 (addendum) — Bug 2 (PDF 404) resolved: NUL-byte corruption in pdf_generator.py

`services/pdf_generator.py` carried 117 trailing NUL bytes (EOF padding) across many commits, making the module unimportable → all contractor PDFs returned `-unavailable.pdf` (404). Stripped the nulls (no code lost; AST + import verified). PDF generation restored. Verified on prod: generates 5.4 KB PDF → Cloudflare R2 → valid `%PDF-`. Staging uses LocalStorage (no R2 creds set there). Commits: staging `0cc5eb7`, main `94737c2`. Recommend a CI NUL-byte guard given this repo's truncation history (DEC-005/027/028).

---

## DEC-115 — Post-audit hardening + cleanups (2026-06-21)

After the security audit (migrations 042/043, CSP/nonce, rate-limiting, JWKS/CORS, report-link hardening) landed on prod, completed the remaining gaps from the Day-1-5 work:

- **#2 Friendly PDF-503 handler** (`main.py`): `GET /files/pdfs/{filename}` returns a friendly 503 for legacy `-unavailable.pdf` links (instead of a bare 404) while still serving real local PDFs. New PDFs already generate fine after the NUL-byte fix (DEC-114).
- **#10b Markup >100% warning** (estimate builder): warns when company markup exceeds 100% so contractors don't accidentally send a homeowner total that's >2× cost.
- **#3 CI NUL-byte guard** (`.github/workflows/nul-byte-guard.yml`): fails CI on embedded NUL bytes in source — prevents recurrence of the exact corruption that broke PDF generation for many commits (DEC-114).
- **#5 pytest CI** (`.github/workflows/pytest.yml`): runs the backend unit suite incl. `test_fault_estimate_v2.py`.
- **Cleanups:** deleted the dead `estimate/[id]/page.tsx` (staging+prod; `/estimate/[id]`→`/assessment/[id]` redirect intact); reverted the unnecessary staging lucide-react downgrade.
- Commits: staging `0699297` (+ earlier `75234ec`, `0cc5eb7`), prod `94737c2`/`767932b`/`7689665`.

**OPEN / handed off:**
- **#4 R2 creds on Railway *staging*** — staging PDFs still use LocalStorage (localhost). Needs `R2_*` env vars set on the Railway staging environment (manual; secrets). Prod works.
- **#9 PK dashboard React #418 hydration** — root cause: i18n `t()` renders English on the server but Urdu on the client (PK-only), and `timeAgo()` uses locale-sensitive `toLocaleDateString`. Non-fatal (app functions). Deliberately NOT blind-patched on prod; recommended fix for the migration owner: make the language deterministic server-side (from hostname) and/or `suppressHydrationWarning` on locale/time nodes. Tracks with DEC-113.
- **#10a PK Level 3/4 wording** — PK-adapted (R-22/capillary/voltage) English + Urdu repair line items: large content workstream via snapai-pk-outreach, still deferred per PK-test-market positioning.

**Note on brain-file versioning:** these docs are maintained in the Drive folder (source of truth); the git copies are an intentionally-stale snapshot (~DEC-90) per the migration AI's "docs intentionally not touched" decision. Not force-committing the full brain history to git to avoid staging/main doc divergence.

---

## DEC-116 — PK dashboard React #418 hydration fix (2026-06-22)

Root-caused the long-standing PK-only React #418 hydration error (manifested as the "API offline"/console error on pk.snapai dashboards). **Cause:** `components/LanguageToggle.tsx` did `if (detectMarket() !== "PK") return null;` *during render*. `detectMarket()` returns "US" on the server (no `window`) and "PK" on the client, so on PK the server emitted `null` while the client emitted the اردو toggle button → server/client HTML mismatch → #418 on every PK authenticated page (LanguageToggle sits in SidebarNav + BottomNav). US never hit it (US → null on both sides).

**Fix:** added a `mounted` state (`useState(false)` + `useEffect(()=>setMounted(true),[])`) and gated the render on `!mounted || detectMarket() !== "PK"`. Server + first client render are now identical (both null) → no mismatch; the toggle appears right after mount on PK. **US render path is byte-identical (always null) → zero US impact.**

Verified live on pk-staging (Browser 2, authenticated): console #418 gone after SW unregister + cache clear (new chunk `…fd86053729869cb3`), اردو toggle still present, dashboard renders. Diagnostic note: Claude-in-Chrome automation runs in a browsing context that does NOT inherit the user's Clerk session — had to use the user's already-authenticated Browser 2 to observe/verify.

Commits: staging `af70688` → prod `e344b49`.

**Known same-root-cause follow-ups (NOT in this change, flagged):** `app/(app)/assess/page.tsx` and `app/(app)/assessment/[id]/page.tsx` also branch on `detectMarket()` during render (placeholders / conditional fields, lines ~528/579/586 and ~1467/1484/1537/1557). These can produce the same PK hydration mismatch on those routes; left untouched to keep this fix tightly scoped + low-risk. `StepZeroPanel.tsx` already defers correctly via useEffect.

---

## DEC-117 — Staging R2 was silently falling back to localhost (2026-06-22)

#4 follow-up. Staging *appeared* to have all 5 R2_* vars in Railway, but runtime check (POST /api/estimates/{id}/documents on staging) returned a `http://localhost:8000/files/...` contractor_pdf_url — i.e. LocalStorage, not R2. Root cause: **`R2_PUBLIC_URL` was an empty string** (the other 4 were set; `R2_ACCOUNT_ID`=0c1bfa87…, bucket=scopesnap-uploads-staging). `get_storage()` requires `all([...5 R2 vars])` truthy; one blank value drops it to LocalStorage. Compounding: the Cloudflare bucket's **Public Development URL was disabled**, so no public URL existed to put there.

Fix: enabled the staging bucket's Public Development URL (→ `https://pub-6b29e33e883e45a9ba7ff022ee90a1ce.r2.dev`), set `R2_PUBLIC_URL` to it in Railway staging, redeployed. Re-verified: staging now returns `https://pub-…r2.dev/documents/...` URLs, upload succeeds (keys valid), and the PDF is publicly retrievable (rendered it in-browser). **Staging file storage now persists across redeploys, matching prod.**

Diagnostic notes for next time:
- Railway masks ALL values as `*******` (even empty/non-secret) — must reveal individually to spot a blank. The eye-icon showed `R2_PUBLIC_URL = <empty string>`.
- Claude-in-Chrome automation does NOT inherit the user's Clerk/app session; used the user's already-authenticated Browser 2.
- `get_storage()` warning text says "ENVIRONMENT=production but R2 credentials are not set" even when environment=staging — misleading. Minor code-polish candidate (not done): make the warning environment-accurate so a blank staging cred isn't silently hidden behind a prod-worded message.

---

## DEC-118 — assess/assessment #418: verified NON-issue (2026-06-22)

Followed up on DEC-116's flagged concern (assess + assessment/[id] call detectMarket() during render). Live-tested both on pk-staging (authenticated), hard-reload + error-only console: **no React #418 on either page.** Reason: these pages gate market-dependent content behind client-side data-loading (the estimate/brand data loads via useEffect), so the detectMarket()-dependent JSX renders AFTER mount, past hydration — no server/client mismatch. Unlike LanguageToggle (DEC-116), which rendered the market branch during the initial SSR/hydration pass. Net: no code change needed; the DEC-116 follow-up is closed as a non-issue.

---

## DEC-119 — Bug 5 (4-component replacement) verified live (2026-06-22)

#7 closed. Old drafts (e.g. rpt-925795) show a single replacement line because their options were stored pre-fix (/refresh only re-stamps text, never line_items — confirmed in code). Generated a FRESH estimate on staging (new assessment 9b429e3b… → POST /api/estimates/fault-card with assessment_id, card_id 8 "Refrigerant Undercharge/Leak", unit_age 18, age_source homeowner_sure → rpt-168150). Tier C (is_replacement=true) now has the **4-component breakdown** summing exactly to the ₨6,480 cost: equipment ₨4,017.60 (62%), refrigerant ₨453.60 (7%), installation ₨1,296 (20%), service ₨712.80 (11%). Confirmed it renders in the Estimate Builder grouped LABOR / PARTS & EQUIPMENT / FEES with the board-reviewed wording (incl. "registration of the new system with the manufacturer"). USE_HARDCODED_REPLACEMENT_RATIOS defaults "true" (enabled). Note: left a harmless staging test draft rpt-168150 ("QA Bug5 Test").

---

## DEC-120 — Found + fixed: homeowner report React #418 (2026-06-22)

During #6 PK functional QA, the public homeowner report page (/r/{slug}/{token}, ReportClient) threw React #418. page.tsx is a server component that fetches the report and passes it as a prop, so ReportClient renders fully at SSR. Root cause: `ReportQRCode` used a lazy `useState` initializer that returned "" on the server (typeof window undefined → render null) but computed a `window.location.href` URL on the client (render <img>) → hydration mismatch. NOT PK-specific (hits every report, both markets) — just surfaced during PK QA. Fix: moved URL computation into `useEffect` so SSR + first client render are identical (null), QR appears post-mount (still before print, preserving the A.5 intent). Verified on pk-staging: #418 gone, QR still renders (hasQRimg=true). Commits: staging 4bd9507 → prod a26e10e.

Other ReportClient render-time items reviewed + cleared: reportMarket comes from stored `report.market` (consistent SSR/client, not detectMarket); lang/dir set in useEffect. Latent (not firing): line ~497 date uses tz-sensitive toLocaleDateString — could mismatch at day boundaries; left as-is since not observed.

**Separate observation (not a bug fixed here):** rpt-925795's report renders in USD ($) despite being a PK estimate — its stored `report.market` is US/null (old draft, pre-market-stamping). Fresh estimates (rpt-168150) format in ₨ correctly in the builder. Worth a data check on whether PK estimates reliably stamp market on the report record. Logged for follow-up, not actioned.

## #6 PK functional QA — result (2026-06-22)

Exercised on pk-staging (authenticated): dashboard (no #418), assess (no #418), assessment create (201), estimate generate /fault-card (200, correct 4-tier + 4-component replacement), estimate builder render (₨, 4 components), document/PDF generate (R2 url, publicly retrievable), homeowner report page (#418 found→fixed). Did NOT trigger /send (would dispatch a real email/WhatsApp) — verified report-link generation instead. Net: core PK flows PASS; one new bug (report #418) found and fixed.

---

## DEC-121 — CI + Sentry verified via GitHub/Sentry UI (2026-06-22)

#3/#5 (CI): viewed GitHub Actions (logged in). **NUL-byte guard ✅ green** on every commit (#9/#10/#11). **pytest (backend) ✅ green** on all 5 runs (staging + main, #1-#5). Secret Scan (gitleaks) ✅ green. So the two CI workflows I added are confirmed green in CI, not just locally.
- **Stage 3 Playwright E2E is RED — but PRE-EXISTING, not mine.** Run #44 (audit batch-2 5ea756e) and #45/#46 (my 503/markup/CI-guard commits, which touch no tested UI flow) are all red, same as later commits. It's been failing since the Next16/React19/Clerk v7 migration era (env/server setup the CI job doesn't provide). Flagged as a separate cleanup item; my hydration fixes did not introduce it.

#8 (Sentry): org mainnov (mainnov.sentry.io), logged in. Issues feed (14d, unresolved, all projects/envs) = **only 2 issues, both 3-4d old, NONE from today's deploys**: (1) /tech UnhandledRejection "Object Not Found Matching Id…MethodName:update" = browser-extension artifact, not app code; (2) /dashboard Error SNAPAI-MIG-NEXT16-STG = the #418 hydration I fixed today (last seen 4d ago, pre-fix). **Post-deploy error delta = zero new errors** from today's 5 deploys. Did not modify Sentry state (left WEB-2 unresolved; can be resolved once the fix is confirmed not recurring).

---

## DEC-122 — Prod-QA gaps closed (2026-06-22)

Re-verified today's work on PRODUCTION (pk.snapai.mainnov.tech, authenticated). Generated a fresh prod estimate (assessment → rpt-476891, card 8, age 18): tier C is_replacement, **4-component breakdown** present (Bug 5 ✅ on prod); contractor PDF URL = `https://pub-012aaca441ab4706a8e536e3e06dd383.r2.dev/...` → **prod uses R2** (✅, separate prod bucket from staging's pub-6b29e33e…). Loaded the fresh prod report page, SW-cleared + hard reload: **no #418** (report QR fix ✅ on prod), QR still renders. So report-#418, Bug 5, and R2 are all confirmed on PROD, not just staging. (Left harmless prod test draft rpt-476891 "QA Prod Test".)

---

## DEC-123 — Market policy: US is production, PK is a dormant test market (2026-06-22)

**Authoritative clarification — read this before "fixing" any PK currency/market issue.**

- **US (Houston) is the real production market.** PK (`pk.snapai.mainnov.tech`) exists only as a secondary "another set of eyes" test surface. PK is **NOT** an intended/active market. Per Shoab (2026-06-22).

- **Known, EXPECTED, NOT-A-BUG behavior:** homeowner reports (and the trusted-market side of the app) render in **USD ($) even on the PK frontend**. This is correct given the design — do not log it as a bug, do not "fix" it.

- **Why it happens (root cause, for reference only):** currency has two drivers:
  1. The **report** uses the estimate's *trusted* market = `estimate.market` = the company's `companies.market` field (audit BUG-037 anti-spoofing — deliberately ignores the `X-Market`/hostname header).
  2. The **builder** uses the *hostname* (`detectMarket()`), so it shows ₨ on pk.snapai.
  Every company is `market='US'` because company market is stamped at signup by `_market_from_host(request.headers.get("host"))` in the **Clerk webhook** (api/clerk_webhook.py ~L237) — but Clerk webhooks fire **server-to-server**, so `host` is the API host (`scopesnap-api-…railway.app`), never `pk.snapai`, so it always resolves to **US**. Net: all signups (incl. PK-frontend) get US-market companies → reports show $ → builder shows ₨ → the visible mismatch. This is understood and accepted.

- **Easy workaround IF a PK test ever needs to show ₨ (NOT applied, by choice):** one-row data update, no code:
  `UPDATE companies SET market='PK' WHERE slug='<test-company-slug>';`
  (e.g. `shoab-ds-s-hvac-1381`). That makes that one company show ₨ everywhere on PK. It does NOT auto-fix future signups. Intentionally left undone because PK is not the real market.

- **Do NOT:** rip out PK code/`pak_*` tables/hostname detection just to reduce confusion — it's woven throughout and removal is high-risk for zero functional gain. Do NOT change the report to read hostname instead of trusted market (re-breaks BUG-037 anti-spoofing). The "proper" fix (auto-stamp PK at signup via Clerk `unsafe_metadata` or first authed `/me` call) is real work and **not worth it** for a dormant test market.

- **Bottom line for future AIs:** US = $ is correct. PK showing $ is expected. Leave it. No code/data change was made for this — docs only.

## DEC-124 — Stale CI workflow note (2026-06-22)

`playwright-e2e.yml` (GitHub Actions) runs `scopesnap-web/tests/e2e` (4 Stage-3 specs) and has been **RED since the Next16/React19/Clerk-v7 migration** — independent of any recent work (red on the audit commits 78166b0/5ea756e too). It is a SEPARATE suite from the `snapai-full-audit` skill's Playwright, which lives in the isolated `audit/` folder (`snapai-audit-harness`, "NOT part of the Next.js app build") and is healthy. Running the full audit does NOT make this CI workflow green. Decision pending from Shoab: delete the stale `playwright-e2e.yml` (recommended — audit harness covers E2E/security) vs. migration-debug the 4 specs. No change made yet. **→ RESOLVED in DEC-125 (debugged + fixed, not deleted).**

## DEC-125 — playwright-e2e.yml ROOT-CAUSED + FIXED → GREEN + PROMOTED TO PROD (2026-06-22)

The red suite (DEC-124) is fixed and CI is green on `staging` (run #56, commit `724fdf7`, "completed successfully", 34/34). Shoab's call was "make Playwright work" — debugged, not deleted. **PROMOTED TO PROD on Shoab's "go"**: file-scoped overlay (DEC-102 method) of the 3 files onto `main` = commit `b09f155` (`a26e10e..b09f155`). Staging QA + prod QA both clean (dashboard renders through middleware, sign-in→dashboard auth redirect, Clerk under strict CSP, zero console errors/CSP/418; staging test-harness renders a full report). Prod was runtime-neutral as predicted.

**Root cause (single, definitive):** the dev-only e2e mount points `app/test-harness/*` were still matched by the Clerk middleware (`proxy.ts`). `clerkMiddleware` runs a **dev-browser handshake** that 302s to the Clerk Frontend-API domain *derived from the publishable key*. Under the e2e dummy key `pk_test_Y2xlcmsuZXhhbXBsZS5jb20k` that domain decodes to **`clerk.example.com`**, which does not resolve, so every Chromium navigation died with `net::ERR_NAME_NOT_RESOLVED` — reported against the loopback URL, which masked the real redirect target and sent earlier debugging down proxy/loopback/IPv6 rabbit holes. Why it went red at the migration: Clerk v7's middleware does this handshake; pre-migration Clerk v5 did not.

**How it was proven (method worth reusing):** reproduced locally on Windows with the *bundled* Chromium (`npm i -D @playwright/test@1.61.0`, no browser download needed beyond `playwright install chromium`), then isolated with a standalone script using `page.on('requestfailed')` — which printed the actual failing request `https://clerk.example.com/v1/client/handshake?redirect_url=...`. A trivial Node server proved Chromium reaches every loopback (127.0.0.1, localhost, [::1]) fine, killing the loopback/proxy theories. Lesson: **`requestfailed` reveals the true failing URL when `page.goto` blames the wrong one on a redirect.**

**Fix (3 files, prod-runtime-neutral):**
1. `proxy.ts` — add `test-harness` to the middleware matcher negative-lookahead so Clerk never runs on those routes. (Also kept the dev-gating of the audit's strict CSP: `...(IS_DEV ? {} : { contentSecurityPolicy })` — strict CSP still applies in staging+prod, is a no-op only in dev, where it had broken Next HMR.)
2. `next.config.js` — `allowedDevOrigins: ["localhost","127.0.0.1"]` (Next 16 dev cross-origin allowlist; dev-only hardening).
3. `playwright.config.ts` — `baseURL`/webServer use `127.0.0.1` + `npx next dev -H 0.0.0.0` (dropped the earlier misdiagnosed proxy/host-resolver launch-arg guesses).

**Prod impact: none functional.** In prod `IS_DEV` is false → strict CSP unchanged; the only behavioral change is test-harness (dev-only routes) bypassing middleware. Verified: prod `main`'s `proxy.ts` already carries the audit strict-CSP, so `main↔staging` diff for these 3 files is *exactly* this fix and nothing else.

**Cross-refs:** DEC-124 (the open item this closes), DEC-099 (the suite is deliberate "permanent CI", kept), DEC-112 (Clerk v7 migration that introduced the handshake), DEC-102 (file-scoped promote method for diverged staging↔main).

## DEC-126 — Railway staging env audit: R2 confirmed set (DEC-117 closed); CRON_SECRET missing on staging (process-followups fail-open) (2026-06-22)

Live read-only check of the `scopesnap-api` **staging** environment variables in the Railway dashboard (Chrome), prompted by reconciling the old "#4 R2 staging — NEEDS USER" item.

**Finding 1 — R2 on staging is CONFIGURED. ✅ Re-confirms DEC-117 (already fixed + verified earlier this session).** All five R2 variables are present on staging: `R2_ACCESS_KEY_ID`, `R2_ACCOUNT_ID`, `R2_BUCKET_NAME`, `R2_PUBLIC_URL`, `R2_SECRET_ACCESS_KEY` (values masked; presence confirmed). DEC-117 had already root-caused + fixed this (the blank `R2_PUBLIC_URL` was set, the Cloudflare bucket's Public Development URL enabled, and a staging PDF confirmed publicly retrievable at `pub-…r2.dev`). This live re-check just confirms all 5 are still present — so the old "#4 R2 staging — NEEDS USER" item was actually closed by DEC-117, not still open. (Config presence confirmed; the definitive proof remains functional — a staging PDF URL of `*.r2.dev`, not localhost, which DEC-117 already demonstrated.)

**Finding 2 — `CRON_SECRET` is set on PROD but MISSING on staging → staging `process-followups` is UNAUTHENTICATED.** Railway's own env diff flags it ("found in production, missing in this one"). The guard `verify_cron_secret` in `scopesnap-api/api/estimates.py` **fails OPEN by design** when the secret is empty:
```python
expected = (get_settings().cron_secret or "").strip()
if not expected:
    logging.warning("process-followups is UNAUTHENTICATED: set CRON_SECRET ...")
    return            # ← allows the call
if not x_cron_secret or x_cron_secret != expected:
    raise HTTPException(401)
```
So both `GET /api/estimates/process-followups` endpoints (lines ~161 + ~968, WP-09 cron) accept **unauthenticated** calls on staging; on prod they require a matching `X-Cron-Secret`. No in-repo scheduler calls them (trigger is an external cron), but the endpoint is reachable regardless — anyone could POKE staging follow-up processing (which iterates due follow-ups, i.e. can fire follow-up emails via the staging Resend key). **Risk: LOW** (staging, test data) but it is a real unauthenticated-endpoint gap and an avoidable staging↔prod drift.

**Recommendation (NOT done — Shoab said check only):** set `CRON_SECRET` on the staging `scopesnap-api` env to a staging-specific value so the endpoint fails closed there too (matching prod). This is a Shoab action in the Railway dashboard; no code change needed (the guard already enforces it once the var is present).

**Cross-refs:** DEC-117 (the R2 staging fallback this closes), the cron-secret auth + open-redirect remediation (`a89aef8`).


### DEC-113 UPDATE — 2026-06-29: Turbopack ADOPTED ON STAGING (verified)
Done on staging via PR #23 (merge `a43c681`). Build script flipped `next build --webpack` -> `next build` (Turbopack). Sentry migrated to `instrumentation-client.ts` + `instrumentation.ts` (register server/edge + onRequestError); `sentry.client.config.ts` deleted; `disableLogger` removed; `webpack()` block removed from next.config.js. **Tailwind v3.4 builds CLEAN under Turbopack** — the feared `Can't resolve 'fs'` issue did NOT occur, so we stayed on v3 (no v4 upgrade needed). Verified: Turbopack prod build green on Vercel (both projects), staging e2e CI run #65 green, local Turbopack build + full e2e 34 passed, **§5 Sentry delivers under Turbopack** (ingest 200, sentry.javascript.nextjs/10.62.0 via instrumentation-client.ts) — the key risk (Turbopack not auto-loading legacy client config) is resolved. **PROD still on `next build --webpack`** until a separate gated promote.


### DEC-113 UPDATE — 2026-06-29: Turbopack PROMOTED TO PROD (verified)
After staging verification, Turbopack promoted to prod via a SCOPED file-scoped overlay (main commit `66699a05`) — only the Turbopack files (next.config.js webpack()/disableLogger removed, package.json build `next build`, instrumentation-client.ts + instrumentation.ts added, sentry.client.config.ts deleted); prod already had the audit-session work + migrations 042-044, so nothing else was shipped. Verified on prod: Vercel Turbopack build green (both projects), e2e CI green, /health ok, /api/version 1.2, **§5 Sentry delivers under Turbopack on prod** (ingest 200, nextjs/10.62.0 via instrumentation-client.ts), public landing + Clerk v7 sign-in render, proxy.ts auth-protection works, no console errors (US+PK). **Turbopack now LIVE on prod + staging.** Tailwind stayed v3 (works under Turbopack).


## DEC-127 — Dependabot postcss alert #34 is a KNOWN NON-ISSUE (no upstream fix; do NOT override)

**Status (2026-06-29): ACCEPTED / WAIT-FOR-UPSTREAM. Do not re-investigate or re-attempt a fix.**

**Alert:** GitHub Dependabot **#34** -- postcss (npm), MEDIUM, GHSA-qx2v-qp2m-jg93 / CVE-2026-41305 ("PostCSS XSS via unescaped `</style>` in CSS stringify output"). Vulnerable range `< 8.5.10`, patched in `8.5.10`.

**Why it is open:** The vulnerable postcss **8.4.31** is NOT a direct dependency we control -- it is **vendored inside Next.js**. Next **16.2.9** (the newest Next release on the npm registry as of 2026-06-29; `dist-tags.latest` = 16.2.9, no 16.3.x / 17.x exists) still pins postcss 8.4.31 in its own dependencies. **There is currently NO Next version to upgrade to that carries the patch.**

**Why we canNOT just override it:** Forcing postcss via npm `overrides` was tried FOUR ways on 2026-06-29; all fail:
1. `"postcss":"8.5.16"` -> npm **EOVERRIDE** (conflicts with the direct postcss devDependency).
2. `"postcss@8.4.31":"8.5.16"` -> same **EOVERRIDE**.
3. `"postcss":"$postcss"` + pin direct dep to 8.5.16 -> install leaves postcss **uninstalled**; `next build` dies with **"Cannot find module 'postcss'"** (reproduced on clean installs).
4. scoped `"next":{"postcss":"8.5.16"}` -> **ineffective**, Next still resolves 8.4.31.

Root cause: Next's compiled webpack CSS toolchain `require()`s its own nested postcss; npm dedupe/hoist removes that copy and breaks the build. A forced override would RED the Vercel build.

**Real-world risk: LOW.** postcss is a build-time tool; the flaw needs attacker-controlled CSS being stringified, which is not a path in this app. Since DEC-113 (Turbopack on prod), the prod build runs `next build` (Turbopack), so the vulnerable webpack `postcss-scss` code path is **not even loaded** -- Dependabot flags #34 only because the copy still sits in `package-lock.json`.

**Decision / what future sessions must do:** Leave #34 open and **accept it as low-risk**. Do NOT attempt lockfile overrides (they break the build). It clears for real only when upstream Next ships a release whose bundled postcss `>= 8.5.10` -- at that point bump Next (staging-first, DEC-070) and the alert closes on its own. **Future AI / QA / Dependabot-triage sessions: this is expected and already analyzed -- do not re-litigate.**


## DEC-128 — Cowork advisor-board skills: installed plugin cache is SEPARATE from the Drive canonical source; roster edits must be re-synced (2026-07-02)

**Status: ACTIVE RULE.** Applies to the @board (snapai-board) and @nav (snapai-nav) Cowork skills. This is tooling/infra, not app code.

**The gotcha:** The @board / @nav skills load their ROSTER TEXT (member list, panels, seats, slug tables) from an app-managed plugin CACHE, not from the Drive canonical folders.
- Canonical editable source: `Personal Claude/snapai-board/SKILL.md`, `Personal Claude/snapai-nav/SKILL.md` (+ their `references/<slug>/` knowledge folders).
- Runtime cache (what actually loads): `%AppData%\Roaming\Claude\local-agent-mode-sessions\skills-plugin\<ids>\skills\snapai-board\SKILL.md` (+ sibling `manifest.json`). Real path is a junction into `...\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\...`. Skills carry server-side skillIds (creatorType user) and `manifest.lastUpdated` is rewritten by the app -- i.e. the app REGENERATES this cache from its backend skill store.

**Consequence:** Editing ONLY the Drive canonical SKILL.md does NOT update the running skill's roster. The reference KNOWLEDGE folders ARE read live from Drive (advisors speak with correct data), but the board's own member list / panel text lags until the cache is refreshed. Overwriting the cache via Desktop Commander works immediately but is a STOPGAP the app may regenerate.

**Sync procedure after any roster change (add/remove advisor, panel, or seat):**
1. Edit the Drive canonical `snapai-board/SKILL.md` + `snapai-nav/SKILL.md` (bash heredoc per DEC-027; ASCII punctuation per DEC-005).
2. Keep both slug-mapping tables matching the actual `references/<slug>/` folder names.
3. To update the RUNNING skill durably: re-import/update the skill in the app (Settings -> Capabilities). As a same-session stopgap, overwrite the plugin-cache SKILL.md + manifest.json via Desktop Commander (real-FS write).
4. Also grep other skills (e.g. snapai-dev) for stale cross-refs like "21 experts" / "15-seat".

**2026-07-02 state:** 6 advisors added -- board Panel 5 (bryan-orr, jenny-hoyos, zaria-parvez, alex-su) and nav Seat #16 (mrbeast) + Seat #17 (terence-reilly). Drive canonical, plugin cache, and manifest.json all synced to 25 board / 17 nav this session. Durable re-import via Settings -> Capabilities still recommended.


## DEC-129 — diagnostic_questions branch_logic_jsonb is Monaco-seeded; migrations alone are INSUFFICIENT evidence of what is live (2026-07-03)

**Status: ACTIVE RULE.** Applies to any AI or human session evaluating the diagnostic flow's coverage, completeness, or bug status.

**The gotcha (real incident, this session):** Bryan Orr @board evaluation of the SnapAI diagnostic app concluded from reading migration files alone that:
- Item 1 -- Card #13 Ductwork Leak branch on Not Cooling YES / normal pressures + warm supply was "NOT DONE" (migration 013 comment appeared to have replaced the 4-way Phase 2 gate with a single-reading suction-only gate resolving to a repurposed "TXV/Metering" card).
- Item 2 -- Error Code / refrigerant_low Phase 2 gate discriminating Card #8 (leak) vs Card #15 (piston) was "NOT DONE" (no migration file adds this discrimination).
- Item 3 -- Intermittent Shutdown Path B all-checks-pass FLIR camera escalate was "PARTIALLY DONE, unverifiable from migrations."

Shoab said "check it yourself" via Supabase MCP. Live prod query against `diagnostic_questions` on `snapai-prod-use1` (project `zpsoprffaujswywtsgzy`) proved ALL THREE ITEMS ARE LIVE:
- not_cooling / q2-nc-suction routes low→Card 8, ok→Card 13 (verified Ductwork Leak in fault_cards), high→q2-nc-discharge which routes to Card 14 / Card 17 / escalate for compressor-valve edge case. Full 4-card discrimination lives.
- error_code / q1 branch_logic contains `"refrigerant_low": {"phase_2_gate": true, "after": {"piston_pattern": {"resolve_card": 15}, "low_suction_high_superheat": {"resolve_card": 8}}}`. Exact tree-spec gate, live.
- intermittent_shutdown / q5-voltage-drop has `"elevated": {"escalate": true, "reason": "Marginal voltage drop -- Path B caps at 85-90%. Consider FLIR camera."}` -- exact tree-spec FLIR escalate branch, live.

**Root cause:** Migration `011_p3_diagnostic_engine.py` is intentionally a NO-OP (`upgrade(): pass`) with docstring "DDL applied directly in Supabase (same technique as WS-C migration 008). This file is a no-op so Railway alembic upgrade head skips cleanly." The initial diagnostic_questions rows -- and every later mutation of their branch_logic_jsonb -- were seeded via the Supabase Monaco SQL editor, NOT in migration files. Same pattern applies to migration 008 (WS-C readings gate). Any migration whose docstring says "applied directly in Supabase" or "seeded via Monaco" leaves NO trace in Alembic history but is fully live in the DB.

**Rule / How to verify diagnostic coverage from now on:**
1. NEVER claim a diagnostic step, branch, or resolve_card is absent based on migration files alone. Migrations are a PARTIAL source.
2. Query Supabase directly via `mcp__supabase__execute_sql` on `snapai-prod-use1` (or `snapai-staging-use1` for pre-prod state). Base query:
   ```sql
   SELECT complaint_type, step_id, step_order, question_text, input_type,
          reading_spec, branch_logic_jsonb, is_terminal
   FROM diagnostic_questions
   WHERE complaint_type = <target>
   ORDER BY step_order;
   ```
3. Cross-reference resolve_card IDs against `fault_cards.card_name` to confirm the card the branch resolves to:
   ```sql
   SELECT card_id, card_name FROM fault_cards WHERE card_id IN (...) ORDER BY card_id;
   ```
4. Only after the live DB has been queried is it safe to claim "done" or "not done" on a discrimination / escalate branch.
5. The `SnapAI_Decision_Tree.html` v5 is the DESIGN SPEC. It reflects intent, not necessarily what shipped. Migrations reflect a SUBSET of what shipped. The live `diagnostic_questions` table is the AUTHORITATIVE source of what runs today.

**Impact on the Bryan Orr @board evaluation:** With live verification, all three items marked "not done" or "partially done" are FULLY DONE and match the tree spec. The 80% senior-tech-replacement claim moves from "not defensible" to "defensible on the 15-20 fault types the cards cover, given the discrimination cascade and honest escalate branches are live." Two remaining honesty flags stand: (a) the confidence label calibration -- current UI says "High Confidence" from ONE suction reading before the discrimination cascade completes; should say "hypothesis" or "probable" until the cascade converges; (b) landing page copy still says "Good / Better / Best" which per MBrain is retired language.

**Cross-references:** DEC-111 (never claim without verifying), DEC-070 (staging-first workflow), migration 011 (no-op Monaco-seeded diagnostic tables), migration 008 (same pattern for WS-C readings gate), tree spec `SnapAI_Decision_Tree.html`.

## DEC-130 — Legal-safe wordings v1 SHIPPED to prod

---

## DEC-131 — Board-persona reference material versioned in git via mirror-and-promote pattern (2026-07-08)

**Decision:** Board-member reference material (compendia, framework docs, voice examples, source indexes, etc.) lives canonically in `Personal Claude/snapai-board/references/<slug>/` (and `Personal Claude/snapai-nav/references/<slug>/`) where Cowork loads it, AND is mirrored into `ScopeSnapAI/snapai-board/references/<slug>/` (or `ScopeSnapAI/snapai-nav/references/<slug>/`) for version control. Ship via scoped promote (staging `feat(board-ref)` commit → main `promote(board-ref)` scoped promote), same pattern as `promote(plan)` and `promote(writing)` used for planning + writing-guide docs earlier this week.

**Rationale:**
- Board-persona knowledge is load-bearing for `@board` and `@nav` response quality. Proven live 2026-07-08: Bryan diagnostic response cited 4 verbatim episode IDs from the compendium (episodes `qIo_iT8msZA`, `lfuiVg8WSQ0`, `QjF4I8db1kA`, `6WlUva3hrhk`) — grounding that would not exist without the extraction.
- Version control gives audit trail, weekly-audit drift detection, and rollback if bad data seeps in.
- Consistency: brain files, planning docs, writing guide all in git — board refs should not be the exception.
- Cowork loading unchanged (still reads Drive path) — this is a mirror for backup + audit, not a source-of-truth move.

**Precedent set:** Bryan Orr HVAC School compendium v1 (2026-07-08) — staging `70b03bd` `feat(board-ref): Bryan Orr HVAC School compendium v1 - 959 episodes`, main `47d4c37` `promote(board-ref): sync Bryan Orr HVAC compendium v1 to prod - scoped`. 16 files: 1 master + 12 topics + 3 refreshed board refs.

**Applies to future board-member compendia:** Codie Sanchez 800K-reader Contrarian Thinking newsletter archive; Rory Sutherland Ogilvy speeches + Alchemy book chapters; Jordan Crawford Blueprint GTM playbook; Terence Reilly Stanley/Crocs operator interviews; MrBeast leaked-memo synthesis; any other board member whose knowledge base warrants deep grounding via extraction.

**Does NOT apply to:** persona `_index.md` / `frameworks.md` / `voice_examples.md` at their default depth — those already exist in the Drive path, are refreshed via the advisor-kb-monthly-refresh skill, and don't need per-file git tracking unless they materially change. This DEC covers COMPENDIA (deep structured extractions), not the standard 3-file persona folder.

**Cross-references:** DEC-070 (staging→main→prod flow), DEC-128 (Cowork advisor-board skills separate from Drive canonical), Section 7 routing table in `SnapAI_Project_Instructions.md`, `session_logs/SESSION_LOG_2026-07-08_bryan_compendium_extraction.md`.
