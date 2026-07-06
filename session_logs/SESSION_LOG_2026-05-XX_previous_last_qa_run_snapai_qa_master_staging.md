# SESSION LOG — Previous Last QA Run (snapai-qa-master, staging) — 2026-05-XX

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## Previous Last QA Run (snapai-qa-master, staging)
- Date: 2026-06-16
- Layers run: 1 (pre-deploy code), 2 (staging), 3 (promote-gate readiness), 5 (brain update). Layer 4 N/A — prod held for go.
- Markets: Houston + PK (both)
- Result: Layer 1 PASS (backend pytest 94/94; a11y PASS static WCAG AA — 5 issues fixed; Playwright SKIPPED — no browser binary in sandbox; quality-playbook SKIPPED — protocols not generated) | Layer 2 PASS (US+PK API/data routing + schema + backfill 57 + version cols; **Chrome UI audit on US staging: 3A StepZeroPanel install-year+confidence+Ask-homeowner+refrigerant-by-year hint, 3B report correction 3 paths, 3C chooser-gate banner + show-the-math panel (remaining-life band 1-4yrs, 5 weighted factors 0.78) all render LIVE; real-page console clean**; PK UI SKIPPED — separate Clerk login; isolation SKIPPED — authed writes) | Layer 3 NO-GO (checkpoint 2 schema parity: staging 040 vs prod 038 BY DESIGN — 039+040 intentionally not promoted; checkpoints 3,6 SKIPPED — no Railway/Vercel env+log tools)
- Chrome audit findings (LOW, non-blocking): dev-only /test-harness/report throws React #418/#422 hydration (client-mounts SSR component; prod-guarded, returns null in prod); harness report fixture shows "Approve undefined"/"—" (fixture lacks option totals); PK footer em-dash mojibake "â" (pre-existing, not Stage 3).
- Bugs found: 0 new this run (build-time: duplicate alembic 036 + PK serial_decodable — both fixed in-loop earlier)
- Bugs fixed in-loop: 0 (this run)
- Notable findings: Brand-Decoder v1.2 Stages 1-6 + glue live on staging (tip 01ef5d0, head 040). analytics_enabled=false (POSTHOG_API_KEY unset on Railway staging — owner action). Interactive UI QA blocked by Vercel SSO; covered by Stage 7 field walkthrough. Prod held for explicit go.


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
