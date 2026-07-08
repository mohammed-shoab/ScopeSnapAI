# SnapAI Video-Marketing Discussion — Continuation Prompt

**Purpose:** Paste this entire document as the FIRST message in a new chat inside the SnapAI Cowork project. It gives the new AI the full context of where the SnapAI video-marketing + virality strategy stands, what has been decided, what documents exist, what standing rules apply, and what open decisions Shoab needs to resolve. After you paste this, attach the verbatim transcript listed in Section 1 below for full session history.

**All files below live in the same folder (`C:\Users\Shoab\My Drive\Personal Claude\`) or its `ScopeSnapAI\` and `marketing\` subfolders — the folder is already mounted in the new chat.**

---

## 1. Files to open (in this order)

1. **This continuation prompt** — [computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_VideoMarketing_Discussion_Continuation_Prompt_2026-07-08.md](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_VideoMarketing_Discussion_Continuation_Prompt_2026-07-08.md)
2. **Verbatim chat transcript** (this session's back-and-forth) — [computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_VideoMarketing_Discussion_Full_Chat_Transcript_2026-07-08.md](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_VideoMarketing_Discussion_Full_Chat_Transcript_2026-07-08.md)
3. **Boards' options doc from 2026-07-01** (27-voice pressure test — the base of this thread) — [computer://C:\Users\Shoab\My Drive\Personal Claude\marketing\SnapAI_Virality_FreeTrial_Strategy_Boards_Recommendations_2026-07-01.md](computer://C:\Users\Shoab\My Drive\Personal Claude\marketing\SnapAI_Virality_FreeTrial_Strategy_Boards_Recommendations_2026-07-01.md)
4. **Two-Door video strategy foundation** (2026-05-22 — the strategic base under everything) — [computer://C:\Users\Shoab\My Drive\Personal Claude\marketing\SnapAI_Video_Marketing_Strategy_TwoDoor.md](computer://C:\Users\Shoab\My Drive\Personal Claude\marketing\SnapAI_Video_Marketing_Strategy_TwoDoor.md)
5. **Video-analysis Gemini prompts v2** (operational layer for Video 1 + Video 2) — [computer://C:\Users\Shoab\My Drive\Personal Claude\marketing\SnapAI_Video_Analysis_Prompts_for_Gemini_v2.md](computer://C:\Users\Shoab\My Drive\Personal Claude\marketing\SnapAI_Video_Analysis_Prompts_for_Gemini_v2.md)
6. **Azhan production plan** — [computer://C:\Users\Shoab\My Drive\Personal Claude\marketing\Azhan\SnapAI_Azhan_Plan_v2.md](computer://C:\Users\Shoab\My Drive\Personal Claude\marketing\Azhan\SnapAI_Azhan_Plan_v2.md)
7. **SnapAI Project Instructions router** (loads on every session) — [computer://C:\Users\Shoab\My Drive\Personal Claude\SnapAI_Project_Instructions.md](computer://C:\Users\Shoab\My Drive\Personal Claude\SnapAI_Project_Instructions.md)
8. **STATUS.md** (current live state) — [computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\STATUS.md](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\STATUS.md)

---

## 2. Read this FIRST, then open the files above

- **File 2 (verbatim transcript)** contains the actual back-and-forth from the previous session including the 33-voice board re-ask (Panel 5 + MrBeast + Reilly + updated positions from the original 27 voices). Read it to understand the flow of reasoning.
- **File 3 (2026-07-01 options doc)** is the ORIGINAL 27-voice pressure test. It has the Stanley + Charlotte Trecartin research, the 5 protections, the 3 death risks, and the 7 open questions. File 2 references it constantly.
- **File 4 (Two-Door strategy)** is the strategic foundation everything sits on: Door A homepage hero (single asset, diagnosis-led), Door B social shorts (variety across 8 angles, cartoon-cat universe).

---

## 3. Standing rules for this chat (do not violate)

1. **Boards persist without invocation.** In every SnapAI chat, `@board` (25 members including Panel 5) and `@nav` (17 seats including Alfred, MrBeast, Reilly) remain active by default. Bryan Orr + Mark Delgado chime in on substantive discussions without explicit invocation. Shoab can say "drop the boards" to deactivate.
2. **Alfred is on for legal questions.** Any UGC amplification, ToS change, contractor onboarding language, or free-trial wording needs Alfred's sign-off.
3. **Read the router file first for any task.** `SnapAI_Project_Instructions.md` Section 8 has the 20-row routing table.
4. **Marketing docs go under `Personal Claude/marketing/`** — never Personal Claude root. Legal + code + brain-file docs go under `Personal Claude/ScopeSnapAI/`.
5. **Homeowner-facing copy: NO future-tense outcome promises** (DEC-088). No "will save you $X," no "your bill will drop by Y%." Texas DTPA §17.46.
6. **Cartoon cats brand identity is locked** for social shorts (Door B). Not applicable to homepage hero (Door A).
7. **Tagline "Snap it. Diagnose it. Quote it. Close it." is currently locked** — but "Diagnose" is a flagged legal-risk word (Alfred's earlier finding). Do not unilaterally propose retiring it; do surface it if a tagline decision comes up.
8. **No emojis in files unless Shoab explicitly asks for them.**
9. **DEC-027:** Cowork Edit tool truncates files with Unicode. For files >100 lines, use `cat > file.md <<'EOF' ... EOF` heredoc via `mcp__workspace__bash`.
10. **DEC-070:** All doc-shipping goes through staging → main → prod. For marketing docs the ship pattern is `feat(marketing)` → staging → `promote(marketing)` scoped promote → main.
11. **Session close ritual = analyze + propose, NOT ask questions.** Per Section 7 of the router — at end of substantive session, analyze what happened, decide which brain files to update using the routing table, present ONE consolidated proposal, wait for Shoab's yes, execute in one pass.
12. **Bryan Orr compendium is live** at `Personal Claude/snapai-board/references/bryan-orr/` (also mirrored in git at `ScopeSnapAI/snapai-board/references/bryan-orr/`). 959-episode structured extraction. When Bryan speaks with a specific technical claim, cite the source episode by video ID.
13. **Writing Guidelines v1 is live** at `ScopeSnapAI/SnapAI_Writing_Guidelines_v1.md`. Any copy work (landing pages, video captions, cold emails, social posts, disclaimers) MUST comply — the guide has DTPA substitution tables, Alfred flag system `[A!]`/`[A]`, brand voice locks, 5-step SOP.

---

## 4. Current state of the video-marketing discussion (as of 2026-07-08)

### The strategic play on the table (unchanged since 2026-07-01)

**Three moves being pressure-tested:**
1. **Virality as acquisition engine** — 100+ AI-generated cartoon-cat videos per month across TikTok / Reels / YouTube Shorts. Not chasing "millions of views" — chasing enough views to drive tester signups.
2. **Free extended trial** — ~1 month free for anyone signing up from viral traffic. Marketing language: "Free during beta period. Pricing will be announced with advance notice." (Alfred-approved, DEC-130 shipped.)
3. **Product becomes indispensable via dependency** — junior + mid techs adopting SnapAI stop calling seniors for diagnoses. Cheaper labor delivers senior-quality output. Shop owners save on labor cost.

### What's SHIPPED since 2026-07-01 (context the new chat needs)

- **DEC-130 legal-safe-wordings v1 SHIPPED to prod 2026-07-06** (prompts, report H9/H10, gate C3, /tos, /methodology, redirects, email). Protection #1 from the original 2026-07-01 doc is now CLOSED.
- **Tier A app upgrades SHIPPED 2026-07-07** — Cards #20 Under-Airflow, #22 Latent Deficit, #23 Thermostat, #24 Oversizing, Airflow Assessment sub-flow, Comfort Complaint tab J, superheat/subcool discrimination on Card #8, Reading Receipt (deterministic numeric), migration 047. More diagnostic capability = more data-per-user = data moat strengthened.
- **Writing Guidelines v1 SHIPPED 2026-07-07** (`ScopeSnapAI/SnapAI_Writing_Guidelines_v1.md`, 369 lines, DEC-070). Brand voice locked, DTPA substitution tables, disclaimer text canonical.
- **Bryan Orr HVAC compendium SHIPPED 2026-07-08** (959-episode structured extraction, 12 topic files, 3 board refs). Panel 5's Bryan seat now grounded in real citations. DEC-131 (mirror-and-promote pattern for board-persona reference material) set the precedent.
- **Brain-files pass 1 executed 2026-07-08** — STATUS.md + ACTIVE_TASKS.md + DECISIONS.md (DEC-131) updated. **DEC-070 ship of pass 1 is PENDING** — deliberately held to batch with pass 2 at end-of-session.

### The 6 new board voices added 2026-07-02 (crucial context)

**@board Panel 5 (video marketing):**
- **Bryan Orr** — trades audience-seed gate. Warm, technical, calm, wry. His podcast reaches SnapAI's actual buyer.
- **Jenny Hoyos** — short-form storyline-craft gate. "Queen of YouTube Shorts." Full-arc storytelling in under 60 seconds. 70%+ retention.
- **Zaria Parvez** — mascot voice-identity gate. Built Duolingo's Duo character. Gives mascots a specific human voice, not corporate smile.
- **Alex Su** — B2B-niche TikTok specialist. `@legaltechbro`. Insider knowledge → performative comedy without dumbing down.

**@nav additions:**
- **MrBeast (Jimmy Donaldson)** — quantitative retention engineering. "How to succeed in MrBeast production" leaked memo. Title-and-thumbnail-first. Kill C-players immediately.
- **Terence Reilly** — mainstream-breakthrough architect. Actual Stanley Quencher operator ($70M → $750M). Also ex-Crocs CMO. Chase hearts not wallets.

### What the 33-voice board re-ask on 2026-07-08 concluded

**Where the boards ALL now agree (unchanged from 2026-07-01):**
1. Ship the strategy — 5 protections must hold
2. "Leverage senior tech" reframe (not "replace" — Bryan compendium now makes this defensible)
3. Diagnostic accuracy Q7.1 gates EVERYTHING — measure this week (still open)
4. Data moat compounds regardless of conversion — strengthened by Tier A
5. Engineered virality via right seeder / right demo — Reilly says wait for organic
6. Test-and-measure discipline (Levels + MrBeast fully aligned)
7. Legal cover shipped — Protection #1 CLOSED

**NEW consensus from Panel 5 + Reilly + MrBeast:**
8. Cartoon cats = awareness + reverse-demand play, NOT primary shop-owner acquisition (Bryan). Primary for shop owners is podcast circuit + real-tech content.
9. Voice-identity work is a PREREQUISITE, not a nice-to-have. Cats need a specific human voice before scale (Zaria + Fadell + Reilly).
10. Master ONE platform first — TikTok (Alex Su). Skip Reels for shop-owner buyer, LinkedIn is Sajan's parallel channel with different content.
11. Every video engineered as a full arc with a template (Jenny). Not "make it cute" — "make it structurally complete."
12. Metrics-per-video from day 1 (MrBeast). Kill formats that miss thresholds within 5 videos.
13. Amplify a real organic tester win, don't manufacture the Stanley moment (Reilly). Don't over-invest in the machine before ONE real win exists.

**Where DISSENT is now sharper:**
- Bryan vs "100 videos/month" plan → resolution: run BOTH funnels (cartoon cats for awareness, podcast pitch + real-tech content for buyer conversion). Different metrics, no confusion.
- Reilly vs "engineer virality" framing → resolution: engineered production, organic seeding. Build the machine but let it AMPLIFY real wins, don't manufacture the win itself.

---

## 5. STILL BLOCKING (unchanged from 2026-07-01, now overdue)

- **Q7.1 diagnostic accuracy measurement.** Karpathy's threshold: >80% required for dependency to form. Was flagged "this week" on 2026-07-01 — STILL OPEN a week later. Concrete ask: measure the % of tester-submitted diagnostic cases from the last 30 days where SnapAI's suggested primary card matched the confirmed field outcome. Sample size ≥50. If <80%, everything else waits.
- **Q7.3 named 50 shop owners list.** Jordan Crawford's view-density approach. Need the list built before videos ship so demo fit can be measured.

## NEW BLOCKS surfaced by re-ask

- **Zaria's voice-identity work on Tech Tom + Homeowner Cat** — days of work, not weeks. Prerequisite before video 6.
- **UGC amplification rights in ToS** — Alfred flag: needed before Reilly-playbook amplification of any tester win.
- **Senior tech advocate seeding** — Delgado's original flag, still open. Top 10 Houston shop trainers, "SnapAI Certified Trainer" designation.

## 5 open questions from 2026-07-01 doc still open

- Q7.2 Primary buyer persona for videos (techs / shop owners / homeowners)
- Q7.4 Is the daily-ritual metric measurable in-app?
- Q7.5 Automated production pipeline architecture
- Q7.6 Value metric for pricing (per-diagnostic / per-tech / per-shop / %-of-closed-revenue)
- Q7.7 Which 3 videos ship first for the 14-day empirical test

---

## 6. Updated 5-item ordered action list (from 2026-07-08 board re-ask)

1. **Measure diagnostic accuracy.** Third time asking. Owner: Shoab. Timeline: 48 hours.
2. **Ship the 3-video 14-day empirical test** using Video 1 + Video 2 + one new script following Jenny's arc template. Master TikTok first (Alex Su). Track MrBeast metrics per video. Owner: Azhan. Timeline: 5 days.
3. **Zaria voice-identity workshop** — lock Tech Tom + Homeowner Cat attitude before videos-per-week ramps. Owner: Shoab + Azhan (Zaria advisory). Timeline: parallel with #2.
4. **Build the named 50-shop-owner list** using Jordan's signal filters (hiring HVAC techs in Houston + recent negative reviews + ACCA-listed with no ServiceTitan/Housecall). Owner: Sajan. Timeline: 1 week.
5. **Pitch Bryan Orr for HVAC School guest spot** with a compendium-cited diagnostic story. Owner: Shoab (via `snapai-podcast-pitch` skill). Timeline: 2 weeks.

---

## 7. The 3-move decision waiting on Shoab (last message of prior session)

At the end of the 2026-07-08 board re-ask, the AI offered Shoab three next-move options:

- **Move A — Save the session as an options doc.** Persist the 33-voice discussion as `marketing/SnapAI_Virality_v2_Boards_Recommendations_2026-07-08.md` mirroring the 2026-07-01 structure. Gives Sajan/Azhan/Priya a reference for execution work.
- **Move B — Act on ONE item from the 5-item ordered list.** Strong recommendation: Karpathy's accuracy measurement (Q7.1). Nothing else is worth executing until that number exists. If <80% → thesis fails and viral videos amplify a broken product. If ≥80% → whole strategy is defensible. Cost: ~4 hours of Sajan pulling last-30-days tester data.
- **Move C — Close the session with brain-files pass 2 + DEC-070 ship.** Batches pass 1 + pass 2 commits together to staging → main. Encodes: voice-identity work now a prerequisite, engineered-production/organic-amplification synthesis, updated action list.

Shoab did NOT pick A/B/C — instead he asked for this handoff to a fresh chat. **When you open this new chat, your FIRST question should be: "Shoab, which of A / B / C (or combination) do you want to run first in this new chat?"**

---

## 8. What to do FIRST in this new chat

1. Read files 3, 4, 8 (options doc, Two-Door strategy, STATUS.md) BEFORE responding to Shoab
2. Read files 5, 6 (Gemini prompts + Azhan plan) if Move B or Move C is chosen
3. Attach or paste the verbatim transcript (file 2) if Shoab wants to reference specific past exchanges
4. Ask Shoab to pick A / B / C or a combination
5. DO NOT propose brand-new strategy — the 33-voice consensus is the base. Any strategic shift needs to be surfaced explicitly with reference to which voice(s) are changing position and why.

---

## 9. Personas most relevant to reactivate in this chat

If Shoab picks **Move A** (save doc): Codie Sanchez writes the actual summary (per Section 8 skill routing); Jeanne DeWitt Grosser frames the sequence structure.

If Shoab picks **Move B** (accuracy measurement): Karpathy leads (threshold owner); Will (data pipeline); Rob (system architecture); Joe (verification).

If Shoab picks **Move C** (close session): analyze + propose per Section 7. Files to update: STATUS.md (workstream #4 status change), ACTIVE_TASKS.md (new session block), DECISIONS.md (DEC-132 if a real decision landed), possibly a new session log.

If Shoab picks **execute the 5-item action list**: the full 33-voice roster is available — bring forward the 6-10 most relevant per Section 7 skill discipline.

---

## 10. Key numbers to remember

- 27 voices weighed in on 2026-07-01 (12 @board + 15 @nav — original roster before Panel 5 additions)
- 33 voices in the 2026-07-08 re-ask (27 original + Panel 5's 4 + @nav's MrBeast + Reilly)
- Karpathy's diagnostic accuracy threshold: **>80%**
- Lincoln Murphy's realistic trial-to-paid conversion: **2-5%** (500 free testers → 10-25 paying customers by month 6)
- Levels's 14-day test threshold: **50+ signups = works, <10 = wrong**
- MrBeast's retention discipline: first-3-second retention + full completion + signup conversion tracked per video, kill formats missing thresholds within 5 videos
- Alfred's shipped free-trial language: **"Free during beta period. Pricing will be announced with advance notice."** (DEC-130, prod 2026-07-06)

---

## 11. Change log

- **2026-07-08** — this continuation prompt created + verbatim chat transcript created (both in ScopeSnapAI/). Companion doc: SnapAI_VideoMarketing_Discussion_Full_Chat_Transcript_2026-07-08.md.

---

**End of continuation prompt. Now open the files listed in Section 1 in the order given.**
