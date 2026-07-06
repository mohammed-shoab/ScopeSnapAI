# SnapAI — Project Brain

**Current state (2026-07-06):** SnapAI is a Next.js/Vercel + FastAPI/Railway HVAC diagnostic + estimate web app, live in prod at snapai.mainnov.tech (US) and pk.snapai.mainnov.tech (PK, dormant per DEC-123). Backend Alembic head 034. Latest DEC-130 (legal-safe-wordings v1 shipped 2026-07-06). Stack on Turbopack (DEC-113), Next 16 / React 19 / Clerk v7, Sentry v10, PostHog. Beta with first 10 Houston contractor testers. Historical build narrative → `PROJECT_BRAIN_HISTORY.md`.

## CRITICAL RULES (read before every task)

### Code + Deployment
| Rule | Reference |
|---|---|
| Never edit `main` directly — all changes via staging → main → prod | DEC-070 |
| No future-tense outcome promises in homeowner-facing copy | DEC-088 |
| PK is dormant test market; US is production | DEC-123 |
| `diagnostic_questions` is Monaco-seeded — verify against live Supabase, not migrations | DEC-129 |
| Never claim a fault card or capability is live without live Supabase verification | Mark's rule 2026-07-05 |

### Product Scope + Identity
| Rule | Reference |
|---|---|
| Card #21 Heat Exchanger + Combustion Safety Check PERMANENTLY EXCLUDED (structural, not a hold) | Alfred + Bryan 2026-07-06 |
| All SnapAI outputs are decision-support, never certified diagnosis | Legal chat 2026-07-05 |
| No CO / HX / combustion safety in scope — will never build | Alfred 2026-07-06 |
| Transcripts + photos + readings only — no audio, no STT | User standing rule |
| Card #24 Manual J gate ENFORCED IN CODE (server-side) | ALFRED C1 |
| Layer 4 + Layer 5 disclaimers render on every [A!] surface | ALFRED C2 |
| Homeowner conclusions attributed to [Company], never the app | ALFRED C3 |

### AI Behavior + File Placement
| Rule | Reference |
|---|---|
| Boards persist without invocation in SnapAI chats (@board + @nav standing) | User rule 2026-06-29 |
| Marketing docs under `Personal Claude/marketing/`, never Personal Claude root | User rule 2026-07-01 |
| For any SnapAI marketing task, read `marketing/MBrain/README.md` FIRST | User rule 2026-07-01 |
| Never name Houston or any city in public-facing copy | User rule 2026-07-06 |

---

## Change Workflow (added 2026-05-23 — DEC-070)

**Every code, schema, env-var, or infra change uses the staging-first workflow defined in `WORKFLOW.md`.** The flow is: branch off `staging` → merge to `staging` → auto-deploys to staging.snapai.mainnov.tech + pk-staging.snapai.mainnov.tech → verify → run `scripts/promote-to-prod.sh <files>` → main updates → prod auto-deploys → verify on real domain.

**The four absolute rules (codified in DEC-070):**
1. Never edit code directly on `main` without going through `staging` first
2. Never push migrations to prod that haven't run on staging first
3. Never add env vars to prod without mirroring them on staging
4. Never test on production — testing happens on staging

**Activation status:** ACTIVE (Stage 7 signed off 2026-05-24). All gaps resolved: Alembic 034 on both envs (Stage 5), Vercel staging domains serve `staging` branch (DEC-080, Stage 6), Houston full E2E QA PASS on staging (Stage 7), PK staging backend PASS (Stage 7). DEC-070 is now mandatory — no direct edits to main, no prod testing.

For full protocol — migration handling, env var handling, hotfix path, rollback procedure, AI session bootstrap, worked examples — read `C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI\WORKFLOW.md` in full before any change work.

---

## Staging Mirror Effort -- Closing Summary (2026-05-24)

The 8-stage staging-mirror effort is COMPLETE. All stages signed off. DEC-070 ACTIVE.

Reference document: `C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI\STAGING_MIRROR_CLOSEOUT.md`

What was accomplished:
- Stage 1: Production live-verify (all 6 flows PASS, BUG-040 + BUG-041 fixed)
- Stage 2: Free-tier cost audit ($5/mo confirmed, budget alerts set)
- Stage 3: Google Maps integration live (CSP + SW passthrough fixes, DEC-078/DEC-079)
- Stage 4: Staging isolation audit (2 critical cross-contaminations found and fixed)
- Stage 5: Staging DB + branch parity (Alembic 034, 15 ref tables synced)
- Stage 6: Vercel staging branch rewire (DEC-080, domain-level gitBranch, DEC-067 superseded)
- Stage 7: Staging E2E QA (Houston full flow PASS, PK backend PASS, DEC-070 activated)
- Stage 8: Final documentation (this entry + STAGING_MIRROR_CLOSEOUT.md)

---

## Critical Rules (Hard-Won — 2026-05-20)

> Full details in TECH_STACK.md WA-9 through WA-14. Read before starting new work.

## Canonical PSI Threshold Table (authoritative — Phase 2 updated 2026-05-24)

| Refrigerant | Market | Suction Normal (PSI) | Suction High Threshold | Discharge Normal (PSI) | Discharge High Threshold |
|-------------|--------|----------------------|------------------------|------------------------|--------------------------|
| R-410A      | US     | 115 – 140            | >= 141                 | 225 – 275              | >= 276                   |
| R-22        | US     | 55 – 78              | >= 79                  | 150 – 275              | >= 276                   |
| R-32        | US/PK  | 110 – 145            | >= 146                 | 225 – 290              | >= 291                   |
| R-410A      | PK     | operating_targets (dynamic lookup by ambient_c — market='PK') ||
| R-22        | PK     | operating_targets (dynamic lookup by ambient_c — market='PK') ||

> Source of truth: `operating_targets` table (dynamic lookup, both markets) + Alembic 036 migration. Static dicts `_FALLBACK_SUCTION`/`_FALLBACK_DISCHARGE` in diagnostic.py are belt-and-suspenders only.
> Do NOT use pre-035 DB values or Stage 7 QA report numbers (45 PSI was a low test value).
> At 95 degrees F outdoor ambient, R-410A suction normal is 115-140 PSI.


