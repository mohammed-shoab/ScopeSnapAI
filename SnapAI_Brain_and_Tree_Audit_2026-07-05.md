# SnapAI Brain Files + Diagnostic Tree HTML — Audit Report

**Date:** 2026-07-05
**Status:** ⏸ PAUSED — awaiting Shoab's decisions on Q1-Q4 (bottom of doc)
**Scope:** Read-only audit of all 7 brain files + `SnapAI_Decision_Tree.html` vs live prod Supabase
**Zero writes made this session** — waiting for approval before applying any updates

---

## How to resume from this doc

When you come back, tell the AI session:
> "Read `Personal Claude/ScopeSnapAI/SnapAI_Brain_and_Tree_Audit_2026-07-05.md`. I'm answering the Q1-Q4 questions at the bottom now: [your answers]. Proceed with the approved updates using DEC-070 staging-first flow."

The audit is grounded in:
- Live Supabase queries against `snapai-prod-use1` (`zpsoprffaujswywtsgzy`) — `diagnostic_questions` (46 rows, 9 complaint_types) + `fault_cards` (19 cards)
- Direct file reads of all 7 brain files (7896 lines total)
- Direct file read of `SnapAI_Decision_Tree.html` (1327 lines, v5)

---

## Part 1 — Brain files audit

### 🟥 `STATUS.md` (57 lines) — SEVERELY STALE

Content dated **2026-05-11**. Says:
- "ALL 16 WORK PACKAGES COMPLETE"
- 9/9 complaint types PASS (from 2026-05-11 beta gate)
- Bug fixes list: BUG-006, #9, #10, #11, #12, #13

**Reality now (2026-07-05):** 8 weeks later. Since May 11 we've shipped:
- Brand Decoder v1.2 (DEC-091..DEC-099)
- Next 16 / React 19 / Clerk v7 migration (DEC-112)
- Turbopack on prod (DEC-113)
- PostHog analytics live (DEC-100)
- ~40 more DECs
- DEC-129 (Monaco-seeded gotcha)
- 3 landing pages G/B/B retired
- Diagnostic tree Phase 2 gates live in DB

**Recommendation:** Complete rewrite. STATUS.md should be a short current-state doc (~30 lines): current alembic head, current /api/version, current build hash, current DEC number, open blockers. NOT a completion log — that's what ACTIVE_TASKS.md is for.

### 🟨 `PROJECT_BRAIN.md` (650 lines) — TOP running-commentary block is out of control

Line 5 is a single "Last updated:" paragraph that runs to over 12,000 characters spanning **7 separate "Previously:" nested blocks** from 2026-05-22 through 2026-06-29. That's not a brain file, it's a git log.

**Recommendation:**
- Keep top of file to **one paragraph** describing current live state (~150 words)
- Move the running "Previously:" archive to a new `PROJECT_BRAIN_HISTORY.md`
- Everything else in PROJECT_BRAIN.md (Critical Rules table, Change Workflow section, PSI Threshold Table, decoder facts, DEC-129 rule) is still useful and current

### 🟨 `TECH_STACK.md` (1939 lines) — same problem as PROJECT_BRAIN

Line 3 "Last updated: May 24, 2026" — but content extends through 2026-06-22 in nested "Previously:" blocks. Same running-commentary pattern.

**Recommendation:** Same approach — keep top short, archive the historical narrative.

### 🟨 `ACTIVE_TASKS.md` (1143 lines) — session-log accumulation

Top of file has **session-by-session logs** back to 2026-06-04 (Turbopack promote, Turbopack staging, Dependabot triage, CI fix, etc.). Every session is preserved as its own header block.

**Recommendation:**
- Move sessions where "OPEN / follow-ups" list is fully resolved to a `ACTIVE_TASKS_HISTORY.md`
- Keep only OPEN work + last 2 sessions at top of ACTIVE_TASKS.md

### 🟩 `DECISIONS.md` (2566 lines, 119 DECs, latest DEC-129) — mostly clean

Superseded DECs are **already** marked SUPERSEDED (e.g., DEC-067 SUPERSEDED by DEC-080). Preserve-for-history pattern is intact.

