# SESSION LOG - Bryan Orr HVAC School Compendium Extraction - 2026-07-08

**Duration:** ~2 hours (parallel-wave subagent execution)
**Participants:** Shoab + Claude (Opus orchestrator + 30 Opus extraction subagents)
**Related workstream:** snapai-board advisor knowledge base (Bryan Orr persona grounding)
**Related files:**
- Plan: ScopeSnapAI/SnapAI_Bryan_Compendium_Extraction_Plan_v1.md
- Master output: snapai-board/references/bryan-orr/Bryan_Orr_HVAC_School_Master_Compendium_v1.md
- Topic outputs: snapai-board/references/bryan-orr/topics/Bryan_Compendium_*.md (12 files)
- Router: SnapAI_Project_Instructions.md (Section 8 routing row added)
- Source corpus: HVAC_School_Transcripts/transcripts/ (960 files; 959 transcripts + 1 URL index)

---

## Context (what we started with)

The snapai-board Bryan Orr persona was grounded only on scraped bio/interview pages (7 sources in source_index.md). The full HVAC School podcast back-catalogue - 959 episode transcripts, ~3.8M words - sat unmined in HVAC_School_Transcripts/transcripts/. The extraction plan (v1, committed to prod 2026-07-06) specified a 30-subagent parallel extraction into a structured compendium.

## Goal

Execute Sections 4-6 of the plan: verify source, run 3 waves of 10 subagents each (32 transcripts per batch), merge to JSON, generate 1 master + 12 topic compendia, wire into board references + router, commit, log.

## What we did

1. **Source verification.** Confirmed 960 .txt files. Discovered 1 is `_videos_without_captions.txt` (a YouTube URL index, not a transcript) -> 959 real transcripts. Filenames are YouTube titles with bracketed video IDs, NOT `{episode_number}_{title}` as the plan assumed. Decision: use the video ID as the stable citation key; capture spoken episode number only when stated in-transcript.
2. **Batching.** 959 -> 30 manifests (29x32 + 1x31) written to _extraction/manifests/.
3. **Model choice.** Shoab chose Opus for all 30 subagents (highest fidelity; higher cost accepted).
4. **Wave 1 (batches 1-10, 320 eps).** Validated: 320/320, 0 schema/tag violations. Format approved.
5. **Taxonomy decision.** Kept the 12 canonical primary-topic tags for extraction consistency across all 30 batches; install/drains/brazing/hydronics (no dedicated tag) mapped to nearest bucket with true theme in secondary_topics/field_tips. "Use as much as required" -> expand at merge if a cluster warrants; all 12 buckets ended well-populated so no 13th bucket needed for v1.
6. **Wave 2 (11-20) + Wave 3 (21-30).** All validated. Final corpus: 959 episodes, 0 schema/tag violations, 959 unique video IDs, 0 duplicates.
7. **Merge + generation.** Python merge (generate_compendium.py) -> 1 master (178 KB) + 12 topic files (~2.8 MB total). Master carries: topic frequency table, primary-x-secondary cross-reference matrix, 256-guest specialty index, sampled recurring Bryan-isms, documented source-gap table, and full 959-row episode index.
8. **Board reference wiring.** source_index.md (+1 source, refreshed date, source_count 7->8), recent_thinking.md (+canonical knowledge base section), voice_examples.md (+verbatim technical phrasing section). Router SnapAI_Project_Instructions.md: added Section 8 routing row ("Deep HVAC domain expertise / Bryan Orr technical grounding..." -> master + topics), bumped header + last-updated line.

## Verified numbers

- Episodes processed: 959 (948-950 with recoverable content; 9-11 no-caption/corrupt stubs documented in master)
- Topic distribution: Electrical and Controls 182, Tools and Instruments 152, Refrigeration Cycle 127, Business and Trade 91, Airflow 88, Diagnostics Methodology 85, Comfort and Latent 63, Compressor 57, Vacuum and Recovery 46, Combustion and HX 31, Metering Devices 28, Guest Wisdom 9
- Guests indexed: 256
- Content volume: e.g. Refrigeration Cycle bucket = 466 cited numbers, 397 field tips; Electrical bucket = 540 field tips, 452 numbers

## Root causes / gotchas found

- **Sandbox bash flakiness.** `mcp__workspace__bash` intermittently returned "process already running" (Google Drive mount latency). Subagents adapted by reading transcripts via the Read tool on Windows paths and building JSON via Python. No data lost.
- **Drive mount blocks deletion.** `rm` returns "Operation not permitted" on the Drive mount. Several subagents left scratch build .py files in _extraction/ (and one build_b28.py in HVAC_School_Transcripts/). These are inert - the merge reads only batch_XX.json - but need manual deletion from Windows. (Later waves were instructed to keep helpers in /tmp.)
- **Pre-existing NUL bytes.** source_index.md had 7 trailing NUL bytes (NTFS truncation artifact per DEC-005). Cleaned during the reference update; all 13 generated files verified NUL-free.
- **No-caption files = corrupt transcripts.** The ~11 empty-content entries correspond to videos in `_videos_without_captions.txt`; their .txt files are boilerplate/ASR-garbage. Recorded as stubs, not re-downloaded for v1.

## OPEN items

- **Commit path unresolved (criterion 9).** The 13 compendium files + board refs + router live in the Drive-synced workspace, OUTSIDE the ScopeSnapAI git repo (snapai-board/ is not tracked; verified `git ls-files` = 0 matches). Only this session log lives inside the repo (session_logs/ is tracked). DEC-070 staging->main->prod cannot apply to files not in the repo. Awaiting Shoab's decision on whether to (a) leave board refs in Drive only, (b) relocate/mirror them into ScopeSnapAI and commit, or (c) commit only the session log + router via DEC-070.
- Manual cleanup of scratch .py files in _extraction/ and HVAC_School_Transcripts/ (Drive-side delete).
- Optional v1.1: re-download the ~11 no-caption episodes; consider a 13th "Installation & Maintenance" bucket if that cluster proves heavily queried.

## Success criteria status (plan Section 8)

1. All 959 transcripts processed -> DONE
2. Master compendium (index + frequency + cross-ref) -> DONE
3. 12 topic compendia -> DONE
4. Every claim cites source episode (video ID) -> DONE
5. source_index.md updated -> DONE
6. recent_thinking.md refreshed -> DONE
7. voice_examples.md refreshed -> DONE
8. Router routing row added -> DONE
9. Committed via DEC-070 -> OPEN (see above; outputs are outside the repo)
10. Session log written -> DONE (this file)