| Rule | One-liner | Where |
|------|-----------|-------|
| Dependabot postcss alert #34 = KNOWN NON-ISSUE, do NOT re-investigate | postcss 8.4.31 is vendored inside Next.js 16.2.9 (newest release, still ships it) -- nothing to upgrade to yet. All lockfile overrides break the build (proven 2026-06-29). Prod build is Turbopack so the vulnerable webpack postcss-scss path isn't even loaded. Build-time only, needs attacker-controlled CSS. ACCEPT as low-risk; wait for an upstream Next release bundling postcss >=8.5.10, then bump. Do NOT attempt overrides. | DEC-127 |
| apiFetch needs explicit token | `apiFetch` never auto-injects JWT. Pass `token: await getToken()` on every call. Fire-and-forget: wrap in `getToken().then()`. | WA-9, DEC-030 |
| No Edit tool on Unicode files | Edit tool truncates NTFS files at non-ASCII chars. Use Python replace() in /tmp clone. | WA-10, DEC-027 |
| Task done ≠ code written | Grep `@router.` count before closing any backend track. | WA-11, DEC-031 |
| NameError inside try/except | Silently disables the feature. Grep for import + call both present. | WA-12, DEC-034 |
| fault_cards PK is card_id | Never use fc.id. Always fc.card_id in JOINs and WHERE. | DEC-033 |
| estimate/[id] is dead code | Real builder = assessment/[id]/page.tsx | DEC-032 |
| Vercel = client-rendered | Use javascript_tool + document.querySelector(), not get_page_text. | WA-13 |
| safe.directory on /tmp clone | `git config --global --add safe.directory /tmp/snapai_tmpN` after every clone. | WA-14 |
| alembic_version ≠ schema truth | `alembic_version=032` does NOT mean col from 031 exists. Verify with `information_schema.columns`. | DEC-043, WA-17 |
| Python write can truncate tail | After every `.py` patch: `python3 -c "ast.parse(open(f).read())"` + `wc -l`. Silent truncation = SyntaxError on Railway. | DEC-044, WA-19 |
| Railway Online ≠ healthy | Service shows Online while crash-looping on SyntaxError. Only `{"status":"ok"}` from `/health` counts. | DEC-045 |
| Clerk session is cross-domain | Login on `snapai.mainnov.tech` also logs in `pk.snapai.mainnov.tech`. One login covers both markets. | DEC-047 |
| Claude tab group resets | New conversation = new tab group = no cookies. User must re-login in Claude's Chrome window. | DEC-048 |
| Estimate tiers are A/B/C | `fault_estimate.py` stores tier as "A"/"B"/"C". `reports.py` approve accepts both. `pak_pricing_tiers.tier` uses good/better/best. These are DIFFERENT naming schemes — never conflate them. | DEC-049 |
| NEVER set NEXT_PUBLIC_ENV=staging on production Vercel | StagingBanner shows on prod (BUG-031). Fix via Vercel dashboard — no code change. | DEC-023 |
| ServiceChecklist ≠ DiagnosticFlow | Service/Tune-Up renders ServiceChecklist.tsx. UI features in DiagnosticFlow are silently absent for service flows. Duplicate any skip/override UI in both components. | WA-25, DEC-056 |
| Maps API key never echoed | `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` is NEXT_PUBLIC (baked at build time, visible in browser network tab). Never echo in assistant responses. SW must passthrough googleapis.com or opaque response blocks script execution (DEC-079). GCP project snapai-maps. | DEC-078, DEC-079 |
| PK models live in pak_brands JSONB, not equipment_models | pak_equipment_models does not exist. PK models = pak_brands.series[] JSONB array. `type: "inverter"` drives the inverter badge. After seeding, clear IndexedDB cache. | DEC-057, WA-26 |
| IndexedDB model cache = 24h TTL | After updating pak_brands, browser shows stale models for 24h. Force-clear: `indexedDB.deleteDatabase('snapai_models_pk')` + reload. localStorage has no model cache. | WA-26 |
| React controlled components ignore native events | `element.click()` and `dispatchEvent` do NOT update React state. Must call `element[__reactPropsKey].onChange/onClick()` directly. | WA-27 |
| estimates table has NO updated_at | INSERT INTO estimates must NOT include updated_at — column does not exist. Omit it. BUG-035 caused silent failure in _generate_service_estimate. | DEC-059, WA-28 |
| POST /api/estimates/service does NOT exist | ServiceChecklist must call onComplete() directly after service_step_complete. Backend auto-generates estimate. Frontend must NEVER POST to this missing endpoint. | DEC-060, WA-29 |
| ServiceChecklist needs getAuthHeaders callback | Pass `getAuthHeaders: () => Promise<headers>` — NOT pre-baked authHeaders. Clerk JWTs expire in 60s; a pre-baked token always expires during a service checklist session. | DEC-058, WA-30 |
| Edit tool truncates NTFS .md files too | DEC-027 applies to ALL files with non-ASCII (emoji, arrows, dashes). Use Python replace() via Desktop Commander. If truncated: `git cat-file blob <sha>` to restore, then patch via Python. | DEC-027, WA-31 |
| `/api/brands` does NOT exist | Use `/api/models/all` with X-Market header. Response is `{models:[...]}` — parse as `data.models`, never `Array.isArray(data)`. | arch note |
| `pak_diagnostic_questions` does NOT exist | PK PSI thresholds live in `pak_operating_targets` (refrigerant, ambient_c, suction_min_psi, suction_max_psi). suction_max_psi IS the high threshold (R-410A=145, R-32=140, R-22=88 at 40-45C). | arch note |
| DNS for mainnov.tech is in Hostinger, NOT Cloudflare | Account: `mshoabarabi@gmail.com` at hpanel.hostinger.com. staging_secrets.txt comment says Cloudflare — WRONG. CNAME names must be `staging.snapai` and `pk-staging.snapai` (NOT `staging`/`pk-staging` which resolves to wrong subdomain). Target: `e08b930de4517e81.vercel-dns-017.com`. Fixed and verified live 2026-05-23. | DEC-068 |
| Vercel staging domains serve `staging` branch via domain-level gitBranch | All 3 staging domains have `gitBranch: "staging"` set at domain level (DEC-067 SUPERSEDED). Push to `staging` branch → all staging domains rebuild automatically. The project-level `link.productionBranch` still shows `main` (Vercel API won't let us change it) but domains ignore it. | DEC-080 |
| StagingBanner is RSC in (app)/layout.tsx, auth-only | Banner only shows on authenticated routes. Public pages (homepage, sign-in) do NOT show it. Correct behavior — do not add to root layout. | DEC-069 |
| 2.5T commercial warning = MANUAL TONNAGE text input | Commercial warning triggers when user types "2.5" into the TONNAGE text field. NOT triggered by tonnage buttons (which only show 1.0T/1.5T/2.0T for all current PK brands). Test via manual text entry. | WA-40 |
| CAST(:options AS jsonb) required for JSONB INSERT | SQLAlchemy raw SQL INSERT into JSONB column silently fails without explicit CAST. Use `CAST(:options AS jsonb)`. No exception raised on failure. | DEC-072 |
| diagnostic_questions uses step_id, no market col | Column is `step_id` (NOT `step_key`). No `market` column. Table is shared US+PK. PSI thresholds stored here. | — |
| diagnostic_questions IS Monaco-seeded — migrations alone can NOT prove absence | The `branch_logic_jsonb` for every complaint's step chain was seeded directly in Supabase via the Monaco SQL editor, NOT in Alembic migration files (011 is a no-op with docstring saying so; 008 same pattern). Reading migrations to conclude a branch is missing is DEC-111 failure. Query live prod DB (`mcp__supabase__execute_sql` on `snapai-prod-use1`) against `diagnostic_questions` before claiming any diagnostic branch, resolve_card, or escalate reason is absent. | DEC-129 |
| NEXT_PUBLIC_ENV=staging on prod = recurring bug | BUG-031 (2026-05-21) and BUG-041 (2026-05-23) both caused by this. After ANY Vercel env var changes, verify production NEXT_PUBLIC_ENV is absent or "production". | DEC-023, DEC-073 |
| Address gate affects BOTH markets — ✅ RESOLVED 2026-05-24 | WA-32 gate removed: 5-line R.3 block deleted from handleComplaintSelected in assess/page.tsx. Complaint selection works without address on both US and PK markets. Backend already supports property_id=None. | WA-32
| QA pass ≠ front-end content accuracy | Stage 7 Houston QA “PASS” verified backend routing (45 PSI → Refrigerant Leak). It did NOT verify displayed hint accuracy. ✅ RESOLVED 2026-05-24: Alembic 035 + diagnostic.py corrected R-410A thresholds to 115-140 PSI suction, 225-275 PSI discharge. hint text updated in diagnostic_questions. | WA-41 ✔ |
| Houston PSI routing is ambient-aware via operating_targets | Phase 2 complete 2026-05-24. pak_operating_targets renamed → operating_targets with market column. Both US and PK use unified dynamic per-ambient lookup. Ambient captured via 3-button UI (Mild/Hot/Extreme) on Step Zero. DEC-085. | Phase 2 ✔ |
| R-410A PSI hint shows R-22 numbers — ✅ RESOLVED 2026-05-24 | Alembic 035 corrects all 4 affected diagnostic_questions rows (q2-nc-suction, q2-nc-discharge, q2-hiss-suction, q2-wd-suction). diagnostic.py _us_suction/_us_discharge dicts corrected. Verified boundary-value: 80→low, 125→ok, 160→high for suction; 210→escalate, 250→ok, 310→high for discharge. | WA-41 closed |
| Brand voice on landing pages â â RESOLVED 2026-05-24 | Homepage, /tech, /homeowner rewritten with honest builder positioning. Loom placeholders removed, "1 in 4" stat removed, Gemini Vision removed, banned-word scrub clean. Pricing line added. | chore/brand-voice-landing-pages
| Tier naming — ✅ RESOLVED 2026-05-24 | Good/Better/Best unified across estimate builder, /homeowner, /r/ report, and contractor PDF. isRec split into isMiddleTier (styling) + isRecommended (badge, wired to opt.recommended). | DEC-049 resolved
| /d/ vs /r/ URL audiences differ | `/d/{share_token}` = tech-to-tech diagnostic share. Uses HVAC jargon ("pull vacuum to 500 microns", "Schrader valves"). Public, no auth. NOT homeowner-facing. `/r/{slug}/{reportId}` = homeowner-facing report (Good/Better/Best, plain English, no jargon). When sharing externally, use the right URL for the audience. | arch note |

| StepZeroPanel self-sources Clerk JWT | `useAuth().getToken()` is called inside `runOCR` and `handleConfirm` in StepZeroPanel. The `clerkToken` prop is retained in Props but passed as `null` from `assess/page.tsx` (Server Component — cannot call hooks). Never rely on prop-passed tokens for OCR or any StepZeroPanel fetch. | WA-48, DEC-087 |
| `onSkip` in StepZeroPanel is NEVER called | The `onSkip` prop is declared in Props and passed from assess/page.tsx but StepZeroPanel never calls it internally. There is NO skip button in the UI. To advance past step-zero in automated QA, use React fiber state injection. | WA-42 |
| React fiber QA pattern for step-zero bypass | Walk `document.body.__reactFiber*` tree; find memoizedState where `s.memoizedState === 'step-zero'`; call `s.queue.dispatch('complaint')`. This jumps the assess page to complaint phase without OCR. Use ONLY for QA automation — not production. | DEC-082 |
| Diagnostic API requires `answer` field with classification string | POST to `/api/diagnostic/session/{id}/answer` requires `{ answer: 'low'/'ok'/'high', refrigerant_type: 'R-410A' }`. NOT `{ value: 80 }`. Sending `value` returns 422 "Field required" for `answer`. | WA-43 |
| Production assess page has extra q1 yesno step | On production, Not Cooling flow starts with "Is the outdoor unit running?" (yesno) BEFORE the PSI step. Staging goes directly to PSI. Always answer q1=YES before submitting PSI in production tests. | WA-44 |
| No PK DB model has 2.5T tonnage_data | All pak_brands.series[] tonnage_data keys are 1.0/1.5/2.0 only. The 2.5T commercial warning (isPK && manualUnit.tonnage===2.5) can only be triggered via React fiber injection or when a user types 2.5 in the manual spec text input. The tonnage BUTTONS never show 2.5T. | WA-45 |
| Vercel build errors trace to FIRST failing commit | When Vercel shows ERROR on current deployment, grep git log for the first ERROR commit and diff it against the last READY commit. The bug is always in that diff — not in subsequent commits. Use `git diff <READY_sha>..<FIRST_ERROR_sha> -- <file>` to isolate. | WA-46 |
| TypeScript "Cannot find name" breaks ALL builds silently | A TS error introduced in commit N breaks every subsequent Vercel build including commits N+1...N+K. The fix must be applied in the same file where the undeclared name is used. Always declare ALL JSX variables at the top of the render scope. | WA-47 |
| Goodman model database has 10 series only | Brand dropdown shows "Goodman (10 models)". Real Houston Goodman fleet likely spans 30-50+ series across 20 years (DSZC, GSX, GSXC, GSZC, ARUF, AVPTC, etc.). "My brand isn't listed…" fallback exists but its end-to-end flow is unverified. First 5 testers will surface which brands are missing. | open — wait for beta data |
| Migration hotfix duplicate block = invisible on staging | When adding a step to an existing migration as a hotfix, the fixed migration does NOT re-run on staging (DB already at that version). Grep `ADD CONSTRAINT` count before committing — must be exactly 1. DEC-086. | DEC-086 |
| No naming non-existent people in marketing copy | “Beta panel” framing is aspirational; switch to panel-claim language only after tester #1 signs up with consent. Never attribute quotes to real people in copy without verification. | open — enforced in brand-voice PR |
| Two GCP projects exist — production Gemini API keys live in Default Gemini Project, NOT snapai-maps | Production Gemini API keys (`...nAgY` + `..._69A`) live in GCP project `Default Gemini Project` (ID `gen-lang-client-0809557545`). The other project `snapai-maps` (ID `root-matrix-497207-j4`) holds the Google Maps API key. BOTH are linked to "My Billing Account" as of 2026-05-29. When future AI sessions check Gemini usage/spend/quotas, they must check the Default Gemini Project — not snapai-maps. Same applies to rate-limit chart and the AI Studio Spend page (project picker must be set to `Default Gemini Project`). | 2026-05-29 audit |
| Photos AND PDFs both go to Cloudflare R2 in production — NOT Supabase Storage | `scopesnap-api/services/storage.py` defines a `BaseStorage` abstract with `LocalStorage` (dev) + `R2Storage` (prod) implementations. Factory `get_storage()` picks based on `ENVIRONMENT` env var + presence of 5 R2 env vars. Production buckets: `scopesnap-uploads` (prod) and `scopesnap-uploads-staging` (staging). Storage paths: photos at `photos/{company_slug}/assessment-{id}/...`; documents at `documents/{company_slug}/estimate-{id}/...`. Supabase Storage is unused in production. Future cost projections must NOT assume photos count against Supabase egress/storage caps. | 2026-05-29 audit |
| R2 env vars are mandatory in production — fallback to LocalStorage silently loses photos on redeploy | `get_storage()` checks for all 5 of `R2_ACCOUNT_ID` / `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` / `R2_BUCKET_NAME` / `R2_PUBLIC_URL`. If any is missing in production, it falls back to LocalStorage with a printed warning AND photos write to Railway's ephemeral disk that resets on every redeploy. Verify these 5 env vars exist in Railway production env before any deploy that touches storage code. As of 2026-05-29 audit: all 5 confirmed set. | 2026-05-29 audit |


---

---

## Stage 4 Staging Isolation Audit — COMPLETE (2026-05-23)

**Audit scope:** 8 dimensions audited (Vercel, Railway, Supabase, Clerk, R2, Visual/Domain, Sentry, DNS)
**Result:** ALL PASS. 2 critical cross-contaminations found and fixed.
**Lead:** Claude (autonomous) — Shoab approved all fixes

### Findings & Fixes

| # | Dimension | Finding | Action | Status |
|---|-----------|---------|--------|--------|
| 4.1 | Vercel env vars | Staging project had pk_live_ in NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY | Corrected to pk_test_; staged branch Preview redeploy 5HJ2piG8A | FIXED |
| 4.1 | Vercel project structure | 2 projects confirmed: scope-snap-ai (prod) + scopesnap-web-staging (staging) | No action | PASS |
| 4.2 | Railway services | Staging service had sk_live_ CLERK_SECRET_KEY (production key) | Replaced with sk_test_ from firm-chamois-61 | FIXED |
| 4.3 | Supabase | prod=quqrvnoguofbjacrxcim, staging=pqmgveqkuckbvyygsilk; no data overlap | No action | PASS |
| 4.4 | Clerk apps | prod=pk_live_ app, staging=firm-chamois-61 (pk_test_) — separate apps | No action | PASS |
| 4.5 | R2 buckets | prod=scopesnap-uploads, staging=scopesnap-uploads-staging — separate buckets | No action | PASS |
| 4.6 | Visual/domain | pk.snapai.mainnov.tech was serving pk_test_ (ISR cache) | No-cache prod redeploy CwjgWfNBi; confirmed pk_live_ | FIXED |
| 4.6 | Visual/domain | staging.snapai.mainnov.tech was serving pk_live_ after initial fix | Staging branch Preview redeploy 5HJ2piG8A; confirmed pk_test_ | FIXED |
| 4.7 | Sentry | production filter: 8+ issues (SNAPAI-API-P/F/S/Y/X/W/V/T); staging filter: 1 issue (SNAPAI-API-Z) | No action | PASS |
| 4.8 | DNS | staging CNAME e08b930de4517e81.vercel-dns-017.com; prod e9353dffc8a96116 — different endpoints | No action | PASS |

### Key Deployment IDs

| Deployment | Project | Purpose | Result |
|------------|---------|---------|--------|
| `5HJ2piG8A` | scopesnap-web-staging | Staging branch Preview redeploy (no cache) — fixes pk_live_ on staging custom domains | pk_test_ confirmed on both staging domains |
| `CwjgWfNBi` | scope-snap-ai | Production no-cache redeploy — fixes ISR cache serving pk_test_ on pk.snapai.mainnov.tech | pk_live_ confirmed on pk.snapai.mainnov.tech |

### Critical Pattern Discovered (DEC-074)

Staging custom domains (staging.snapai.mainnov.tech, pk-staging.snapai.mainnov.tech) are served by **Preview branch deployments** of the `staging` git branch — NOT by Production environment builds. To update staging custom domains after an env var change: Deployments → filter "staging" branch → latest Preview → Redeploy (no cache).

## Live URLs

### Production
| Market | Frontend | Status |
|--------|----------|--------|
| Houston (US) | https://snapai.mainnov.tech | ✅ Live |
| Pakistan (PK) | https://pk.snapai.mainnov.tech | ✅ Live |
| /tech landing (contractor) | https://snapai.mainnov.tech/tech | ✅ Live (commit a000a23, Track H D.1) |
| /homeowner landing | https://snapai.mainnov.tech/homeowner | ✅ Live (commit a000a23, Track H D.2) |

**Backend (Railway):** https://scopesnap-api-production.up.railway.app
**Health endpoint:** `GET /health` → `{"status":"ok","db":"connected","environment":"production","version":"0.1.0"}`

### Staging
| Market | Frontend | Status |
|--------|----------|--------|
| US Staging | https://staging.snapai.mainnov.tech | ✅ Live (custom domain verified 2026-05-23) |
| PK Staging | https://pk-staging.snapai.mainnov.tech | ✅ Live (custom domain verified 2026-05-23) |
| Vercel default | https://scopesnap-web-staging.vercel.app | ✅ Valid+Live |

**Backend (Railway staging):** https://scopesnap-api-staging.up.railway.app
**Health endpoint:** `GET /health` → `{"status":"ok","db":"connected","environment":"staging","version":"0.1.0"}`
**Staging banner:** amber bar "⚠ STAGING — not production data" — RSC in `app/(app)/layout.tsx`, visible only on authenticated routes
**DNS managed:** Hostinger account `mshoabarabi@gmail.com` (mainnov.tech zone) — NOT Cloudflare as staging_secrets.txt comment says
**Vercel staging deploys:** `staging` branch via domain-level gitBranch on all 3 staging domains (DEC-080, Stage 6 complete 2026-05-24)

---

## Infrastructure IDs

### Production
| Service | ID / Reference |
|---------|---------------|
| Railway project | `0e78dd68-ce72-46be-a2b1-7d3119de40a4` |
| Railway service | `a23d5cad-d8c9-434e-a3dc-89634d8642ab` |
| Railway environment | `03c478ed-5720-427a-b567-d6bd2ebf3eb1` |
| Supabase project | `quqrvnoguofbjacrxcim` |
| Vercel project | `scope-snap-ai` (mohammed-shoabs-projects-7844119e) |
| GitHub repo | `mohammed-shoab/ScopeSnapAI` |

### Staging
| Service | ID / Reference |
|---------|---------------|
| Railway staging URL | `https://scopesnap-api-staging.up.railway.app` |
| Supabase staging project | `pqmgveqkuckbvyygsilk` (ap-northeast-1) |
| Vercel staging project | `prj_vq1rWfPN9tD3k82OLFjfIxmNdULc` (`scopesnap-web-staging`) |
| Clerk staging app | `firm-chamois-61` (pk_test_ZmlybS1jaGFtb2lzLTYx…) |
| R2 staging bucket | `scopesnap-uploads-staging` |
| Git branch | `staging` (off `main`) |
| GitHub Actions keepalive | `.github/workflows/keepalive-supabase-A.yml` + `keepalive-supabase-B.yml` (every Sun+Wed) |
| `research` schema (added 2026-05-31) | Marketing Research Agent DB inside the **staging** project, isolated `research` schema (NOT `public`, NOT prod). Full Houston-MSA HVAC operator dataset (4,365 operators, cross-source-verified, diaspora-flagged). Touches no app table. Details: `TECH_STACK.md` → "Marketing Research Database"; code in `marketing/research_agent/`. |
| Secrets reference | `C:\Users\dell\My Drive\Personal Claude\.staging_secrets.txt` (⚠ never commit) |

---

## Current Deployment State

### Production
| Layer | Commit | Status | Date |
|-------|--------|--------|------|
| Vercel (both prod domains) | `5596fde` (fix isRecommended TS error) | ✅ READY — pre-beta walkthrough | 2026-05-24 |
| Railway backend (prod) | `5596fde` (6 issues + 2 build fixes) | ✅ Auto-deploying | 2026-05-24 |
| Alembic migration (prod) | `036` | ✅ Applied — Phase 2 ambient-aware PSI routing, operating_targets unified | 2026-05-24 |
| diagnostic_sessions.photo_skipped | BOOLEAN NOT NULL DEFAULT false | ✅ Applied directly (031 was skipped by Railway during outage) | 2026-05-21 |
| card_tco_data (US) | 57 rows | ✅ Seeded | 2026-05-21 |
| pak_card_tco_data (PK) | 45 rows | ✅ Seeded | 2026-05-21 |
| pak_data_defaults | 1 row (market=PK) | Seeded | 2026-05-19 |
| pak_operating_targets | PK rows (R-22/R-32/R-410A, 30-50°C) + US rows (R-410A/R-22, 25-40°C) | ✅ migration 036 | 2026-05-24 |

### Staging
| Layer | Commit | Status | Date |
|-------|--------|--------|------|
| Vercel staging (vercel.app URL) | `80df2e4` (redeploy BphSPPVbC) | ✅ Ready — Valid Configuration | 2026-05-22 |
| Vercel staging (custom domains) | Both custom domains live | ✅ DNS fixed 2026-05-23; Clerk key fixed 2026-05-23 — Preview redeploy 5HJ2piG8A | 2026-05-23 |
| NEXT_PUBLIC_ENV | `staging` | ✅ Set+saved (direct typing), redeployed | 2026-05-22 |
| Railway staging backend | `92034b3b` | ✅ Health OK, alembic=034 | 2026-05-24 |
| Supabase staging DB | All tables seeded (US + pak_*) | ✅ Full mirror of prod schema | 2026-05-19 |
| Alembic migration (staging) | `036` (Phase 2: operating_targets unified, ambient-aware routing) | ✅ Applied | 2026-05-24 |
| pak_pricing_tiers (staging) | 45 rows (15 cards × 3 tiers) | ✅ Seeded | 2026-05-19 |
| pak_labor_rates (staging) | full_system_1ton/1_5ton_pkr backfilled | ✅ Updated | 2026-05-19 |
| Reference data parity (staging) | All 15 ref tables synced from prod (Stage 5) | ✅ Complete | 2026-05-24 |

**Staging git HEAD:** `92034b3b` — matches main HEAD (Stage 5 force-push 2026-05-24)
**Promote staging → prod:** `scripts/promote-to-prod.sh <file1> [file2 ...]` (run from a local main checkout)

**Current git HEAD (main):** `5596fde` -- "fix(build): declare isRecommended variable in assessment/[id]/page.tsx" (2026-05-24)

**Previous git HEAD (main):** `92034b3b` -- "docs: Stage 3 Google Maps sign-off — DEC-078/DEC-079, BUG-042" (latest as of 2026-05-24)

**Recent commits (newest first -- main):**
- `19db2d1` -- chore: remove [MKT:] debug marker from REF line (2026-05-22)
- `a908eac` -- fix(build): remove broken package-lock.json -- restores Vercel builds (2026-05-22)
- `56fb12f` -- debug(BUG-038): expose reportMarket value in REF line for SSR verification (2026-05-22)
- `7736a7d` -- fix(BUG-038): remove dead module-level fmt() to fix SSR dollar-sign bug (2026-05-22)
- `8ed9a8b` -- debug(BUG-037): add console.log to verify reportMarket value at runtime (2026-05-22)
- `78d0fff` -- feat(BUG-037/mig-030-031): Houston Better-tier copy + estimates.market column (2026-05-22)
- `4db39be` -- fix(BUG-036): remove dead POST /api/estimates/service call — call onComplete directly on service_step_complete (2026-05-22)
- `937b8c7` -- fix(BUG-035): remove updated_at from service estimate INSERT — column does not exist in estimates table (2026-05-22)
- `0140c83` -- fix(BUG-034): pass getAuthHeaders callback to ServiceChecklist instead of pre-baked authHeaders (2026-05-22)
- `c009dbb` -- fix(A.3): fault card is primary issue source in homeowner report (2026-05-22)
- `ac0c3d4` -- docs: update DECISIONS, TECH_STACK, ACTIVE_TASKS (2026-05-22)
- `55d76f8` -- fix(A.5): QR code renders synchronously for PDF print (2026-05-22)
- `c5abd24` -- docs(track-h-b): PROJECT_BRAIN update -- B.1/B.2/B.3 shipped, HEAD 7d164d1 (2026-05-22)
- `7d164d1` -- fix(B.1/B.2/B.3): enrich assessment+diagnoses list rows; hide confidence pill (2026-05-22)
- `31c2b6c` -- docs(D.1+D.2): add /tech + /homeowner landing page URLs to PROJECT_BRAIN (2026-05-22)
- `65f0b00` -- fix(C.2+C.3): diagnostic visit fee above TCO section; peak-season notice gray (2026-05-22)
- `addc57f` -- feat(C.1): TCO cards add polarity arrows + color cues + clarifying labels (2026-05-22)
- `a000a23` -- feat(D.1+D.2): /tech and /homeowner landing pages (2026-05-22)
- `23e3019` -- fix(BUG-033): add photo skip UI to ServiceChecklist (2026-05-21)
- `8872cf9` -- docs(qa-post-track-f-c+bug032): QA sign-off + DEC-049/050/051 + WA-23/24 + BUG-032 retrospective (2026-05-21)
- `4743a40` -- fix(BUG-032): approve endpoint accepts tier A/B/C from stored estimates (2026-05-21)
- `66a772c` -- feat(track-f-c.1/c.3/c.4) (2026-05-21)
- `a6d4a15` -- fix(BUG-027): restore approve endpoint tail in reports.py (2026-05-21)
- `aa4e65b` -- feat(track-f-b.1+b.2+b.3+b.5+b.6): UI polish for beta readiness -- all Group B items (2026-05-21)
- `477314b` -- docs(qa-post-track-f+dx): QA sign-off + BUG-025/026 retrospective + DEC-036/037 + WA-15/16 (2026-05-20)
- `85c5755` -- fix(qa): seasonal_modifier_pct ORM column + handleContinue creates estimate before navigating (2026-05-20)
- `d5efc36` -- fix(migration-030): diagnosis_feedback only -- pak_diagnosis_feedback does not exist in prod (2026-05-20)
- `1ca5ed6` -- feat(track-dx-group-b): diagnosis screen UX overhaul (DX.3 through DX.15) (2026-05-20)
- `1674b4e` -- fix(track-f-a.1+a.3): seasonal report disclosure + dashboard Sent count canonical fix (2026-05-20)
- `ba15901` -- docs(cleanup): remove stale to-dos + update all .md files (2026-05-20)
- `02ad667` -- docs(TECH_STACK+BRAIN): full post-audit update (2026-05-20)
- `35f450c` -- docs: all QA decisions resolved -- D.6 backfill done, R.7+S.7 shipped (2026-05-20)
- `172b825` -- fix(R.7+S.7): contractor profile guard on sendEstimate + StagingBanner (2026-05-20)
- `85197fc` -- docs: full QA audit 2026-05-20 results (2026-05-20)
- `53db54a` -- fix(D.11): pass Clerk JWT token to diagnostic finalize call (DEC-030) (2026-05-20)
- `928a476` -- fix(BUG-024): diagnoses pages guard on isLoaded before getToken() + restore all web routes (2026-05-20)
- `fe5b02a` -- fix(BUG-023): diagnostic list+result use pak_fault_cards directly -- bypass stale prepared statement (2026-05-20)
- `f82d760` -- fix(diagnostic): global exception handler for CORS-aware 500s + has_more/share_token in list response (2026-05-20)
- `575f73e` -- fix: diagnoses detail page passes Clerk token to apiFetch (2026-05-20)
- `872e959` -- feat: add GET /api/diagnostic/result/{session_id} endpoint (2026-05-20)
- `6e3ef5e` -- fix(build): restore scopesnap-api backend files to git index + BUG-020 fc.card_id fix

**Local working tree state (2026-05-20 post-audit):**
All BUG-D.AUTH fixes are pushed. Local NTFS checkout is BEHIND remote — sync before editing:
`git pull --rebase origin main` (use /tmp clone pattern per DEC-004 for any commits).

---


---

## QA History

| Date | Markets | Outcome | Bugs Fixed | HEAD |
|------|---------|---------|------------|------|
| 2026-05-29 | Houston (prod /tech page) | COMPLETE ✅ | Zero bugs. Copy-only deploy: Changes A–E (Wave 1 framing, first-5, $39/tech/mo pricing, About footer with Pakistan/Shoab honesty). Staged on feat/tech-landing-v2.1.2-copy → staging (8e48891) → main (0b7bec0). All 7 smoke checks PASS on snapai.mainnov.tech/tech. Railway health OK. Tracker item 73 closed. | 0b7bec0 |
| 2026-05-27 | Houston + PK (staging→prod) | COMPLETE ✅ | BUG-034 nameplate OCR: JWT auth fix (getToken() inside StepZeroPanel), Tesseract CDN removed, 4-tier Gemini waterfall, photo persistence on Tier-4, spinner text de-branded, Scenario D returning-user path (snap_sz_path localStorage), Scenario E A/B variant + PostHog ab_test_variant_assigned. All 21 acceptance checks PASS. Promoted staging→main commit 3f06f0b. | 3f06f0b |
| 2026-05-24 | Houston + PK | COMPLETE ✅ | 2 build bugs (BUG-043 orphaned brace in homeowner/page.tsx, BUG-044 undeclared isRecommended in assessment/[id]/page.tsx). Both fixed commits 5b137ba/5596fde. All 6 pre-beta issues verified live. Flows 1-6 PASS both markets. PSI thresholds DB confirmed. | 5596fde |
| 2026-05-24 | Houston + PK (staging) | COMPLETE ✅ | Zero production bugs. Stage 7 Staging E2E QA. Houston full flow PASS: Not Cooling -> 45 PSI low -> Refrigerant Leak High Confidence -> Estimate Builder A=$608/B=$1013/C=$1368 USD. PK: environment:staging confirmed, Clerk pk_test_, /api/diagnostic/pk/pressure-targets R-410A data. DEC-070 ACTIVE. |
| 2026-05-23 | Houston + PK | COMPLETE ✅ | BUG-040 (CAST jsonb fix in _generate_service_estimate), BUG-041 (NEXT_PUBLIC_ENV=production on Vercel, redeployed 8WLih2SBr). All 6 flows PASS. PSI thresholds verified. 2.5T warning confirmed. | 19db2d1 |
| 2026-05-23 | Houston + PK | COMPLETE ✅ | Zero — full verification QA + brain file updates. All 6 flows PASS both markets. Lessons L32-L35 documented. DEC-065/066 added. WA-28 through WA-37 added to TECH_STACK. | 19db2d1 |
| 2026-05-22 | Houston | COMPLETE OK | BUG-037 LIVE VERIFIED (Rs.5,906 PKR confirmed on Houston domain rpt-701093). BUG-038-build FIXED (removed 7954-line package-lock.json added by 78d0fff -- was breaking every Vercel build in ~8s). fmt() module-level removed. Debug markers cleaned. | 19db2d1 |
| 2026-05-22 | Houston + PK | COMPLETE ✅ | BUG-037 (estimates.market), BUG-033b (Houston Better-tier copy all 19 cards). Migrations 033+034 deployed. Report currency fixed. | 1b86b77 |
| 2026-05-22 | Houston + PK | COMPLETE ✅ | Track H Group E retro: all 6 flows re-verified PASS. BUG-031 RE-REGRESSION resolved: NEXT_PUBLIC_ENV confirmed as "production" in Vercel (All Environments). pk.snapai.mainnov.tech staging banner gone. | 4db39be |
| 2026-05-22 | Houston + PK | COMPLETE ✅ | Zero — verification-only run. Track H Group A fixes (A.3/A.5) confirmed live. All 6 flows PASS. New learnings: WA-32 (address blocks complaint), WA-33 (no client-side fetches), DEC-061 (A.6 scope). | 4db39be |
| 2026-05-22 | Houston + PK | COMPLETE ✅ | BUG-034 (ServiceChecklist 401 token expiry), BUG-035 (estimates INSERT updated_at), BUG-036 (dead POST /api/estimates/service). All 6 flows PASS both markets. | 4db39be |
| 2026-05-22 | Houston + PK | COMPLETE ✅ | Track H Group A: A.2 backfill (18 rows), A.3 fault card as primary issue source (reports.py), A.5 QR code sync render (ReportClient.tsx). A.1/A.4/A.6/A.7 already done. | c009dbb |
| 2026-05-22 | PK only | COMPLETE ✅ | Track H Group E: full Urdu translation. Dashboard hero + stats, sidebar OVERVIEW/SETTINGS/EARLY ACCESS/Diagnoses, Step Zero panel, homeowner report (Print, Equipment Health, System Overview, Brand, Installed, Call, Text, Peak season). Fixed 4 duplicate keys (TS build error). HEAD: b57d969 | b57d969 |
| 2026-05-22 | Houston + PK | PASS ✅ | Track H Group C: C.1 TCO polarity arrows + labels, C.2 fee placement above TCO, C.3 peak-season notice gray | 65f0b00 |
| 2026-05-21 | Houston + PK | PASS ✅ | BUG-033 resolved (photo skip UI in ServiceChecklist) | 23e3019 |
| 2026-05-21 | Houston + PK | CONDITIONAL PASS ✅ | BUG-031 resolved; BUG-033 open (skip buttons) | 4743a40 (no deploy) |
| 2026-05-21 | Houston + PK | PASS ✅ | BUG-030 (NUMERIC decimal), BUG-032 (tier naming), BUG-027 (reports.py truncation) | 4743a40 |
| 2026-05-21 | Houston + PK | PASS ✅ | BUG-025 (ORM col missing), BUG-026 (wrong nav ID), Track F B.1-B.6 | 66a772c |
| 2026-05-20 | Houston + PK | PASS ✅ | BUG-D.AUTH (4 files), D.6 backfill, R.7+S.7 | 85c5755 |

**Open known issues:**
- None. BUG-034/BUG-045 resolved and promoted to production 2026-05-27.

**Resolved this session (2026-05-24 pre-beta walkthrough):**
- BUG-043: Orphaned Video Embed `<section>`+`<div>`+`{` wrapper in homeowner/page.tsx (Issue #4 incomplete removal) caused webpack syntax error (unclosed brace). Fixed commit 5b137ba8 (main) + ae78c09 (staging).
- BUG-044: `isRecommended` used at line 815 in assessment/[id]/page.tsx JSX but never declared (only `isRec` existed). TS 'Cannot find name' broke ALL Vercel builds from Issue #3 commit onward. Fixed by declaring `const isRecommended` separately from `const isRec`. Fixed commit 5596fde (main) + eca731c (staging).

**Recently resolved:**
- BUG-040 (2026-05-23): CAST(:options AS jsonb) fix — `_generate_service_estimate()` in `api/diagnostic.py`. Service flow now creates estimate correctly.
- BUG-041 (2026-05-23): NEXT_PUBLIC_ENV=production set in Vercel prod ALL environments. Staging banner no longer appears on pk.snapai.mainnov.tech.

**Architecture facts — estimates table:**
- `estimates` table columns: id, assessment_id, company_id, report_token, report_short_id, options, selected_option, total_amount, deposit_amount, markup_percent, status, viewed_at, approved_at, stripe_payment_intent_id, contractor_pdf_url, homeowner_report_url, sent_via, sent_at, actual_cost, accuracy_score, created_at, seasonal_modifier_pct, market
- NO `updated_at` column — any INSERT must omit it
- `market` VARCHAR(2) NOT NULL DEFAULT 'US' — added migration 034. Stamped at estimate creation in fault_estimate.py + diagnostic.py. Used by reports.py to return stored market to report viewer. ReportClient.tsx reads report.market to drive currency formatting (overrides detectMarket()).
- Service estimate: auto-generated by `_generate_service_estimate()` in diagnostic.py when svc-8-run answer returns. Frontend must NOT call POST /api/estimates/service — it does not exist. After service_step_complete, call onComplete() directly; backend estimate is accessible at GET /api/estimates/{assessment_id}.

**Resolved issues:**
- BUG-038-build: RESOLVED 2026-05-22. Root cause: commit 78d0fff accidentally included scopesnap-web/package-lock.json (7954 lines) -- repo intentionally has no lockfile since c2eac8d (force Node 18 fix, March 2026). Vercel npm ci failed in ~8s on every subsequent build. 7 consecutive builds all failed. Fix: `git rm scopesnap-web/package-lock.json` + commit a908eac. Alembic head: 034. Both markets PASS. New HEAD: 19db2d1.

---


---

## 2026-06-08 — STAGING DB MIGRATED Tokyo → Virginia (us-east-1) + connection-pool tuning

**What changed:** Staging database moved Supabase **Tokyo (ap-northeast-1) → Virginia (us-east-1)**, co-located with the Railway backend (US East). Fixes the ~1,300 ms-per-query cross-Pacific latency. Cost unchanged: **$0** (Free plan, NANO).

**Why:** Speed audit found Railway (Virginia) → Supabase (Tokyo) was ~11,000 km each way, costing ~1,300 ms on EVERY DB query. Region mismatch confirmed by inspecting actual project regions.

**Supabase project state now:**
- Staging (NEW): `snapai-staging-use1` ref `kikhhnanuwzocwcpzutr`, region **us-east-1**, ACTIVE. Railway staging DATABASE_URL points here (session pooler, port 5432).
- Staging (OLD): `snapai-staging` ref `pqmgveqkuckbvyygsilk`, Tokyo — **PAUSED** (rollback; fully backed up).
- Prod: `scopesnap` ref `quqrvnoguofbjacrxcim`, Tokyo — **UNCHANGED. PROD NOT YET MIGRATED.**
- Free-tier 2-active-project limit handled by pausing old before creating new → always ≤2 active = $0.

**Code change (committed to `staging` branch, commit b5fc5d0):** `scopesnap-api/db/database.py` engine pool — removed `pool_pre_ping=True` (extra SELECT 1 round-trip per checkout, wasteful now DB is co-located), added `pool_recycle=1800`, set `pool_size=5`, `max_overflow=5` (max conns still 10, under Supabase 15-conn session-pooler cap). NOTE: local repo was 7 commits behind remote + dirty tree, so this was committed directly on GitHub web, not pushed from local.

**DB index (Virginia staging, applied directly via MCP — NOT yet an Alembic migration):** `ix_app_events_report_viewed_short_id` partial index on `app_events ((event_data->>'report_short_id')) WHERE event_name='report_viewed'`. Future-proofs the report-view-count query. ADD AS A MIGRATION before/with prod.

**Measured results (staging, post-tuning):** DB query ~1,300 ms → **~18 ms**; `/api/events` (was slowest) ~3,200 ms → **~417 ms**; Dashboard TTFB 2,462 ms → **726 ms**. ~400 ms of measured latency is the measuring machine's distance to Virginia (a Houston user pays ~30–50 ms there).

**Data integrity — VERIFIED 0 differences:** Virginia staging is a byte-exact clone of old Tokyo staging (restored from verified pg_dump). 57 tables / 41,163 rows, row-by-row identical, incl full `research` (marketing) schema (operator_fields 22,703, canonical_operators 4,365) AND all app US+PK tables. App confirmed reading correct data: equipment_models exact (76, app==DB fingerprint), estimates exact (rpt-567750, rpt-922499), diagnoses exact (fault_cards joins intact).

**Backups (`ScopeSnapAI/backups/`):** `prod_20260608_131219.sql.gz` (Tokyo prod full), `staging_20260608_131219.sql.gz` (Tokyo staging full incl research). gzip-verified + row-count-exact vs live.

**Gemini API key (same day):** old key expired → rotated to new no-expiry AI Studio key in project gen-lang-client-0809557545; billing moved to Prepay ($10 loaded). OCR working.

**NEXT STEP — migrate PROD the same way (after Shoab sign-off).** Proven recipe: pause old → create us-east-1 project → restore fresh pg_dump → swap DATABASE_URL (staging-first done) → verify. Add app_events index as Alembic migration. Known low-risk items user opted to leave: prod Supabase pw + a GitHub PAT were briefly exposed in-session.

## 2026-06-08 (later) — PROD DB ALSO MIGRATED to Virginia (us-east-1) ✅

Production database migrated Tokyo → Virginia, same recipe as staging. New prod project: `snapai-prod-use1` ref `zpsoprffaujswywtsgzy` (us-east-1). Railway prod DATABASE_URL now points here (session pooler 5432 + ?sslmode=require). Verified: Virginia-prod == Tokyo-prod byte-exact (45 tables, 2,450 rows, 0 diff). Prod DB query latency 1,307 ms → **18 ms**. Deploy Active/healthy. Tokyo-prod (`scopesnap`/quqrvnoguofbjacrxcim) kept as hot rollback. app_events index applied to Virginia-prod directly. NOTE: one failed deploy first (pasted staging ref kikhhnanuwzocwcpzutr + port 6543 by mistake) — Railway kept old Tokyo container serving so NO prod downtime; corrected to prod ref + 5432 and it deployed clean. **Both markets US+PK now on Virginia.** Remaining follow-ups: promote the pool-tuning commit (b5fc5d0) from staging→main so prod gets it too (prod already fast at 18 ms without it); convert app_events index to an Alembic migration; decide when to delete the paused Tokyo projects.

## 2026-06-08 — POST-MIGRATION QA: ALL 4 SURFACES PASS (US+PK × staging+prod)

Full QA after both DB migrations to Virginia (us-east-1):
- Backend health: prod + staging both `{"status":"ok","db":"connected"}`. ✅
- Speed (DB query cost, co-located): prod ~0–18 ms, staging ~18 ms (was ~1,300 ms). Health/endpoints ~430–490 ms (mostly measurement-distance network). ✅
- Data integrity Virginia-PROD: US equipment_models=76 (fingerprint 1760, app==DB exact), fault_cards=19, pricing_tiers=57, operating_targets=20 | PK pak_fault_cards=16, pak_pricing_tiers=48, pak_brands=15, PK-models=73 | TXN assessments=199, estimates=43, diagnostic_sessions=192. Matches Tokyo-prod 0-diff. ✅
- Data integrity Virginia-STAGING: US same reference set (76/19/57/20) | PK pak_fault_cards=16, pak_pricing_tiers=45, pak_brands=15 | TXN assessments=20, estimates=2 | RESEARCH/marketing operator_fields=22,703, canonical_operators=4,365 (full schema preserved). Matches staging backup 0-diff. ✅
- App-reads-correct verified on prod (US models API 76/1760 exact) and staging (equipment_models, estimates rpt-567750/rpt-922499, diagnoses fault-card joins all exact).
- Note: US-prod authenticated + all PK frontends need separate Clerk logins not available in-session, so those were verified at backend+data level (same shared backend+DB as the US-staging frontend, which was verified end-to-end). Staging Vercel renderer intermittently freezes on heavy pages — pre-existing frontend perf issue, unrelated to DB migration.

VERDICT: Migration fully verified. Both markets, both environments, on Virginia, fast, data byte-exact.

---

## ⚠️ PK MARKET COMPATIBILITY VIEWS — critical, read before touching PK or migrations (DEC-092, 2026-06-09)

The PK market request path does NOT query the `pak_*` base tables directly. `api/dependencies.py` → `MarketTables` routes PK requests to **five compatibility VIEWS** that remap Pakistani columns onto the US-compatible names the shared SQL expects:

| View | Maps |
|---|---|
| `pak_fault_cards_v` | `pkr_est_*` → `price_list_*`; NULL `phase`/`difficulty` |
| `pak_error_codes_v` | `brand_id` → `brand_family`; `code` → `error_code`; `description` → `meaning` |
| `pak_labor_rates_v` | PKR labor cols → Houston names (attic/r22) |
| `pak_replacement_costs_v` | `pkr_min/max/typical` → `price_min/max/typical` |
| `pak_lifecycle_rules_v` | US-compatible schema, 0 rows (`WHERE false`) → falls to default |
| `pak_operating_targets_v` | owned by migration 036 (`operating_targets WHERE market='PK'`) |

**These views are load-bearing for ALL PK functionality.** If any are missing, every PK query throws "relation does not exist" → backend 503 with NO CORS headers (WA-21 escaped-exception pattern) → the browser shows "Failed to fetch", which *looks* like a CORS/service-worker/connectivity bug but is actually a missing-relation bug. Do not chase CORS/SW first — check these views exist.

**History:** The 5 non-`operating_targets` views were originally created out-of-band (Supabase SQL editor) and were NOT in Alembic. The 2026-06-08 Tokyo→Virginia DB migration lost them on the **staging** restore (the staging dump never contained them). Repaired 2026-06-09 by recreating from the Tokyo-prod backup, and now codified in **Alembic migration `037_pak_market_views.py`** (idempotent `CREATE OR REPLACE VIEW`) so future restores recreate them automatically. Virginia **prod** always had all 6.

**Migration-verification lesson:** row-count diffs do NOT catch missing views/functions/sequences (views have no rows). Any future DB migration must also diff `information_schema.views`, functions, and sequences — not just table row counts.

**US is unaffected by all of this** — US uses the base `fault_cards`/`error_codes`/etc. tables, which restored fine. Verified working on US prod (76 models, estimates resolve, pricing_rules 28) and US staging.

### Two separate PK issues still OPEN (NOT the view bug — do not conflate):
1. **Dashboard "Recent Assessments" / "API offline"** — the dashboard's `/api/estimates/?limit=5` and `/api/analytics/estimates-summary` calls use the SHARED `estimates`/`assessments` ORM tables (no views), yet fail on the PK origin with a network/CORS-layer error (the React `.catch`, not an HTTP error). DB is clean post-view-fix. Needs the Railway/Sentry response-header trace to confirm whether the deployed CORS is not returning `Access-Control-Allow-Origin` for PK origins on normal 200 responses. US origins are unaffected.
2. **`pk.snapai.mainnov.tech` (PROD) renders the DEV/staging Clerk instance** on sign-in ("Sign in to ScopeSnapAI Staging", "Development mode", `firm-chamois-61.accounts.dev`). Possible prod Clerk-key misconfiguration OR the PK prod domain is mapped to the staging Vercel deployment. Verify the PK prod domain's Vercel project + Clerk env vars vs US prod (`snapai.mainnov.tech`, which correctly uses prod Clerk).

### UPDATE 2026-06-09 — PK prod misconfig CONFIRMED (was "possible" above)
Verified by reading the deployed builds' Clerk publishable key + CSP API target:
- **US prod** `snapai.mainnov.tech` → `pk_live_` Clerk + `scopesnap-api-production` ✅ correct.
- **PK prod** `pk.snapai.mainnov.tech` → `pk_test_` (DEV) Clerk + `scopesnap-api-staging` ❌ — it is serving the **staging build/env**, not production.
Implication: pk.snapai has been running against the **staging** backend + staging DB + dev Clerk. So (a) the 2026-06-09 staging view fix also benefits pk.snapai, and (b) the real remedy is to re-point the pk.snapai prod domain to the production Vercel deployment/env (prod Clerk `pk_live_` + `scopesnap-api-production`). Needs Vercel domain/env access.

---

## ✅ CURRENT STATE — 2026-06-09 (PK fully resolved + 2 open follow-ups)

**Working & live-verified:**
- **US prod** `snapai.mainnov.tech` — dashboard loads real data (rpt-0456, rpt-688001, rpt-9515, rpt-547105, rpt-5025). pk_live Clerk + scopesnap-api-production. ✅
- **PK prod** `pk.snapai.mainnov.tech` — NOW serves the correct production build (pk_live Clerk + scopesnap-api-production + Virginia-prod DB). Dashboard loads the same real data. ✅ (was serving a stale staging build; re-aliased via Vercel → Domains → Edit → Save.)
- **Backends:** prod + staging both `{"status":"ok","db":"connected"}`. ✅
- **DBs:** Virginia staging + prod both at alembic **037**, both have all **6** `pak_*_v` views. ✅
- **Migration `037_pak_market_views.py`** committed to staging + main, deployed and ran on both backends (idempotent). ✅

**The 3 PK issues (all fixed):**
1. Missing `pak_*_v` views (migration restore gap) → recreated + codified in migration 037.
2. pk.snapai aliased to stale staging build → re-aliased to production deployment (no rebuild).
3. Dashboard "API offline" → was a STALE SERVICE WORKER (snapai-shell-v2) from the old build intercepting /api calls, NOT backend CORS → cleared.

**OPEN FOLLOW-UP #1 — frontend prod builds fail (`npm error E404`).** Fresh Vercel production builds error at `npm install --legacy-peer-deps` because a dependency version is missing from the npm registry (E404). The live prod deployment (03d80cb, May 29) still serves fine, but NO new frontend change can deploy to prod until the offending dep is pinned/updated in scopesnap-web/package.json + package-lock.json. (Backend/Railway builds are Docker-based and unaffected — migration 037 deployed fine.)

**OPEN FOLLOW-UP #2 — stale SW for returning PK users.** Returning visitors who used the old pk.snapai may still hold the stale service worker and see "API offline" until it updates or they hard-refresh (clear site data / unregister SW). The robust fix is to bump the SW cache name (snapai-shell-v2 → v3) in sw.js on the next frontend deploy so all clients force-update — but that is blocked by follow-up #1 (build must be fixed first).

---

## QA RUN — 2026-06-09 (snapai-qa, all 4 surfaces)

**Surfaces:** US