**Minor issue:** DEC-129 (added this session) uses `--` separator instead of `—` em-dash. Line 2540 header is `## DEC-129 -- ...` — should match style of earlier entries (`## DEC-XXX — ...`). Cosmetic only.

**Recommendation:** No pruning needed. Just style-fix the DEC-129 header separator to em-dash.

### 🟩 `WORKFLOW.md` (672 lines) — mostly current

Section 1 "Activation status" still says the workflow is "not yet operational" during the transition. But then confirms Stage 7 signed off 2026-05-24. The stale wording is a distraction — reader has to scroll past "not yet operational" to learn it's been active for 6 weeks.

**Recommendation:** Rewrite Section 1 (~20 lines) to reflect ACTIVE status as of 2026-05-24. Drop the "Until that moment" bullets — that transition is done.

### 🟩 `MARKET_GUIDE.md` (259 lines) — mostly current

Content is fine. But needs a top-of-file note reflecting **DEC-123 — PK is a dormant test market, US is production**. That decision was locked 2026-06-22 but not surfaced in MARKET_GUIDE.md. Right now the file reads as if both markets are live-equivalent.

**Recommendation:** Add a 3-line banner at top: "As of DEC-123 (2026-06-22): PK is a dormant test market. All active development targets Houston (US). PK code paths and data are preserved but not being iterated on."

---

## Part 2 — `SnapAI_Decision_Tree.html` (v5, 1327 lines) vs live Supabase

### 🔴 5 bug banners STALE — all bugs are FIXED

| Tree line | Banner shown | Reality per live DB |
|---|---|---|
| 293 + 384 | 🔴 BUG #10 CRITICAL Service/Tune-Up Step 8 → 503 | ✅ FIXED. Service flow has svc-1 through svc-8. svc-8 branch_logic has `service_complete: true, generate_estimate: true`. |
| 294 (implied) | 🔴 BUG #11 CRITICAL Not Cooling → NO always escalates | ✅ FIXED per migration 014. NO routes to q2-cap → q3-contactor with proper voltage handling (no_power / phase_loss escalate with reason; power_passes_normal → Card 3). |
| 295 + 710 | 🔴 BUG #12 CRITICAL Water Dripping → Outdoor → 404/422 | ✅ FIXED per migration 014. water_dripping outdoor_refrigerant → q2-wd-suction with proper suction PSI routing. |
| 296 + 999 | 🟠 BUG #13 HIGH Not Heating → Ignites shuts off | ✅ FIXED per migrations 014+015. q4-flame-sensor has proper microamps handling with low / marginal / ok branches. |
| 297 + 945 | 🟠 BUG #9 HIGH Error Code → NO reset → escalates | ✅ FIXED per migration 014. q4-reset NO → resolve_card:7 (control board lockout), same as YES. |

### 🟠 Phase 2 build-status markers STALE

| Tree line | Marker | Reality |
|---|---|---|
| 600 | *"Phase 2 build needed (Task #9 + #10)"* on Not Cooling YES gate | ✅ BUILT. Live routing: q2-nc-suction (low→Card 8 leak, ok→Card 13 ductwork, high→q2-nc-discharge → ok→Card 14 dirty coil, low→escalate compressor valve, high→Card 17 overcharge). 4-way discrimination is live. |
| 1021 | *"Add 'Intermittent Shutdown' as the 8th complaint to top screen"* warning box | ✅ ADDED. intermittent_shutdown has 5 steps q1-q5 live. Card #16 fully wired. FLIR camera escalate at q5-voltage-drop "elevated" branch. |
| 906 | *"Task #12 (brand DB) needed for full auto-route"* on Error Code | 🟡 PARTIAL. error_code q1 has full `extract_then_lookup` action with 7-way discrimination live (capacitor / contactor / lockout / refrigerant_low with Phase 2 sub-gate for Card 8 vs 15 / communication / nuisance / pressure_sensor). Brand DB auto-route is wired. |
| 1222 | *"XGBoost exists and works BUT it needs the Phase 2 mandatory readings gate (Task #9)"* | 🟡 Phase 2 gate is live but XGBoost is NOT in the diagnostic path per Shoab's earlier confirmation. Live path uses threshold-routing on suction+discharge. |

