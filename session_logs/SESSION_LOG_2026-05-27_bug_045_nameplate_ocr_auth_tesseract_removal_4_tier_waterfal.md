# SESSION LOG — BUG-045 — Nameplate OCR Auth + Tesseract Removal + 4-Tier Waterfall — COMPLETE + LIVE 2026-05-27 — 2026-05-27

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## BUG-045 — Nameplate OCR Auth + Tesseract Removal + 4-Tier Waterfall — COMPLETE + LIVE 2026-05-27

| Check | Result |
|-------|--------|
| Root Cause A: JWT in OCR request (intercepted in Chrome) | PASS — `Authorization: Bearer <JWT>` + `X-Market: US` confirmed |
| Root Cause B: No Tesseract CDN requests | PASS — zero `cdn.jsdelivr.net` requests in performance entries |
| Old error string "Both AI and local OCR failed" absent from bundle | PASS — absent from `page-7542711e330724e9.js` |
| `nameplate_ocr_attempt` PostHog event in bundle | PASS — present in new chunk |
| Yellow border `#facc15` code in bundle | PASS — present in new chunk |
| Invisible failure: silent switch to manual tab on bad image | PASS — no error toast, UI on manual tab |
| New chunk hash deployed (page-7542711e330724e9.js) | PASS — old chunk 404, new chunk 200 + 109KB |
| US staging Railway health | PASS — `{"status":"ok","db":"connected","environment":"staging"}` |
| Flow 1 Not Cooling 128 PSI → NORMAL | PASS — `128 PSI (ok)` confirmed |
| Fault card returned end-to-end | PASS — Ductwork Leak, High Confidence |

**Git state:**
- `staging` branch HEAD: `25492dc` (Scenario D returning-user + Scenario E A/B variant)
- `main` branch HEAD: `3f06f0b` — PROMOTED TO PRODUCTION 2026-05-27 ✅
- Alembic: no migration — frontend-only change

**21-point acceptance QA: ALL PASS (2026-05-27)**
- Scenarios A–E × 2 markets: 10/10 ✅
- Negative tests NT-1 through NT-11: 11/11 ✅

**Additional fixes in this session (not in original BUG-045 scope):**
- Scenario C: photo persists on Tier-4 manual fallback (photo strip with "Tap to retake" in manual tab)
- Spinner text: "Gemini reading nameplate…" → "Reading nameplate…" (de-branded)
- Scenario D: returning user restores last-used tab via `snap_sz_path` localStorage
- Scenario E: new user A/B variant via `snap_sz_variant` + `ab_test_variant_assigned` PostHog event

**Note on bug numbering:** Commits were labeled BUG-034 due to an error; that number was already used for ServiceChecklist 401 (2026-05-22). Canonical number for this fix is **BUG-045**.

---


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
