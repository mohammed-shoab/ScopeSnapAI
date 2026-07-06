# SESSION LOG — Verification close-out (items 3/4/5) — 2026-06-17 — 2026-06-17

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## Verification close-out (items 3/4/5) — 2026-06-17

- **Item 5 (full backend pytest) — DONE, and caught a real regression.** Cloned scopesnap-api@staging + ran the suite: it was NOT clean — `test_fault_estimate_age_v2.py` failed at collection because its `_load_fault_estimate_funcs()` head-loader injects a fixed name set (Optional/math/datetime/timezone/logging) but NOT `re`, and the Finding-1 fix added `re`-using helpers in that head region → `NameError: name 're' is not defined`. Frontend Playwright CI is backend-blind so it didn't catch this. **Fixed** (`d7dbc2a8`): inject `re` into the loader. Suite now **120 passed, 0 errors** (was 105 passed + 1 collection error). New tests confirmed: test_finalize_replacement_copy 9/9, test_market_isolation 17/17.
- **Item 3 ([N] substitution path) + Item 4 (US side) — LIVE-VERIFIED on US staging.** Fresh diagnostic: Carrier, 3-ton, install **2008** + confidence **Sure** (reliable age) → Not Cooling → 55 PSI → Refrigerant Leak (High Conf) → estimate `rpt-925795` (`staging.snapai.mainnov.tech`, USD). Full Replacement ★REC reads **"At 18 years old, complete system replacement."** (substitution path — real age, not `[N]`, not stripped). Continue button = **"Continue with Replace Immediately ($6,480)"** (= ★REC tier). Both findings confirmed on US with the reliable-age substitution branch.

Staging tip after all fixes: **`d7dbc2a8`**.


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
