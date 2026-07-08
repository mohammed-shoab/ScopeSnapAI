# SnapAI — Bryan Orr HVAC School Compendium Extraction Plan v1

**Version:** v1.0
**Date:** 2026-07-06
**Author:** Bryan Orr (snapai-board) + Shoab
**Status:** Handoff plan — self-contained for a dedicated fresh Cowork chat to execute
**Purpose:** Extract structured knowledge from all 960 HVAC School podcast transcripts into a canonical Bryan compendium. Referenced by `snapai-board/references/bryan-orr/` so all future Bryan-persona invocations have 960 episodes of context baked in.

---

## 1. How to use this document

**Paste this entire file as the first message in a fresh Cowork chat inside the SnapAI project.** That chat will execute the extraction autonomously per the instructions below.

**Standing rules apply** (per `SnapAI_Project_Instructions.md`):
- `@board` and `@nav` remain active
- No emojis in files
- DEC-070 staging → main → prod for any code
- DEC-088 no future-tense homeowner promises
- Geo-neutral (no city names in user-facing strings, but geo/regional data is OK in this internal-reference compendium)
- Attribution rule: this compendium synthesizes Bryan Orr's public podcast IP for internal reference only. Any downstream use in SnapAI-facing copy must attribute Bryan Orr / HVAC School properly and never imply endorsement he didn't give.

---

## 2. Source data

**Location:** `C:\Users\Shoab\My Drive\Personal Claude\HVAC_School_Transcripts\transcripts\` (~960 `.txt` files)

**Format:** Plain text, one file per episode. Naming typically `{episode_number}_{title}.txt` or similar.

**Sandbox path:** `/sessions/<session-name>/mnt/Personal Claude/HVAC_School_Transcripts/transcripts/`

**Total scope:** ~960 files, avg ~4,000 words each → ~4M words total. Well beyond any single-chat context window. Extraction must be done via parallel subagents.

**Prior scan available** (per `session_logs/SESSION_LOG_2026-07-05_product_gap_fills_v7_tree.md`):
- Topic frequency scan complete — duct 598, compressor 468, refrigeration 361, vacuum 263, airflow 212, superheat 193, dehumidification 152, HX 87, CO 37 (approximate mention counts, not exact episode counts)
- Frequency scan is a starting reference — full deep extraction is what THIS plan produces

---

## 3. Output structure — 1 master + 12 topic compendia

### 3A. Master file (single file)

**Location:** `Personal Claude/snapai-board/references/bryan-orr/Bryan_Orr_HVAC_School_Master_Compendium_v1.md`

**Structure:**
```
# Bryan Orr — HVAC School Master Compendium v1

**Total episodes:** 960 (or actual count after scan)
**Extraction date:** {date}
**Extraction method:** Parallel-subagent structured extraction per SnapAI_Bryan_Compendium_Extraction_Plan_v1.md
**Change log:** at bottom

## Episode index (all episodes, sortable)
| Ep # | Date | Guest | Primary topic | 3-word summary | Compendium file |
|---|---|---|---|---|---|
| 001 | ... | (solo) | Refrigeration cycle | Basic circuit walkthrough | Refrigeration_Cycle.md |
| 002 | ... | Guest name | Compressor start | Hard-start capacitor use | Compressor.md |
| ... | ... | ... | ... | ... | ... |

## Topic frequency table (verified count)
| Primary topic | Episode count | Compendium file |
|---|---|---|
| Compressor | 468 | Bryan_Compendium_Compressor.md |
| Refrigeration cycle | 361 | Bryan_Compendium_Refrigeration_Cycle.md |
| ...

## Cross-reference matrix
Which topics co-occur most often. Rows = topic A, columns = topic B, cell = count of episodes that discuss both.

## Recurring Bryan-isms and characteristic language
Extracted quotable phrases + typical reasoning patterns for persona fidelity.

