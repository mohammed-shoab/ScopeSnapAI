# SESSION LOG — Phase 2 Ambient-Aware PSI Routing -- COMPLETE + LIVE -- 2026-05-24 — 2026-05-24

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## Phase 2 Ambient-Aware PSI Routing -- COMPLETE + LIVE -- 2026-05-24

| Check | Result |
|-------|--------|
| Alembic 036 on production (quqrvnoguofbjacrxcim) | PASS -- version_num=036 |
| Alembic 036 on staging (pqmgveqkuckbvyygsilk) | PASS -- version_num=036 |
| operating_targets: US rows (R-410A + R-22, 4 ambients each) | PASS -- 8 rows, market=US |
| operating_targets: PK rows intact | PASS -- 12 rows, market=PK |
| pak_operating_targets_v view | PASS -- VIEW exists, returns PK rows |
| Composite index idx_operating_targets_market_ref_amb | PASS -- created |
| hint_text updated (4 rows: q2-nc-suction/discharge, q2-hiss/wd-suction) | PASS -- ambient-aware wording |
| Railway production: deployment successful | PASS -- 84fedcf ACTIVE, Online |
| Health endpoint: environment=production | PASS -- {"status":"ok","db":"connected","environment":"production"} |
| PK pressure-targets API (R-410A @ 40C) | PASS -- suction 125-145, discharge 325-370 |
| PK pressure-targets API (R-32 @ 45C) | PASS -- suction 130-150, discharge 410-460 |
| Boundary test suite: 24/24 scenarios | PASS -- R-410A + R-22, all 3 ambients, LOW/NORMAL/HIGH |
| Ambient bucket resolution (amb=28 -> bucket 25) | PASS |

**Crash retrospective (DEC-086):**

| Event | Commit | Root Cause | Fix |
|-------|--------|------------|-----|
| 1st production crash | 291212b | UNIQUE(refrigerant, ambient_c) constraint blocked US row INSERT | Drop constraint in step 2b (83f8329) |
| 2nd production crash | e094192 | Duplicate step-2b block ran ADD CONSTRAINT twice -> duplicate error | Remove duplicate block |
| Manual DB migration | Supabase MCP | alembic upgrade head kept failing | 7 SQL steps + SET version_num=036 directly |
| Production recovered | 84fedcf | alembic sees 036 -> skips -> uvicorn starts clean | Confirmed Railway dashboard + /health |

**New DEC entries:** DEC-085 (Phase 2 architecture), DEC-086 (duplicate block crash)

**Lesson:** When a migration hotfix adds steps to an existing migration, staging masks the bug because the DB is already at that version. Grep ADD CONSTRAINT count = 1 before committing any migration change.

**Git state post-Phase 2:**
- main HEAD: 84fedcf (fix: remove duplicate 2b constraint block)
- staging HEAD: 536bc1f (same fix)
- Alembic: staging=036, production=036
- Railway: ACTIVE + Online on 84fedcf

---


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
