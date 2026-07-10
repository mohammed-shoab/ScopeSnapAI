# SnapAI Brain Files — Comprehensive Cleanup + Management Plan

**Date:** 2026-07-05
**Owner:** Shoab
**Prepared by:** Karpathy (nav) + Rob (board) + Bryan Orr (board) + Mark Delgado (board)
**Purpose:** One-time cleanup of the current bloat AND standing discipline going forward
**Status:** DRAFT — awaiting Shoab's approval before execution

**Sources this plan integrates:**
- Audit findings: [SnapAI_Brain_and_Tree_Audit_2026-07-05.md](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Brain_and_Tree_Audit_2026-07-05.md)
- Router mechanism: [SnapAI_Project_Instructions.md](computer://C:\Users\Shoab\My Drive\Personal Claude\SnapAI_Project_Instructions.md)
- Cowork setup reference: [Cowork_Projects_Setup_Reference.md](computer://C:\Users\Shoab\My Drive\Personal Claude\Cowork_Projects_Setup_Reference.md)
- Board discussion on management approach (this chat, 2026-07-05)

---

## Executive summary

**The problem in one sentence:** Your brain files have become a mix of load-bearing rules + running commentary + session logs, and the AI has to wade through it all every session — burning tokens, slowing responses, and letting stale claims compete with current truth.

**The fix in two sentences:** Right now — apply the audit findings (rewrite 3 files, prune 3 files, add 1 banner, fix 1 char) and reissue the diagnostic tree HTML as v6. Going forward — enforce three file archetypes with mechanical rules (line caps, session-end hygiene, weekly auto-audit) so bloat can't recur.

**Estimated effort:**
- One-time cleanup: 3-4 hours (brain files) + 2-3 hours (tree HTML) = **~1 working day**
- Ongoing discipline: ~15 min/week session-end hygiene + weekly auto-audit report review

---

## Part 1 — Answers to the four pending questions

The audit doc had four open questions (Q1-Q4) waiting on you. My recommendations for each — YOU MUST STILL APPROVE:

### Q1 — Update scope

**Recommendation: Option B — Brain files first (7 md files), verify, then tree HTML.**

Reasoning: brain files are pure text — safer to iterate. Tree HTML is a bigger structural change (bug banners, phase 2 markers, Card #13 relabel, Not Cooling YES redraw). Doing brain files first lets you feel the impact of the discipline before compounding it with tree changes. Also each brain-file commit is small and reversible; the tree HTML is one big commit that's harder to unwind.

### Q2 — Tree HTML rewrite of Not Cooling YES branch

**Recommendation: Option 3 — Both — show the 2-step cascade with the 4-outcome grid rendered at the leaves.**

Reasoning: matches live UX (a tech sees suction first, then discharge if suction is high — that's the actual sequential experience) AND preserves the design-spec view (the four outcomes are still visible on the tree at a glance). Best of both. Bryan's field-authenticity principle: the tree should mirror what a tech actually sees. Mark's design-spec principle: outcomes should still be visible for the stakeholder view.

### Q3 — History file destination

**Recommendation: Option A — new files at repo root.**

Reasoning: `_archive/` folders tend to become invisible. Repo root keeps history files queryable (`grep` across `*_HISTORY.md` works cleanly). Self-documenting filenames (`PROJECT_BRAIN_HISTORY.md`, `TECH_STACK_HISTORY.md`, `ACTIVE_TASKS_HISTORY.md`) tell any future AI or human what's inside without having to open them. The history files themselves are LARGE — Karpathy's rule "AI reads what it needs" applies: the AI won't open the history file unless a task specifically requires it, so root vs archive folder doesn't cost anything.

### Q4 — DEC-070 compliance

**Recommendation: Option A — push via staging → main → prod.**

Reasoning: DEC-070 rule 1 says "never edit main directly." Brain files live in the repo. Same rule applies. This adds ~20 minutes to each edit cycle but preserves the invariant. Shortcuts on rules erode trust in the rules. Alfred's Principle 4 (documented QA + accuracy monitoring) argues for the same discipline on brain files as on code — every change flows through staging.

---

## Part 2 — File classification (three archetypes)

Karpathy's framework, applied to your 7 brain files:

### Archetype 1 — Mutable current-state snapshots (atomic replacement, not appending)

**Files:** `STATUS.md`, `ACTIVE_TASKS.md` (OPEN section)

**Rule:** Every session that touches these files *overwrites* the current section. Never append "Previously:" narrative. If you need history, that's what git log is for.

**Line caps:** `STATUS.md` ≤ 60 lines. `ACTIVE_TASKS.md` OPEN section ≤ 300 lines.

### Archetype 2 — Reference documents (occasional updates, structure > prose)

**Files:** `PROJECT_BRAIN.md`, `TECH_STACK.md`, `WORKFLOW.md`, `MARKET_GUIDE.md`

**Rule:** Tables > prose. First 20 lines = load-bearing rules table (CRITICAL RULES section). No running commentary at top. Updates are surgical, not narrative.

**Line caps:** `PROJECT_BRAIN.md` ≤ 500 lines. `TECH_STACK.md` ≤ 2000 lines. `WORKFLOW.md` ≤ 2000 lines. `MARKET_GUIDE.md` ≤ 300 lines.

### Archetype 3 — Immutable append-only logs (grow indefinitely, no cap)

**Files:** `DECISIONS.md`

**Rule:** Never delete, never rewrite. Superseded entries flagged in-place. Grows indefinitely because it's queried, not scanned.

**Line cap:** None. Currently 2566 lines, will grow. Fine.

### Archetype 4 — History files (AI-only archive, no cap)

**Files (NEW to create):** `PROJECT_BRAIN_HISTORY.md`, `TECH_STACK_HISTORY.md`, `ACTIVE_TASKS_HISTORY.md`

**Rule:** Where the "Previously:" narrative gets moved during Phase 1 cleanup. Human-rarely-opened, AI-opens-only-when-needed.

**Line cap:** None.

### Archetype 5 — Human-facing onboarding (NEW to create)

**File (NEW):** `ONBOARDING.md`

**Rule:** For when you hire a dev, bring on a new tester, or explain SnapAI to Sajan's team. Curated narrative. Marketing-adjacent voice. Separate audience from AI brain files.

**Line cap:** ≤ 500 lines.

---

## Part 3 — Phase 1: One-time cleanup (this week)

### Order of operations (5 commits total)

**Commit 1 — DECISIONS.md style fix (5 minutes, no risk)**

Fix DEC-129 header `-- ` → `— ` for style consistency. One-character change, low-risk warmup commit. Establishes the staging → main → prod path is working for docs.

**Commit 2 — WORKFLOW.md Section 1 rewrite (20 minutes)**

Drop "not yet operational" language. Rewrite Section 1 (~20 lines) to reflect ACTIVE status as of 2026-05-24. This is a small isolated change that lets you verify the pattern works before touching bigger files.

**Commit 3 — MARKET_GUIDE.md banner add (10 minutes)**

Add 3-line banner at top: *"As of DEC-123 (2026-06-22): PK is a dormant test market. All active development targets Houston (US). PK code paths and data are preserved but not being iterated on."*

**Commit 4 — Three big prunes (2-3 hours)**

Do all three files in one atomic commit to avoid partial-state confusion:

**4a. STATUS.md — complete rewrite (~40 lines).** New format:

```markdown
# SnapAI — Current Live State

**As of:** {{date}}
**Live prod:** https://snapai.mainnov.tech (revision X.Y.Z)
**Alembic head:** {{migration_id}}
**Latest DEC:** DEC-{{N}}

## Current focus (2-3 lines)

{{what Shoab is actively working on}}

## Open blockers (0-5 items)

- {{blocker 1}}
- {{blocker 2}}

## Recent milestones (last 7 days only)

- {{milestone 1}}
- {{milestone 2}}

## Auto-updated

{{last verified by ${session_id} on ${date}}}
```

**4b. PROJECT_BRAIN.md — collapse top narrative + preserve body.**
- Move the 12,000-char "Previously:" block at line 5 → new `PROJECT_BRAIN_HISTORY.md`
- Keep the top current-state paragraph to ~150 words describing what SnapAI is + what's live today
- Keep everything below (Critical Rules table, Change Workflow, PSI Threshold Table, decoder facts, DEC-129 rule) as-is
- Add a "CRITICAL RULES" table as the first 20 lines (see Part 4 for format)

**4c. TECH_STACK.md — same pattern as PROJECT_BRAIN.md.**
- Move top narrative → new `TECH_STACK_HISTORY.md`
- Keep body sections (infrastructure inventory, deploy config, staging/prod split, integrations)
- Add current-state paragraph at top (~150 words)

**Commit 5 — ACTIVE_TASKS.md restructure (1 hour)**

- Move all sessions with fully-resolved "OPEN / follow-ups" → new `ACTIVE_TASKS_HISTORY.md`
- Keep only OPEN work + last 2 sessions at top
- Add a "In Flight" table at top showing what's currently active (e.g., "Legal cleanup — Alfred workstream," "Product Tier A build — Bryan/Mark workstream," "Brain files cleanup — this plan")

### Tree HTML (Commit 6, after brain files verified)

**Version bump:** `SnapAI_Decision_Tree.html` v5 → v6 (or v6.x if you want to preserve the v6 gap-fills doc name — could do v5.2 for the audit fixes and let v7 remain the branching diagram we built today).

**Actually:** given we already have v7 (`SnapAI_Decision_Tree_v7_full_diagram.html`) and v5.1 (audit-corrected LIVE tree), the cleanest naming is:
- v5.1 → v5.2 (this cleanup pass — audit fixes on the LIVE tree)
- v6 (gap-fills doc) unchanged
- v7 (branching tree with LIVE + NEW) unchanged

**Changes to apply to v5.2:**
- Remove 5 bug banners (all fixed per migrations 014+015) — replace with green ✅ "FIXED — {migration_id}" tag if you want to preserve the historical record, otherwise delete
- Remove 3 Phase 2 build markers (all built) — replace with green ✅ "LIVE"
- Card #13 relabel: drop "Gemini reasoning / Tech Judgment" tag, replace with "Threshold routing outcome (normal suction, 115-141 PSI @ 95°F)"
- Not Cooling YES branch redraw: 2-step cascade + 4-outcome grid at leaves (Q2 Option 3)
- Version bump to v5.2 in header

---

## Part 4 — CRITICAL RULES table (top of PROJECT_BRAIN.md)

Mark's proposal: first 20 lines of `PROJECT_BRAIN.md` = load-bearing rules table. Enforced constraint style, not narrative. Any AI reading this file sees the rules FIRST, before any prose.

Format:

```markdown
# SnapAI — Project Brain

**Current live state:** {{one-paragraph, ~150 words}}

## CRITICAL RULES (read before every task)

| Rule | Where enforced | Reference |
|---|---|---|
| Never edit main directly | git workflow | DEC-070 |
| Homeowner copy: no future-tense outcome promises | homeowner-facing surfaces | DEC-088 |
| PK is dormant, US is production | market decisions | DEC-123 |
| Monaco seeds `diagnostic_questions` — verify against live DB, not migrations | code state claims | DEC-129 |
| Boards persist without invocation in SnapAI chats | AI behavior | User rule 2026-06-29 |
| Marketing docs go under `Personal Claude/marketing/` | file placement | User rule 2026-07-01 |
| For any SnapAI marketing task, read `marketing/MBrain/README.md` FIRST | task routing | User rule 2026-07-01 |
| Never name Houston or any city in public-facing copy | homeowner-facing copy | User rule 2026-07-06 |
| Card #21 Heat Exchanger + Combustion Safety Check = Tier D indefinite hold | product scope | Legal chat 2026-07-05 |
| All SnapAI outputs are decision-support, never certified diagnosis | product identity | Legal chat 2026-07-05 |
| No CO / HX / combustion safety in scope until Alfred's six gates clear | product scope | Legal chat 2026-07-05 |
| Transcripts + photos + readings only — no audio, no STT | ingestion scope | User rule |

## Body sections
{{everything else — Change Workflow, PSI Threshold Table, decoder facts, etc.}}
```

Karpathy's rationale: an AI loading this file sees the load-bearing constraints in the first 20 lines. Even if the body is 480 lines, the top-of-file rules dominate the AI's model of what's non-negotiable.

---

## Part 5 — Router update (SnapAI_Project_Instructions.md)

Now that today's session created six new files, the router needs updating. Add to `SnapAI_Project_Instructions.md`:

```markdown
## Task routing table (updated 2026-07-05)

| Task type | File to load first |
|---|---|
| Marketing task | marketing/MBrain/README.md |
| App dev / bug fix / QA | invoke snapai-dev skill |
| Board discussion (general strategy) | invoke snapai-board skill |
| Nav discussion (frameworks / operators) | invoke snapai-nav skill |
| Legal / ToS / DTPA / Card #21 / CO / disclaimer | ScopeSnapAI/SnapAI_Legal_Discussion_Continuation_Prompt.md |
| Product / gap-fills / Tier A/B / build queue | ScopeSnapAI/SnapAI_Product_Discussion_Continuation_Prompt.md |
| Brain files cleanup / audit updates | ScopeSnapAI/SnapAI_Brain_Files_Management_Plan_2026-07-05.md (this file) |
| Cold email / LinkedIn DM | marketing/MBrain/README.md → voice_research/_TEMPLATE_FUEL_v1.md + personas/_banned_phrases.md |
| Video script / production | marketing/MBrain/README.md → marketing/Azhan/README.md |
| Dossier work / prospect research | marketing/MBrain/README.md → marketing/Murtaza/ |
| Diagnostic tree / decision flow | ScopeSnapAI/SnapAI_Decision_Tree_v7_full_diagram.html (branching v7) + ScopeSnapAI/SnapAI_Decision_Tree.html (LIVE v5.2) |
```

Also add a "Session start signal" instruction so you know the router loaded successfully:

```markdown
## Session start signal

On successful load, greet with:
"SnapAI project loaded. Boards on. Routing table {{count}} entries. Ready."
```

---

## Part 6 — Phase 2: Ongoing discipline (going forward)

### Rob's 6 mechanical rules

**1. Session-end hygiene ritual.** Every session that touches `STATUS.md` or the top section of `PROJECT_BRAIN.md` / `TECH_STACK.md` ends by *overwriting* the current section — not appending. Enforced by a pre-commit hook that greps for `Previously:` blocks in those files and rejects the commit.

**2. Line-count caps.** Enforced by a pre-commit hook:

| File | Cap | Action if exceeded |
|---|---|---|
| STATUS.md | 60 lines | Reject commit, prompt to prune |
| PROJECT_BRAIN.md | 500 lines | Warn + prompt to move history |
| TECH_STACK.md | 2000 lines | Warn + prompt to move history |
| ACTIVE_TASKS.md (OPEN section) | 300 lines | Warn + prompt to archive closed sessions |
| WORKFLOW.md | 2000 lines | Warn |
| MARKET_GUIDE.md | 300 lines | Warn |
| DECISIONS.md | none | — |
| *_HISTORY.md files | none | — |
| ONBOARDING.md | 500 lines | Warn |

**3. Weekly auto-audit.** Scheduled task (Friday 09:00 CT via `mcp__scheduled-tasks__create_scheduled_task`):
- Loads all brain files
- Flags: line-count overages, staleness (`last_verified` > 60 days), duplicate rule statements across files, contradictions with live Supabase / live app state
- Reports as a Cowork chat message to you
- Never auto-applies changes

**4. Provenance metadata on every entry.** Each fact/rule in a brain file gets a small YAML header at the top of its section:

```yaml
---
added: 2026-06-22
last_verified: 2026-07-05
source: DEC-123
---
```

Enables the weekly audit to compute staleness.

**5. Single source of truth per fact.** If a rule is stated in `DEC-123`, `PROJECT_BRAIN.md`, and `MARKET_GUIDE.md` — that's three files to update when it changes. Pick one canonical location, everywhere else references by pointer: *"See DEC-123 for full detail."* Enforced by a grep hook that catches duplicate rule statements.

**6. "Regenerate from source" test.** Every quarter (or during weekly audit if flagged), ask: could I delete this section and reconstruct it from git log + code + DB in <5 minutes? If yes, delete it. If no, keep.

### Bryan's dual-audience principle

Brain files serve HUMANS (Shoab, Sajan, future devs) + AI (Cowork sessions). History files are AI-only. If STATUS.md is 30 lines a human can read in 90 seconds, it's serving both. If it's 500 lines of running commentary, it's serving neither.

### Mark's ONBOARDING.md pattern

Separate curated document for when you hire a dev or bring on a new tester. Marketing-adjacent voice. Brain files stay AI-optimized; ONBOARDING.md stays human-optimized.

---

## Part 7 — Automation setup steps (Rob's tactical layer)

### Step A — Create pre-commit hooks (30 min)

File: `ScopeSnapAI/.git/hooks/pre-commit` (or `.pre-commit-config.yaml` if you're using pre-commit framework)

Checks to run:
1. Reject if any file has `Previously:` block in the top 30 lines of `STATUS.md`, `PROJECT_BRAIN.md`, `TECH_STACK.md`
2. Reject if any file exceeds line-count cap
3. Reject if any file has `diagnos*` string in homeowner-touching files (`app/homeowner/`, `app/d/`, `app/r/`, `templates/`, `services/email.py` homeowner sections) — this is Alfred's Principle 3 enforcement
4. Warn if any brain-file entry lacks `last_verified` metadata

### Step B — Set up weekly auto-audit scheduled task (10 min)

Use `mcp__scheduled-tasks__create_scheduled_task`:
- Schedule: `0 9 * * 5` (every Friday 09:00 CT)
- Prompt: *"Run the SnapAI brain files audit. Load all 7 brain files + DECISIONS.md + the v5.2 tree HTML. Compare against live Supabase state. Flag: line-count overages, staleness, duplicates, contradictions. Report to Shoab as a Cowork chat message. Do not apply changes."*

### Step C — Session-end helper (optional, 20 min)

Create a `session-end-hygiene.md` skill that Shoab can invoke at end of any brain-file-touching session:
- Reviews the diff on brain files
- Flags if any appended narrative was added instead of overwriting
- Prompts to compact if bloat detected

---

## Part 8 — Success metrics

You know this is working when:

1. **Total brain-file token load < 10K tokens** on a fresh Cowork session start (measurable via context usage stats)
2. **Every session start is <3 seconds** from user's first message to Claude's first response (no giant file reads bogging things down)
3. **Zero "Previously:" blocks** in the top 30 lines of any mutable-state file
4. **Weekly audit reports find <5 issues** each week after month 2 (system stabilizes)
5. **No brain-file update lags actual state by more than 1 week** (STATUS.md always reflects current reality)
6. **New Cowork chat can accurately answer "what's currently live?" without asking follow-ups** (STATUS.md carries the load)

---

## Part 9 — Rollout timeline

### Week 1 (2026-07-06 → 2026-07-12)
- Day 1: Approve this plan (you) + start Commits 1-3 (small warmup commits)
- Day 2-3: Commit 4 (three big prunes)
- Day 4: Commit 5 (ACTIVE_TASKS restructure)
- Day 5: Verify — new Cowork chat, confirm STATUS.md + PROJECT_BRAIN.md load cleanly, routing works
- Day 6-7: Buffer for corrections

### Week 2 (2026-07-13 → 2026-07-19)
- Day 1-2: Commit 6 (v5.2 tree HTML)
- Day 3: Update `SnapAI_Project_Instructions.md` with new routing table
- Day 4: Create `ONBOARDING.md` (human-facing narrative)
- Day 5: Set up pre-commit hooks (Rob's Step A)
- Day 6-7: Set up weekly auto-audit (Rob's Step B) + optional session-end helper (Step C)

### Week 3+ (2026-07-20 onward)
- Weekly Friday audit reports arrive; you review, apply what's needed
- Adjust caps / thresholds based on 2-3 weeks of real data

---

## Part 10 — What NOT to do

Karpathy + Rob's list of anti-patterns to avoid:

1. **Do NOT add "Previously:" blocks to STATUS.md or PROJECT_BRAIN.md top.** Overwrite in place, move history to history files. The audit found this was the #1 bloat driver.

2. **Do NOT duplicate rules across files** without a canonical source. Pick one location, reference by pointer.

3. **Do NOT append session narratives to brain files** ("2026-07-05 session: did X, Y, Z"). Session narratives belong in verbatim transcript files (like the ones we made for legal + product), not in brain files.

4. **Do NOT skip the weekly audit** after week 2. The system requires the audit signal to catch drift.

5. **Do NOT edit brain files directly on `main` branch.** DEC-070 applies. Every change flows through staging.

6. **Do NOT create a `Personal Claude/CLAUDE.md`.** That leaks context across Bolder Park, Portugal, SnapAI. Cowork Project Instructions is the right mechanism (already in place for SnapAI via `SnapAI_Project_Instructions.md`).

7. **Do NOT let ACTIVE_TASKS.md grow to session-log-heaven.** OPEN section only. Closed → history file.

---

## Change log

- **2026-07-05:** Initial plan drafted by Karpathy + Rob + Bryan + Mark. Awaiting Shoab's approval of Q1-Q4 recommendations before execution.

---

## Approval checklist (Shoab to sign off before Phase 1 starts)

- [ ] Q1 approved: Option B (brain files first, then tree HTML)
- [ ] Q2 approved: Option 3 (2-step cascade with 4-outcome grid at leaves)
- [ ] Q3 approved: Option A (history files at repo root)
- [ ] Q4 approved: Option A (staging → main → prod path per DEC-070)
- [ ] Phase 1 5-commit sequence approved
- [ ] Phase 2 6 mechanical rules approved
- [ ] Weekly audit cadence approved (Friday 09:00 CT)
- [ ] Line-count caps approved
- [ ] File archetypes approved

Once Shoab signs off, this plan becomes the executable blueprint. Each week's work will be tracked against it and against the audit doc.