## Guest-frequency and specialty index
Which guest speakers appear most often and their specialties.
```

### 3B. Topic compendia (12 files, ~50-100 pages each)

**Location:** `Personal Claude/snapai-board/references/bryan-orr/topics/`

1. `Bryan_Compendium_Compressor.md` — start components, replacement decisions, testing, failure modes (grounded / mechanical / compression ratio / start component / crankcase)
2. `Bryan_Compendium_Refrigeration_Cycle.md` — superheat, subcool, charging, pressures, refrigerant types
3. `Bryan_Compendium_Airflow.md` — TESP, static profiles, blower sizing, duct design, delta-T
4. `Bryan_Compendium_Vacuum_and_Recovery.md` — micron gauge, decay tests, moisture, evacuation, pump maintenance
5. `Bryan_Compendium_Electrical_and_Controls.md` — capacitors, contactors, boards, wiring diagnosis, control voltage
6. `Bryan_Compendium_Combustion_and_HX.md` — furnace safety, CO, flame sensors, ignitors, gas trains
7. `Bryan_Compendium_Comfort_and_Latent.md` — humidity, wet-bulb, latent capacity, right-sizing, dehumidification
8. `Bryan_Compendium_Metering_Devices.md` — TXV, EEV, orifice, piston mismatch, hunting
9. `Bryan_Compendium_Diagnostics_Methodology.md` — how Bryan teaches systematic fault isolation, evidence-driven troubleshooting
10. `Bryan_Compendium_Tools_and_Instruments.md` — gauges, thermal cameras, combustion analyzers, meters
11. `Bryan_Compendium_Business_and_Trade.md` — pricing, sales, tech development, apprenticeship, callback rates
12. `Bryan_Compendium_Guest_Wisdom.md` — everything worth keeping from manufacturer + specialist interviews

**Each topic compendium structure:**
```
# Bryan Orr HVAC School — Compendium: {Topic}

**Version:** v1.0
**Date:** {date}
**Source episodes:** {count, list of ep numbers}
**Cross-references:** {other topic compendia this ties to}

## Overview — Bryan's core teaching on this topic (500 words)

## Key technical points (bulleted, with citations to episode number)

### Point 1 — {name}
- What Bryan teaches: ...
- Sources: Ep 042, Ep 187, Ep 512
- Numbers he cites: ...
- Common misconception he corrects: ...

### Point 2 — {name}
... (etc.)

## Canonical field stories

### Story 1 — {short title, e.g., "The 90-degree drop on a 3-ton with no load"}
- Setting: ...
- Diagnosis chain: ...
- Root cause: ...
- Lesson: ...
- Sources: Ep 234

### Story 2 — {short title}
... (etc.)

## Contrarian takes (where Bryan disagrees with common HVAC teaching)

### Take 1 — {name}
- Common teaching: ...
- Bryan's position: ...
- His reasoning: ...
- Sources: Ep XXX, YYY

## Specific numbers Bryan cites (with sources when given)
- Superheat target on TXV system: ...
- TESP design budget: ...
- ... (table)

## Field tips (the "trick that saves 20 minutes")
- Tip 1: ...
- Tip 2: ...
- ... (bulleted)

## Bryan's characteristic phrases on this topic
- "..." — used in Ep XXX, YYY, ZZZ
- ... (quotable, for persona fidelity)

## Guest wisdom on this topic
- Ep {N} with {guest name} — key point: ...
- ... (compilation)

## Change log
- {date}: Initial extraction from {N} episodes
```

---

## 4. Extraction schema — 10 fields per episode

For every transcript file, the subagent extracts:

1. **Metadata**
   - Episode number (from filename or intro)
   - Date (if available)
   - Guest name(s) (if any) + guest specialty
   - Duration (if determinable)
   - Primary topic (single tag from the 12 topic compendia; pick most-emphasized)
   - Secondary topics (multi-tag, may include multiple compendium categories)

2. **Core teaching** — 1-3 key technical points Bryan drills into

3. **Canonical stories** — the "one time I saw this in the field..." anecdotes with:
   - Short title
   - Setting
   - Diagnostic chain
   - Root cause
   - Lesson

4. **Contrarian takes** — where Bryan disagrees with common HVAC teaching or manufacturer defaults

5. **Diagnostic reasoning chains** — how Bryan walks through fault isolation

6. **Specific numbers** — thresholds, targets, tolerances Bryan cites (with sources when he gives them)

7. **Field tips** — the "trick that saves 20 minutes" stuff

8. **Guest wisdom** — when a manufacturer or specialist guest drops knowledge worth capturing (attribute to guest)

9. **Recurring theme cross-refs** — this episode ties to episodes X, Y, Z on same topic (via Bryan's own "as I discussed on episode..." mentions or by content overlap)

10. **Quotable phrases** — Bryan's characteristic sayings, useful for future Bryan-persona responses

---

## 5. Agent orchestration

### 5A. Batch size
Batch of 32 transcripts per subagent. 960 / 32 = 30 subagents.

**Rationale:** Each subagent has its own context window. 32 transcripts × ~4,000 words = ~128,000 words per batch, well within a subagent's capacity to hold + reason over. Reduces if transcripts vary wildly in length.

### 5B. Subagent prompt template (to be adapted)

```
You are a research extraction agent. Read the following transcripts and produce
structured JSON per this schema:

[schema from §4]

Files to read: {batch_list}

Output: single JSON file at `_extraction/batch_{XX}.json` with one entry per episode.

Requirements:
- Faithful to source (verbatim quotes must be marked as such)
- No paraphrase drift
- No hallucination — if Bryan didn't cite a number, don't invent one
- Every extracted claim references an approximate transcript location (line
  range or timestamp if available)
- If a field has no data for a given episode, leave it empty
- Output must be valid JSON that can be programmatically merged
```

### 5C. Parallel execution
Spawn 30 subagents in parallel (or in waves of 5-10 to manage cost/context).

**Recommended waves:**
- Wave 1: 10 subagents on batches 1-10 (first 320 episodes)
- Verify output format on first 10 batches
- Wave 2: 10 subagents on batches 11-20 (episodes 321-640)
- Wave 3: 10 subagents on batches 21-30 (episodes 641-960)

### 5D. Cost estimate (rough)
- 30 subagents × ~130K tokens input each = ~4M input tokens
- 30 subagents × ~15K tokens output each = ~450K output tokens
- Total: significant but bounded. Estimate cost per API pricing at time of run.

### 5E. Wall clock estimate
- Sequential: 30 × 15-30 min per subagent = 7.5-15 hours (too slow)
- Parallel waves: 3 waves × 15-30 min = 45-90 min total (feasible)

---

## 6. Merge strategy

After all 30 batches produce JSON output:

1. **Consolidate** — load all `_extraction/batch_XX.json` into a single Python data structure
2. **Deduplicate** — episodes may overlap between batches if listing was imperfect
3. **Group by primary topic** — bucket episodes into the 12 topic compendia
4. **Compile per-compendium** — for each of 12 topics, generate the per-compendium output structure (§3B)
5. **Compile master** — generate the master file (§3A) with:
   - Full episode index sortable by number, date, topic
   - Topic frequency table (verified count from extraction, not initial scan)
   - Cross-reference matrix
   - Recurring phrases + guest index
6. **Version stamp everything** — v1.0, date, source count, method
7. **Write to canonical location** — `Personal Claude/snapai-board/references/bryan-orr/`

Merge script: use Python (via workspace bash) with pandas for tabular ops.

---

## 7. Where to reference — `snapai-board/references/bryan-orr/`

Per the board setup (see `advisor-kb-monthly-refresh` skill), each board member has a reference folder at:
`C:\Users\Shoab\My Drive\Personal Claude\snapai-board\references\bryan-orr\`

**Files in that folder to update:**

1. **`source_index.md`** — add the master compendium as primary knowledge source:
   ```
   ## Source: HVAC School Podcast Compendium v1
   - **Path:** references/bryan-orr/Bryan_Orr_HVAC_School_Master_Compendium_v1.md
   - **Type:** structured_knowledge_synthesis
   - **Coverage:** 960 episodes as of 2026-07-06
   - **Refresh cadence:** monthly (new episodes since last scan)
   - **Last refreshed:** {date}
   - **Status:** active
   ```

2. **`recent_thinking.md`** — refresh to include compendium as citation source. Point at the topic compendia for specific technical positions.

3. **`voice_examples.md`** — refresh with quotable phrases + characteristic language patterns extracted (from field #10 of the schema).

4. **`topics/`** — new subfolder containing all 12 topic compendia.

**Router update** (`Personal Claude/SnapAI_Project_Instructions.md`):
Add a row to Section 8 routing table:
```
| Anything requiring deep Bryan Orr HVAC domain expertise | `snapai-board/references/bryan-orr/Bryan_Orr_HVAC_School_Master_Compendium_v1.md` + relevant topic compendium from `topics/` folder |
```

---

## 8. Success criteria

The extraction is considered complete and shippable when:

1. All 960 transcripts (or actual count) processed into JSON
2. Master compendium file generated with episode index + topic frequency + cross-ref matrix
3. All 12 topic compendia generated with §3B structure
4. Every extracted claim cites source episode number
5. `snapai-board/references/bryan-orr/source_index.md` updated
6. `snapai-board/references/bryan-orr/recent_thinking.md` refreshed
7. `snapai-board/references/bryan-orr/voice_examples.md` refreshed
8. `SnapAI_Project_Instructions.md` routing table updated (new row)
9. All committed to git via DEC-070 flow (staging → main → prod)
10. Session log written at `session_logs/SESSION_LOG_{date}_bryan_compendium_extraction.md`

---

## 9. Estimated cost + duration

- **Wall clock:** 2-4 hours in the dedicated Cowork chat (assuming parallel-wave execution)
- **Token cost:** significant. Roughly 5M input + 500K output. At current pricing (Claude Sonnet), estimate ~$100-200. Confirm before executing.
- **Storage:** ~5-10 MB total for all compendium files. Fits comfortably in git.

---

## 10. Escalation

- **Extraction schema unclear:** escalate to Bryan (invoke `@board Bryan Orr`) via a separate chat while extraction is paused
- **Quality drift in subagent output:** stop wave 2, review wave 1 output, adjust prompt, re-run
- **Guest attribution ambiguity:** default to "Guest speaker on Ep {N}" without name until Bryan clarifies in review
- **Legal question on quoting Bryan verbatim:** escalate to Alfred (`@nav Alfred`)
- **Missing transcripts / broken files:** log missing, proceed with available. Master compendium notes gaps.
- **Any DEC-070 violation:** stop. This is docs-only for now, so DEC-070 flow means staging → main → prod for the output docs after extraction completes.

---

## 11. Ready-to-paste kickoff prompt (for the dedicated fresh chat)

Copy this section into the new chat's first message:

---

Continuing SnapAI Bryan Orr HVAC School compendium extraction. Standing rules apply (@board + @nav active, no emojis, DEC-070 flow, geo-neutral internal references OK).

READ FIRST: `ScopeSnapAI/SnapAI_Bryan_Compendium_Extraction_Plan_v1.md` — the full plan is there.

Execute per Sections 4-6 of the plan:
1. Verify source at `Personal Claude/HVAC_School_Transcripts/transcripts/` (should be ~960 .txt files)
2. Verify prior frequency scan matches source count
3. Confirm the 12 topic compendia list per Section 3B
4. Spawn Wave 1 — 10 subagents each processing 32 transcripts per Section 5B agent template
5. Report Wave 1 output format — pause for my approval before Wave 2
6. On approval, spawn Wave 2 (10 more)
7. On approval, spawn Wave 3 (final 10)
8. Merge per Section 6 via Python
9. Generate the 13 output files (1 master + 12 topics) per Section 3
10. Update `snapai-board/references/bryan-orr/` per Section 7
11. Update `SnapAI_Project_Instructions.md` router row per Section 7
12. Commit via DEC-070 flow (staging → main → prod)
13. Write session log per Section 8, criterion 10

Estimated wall clock: 2-4 hours. Estimated cost: $100-200 (confirm before Wave 1).

Ready. Report Section 1 (source verification) and pause for my go-ahead on cost.

---

## 12. Change log

- **2026-07-06:** Initial plan drafted by Bryan Orr (snapai-board) + Shoab. Not yet executed. Ready for dedicated session pickup.

---

## Related files

- `SnapAI_Project_Instructions.md` — router
- `session_logs/SESSION_LOG_2026-07-05_product_gap_fills_v7_tree.md` — where initial frequency scan is captured
- `snapai-board` skill — advisor board persona loader
- `advisor-kb-monthly-refresh` skill — related monthly refresh workflow
- DEC-070 — staging-first flow (applies to compendium output docs)
- Bryan Orr / HVAC School — https://hvacrschool.com/ (source attribution)
