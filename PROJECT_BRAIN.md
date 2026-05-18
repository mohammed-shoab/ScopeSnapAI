# SnapAI — Project Brain

> Single source of truth for live URLs, infra IDs, deployment state, and architecture facts.
> Read this first at the start of every session. Update after every deploy or schema change.
>
> Last updated: 2026-05-18

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
| Vercel (both domains) | `6a8eecb` | Production Current Ready (1m 16s) | 2026-05-18 |
| Railway backend | `e1db2ac` (last Railway-touching commit) | Health OK | 2026-05-18 |
| Alembic migration | `019` (photo_policy_any_wildcard) | Applied | 2026-05-11 |

**Current git HEAD:** `6a8eecb` — "feat: auto-fill electrical specs (RLA/LRA/MCA/MOCP/Cap) from reference table on model select"

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
| `scopesnap-api/db/migrations/versions/` | Alembic migrations (current head: `019`) |

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
| 2026-05-18 | Houston only | PASS ✅ COMPLETE | 7 (BUG-011 badge + 5 CRLF stash truncations + BUG-012 electrical spec auto-fill) |
| 2026-05-15 | Houston + PK | PASS | BUG-010b (_complete_service_session rollback) |
| 2026-05-11 | Houston + PK | PASS | Multiple routing bugs, photo policy, inverter flag |

---

## Current Known Issues

- None. All issues from 2026-05-18 QA run resolved and live.

---

## Critical Rules for AI Sessions

1. **Never `git stash` from Linux sandbox** — truncates TSX/TS files on NTFS (DEC-013). Use WIP commits instead.
2. **All git ops via Desktop Commander `.bat` files** — sandbox cannot write `.git/` lock files on NTFS (DEC-004).
3. **Emoji files (DEC-005):** Never read from NTFS mount during git ops. Use `git cat-file blob <sha>`.
4. **Next Alembic migration must be `020`** — current head is `019`.
5. **PK changes always gated:** `detectMarket() === "PK"` in frontend, `tables.market == "PK"` in backend.
6. **After any merge:** run `git diff <last-good-sha>..HEAD -- 'scopesnap-web/**/*.tsx' --stat` to detect truncation before pushing.
