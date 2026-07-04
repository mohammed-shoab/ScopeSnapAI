# SnapAI -- Legal-Safe Wordings + Gate + ToS DEPLOYMENT DISPATCH (v1.1, 2026-07-06)

>>> UPDATE 2026-07-06: A starting branch is already built. Apply
>>> SnapAI_LegalWordings_APPLIED_2026-07-06.patch (off origin/staging) instead of implementing
>>> from scratch -- it already contains: LLM prompt rewrites, homeowner email fixes, report+share
>>> assessment wording, /tos+/methodology pages, /tech legal removals + waitlist move + redirects
>>> (dead pages deleted), report 5-year-block removal + RECOMMENDED + H7 labels, and the full
>>> contractor gate C3 (migration 045). See SnapAI_Legal_Wordings_Implementation_Status_2026-07-06.md
>>> for exactly what is DONE vs the remaining follow-ups (D7 field rename+test, D8 pre-commit hook,
>>> gate tests, ToS content + Alfred sign-off, methodology numbers, Codie sign-off on /tech copy).
>>> All three prior open decisions are RESOLVED (waitlist kept/moved, 5-year removed, gate authorized).
>>> Your job: apply patch -> finish the follow-ups -> staging -> /snapai-qa -> Shoab confirm ->
>>> prod -> /snapai-qa -> update brain/tech-stack docs. Hard gates still stand.

PASTE THIS ENTIRE FILE AS THE FIRST MESSAGE IN A NEW SnapAI PROJECT CHAT.

You are the execution lead. Deploy the SnapAI "legal-safe wordings v1" change set PLUS the
contractor onboarding GATE (C3) PLUS the Terms of Service at /tos PLUS the single-landing-page
consolidation: build it in STAGING, QA it, get Shoab's confirmation, promote to PROD, QA it
again, then update the project brain + tech-stack docs. You have Desktop Commander (file + shell
on the real machine) and Chrome (live browser). Use 10-18 agents/subagents across the phases.

DO NOT edit anything until PHASE 0 (bootstrap) is complete and Shoab has approved scope in
writing. Leave NOTHING to assumption. When unsure, STOP and ask Shoab.

================================================================
SECTION 0 -- NON-NEGOTIABLE OPERATING RULES (read first, obey always)
================================================================

CODE-STATE TRUTH (DEC-111): The Google-Drive working copy is days-to-weeks stale. NEVER reason
about code state from local Drive files. Before ANY code-state claim run, in a sandbox clone:
    cd ScopeSnapAI && git fetch origin --no-tags
    git log origin/main --oneline -5
    git log origin/staging --oneline -5
Use `git show origin/<branch>:<path>` to read the REAL current file, not the Drive copy.

GIT OPS (DEC-004): All git operations run from a sandbox clone at /tmp/snapai_tmp.

UNICODE / FILE-WRITE SAFETY (DEC-005 + DEC-027): Silent NTFS truncation bug on this Drive for
.py/.md files; the Edit tool has truncated files before. For any file with em-dashes/emoji/Urdu/
Rs or >100 lines: DO NOT use the Edit tool. Use bash heredoc or Desktop Commander write. After
every write verify with `wc -l` + tail-check.

GIT INDEX CORRUPTION FALLBACK (DEC-028): if the index corrupts, use git fast-import fallback.

STAGING-FIRST PER PR (DEC-070): Every change follows the documented 7-step staging-first workflow.
READ ScopeSnapAI/WORKFLOW.md and DECISIONS.md (DEC-070) and follow them literally. Do not invent
a pipeline.

HOMEOWNER-COPY BAN (DEC-088): No future-tense outcome promises in homeowner-facing copy. BANNED:
prevent, guarantee, ensure, will not, lasts X years, eliminates, stop forever, "save you $X",
"bill will drop", "5-year savings", "issues get worse", any predictive claim about a specific
unit. Delete, do not rephrase.

COPY OWNERSHIP: Codie (via /snapai-copywriting) owns homeowner-facing copy. Agents do STRUCTURAL
validation only. Approved strings are in SnapAI_Legal_Safe_Wordings_v1_2026-07-06.md.

MARKET RULE: PK is permanently test-market only; this deployment is US-market. Do not touch PK
serial decoders (return (None, pk_no_format)).

