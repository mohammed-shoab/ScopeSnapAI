# SESSION LOG — Last QA Run — /snapai-qa on PRODUCTION (2026-06-17 PM) — 2026-06-17

**Retrofit note:** Extracted from `ACTIVE_TASKS.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS.md session block; the block also remains in ACTIVE_TASKS.md for chronological continuity.

**Source:** `ACTIVE_TASKS.md` (session block, extracted 2026-07-06)

---

## Last QA Run — /snapai-qa on PRODUCTION (2026-06-17 PM)
- **Target: PROD** (snapai.mainnov.tech). Run after Brand Decoder v1.2 promote (main `f70b6276`).
- **Phase 2 backend — PASS:** `/health` ok (db connected, environment:production); `/api/version` decoder/replace/brand_data **1.2** + `analytics_enabled:true`; prod DB (`zpsoprffaujswywtsgzy`) market data intact — **58 US brands / 15 PK brands**, York+Gree present, 19 US + 16 PK fault cards, **57 brands carry serial_decodable** (migration 039 backfill on prod); PSI thresholds **R-410A PK 125-145 ✓, R-32 PK 120-140 ✓** (R-22 US 60-82 vs skill-ref 88 — minor pre-existing reference nuance, not Brand-Decoder, not a regression); alembic head **040**.
- **Phase 1 UI (US prod, logged in) — PASS:** Flow 1 Not Cooling full diagnostic → Refrigerant Leak (High Conf) → estimate **rpt-592468** USD, **Finding-1 `[N]`→"At 18 years old…" substituted**, **Finding-2 Continue="Replace Immediately ($6,480)"=★REC**; Flow 6 nameplate manual entry inline-edit works; Flow 7 env-banner **correctly ABSENT** on prod (host=snapai.mainnov.tech, no StagingBanner, frontend PostHog env=`production`). a11y SidebarNav contrast clean.
- **Phase 1.5/1.6 — PASS (cited):** Playwright/axe CI run #5 on main `f70b6276` = **success 26/26** (the workflow triggers on push to staging AND main); backend pytest **120 passed** this session (`d7dbc2a8`, after fixing the `re`-loader regression); tsc clean via CI build.
- **Phase 1 UI (PK prod) — PASS (Shoab kept prod logged in; US+PK prod SHARE the same Clerk prod app, so the session carried over — no separate PK login needed).** Fresh PK diagnostic on pk.snapai.mainnov.tech: Gree (DWP Group), 1.5-ton, **R-410A** selector, install 2008 + Sure → Not Cooling → outdoor running YES → 55 PSI → **Refrigerant Undercharge/Leak (High Conf)** with PK-specific copy (soap-solution leak detect; "R-32 dominant in new PK split ACs, not interchangeable with R-410A") → estimate **rpt-076836** in **PKR**: ₨4,725 / ₨8,775 / ₨135,000. **Finding-1 LIVE:** Full Replacement reads "**At 18 years old**, complete system replacement shifts to R-32 or R-410A…" (real age, no `[N]`). **Finding-2 LIVE:** Continue = "Replace Immediately (₨135,000)" = ★REC. PK market routing (brands/fault-cards/currency) all correct on prod.
- **BOTH MARKETS now fully verified on production.** NOT individually re-run on prod: US Flows 2-5 (Service/Tune-Up, Water Dripping, Not Turning On) — covered by staging snapai-qa-master + identical promoted build. Skill's Phase 1.5 clone recipe is stale (pnpm/`SnapAIAI`/git@ SSH/`pak_diagnostic_questions`) — used real GitHub Actions CI + Supabase prod DB instead.
- **Minor obs (non-blocking):** opening a draft estimate's PDF before "Send" returns `estimate-rpt-…-unavailable.pdf` (PDFs generate on Send, not on draft) — expected behavior, noted.
- **Bugs found: 0** on prod. **QA result: PASS — both markets verified live on production.**


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS.md session block during Phase 3 retrofit (Option B).
