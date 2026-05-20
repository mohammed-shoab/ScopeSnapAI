# SnapAI — Project Brain

> Single source of truth for live URLs, infra IDs, deployment state, and architecture facts.
> Read this first at the start of every session. Update after every deploy or schema change.
>
> Last updated: 2026-05-20 (QA run post-track-F+DX. HEAD: 85c5755. BUG-025+BUG-026 fixed. Alembic 030. All .md files current.)

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


---

## Live URLs

### Production
| Market | Frontend | Status |
|--------|----------|--------|
| Houston (US) | https://snapai.mainnov.tech | ✅ Live |
| Pakistan (PK) | https://pk.snapai.mainnov.tech | ✅ Live |

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
| Vercel (both prod domains) | `85c5755` | Production Live | 2026-05-20 |
| Railway backend (prod) | `85c5755` | Health OK — "Deployment successful" | 2026-05-20 |
| Alembic migration (prod) | `030` | pak_diagnosis_feedback alternative_fault_id col | 2026-05-20 |
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

**Current git HEAD (main):** `85c5755` -- "fix(qa): seasonal_modifier_pct ORM column + handleContinue creates estimate before navigating"

**Recent commits (newest first -- main):**
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

## Architecture Quick Reference

- **Frontend:** Next.js (Vercel). Two domains, one deployment. Market detected via hostname → `detectMarket()` in `lib/market.ts`
- **Backend:** FastAPI (Railway). Single service. Market routed via `X-Market` header → `get_tables()` in `api/dependencies.py`
- **Database:** Supabase (PostgreSQL). US tables = standard names. PK tables = `pak_*` prefix.
- **Auth:** Clerk JWT. All protected endpoints require `Authorization: Bearer <clerk-token>`
- **Model data endpoint:** `GET /api/models/all` (with `X-Market` header) → returns all equipment records for that market
- **US models:** 76 records. Brands include Carrier, Goodman, Lennox, Rheem, Trane, York, etc.
- **PK models:** 72 records. Brands include Gree, Dawlance, Haier, Changhong Ruba, EcoStar, etc.

---

## Key Files — Frontend

| File | Purpose |
|------|---------|
| `scopesnap-web/lib/market.ts` | `detectMarket()`, `MARKET_CONFIG`, `formatCurrency()` |
| `scopesnap-web/lib/api.ts` | All typed API fetch wrappers, X-Market header injection |
| `scopesnap-web/lib/modelCache.ts` | Client-side model cache (`/api/models/all`), `getBrands()`, `searchModels()` |
| `scopesnap-web/components/StepZeroPanel.tsx` | Nameplate entry screen (Step 0) — brand/model lookup, DB badge, ✏ Edited badge, Est. electrical spec auto-fill |
| `scopesnap-web/components/diagnostic/DiagnosticFlow.tsx` | Main diagnostic step renderer |
| `scopesnap-web/app/(app)/assess/page.tsx` | New assessment page entry point |

## Key Files — Backend

| File | Purpose |
|------|---------|
| `scopesnap-api/api/diagnostic.py` | All diagnostic session logic, PSI routing, fault card return |
| `scopesnap-api/api/dependencies.py` | `get_tables()` — market routing, `_US_TABLES` / `_PK_TABLES` |
| `scopesnap-api/api/assessments.py` | Assessment CRUD |
| `scopesnap-api/api/fault_estimate.py` | Primary estimate engine -- `POST /api/estimates/fault-card`. Seasonal modifier, recommendation overlay, tier labels, markup, surcharges. |
| `scopesnap-api/api/estimates.py` | Estimate generation and retrieval |
| `scopesnap-api/db/migrations/versions/` | Alembic migrations (current head: `029` — applied via Supabase direct) |

---

## PSI Thresholds (from diagnostic_questions / pak_diagnostic_questions)

| Refrige

---

## QA History

| Date | Markets | Outcome | Bugs Fixed | Commit |
|------|---------|---------|------------|--------|
| 2026-05-20 (full audit) | Houston + PK | PASS ✅ | 53 items resolved | ba15901 |
| 2026-05-20 (post-track-F+DX) | Houston + PK | PASS ✅ | BUG-025, BUG-026 | 85c5755 |
