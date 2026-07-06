# SESSION LOG — Stage 5 Sign-Off — Staging DB & Branch Parity — 2026-05-24 — 2026-05-24

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## Stage 5 Sign-Off — Staging DB & Branch Parity — 2026-05-24

| Check | Result |
|-------|--------|
| Code parity (git main = staging) | ✅ both 92034b3b |
| Schema parity (alembic_version) | ✅ 034 on both prod and staging |
| Reference data parity (15 tables) | ✅ all row counts match prod |
| Health endpoint | ✅ `{"status":"ok","db":"connected","environment":"staging","version":"0.1.0"}` |
| App-level smoke test | ⚠ Manual — requires Shoab login to staging.snapai.mainnov.tech |

**Reference table row counts (prod = staging):**
brands=15, data_defaults=1, fault_cards=19, labor_rates_houston=1, lifecycle_rules=44,
pak_brands=15, pak_data_defaults=1, pak_fault_cards=16, pak_labor_rates=1,
pak_lifecycle_rules=5, pak_operating_targets=12, pak_pricing_tiers=45,
pak_replacement_costs=4, pricing_tiers=57, replacement_cost_estimates=8

**Issues encountered:** `operating_targets` (US) table does not exist on either env — not in scope.
`pak_fault_card_descriptions` / `pak_fault_card_urdu_descriptions` tables do not exist — descriptions
are embedded in pak_fault_cards JSONB columns. pak_fault_cards synced via psycopg2 direct-connect
(16 rows) due to RLS blocking anon REST reads on production.

Stage 5 complete. Ready for Stage 6 (Vercel Staging Branch Rewire — DEC-067 fix).

> Tracks in-flight work, recent completions, and backlog.
> Updated by QA/dev sessions. Read this before starting any new work.
>
> Last updated: 2026-05-24 (Stage 8 COMPLETE. All 8 stages signed off. STAGING_MIRROR_CLOSEOUT.md written. | Stage 7 Staging E2E QA COMPLETE. DEC-070 ACTIVE. | Stage 3 Google Maps Integration COMPLETE. HoustonAddressAutocomplete live on snapai.mainnov.tech. DEC-078/DEC-079 added. BUG-042 logged. | Stage 4 Staging Isolation Audit COMPLETE. All 8 dimensions PASS. 2 critical contaminations fixed. DEC-074/075/076/077 added. | Stage 1 Production Verification COMPLETE. BUG-040 + BUG-041 fixed. All 6 flows PASS. L36-L39 added.) | Previously: (Stage 2 Free-Tier Cost Audit COMPLETE. Total spend $5.00/mo. All 15 services verified. Supabase spend cap enabled. DEC-071 added.) | Previously: 2026-05-23 (Full QA pass both markets -- all 6 flows PASS. Lessons L32-L35 added. DEC-065/066 added. WA-28 through WA-37 added to TECH_STACK.) | Previous: 2026-05-22 (Staging Fix Plan COMPLETE — all phases 1-10 done. NEXT_PUBLIC_ENV=staging fixed+redeployed. DNS updated in Hostinger. scopesnap-web-staging.vercel.app VALID. Custom domains pending DNS propagation. Production: HEAD 19db2d1, Alembic 034. No open production bugs.) | **2026-05-23 patch:** `WORKFLOW.md` + DEC-070 added (staging-first workflow).

---


---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
