# SESSION LOG — 2026-06-20 — Day 1-5 Estimate Builder bug fixes: STATUS — 2026-06-20

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## 2026-06-20 — Day 1-5 Estimate Builder bug fixes: STATUS

**RESOLVED (live on staging + prod):**
- [x] Bug 1 — markup leak: line items now sum to displayed total
- [x] Bug 3 — PresentMode Slide 1: real photo + health badge + footer + 28-char truncation
- [x] Bug 4 — report URL clickable + Preview button (in the LIVE `assessment/[id]` builder)
- [x] Bug 5 — replacement semantics: 4 distinct component line items
- [x] Level 2 wording shipped (57 DEC-088-compliant strings)
- [x] Warranty field: Alembic 041 + Settings UI + homeowner-report render
- [x] DEC-088 enforcement: 6 pre-existing banned-word strings scrubbed

**DEFERRED / BACKLOG:**
- [ ] **Bug 2 — PDF 404:** `/files/pdfs/...-unavailable.pdf` has no route handler; needs Railway-log root-cause (generation exception vs R2 upload). Add a friendly 503 handler + fix the generator.
- [ ] **DEC-113 — Turbopack CSS/PostCSS migration** (frontend builds via webpack for now).
- [ ] Clean up: `estimate/[id]/page.tsx` is dead/legacy — consider deleting to avoid future wrong-file edits.
- [ ] Level 3 PK English wording / Level 4 PK Urdu (deferred per PK Market Positioning).
- [ ] Per-contractor markup warning at >100% (Taleb mitigation, separate ticket).

**Last QA:** 2026-06-20, staging + prod, Houston market, Bug 1/3/4/5 + Level 2 + warranty verified live in-browser. Build green (Vercel). Bug 2 deferred.

---


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
