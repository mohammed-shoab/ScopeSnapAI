# SnapAI Legal-Safe Wordings -- Implementation Status (2026-07-06)

Executed by the deployment dispatch, in a sandbox clone of origin/staging.
Branch: fix/legal-safe-wordings-v1 (base 236942d).
IMPORTANT: the sandbox clone is EPHEMERAL and was NOT pushed. The applied changes are
preserved as SnapAI_LegalWordings_APPLIED_2026-07-06.patch (apply with `git apply` on the
real repo, or re-create the branch and push from the machine with deploy credentials).

NOTHING WAS DEPLOYED. No push, no staging deploy, no prod. /snapai-qa NOT run (no live deploy
+ no deploy CLIs in this sandbox). This is a reviewed, committed branch awaiting real deploy.

=====================================================================
APPLIED + COMMITTED (2 commits, in the .patch)
=====================================================================
1. scopesnap-api/prompts/cascade_prompts.py -- both TRACK_A + TRACK_B role line
   "expert HVAC fault diagnosis system" -> "decision-support assistant for licensed HVAC
   technicians ... never a certified diagnosis ... requires the licensed technician's
   verification and final determination." (highest-leverage fix)
2. scopesnap-api/prompts/homeowner_narrative.py -- full prompt rewrite: removed "honest",
   "doctor visit summary", the 15-20% efficiency example; attributes to contractor;
   NARRATIVE_PROMPT_VERSION 1.0.0 -> 1.1.0
3. scopesnap-api/services/email.py -- removed homeowner predictive/urgency ("5-year savings",
   "HVAC issues get worse", "could save you money", "last follow-up"). CONTRACTOR welcome email
   left intact (it is B2B, not homeowner).
4. scopesnap-web/app/r/[slug]/[reportId]/ReportClient.tsx -- "Equipment Health Report" ->
   "Contractor Assessment Report"; condition summaries contractor-attributed + non-predictive;
   "AI-Enhanced Assessment Photo" -> "Assessment Photo". (CRLF preserved.)
5. scopesnap-web/app/d/[share_token]/page.tsx -- "Diagnostic Report" -> "Contractor Assessment
   Report"; error strings "diagnosis" -> "assessment".
6. scopesnap-web/lib/urdu-strings.ts -- matching key rename so Urdu lookup doesn't break.
7. NEW scopesnap-web/app/tos/page.tsx + app/methodology/page.tsx -- placeholder pages
   (ToS content TODO from framework DRAFT + Alfred sign-off; methodology confidence-band
   numbers TODO from Will/Alfred).

=====================================================================
DEFERRED -- exact patches ready, need a decision, a migration, or tests
=====================================================================

