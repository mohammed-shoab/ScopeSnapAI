# SnapAI — Project Brain

> Single source of truth for live URLs, infra IDs, deployment state, and architecture facts.
> Read this first at the start of every session. Update after every deploy or schema change.
>
> Last updated: 2026-05-24 — Stage 6 Vercel Staging Branch Rewire COMPLETE. All 3 staging domains (staging.snapai.mainnov.tech, pk-staging.snapai.mainnov.tech, scopesnap-web-staging.vercel.app) now serve staging git branch via domain-level gitBranch setting. DEC-067 SUPERSEDED by DEC-080. main HEAD=ebe82f6c, staging HEAD=71bc7fea. | Previously: Stage 5 Staging DB & Branch Parity COMPLETE. Staging alembic=034 (was 025), git branch force-pushed to main HEAD 92034b3b, all 15 reference tables synced from prod. Health OK. Manual app smoke test pending Shoab login. | Previously: 2026-05-23 — Stage 3 Google Maps Integration COMPLETE. HoustonAddressAutocomplete live. DEC-078 (CSP) + DEC-079 (SW passthrough) added. BUG-042 (i18n placeholder) logged. GCP key restrictions DONE (HTTP referrer restrictions restored 2026-05-23: localhost:3000/*, snapai.mainnov.tech/*, staging.snapai.mainnov.tech/*). Code comments in next.config.js + sw.js erroneously reference DEC-076/DEC-077 for Maps -- correct refs are DEC-078/DEC-079. | Stage 4 Staging Isolation Audit COMPLETE. All 8 dimensions PASS. 2 critical cross-contaminations found and fixed (Railway sk_live_ on staging → sk_test_; pk.snapai.mainnov.tech ISR cache → fresh redeploy CwjgWfNBi). Staging branch Preview redeploy pattern confirmed (DEC-074). DEC-074/075/076/077 added. | Previously: Stage 1 Production Verification COMPLETE. BUG-040 (CAST(:options AS jsonb) fix in diagnostic.py), BUG-041 (NEXT_PUBLIC_ENV=production on Vercel prod, redeployed 8WLih2SBr). All 6 flows PASS both markets. L36-L39 added, DEC-072/073, WA-38/39. | Previously: Stage 2 Free-Tier Cost Audit COMPLETE. All 15 services verified. Total: $5.00/mo (Railway flat fee only). Supabase spend cap enabled, Railway $10 limit set. DEC-071 added. | Previously: 2026-05-23 — Full QA pass (both markets, all 6 flows, zero bugs). Brain files updated with lessons L28-L35, DEC-065/066, WA-28 through WA-37. | Previously: 2026-05-22 — STAGING FIX PLAN phases 1-10 complete. BUG-037 CONFIRMED LIVE. BUG-038-build FIXED. HEAD: 19db2d1. Alembic: 034. Staging: NEXT_PUBLIC_ENV=staging fixed+redeployed; DNS updated in Hostinger (mshoabarabi@gmail.com — NOT Cloudflare); custom domains pending propagation; scopesnap-web-staging.vercel.app VALID. StagingBanner = RSC in app/(app)/layout.tsx (auth-only routes). pak_diagnostic_questions does NOT exist — PSI thresholds in pak_operating_targets. Address input must be populated via React onChange BEFORE complaint selection (WA-32). A.6 scope = DiagnosisListRow only (DEC-061). PK pricing DB URL = /settings/pricing. Next.js uses SSR — no client-side API fetches visible (WA-33).
> Previous: Track H Group E complete: full Urdu translation live on pk.snapai.mainnov.tech. Dashboard, sidebar, Step Zero, homeowner report all translated. HEAD: b57d969. Alembic: 032. No open issues.)
> **2026-05-23 patch:** change workflow `WORKFLOW.md` + DEC-070 added — staging-first 7-step loop becomes mandatory after Stage 7 sign-off.

---

## Change Workflow (added 2026-05-23 — DEC-070)

**Every code, schema, env-var, or infra change uses the staging-first workflow defined in `WORKFLOW.md`.** The flow is: branch off `staging` → merge to `staging` → auto-deploys to staging.snapai.mainnov.tech + pk-staging.snapai.mainnov.tech → verify → run `scripts/promote-to-prod.sh <files>` → main updates → prod auto-deploys → verify on real domain.

**The four absolute rules (codified in DEC-070):**
1. Never edit code directly on `main` without going through `staging` first
2. Never push migrations to prod that haven't run on staging first
3. Never add env vars to prod without mirroring them on staging
4. Never test on production — testing happens on staging

**Activation status:** workflow becomes canonical and mandatory after Stage 7 sign-off (staging full QA matches a full prod QA pass). Current gaps resolved: staging DB at parity (Alembic 034, Stage 5 complete 2026-05-24); Vercel staging domains now serve `staging` branch via domain-level gitBranch (DEC-067 SUPERSEDED by DEC-080, Stage 6 complete 2026-05-24). Remaining: Stage 7 staging E2E QA must pass before DEC-070 activates.

For full protocol — migration handling, env var handling, hotfix path, rollback procedure, AI session bootstrap, worked examples — read `C:\Users\dell\My Drive\Personal Claude\ScopeSnapAI\WORKFLOW.md` in full before any change work.

---

## Critical Rules (Hard-Won — 2026-05-20)

> Full details in TECH_STACK.md WA-9 through WA-14. Read before starting new work.

| Rule | One-liner | Where |
|------|-----------|-------|
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
| NEXT_PUBLIC_ENV=staging on prod = recurring bug | BUG-031 (2026-05-21) and BUG-041 (2026-05-23) both caused by this. After ANY Vercel env var changes, verify production NEXT_PUBLIC_ENV is absent or "production". | DEC-023, DEC-073 |


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
**Vercel staging deploys:** `main` branch as Production (not `staging` branch Preview)

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
| Secrets reference | `C:\Users\dell\My Drive\Personal Claude\.staging_secrets.txt` (⚠ never commit) |

---

## Current Deployment State

### Production
| Layer | Commit | Status | Date |
|-------|--------|--------|------|
| Vercel (both prod domains) | `4db39be` (BUG-036 ServiceChecklist fix) | ✅ Auto-deploying | 2026-05-22 |
| Railway backend (prod) | `937b8c7` (BUG-035 estimates INSERT fix) | ✅ Auto-deploying | 2026-05-22 |
| Alembic migration (prod) | `034` | ✅ Applied (031 photo_skipped direct; 033 estimates.market; 034 card_tco_data) | 2026-05-21 |
| diagnostic_sessions.photo_skipped | BOOLEAN NOT NULL DEFAULT false | ✅ Applied directly (031 was skipped by Railway during outage) | 2026-05-21 |
| card_tco_data (US) | 57 rows | ✅ Seeded | 2026-05-21 |
| pak_card_tco_data (PK) | 45 rows | ✅ Seeded | 2026-05-21 |
| pak_data_defaults | 1 row (market=PK) | Seeded | 2026-05-19 |
| pak_operating_targets | PK PSI thresholds + R-32 (5 rows, 30-50C ambient) | Seeded | 2026-05-18 |

### Staging
| Layer | Commit | Status | Date |
|-------|--------|--------|------|
| Vercel staging (vercel.app URL) | `80df2e4` (redeploy BphSPPVbC) | ✅ Ready — Valid Configuration | 2026-05-22 |
| Vercel staging (custom domains) | Both custom domains live | ✅ DNS fixed 2026-05-23; Clerk key fixed 2026-05-23 — Preview redeploy 5HJ2piG8A | 2026-05-23 |
| NEXT_PUBLIC_ENV | `staging` | ✅ Set+saved (direct typing), redeployed | 2026-05-22 |
| Railway staging backend | `92034b3b` | ✅ Health OK, alembic=034 | 2026-05-24 |
| Supabase staging DB | All tables seeded (US + pak_*) | ✅ Full mirror of prod schema | 2026-05-19 |
| Alembic migration (staging) | `034` (migrations 026–034 applied, Stage 5 parity) | ✅ Applied | 2026-05-24 |
| pak_pricing_tiers (staging) | 45 rows (15 cards × 3 tiers) | ✅ Seeded | 2026-05-19 |
| pak_labor_rates (staging) | full_system_1ton/1_5ton_pkr backfilled | ✅ Updated | 2026-05-19 |
| Reference data parity (staging) | All 15 ref tables synced from prod (Stage 5) | ✅ Complete | 2026-05-24 |

**Staging git HEAD:** `92034b3b` — matches main HEAD (Stage 5 force-push 2026-05-24)
**Promote staging → prod:** `scripts/promote-to-prod.sh <file1> [file2 ...]` (run from a local main checkout)

**Current git HEAD (main):** `92034b3b` -- "docs: Stage 3 Google Maps sign-off — DEC-078/DEC-079, BUG-042" (latest as of 2026-05-24)

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
- None currently.

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

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           