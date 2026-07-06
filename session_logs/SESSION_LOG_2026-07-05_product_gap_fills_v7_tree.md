# SESSION LOG — v7 Diagnostic Tree Build + Tier A/B/C Product Gap-Fills — 2026-07-05

**Duration:** ~3 hours
**Participants:** Shoab + Bryan Orr (board — HVAC domain) + Mark Delgado (board — product strategy) + Will (board — stats) + Joe (board — research)
**Related workstream:** Adding new complaint cards (workstream #2 of the 4 active)
**Related files:**
- v7 tree: `SnapAI_Decision_Tree_v7_full_diagram.html`
- Product continuation prompt: `SnapAI_Product_Discussion_Continuation_Prompt.md`
- Product verbatim transcript: `SnapAI_Product_Discussion_Verbatim_Transcript_2026-07-05.md`
- Companion legal thread: `session_logs/SESSION_LOG_2026-07-05_deep_legal_audit.md`

## Context (what we started with)

960-episode HVAC School podcast transcript archive scanned, gap analysis complete. Bryan proposed additions vs LIVE state. v5 tree audit-corrected to v5.1. v6 gap-fills doc created (card-grid format). Shoab wanted a branching-diagram version with LIVE + NEW branches distinguished.

## Goal (what we tried to accomplish)

1. Build v7 branching diagnostic tree HTML showing LIVE + NEW branches distinguished
2. Verify percentages of live vs new fault coverage
3. Enumerate every blue (Question) and orange (Escalate) node with LIVE/NEW status
4. Get to a formal build queue with Tier A/B/C sequencing

## What we tried (chronological)

1. **v7 tree build** — full branching HTML with 6 color legend (GREEN=LIVE, PURPLE=NEW, RED=NEW+SAFETY, YELLOW-dashed=cross-cutting sub-flow, BLUE=Question node type, ORANGE=Escalate node type). 10 complaint tabs (A-J including new Comfort Complaint tab J). 3 cross-cutting sub-flows (Airflow Assessment, Vacuum Validation, Combustion Safety Check). 2 card families expanded (#10 → 10a-e, #15 → 15a-d).
2. **Will + Joe fault frequency stats** — ranked table of 29 fault types Houston-weighted. Cross-triangulated 5 sources (ACHR News surveys, warranty databases, DOE Building America, ENERGY STAR audits, Bryan's 960-episode archive, manufacturer warranty reports).
3. **Coverage math** — Lens 1 (surface breadth: LIVE 55%, NEW 45%) vs Lens 2 (call-resolution weighted: LIVE catches root cause 72-78%, NEW adds 17-22%, permanent tech-judgment residual 5-8%). Executive framing: "3 out of 4 today, 9 out of 10 with gap-fills."
4. **Blue/orange enumeration** — 33 blue nodes (all LIVE, coincidence of how tree was coded), 11 orange nodes (7 LIVE + 4 NEW). NEW oranges are RETURN/HOLD outcomes inside the 3 cross-cutting sub-flows.
5. **11-item build queue** — Mark reframed color-by-color into engineering-ticket form: 8 big builds (cards + tabs) + 3 cross-cutting sub-flows + 4 reading/step expansions.
6. **Bryan's 3-tier ship proposal** — Tier A (4-6 weeks): #20 Airflow, #22 Latent, #23 Thermostat, #24 Oversizing, Airflow sub-flow, superheat/subcool discrim, Comfort tab J. Tier B (+6-8 weeks): #10 family, #15 family, Vacuum sub-flow. Tier C: Card #21 HX + Combustion — gated on legal review.
7. **Card #21 pivot to legal thread** — Bryan raised CO liability. Discussion forked into Alfred-led legal thread (separate session log 2026-07-05_deep_legal_audit).

## What worked

1. **Full color legend** — 6-color scheme with status vs node-type distinction. Mark suggested legend split for v7.1 clarity.
2. **Will + Joe fault frequency triangulation** — 5 sources cross-checked with confidence-level column (high/medium/low). Realistic numbers, not aspirational.
3. **Card #8 discrimination insight** — Bryan flagged that 40-50% of current "Card #8 refrigerant leak" fires are actually #15b (TXV bulb loss), #10c (compression ratio), or #20 (under-airflow). Superheat/subcool discrimination is the highest-leverage single fix.
4. **B2B/B2C-like split (for product)** — cross-cutting sub-flows as reusable modules called by multiple complaint flows (Airflow feeds 4 complaints; Vacuum injects before any charge action; Combustion auto-triggers on aged/high-TESP furnace calls).
5. **Tiered ship proposal with legal gate on Tier C** — clean sequencing that gets 80% of value in 6 weeks vs 3 months of "build everything."

## What DIDN'T work

1. **Initial "build everything" ambition** — Shoab wanted all 11 items shipped simultaneously to make the app "perfect." Bryan pushed back with 5 issues: (1) can't validate rare-fire cards without months of data, (2) Card #21 CO liability is a different category of risk, (3) sub-flows are 3-4x the engineering of individual cards, (4) LLM cost per diagnosis climbs 40-60% with all cards active, (5) cognitive load spikes on techs.
2. **v7 legend design** — 6 colors mixing status (LIVE/NEW) and node-type (Question/Escalate) confused readers. Mark proposed a 2-box split for v7.1.
3. **Card #10 sub-mode field validation blindspot** — Cards #10a-e each fire on <1% of calls. At 80 calls/day Houston pilot volume, Card #10e Crankcase Heater fires ~once every 30 days. Shipping without field validation = shipping blind.

## Root causes

1. **"Build everything" ambition** was a completeness-optimization vs velocity-optimization tradeoff. Completeness wins on marketing story; velocity wins on real-world learning.
2. **v7 legend confusion** — mixed two orthogonal dimensions (build status × node function) in one visual language. Mark's 2-box split separates them.
3. **Card #10 family blindness** — the LIVE catch-all "Card #10 Compressor" fires often (Bryan estimates 3-5% of calls) but breaking into sub-modes without discrimination data risks wrong-diagnosis.

## Resolution

- v7 branching tree HTML built and saved.
- 29-fault ranked table produced with confidence levels.
- 11-item build queue formalized.
- Bryan's 3-tier ship proposal on the table (Tier A / Tier B / Tier D — Card #21 moved to D per Alfred).
- Cross-cutting sub-flows identified as 3-4x standalone card engineering.
- Card #10 + #15 families require 3-4 week validation window before shipping (Tier B rationale).

## Lessons for next time

1. **Legend design should separate orthogonal dimensions.** Status vs node-type = 2 boxes, not 1 mixed color palette.
2. **"Build everything" is a founder trap.** Sequenced ship > single-batch ship for velocity + learning.
3. **Tail-frequency cards need field-validation windows.** Anything firing <1% of calls needs months of real data before threshold discipline is trustworthy.
4. **Sub-flows are more expensive than they look.** Cross-cutting modules called by multiple flows have entry/exit surface area = 3-4x standalone work.
5. **LLM cost per diagnosis is a real budget constraint.** Discrimination logic (2 LLM calls where there was 1) needs cost modeling before ship.
6. **Bryan Orr's podcast pitch narrative** doesn't require every card shipped. Tier A alone tells a complete "airflow + latent + oversizing + thermostat" story that no other product covers.

## Follow-up items

- [ ] Formally commit to Tier A vs "build everything" (Shoab)
- [ ] Set Tier A start date (blocked on legal chat's Layer 1-4 landing)
- [ ] Build spec per Tier A item (Card #20 + #22 + #23 + #24 + Airflow Assessment sub-flow + Comfort tab J + superheat/subcool discrim on #8)
- [ ] v7.1 legend fix (Mark's 2-box split) — 10-minute change, do if v7 goes into a demo/pitch
- [ ] Tier B trigger criteria (calendar vs validation gate vs founder call)
- [ ] Sub-flow architecture decision (Airflow + Vacuum) — shared component, complaint type, or branch-insert?

## References

- Related workstream chat: `SnapAI_Product_Discussion_Continuation_Prompt.md`
- Related audit doc: `SnapAI_Brain_and_Tree_Audit_2026-07-05.md`
- Companion legal session: `session_logs/SESSION_LOG_2026-07-05_deep_legal_audit.md`
- 960-episode podcast archive: `Personal Claude/HVAC_School_Transcripts/transcripts/`

## Change log

- **2026-07-06:** Backdated session log created during Phase 3 retrofit (Option B). Content derived from `SnapAI_Product_Discussion_Verbatim_Transcript_2026-07-05.md` + v7 tree build session.