D1. PUBLIC LANDING COPY (app/tech/page.tsx) -- DEFERRED to Codie review (public marketing copy
    is Codie's per copy-ownership rule; page also just changed via DEC-129). MANDATORY legal
    removals confirmed present on the page (apply regardless of final wording):
    - L94  "Houston Contractors Only" -> "Built for independent HVAC shops"
    - L98  H1 "Diagnose, estimate, and close before you leave the driveway." (SnapAI as subject)
           -> "Your newest tech diagnoses like your most experienced." (tech = subject)
    - L101-105 subhead: drop "Houston", drop "one honest recommendation", reframe "AI HVAC
           diagnostic tool" -> "decision-support app ... walks your tech through the fault"
    - L52  "App walks the diagnostic" -> "App walks the tech through the fault"
    - L149-152 "diagnostic engine" -> "assessment engine"; remove "Houston" mentions
    - L115 "First 10 Houston testers..." / L155 "first 10 Houston HVAC techs" / L168 "Houston
           techs" / L171-173 "Houston field experience ... Houston labor rates" -> geo-neutral
    - Add Layer-1 decision-support disclaimer below the hero CTA (snippet in agent notes).
    NOTE: grep app/tech/page.tsx for "Houston" after edits -> must be zero.

D2. SINGLE-LANDING CONSOLIDATION (next.config.js redirects()) -- DECISION NEEDED.
    Add: {source:"/",destination:"/tech",permanent:true} and
         {source:"/homeowner",destination:"/tech",permanent:true}
    (repo convention = permanent:true = 308; use permanent:false + statusCode:301 if strict 301
    required.) CONSEQUENCE: the root `/` page currently hosts the ONLY waitlist email-capture
    form -- redirecting `/` disables waitlist capture. DECISION: move the waitlist form to /tech
    first, or accept losing it. Then remove app/page.tsx + app/homeowner/page.tsx (dead routes).

D3. FOOTER "Terms" LINK -- add <Link href="/tos">Terms</Link> after the Privacy link in the
    footer of app/tech/page.tsx (and app/page.tsx + app/homeowner/page.tsx if they survive).
    No shared Footer component exists (3 inline footers).

D4. REPORT "RECOMMENDED" BADGE (ReportClient.tsx ~L806) + H7 CONDITION LABELS -- DEFERRED
    (needs small code edits, not pure literal swaps):
    - "* RECOMMENDED" badge -> attribute to contractor (company.name is in scope at L465).
      Also a SECOND badge in components/FiveYearComparison.tsx L80.
    - H7: add CONDITION_LABELS map next to CONDITION_COLORS (L146-162): excellent/good ->
      "Operating normally"; fair -> "Showing wear"; poor -> "Needs service"; critical/failed ->
      "End-of-life". Apply at HealthGauge L213 + heading L648. DISPLAY-ONLY (do NOT change stored
      values -- backend tier logic in pdf_generator._tier_label keys on the raw values).

D5. FIVE-YEAR PROJECTION (components/FiveYearComparison.tsx, rendered ReportClient L1237-1249) --
    DECISION NEEDED. Contains H10 5-year cost/risk projections, an efficiency/"electricity saved"
    savings claim (banned), a 2nd "* RECOMMENDED" badge, AND hardcoded "Houston" (L151, L200).
    RECOMMENDED FIX: gate the entire <FiveYearComparison> render out of the homeowner report
    (remove the block at L1237-1249, or gate behind present-mode only). Confirm before applying.

D6. CONTRACTOR GATE (C3) -- DEFERRED (needs DB migration + backend + tests). Plan (agent-verified):
    - Middleware is scopesnap-web/proxy.ts (Clerk); user metadata is in the BACKEND DB
      (scopesnap-api/db/models.py: Company / User), NOT Clerk metadata.
    - onboarding at app/(app)/onboarding/page.tsx: License # is OPTIONAL (validation L127-131 only
      checks company name); has a "Skip" button. CONFIRMED audit finding.
    - Build: (a) add attestation + Sec 2A-2C acknowledgment checkboxes; (b) make license # REQUIRED
      (extend validation, disable Launch until truthy); (c) REMOVE Skip button + handleSkip;
      (d) DB migration: add Company.attestation_accepted_at (timestamp) + terms_ack_version;
      (e) backend PATCH /api/auth/me/company: persist attestation, reject blank license (422),
      return fields in GET /me; (f) enforce in app/(app)/layout.tsx guard: if 200 but license
      empty or attestation null -> redirect("/onboarding") (already in skipPaths, no loop).
    - This is the PREREQUISITE that makes the definitional-clause strategy real. High priority.

D7. LLM FIELD RENAMES (cascade JSON) -- DEFERRED (needs a test; SILENT-FALLBACK trap).
    confirmed_fault is read at services/ai_cascade.py:142,183,299 via .get(key, default) -- a
    partial rename FAILS SILENTLY (wrong fault, no error). Rename all 5 sites atomically
    (cascade_prompts.py:71,96 + ai_cascade.py:142,183,299) AND add a test asserting the cascade
    returns the Gemini fault not the fallback. sensor_diagnosis_correct / visual_findings_correct
    are prompt-only labels (persisted in stored JSON, never read) -- rename for consistency only.
    LOWER PRIORITY: these are contractor-internal / subpoena-visible; deferrable under the
    definitional clause once the ToS + gate are live.

