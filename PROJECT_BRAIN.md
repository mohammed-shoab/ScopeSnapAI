# SnapAI — Project Brain

> Single source of truth for live URLs, infra IDs, deployment state, and architecture facts.
> Read this first at the start of every session. Update after every deploy or schema change.
>
> Last updated: 2026-05-22 — BUG-037 CONFIRMED LIVE: PKR prices render correctly on Houston domain (rpt-701093: Rs.5,906/Rs.10,969/Rs.14,808). BUG-038-build FIXED: package-lock.json removed (78d0fff had added 7954-line lockfile breaking every Vercel build in ~8s; repo intentionally has no lockfile since c2eac8d). HEAD: 19db2d1. Alembic: 034. Alembic: 034. pak_diagnostic_questions does NOT exist — PSI thresholds in pak_operating_targets. Address input must be populated via React onChange BEFORE complaint selection (WA-32, blocks on PK). A.6 scope = DiagnosisListRow only; /diagnoses/{id} detail still shows confidence (DEC-061). PK pricing DB URL = /settings/pricing. Next.js uses SSR — no client-side API fetches visible (WA-33).
> Previous: Track H Group E complete: full Urdu translation live on pk.snapai.mainnov.tech. Dashboard, sidebar, Step Zero, homeowner report all translated. HEAD: b57d969. Alembic: 032. No open issues.)

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
| PK models live in pak_brands JSONB, not equipment_models | pak_equipment_models does not exist. PK models = pak_brands.series[] JSONB array. `type: "inverter"` drives the inverter badge. After seeding, clear IndexedDB cache. | DEC-057, WA-26 |
| IndexedDB model cache = 24h TTL | After updating pak_brands, browser shows stale models for 24h. Force-clear: `indexedDB.deleteDatabase('snapai_models_pk')` + reload. localStorage has no model cache. | WA-26 |
| React controlled components ignore native events | `element.click()` and `dispatchEvent` do NOT update React state. Must call `element[__reactPropsKey].onChange/onClick()` directly. | WA-27 |
| estimates table has NO updated_at | INSERT INTO estimates must NOT include updated_at — column does not exist. Omit it. BUG-035 caused silent failure in _generate_service_estimate. | DEC-059, WA-28 |
| POST /api/estimates/service does NOT exist | ServiceChecklist must call onComplete() directly after service_step_complete. Backend auto-generates estimate. Frontend must NEVER POST to this missing endpoint. | DEC-060, WA-29 |
| ServiceChecklist needs getAuthHeaders callback | Pass `getAuthHeaders: () => Promise<headers>` — NOT pre-baked authHeaders. Clerk JWTs expire in 60s; a pre-baked token always expires during a service checklist session. | DEC-058, WA-30 |
| Edit tool truncates NTFS .md files too | DEC-027 applies to ALL files with non-ASCII (emoji, arrows, dashes). Use Python replace() via Desktop Commander. If truncated: `git cat-file blob <sha>` to restore, then patch via Python. | DEC-027, WA-31 |
| `/api/brands` does NOT exist | Use `/api/models/all` with X-Market header. Response is `{models:[...]}` — parse as `data.models`, never `Array.isArray(data)`. | arch note |
| `pak_diagnostic_questions` does NOT exist | PK PSI thresholds live in `pak_operating_targets` (refrigerant, ambient_c, suction_min_psi, suction_max_psi). suction_max_psi IS the high threshold (R-410A=145, R-32=140, R-22=88 at 40-45C). | arch note |


---

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
| US Staging | https://staging.snapai.mainnov.tech | ✅ Live |
| PK Staging | https://pk-staging.snapai.mainnov.tech | ✅ Live |
| Vercel default | https://scopesnap-web-staging.vercel.app | ✅ Live |

**Backend (Railway staging):** https://scopesnap-api-staging.up.railway.app
**Health endpoint:** `GET /health` → `{"status":"ok","db":"connected","environment":"staging","version":"0.1.0"}`
**Staging banner:** amber bar "⚠ STAGING — not production data" visible on all pages

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
| Alembic migration (prod) | `032` | ✅ Applied (031 photo_skipped applied directly via Supabase MCP) | 2026-05-21 |
| diagnostic_sessions.photo_skipped | BOOLEAN NOT NULL DEFAULT false | ✅ Applied directly (031 was skipped by Railway during outage) | 2026-05-21 |
| card_tco_data (US) | 57 rows | ✅ Seeded | 2026-05-21 |
| pak_card_tco_data (PK) | 45 rows | ✅ Seeded | 2026-05-21 |
| pak_data_defaults | 1 row (market=PK) | Seeded | 2026-05-19 |
| pak_operating_targets | PK PSI thresholds + R-32 (5 rows, 30-50C ambient) | Seeded | 2026-05-18 |

### Staging
| Layer | Commit | Status | Date |
|-------|--------|--------|------|
| Vercel staging (both staging domains) | `980698b` | Staging Live | 2026-05-19 |
| Railway staging backend | `980698b` | Health OK, alembic=025 | 2026-05-19 |
| Supabase staging DB | All tables seeded (US + pak_*) | Full mirror of prod schema | 2026-05-19 |
| Alembic migration (staging) | `025` (pak_fault_card_urdu_descriptions) | Applied | 2026-05-19 |
| pak_pricing_tiers (staging) | 45 rows (15 cards × 3 tiers) | Seeded | 2026-05-19 |
| pak_labor_rates (staging) | full_system_1ton/1_5ton_pkr backfilled | Updated | 2026-05-19 |

