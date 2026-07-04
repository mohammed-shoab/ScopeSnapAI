# SnapAI Legal Discussion — Continuation Prompt

**Purpose:** Paste this entire document as the FIRST message in a new chat inside the SnapAI project. It gives Claude the full context of where the SnapAI legal work stands, what has been decided, what documents exist, what standing rules apply, and what open decisions the user needs to resolve.

**All files are in the same folder (`C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\`) which is already mounted in the new chat.** Direct links below.

**Files to read (in this order):**

1. **This continuation prompt** — [computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Legal_Discussion_Continuation_Prompt.md](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Legal_Discussion_Continuation_Prompt.md)
2. **Verbatim board discussion transcript** — [computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Legal_Discussion_Verbatim_Transcript_2026-07-05.md](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Legal_Discussion_Verbatim_Transcript_2026-07-05.md)
3. **v2 deep audit (authoritative current state)** — [computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Legal_UI_Audit_v2_DEEP_2026-07-05.md](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Legal_UI_Audit_v2_DEEP_2026-07-05.md)
4. **v1 surface UI audit (superseded but useful for marketing findings)** — [computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Legal_UI_Audit_2026-07-05.md](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Legal_UI_Audit_2026-07-05.md)
5. **v1 ToS + five-layer framework DRAFT** — [computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Legal_Framework_ToS_and_Disclaimers_v1_DRAFT.md](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Legal_Framework_ToS_and_Disclaimers_v1_DRAFT.md)

---

## Read this FIRST, then open the four attached files in the order above

1. **Verbatim Transcript** — the actual board discussion from Bryan Orr raising Card #21 CO liability through Alfred's definitional-clause strategy. Read this to understand the flow of reasoning and the decisions the user has already made.
2. **v2 Deep Audit** — the current authoritative audit of what's legally wrong in the live SnapAI app. Read this to understand the concrete state of the codebase.
3. **v1 UI Audit** — the surface-level UI audit (superseded by v2 but useful for the marketing-page findings).
4. **v1 ToS Framework Draft** — the five-layer legal defense structure. Read this to understand what needs to be deployed.

---

## Standing rules for this chat (do not violate)

1. **Boards persist without invocation.** In every SnapAI chat, Bryan Orr and Mark Delgado from `snapai-board` remain active by default without explicit `@board` invocation. They answer or add color on all substantive discussions. The user can deactivate ("drop the boards") if they wish, but the default is on.
2. **Alfred is on for legal questions.** For legal-strategy or ToS-drafting questions, invoke Alfred from `snapai-nav` explicitly (or Claude may invoke Alfred proactively for legal work).
3. **No emojis in files unless the user explicitly requests them.**
4. **Never leak Bolder Park, Omni Sales OS, or Portugal D8 context into SnapAI work.** Each project has its own folder + workflow.
5. **Marketing docs go under `Personal Claude/marketing/`** — never root. Legal docs go under `Personal Claude/ScopeSnapAI/`.
6. **Homeowner-facing copy: NO future-tense outcome promises** (DEC-088). No "will save you $X," no "your bill will drop by Y%" — even hedged forward-looking language triggers Texas DTPA §17.46 exposure.
7. **Cartoon cats brand identity** — locked for contractor video content (not applicable to legal work, but relevant if the discussion extends to marketing).
8. **Tagline "Snap it. Diagnose it. Quote it. Close it." is currently locked.** NOTE: the word "Diagnose" in this tagline is exactly the issue Alfred flagged. Any change to the tagline is a marketing decision the user has not yet made — do not unilaterally propose retiring it, but do surface that the tagline is one of the legal risk items if the tagline discussion arises.
9. **App is transcripts + text ONLY for the diagnostic pipeline.** No audio, no STT — that's the Omni Sales OS scope decision, but also relevant here because SnapAI photo/reading inputs are the extent of the ingestion. Do not add new input modalities without a scope review.
10. **File writes for legal docs use bash heredoc, not the Edit tool** (DEC-027 — Cowork Edit tool has truncated `models.py` and `scorer.py` before). For any doc >100 lines, use `cat > file.md <<'EOF' ... EOF`.

---

## Current state of the SnapAI legal discussion (as of 2026-07-05)

### What's been decided

**Product-scope decision — Card #21 Heat Exchanger and Combustion Safety Check are Tier D (indefinite hold).** Alfred laid out six gates that must clear before Card #21 can ship (insurance rider, ToS rewrite, homeowner report language, threshold recalibration, PE engineering review, full audit trail). Combustion safety is NOT in scope for Tier A or Tier B. Bryan and Mark concurred.

**Product-scope decision — Ship Tier A first (Cards #20, #22, #23, #24, superheat/subcool discrimination, Airflow Assessment sub-flow, Comfort Complaint tab J), then Tier B (Cards #10 family, #15 family, Vacuum Validation), then Tier D only if six gates clear.** User committed to this sequencing after Bryan and Mark walked through the tradeoffs.

**Legal-strategy decision — Five-layer defense framework.** Alfred drafted the framework and saved it. The user's stated goal is "0 legal issue" — Alfred pushed back and explained that ~95% protection is the realistic ceiling. The user accepted this. The five layers are (1) homepage disclaimer, (2) contractor ToS, (3) contractor onboarding acknowledgment click-through, (4) in-app Output disclaimer, (5) homeowner report disclaimer.

**Legal-strategy decision — Five preventive design principles.** Alfred articulated these to engineer out the non-disclaimable risks:
1. No safety-critical diagnostics
2. No direct-to-consumer relationship
3. Language consistency between marketing and ToS
4. Documented QA + accuracy monitoring on every card
5. Substantiation file for every marketing claim

**Legal-strategy decision (tentative — user is considering) — Definitional-clause approach.** Alfred confirmed a Section 2A-2C definitional clause in the ToS works for contractor-facing "diagnosis" language (~55-60% of the rename work drops off). Alfred confirmed it does NOT work for homeowner-facing surfaces (DTPA §17.42 voids consumer waivers). User has not yet formally committed to this approach — the discussion ended with Bryan and Mark supporting it and Alfred delivering the exact clause text.

### What's confirmed live in the app (from v2 deep audit)

- **Zero Terms of Service deployed.** `/tos`, `/terms`, `/legal`, `/disclaimer` all return 404.
- **Homepage** (`snapai.mainnov.tech/`) uses "AI-Powered HVAC Estimation" title (good) but has unhedged marketing claims ("one honest recommendation," "AI identifies everything") and no footer ToS link.
- **`/homeowner` page** directly violates Texas DTPA §17.42 — markets to consumers with "A diagnostic report explaining what is wrong," "The app identifies the problem — no guessing," "★ RECOMMENDED" tier selection, plus a "Share with your contractor" CTA that pulls homeowners into a direct SnapAI consumer relationship.
- **`/tech` page** uses banned "diagnostic tool" language ("AI HVAC diagnostic tool," "Diagnose, estimate, and close").
- **Onboarding** at `/onboarding` — no ToS acceptance, no acknowledgment click-through, License # marked OPTIONAL. Anyone with an email can create an account.
- **In-app diagnostic UI** — no Output disclaimer anywhere. Sidebar nav shows "Diagnoses." "Cancel diagnosis" button visible.
- **LLM system prompts** (`scopesnap-api/prompts/cascade_prompts.py`) instruct the AI: *"You are an expert HVAC fault diagnosis system acting as a senior reviewer."* Both prompt templates (Track A + Track B).
- **Homeowner LLM prompt** (`homeowner_narrative.py`) instructs the LLM to write like a "doctor visit summary" and includes "honest" superlative. Example baked into prompt makes specific 15-20% efficiency claim to consumers.
- **Database schema** — tables named `diagnostic_questions`, `diagnostic_sessions`. API prefix `/api/diagnostic/*`. Event names `diagnostic_resolved`, `diagnostic_escalated`. Response fields `diagnosed_card_id`, `diagnosis_correct`.
- **Homeowner report PDF** (`contractor_estimate.html`) has zero SnapAI disclaimers — only contractor commercial terms. Footer says "This estimate was prepared using SnapAI HVAC Intelligence."
- **Homeowner-facing web report** (`app/r/[slug]/[reportId]/ReportClient.tsx`) titled "Equipment Health Report" with health-graded outputs ("Your system is in good shape," "Needs attention soon to prevent system failure") and algorithmic "★ RECOMMENDED" tier selection.
- **Homeowner follow-up emails** (`services/email.py`) include predictive claims ("see your 5-year savings," "HVAC issues get worse") and urgency framing ("last follow-up").

### What's pending (open decisions the user needs to make)

**1. Confirm definitional-clause strategy vs. wholesale rename.** Alfred delivered the analysis but the user has not formally chosen. Recommendation was the definitional-clause approach because:
- ~55-60% engineering savings
- Field-authentic contractor language preserved (Bryan's point)
- B2B/B2C split becomes useful product-design discipline (Mark's point)
- The 7 homeowner-facing surfaces still need full rewrite regardless

If the user confirms, the next step is (a) legal counsel review of Section 2A-2C clause, (b) apply the 7 mandatory homeowner-facing rewrites, (c) rewrite both LLM system prompts.

**2. Retain Texas-licensed attorney.** Alfred's estimate: $5-12K for full review including LLM prompts + report template + email templates in addition to the ToS itself. Recommended firms in Houston: Baker Botts (SaaS), Winstead PC (product liability), Jackson Walker (tech). User has not yet initiated outreach.

**3. Tech E&O insurance placement.** Alfred's estimate: $5-25K/yr baseline policy. Recommended brokers: Hiscox, Founder Shield, Vouch. User has not yet initiated outreach.

**4. Immediate stop-the-bleed items (Week 1) — user has not yet committed to a start date:**
- Publish v1 ToS at `/tos` (even unreviewed, better than nothing)
- Suspend `/homeowner` "share with your contractor" CTA (highest DTPA exposure)
- Add homepage prominent disclaimer above the fold
- Route homeowner emails through contractor domain OR add SnapAI decision-support disclaimer
- Add PDF disclaimer block to `contractor_estimate.html`
- Rewrite both LLM system prompts (`cascade_prompts.py` + `homeowner_narrative.py`)
- Rewrite homeowner report title from "Equipment Health Report" to "Contractor Assessment Report"

**5. Full remediation plan approval.** v2 audit lays out a 4-week plan with per-week priorities. User has not yet approved the plan or assigned start dates.

**6. Tagline decision.** "Snap it. Diagnose it. Quote it. Close it." contains "Diagnose" — Alfred did not push on this because the discussion focused on ToS and UI, but the tagline is part of the marketing surface Alfred flagged (Risk 2 — willful misconduct / language consistency). User should decide whether to retire "Diagnose" from the tagline or keep it under the definitional-clause strategy.

### Documents that exist (all in `C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\`)

| File | Contents | Status | Link |
|---|---|---|---|
| `SnapAI_Legal_Framework_ToS_and_Disclaimers_v1_DRAFT.md` | Alfred's five-layer defense framework; full v1 ToS draft (16 sections); Layer 3 onboarding acknowledgment; Layer 4 in-app disclaimer; Layer 5 homeowner report disclaimer | DRAFT — needs Texas counsel review | [Open](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Legal_Framework_ToS_and_Disclaimers_v1_DRAFT.md) |
| `SnapAI_Legal_UI_Audit_2026-07-05.md` | v1 UI-only audit of live app; 4 Critical + 5 High findings on marketing pages; framework coverage comparison; Week-by-week remediation plan | Superseded by v2 but retained for the marketing findings | [Open](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Legal_UI_Audit_2026-07-05.md) |
| `SnapAI_Legal_UI_Audit_v2_DEEP_2026-07-05.md` | v2 code + UI audit; 12 Critical + 11 High findings; LLM prompt findings; DB schema findings; PDF template findings; email template findings; 124-string frontend catalog; per-file severity ratings | **AUTHORITATIVE — current state** | [Open](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Legal_UI_Audit_v2_DEEP_2026-07-05.md) |
| `SnapAI_Legal_Discussion_Verbatim_Transcript_2026-07-05.md` | Verbatim board discussion from Bryan's initial CO liability raise through Alfred's definitional-clause proposal | Discussion record | [Open](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Legal_Discussion_Verbatim_Transcript_2026-07-05.md) |
| `SnapAI_Legal_Discussion_Continuation_Prompt.md` | This file — handoff prompt for the new chat | Handoff | [Open](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Legal_Discussion_Continuation_Prompt.md) |

### Related product / tree files (referenced in the discussion but not required for legal continuation)

| File | Purpose | Link |
|---|---|---|
| `SnapAI_Decision_Tree_v7_full_diagram.html` | v7 branching diagnostic tree with LIVE + NEW branches (source of the fault card scope discussion) | [Open](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Decision_Tree_v7_full_diagram.html) |
| `SnapAI_Decision_Tree_v6_with_gaps.html` | v6 card-grid gap-fills doc (Bryan's proposed additions) | [Open](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Decision_Tree_v6_with_gaps.html) |
| `SnapAI_Decision_Tree.html` | v5.1 audit-corrected LIVE tree | [Open](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Decision_Tree.html) |
| `SnapAI_Brain_and_Tree_Audit_2026-07-05.md` | Brain-file + tree audit awaiting Shoab's Q1-Q4 answers | [Open](computer://C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\SnapAI_Brain_and_Tree_Audit_2026-07-05.md) |

### Live app + code locations (audits refer to these)

- **Live prod app:** https://snapai.mainnov.tech
- **Frontend code:** `C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\scopesnap-web\` (Next.js — all UI text strings, React components, PDF templates via web share route)
- **Backend code:** `C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\scopesnap-api\` (FastAPI — LLM prompts, API endpoints, PDF templates via server, email templates)
- **LLM prompts (highest-leverage fix):** `C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\scopesnap-api\prompts\cascade_prompts.py` + `homeowner_narrative.py`
- **PDF report template:** `C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\scopesnap-api\templates\contractor_estimate.html`
- **Homeowner email templates:** `C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\scopesnap-api\services\email.py`
- **Homeowner report web page:** `C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\scopesnap-web\app\r\[slug]\[reportId]\ReportClient.tsx`
- **Fault resolution UI component:** `C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\scopesnap-web\components\FaultResolutionScreen.tsx`
- **Sidebar nav (the "Diagnoses" tab):** `C:\Users\Shoab\My Drive\Personal Claude\ScopeSnapAI\scopesnap-web\components\SidebarNav.tsx`

---

## How to continue the discussion in the new chat

**Suggested opening prompt for the user:**
> "Continuing the SnapAI legal discussion from the previous chat. Bryan, Mark, and Alfred are on. Read the attached transcript + audit docs. I want to [state your specific goal — e.g., 'commit to the definitional-clause approach and get the exact week-1 checklist' or 'decide whether to retain Baker Botts vs Winstead' or 'get Alfred to draft the finalized Section 2A-2C after I give him feedback' or 'work through the homeowner report rewrite']."

**What Claude should do at the start of the new chat:**
1. Confirm that Bryan and Mark are on (per standing rule 1) and Alfred is available for legal questions (per standing rule 2)
2. Read the four attached docs in the order specified above
3. Do NOT re-audit or re-derive findings — the audit is authoritative as-of 2026-07-05; if the user wants a re-audit, they will ask
4. Answer the user's specific question in-line, deferring to Alfred for legal issues and Bryan/Mark for HVAC + product angles
5. If the user says "let's ship [item X]" — ask which of the 7 mandatory homeowner-facing surfaces is being touched, and whether Alfred should review the specific language before deploy
6. If the user asks Claude to write new legal-related files, save to `Personal Claude/ScopeSnapAI/` using bash heredoc (never Edit tool for legal drafts)
7. Update the v2 audit doc as items are addressed (mark items resolved with a strikethrough or a "RESOLVED 2026-XX-XX" note)

**What Claude should NOT do:**
- Do not restart the discussion from Card #21 CO liability — that decision is settled (Tier D indefinite hold)
- Do not re-derive the five preventive design principles — those are settled
- Do not re-explain the five layers of the defense framework — the user has read them
- Do not propose retiring the definitional-clause strategy unless the user brings up a new blocker
- Do not initiate any code changes without confirming with the user (all code fixes must be authorized per-item)
- Do not initiate any legal-doc changes on the live app without the user's explicit approval (v1 ToS is a DRAFT — not deployed language)

---

## Quick reference — key legal citations from the discussion

The verbatim transcript contains these authorities. If the user asks "what's the case for X?" here they are quickly:

- **Texas DTPA §17.42** — voids all consumer waivers of DTPA protections. Reason the definitional-clause approach fails for homeowners.
- **Texas DTPA §17.46** — deceptive trade practices standard; unsubstantiated superlatives trigger treble damages + attorneys' fees.
- **Restatement 2d §402A** — strict product liability; cannot be waived by contract in most states.
- **Texas Civil Practice & Remedies Code §16.012** — 15-year statute of repose; Card #21 outputs today carry potential liability until 2041.
- ***Meyer v. Uber* / *Cullinane v. Uber*** — ToS enforceability requires "reasonably conspicuous notice AND unambiguous manifestation of assent."
- ***Wickline v. State* / *Wilson v. Blue Cross*** — learned intermediary doctrine protects decision-support software when a licensed professional is the final decision-maker.
- ***FTC v. Amazon* / *FTC v. Tapjoy*** — UI language overrides disclaimer language when they conflict.
- **NFPA 54** — gas code; 100 ppm CO is the emergency-service level (Alfred said this is too permissive for product-liability defense).
- **OSHA 8-hour exposure limit** — 35 ppm CO.
- **EPA §608** — refrigerant handling is contractor-only; unlicensed users cannot handle refrigerant.
- **Illinois BIPA** — biometric information private cause of action ($1,000-$5,000/violation); relevant if photos include people.

---

## Bryan Orr's persistent field-authenticity themes

Bryan has surfaced these across the discussion — carry them forward:

1. **Fault-card resolution language visible to techs must match how techs actually talk.** "Diagnosis" is authentic tech vocabulary. "Assessment" is authentic homeowner vocabulary. Both audiences deserve their own language.
2. **Card #24 Oversizing bias must be conservative** — $8-15K per wrong output. Never fire without two supporting readings + Manual J + age gate.
3. **Combustion safety is combustion analysis + visual — not either/or.** If SnapAI ships anything HX-related, it's both or nothing.
4. **CO threshold gradient matters:** 9 ppm ambient = investigate, 35 ppm = OSHA limit, 100 ppm = emergency (NFPA 54). Alfred's product-liability threshold recalibration matches Bryan's field practice.
5. **Techs skim disclaimers.** Layer 4 in-app Output disclaimer must be inline text, always visible, never behind a "learn more" link.

## Mark Delgado's persistent product-strategy themes

Mark has surfaced these across the discussion — carry them forward:

1. **"Perfect" is a moving target, not a build spec.** Ship Tier A in 6 weeks, learn from real Houston traffic, then Tier B. Do not delay shipping in pursuit of perfection.
2. **Card #21 delay is a positioning asset, not a weakness.** "We chose not to ship HX diagnostics until our insurance, threshold engineering, and legal framework meet the standard our contractors' families deserve" is a stronger story than shipping the card.
3. **The B2B/B2C split (from Alfred's Principle 2) is competitive strategy.** "SnapAI works FOR contractors — never around them" differentiates from ServiceTitan and Housecall Pro.
4. **v2 audit is a product-identity finding, not a marketing problem.** Fixing the LLM prompt + PDF template + report title is stronger product positioning + legal protection from the same rewrite.
5. **Pre-commit hook to enforce B2B/B2C language split** — mechanical enforcement prevents drift. Simple hook: block "diagnos*" strings in `app/homeowner/`, `app/d/`, `app/r/`, `templates/`, and homeowner-touching sections of `services/email.py`.

---

## End of continuation prompt

**Ready to continue.** Ask the user their specific goal for the new chat and Alfred + Bryan + Mark will pick up where the previous discussion left off.

