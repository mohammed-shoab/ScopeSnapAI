# SnapAI ΓÇö Project Brain

> Single source of truth for live URLs, infra IDs, deployment state, and architecture facts.
> Read this first at the start of every session. Update after every deploy or schema change.
>
> Last updated: 2026-05-29 evening ΓÇö **Production infrastructure audit + Gemini billing fix.** Joe ran live verification via Chrome on all 5 production services. Findings: (1) Default Gemini Project (gen-lang-client-0809557545) where production API keys live was on Free tier hitting 20 RPD caps + visible 429 errors ΓÇö linked to My Billing Account tonight, now Tier 1 paid (10,000 RPD on Flash, Unlimited on Flash Lite). (2) All 5 R2 env vars verified set in Railway production ΓÇö photos AND PDFs already routing to Cloudflare R2 via storage.py abstraction. (3) Supabase still on Free tier and will stay there long past 25 paying users because R2 absorbs the photo/PDF storage path. (4) Vercel still on Hobby (Free) ΓÇö ToS upgrade trigger is first paid tester conversion event. (5) Cost-to-serve at $39/tech/mo verified: 5 paying users = $40/mo total cost vs $195 revenue = +$155 / 79% margin; 25 users = $78 cost vs $975 revenue = +$897 / 92% margin. Break-even at 2 users. **Stale entries corrected in TECH_STACK.md:** Clerk plan line (was "dev mode" ΓÇö actually Production keys per DEC-077) + Gemini line (was "Pay-per-use" ΓÇö now Tier 1 with project IDs). New sections added to TECH_STACK.md: Marketing Infrastructure (hellosnapai.com outreach domain separation from mainnov.tech product domain) + Production Account Inventory (live-verified account/plan map) + Cost-to-Serve Structure (verified). v2.1.2 marketing templates + v1.1 Strategic Narrative draft shipped same day; cost-recoverability gate on Shoab's $39 price veto closed PASS.
> Previously: 2026-05-26 ΓÇö BUG-045 (nameplate OCR auth + Tesseract removal + 4-tier waterfall) STAGED + QA PASS. Commit c42cce0 on `staging` branch. WA-48, DEC-087/DEC-088 added. | Previously: 2026-05-24 ΓÇö Phase 2 ambient-aware PSI routing COMPLETE + LIVE. Main HEAD: 84fedcf. Alembic: 036 (production + staging). Boundary tests: 24/24 PASS. DEC-085 + DEC-086. | Pre-beta walkthrough COMPLETE. All 6 issues fixed, 2 build bugs found and fixed, full QA PASS both markets. Main HEAD: 5596fde. Alembic: 035. | Stage 8 COMPLETE. All 8 stages signed off. STAGING_MIRROR_CLOSEOUT.md written. DEC-070 ACTIVE. | Stage 7 Staging E2E QA COMPLETE. DEC-070 ACTIVE. Houston full diagnostic flow PASS on staging (Not Cooling -> PSI low -> Refrigerant Leak -> estimate USD A=$608/B=$1013/C=$1368). PK staging backend PASS (environment:staging, Clerk pk_test_, /api/diagnostic/pk/pressure-targets R-410A data). Staging is a true mirror of production. | Stage 6 Vercel Staging Branch Rewire COMPLETE. All 3 staging domains (staging.snapai.mainnov.tech, pk-staging.snapai.mainnov.tech, scopesnap-web-staging.vercel.app) now serve staging git branch via domain-level gitBranch setting. DEC-067 SUPERSEDED by DEC-080. main HEAD=ebe82f6c, staging HEAD=71bc7fea. | Previously: Stage 5 Staging DB & Branch Parity COMPLETE. Staging alembic=034 (was 025), git branch force-pushed to main HEAD 92034b3b, all 15 reference tables synced from prod. Health OK. Manual app smoke test pending Shoab login. | Previously: 2026-05-23 ΓÇö Stage 3 Google Maps Integration COMPLETE. HoustonAddressAutocomplete live. DEC-078 (CSP) + DEC-079 (SW passthrough) added. BUG-042 (i18n placeholder) logged. GCP key restrictions DONE (HTTP referrer restrictions restored 2026-05-23: localhost:3000/*, snapai.mainnov.tech/*, staging.snapai.mainnov.tech/*). Code comments in next.config.js + sw.js erroneously reference DEC-076/DEC-077 for Maps -- correct refs are DEC-078/DEC-079. | Stage 4 Staging Isolation Audit COMPLETE. All 8 dimensions PASS. 2 critical cross-contaminations found and fixed (Railway sk_live_ on staging ΓåÆ sk_test_; pk.snapai.mainnov.tech ISR cache ΓåÆ fresh redeploy CwjgWfNBi). Staging branch Preview redeploy pattern confirmed (DEC-074). DEC-074/075/076/077 added. | Previously: Stage 1 Production Verification COMPLETE. BUG-040 (CAST(:options AS jsonb) fix in diagnostic.py), BUG-041 (NEXT_PUBLIC_ENV=production on Vercel prod, redeployed 8WLih2SBr). All 6 flows PASS both markets. L36-L39 added, DEC-072/073, WA-38/39. | Previously: Stage 2 Free-Tier Cost Audit COMPLETE. All 15 services verified. Total: $5.00/mo (Railway flat fee only). Supabase spend cap enabled, Railway $10 limit set. DEC-071 added. | Previously: 2026-05-23 ΓÇö Full QA pass (both markets, all 6 flows, zero bugs). Brain files updated with lessons L28-L35, DEC-065/066, WA-28 through WA-37. | Previously: 2026-05-22 ΓÇö STAGING FIX PLAN phases 1-10 complete. BUG-037 CONFIRMED LIVE. BUG-038-build FIXED. HEAD: 19db2d1. Alembic: 034. Staging: NEXT_PUBLIC_ENV=staging fixed+redeployed; DNS updated in Hostinger (mshoabarabi@gmail.com ΓÇö NOT Cloudflare); custom domains pending propagation; scopesnap-web-staging.vercel.app VALID. StagingBanner = RSC in app/(app)/layout.tsx (auth-only routes). pak_diagnostic_questions does NOT exist ΓÇö PSI thresholds in pak_operating_targets. Address input must be populated via React onChange BEFORE complaint selection (WA-32). A.6 scope = DiagnosisListRow only (DEC-061). PK pricing DB URL = /settings/pricing. Next.js uses SSR ΓÇö no client-side API fetches visible (WA-33).
> Previous: Track H Group E complete: full Urdu translation live on pk.snapai.mainnov.tech. Dashboard, sidebar, Step Zero, homeowner report all translated. HEAD: b57d969. Alembic: 032. No open issues.)
> **2026-05-23 patch:** change workflow `WORKFLOW.md` + DEC-070 added ΓÇö staging-first 7-step loop becomes mandatory after Stage 7 sign-off.

---

## Change Workflow (added 2026-05-23 ΓÇö DEC-070)

**Every code, schema, env-var, or infra change uses the staging-first workflow defined in `WORKFLOW.md`.** The flow is: branch off `staging` ΓåÆ merge to `staging` ΓåÆ auto-deploys to staging.snapai.mainnov.tech + pk-staging.snapai.mainnov.tech ΓåÆ verify ΓåÆ run `scripts/promote-to-prod.sh <files>` ΓåÆ main updates ΓåÆ prod auto-deploys ΓåÆ verify on real domain.

**The four absolute rules (codified in DEC-070):**
1. Never edit code directly on `main` without going through `staging` first
2. Never push migrations to prod that haven't run on staging first
3. Never add env vars to prod without mirroring them on staging
4. Never test on production ΓÇö testing happens on staging

**Activation status:** ACTIVE (Stage 7 signed off 2026-05-24). All gaps resolved: Alembic 034 on both envs (Stage 5), Vercel staging domains serve `staging` branch (DEC-080, Stage 6), Houston full E2E QA PASS on staging (Stage 7), PK staging backend PASS (Stage 7). DEC-070 is now mandatory ΓÇö no direct edits to main, no prod testing.

For full protocol ΓÇö migration handling, env var handling, hotfix path, rollback procedure, AI session bootstrap, worked examples ΓÇö read `C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI\WORKFLOW.md` in full before any change work.

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

## Critical Rules (Hard-Won ΓÇö 2026-05-20)

> Full details in TECH_STACK.md WA-9 through WA-14. Read before starting new work.

## Canonical PSI Threshold Table (authoritative ΓÇö Phase 2 updated 2026-05-24)

| Refrigerant | Market | Suction Normal (PSI) | Suction High Threshold | Discharge Normal (PSI) | Discharge High Threshold |
|-------------|--------|----------------------|------------------------|------------------------|--------------------------|
| R-410A      | US     | 115 ΓÇô 140            | >= 141                 | 225 ΓÇô 275              | >= 276                   |
| R-22        | US     | 55 ΓÇô 78              | >= 79                  | 150 ΓÇô 275              | >= 276                   |
| R-32        | US/PK  | 110 ΓÇô 145            | >= 146                 | 225 ΓÇô 290              | >= 291                   |
| R-410A      | PK     | operating_targets (dynamic lookup by ambient_c ΓÇö market='PK') ||
| R-22        | PK     | operating_targets (dynamic lookup by ambient_c ΓÇö market='PK') ||

> Source of truth: `operating_targets` table (dynamic lookup, both markets) + Alembic 036 migration. Static dicts `_FALLBACK_SUCTION`/`_FALLBACK_DISCHARGE` in diagnostic.py are belt-and-suspenders only.
> Do NOT use pre-035 DB values or Stage 7 QA report numbers (45 PSI was a low test value).
> At 95 degrees F outdoor ambient, R-410A suction normal is 115-140 PSI.


| Rule | One-liner | Where |
|------|-----------|-------|
| apiFetch needs explicit token | `apiFetch` never auto-injects JWT. Pass `token: await getToken()` on every call. Fire-and-forget: wrap in `getToken().then()`. | WA-9, DEC-030 |
| No Edit tool on Unicode files | Edit tool truncates NTFS files at non-ASCII chars. Use Python replace() in /tmp clone. | WA-10, DEC-027 |
| Task done Γëá code written | Grep `@router.` count before closing any backend track. | WA-11, DEC-031 |
| NameError inside try/except | Silently disables the feature. Grep for import + call both present. | WA-12, DEC-034 |
| fault_cards PK is card_id | Never use fc.id. Always fc.card_id in JOINs and WHERE. | DEC-033 |
| estimate/[id] is dead code | Real builder = assessment/[id]/page.tsx | DEC-032 |
| Vercel = client-rendered | Use javascript_tool + document.querySelector(), not get_page_text. | WA-13 |
| safe.directory on /tmp clone | `git config --global --add safe.directory /tmp/snapai_tmpN` after every clone. | WA-14 |
| alembic_version Γëá schema truth | `alembic_version=032` does NOT mean col from 031 exists. Verify with `information_schema.columns`. | DEC-043, WA-17 |
| Python write can truncate tail | After every `.py` patch: `python3 -c "ast.parse(open(f).read())"` + `wc -l`. Silent truncation = SyntaxError on Railway. | DEC-044, WA-19 |
| Railway Online Γëá healthy | Service shows Online while crash-looping on SyntaxError. Only `{"status":"ok"}` from `/health` counts. | DEC-045 |
| Clerk session is cross-domain | Login on `snapai.mainnov.tech` also logs in `pk.snapai.mainnov.tech`. One login covers both markets. | DEC-047 |
| Claude tab group resets | New conversation = new tab group = no cookies. User must re-login in Claude's Chrome window. | DEC-048 |
| Estimate tiers are A/B/C | `fault_estimate.py` stores tier as "A"/"B"/"C". `reports.py` approve accepts both. `pak_pricing_tiers.tier` uses good/better/best. These are DIFFERENT naming schemes ΓÇö never conflate them. | DEC-049 |
| NEVER set NEXT_PUBLIC_ENV=staging on production Vercel | StagingBanner shows on prod (BUG-031). Fix via Vercel dashboard ΓÇö no code change. | DEC-023 |
| ServiceChecklist Γëá DiagnosticFlow | Service/Tune-Up renders ServiceChecklist.tsx. UI features in DiagnosticFlow are silently absent for service flows. Duplicate any skip/override UI in both components. | WA-25, DEC-056 |
| Maps API key never echoed | `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` is NEXT_PUBLIC (baked at build time, visible in browser network tab). Never echo in assistant responses. SW must passthrough googleapis.com or opaque response blocks script execution (DEC-079). GCP project snapai-maps. | DEC-078, DEC-079 |
| PK models live in pak_brands JSONB, not equipment_models | pak_equipment_models does not exist. PK models = pak_brands.series[] JSONB array. `type: "inverter"` drives the inverter badge. After seeding, clear IndexedDB cache. | DEC-057, WA-26 |
| IndexedDB model cache = 24h TTL | After updating pak_brands, browser shows stale models for 24h. Force-clear: `indexedDB.deleteDatabase('snapai_models_pk')` + reload. localStorage has no model cache. | WA-26 |
| React controlled components ignore native events | `element.click()` and `dispatchEvent` do NOT update React state. Must call `element[__reactPropsKey].onChange/onClick()` directly. | WA-27 |
| estimates table has NO updated_at | INSERT INTO estimates must NOT include updated_at ΓÇö column does not exist. Omit it. BUG-035 caused silent failure in _generate_service_estimate. | DEC-059, WA-28 |
| POST /api/estimates/service does NOT exist | ServiceChecklist must call onComplete() directly after service_step_complete. Backend auto-generates estimate. Frontend must NEVER POST to this missing endpoint. | DEC-060, WA-29 |
| ServiceChecklist needs getAuthHeaders callback | Pass `getAuthHeaders: () => Promise<headers>` ΓÇö NOT pre-baked authHeaders. Clerk JWTs expire in 60s; a pre-baked token always expires during a service checklist session. | DEC-058, WA-30 |
| Edit tool truncates NTFS .md files too | DEC-027 applies to ALL files with non-ASCII (emoji, arrows, dashes). Use Python replace() via Desktop Commander. If truncated: `git cat-file blob <sha>` to restore, then patch via Python. | DEC-027, WA-31 |
| `/api/brands` does NOT exist | Use `/api/models/all` with X-Market header. Response is `{models:[...]}` ΓÇö parse as `data.models`, never `Array.isArray(data)`. | arch note |
| `pak_diagnostic_questions` does NOT exist | PK PSI thresholds live in `pak_operating_targets` (refrigerant, ambient_c, suction_min_psi, suction_max_psi). suction_max_psi IS the high threshold (R-410A=145, R-32=140, R-22=88 at 40-45C). | arch note |
| DNS for mainnov.tech is in Hostinger, NOT Cloudflare | Account: `mshoabarabi@gmail.com` at hpanel.hostinger.com. staging_secrets.txt comment says Cloudflare ΓÇö WRONG. CNAME names must be `staging.snapai` and `pk-staging.snapai` (NOT `staging`/`pk-staging` which resolves to wrong subdomain). Target: `e08b930de4517e81.vercel-dns-017.com`. Fixed and verified live 2026-05-23. | DEC-068 |
| Vercel staging domains serve `staging` branch via domain-level gitBranch | All 3 staging domains have `gitBranch: "staging"` set at domain level (DEC-067 SUPERSEDED). Push to `staging` branch ΓåÆ all staging domains rebuild automatically. The project-level `link.productionBranch` still shows `main` (Vercel API won't let us change it) but domains ignore it. | DEC-080 |
| StagingBanner is RSC in (app)/layout.tsx, auth-only | Banner only shows on authenticated routes. Public pages (homepage, sign-in) do NOT show it. Correct behavior ΓÇö do not add to root layout. | DEC-069 |
| 2.5T commercial warning = MANUAL TONNAGE text input | Commercial warning triggers when user types "2.5" into the TONNAGE text field. NOT triggered by tonnage buttons (which only show 1.0T/1.5T/2.0T for all current PK brands). Test via manual text entry. | WA-40 |
| CAST(:options AS jsonb) required for JSONB INSERT | SQLAlchemy raw SQL INSERT into JSONB column silently fails without explicit CAST. Use `CAST(:options AS jsonb)`. No exception raised on failure. | DEC-072 |
| diagnostic_questions uses step_id, no market col | Column is `step_id` (NOT `step_key`). No `market` column. Table is shared US+PK. PSI thresholds stored here. | ΓÇö |
| NEXT_PUBLIC_ENV=staging on prod = recurring bug | BUG-031 (2026-05-21) and BUG-041 (2026-05-23) both caused by this. After ANY Vercel env var changes, verify production NEXT_PUBLIC_ENV is absent or "production". | DEC-023, DEC-073 |
| Address gate affects BOTH markets ΓÇö Γ£à RESOLVED 2026-05-24 | WA-32 gate removed: 5-line R.3 block deleted from handleComplaintSelected in assess/page.tsx. Complaint selection works without address on both US and PK markets. Backend already supports property_id=None. | WA-32
| QA pass Γëá front-end content accuracy | Stage 7 Houston QA ΓÇ£PASSΓÇ¥ verified backend routing (45 PSI ΓåÆ Refrigerant Leak). It did NOT verify displayed hint accuracy. Γ£à RESOLVED 2026-05-24: Alembic 035 + diagnostic.py corrected R-410A thresholds to 115-140 PSI suction, 225-275 PSI discharge. hint text updated in diagnostic_questions. | WA-41 Γ£ö |
| Houston PSI routing is ambient-aware via operating_targets | Phase 2 complete 2026-05-24. pak_operating_targets renamed ΓåÆ operating_targets with market column. Both US and PK use unified dynamic per-ambient lookup. Ambient captured via 3-button UI (Mild/Hot/Extreme) on Step Zero. DEC-085. | Phase 2 Γ£ö |
| R-410A PSI hint shows R-22 numbers ΓÇö Γ£à RESOLVED 2026-05-24 | Alembic 035 corrects all 4 affected diagnostic_questions rows (q2-nc-suction, q2-nc-discharge, q2-hiss-suction, q2-wd-suction). diagnostic.py _us_suction/_us_discharge dicts corrected. Verified boundary-value: 80ΓåÆlow, 125ΓåÆok, 160ΓåÆhigh for suction; 210ΓåÆescalate, 250ΓåÆok, 310ΓåÆhigh for discharge. | WA-41 closed |
| Brand voice on landing pages ├ó┬Ç┬ö ├ó┬£┬à RESOLVED 2026-05-24 | Homepage, /tech, /homeowner rewritten with honest builder positioning. Loom placeholders removed, "1 in 4" stat removed, Gemini Vision removed, banned-word scrub clean. Pricing line added. | chore/brand-voice-landing-pages
| Tier naming ΓÇö Γ£à RESOLVED 2026-05-24 | Good/Better/Best unified across estimate builder, /homeowner, /r/ report, and contractor PDF. isRec split into isMiddleTier (styling) + isRecommended (badge, wired to opt.recommended). | DEC-049 resolved
| /d/ vs /r/ URL audiences differ | `/d/{share_token}` = tech-to-tech diagnostic share. Uses HVAC jargon ("pull vacuum to 500 microns", "Schrader valves"). Public, no auth. NOT homeowner-facing. `/r/{slug}/{reportId}` = homeowner-facing report (Good/Better/Best, plain English, no jargon). When sharing externally, use the right URL for the audience. | arch note |

| StepZeroPanel self-sources Clerk JWT | `useAuth().getToken()` is called inside `runOCR` and `handleConfirm` in StepZeroPanel. The `clerkToken` prop is retained in Props but passed as `null` from `assess/page.tsx` (Server Component ΓÇö cannot call hooks). Never rely on prop-passed tokens for OCR or any StepZeroPanel fetch. | WA-48, DEC-087 |
| `onSkip` in StepZeroPanel is NEVER called | The `onSkip` prop is declared in Props and passed from assess/page.tsx but StepZeroPanel never calls it internally. There is NO skip button in the UI. To advance past step-zero in automated QA, use React fiber state injection. | WA-42 |
| React fiber QA pattern for step-zero bypass | Walk `document.body.__reactFiber*` tree; find memoizedState where `s.memoizedState === 'step-zero'`; call `s.queue.dispatch('complaint')`. This jumps the assess page to complaint phase without OCR. Use ONLY for QA automation ΓÇö not production. | DEC-082 |
| Diagnostic API requires `answer` field with classification string | POST to `/api/diagnostic/session/{id}/answer` requires `{ answer: 'low'/'ok'/'high', refrigerant_type: 'R-410A' }`. NOT `{ value: 80 }`. Sending `value` returns 422 "Field required" for `answer`. | WA-43 |
| Production assess page has extra q1 yesno step | On production, Not Cooling flow starts with "Is the outdoor unit running?" (yesno) BEFORE the PSI step. Staging goes directly to PSI. Always answer q1=YES before submitting PSI in production tests. | WA-44 |
| No PK DB model has 2.5T tonnage_data | All pak_brands.series[] tonnage_data keys are 1.0/1.5/2.0 only. The 2.5T commercial warning (isPK && manualUnit.tonnage===2.5) can only be triggered via React fiber injection or when a user types 2.5 in the manual spec text input. The tonnage BUTTONS never show 2.5T. | WA-45 |
| Vercel build errors trace to FIRST failing commit | When Vercel shows ERROR on current deployment, grep git log for the first ERROR commit and diff it against the last READY commit. The bug is always in that diff ΓÇö not in subsequent commits. Use `git diff <READY_sha>..<FIRST_ERROR_sha> -- <file>` to isolate. | WA-46 |
| TypeScript "Cannot find name" breaks ALL builds silently | A TS error introduced in commit N breaks every subsequent Vercel build including commits N+1...N+K. The fix must be applied in the same file where the undeclared name is used. Always declare ALL JSX variables at the top of the render scope. | WA-47 |
| Goodman model database has 10 series only | Brand dropdown shows "Goodman (10 models)". Real Houston Goodman fleet likely spans 30-50+ series across 20 years (DSZC, GSX, GSXC, GSZC, ARUF, AVPTC, etc.). "My brand isn't listedΓÇª" fallback exists but its end-to-end flow is unverified. First 5 testers will surface which brands are missing. | open ΓÇö wait for beta data |
| Migration hotfix duplicate block = invisible on staging | When adding a step to an existing migration as a hotfix, the fixed migration does NOT re-run on staging (DB already at that version). Grep `ADD CONSTRAINT` count before committing ΓÇö must be exactly 1. DEC-086. | DEC-086 |
| No naming non-existent people in marketing copy | ΓÇ£Beta panelΓÇ¥ framing is aspirational; switch to panel-claim language only after tester #1 signs up with consent. Never attribute quotes to real people in copy without verification. | open ΓÇö enforced in brand-voice PR |
| Two GCP projects exist ΓÇö production Gemini API keys live in Default Gemini Project, NOT snapai-maps | Production Gemini API keys (`...nAgY` + `..._69A`) live in GCP project `Default Gemini Project` (ID `gen-lang-client-0809557545`). The other project `snapai-maps` (ID `root-matrix-497207-j4`) holds the Google Maps API key. BOTH are linked to "My Billing Account" as of 2026-05-29. When future AI sessions check Gemini usage/spend/quotas, they must check the Default Gemini Project ΓÇö not snapai-maps. Same applies to rate-limit chart and the AI Studio Spend page (project picker must be set to `Default Gemini Project`). | 2026-05-29 audit |
| Photos AND PDFs both go to Cloudflare R2 in production ΓÇö NOT Supabase Storage | `scopesnap-api/services/storage.py` defines a `BaseStorage` abstract with `LocalStorage` (dev) + `R2Storage` (prod) implementations. Factory `get_storage()` picks based on `ENVIRONMENT` env var + presence of 5 R2 env vars. Production buckets: `scopesnap-uploads` (prod) and `scopesnap-uploads-staging` (staging). Storage paths: photos at `photos/{company_slug}/assessment-{id}/...`; documents at `documents/{company_slug}/estimate-{id}/...`. Supabase Storage is unused in production. Future cost projections must NOT assume photos count against Supabase egress/storage caps. | 2026-05-29 audit |
| R2 env vars are mandatory in production ΓÇö fallback to LocalStorage silently loses photos on redeploy | `get_storage()` checks for all 5 of `R2_ACCOUNT_ID` / `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` / `R2_BUCKET_NAME` / `R2_PUBLIC_URL`. If any is missing in production, it falls back to LocalStorage with a printed warning AND photos write to Railway's ephemeral disk that resets on every redeploy. Verify these 5 env vars exist in Railway production env before any deploy that touches storage code. As of 2026-05-29 audit: all 5 confirmed set. | 2026-05-29 audit |


---

---

## Stage 4 Staging Isolation Audit ΓÇö COMPLETE (2026-05-23)

**Audit scope:** 8 dimensions audited (Vercel, Railway, Supabase, Clerk, R2, Visual/Domain, Sentry, DNS)
**Result:** ALL PASS. 2 critical cross-contaminations found and fixed.
**Lead:** Claude (autonomous) ΓÇö Shoab approved all fixes

### Findings & Fixes

| # | Dimension | Finding | Action | Status |
|---|-----------|---------|--------|--------|
| 4.1 | Vercel env vars | Staging project had pk_live_ in NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY | Corrected to pk_test_; staged branch Preview redeploy 5HJ2piG8A | FIXED |
| 4.1 | Vercel project structure | 2 projects confirmed: scope-snap-ai (prod) + scopesnap-web-staging (staging) | No action | PASS |
| 4.2 | Railway services | Staging service had sk_live_ CLERK_SECRET_KEY (production key) | Replaced with sk_test_ from firm-chamois-61 | FIXED |
| 4.3 | Supabase | prod=quqrvnoguofbjacrxcim, staging=pqmgveqkuckbvyygsilk; no data overlap | No action | PASS |
| 4.4 | Clerk apps | prod=pk_live_ app, staging=firm-chamois-61 (pk_test_) ΓÇö separate apps | No action | PASS |
| 4.5 | R2 buckets | prod=scopesnap-uploads, staging=scopesnap-uploads-staging ΓÇö separate buckets | No action | PASS |
| 4.6 | Visual/domain | pk.snapai.mainnov.tech was serving pk_test_ (ISR cache) | No-cache prod redeploy CwjgWfNBi; confirmed pk_live_ | FIXED |
| 4.6 | Visual/domain | staging.snapai.mainnov.tech was serving pk_live_ after initial fix | Staging branch Preview redeploy 5HJ2piG8A; confirmed pk_test_ | FIXED |
| 4.7 | Sentry | production filter: 8+ issues (SNAPAI-API-P/F/S/Y/X/W/V/T); staging filter: 1 issue (SNAPAI-API-Z) | No action | PASS |
| 4.8 | DNS | staging CNAME e08b930de4517e81.vercel-dns-017.com; prod e9353dffc8a96116 ΓÇö different endpoints | No action | PASS |

### Key Deployment IDs

| Deployment | Project | Purpose | Result |
|------------|---------|---------|--------|
| `5HJ2piG8A` | scopesnap-web-staging | Staging branch Preview redeploy (no cache) ΓÇö fixes pk_live_ on staging custom domains | pk_test_ confirmed on both staging domains |
| `CwjgWfNBi` | scope-snap-ai | Production no-cache redeploy ΓÇö fixes ISR cache serving pk_test_ on pk.snapai.mainnov.tech | pk_live_ confirmed on pk.snapai.mainnov.tech |

### Critical Pattern Discovered (DEC-074)

Staging custom domains (staging.snapai.mainnov.tech, pk-staging.snapai.mainnov.tech) are served by **Preview branch deployments** of the `staging` git branch ΓÇö NOT by Production environment builds. To update staging custom domains after an env var change: Deployments ΓåÆ filter "staging" branch ΓåÆ latest Preview ΓåÆ Redeploy (no cache).

## Live URLs

### Production
| Market | Frontend | Status |
|--------|----------|--------|
| Houston (US) | https://snapai.mainnov.tech | Γ£à Live |
| Pakistan (PK) | https://pk.snapai.mainnov.tech | Γ£à Live |
| /tech landing (contractor) | https://snapai.mainnov.tech/tech | Γ£à Live (commit a000a23, Track H D.1) |
| /homeowner landing | https://snapai.mainnov.tech/homeowner | Γ£à Live (commit a000a23, Track H D.2) |

**Backend (Railway):** https://scopesnap-api-production.up.railway.app
**Health endpoint:** `GET /health` ΓåÆ `{"status":"ok","db":"connected","environment":"production","version":"0.1.0"}`

### Staging
| Market | Frontend | Status |
|--------|----------|--------|
| US Staging | https://staging.snapai.mainnov.tech | Γ£à Live (custom domain verified 2026-05-23) |
| PK Staging | https://pk-staging.snapai.mainnov.tech | Γ£à Live (custom domain verified 2026-05-23) |
| Vercel default | https://scopesnap-web-staging.vercel.app | Γ£à Valid+Live |

**Backend (Railway staging):** https://scopesnap-api-staging.up.railway.app
**Health endpoint:** `GET /health` ΓåÆ `{"status":"ok","db":"connected","environment":"staging","version":"0.1.0"}`
**Staging banner:** amber bar "ΓÜá STAGING ΓÇö not production data" ΓÇö RSC in `app/(app)/layout.tsx`, visible only on authenticated routes
**DNS managed:** Hostinger account `mshoabarabi@gmail.com` (mainnov.tech zone) ΓÇö NOT Cloudflare as staging_secrets.txt comment says
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
| Clerk staging app | `firm-chamois-61` (pk_test_ZmlybS1jaGFtb2lzLTYxΓÇª) |
| R2 staging bucket | `scopesnap-uploads-staging` |
| Git branch | `staging` (off `main`) |
| GitHub Actions keepalive | `.github/workflows/keepalive-supabase-A.yml` + `keepalive-supabase-B.yml` (every Sun+Wed) |
| `research` schema (added 2026-05-31) | Marketing Research Agent DB inside the **staging** project, isolated `research` schema (NOT `public`, NOT prod). Full Houston-MSA HVAC operator dataset (4,365 operators, cross-source-verified, diaspora-flagged). Touches no app table. Details: `TECH_STACK.md` ΓåÆ "Marketing Research Database"; code in `marketing/research_agent/`. |
| Secrets reference | `C:\Users\dell\My Drive\Personal Claude\.staging_secrets.txt` (ΓÜá never commit) |

---

## Current Deployment State

### Production
| Layer | Commit | Status | Date |
|-------|--------|--------|------|
| Vercel (both prod domains) | `5596fde` (fix isRecommended TS error) | Γ£à READY ΓÇö pre-beta walkthrough | 2026-05-24 |
| Railway backend (prod) | `5596fde` (6 issues + 2 build fixes) | Γ£à Auto-deploying | 2026-05-24 |
| Alembic migration (prod) | `036` | Γ£à Applied ΓÇö Phase 2 ambient-aware PSI routing, operating_targets unified | 2026-05-24 |
| diagnostic_sessions.photo_skipped | BOOLEAN NOT NULL DEFAULT false | Γ£à Applied directly (031 was skipped by Railway during outage) | 2026-05-21 |
| card_tco_data (US) | 57 rows | Γ£à Seeded | 2026-05-21 |
| pak_card_tco_data (PK) | 45 rows | Γ£à Seeded | 2026-05-21 |
| pak_data_defaults | 1 row (market=PK) | Seeded | 2026-05-19 |
| pak_operating_targets | PK rows (R-22/R-32/R-410A, 30-50┬░C) + US rows (R-410A/R-22, 25-40┬░C) | Γ£à migration 036 | 2026-05-24 |

### Staging
| Layer | Commit | Status | Date |
|-------|--------|--------|------|
| Vercel staging (vercel.app URL) | `80df2e4` (redeploy BphSPPVbC) | Γ£à Ready ΓÇö Valid Configuration | 2026-05-22 |
| Vercel staging (custom domains) | Both custom domains live | Γ£à DNS fixed 2026-05-23; Clerk key fixed 2026-05-23 ΓÇö Preview redeploy 5HJ2piG8A | 2026-05-23 |
| NEXT_PUBLIC_ENV | `staging` | Γ£à Set+saved (direct typing), redeployed | 2026-05-22 |
| Railway staging backend | `92034b3b` | Γ£à Health OK, alembic=034 | 2026-05-24 |
| Supabase staging DB | All tables seeded (US + pak_*) | Γ£à Full mirror of prod schema | 2026-05-19 |
| Alembic migration (staging) | `036` (Phase 2: operating_targets unified, ambient-aware routing) | Γ£à Applied | 2026-05-24 |
| pak_pricing_tiers (staging) | 45 rows (15 cards ├ù 3 tiers) | Γ£à Seeded | 2026-05-19 |
| pak_labor_rates (staging) | full_system_1ton/1_5ton_pkr backfilled | Γ£à Updated | 2026-05-19 |
| Reference data parity (staging) | All 15 ref tables synced from prod (Stage 5) | Γ£à Complete | 2026-05-24 |

**Staging git HEAD:** `92034b3b` ΓÇö matches main HEAD (Stage 5 force-push 2026-05-24)
**Promote staging ΓåÆ prod:** `scripts/promote-to-prod.sh <file1> [file2 ...]` (run from a local main checkout)

**Current git HEAD (main):** `5596fde` -- "fix(build): declare isRecommended variable in assessment/[id]/page.tsx" (2026-05-24)

**Previous git HEAD (main):** `92034b3b` -- "docs: Stage 3 Google Maps sign-off ΓÇö DEC-078/DEC-079, BUG-042" (latest as of 2026-05-24)

**Recent commits (newest first -- main):**
- `19db2d1` -- chore: remove [MKT:] debug marker from REF line (2026-05-22)
- `a908eac` -- fix(build): remove broken package-lock.json -- restores Vercel builds (2026-05-22)
- `56fb12f` -- debug(BUG-038): expose reportMarket value in REF line for SSR verification (2026-05-22)
- `7736a7d` -- fix(BUG-038): remove dead module-level fmt() to fix SSR dollar-sign bug (2026-05-22)
- `8ed9a8b` -- debug(BUG-037): add console.log to verify reportMarket value at runtime (2026-05-22)
- `78d0fff` -- feat(BUG-037/mig-030-031): Houston Better-tier copy + estimates.market column (2026-05-22)
- `4db39be` -- fix(BUG-036): remove dead POST /api/estimates/service call ΓÇö call onComplete directly on service_step_complete (2026-05-22)
- `937b8c7` -- fix(BUG-035): remove updated_at from service estimate INSERT ΓÇö column does not exist in estimates table (2026-05-22)
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
All BUG-D.AUTH fixes are pushed. Local NTFS checkout is BEHIND remote ΓÇö sync before editing:
`git pull --rebase origin main` (use /tmp clone pattern per DEC-004 for any commits).

---


---

## QA History

| Date | Markets | Outcome | Bugs Fixed | HEAD |
|------|---------|---------|------------|------|
| 2026-05-29 | Houston (prod /tech page) | COMPLETE Γ£à | Zero bugs. Copy-only deploy: Changes AΓÇôE (Wave 1 framing, first-5, $39/tech/mo pricing, About footer with Pakistan/Shoab honesty). Staged on feat/tech-landing-v2.1.2-copy ΓåÆ staging (8e48891) ΓåÆ main (0b7bec0). All 7 smoke checks PASS on snapai.mainnov.tech/tech. Railway health OK. Tracker item 73 closed. | 0b7bec0 |
| 2026-05-27 | Houston + PK (stagingΓåÆprod) | COMPLETE Γ£à | BUG-034 nameplate OCR: JWT auth fix (getToken() inside StepZeroPanel), Tesseract CDN removed, 4-tier Gemini waterfall, photo persistence on Tier-4, spinner text de-branded, Scenario D returning-user path (snap_sz_path localStorage), Scenario E A/B variant + PostHog ab_test_variant_assigned. All 21 acceptance checks PASS. Promoted stagingΓåÆmain commit 3f06f0b. | 3f06f0b |
| 2026-05-24 | Houston + PK | COMPLETE Γ£à | 2 build bugs (BUG-043 orphaned brace in homeowner/page.tsx, BUG-044 undeclared isRecommended in assessment/[id]/page.tsx). Both fixed commits 5b137ba/5596fde. All 6 pre-beta issues verified live. Flows 1-6 PASS both markets. PSI thresholds DB confirmed. | 5596fde |
| 2026-05-24 | Houston + PK (staging) | COMPLETE Γ£à | Zero production bugs. Stage 7 Staging E2E QA. Houston full flow PASS: Not Cooling -> 45 PSI low -> Refrigerant Leak High Confidence -> Estimate Builder A=$608/B=$1013/C=$1368 USD. PK: environment:staging confirmed, Clerk pk_test_, /api/diagnostic/pk/pressure-targets R-410A data. DEC-070 ACTIVE. |
| 2026-05-23 | Houston + PK | COMPLETE Γ£à | BUG-040 (CAST jsonb fix in _generate_service_estimate), BUG-041 (NEXT_PUBLIC_ENV=production on Vercel, redeployed 8WLih2SBr). All 6 flows PASS. PSI thresholds verified. 2.5T warning confirmed. | 19db2d1 |
| 2026-05-23 | Houston + PK | COMPLETE Γ£à | Zero ΓÇö full verification QA + brain file updates. All 6 flows PASS both markets. Lessons L32-L35 documented. DEC-065/066 added. WA-28 through WA-37 added to TECH_STACK. | 19db2d1 |
| 2026-05-22 | Houston | COMPLETE OK | BUG-037 LIVE VERIFIED (Rs.5,906 PKR confirmed on Houston domain rpt-701093). BUG-038-build FIXED (removed 7954-line package-lock.json added by 78d0fff -- was breaking every Vercel build in ~8s). fmt() module-level removed. Debug markers cleaned. | 19db2d1 |
| 2026-05-22 | Houston + PK | COMPLETE Γ£à | BUG-037 (estimates.market), BUG-033b (Houston Better-tier copy all 19 cards). Migrations 033+034 deployed. Report currency fixed. | 1b86b77 |
| 2026-05-22 | Houston + PK | COMPLETE Γ£à | Track H Group E retro: all 6 flows re-verified PASS. BUG-031 RE-REGRESSION resolved: NEXT_PUBLIC_ENV confirmed as "production" in Vercel (All Environments). pk.snapai.mainnov.tech staging banner gone. | 4db39be |
| 2026-05-22 | Houston + PK | COMPLETE Γ£à | Zero ΓÇö verification-only run. Track H Group A fixes (A.3/A.5) confirmed live. All 6 flows PASS. New learnings: WA-32 (address blocks complaint), WA-33 (no client-side fetches), DEC-061 (A.6 scope). | 4db39be |
| 2026-05-22 | Houston + PK | COMPLETE Γ£à | BUG-034 (ServiceChecklist 401 token expiry), BUG-035 (estimates INSERT updated_at), BUG-036 (dead POST /api/estimates/service). All 6 flows PASS both markets. | 4db39be |
| 2026-05-22 | Houston + PK | COMPLETE Γ£à | Track H Group A: A.2 backfill (18 rows), A.3 fault card as primary issue source (reports.py), A.5 QR code sync render (ReportClient.tsx). A.1/A.4/A.6/A.7 already done. | c009dbb |
| 2026-05-22 | PK only | COMPLETE Γ£à | Track H Group E: full Urdu translation. Dashboard hero + stats, sidebar OVERVIEW/SETTINGS/EARLY ACCESS/Diagnoses, Step Zero panel, homeowner report (Print, Equipment Health, System Overview, Brand, Installed, Call, Text, Peak season). Fixed 4 duplicate keys (TS build error). HEAD: b57d969 | b57d969 |
| 2026-05-22 | Houston + PK | PASS Γ£à | Track H Group C: C.1 TCO polarity arrows + labels, C.2 fee placement above TCO, C.3 peak-season notice gray | 65f0b00 |
| 2026-05-21 | Houston + PK | PASS Γ£à | BUG-033 resolved (photo skip UI in ServiceChecklist) | 23e3019 |
| 2026-05-21 | Houston + PK | CONDITIONAL PASS Γ£à | BUG-031 resolved; BUG-033 open (skip buttons) | 4743a40 (no deploy) |
| 2026-05-21 | Houston + PK | PASS Γ£à | BUG-030 (NUMERIC decimal), BUG-032 (tier naming), BUG-027 (reports.py truncation) | 4743a40 |
| 2026-05-21 | Houston + PK | PASS Γ£à | BUG-025 (ORM col missing), BUG-026 (wrong nav ID), Track F B.1-B.6 | 66a772c |
| 2026-05-20 | Houston + PK | PASS Γ£à | BUG-D.AUTH (4 files), D.6 backfill, R.7+S.7 | 85c5755 |

**Open known issues:**
- None. BUG-034/BUG-045 resolved and promoted to production 2026-05-27.

**Resolved this session (2026-05-24 pre-beta walkthrough):**
- BUG-043: Orphaned Video Embed `<section>`+`<div>`+`{` wrapper in homeowner/page.tsx (Issue #4 incomplete removal) caused webpack syntax error (unclosed brace). Fixed commit 5b137ba8 (main) + ae78c09 (staging).
- BUG-044: `isRecommended` used at line 815 in assessment/[id]/page.tsx JSX but never declared (only `isRec` existed). TS 'Cannot find name' broke ALL Vercel builds from Issue #3 commit onward. Fixed by declaring `const isRecommended` separately from `const isRec`. Fixed commit 5596fde (main) + eca731c (staging).

**Recently resolved:**
- BUG-040 (2026-05-23): CAST(:options AS jsonb) fix ΓÇö `_generate_service_estimate()` in `api/diagnostic.py`. Service flow now creates estimate correctly.
- BUG-041 (2026-05-23): NEXT_PUBLIC_ENV=production set in Vercel prod ALL environments. Staging banner no longer appears on pk.snapai.mainnov.tech.

**Architecture facts ΓÇö estimates table:**
- `estimates` table columns: id, assessment_id, company_id, report_token, report_short_id, options, selected_option, total_amount, deposit_amount, markup_percent, status, viewed_at, approved_at, stripe_payment_intent_id, contractor_pdf_url, homeowner_report_url, sent_via, sent_at, actual_cost, accuracy_score, created_at, seasonal_modifier_pct, market
- NO `updated_at` column ΓÇö any INSERT must omit it
- `market` VARCHAR(2) NOT NULL DEFAULT 'US' ΓÇö added migration 034. Stamped at estimate creation in fault_estimate.py + diagnostic.py. Used by reports.py to return stored market to report viewer. ReportClient.tsx reads report.market to drive currency formatting (overrides detectMarket()).
- Service estimate: auto-generated by `_generate_service_estimate()` in diagnostic.py when svc-8-run answer returns. Frontend must NOT call POST /api/estimates/service ΓÇö it does not exist. After service_step_complete, call onComplete() directly; backend estimate is accessible at GET /api/estimates/{assessment_id}.

**Resolved issues:**
- BUG-038-build: RESOLVED 2026-05-22. Root cause: commit 78d0fff accidentally included scopesnap-web/package-lock.json (7954 lines) -- repo intentionally has no lockfile since c2eac8d (force Node 18 fix, March 2026). Vercel npm ci failed in ~8s on every subsequent build. 7 consecutive builds all failed. Fix: `git rm scopesnap-web/package-lock.json` + commit a908eac. Alembic head: 034. Both markets PASS. New HEAD: 19db2d1.

---


---

## 2026-06-08 ΓÇö STAGING DB MIGRATED Tokyo ΓåÆ Virginia (us-east-1) + connection-pool tuning

**What changed:** Staging database moved Supabase **Tokyo (ap-northeast-1) ΓåÆ Virginia (us-east-1)**, co-located with the Railway backend (US East). Fixes the ~1,300 ms-per-query cross-Pacific latency. Cost unchanged: **$0** (Free plan, NANO).

**Why:** Speed audit found Railway (Virginia) ΓåÆ Supabase (Tokyo) was ~11,000 km each way, costing ~1,300 ms on EVERY DB query. Region mismatch confirmed by inspecting actual project regions.

**Supabase project state now:**
- Staging (NEW): `snapai-staging-use1` ref `kikhhnanuwzocwcpzutr`, region **us-east-1**, ACTIVE. Railway staging DATABASE_URL points here (session pooler, port 5432).
- Staging (OLD): `snapai-staging` ref `pqmgveqkuckbvyygsilk`, Tokyo ΓÇö **PAUSED** (rollback; fully backed up).
- Prod: `scopesnap` ref `quqrvnoguofbjacrxcim`, Tokyo ΓÇö **UNCHANGED. PROD NOT YET MIGRATED.**
- Free-tier 2-active-project limit handled by pausing old before creating new ΓåÆ always Γëñ2 active = $0.

**Code change (committed to `staging` branch, commit b5fc5d0):** `scopesnap-api/db/database.py` engine pool ΓÇö removed `pool_pre_ping=True` (extra SELECT 1 round-trip per checkout, wasteful now DB is co-located), added `pool_recycle=1800`, set `pool_size=5`, `max_overflow=5` (max conns still 10, under Supabase 15-conn session-pooler cap). NOTE: local repo was 7 commits behind remote + dirty tree, so this was committed directly on GitHub web, not pushed from local.

**DB index (Virginia staging, applied directly via MCP ΓÇö NOT yet an Alembic migration):** `ix_app_events_report_viewed_short_id` partial index on `app_events ((event_data->>'report_short_id')) WHERE event_name='report_viewed'`. Future-proofs the report-view-count query. ADD AS A MIGRATION before/with prod.

**Measured results (staging, post-tuning):** DB query ~1,300 ms ΓåÆ **~18 ms**; `/api/events` (was slowest) ~3,200 ms ΓåÆ **~417 ms**; Dashboard TTFB 2,462 ms ΓåÆ **726 ms**. ~400 ms of measured latency is the measuring machine's distance to Virginia (a Houston user pays ~30ΓÇô50 ms there).

**Data integrity ΓÇö VERIFIED 0 differences:** Virginia staging is a byte-exact clone of old Tokyo staging (restored from verified pg_dump). 57 tables / 41,163 rows, row-by-row identical, incl full `research` (marketing) schema (operator_fields 22,703, canonical_operators 4,365) AND all app US+PK tables. App confirmed reading correct data: equipment_models exact (76, app==DB fingerprint), estimates exact (rpt-567750, rpt-922499), diagnoses exact (fault_cards joins intact).

**Backups (`ScopeSnapAI/backups/`):** `prod_20260608_131219.sql.gz` (Tokyo prod full), `staging_20260608_131219.sql.gz` (Tokyo staging full incl research). gzip-verified + row-count-exact vs live.

**Gemini API key (same day):** old key expired ΓåÆ rotated to new no-expiry AI Studio key in project gen-lang-client-0809557545; billing moved to Prepay ($10 loaded). OCR working.

**NEXT STEP ΓÇö migrate PROD the same way (after Shoab sign-off).** Proven recipe: pause old ΓåÆ create us-east-1 project ΓåÆ restore fresh pg_dump ΓåÆ swap DATABASE_URL (staging-first done) ΓåÆ verify. Add app_events index as Alembic migration. Known low-risk items user opted to leave: prod Supabase pw + a GitHub PAT were briefly exposed in-session.

## 2026-06-08 (later) ΓÇö PROD DB ALSO MIGRATED to Virginia (us-east-1) Γ£à

Production database migrated Tokyo ΓåÆ Virginia, same recipe as staging. New prod project: `snapai-prod-use1` ref `zpsoprffaujswywtsgzy` (us-east-1). Railway prod DATABASE_URL now points here (session pooler 5432 + ?sslmode=require). Verified: Virginia-prod == Tokyo-prod byte-exact (45 tables, 2,450 rows, 0 diff). Prod DB query latency 1,307 ms ΓåÆ **18 ms**. Deploy Active/healthy. Tokyo-prod (`scopesnap`/quqrvnoguofbjacrxcim) kept as hot rollback. app_events index applied to Virginia-prod directly. NOTE: one failed deploy first (pasted staging ref kikhhnanuwzocwcpzutr + port 6543 by mistake) ΓÇö Railway kept old Tokyo container serving so NO prod downtime; corrected to prod ref + 5432 and it deployed clean. **Both markets US+PK now on Virginia.** Remaining follow-ups: promote the pool-tuning commit (b5fc5d0) from stagingΓåÆmain so prod gets it too (prod already fast at 18 ms without it); convert app_events index to an Alembic migration; decide when to delete the paused Tokyo projects.

## 2026-06-08 ΓÇö POST-MIGRATION QA: ALL 4 SURFACES PASS (US+PK ├ù staging+prod)

Full QA after both DB migrations to Virginia (us-east-1):
- Backend health: prod + staging both `{"status":"ok","db":"connected"}`. Γ£à
- Speed (DB query cost, co-located): prod ~0ΓÇô18 ms, staging ~18 ms (was ~1,300 ms). Health/endpoints ~430ΓÇô490 ms (mostly measurement-distance network). Γ£à
- Data integrity Virginia-PROD: US equipment_models=76 (fingerprint 1760, app==DB exact), fault_cards=19, pricing_tiers=57, operating_targets=20 | PK pak_fault_cards=16, pak_pricing_tiers=48, pak_brands=15, PK-models=73 | TXN assessments=199, estimates=43, diagnostic_sessions=192. Matches Tokyo-prod 0-diff. Γ£à
- Data integrity Virginia-STAGING: US same reference set (76/19/57/20) | PK pak_fault_cards=16, pak_pricing_tiers=45, pak_brands=15 | TXN assessments=20, estimates=2 | RESEARCH/marketing operator_fields=22,703, canonical_operators=4,365 (full schema preserved). Matches staging backup 0-diff. Γ£à
- App-reads-correct verified on prod (US models API 76/1760 exact) and staging (equipment_models, estimates rpt-567750/rpt-922499, diagnoses fault-card joins all exact).
- Note: US-prod authenticated + all PK frontends need separate Clerk logins not available in-session, so those were verified at backend+data level (same shared backend+DB as the US-staging frontend, which was verified end-to-end). Staging Vercel renderer intermittently freezes on heavy pages ΓÇö pre-existing frontend perf issue, unrelated to DB migration.

VERDICT: Migration fully verified. Both markets, both environments, on Virginia, fast, data byte-exact.

---

## ΓÜá∩╕Å PK MARKET COMPATIBILITY VIEWS ΓÇö critical, read before touching PK or migrations (DEC-092, 2026-06-09)

The PK market request path does NOT query the `pak_*` base tables directly. `api/dependencies.py` ΓåÆ `MarketTables` routes PK requests to **five compatibility VIEWS** that remap Pakistani columns onto the US-compatible names the shared SQL expects:

| View | Maps |
|---|---|
| `pak_fault_cards_v` | `pkr_est_*` ΓåÆ `price_list_*`; NULL `phase`/`difficulty` |
| `pak_error_codes_v` | `brand_id` ΓåÆ `brand_family`; `code` ΓåÆ `error_code`; `description` ΓåÆ `meaning` |
| `pak_labor_rates_v` | PKR labor cols ΓåÆ Houston names (attic/r22) |
| `pak_replacement_costs_v` | `pkr_min/max/typical` ΓåÆ `price_min/max/typical` |
| `pak_lifecycle_rules_v` | US-compatible schema, 0 rows (`WHERE false`) ΓåÆ falls to default |
| `pak_operating_targets_v` | owned by migration 036 (`operating_targets WHERE market='PK'`) |

**These views are load-bearing for ALL PK functionality.** If any are missing, every PK query throws "relation does not exist" ΓåÆ backend 503 with NO CORS headers (WA-21 escaped-exception pattern) ΓåÆ the browser shows "Failed to fetch", which *looks* like a CORS/service-worker/connectivity bug but is actually a missing-relation bug. Do not chase CORS/SW first ΓÇö check these views exist.

**History:** The 5 non-`operating_targets` views were originally created out-of-band (Supabase SQL editor) and were NOT in Alembic. The 2026-06-08 TokyoΓåÆVirginia DB migration lost them on the **staging** restore (the staging dump never contained them). Repaired 2026-06-09 by recreating from the Tokyo-prod backup, and now codified in **Alembic migration `037_pak_market_views.py`** (idempotent `CREATE OR REPLACE VIEW`) so future restores recreate them automatically. Virginia **prod** always had all 6.

**Migration-verification lesson:** row-count diffs do NOT catch missing views/functions/sequences (views have no rows). Any future DB migration must also diff `information_schema.views`, functions, and sequences ΓÇö not just table row counts.

**US is unaffected by all of this** ΓÇö US uses the base `fault_cards`/`error_codes`/etc. tables, which restored fine. Verified working on US prod (76 models, estimates resolve, pricing_rules 28) and US staging.

### Two separate PK issues still OPEN (NOT the view bug ΓÇö do not conflate):
1. **Dashboard "Recent Assessments" / "API offline"** ΓÇö the dashboard's `/api/estimates/?limit=5` and `/api/analytics/estimates-summary` calls use the SHARED `estimates`/`assessments` ORM tables (no views), yet fail on the PK origin with a network/CORS-layer error (the React `.catch`, not an HTTP error). DB is clean post-view-fix. Needs the Railway/Sentry response-header trace to confirm whether the deployed CORS is not returning `Access-Control-Allow-Origin` for PK origins on normal 200 responses. US origins are unaffected.
2. **`pk.snapai.mainnov.tech` (PROD) renders the DEV/staging Clerk instance** on sign-in ("Sign in to ScopeSnapAI Staging", "Development mode", `firm-chamois-61.accounts.dev`). Possible prod Clerk-key misconfiguration OR the PK prod domain is mapped to the staging Vercel deployment. Verify the PK prod domain's Vercel project + Clerk env vars vs US prod (`snapai.mainnov.tech`, which correctly uses prod Clerk).

### UPDATE 2026-06-09 ΓÇö PK prod misconfig CONFIRMED (was "possible" above)
Verified by reading the deployed builds' Clerk publishable key + CSP API target:
- **US prod** `snapai.mainnov.tech` ΓåÆ `pk_live_` Clerk + `scopesnap-api-production` Γ£à correct.
- **PK prod** `pk.snapai.mainnov.tech` ΓåÆ `pk_test_` (DEV) Clerk + `scopesnap-api-staging` Γ¥î ΓÇö it is serving the **staging build/env**, not production.
Implication: pk.snapai has been running against the **staging** backend + staging DB + dev Clerk. So (a) the 2026-06-09 staging view fix also benefits pk.snapai, and (b) the real remedy is to re-point the pk.snapai prod domain to the production Vercel deployment/env (prod Clerk `pk_live_` + `scopesnap-api-production`). Needs Vercel domain/env access.

---

## Γ£à CURRENT STATE ΓÇö 2026-06-09 (PK fully resolved + 2 open follow-ups)

**Working & live-verified:**
- **US prod** `snapai.mainnov.tech` ΓÇö dashboard loads real data (rpt-0456, rpt-688001, rpt-9515, rpt-547105, rpt-5025). pk_live Clerk + scopesnap-api-production. Γ£à
- **PK prod** `pk.snapai.mainnov.tech` ΓÇö NOW serves the correct production build (pk_live Clerk + scopesnap-api-production + Virginia-prod DB). Dashboard loads the same real data. Γ£à (was serving a stale staging build; re-aliased via Vercel ΓåÆ Domains ΓåÆ Edit ΓåÆ Save.)
- **Backends:** prod + staging both `{"status":"ok","db":"connected"}`. Γ£à
- **DBs:** Virginia staging + prod both at alembic **037**, both have all **6** `pak_*_v` views. Γ£à
- **Migration `037_pak_market_views.py`** committed to staging + main, deployed and ran on both backends (idempotent). Γ£à

**The 3 PK issues (all fixed):**
1. Missing `pak_*_v` views (migration restore gap) ΓåÆ recreated + codified in migration 037.
2. pk.snapai aliased to stale staging build ΓåÆ re-aliased to production deployment (no rebuild).
3. Dashboard "API offline" ΓåÆ was a STALE SERVICE WORKER (snapai-shell-v2) from the old build intercepting /api calls, NOT backend CORS ΓåÆ cleared.

**OPEN FOLLOW-UP #1 ΓÇö frontend prod builds fail (`npm error E404`).** Fresh Vercel production builds error at `npm install --legacy-peer-deps` because a dependency version is missing from the npm registry (E404). The live prod deployment (03d80cb, May 29) still serves fine, but NO new frontend change can deploy to prod until the offending dep is pinned/updated in scopesnap-web/package.json + package-lock.json. (Backend/Railway builds are Docker-based and unaffected ΓÇö migration 037 deployed fine.)

**OPEN FOLLOW-UP #2 ΓÇö stale SW for returning PK users.** Returning visitors who used the old pk.snapai may still hold the stale service worker and see "API offline" until it updates or they hard-refresh (clear site data / unregister SW). The robust fix is to bump the SW cache name (snapai-shell-v2 ΓåÆ v3) in sw.js on the next frontend deploy so all clients force-update ΓÇö but that is blocked by follow-up #1 (build must be fixed first).

---

## QA RUN ΓÇö 2026-06-09 (snapai-qa, all 4 surfaces)

**Surfaces:** US prod (snapai.mainnov.tech), PK prod (pk.snapai.mainnov.tech), US staging (staging.snapai.mainnov.tech), PK staging (pk-staging.snapai.mainnov.tech). **Outcome: PASS.**

**Backend health:** prod + staging `/health` ΓåÆ `{"status":"ok","db":"connected"}`.

**Engine data (BOTH Virginia DBs at Alembic 037):**
- equipment_models 76; fault_cards US 19 / PK 16 (view == base); operating_targets US 8 / PK 12 (ambient-aware per DEC migration 036).
- PSI thresholds @35┬░C: US R-410A 115ΓÇô140 (128 PSI ΓåÆ NORMAL Γ£ô); PK R-410A 115ΓÇô135 (130 PSI ΓåÆ NORMAL, not Dirty Coil Γ£ô); PK R-22 65ΓÇô72; PK R-32 110ΓÇô130.
- pricing_tiers US 57 / PK 48 (prod), 45 (staging); pak_*_v views all populated (error_codes 17, fault_cards 16, labor 1, replacement 4).
- Brands market-separated: US 15 Houston (Carrier/Bryant/AmanaΓÇª), PK 15 (Gree/Dawlance/Daikin/Haier PKΓÇª).

**Frontend config (all 4 correctly wired):** US prod & PK prod = pk_live + production API; US staging & PK staging = pk_test + staging API. PK prod + PK staging serve **SW v4** (browser-native API passthrough). US prod + PK prod dashboards render real data (rpt-0456, rpt-688001, ΓÇª).

**Recent-fix verification (all confirmed live):** migration 037 + pak_*_v views present on both DBs; pk.snapai on prod build (durable ΓÇö vercel.json alias removed); SW v4 deployed prod+staging; package-lock.json deterministic builds green; vercel.json pk.snapai alias removed.

**Bugs found this run:** none new. **Caveat:** full manual click-through of all 6 diagnostic flows per surface was not performed (staging needs dev-Clerk login; browser tooling intermittent) ΓÇö but the data those flows depend on is fully verified and prod dashboards render live data.

---

# ≡ƒº¡ SESSION RETROSPECTIVE & LEARNINGS ΓÇö 2026-06-09 (the PK "API offline" + TokyoΓåÆVirginia migration saga)

This was a long debugging session. Capturing roadblocks ΓåÆ how they were resolved ΓåÆ reusable lessons so future AI/dev sessions skip the detours. **The single biggest lesson: READ THIS FILE + `api/dependencies.py` (MarketTables) BEFORE doing extensive live browser probing.** Reading the brain cracked a multi-hour problem in minutes.

## ROADBLOCK 1 ΓÇö "API offline" / "Failed to fetch" on PK had FOUR identical-looking causes
A browser "Failed to fetch" / the app's "API offline" looks the same whether the cause is:
(a) a backend 503/raw exception that **bypasses CORS middleware** so the response has no CORS headers (WA-21 pattern), (b) a missing CORS allowed-origin, (c) the **service worker intercepting** the request, or (d) a **missing DB relation** making the backend error. I burned hours assuming CORS and oscillating between CORSΓåöSW.
**What it actually was:** THREE layered causes, not one ΓÇö (1) missing `pak_*_v` views from the migration, (2) pk.snapai serving the wrong build, (3) the service worker intercepting API calls.
**Diagnostic order that works (use this next time):**
1. Read `api/dependencies.py` `MarketTables` + this brain ΓÇö PK routes to **views** `pak_*_v`, not base tables. If a view is missing ΓåÆ backend errors ΓåÆ looks like CORS.
2. Pull **Supabase Postgres logs** (`get_logs` postgres) + `get_advisors` ΓÇö the real SQL error is there. Browser probes are confounded by SW/CSP/cache.
3. `fetch(url,{mode:'no-cors'})` succeeds opaquely if the request **reaches the server** ΓåÆ isolates network/CSP from CORS. `mode:'cors'` failing while no-cors succeeds = CORS/headers issue, not reachability.
4. **Clerk deduction:** Clerk is also a cross-origin call through the same SW passthrough. If Clerk works from the origin, the SW + cross-origin path is fine ΓåÆ the problem is backend or CORS-config, NOT the SW.
5. **Unregister the SW and reload.** If the API works with no SW but fails when the SW controls the page ΓåÆ the SW is the culprit (see ROADBLOCK 4).

## ROADBLOCK 2 ΓÇö Migration row-count check passed but PK was broken (missing VIEWS)
The TokyoΓåÆVirginia data-integrity check compared **table row counts** (0 differences) and declared success ΓÇö but the 5 `pak_*_v` views have no rows, so they were invisible to the check and silently lost on the staging restore.
**Resolution:** found the views referenced in `dependencies.py`, queried `information_schema.views` on the live DB (only 1 of 6 present), extracted the `CREATE VIEW` DDL from the **Tokyo-prod backup** (`backups/prod_fresh_*.sql.gz`), recreated them, and codified in Alembic migration `037`.
**Lesson:** after ANY pg_dump/restore, diff **views, functions, sequences** ΓÇö not just table row counts. Backups are the recovery source of truth (the prod dump held the exact view definitions).

## ROADBLOCK 3 ΓÇö pk.snapai kept reverting to the wrong build after every deploy (FLAPPING)
I fixed pk.snapai (re-aliased to prod) several times via Vercel Domains ΓåÆ Save, but it kept reverting to the staging build (dev Clerk) after the next deploy.
**Root cause:** `scopesnap-web/vercel.json` had a hardcoded `"alias": ["pk.snapai.mainnov.tech"]`. BOTH the prod project (builds `main`) and the staging project (builds `staging`) build this same file, so **every staging deploy stole pk.snapai to staging, every prod deploy stole it back.**
**Resolution:** removed the `alias` from vercel.json on both branches ΓåÆ pk.snapai is now governed **only by the Vercel Domains UI** (assigned to the prod project). It stays put now.
**Lesson:** if a domain serves the wrong build or flaps between deploys, check `vercel.json` `"alias"` first. Govern multi-project domains via the Domains UI, never a hardcoded vercel.json alias.

## ROADBLOCK 4 ΓÇö the service worker broke cross-origin API calls
After fixing the views + build, "API offline" still recurred whenever the SW controlled the page. `sw.js` did `event.respondWith(fetch(event.request))` for `/api/` + cross-origin ΓÇö that re-fetch from the SW context **failed on the PK origin even though a direct browser fetch returned 200 + data.**
**Resolution:** SW **v4** now `return`s WITHOUT `respondWith` for API/cross-origin ΓåÆ the browser handles them natively. Bumped `CACHE_NAME` v2ΓåÆv3ΓåÆv4 to force stale clients to update.
**Lesson:** `respondWith(fetch(event.request))` is interception, not passthrough, and can fail cross-origin where native fetch works. True passthrough = early `return`. Always bump the SW cache name when changing sw.js so clients update.

## ROADBLOCK 5 ΓÇö E404 build failure was a red herring; the real gap was no lockfile
A no-cache "Redeploy" failed at `npm install` with E404. I over-flagged it as blocking.
**Resolution/finding:** **normal git-push deploys use the build cache and succeed** ΓÇö only a *from-scratch* rebuild re-resolves deps and can hit a **transient** registry E404 (a clean `npm install` later completed with 0 errors ΓåÆ not a yanked package). The real fragility was **no lockfile** (repo had only package.json), so every clean build re-resolved "latest matching". Fixed by committing `package-lock.json` (verified on staging, promoted to prod).
**Lesson:** Railway/Docker builds are unaffected by npm registry blips; only Vercel clean rebuilds are. Commit a lockfile for determinism. Don't panic on a one-off E404 ΓÇö confirm whether normal deploys still pass.

## TOOLING GOTCHAS hit this session (save time next time)
- **Vercel/Railway dashboards FREEZE the browser renderer** on screenshots (CDP timeout). Use `get_page_text` (text extraction) instead of screenshots for these SPAs.
- **API-fetch JS from PK origins can HANG/freeze the renderer** (the failing fetch). DOM-read JS is fine; for API checks use `no-cors`, the Supabase logs, or `web_fetch` (server-side) instead.
- **Sandbox bash:** each call is independent (no cwd/env carryover), 45s hard limit; **background processes and /tmp do NOT persist between calls.** The npm registry IS reachable from the sandbox (registry.npmjs.org ΓåÆ 200), but Clerk/Railway/GitHub APIs are proxy-blocked (403). To run npm within 45s: `--prefer-offline` with a warm cache; log to a file with `--loglevel http` to capture partial output before the timeout kills it.
- **Committing without git push:** the sandbox can't `git push` (proxy 403). Use GitHub web **"Upload files"** + the `file_upload` tool ΓÇö it overwrites existing files with exact content. The green "Commit changes" button often needs **two clicks** (first click can land on the "choose your files" link).
- **Backend deploys via env-var change may reuse a cached image** (the code SHA didn't change) ΓÇö a code commit forces a true rebuild.

## PROCESS LESSONS
1. **Read the project docs + routing code before live probing.** The user had to say "read the tech stack first" ΓÇö that was the turning point. Hours of browser probing vs minutes once the `pak_*_v` view architecture was understood.
2. **Don't commit a speculative fix before confirming the root cause** (nearly shipped a CORS `allow_origin_regex` that wouldn't have fixed the real, view/SW/alias causes).
3. **Staging-first for risky prod changes** (lockfile, etc.) ΓÇö verify the build green on staging before promoting to main.
4. **One "fix" can mask layered causes** ΓÇö PK needed FOUR independent fixes (views, build alias, SW, lockfile). Re-verify end-to-end after each, and don't declare done until the SW-controlled load works.

---

### 2026-06-10 ΓÇö DB backups live (Cloudflare R2) ΓÇö see DEC-094 / TECH_STACK
Free automated daily backups of both Virginia DBs now run via GitHub Actions (`.github/workflows/db-backup-r2.yml`) ΓåÆ private R2 bucket `snapai-db-backups` (14-day retention, $0). Verified green 2026-06-10 (run 27296950101); prod+staging dumps present in bucket. Both backends `/health` ok/db-connected afterward.
- Prod backend (live): `scopesnap-api-production.up.railway.app` ΓÇö note the bare `scopesnap-api.up.railway.app` is STALE (Railway 404).
- **Open:** Healthchecks "Keepalive B DOWN" ΓÇö keepalive workflows still ping the deleted Tokyo Supabase URLs; repoint the 4 keepalive secrets to Virginia or retire the keepalives.

### 2026-06-10 ΓÇö Keepalive "DOWN" RESOLVED (DEC-094 follow-up)
Root cause confirmed from run logs: keepalive-supabase-B failed with `curl: (6) Could not resolve host: quqrvnoguofbjacrxcim.supabase.co` ΓÇö the 4 keepalive secrets still pointed at the **deleted Tokyo** projects, so the ping failed and the `if: success()` Healthchecks heartbeat never fired ΓåÆ DOWN.

**Fix:** repointed all 4 keepalive secrets to the Virginia (us-east-1) projects (values fetched via Supabase MCP; updated through the GitHub Secrets API with libsodium sealed-box encryption ΓÇö the anon keys are publishable/public):
- `SUPABASE_PROD_URL`    = `https://zpsoprffaujswywtsgzy.supabase.co` (snapai-prod-use1)
- `SUPABASE_STAGING_URL` = `https://kikhhnanuwzocwcpzutr.supabase.co` (snapai-staging-use1)
- `SUPABASE_PROD_ANON_KEY` / `SUPABASE_STAGING_ANON_KEY` = each project's legacy anon JWT.

**Verified 2026-06-10:** manually dispatched both keepalive-supabase-A and -B ΓåÆ both **success**; steps Ping production / Ping staging / Heartbeat(Healthchecks.io) all green. Both Healthchecks checks flip DOWNΓåÆUP. Twice-weekly schedule restored (A = Sun 02:00 UTC, B = Wed 14:00 UTC).

Note: keepalive is now somewhat redundant with the daily R2 backup (which pg_dumps both DBs daily = stronger DB-activity keepalive), but it's kept for the independent Healthchecks "did the scheduled job run" monitor.

---

<!-- merged from staging 2026-06-21 : sections/rows present ONLY on origin/staging, preserved here so the union loses no content from either branch -->

## Merged from staging (content unique to the staging branch)

**Staging header lead (the "Last updated" entry staging carried that main's header lacked):**

> Last updated: 2026-05-29 ΓÇö **Algo bias fix: fault_severity├ùage_bucket matrix LIVE on production.** `_compute_recommended_tier()` in `fault_estimate.py` replaces pure-age `_REPLACEMENT_TRIGGER_AGE=8` trigger. 3├ù3 matrix: age_bucket (youngΓëñ7yr / mid_life 8-14yr / end_of_lifeΓëÑ15yr) ├ù fault_severity (easy / medium / major). 9/9 test cases PASS on production. staging HEAD: 38036c0, main HEAD: 03d80cb. ReportClient.tsx `isRec` fixed: removed `|| opt.tier === 'better'` hardcoded fallback. DEC-090, WA-49 added. Marketing team unblocked for 'Three options, one recommendation, no upsell' framing. | Previously: 2026-05-29 evening ΓÇö **Production infrastructure audit + Gemini billing fix.** Joe ran live verification via Chrome on all 5 production services. Findings: (1) Default Gemini Project (gen-lang-client-0809557545) where production API keys live was on Free tier hitting 20 RPD caps + visible 429 errors ΓÇö linked to My Billing Account tonight, now Tier 1 paid (10,000 RPD on Flash, Unlimited on Flash Lite). (2) All 5 R2 env vars verified set in Railway production ΓÇö photos AND PDFs already routing to Cloudflare R2 via storage.py abstraction. (3) Supabase still on Free tier and will stay there long past 25 paying users because R2 absorbs the photo/PDF storage path. (4) Vercel still on Hobby (Free) ΓÇö ToS upgrade trigger is first paid tester conversion event. (5) Cost-to-serve at $39/tech/mo verified: 5 paying users = $40/mo total cost vs $195 revenue = +$155 / 79% margin; 25 users = $78 cost vs $975 revenue = +$897 / 92% margin. Break-even at 2 users. **Stale entries corrected in TECH_STACK.md:** Clerk plan line (was "dev mode" ΓÇö actually Production keys per DEC-077) + Gemini line (was "Pay-per-use" ΓÇö now Tier 1 with project IDs). New sections added to TECH_STACK.md: Marketing Infrastructure (hellosnapai.com outreach domain separation from mainnov.tech product domain) + Production Account Inventory (live-verified account/plan map) + Cost-to-Serve Structure (verified). v2.1.2 marketing templates + v1.1 Strategic Narrative draft shipped same day; cost-recoverability gate on Shoab's $39 price veto closed PASS.

**Critical Rules rows present only on staging:**

| Rule | Detail | Ref |
|---|---|---|
| Recommendation engine uses age├ùfault_severity matrix ΓÇö NOT pure-age trigger | `_compute_recommended_tier()` in `fault_estimate.py`: age_bucket (youngΓëñ7yr / mid_life 8-14yr / end_of_lifeΓëÑ15yr) ├ù fault_severity (easy: difficulty==easy AND repair<$400 / medium: repair<$800 / major: otherwise) ΓåÆ 9-cell matrix ΓåÆ recommended tier A/B/C. Old `_should_recommend_replacement()` is legacy shim (returns True iff tier==C). `recommend.py` lifecycle_rules DB overlay fires ONLY when condition_signalΓëá'default'. No DB migration. US-only fix ΓÇö PK pricing untouched. | DEC-090, 2026-05-29 |
| ReportClient.tsx `isRec` must read backend flag directly ΓÇö no tier-name hardcoding | Old: `const isRec = opt.recommended \|\| opt.tier === 'better'` caused Tier B to always show Recommended badge even when backend recommended Tier A. Fix (line 691): `const isRec = !!opt.recommended`. Never add tier-name fallback to isRec ΓÇö it overrides the backend recommendation signal. | WA-49, 2026-05-29 |

**QA-history stub row that appeared on staging (an incomplete duplicate of the completed `c009dbb` row main carries above; preserved verbatim for completeness):**

| 2026-05-22 | Houston + PK | 

## 2026-06-18 ΓÇö Audit framework activated + synthetic-event filtering shipped to PROD

Completed the `SnapAI_Audit_Framework_Setup` prerequisites and shipped the Sentry/PostHog
synthetic-event filters to production (commit `6f4925a` on `main`).

**Done:**
- MFA on primary Google account: already enabled (2-Step since Apr 5 + passkey).
- Railway compute cap raised $10 ΓåÆ $15.
- GitHub Dependabot enabled (graph/alerts/security/version updates) + `.github/dependabot.yml` on main.
- gitleaks: CLI (winget) + pre-commit hook + `.github/workflows/gitleaks.yml` on main. Semgrep CLI installed.
- Docker Desktop + OWASP ZAP image `ghcr.io/zaproxy/zaproxy:stable` (the doc's `owasp/zap2docker-stable` is dead).
- **Sentry + PostHog `before_send` synthetic-event filters** ΓÇö drop events during audit runs:
  - Backend (`scopesnap-api/main.py`): drops when env `SNAPAI_AUDIT_MODE=1`.
  - Frontend (`sentry.client.config.ts`, `PostHogProvider.tsx`): drops when `?audit_synthetic=1`
    OR `sessionStorage.snapai_audit_mode==='1'`. Sentry **replays** also suppressed (rates zeroed at init).
  - QA'd on staging (proven via live network + Sentry Issues), promoted to prod, re-QA'd on prod.
    Behaviour-neutral under normal operation (pure passthrough unless the audit flag is set).
- Clerk: 5 audit test users in BOTH apps. Audit auth = Clerk **sign-in tokens** (passwordless, no OTP).

**Deferred by choice:** Cloudflare Free WAF migration (mainnov.tech is on Hostinger DNS, not behind
Cloudflare). Next build: the `snapai-full-audit` skill itself.

See **DEC-090** for full decisions, corrections, and retrospective.


## 2026-06-21 - Security remediation batch QA (staging)
snapai-full-audit follow-ups remediated + merged to staging (detail in SECURITY_AUDIT_FINDINGS.md section H).
- Fixed on staging (pending prod promote): rate-limit public report/approve routes (#5); Stripe webhook idempotency (#7, migration 042 + processed_webhook_events table); public report trusts estimate.market not X-Market (#4 partial); JWKS kid-mismatch reject (#10); CORS localhost gated to non-prod + 2 broken API test loaders fixed (#11).
- QA: 145 API unit tests pass (was 122), full app import clean, Vercel staging build Ready, Clerk login harness PASS -> /dashboard, staging API (scopesnap-api-staging) Online, alembic_version=042, processed_webhook_events table present.
- Caught + REVERTED an SRI regression: experimental.sri broke Next bundle script loading at runtime on Vercel (Clerk failed to load, sign-in broke) despite a clean build.
- Pending YOU: rotate 3 leaked keys (#1), set CRON_SECRET + update caller (#2), promote staging->prod (#3). Open (decisions): authed-side market trust via company.market column, CSP nonce migration (#9), report_short_id URL scheme.
- Infra map confirmed: API staging = scopesnap-api-staging.up.railway.app (Railway env "staging" <- staging branch); API prod = scopesnap-api-production.up.railway.app (<- main). DBs: snapai-staging-use1 (now alembic 042) / snapai-prod-use1 (still 041 until promote). Vercel staging = scopesnap-web-staging (<- staging branch, Preview deploys).


