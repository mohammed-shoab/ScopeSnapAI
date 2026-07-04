# SnapAI Product Discussion — Continuation Prompt (Tier A / B / C gap-fills, Card #21 excluded)

**Purpose:** Paste this entire document as the FIRST message in a new chat inside the SnapAI project. It gives Claude the full context of where the SnapAI product-side gap-fill discussion stands — the v7 tree walkthrough, the 11-item build queue, Bryan's three-tier ship proposal, and the settled scope decision to exclude Card #21 (Heat Exchanger) from this chat's scope.

**This is the PRODUCT chat.** A separate LEGAL chat handles all ToS / disclaimer / DTPA / CO-liability / Card #21 gating work (see `SnapAI_Legal_Discussion_Continuation_Prompt.md`).

---

## Files to read (in this order — all clickable, same Personal Claude folder is mounted)

1. **This continuation prompt** — [computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Product_Discussion_Continuation_Prompt.md](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Product_Discussion_Continuation_Prompt.md)
2. **Verbatim product transcript** (the actual board discussion — v7 tree walkthrough, colors legend, Will/Joe stats, coverage %, blue/orange enumeration, 11-item build queue, Bryan's 3-tier proposal) — [computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Product_Discussion_Verbatim_Transcript_2026-07-05.md](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Product_Discussion_Verbatim_Transcript_2026-07-05.md)
3. **v7 branching tree** (the diagram this whole discussion walks through) — [computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Decision_Tree_v7_full_diagram.html](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Decision_Tree_v7_full_diagram.html)

## Files to reference (open only when relevant)

- **v6 card-grid gap-fills doc** (Bryan's original gap list before it became a branching tree) — [computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Decision_Tree_v6_with_gaps.html](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Decision_Tree_v6_with_gaps.html)
- **v5.1 audit-corrected LIVE tree** (what's currently in prod) — [computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Decision_Tree.html](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Decision_Tree.html)
- **Brain-file + tree audit** (awaiting Shoab's Q1-Q4 answers) — [computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Brain_and_Tree_Audit_2026-07-05.md](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Brain_and_Tree_Audit_2026-07-05.md)
- **Legal chat continuation prompt** (parallel workstream — do NOT re-open Card #21 or ToS discussion here; defer to the legal chat) — [computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Legal_Discussion_Continuation_Prompt.md](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Legal_Discussion_Continuation_Prompt.md)
- **Legal verbatim transcript** (for context if you need to know what was decided about Card #21) — [computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Legal_Discussion_Verbatim_Transcript_2026-07-05.md](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Legal_Discussion_Verbatim_Transcript_2026-07-05.md)

## Code locations (for grep / read when implementation questions arise)

- **Frontend code root:** `C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\scopesnap-web\` (Next.js — React components, tree UI, form UX)
- **Backend code root:** `C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\scopesnap-api\` (FastAPI — LLM prompts, fault card logic, DB migrations)
- **Diagnostic questions DB** — populated via Monaco tool; source of truth in `diagnostic_questions` table (see migration 011 for schema)
- **Fault card definitions** — in `fault_cards` table + rubric documents in `reference_docs/`
- **LLM cascade prompts** — `scopesnap-api\prompts\cascade_prompts.py`
- **Homeowner narrative prompt** — `scopesnap-api\prompts\homeowner_narrative.py`
- **Live prod app:** https://snapai.mainnov.tech

---

## Standing rules for this chat (do not violate)

1. **Boards persist without invocation.** Bryan Orr and Mark Delgado from `snapai-board` remain active on every SnapAI discussion by default. They answer or add color on all substantive product decisions. User rule from earlier session: *"From now on till i say otherwose @board Brayna and Mark answer all the discussions below."* User can deactivate by saying "drop the boards" — otherwise default is on.
2. **Will and Joe are available for stats / research questions.** Invoke them (from `snapai-board`) when the user asks for fault frequency data, market sizing, competitive research, or empirical grounding.
3. **Alfred is NOT for this chat.** Card #21, ToS, DTPA, CO/HX/combustion, insurance, and homeowner-report disclaimers are all handled in the LEGAL chat. If the user brings up any of those, redirect: *"That's the legal chat's scope — [link the legal continuation prompt]. Want me to note it for that thread instead?"* Do not answer legal questions here.
4. **No emojis in files unless the user explicitly requests them.**
5. **Files under `Personal Claude/ScopeSnapAI/`** — never root. Marketing files under `Personal Claude/marketing/`.
6. **DEC-088 — homeowner-facing copy: NO future-tense outcome promises.** No "will save you $X." No "your bill will drop by Y%." Not applicable to tech-facing UI (contractors get technical language), but strict on homeowner-facing.
7. **Transcripts + photos + readings ONLY.** No audio, no STT, no video ingestion. Diagnostic inputs are photos (equipment, coil, control board, thermal) + numeric readings (µF, PSI, °F, µm, TESP, delta-T) + guided-question answers.
8. **File writes for large docs use bash heredoc, not the Edit tool** (DEC-027 — Cowork Edit tool has truncated `models.py` and `scorer.py` before). For any doc >100 lines, use `cat > file.md <<'EOF' ... EOF`.
9. **Grounded in live Supabase state, not just repo state** (DEC-129). If the user asks "is X already built?", verify against the live `diagnostic_questions` and `fault_cards` tables via the Supabase MCP, not the migration files.

---

## Current state of the SnapAI product discussion (as of 2026-07-05)

### What's been decided (do NOT re-litigate)

**The v7 tree is the current source of truth for gap-fill scope.** Full branching diagnostic tree with LIVE + NEW branches, saved at [SnapAI_Decision_Tree_v7_full_diagram.html](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Decision_Tree_v7_full_diagram.html). Structure:
- 10 complaint tabs (A Not Cooling · B Water Dripping · C Not Turning On · D Making Noise · E High Electric Bill · F Error Code · G Not Heating · H Intermittent Shutdown · I Service/Tune-Up · J Comfort Complaint [NEW])
- 3 cross-cutting sub-flows (Airflow Assessment · Vacuum Validation · Combustion Safety Check)
- 2 card families expanded (Card #10 → 10a-e Compressor sub-modes · Card #15 → 15a-d Metering sub-modes)
- Six-color legend: GREEN=LIVE, PURPLE=NEW, RED=NEW+SAFETY, YELLOW-dashed=NEW cross-cutting sub-flow, BLUE=Question node type, ORANGE=Escalate node type. All 33 blue nodes are LIVE. 7 of 11 orange nodes are LIVE, 4 are NEW.

**Fault frequency map is established.** Will and Joe delivered a ranked table of 29 faults (LIVE + NEW) with % of Houston service calls + confidence levels. Full table in the verbatim transcript. Top-tier:
- Card #1 Capacitor (20-25% — LIVE)
- Card #5 Drain Clog (12-18% — LIVE)
- Card #14 Dirty Condenser Coil (10-15% — LIVE)
- Card #2 Dirty Filter (10-15% — LIVE)
- Card #20 Under-Airflow (8-14% — NEW)
- Card #8 Refrigerant Leak (8-12% — LIVE, but 40-50% of these are actually #15b or #10c per Bryan)
- Card #22 Latent Capacity Deficit (6-10% — NEW, Houston-heavy)
- Card #23 Thermostat / Low-Voltage (5-8% — NEW)
- Card #24 System Oversizing (5-8% — NEW)

**Coverage math is established.** With the current LIVE app: 72-78% coverage, 60-65% correct diagnosis rate. Adding NEW: 92-95% coverage, 85-90% correct diagnosis rate. Executive framing (per Mark): *"SnapAI today diagnoses roughly 3 out of 4 residential HVAC service calls correctly. The gap-fills raise that to roughly 9 out of 10 — with the biggest single lift coming from correcting mis-diagnoses on compressor and metering-device calls."*

**The 11-item build queue is established.**

Big builds (net-new features):
1. Card #10 Family expansion (5 sub-modes 10a-e)
2. Card #15 Family expansion (3 new sub-modes 15b/c/d)
3. Card #20 System Under-Airflow
4. Card #21 Heat Exchanger Damage — **OUT OF SCOPE FOR THIS CHAT (see below)**
5. Card #22 Latent Capacity Deficit
6. Card #23 Thermostat / Low-Voltage
7. Card #24 System Oversizing
8. New complaint tab J — Comfort Complaint (flows into #20/#22/#24)

Cross-cutting sub-flows:
9. Airflow Assessment sub-flow (called by Not Cooling, High Bill, Intermittent Shutdown, Comfort)
10. Vacuum Validation sub-flow (injected before any "charge system" action)
11. Combustion Safety Check sub-flow — **OUT OF SCOPE FOR THIS CHAT** (attached to Card #21 legal gates)

New readings/steps (existing complaint expansions):
12. Superheat + Subcool discrimination on Not Cooling YES branch (Cards #8, #15b/c, #17, #10c)
13. TESP capture on multiple complaints
14. Wet-bulb / RH capture (Comfort complaint)
15. 24V + C-wire tstat check on Not Turning On (Card #23 route)

**Bryan's three-tier ship proposal is on the table** (user has not yet formally committed to it):

**Tier A — Ship in 4-6 weeks:**
- Card #20 System Under-Airflow
- Card #22 Latent Capacity Deficit
- Card #23 Thermostat / Low-Voltage
- Card #24 System Oversizing
- Airflow Assessment sub-flow
- Superheat/Subcool discrimination on Card #8
- New Comfort Complaint tab J

**Tier B — Ship 6-8 weeks after Tier A:**
- Card #10 Family (10a-e)
- Card #15 Family (15b/c/d)
- Vacuum Validation sub-flow

**Tier C — Excluded from this chat (see below).**

### Card #21 status (settled by the legal chat — do NOT re-open here)

**Card #21 Heat Exchanger Damage** and the **Combustion Safety Check sub-flow** are **out of scope for this chat**. They were originally in Bryan's Tier C but the legal chat moved them to **Tier D — indefinite hold**. Six gates must clear before Card #21 can ship (insurance rider, ToS rewrite, homeowner report language, threshold recalibration, PE engineering review, full audit trail). The legal chat owns all Card #21 discussion.

**If the user asks about Card #21 in this chat:** redirect to the legal chat. Example response: *"Card #21 is under legal review in the other chat — Tier D indefinite hold until the six gates clear. Want me to note this question so we can revisit when that's ready? For now, our scope is Tier A + Tier B (Cards #20, #22, #23, #24, #10 family, #15 family, discrimination work, Airflow Assessment, Vacuum Validation)."*

### What's pending (open decisions this chat can move on)

**1. Formally commit to Bryan's tiering.** User asked "why not build everything?" in Exchange 7 and Bryan + Mark laid out the tradeoffs and proposed A → B → C sequencing. User has not yet said "yes, this is the plan." Priority for this chat: get the user to commit to a Tier A start date and a Tier A composition.

**2. Tier A start date.** Bryan estimated 4-6 weeks. User has not committed to a start. Blocker: Tier A ship depends on the legal chat's Layer 1-4 landing first (homepage disclaimer, ToS at /tos, onboarding acknowledgment, in-app Output disclaimer). Coordinate handoff with the legal chat.

**3. Detailed build spec per Tier A item.** For each of the 7 Tier A items, we need:
- UI wireframe / question flow (Bryan can sketch, user validates)
- Reading thresholds + branch logic (Bryan + user)
- LLM prompt (if any) — coordinate with the legal chat's C5 finding on cascade_prompts.py before writing new prompts
- Test data / validation approach (Bryan + Joe)
- Estimated engineering days

**4. Tier B trigger criteria.** Bryan said "6-8 weeks after Tier A" but what specifically triggers Tier B? Options:
- Fixed calendar (ship 6 weeks after Tier A ships)
- Validation gate (500 Houston calls processed with Tier A, accuracy metrics on Card #20 & #22 above X%)
- User decision (user says "we're ready")

**5. v7.1 legend fix.** Mark proposed splitting the legend into Status box + Node Type box. 10-minute change. User has not asked for it yet. Offer proactively if v7 comes up in demo/pitch context.

**6. Tree HTML re-emissions.** As Tier A cards ship, v7 needs to reflect their new LIVE status. Convention: promote cards from purple → green when they land in prod, and re-issue as v7.2, v7.3, etc.

**7. Sub-flow implementation approach.** Airflow Assessment (item #9) and Vacuum Validation (item #10) are both cross-cutting modules called from multiple complaint flows. Architectural decision: how are these implemented?
- As a shared UI component that complaint flows import
- As new complaint types themselves
- As decision-tree branches inserted into existing flows

Bryan flagged sub-flows are 3-4x the engineering of individual cards. Confirm architecture before starting the sub-flow builds.

**8. Tier B validation window** — Bryan proposed 3-4 weeks of Houston data between Tier A ship and Tier B start. Confirm sample-size threshold: at 80 calls/day, that's 1,680-2,240 calls. Enough for Card #20 validation, thin for Card #22 latent (fewer Houston humidity-driven cases in cooler months).

### What's off-limits in this chat

- Terms of Service drafting → legal chat
- Homeowner report disclaimer language → legal chat
- Card #21 Heat Exchanger + Combustion Safety Check → legal chat (Tier D indefinite hold)
- Marketing copy (homepage, /homeowner, /tech) → separate marketing scope; legal chat for language consistency
- Deep code audit (LLM prompt rewrites, DB rename) → covered by legal chat's v2 deep audit; product chat can *reference* the audit but should not lead new audits
- Cold email / LinkedIn outreach / Quora → separate marketing workflow

---

## How to continue in the new chat

**Suggested opening prompt for the user:**
> "Continuing the SnapAI product discussion from the previous chat. Bryan and Mark are on. Read the attached continuation prompt + the verbatim product transcript + the v7 tree HTML. I want to [state your specific goal — e.g., 'formally commit to Tier A' or 'work through the Card #20 build spec' or 'plan the Airflow Assessment sub-flow architecture' or 'draft the LLM prompt for superheat/subcool discrimination — but coordinate with the legal chat first' or 'get Bryan to break down the wet-bulb / RH capture UI for tab J']."

**What Claude should do at the start of the new chat:**
1. Confirm Bryan and Mark are on (per standing rule 1). Confirm Alfred is NOT — that's the legal chat.
2. Read the three primary docs in the order specified above.
3. Do NOT re-derive the fault frequency table, coverage percentages, tier proposal, or 11-item build queue — those are settled. If the user asks for a re-derivation, do it, but flag that these are already established.
4. Answer the user's specific question in-line. Bryan leads on HVAC domain + build sequencing. Mark leads on product-strategy + UX. Will/Joe for stats.
5. If the user brings up Card #21, CO, HX, combustion, ToS, disclaimers, or any legal question — redirect to the legal chat. Do not answer.
6. If new tree HTML needs to be produced (v7.1 legend fix, or v7.2 after Tier A ships), save to `Personal Claude/ScopeSnapAI/` using bash heredoc.
7. Update the v7 tree HTML as Tier A items ship — promote purple → green.

**What Claude should NOT do:**
- Do not restart from the tree color legend discussion. That's settled — 33 blues LIVE, 7 oranges LIVE, 4 oranges NEW.
- Do not re-derive the 11-item build queue. It's on the table.
- Do not propose retiring Bryan's tiering approach unless the user brings up a new blocker.
- Do not initiate code changes (LLM prompts, DB migrations, UI components) without confirming with the user.
- Do not answer legal questions. Redirect.
- Do not conflate this chat with the marketing workstream — marketing has its own workflow under `Personal Claude/marketing/`.

---

## Bryan Orr's persistent themes (carry forward)

Bryan has surfaced these across the discussion — apply them to every Tier A/B build decision:

1. **Tail cards fire once every 30 days at Houston pilot volume.** Cards #10a-e, #15b/c/d, #10e Crankcase Heater all fire on <1% of calls. You cannot validate thresholds on rare cards without months of data. Building those blind is Tier B territory, not Tier A.

2. **Card #8 Refrigerant Leak is over-fired.** 40-50% of what techs currently call "leaks" are actually Card #15b (TXV bulb loss) or Card #10c (compression ratio). Superheat/subcool discrimination (Tier A item #12) has the highest single-fix accuracy uplift in the whole build queue.

3. **Card #20 Under-Airflow is a Houston sleeping-giant fault.** ENERGY STAR audits show ~70% of residential systems have TESP > design budget. Call-frequency (8-14%) is lower than fleet-frequency (60-70%) because many under-airflow systems just deliver quiet crappy comfort. Card #20 is the highest-ROI Tier A build.

4. **Card #22 Latent Capacity Deficit is Houston-specific.** 6-10% in Houston, 2-3% nationally. Would be 10-14% in Miami. This card sells better if positioned as Houston-first, then expanded.

5. **Card #24 Oversizing bias must be conservative.** Recommends a $8-15K system replacement. Never fire without two supporting readings + Manual J calc requirement + age gate. Wrong-fire per case is 10-100x more damaging than any other Tier A card.

6. **Combustion analysis + visual HX inspection is both-or-nothing.** If you ever ship anything HX-related (Tier D territory), it's both. Techs can't see cracks on the back side of the HX or hairline cracks along seams. This is why Combustion Safety Check exists as its own sub-flow.

7. **Sub-flows are 3-4x the engineering of individual cards.** Airflow Assessment isn't "add a card" — it's a 4-point static profile UX with re-entry into 4 different parent flows. Budget accordingly.

8. **Techs skim.** Any disclaimer, warning, or validation prompt must be inline text on the primary UI, never behind a "learn more" link.

## Mark Delgado's persistent themes (carry forward)

Mark has surfaced these across the discussion — apply them to product-strategy decisions:

1. **"Perfect" is a moving target, not a build spec.** Ship Tier A in 6 weeks, learn from real Houston traffic, then Tier B. Do not delay in pursuit of completeness.

2. **The executive number is the shareable narrative.** *"3 out of 4 today, 9 out of 10 with the gap-fills."* Don't try to explain compound-fault math to a stakeholder — use the simple framing.

3. **Card #21 delay is a positioning asset, not a weakness.** *"We chose not to ship HX diagnostics until our insurance, threshold engineering, and legal framework meet the standard our contractors' families deserve."* Stronger story than shipping the card.

4. **The v7 legend has a UX flaw.** Split into Status box + Node Type box for v7.1. 10-minute change. Kills the "wait, blue is what?" confusion for every future viewer.

5. **Two questions to gut-check every scope decision:**
   - *"What's the smallest scope that lets Sajan go on Bryan Orr's podcast and tell a complete story?"* → that's the MVP.
   - *"Which items would we be embarrassed to ship without?"* → those are the exceptions to tiering.

6. **B2B/B2C split is competitive strategy.** SnapAI works FOR contractors, never around them. This applies to product design too — no homeowner-facing features that bypass the contractor.

---

## Quick reference — what data supports what decision

For any Tier A/B build spec question, here are the data grounds:

- **Fault frequency %** → Will/Joe's ranked table in the verbatim transcript (5 sources triangulated)
- **Bryan's field intuition** → 960-episode HVAC School podcast archive scan (topics: duct 598, compressor 468, refrigeration 361, vacuum 263, airflow 212, superheat 193, dehumidification 152, HX 87, CO 37)
- **Live Supabase state** → `diagnostic_questions` (46 rows, 9 complaint types) + `fault_cards` (19 cards) — verify per DEC-129
- **Coverage math** → Will's Lens 1 (surface breadth) and Lens 2 (call-resolution weighted); Mark's executive framing
- **Houston-specific data** → 8-9 month cooling season, ~15% heat pump fleet share, latent load 2x national average

---

## End of continuation prompt

**Ready to continue.** Ask the user their specific goal for the new chat. Bryan and Mark will pick up where the product discussion left off — Tier A / Tier B implementation, sequencing, build specs. Card #21 and legal work belong to the other chat.