### 🟡 Card #13 Ductwork Leak — semantic mismatch

Tree spec (line 621) labels Card #13 as *"Gemini reasoning. No single reading or photo diagnoses this."* and tags it as `node-pj` = **Tech Judgment**.

Live DB shows Card #13 is reached via threshold routing: `not_cooling / q2-nc-suction / "ok" branch → resolve_card: 13`. So Card #13 is reached when suction is normal (115-141 PSI at 95°F). No Gemini reasoning; no tech-judgment tag; deterministic threshold routing.

**Recommendation:** Update the Card #13 node to reflect it's a normal-suction-routing outcome, not a Gemini/Tech-Judgment branch. Keep the fact that it uses ductwork-leak as the working hypothesis, but drop the "Gemini reasoning" and "Tech Judgment" markers.

### 🟡 Not Cooling YES branch — the 4-way "phase_2_gate" description is outdated

Tree spec (lines 594-628) describes a **single Phase 2 gate** collecting 4 readings simultaneously. Live implementation is a **2-step cascade** (suction first, then discharge if suction is high). Both produce the same 4-way outcome but the visual on the tree shows one gate; the live UX shows sequential prompts.

**Recommendation:** Redraw the Not Cooling YES branch as: suction reading → 3 outcomes → high routes to a second discharge reading → 3 outcomes. That matches what a tech actually sees in the app.

### 🟢 Everything else on the tree matches live state

The tree spec's overall design is correct. Complaint tabs A-I all have live data. Card definitions match. Escalate reasons match (particularly the "consider FLIR camera" line I verified earlier). The tree spec is more right than wrong — it just has old bug banners and old "build needed" markers.

---

## Summary of what needs writing (if approved)

| File | Change size | Scope |
|---|---|---|
| `STATUS.md` | ~40 lines rewrite | Total rewrite as short current-state doc |
| `PROJECT_BRAIN.md` | Top block collapse + move history to new file | Keep body; prune the running "Previously:" narrative |
| `TECH_STACK.md` | Same pattern as PROJECT_BRAIN.md | Keep body; move top narrative to history file |
| `ACTIVE_TASKS.md` | Move closed sessions to new history file | Keep only OPEN + last 2 sessions |
| `DECISIONS.md` | 1 char change (`--` → `—`) | Fix DEC-129 header style |
| `WORKFLOW.md` | ~20 lines Section 1 rewrite | Drop "not yet operational" language |
| `MARKET_GUIDE.md` | ~3 lines added at top | Add DEC-123 dormant-PK banner |
| `SnapAI_Decision_Tree.html` | 5 bug-banner removes + 3 phase-2 marker updates + 1 Card #13 relabel + 1 Not-Cooling-YES redraw | Version bump to v6 |

---

## ❓ Open Questions for Shoab

### Q1 — Update scope
- **A.** All 8 files updated in one commit
- **B.** Brain files first (7 md files), verify, then tree HTML
- **C.** Only some of these — specify which

### Q2 — Tree HTML rewrite of Not Cooling YES branch
- **Option 1.** Keep the 4-way outcome grid intact (design spec view)
- **Option 2.** Show the 2-step cascade (matches live UX)
- **Option 3.** Both — show the cascade with the outcome grid rendered at the leaves

### Q3 — History file destination
When pruning "Previously:" narrative from PROJECT_BRAIN.md, TECH_STACK.md, ACTIVE_TASKS.md:
- **Option A.** Be new files in the repo root (PROJECT_BRAIN_HISTORY.md etc., staging → main path)
- **Option B.** Go into an `_archive/` folder
- **Option C.** Not be created — just delete the narrative outright

### Q4 — DEC-070 compliance for the doc updates
- **Option A.** Push all via staging → main → prod (same flow as landing pages)
- **Option B.** Bypass since they're docs-only, no runtime impact
- (Recommendation: A. DEC-070 rule 1 says "never edit main directly." Docs live in the repo, so same rule.)

---

## Change log

- **2026-07-05:** Initial audit report saved. No writes to any of the 8 files. Awaiting Shoab's answers on Q1-Q4.
