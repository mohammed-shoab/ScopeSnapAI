# SESSION LOG — OPEN BUG (found 2026-06-08 during post-migration QA) — PK FRONTENDS CANNOT REACH API — 2026-06-08

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## OPEN BUG (found 2026-06-08 during post-migration QA) — PK FRONTENDS CANNOT REACH API
Both PK frontends — pk.snapai.mainnov.tech (prod) AND pk-staging.snapai.mainnov.tech (staging) — show "API offline / Could not reach the API". Diagnosis: the API fetch is blocked CLIENT-SIDE (request never appears in the network log → "TypeError: Failed to fetch"). NOT CORS (backend CORS allowlist includes both pk origins; CORS-blocked requests would still appear in network). NOT the backend (healthy; US frontends reach the same API fine). NOT the DB migration (backend-only change). Killing the service worker + clearing caches did NOT fix it. Most likely a Content-Security-Policy `connect-src` directive on the PK frontend build that omits the API domain (scopesnap-api-*.up.railway.app), or a broken service-worker fetch handler (cf. DEC-079 SW passthrough). US frontends (snapai / staging.snapai) work fine — so this is PK-frontend-specific config. NOTE: in the pre-migration audit a raw fetch from the pk-staging origin DID reach the API, so this may have regressed at the frontend layer independently, or is SW-state dependent. PK DATA + BACKEND are verified correct (pak_ tables byte-exact in both Virginia DBs; backend serves X-Market=PK → 73 models). FIX LIKELY IN: scopesnap-web next.config.js CSP connect-src and/or sw.js for the PK build. Until fixed, PK users see "API offline".

---

### 2026-06-09 — PK "API offline" ROOT-CAUSED + staging FIXED (see DEC-092)
- **Root cause:** migration restore dropped 5 of 6 `pak_*_v` views (pak_fault_cards_v, pak_error_codes_v, pak_labor_rates_v, pak_replacement_costs_v, pak_lifecycle_rules_v). PK market path queries these views; missing → 503 no-CORS → "Failed to fetch". US unaffected.
- **DONE:** recreated all 5 views in Virginia **staging** from the prod backup; verified correct PK data; DB logs clean. Virginia **prod** already had all 6 — no change needed.
- **OPEN #1:** add the 5 views to an Alembic migration (currently not version-controlled — fragile to future restores).
- **OPEN #2:** dashboard "Recent Assessments" (`/api/estimates`, `/api/analytics`) still shows "API offline" — uses shared tables not views; DB clean; needs Railway/Sentry traceback (app-layer or browser-side).
- **OPEN #3:** `pk.snapai` (PROD) sign-in shows DEV Clerk ("ScopeSnapAI Staging", firm-chamois-61.accounts.dev) — verify prod Clerk wiring on the PK prod domain.
- **PROCESS FIX:** future migration verification must diff views/functions/sequences, not just table row counts.

---


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
