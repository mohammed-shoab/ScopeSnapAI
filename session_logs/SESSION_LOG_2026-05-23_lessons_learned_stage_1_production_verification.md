# SESSION LOG — Lessons Learned — 2026-05-23 Stage 1 Production Verification — 2026-05-23

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## Lessons Learned — 2026-05-23 Stage 1 Production Verification

BUG-040 and BUG-041 found and fixed. All 6 flows confirmed live on both markets.

| # | What We Learned | Detail | WA / DEC Ref |
|---|-----------------|--------|--------------|
| L36 | 2.5T commercial warning triggers on MANUAL TONNAGE text field, not buttons | Tonnage buttons only show 1.0T/1.5T/2.0T for current PK brands. To trigger the 2.5T commercial warning in QA, type "2.5" into the TONNAGE manual text input field. The warning appears triggered by the input value alone. | WA-40 |
| L37 | CAST(:options AS jsonb) required for JSONB INSERT in raw SQLAlchemy | BUG-040: `_generate_service_estimate()` in `api/diagnostic.py` bound `:options` to a JSONB column without explicit CAST. Silent failure — no exception, no row created. Fix: use `CAST(:options AS jsonb)` in the raw SQL. ALWAYS use explicit CAST for JSONB params. | DEC-072, WA-41 |
| L38 | diagnostic_questions table uses step_id column (not step_key), no market column | The `diagnostic_questions` table column is `step_id` (not `step_key`). The table has no `market` column — it is shared between US and PK markets. PSI thresholds (high_t, low_t) are stored here. All queries must use `step_id`. | — |
| L39 | NEXT_PUBLIC_ENV=staging on production Vercel is a recurring trap — verify after every env change | BUG-031 (2026-05-21) and BUG-041 (2026-05-23) are the same bug occurring twice. Each time: staging setup accidentally propagated `staging` value to the production project. Rule: after ANY Vercel env var change on any project, immediately open pk.snapai.mainnov.tech and confirm no amber STAGING banner. | DEC-073, DEC-023 |

### Bugs Fixed This Session

**BUG-040 (FIXED — diagnostic.py CAST fix) — Service flow never created estimate**
- **Root cause:** `_generate_service_estimate()` in `api/diagnostic.py` used `:options` without `CAST(:options AS jsonb)`. SQLAlchemy silently skipped the INSERT for the JSONB column.
- **Fix:** Added `CAST(:options AS jsonb)` to the INSERT statement
- **Verified:** Estimate rows now created after Service/Tune-Up flow completes

**BUG-041 (FIXED — Vercel env var + new deployment 8WLih2SBr) — Staging banner on pk.snapai.mainnov.tech**
- **Root cause:** `NEXT_PUBLIC_ENV=staging` in production Vercel project (All Environments)
- **Fix:** Set `NEXT_PUBLIC_ENV=production` in Vercel dashboard → All Environments → triggered new deploy
- **Verified:** pk.snapai.mainnov.tech confirmed clean (no amber banner)

---


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
