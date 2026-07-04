# SESSION LOG — Lessons Learned — 2026-05-21 QA Session (Tracks G + TCO + F + DX) — 2026-05-21

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## Lessons Learned — 2026-05-21 QA Session (Tracks G + TCO + F + DX)

Full workarounds in TECH_STACK.md WA-25 through WA-27. DEC entries: DEC-056, DEC-057.

| # | What Went Wrong | Root Cause | How We Fixed It | WA Ref |
|---|-----------------|-----------|-----------------|--------|
| L10 | Service/Tune-Up skip buttons absent from DOM despite code existing | Service/Tune-Up renders `ServiceChecklist.tsx`, not `DiagnosticFlow.tsx`. PHOTO_SKIP_CONFIG only lived in DiagnosticFlow — never reached for service complaints. | Duplicated skip config and UI directly inside ServiceChecklist.tsx | WA-25, DEC-056 |
| L11 | New Gree Fairy Inverter model didn't appear after DB seed | `modelCache.ts` stores models in **IndexedDB** with 24-hour TTL. Hard reload clears module memory but NOT IndexedDB. Stale IDB data served instead of fresh API fetch. | `indexedDB.deleteDatabase('snapai_models_pk')` + reload forces fresh fetch | WA-26, DEC-057 |
| L12 | Gree had no inverter models — QA spec for "Fairy Inverter" couldn't be tested | All 8 Gree series in `pak_brands` had `type: "non_inverter"`. pak_equipment_models does not exist — PK models are JSONB inside pak_brands.series[] | Added "Fairy Inverter" series with `type: "inverter"` to pak_brands via SQL | DEC-057 |
| L13 | React button clicks via `element.click()` didn't update state | React controlled components use synthetic events. Native `click()` / `dispatchEvent` bypass React reconciler entirely — state never updates. | Must call `element[__reactPropsKey].onClick()` or `.onChange()` directly | WA-27 |
| L14 | Staging banner on pk.snapai.mainnov.tech (BUG-031) | `NEXT_PUBLIC_ENV=staging` set in Vercel's Production environment config | Removed/corrected via Vercel dashboard → Environment Variables. No code change. | DEC-051 |

---


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
