# SESSION LOG — QA RUN — 2026-06-09 (snapai-qa, all 4 surfaces) — 2026-06-09

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## QA RUN — 2026-06-09 (snapai-qa, all 4 surfaces)

**Surfaces:** US prod (snapai.mainnov.tech), PK prod (pk.snapai.mainnov.tech), US staging (staging.snapai.mainnov.tech), PK staging (pk-staging.snapai.mainnov.tech). **Outcome: PASS.**

**Backend health:** prod + staging `/health` → `{"status":"ok","db":"connected"}`.

**Engine data (BOTH Virginia DBs at Alembic 037):**
- equipment_models 76; fault_cards US 19 / PK 16 (view == base); operating_targets US 8 / PK 12 (ambient-aware per DEC migration 036).
- PSI thresholds @35°C: US R-410A 115–140 (128 PSI → NORMAL ✓); PK R-410A 115–135 (130 PSI → NOR
---


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