**Staging git HEAD:** `980698b` — "chore(staging): migrations 020-025 + dual keepalive A/B + promote-to-prod.sh"
**Promote staging → prod:** `scripts/promote-to-prod.sh <file1> [file2 ...]` (run from a local main checkout)

**Current git HEAD (main):** `19db2d1` -- "chore: remove [MKT:] debug marker from REF line"

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

**Architecture facts — estimates table:**
- `estimates` table columns: id, assessment_id, company_id, report_token, report_short_id, options, selected_option, total_amount, deposit_amount, markup_percent, status, viewed_at, approved_at, stripe_payment_intent_id, contractor_pdf_url, homeowner_report_url, sent_via, sent_at, actual_cost, accuracy_score, created_at, seasonal_modifier_pct, market
- NO `updated_at` column — any INSERT must omit it
- `market` VARCHAR(2) NOT NULL DEFAULT 'US' — added migration 034. Stamped at estimate creation in fault_estimate.py + diagnostic.py. Used by reports.py to return stored market to report viewer. ReportClient.tsx reads report.market to drive currency formatting (overrides detectMarket()).
- Service estimate: auto-generated by `_generate_service_estimate()` in diagnostic.py when svc-8-run answer returns. Frontend must NOT call POST /api/estimates/service — it does not exist. After service_step_complete, call onComplete() directly; backend estimate is accessible at GET /api/estimates/{assessment_id}.

**Resolved issues:**
- BUG-038-build: RESOLVED 2026-05-22. Root cause: commit 78d0fff accidentally included scopesnap-web/package-lock.json (7954 lines) -- repo intentionally has no lockfile since c2eac8d (force Node 18 fix, March 2026). Vercel npm ci failed in ~8s on every subsequent build. 7 consecutive builds all failed. Fix: `git rm scopesnap-web/package-lock.json` -- commit a908eac. RULE: never commit package-lock.json to this repo. See DEC-065.
- BUG-037: ✕estimates table missing market column✕ — RESOLVED 2026-05-22. Root cause: estimates table had no market stamp; PK estimates viewed on Houston domain displayed PKR amounts formatted as USD. Fix: migration 034 adds market VARCHAR(2) DEFAULT 'US'; fault_estimate.py + diagnostic.py stamp market at creation; reports.py returns market in response; ReportClient.tsx derives currency from report.market not detectMarket(). Commit 1b86b77.
- BUG-033b: ✕Houston fault_cards missing Better-tier (middle) copy for all 19 cards✕ — RESOLVED 2026-05-22. Root cause: migration 021 added Good+Best tiers but skipped Better tier entirely. The 'Why recommended?' collapsible in ReportClient.tsx requires non-null why_recommended to render. Fix: migration 033 populates description+why_recommended for all 19 cards. Applied directly via Supabase SQL + migration for Alembic record. Commit 1b86b77.
- BUG-033: ╳Service/Tune-Up skip buttons not in DOM╳ — RESOLVED 2026-05-21. Root cause: ServiceChecklist.tsx (not DiagnosticFlow.tsx) renders the service flow; PHOTO_SKIP_CONFIG was never reached. Fix: SVC_PHOTO_SKIP_CONFIG + skip UI added to ServiceChecklist.tsx. Commit 23e3019.
- BUG-031: ╳Staging banner on `pk.snapai.mainnov.tech`╳ — RESOLVED 2026-05-21. Re-regression 2026-05-22 confirmed false alarm — NEXT_PUBLIC_ENV already set to "production" (All Environments) in Vercel. pk.snapai.mainnov.tech verified clean 2026-05-22.

---

## Architecture Quick Reference

- **Frontend:** Next.js (Vercel). Two domains, one deployment. Market detected via hostname → `detectMarket()` in `lib/market.ts`
- **Backend:** FastAPI (Railway). Single service. Market routed via `X-Market` header → `get_tables()` in `api/dependencies.py`
- **Database:** Supabase (PostgreSQL). US tables = standard names. PK tables = `pak_*` prefix.
- **TCO tables:** `card_tco_data` (US, 57 rows) + `pak_card_tco_data` (PK, 45 rows). Keyed on `(card_id, tier)`. Served via `_enrich_tco_from_db()` in `estimates.py`.
- **Auth:** Clerk JWT. All protected endpoints require `Authorization: Bearer <clerk-token>`
- **Model data endpoint:** `GET /api/models/all` (with `X-Market` header) → returns `{models: [...]}` (NOT a plain array). Parse as `data.models`. `/api/brands` does NOT exist (404).
- **PSI thresholds table:** `pak_operating_targets` (columns: refrigerant, ambient_c, suction_min_psi, suction_max_psi). `pak_diagnostic_questions` does NOT exist in prod Supabase. At 40°C: R-410A max=145, R-32 max=140. R-22 max=88 at 45°C.
- **US models:** 76 records. Brands include Carrier, Goodman, Lennox, Rheem, Trane, York, etc.
- **PK models:** 73 records (confirmed 2026-05-22). Brands include Gree, Dawlance, Haier, Changhong Ruba, EcoStar, etc.

---

## Key Files — Frontend

| File | Purpose |
|------|---------|
| `scopesnap-web/lib/market.ts` | `detectMarket()`, `MARKET_CONFIG`, `formatCurren