D8. PRE-COMMIT HOOK -- DEFERRED. Add .pre-commit-config.yaml blocking new "diagnos*" / DEC-088
    banned words / city names in app/homeowner (post-removal), app/d/, app/r/, templates/,
    homeowner sections of services/email.py, and app/tech/page.tsx.

=====================================================================
DEPLOY HANDOFF (this sandbox cannot deploy)
=====================================================================
- No deploy CLIs installed; push access unverified; prod is gated on Shoab's confirm.
- To deploy: on the machine with credentials, apply SnapAI_LegalWordings_APPLIED_2026-07-06.patch
  to a branch off origin/staging (or recreate the 2 commits), finish D1-D8, then run the dispatch
  workflow: PR -> staging -> /snapai-qa staging -> Shoab confirm -> promote to prod -> /snapai-qa
  prod -> update brain/tech-stack docs.
- HARD GATES still stand: Alfred sign-off on the /tos text + homeowner report before prod;
  "no upsell" stays parked until Will's substantiation file.

=====================================================================
DECISIONS NEEDED FROM SHOAB
=====================================================================
1. D2/D5: the root `/` redirect disables the only waitlist form -- move it to /tech or drop it?
   And OK to gate out the 5-year projection block (D5) from the homeowner report?
2. D6: authorize the contractor-gate build now (DB migration + onboarding rebuild)? It's the
   prerequisite for the clause strategy.
3. Where to run the actual deploy (your machine via Desktop Commander, or the fresh-chat handoff)?

=====================================================================
UPDATE (2026-07-06, later) -- Shoab approved "do as advised for all"
=====================================================================
NOW APPLIED + COMMITTED (branch fix/legal-safe-wordings-v1, 3 commits; see refreshed .patch):
- D1 DONE: /tech legal removals applied (Houston=0 verified, "honest" dropped, tech-as-subject H1,
  decision-support framing, Layer-1 disclaimer, Terms footer link). MARKED "COPY DRAFT -- pending
  Codie + Alfred sign-off" at top of app/tech/page.tsx. Final marketing wording still needs Codie.
- D2 DONE: next.config.js redirects "/" and "/homeowner" -> "/tech" (permanent). Dead app/page.tsx
  and app/homeowner/page.tsx DELETED. Waitlist email-capture form MOVED onto /tech (waitlist kept).
- D3 DONE: Terms footer link added to /tech.
- D4 DONE: RECOMMENDED badge -> "[company]'s recommendation"; H7 condition labels display-only
  (operating normally/showing wear/needs service/end-of-life). Stored values untouched.
- D5 DONE: <FiveYearComparison> removed from the homeowner report (H10 + savings claim + duplicate
  RECOMMENDED + hardcoded Houston all eliminated). Component file left in repo, no longer rendered.
- D6 DONE (code): contractor gate C3 -- Company.attestation_accepted_at + terms_ack_version,
  migration 045, PATCH requires license (422) + persists attestation, onboarding required license +
  2 checkboxes + Skip removed, (app)/layout guard redirects incomplete profiles to /onboarding.
  py_compile passes. NOT migrated/built/tested here.

STILL DEFERRED (true remaining follow-ups):
- D7 cascade JSON field rename (confirmed_fault etc.) -- needs a test (silent-fallback trap). Lower
  priority (contractor-internal, clause-covered).
- D8 pre-commit hook -- not yet added.
- Gate tests: 422 on blank license; attestation timestamp set; guard redirect for incomplete profile.
- ToS content paste into /tos + Alfred sign-off; methodology confidence-band NUMBERS (Will/Alfred).
- Codie + Alfred sign-off on the /tech COPY DRAFT before prod.
- alembic upgrade head + frontend build + /snapai-qa -- run in the deploy pipeline.

DECISIONS: all three resolved by Shoab ("do as advised for all"): waitlist moved (kept),
5-year block removed, gate authorized. No open decisions remain for the deploy chat except the
hard gates (Alfred sign-off on ToS + report copy; "no upsell" parked until substantiation file).
