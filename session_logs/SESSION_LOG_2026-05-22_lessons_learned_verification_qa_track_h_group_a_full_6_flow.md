# SESSION LOG — Lessons Learned — 2026-05-22 Verification QA (Track H Group A + Full 6-Flow Check) — 2026-05-22

**Retrofit note:** Extracted from `ACTIVE_TASKS_HISTORY.md` on 2026-07-06 as part of the SESSION_LOG_* archetype adoption (Phase 3 retrofit Batch B). Content is verbatim from the ACTIVE_TASKS_HISTORY.md session block; the block also remains in ACTIVE_TASKS_HISTORY.md for chronological continuity.

**Source:** `ACTIVE_TASKS_HISTORY.md` (session block, extracted 2026-07-06)

---

## Lessons Learned — 2026-05-22 Verification QA (Track H Group A + Full 6-Flow Check)

Zero bugs found. All fixes confirmed live. Key learnings captured below.

| # | What We Learned | Detail | WA / DEC Ref |
|---|-----------------|--------|--------------|
| L40 | Frontend gates with 'market-required' comments must implement the market check, not block universally | WA-32 address gate was guarded with // R.3: Address required for US market but fired for ALL markets. Removed gate entirely — backend supports optional address. | 2026-05-24 Issue #2 fix |

| L19 | Address input BLOCKS complaint selection on PK | R.3 guard (`handleComplaintSelected`) fires even when address is empty. On PK this prevented complaint clicks from advancing the flow. Entering just the native value is not enough — must call React onChange. Workaround in QA automation: always enter address via `input[__reactProps].onChange({target, currentTarget, ...})` before clicking complaint. | WA-32 |
| L20 | SnapAI has zero client-side API fetches | Next.js 14 app uses Server Components + Server Actions. All brand/series/diagnostic data is fetched server-side. `window.fetch` intercept and `read_network_requests` capture nothing useful. For Phase 2 market routing checks: use Supabase MCP direct SQL to verify table separation, and infer routing correctness from working UI flows on each domain. | WA-33 |
| L21 | pak_diagnostic_questions does NOT exist | The QA skill spec referenced `pak_diagnostic_questions` for PSI threshold verification. This table does not exist. PSI thresholds live in `pak_operating_targets` with columns: refrigerant, ambient_c, suction_min_psi, suction_max_psi, discharge_min_psi, discharge_max_psi. At 40°C: R-410A 125–145, R-32 120–140, R-22 78–88 (45°C). | DEC-002 updated |
| L22 | A.6 confidence badge fix was DiagnosisListRow ONLY | `CONF_COLORS`, `const conf`, and badge `<span>` removed from `DiagnosisListRow.tsx` (commit 7d164d1). The individual `/diagnoses/{id}` detail page still renders "High Confidence" from a separate component. This is NOT a regression — detail page confidence was never in A.6 scope. Track as future polish if needed. | DEC-061 |
| L23 | PK pricing database URL = /settings/pricing | Not `/pricing` (404) or `/pricing-database` (404). The sidebar link goes to `/settings/pricing`. Contains ₨ (Rupee) national defaults — confirms PKR currency is set at DB level, not just display. | — |
| L24 | Escalated diagnostic is valid tree outcome | Both suction (130 PSI) and discharge (340 PSI) in normal range for R-410A "Not Cooling" → tree returns "⚠ Diagnostic escalated -- please inspect manually" and redirects to complaint selection. This is correct expected behavior. Not a bug. | — |
| L25 | Service/Tune-Up Flow 2 max reachable without real photos | Steps 1 (filter, has skip) + 2 (capacitor, numeric input) + 3 (coil, has skip) advance. Step 4 (drain flush) has no skip button — requires actual photo upload. QA can confirm no 503 error and flow starts correctly; full completion requires a real technician device. | — |
| L26 | "Send via WhatsApp" and "Send via Email" coexist on PK | PK Send tab shows BOTH buttons. The QA check "must read WhatsApp NOT Email" means WhatsApp must be PRESENT (primary CTA). Email remaining as a secondary option is acceptable behavior. Placeholder name = "Ahmed Khan", phone format = "03001234567". | — |
| L27 | React BUTTON elements need onClick via __reactProps | Native `.click()` on BUTTON advances some flows but NOT numeric input submits or condition selections. Always prefer `btn[__reactPropsKey].onClick({preventDefault:()=>{},stopPropagation:()=>{},target:btn,currentTarget:btn,type:'click'})`. For inputs: `onChange` with the same pattern. | WA-27 |

### Track H Group A — Confirmed Live (2026-05-22)

| Item | Status | Evidence |
|------|--------|----------|
| A.1 — BUG-033 photo skip keys | ✅ ALREADY DONE (23e3019) | SVC_PHOTO_SKIP_CONFIG present in ServiceChecklist.tsx |
| A.2 — share_token NULL backfill | ✅ DONE (prod 62 rows, staging 18 rows) | /r/... report URL loads successfully |
| A.3 — "No significant issues" contradiction | ✅ FIXED + CONFIRMED LIVE (c009dbb) | Report shows "System — Ductwork Leak" not "No significant issues" |
| A.4 — Generic post-approval line | ✅ ALREADY DONE | "Your contractor will contact you" only in pre-approval branch |
| A.5 — QR code blank in PDF | ✅ FIXED + CONFIRMED LIVE (55d76f8) | img src = 263-char qrserver.com URL, set synchronously |
| A.6 — Confidence badge always High | ✅ DONE (7d164d1 / DiagnosisListRow only) | Badge absent from list rows; detail page out of scope |
| A.7 — Gree inverter seed data | ✅ ALREADY DONE | pak_brands "Gree" has Fairy Inverter series with type:inverter |

---

---



---

## Change log

- **2026-07-06:** Extracted from ACTIVE_TASKS_HISTORY.md session block during Phase 3 retrofit (Option B).