GEO-NEUTRAL PUBLIC COPY (Shoab rule 2026-07-06): NEVER put "Houston" or any city/region name in
ANY public-facing copy. Houston is BACKEND targeting only. Use geo-neutral ("independent HVAC
shops"). EXCEPTION: 1:1 cold email personalization may reference locale (Shoab confirmed).

SURFACE TAXONOMY (core legal rule): the dividing line is AUTHENTICATED vs PUBLIC.
 - Authenticated contractor app (login + signed ToS + VERIFIED contractor): "diagnose" OK (ToS
   Sec 2A-2C protects it). KEEP as-is. Do NOT rename contractor-facing UI.
 - Public surfaces (the single /tech landing page, videos): NO clause protection. The TECH/
   CONTRACTOR is ALWAYS the grammatical SUBJECT of "diagnose". SnapAI NEVER "diagnoses" publicly.
 - Homeowner outputs (report, PDF, share link, emails): consumer rules. No "diagnosis", no medical
   grading, no predictive/superlative claims, all conclusions attributed to the licensed contractor.

TWO HARD GATES (do not cross without explicit Shoab approval):
 GATE 1 -- "no upsell"/"honest" as a SnapAI claim is PARKED until Will's algo-bias SUBSTANTIATION
   FILE proves it true. Ship only the demonstrated-customer-story form.
 GATE 2 -- Homeowner REPORT final wording + the /tos legal text require Alfred's individual
   sign-off before prod (report is signed and paid against; ToS is the legal foundation).

REALITY CHECK (Alfred + Taleb): "100% legally safe" does not exist; ~95% is the ceiling. Risk
moves on DEPLOYMENT, not drafts. Ship the two zero-cost items first (predictive-claim deletions +
LLM "diagnosis system" prompt rewrite).

CRITICAL DEPENDENCY: the contractor GATE (C3) is the PREREQUISITE that makes the whole
"keep diagnose behind the login" clause strategy real. Until a homeowner can no longer sign up
with a bare Gmail, the definitional clause protects no one. The gate ships in THIS deployment.

================================================================
SECTION 1 -- PHASE 0: MANDATORY BOOTSTRAP (do first, then STOP)
================================================================
Spawn bootstrap agents IN PARALLEL:

A1 "Brain-Reader": Read BRAIN_CANONICAL_PATH.md, then PROJECT_BRAIN.md, DECISIONS.md,
   MARKET_GUIDE.md, TECH_STACK.md, ACTIVE_TASKS.md. Summarize product state, relevant DECs,
   deploy conventions. Explicitly CONFIRM back to Shoab that you have read and understood them.

A2 "TechStack+Workflow-Reader": Read TECH_STACK.md, WORKFLOW.md, DECISIONS.md (DEC-070/004/005/
   027/028/111), STATUS.md, README.md, SETUP_WINDOWS.md, SOW-1.3_Clerk_Production_Keys.md
   (relevant to the gate/Clerk). Produce the EXACT staging + prod-promotion pipeline steps
   verbatim, AND how Clerk auth + middleware.ts currently gate the app.

A3 "Git-State" (DEC-111): in /tmp/snapai_tmp, git fetch; report origin/main + origin/staging last
   5 commits, divergence, and which branch maps to staging vs prod.

A4 "Legal-Context/Change-Map": Read in ScopeSnapAI/:
   - SnapAI_Legal_Safe_Wordings_v1_2026-07-06.md (approved change set -- authoritative)
   - SnapAI_Legal_UI_Audit_v2_DEEP_2026-07-05.md (findings C1-C12, H1-H11 + file paths)
   - SnapAI_Legal_Framework_ToS_and_Disclaimers_v1_DRAFT.md (full ToS 16 sections, Sec 2A-2C,
     Layer 1/3/4/5 disclaimer text)
   Produce the authoritative CHANGE MAP cross-checked against Section 3. Flag any conflict.

A5 "Live-Recon" (Chrome): Walk CURRENT staging AND prod. For every surface in the change map,
   capture current live string + screenshot. Confirm the audit is still accurate; report anything
   already changed/removed. Also confirm current behavior of `/`, `/homeowner`, `/tech`, `/tos`.

PHASE 0 OUTPUT -> STOP GATE 0: Post to Shoab: (a) brain+techstack+pipeline+Clerk summary proving
knowledge, (b) verified git state, (c) reconciled change map, (d) the SCOPE confirmation
(Section 2). DO NOT proceed until Shoab approves.

================================================================
SECTION 2 -- SCOPE
================================================================
IN SCOPE:
  1. LLM prompt rewrites (cascade_prompts.py + homeowner_narrative.py)
  2. Homeowner report page (ReportClient.tsx): title, condition strings, tier label, remove 5-yr
     projection display (H10), fix common_cause_climate attribution (H9)
  3. overall_condition enum (H7) + urgency enum (H8): values + all readers
  4. Share link /d/[token]: header + error strings
  5. PDF template (contractor_estimate.html): footer + disclaimer block (Layer 5)
  6. Homeowner emails (services/email.py): neutral subjects, remove predictive/urgency. EMAIL SENDER (Shoab decided 2026-07-06):
     keep SnapAI as the technical sender BUT make the CONTRACTOR the visible principal --
     From display name = {company}, Reply-To = {company}, body attributes everything to
     {company} ('Your contractor {company} has prepared your report'). Transactional-only.
     Add decision-support disclaimer. CAN-SPAM compliant (accurate headers, working
     unsubscribe, postal address). NEVER 'Welcome to SnapAI' to a homeowner
  7. Public marketing copy on the single /tech landing page: hero H1 + subhead + CTA; remove
     "honest" superlatives; "diagnostic engine"->"assessment engine"; "App walks the diagnostic"
     -> "App walks the tech through the fault"; geo-neutral sweep
  8. SINGLE-LANDING-PAGE CONSOLIDATION: 301 redirect `/` (root homepage) -> `/tech`; 301 redirect
     `/homeowner` -> `/tech` and remove the /homeowner page. /tech is the ONLY public landing page.
  9. Predictive-claim deletions everywhere (zero-cost ship-first items)
 10. CONTRACTOR GATE (C3): onboarding requires (a) attestation checkbox "I'm a licensed HVAC
     contractor, or an authorized employee of one, using SnapAI in my business"; (b) license #
     as a REQUIRED field (currently OPTIONAL -- change); (c) Sec 2A-2C acknowledgment checkbox
     "I understand SnapAI is a decision-support tool for my professional use. It doesn't diagnose
     equipment -- I do, as the licensed pro." Enforce in middleware.ts / Clerk metadata: block app
     access until attestation + license present. (TDLR license VERIFICATION against the state DB is
     a background follow-up, not a launch blocker -- capture + store now.)
 11. TERMS OF SERVICE: deploy the v1 ToS (from the framework DRAFT, incl. Sec 2A-2C definitional
     clause + Sec 7 indemnification) at /tos. Add a visible ToS footer link on EVERY page (fixes
     H5). Wire the onboarding acknowledgment (item 10c) to link to /tos.
 12. LAYER 1 landing disclaimer: prominent decision-support disclaimer on the /tech page (above or
     near the fold) per framework Layer 1.
 13. LAYER 4 in-app OUTPUT disclaimer: inline, always-visible disclaimer text on the fault-
     resolution surface (FaultResolutionScreen.tsx) -- appears in /assess, /diagnoses/[id],
     /d/[token]. NOT behind a "learn more" link (Bryan's rule).
 14. CONFIDENCE BANDS (C12): "High/Medium/Low Confidence" -- either (default) publish a
     /methodology page defining each band numerically, OR remove them. SHOAB DECIDED 2026-07-06: PUBLISH the /methodology page defining each
     band numerically. Do NOT remove the bands.
 15. PRE-COMMIT HOOK: add a pre-commit config that BLOCKS any new "diagnos*" string or banned
     superlative (DEC-088 list) or city name in homeowner-facing paths: app/homeowner/ (post-
     removal, guard anyway), app/d/, app/r/, templates/, and the homeowner-touching sections of
     services/email.py, plus the /tech public page. Prevents future drift.

OUT OF SCOPE unless Shoab adds it:
  Y. "no upsell"/"honest" claim changes -- PARKED behind Gate 1 (substantiation file).
  Z. DB table / API endpoint / event-name renames (deferred under definitional clause).
  W. Privacy Policy multi-state rewrite (H4) -- follow-up.
  V. E&O insurance placement -- follow-up (not code).
  U. Card #21 / combustion-safety -- permanently excluded.
  T. Contractor-facing "diagnose" UI (sidebar, buttons, DB/API) -- KEEP, do not rename.

================================================================
SECTION 3 -- THE CHANGE MAP (verify all paths via git show origin/staging:<path>)
================================================================
Full replacement text lives in SnapAI_Legal_Safe_Wordings_v1_2026-07-06.md. Summary:

BACKEND (scopesnap-api):
  prompts/cascade_prompts.py -- both TRACK_A_CONFLICT_PROMPT + TRACK_B_UNCERTAIN_PROMPT:
    role -> "decision-support assistant for licensed HVAC technicians..."; add "Never present
    findings as certified diagnoses..."; field renames confirmed_fault->suggested_finding_for_
    review, sensor_diagnosis_correct->sensor_reading_appears_consistent, visual_findings_correct->
    visual_scan_supports_finding; bump PROMPT_VERSION + PROMPT_CHANGELOG; update ALL field readers
    (grep backend + frontend, no half-renames).
  prompts/homeowner_narrative.py -- rewrite: decision-support framing; REMOVE "doctor visit
    summary", "honest", the 15-20% efficiency example, any specific efficiency/cost/life claim;
    attribute to "your contractor"; bump version + changelog.
  templates/contractor_estimate.html -- footer -> "Prepared by {{company_name}}, License #
    {{company_license}}, using SnapAI field tools."; add Layer 5 disclaimer block above signature
    (decision-support, requires verification, CO/HX/combustion out-of-scope, not a certification).
  services/email.py -- remove "5-year savings", "HVAC issues get worse", "could save you money",
    "last follow-up", "60 seconds away"; subjects -> "Your service report from {company} is ready.";
    keep SnapAI as technical sender; From display name + Reply-To = {company}; body attributes
    to {company}; transactional-only; decision-support disclaimer; CAN-SPAM compliant; kill
    'Welcome to SnapAI' homeowner subject.
  overall_condition enum + urgency enum -- values -> operating normally/showing wear/needs service/
    end-of-life; urgency neutral contractor-attributed; update ALL readers.
  api/... confidence bands source (if backend-driven) -- align with C12 decision (item 14).

FRONTEND (scopesnap-web):
  app/tech/page.tsx -- THE single public landing page. Add hero H1 "Your newest tech diagnoses
    like your most experienced." + subhead (wordings doc) + CTA "Start free -- built for
    independent HVAC shops"; keep "The diagnostic layer your ServiceTitan stack doesn't have";
    "App walks the diagnostic" -> "App walks the tech through the fault"; add Layer 1 disclaimer;
    geo-neutral.
  app/page.tsx (root `/`) -- REPLACE content with 301 redirect to /tech (consolidation).
  app/homeowner/page.tsx -- REMOVE; 301 redirect /homeowner -> /tech.
    (Implement redirects per repo convention: next.config redirects or middleware.ts.)
  app/layout.tsx -- meta description: remove "honest recommendation"; ensure ToS footer link
    renders on every page (H5).
  app/(app)/dashboard/page.tsx -- remove "honest recommendation" superlative.
  app/r/[slug]/[reportId]/ReportClient.tsx -- title "Equipment Health Report" -> "Contractor
    Assessment Report"; condition strings attributed to contractor, remove "prevent..." (DEC-088);
    tier "* RECOMMENDED" -> "{company}'s recommendation"; "AI-Enhanced Assessment Photo" ->
    "Assessment Photo"; remove/638 gate the 5-year projection display (H10); fix common_cause_
    climate attribution (H9).
  app/d/[share_token]/page.tsx -- header "Diagnostic Report" -> "Contractor Assessment Report";
    errors "diagnosis link" -> "assessment link".
  components/FaultResolutionScreen.tsx -- add Layer 4 inline output disclaimer (always visible);
    confidence bands per item 14.
  ONBOARDING (gate C3) -- onboarding page/component + middleware.ts + Clerk metadata: add
    attestation checkbox, REQUIRED license # field, Sec 2A-2C acknowledgment checkbox linking to
    /tos; block app access until present.
  /tos route -- new page rendering the v1 ToS (from the framework DRAFT). Footer link every page.
  /methodology route -- PUBLISH (Shoab decided): define High/Medium/Low confidence bands
    numerically (what each means, false-positive expectation).
  DO NOT CHANGE (keep "diagnose"): SidebarNav.tsx ("Diagnoses"), FaultResolutionScreen "Cancel
    diagnosis" button text, components/diagnostic/*, DB/API/event names.

REPO ROOT:
  Pre-commit hook (item 15): .pre-commit-config.yaml (or repo convention) blocking banned strings
    in the homeowner-facing + public paths listed in Section 2 item 15.

STRUCTURAL VALIDATION (run on full diff before staging deploy):
  - banned words (DEC-088) in homeowner-facing files -> zero.
  - "Houston"/city names in public files -> zero.
  - "honest"/"no upsell" as SnapAI self-claim anywhere shipped -> zero (Gate 1).
  - every public "diagnose" has tech/contractor as subject.
  - contractor-facing "diagnose" UI untouched.
  - `/`, `/homeowner` both 301 to `/tech`; `/tech` is the only landing page.
  - onboarding blocks access without attestation + license; /tos reachable; ToS footer link on
    every page.

================================================================
SECTION 4 -- WORKFLOW PHASES + STOP GATES
================================================================
PHASE 0  Bootstrap + recon (Section 1). -> STOP GATE 0: Shoab approves scope.
PHASE 1  Implement in STAGING. Branch off origin/staging in /tmp/snapai_tmp. Spawn implementation
         agents in parallel by domain (Section 5). Each: read REAL file via git show, change,
         self-verify (wc -l + tail), commit. Run STRUCTURAL VALIDATION. Run Alfred-review agent on
         the homeowner-report diff AND the /tos text (GATE 2). Open PR + deploy to staging per
         DEC-070/WORKFLOW.md.
PHASE 2  Run /snapai-qa on STAGING. Full cycle: 7 UI flows, Playwright regression, static+dep
         checks, backend health, live Chrome verification of every changed string + the gate +
         the two redirects + /tos. Screenshot each surface. Fix + re-QA until clean.
         -> STOP GATE 1: post staging QA report + screenshots; WAIT for Shoab's "push to prod".
PHASE 3  (Shoab confirmation.) Proceed only after "yes".
PHASE 4  Promote STAGING -> PROD per DEC-070 documented steps.
PHASE 5  Run /snapai-qa on PROD. Same full cycle + live verification of every changed surface,
         the gate, both redirects, /tos, footer link. Fix-forward only via a staging round first.
PHASE 6  Update docs (Section 7).
PHASE 7  Final sign-off + retrospective (Section 8). -> STOP GATE 2: completion report.

================================================================
SECTION 5 -- AGENT ROSTER (target 12-18 agents)
================================================================
Phase 0 (parallel): A1 Brain-Reader, A2 TechStack+Workflow/Clerk, A3 Git-State, A4 Legal-Context/
  Change-Map, A5 Live-Recon (Chrome).
Phase 1 implementation (parallel by domain):
  I1 LLM-Prompts (cascade + homeowner_narrative + field-reader sweep)
  I2 Homeowner-Report (ReportClient.tsx + H9/H10)
  I3 Share-Link (/d/[token])
  I4 PDF-Template (contractor_estimate.html)
  I5 Email (services/email.py)
  I6 Public-Landing (app/tech consolidation target + Layer 1 + geo sweep) + Consolidation-Redirects
     (app/page.tsx root -> /tech; /homeowner -> /tech; remove /homeowner)
  I7 Enum/Backend (overall_condition + urgency + readers)
  I8 Gate/Onboarding (attestation + required license + acknowledgment + middleware/Clerk enforcement)
  I9 ToS-Deploy (/tos page + footer link every page + acknowledgment wiring)
  I10 In-App-Disclaimer + Confidence-Bands (FaultResolutionScreen Layer 4 + C12 decision)
  I11 Pre-commit-Hook
Phase 1 validation:
  V1 Copy-Guardrail (Codie hat: banned words / geo / Gate 1 / taxonomy / tech-as-subject)
  V2 Alfred-Legal-Review (full diff; MANDATORY sign-off on homeowner-report diff + /tos text = Gate 2)
Phase 6: D1 Brain-Updater, D2 TechStack-Updater.
Phase 7: R1 Retrospective/Verification (independent subagent verifies final PROD state:
  strings, gate, redirects, /tos, footer, screenshots).
Never skip V2 or R1. Merge same-domain agents only if capacity requires.

================================================================
SECTION 6 -- /snapai-qa USAGE (both rounds)
================================================================
Invoke /snapai-qa explicitly: "run /snapai-qa on staging" (Phase 2), "run /snapai-qa on prod"
(Phase 5). Do not stop until every step it defines is confirmed. Attach screenshots + pass/fail
table to each STOP-GATE report. Any bug -> fix via a staging round first (DEC-070), never hot-patch
prod. Explicitly QA: the onboarding gate (try to sign up without license -> must be blocked), both
redirects, /tos render + footer link, and every changed homeowner/public string.

================================================================
SECTION 7 -- DOC UPDATES (Phase 6; bash heredoc / Desktop Commander, NOT Edit tool)
================================================================
In ScopeSnapAI/ (canonical):
  DECISIONS.md -> new DEC entries (assign next free numbers): legal-safe wordings v1 deployed;
    authenticated-vs-public surface taxonomy; geo-neutral public-copy rule; single public landing
    page (/ and /homeowner -> /tech); contractor GATE (C3) live; ToS deployed at /tos + Sec 2A-2C
    definitional clause; Layer 1/4/5 disclaimers live; pre-commit hook; confidence-band decision;
    "no upsell" parked behind substantiation file; homeowner report + ToS require Alfred sign-off.
  ACTIVE_TASKS.md -> mark deployment done; add follow-ups: TDLR license verification job,
    substantiation file (Will), Privacy Policy H4, E&O insurance, DB/API rename (deferred).
  PROJECT_BRAIN.md -> product identity = "decision-support for licensed HVAC contractors";
    note taxonomy + single landing page + gate.
  TECH_STACK.md -> record LLM prompt version bumps, enum value changes, /homeowner + root redirects,
    /tos + /methodology routes, gate/middleware/Clerk change, PDF disclaimer, email routing,
    pre-commit hook.
  MARKET_GUIDE.md -> geo-neutral public-copy rule (Houston backend-only).
  STATUS.md / BUILD_LOG.md -> deploy record (staging SHA -> prod SHA, dates, QA results).
Marketing brain: if the public H1/CTA/tagline changed, log per MBrain update protocol (log in
  marketing/SnapAI_Final_Marketing_Plan_Master_Tracker_v3.md). Do NOT edit MBrain silently. Do NOT
  change the locked tagline without Shoab's explicit approval.

================================================================
SECTION 8 -- DEFINITION OF DONE (Phase 7 checklist)
================================================================
[ ] Phase 0 report delivered; Shoab approved scope.
[ ] All in-scope changes implemented in staging; structural validation clean.
[ ] Contractor gate live: signup blocked without attestation + license #.
[ ] /tos live; ToS footer link on every page; onboarding acknowledgment links to it.
[ ] `/` and `/homeowner` both 301 -> `/tech`; /tech is the only public landing page.
[ ] Layer 1 (landing), Layer 4 (in-app), Layer 5 (report/PDF) disclaimers present.
[ ] /methodology page PUBLISHED defining High/Medium/Low confidence bands numerically.
[ ] Pre-commit hook active and blocks a test banned string.
[ ] Alfred-review agent signed off homeowner-report diff + /tos text (Gate 2).
[ ] /snapai-qa STAGING clean; screenshots attached; Shoab confirmed "push to prod".
[ ] Promoted to prod per DEC-070; /snapai-qa PROD clean; prod screenshots attached.
[ ] Brain + tech-stack docs updated (Section 7) and committed.
[ ] Retrospective posted: shipped items, staging SHA -> prod SHA, open follow-ups, residual-risk
    note (~95% ceiling, not 100%).
[ ] Two zero-cost items (predictive-claim deletions + LLM prompt rewrite) confirmed LIVE in prod.

================================================================
SECTION 9 -- STOP GATES (never skip)
================================================================
GATE 0: after bootstrap -> Shoab approves scope before any edit.
GATE 1: "no upsell"/"honest" claim does NOT ship until substantiation file exists.
GATE 2: homeowner report copy + /tos text need Alfred sign-off before prod.
GATE 3: staging QA passed -> Shoab confirms before prod promotion.
Any ambiguity, missing file, moved code, or doc conflict -> STOP and ask Shoab.

================================================================
SECTION 10 -- FINAL REMINDERS
================================================================
- Boards persist: Bryan Orr + Mark Delgado (snapai-board) and Alfred (snapai-nav) active by
  default; consult Alfred on any legal-wording judgment call mid-execution.
- Do not touch PK, Card #21, contractor-facing "diagnose" UI, or the locked tagline.
- The gate (C3) is the foundation the clause strategy stands on -- it MUST ship for the copy
  changes to have legal meaning.
- Risk moves on DEPLOYMENT, not drafts. Ship the zero-cost deletions first.
- Report in plain language at every STOP gate; attach diffs + screenshots + QA tables.
