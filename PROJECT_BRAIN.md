# SnapAI — Project Brain

> Single source of truth for live URLs, infra IDs, deployment state, and architecture facts.
> Read this first at the start of every session. Update after every deploy or schema change.
>
> Last updated: 2026-05-19 (Stream B PK QA fixes — DATA-GAP-001/002 verified, B.3 R-32 audit complete)

---

## Live URLs

| Market | Frontend | Status |
|--------|----------|--------|
| Houston (US) | https://snapai.mainnov.tech | ✅ Live |
| Pakistan (PK) | https://pk.snapai.mainnov.tech | ✅ Live |

**Backend (Railway):** https://scopesnap-api-production.up.railway.app
**Health endpoint:** `GET /health` → `{"status":"ok","db":"connected","environment":"production","version":"0.1.0"}`

---

## Infrastructure IDs

| Service | ID / Reference |
|---------|---------------|
| Railway project | `0e78dd68-ce72-46be-a2b1-7d3119de40a4` |
| Railway service | `a23d5cad-d8c9-434e-a3dc-89634d8642ab` |
| Railway environment | `03c478ed-5720-427a-b567-d6bd2ebf3eb1` |
| Supabase project | `quqrvnoguofbjacrxcim` |
| Vercel project | `scope-snap-ai` (mohammed-shoabs-projects-7844119e) |
| GitHub repo | `mohammed-shoab/ScopeSnapAI` |

---

## Current Deployment State

| Layer | Commit | Status | Date |
|-------|--------|--------|------|
| Vercel (both domains) | `17d19fd` | Production Live | 2026-05-19 |
| Railway backend | `01082c6` | Health OK | 2026-05-19 |
| Alembic migration | `021` (fault_card_descriptions) | Applied | 2026-05-19 |
| pak_data_defaults | 1 row (market=PK) | Seeded | 2026-05-19 |
| pak_operating_targets | PK PSI thresholds + R-32 (5 rows, 30–50°C ambient) | Seeded | 2026-05-18 |

**Current git HEAD:** `c6ef5df` — "[hotfix] Q.7 — Refresh draft estimates on load with latest fault card descriptions"

**Recent commits (PK SOW Addendum):**
- `17d19fd` — fix(A-4): PK homeowner name placeholder shows Ahmed Khan (Vercel frontend)
- `01082c6` — fix(BUG-016): PK ok suction → discharge PSI step, not US Card 13 (Railway backend)
- `0ce93a8` — fix(BUG-015): add X-Market header to getAuthHeaders so PK diagnostic routing hits pak_* tables

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
| `scopesnap-api/api/estimates.py` | Estimate generation and retrieval |
| `scopesnap-api/db/migrations/versions/` | Alembic migrations (current head: `021`) |

---

## PSI Thresholds (from diagnostic_questions / pak_diagnostic_questions)

| Refrigerant | Normal range (suction) | high_min |
|-------------|----------------------|---------|
| R-410A (US) | 108–144 PSI | 145 PSI |
| R-410A (PK) | 125–144 PSI | 145 PSI |
| R-22 | 55–87 PSI | 88 PSI |
| R-32 (PK) | 115–139 PSI | 140 PSI |

**Test case (Houston):** 128 PSI R-410A → NORMAL ✅ (confirmed 2026-05-18)

---

## QA History

| Date | Markets | Outcome | Bugs Fixed |
|------|---------|---------|-----------|
| 2026-05-19 | PK only (SOW Addendum) | PASS ✅ COMPLETE | 2 (BUG-015 X-Market header, BUG-016 PK suction PSI routing); A-2/A-4/A-5 verified; B-1/C-3 seeded |
| 2026-05-18 | Houston only | PASS ✅ COMPLETE | 7 (BUG-011 badge + 5 CRLF stash truncations + BUG-012 electrical spec auto-fill) |
| 2026-05-15 | Houston + PK | PASS | BUG-010b (_complete_service_session rollback) |
| 2026-05-11 | Houston + PK | PASS | Multiple routing bugs, photo policy, inverter flag |

---

## Current Known Issues

- PK flows 2–4 + 6 not yet fully end-to-end verified (partial PK QA — A-2/A-4/A-5/DATA-GAP-001/002/B.3 confirmed; full flow suite pending next session)
- Urdu toggle functional test not yet verified
- `pak_diagnostic_questions` table does NOT exist in production — PK diagnostic routing handled by PK-gated intercept in `diagnostic.py` (BUG-016 workaround, commit `01082c6`); no separate R-32/inverter question tree in DB
- `pak_operating_targets` R-32 notes say "Typical split AC" — should be "Inverter split AC only"; awaiting Shoab approval for data-only UPDATE (no migration needed; see ACTIVE_TASKS.md backlog)
- TECH_STACK.md contains stale SQL for DATA-GAP-001 (`UPDATE pak_brands SET inverter = true WHERE series_name IN (...)`) — both columns (`inverter`, `series_name`) do not exist in 