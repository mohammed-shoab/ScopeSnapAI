# SnapAI Legal-Safe Wordings v1 (sell AND survive)

Date: 2026-07-06
Authors: Codie (lead copy) + marketing bench (Marcus, Rory, Jake, Diana, Alex Su, Zaria, Jenny) + Jeanne (frame)
Legal sign-off: Alfred (US/TX). Verified angle: Bryan Orr + Mark Delgado.
Status: LOCKED v1 drafts. Two hard gates before any claim ships (see bottom).

CORE RULE (from the surface taxonomy):
- Public surfaces (homepage, /tech, videos): NO definitional-clause protection. The TECH/CONTRACTOR
  is always the grammatical subject of "diagnose." SnapAI never "diagnoses" a unit on a public surface.
- Authenticated contractor app (login + signed ToS + verified contractor): "diagnose" is fine (clause protected).
- Homeowner outputs (report, PDF, share link, email): consumer rules. No "diagnosis," no medical grading,
  no predictive/superlative claims. All conclusions attributed to the licensed contractor.
- GEO-NEUTRAL (user rule 2026-07-06): NEVER name "Houston" (or any city/region) in ANY public-facing
  copy. Houston is a BACKEND targeting fact only. A public TikTok/homepage/video reaches every US
  tech; naming a city waves off non-Houston techs who could come onsite. Use "independent HVAC shops".

------------------------------------------------------------
1. PUBLIC -- HOMEPAGE
------------------------------------------------------------
H1:       Your newest tech diagnoses like your most experienced.
Subhead:  SnapAI is the senior guy in every tech's pocket -- snap the nameplate, walk the fault,
          lay out three options and one recommendation, closed on the driveway even when your
          best tech is on another call.
CTA:      Start free -- built for independent HVAC shops
NOTE:     "tech" is the actor of "diagnoses" -- never let SnapAI be the subject of that verb here.

------------------------------------------------------------
2. PUBLIC -- /tech PAGE
------------------------------------------------------------
Hero:     The diagnostic layer your ServiceTitan stack doesn't have.
Support:  ServiceTitan, Housecall Pro, FieldEdge, Jobber move a job from call to invoice.
          None of them help the tech figure out what's wrong with the unit. SnapAI fills that gap.
REWRITE:  "App walks the diagnostic" -> "App walks the tech through the fault"
          (avoid framing the APP as the diagnostician)

------------------------------------------------------------
3. PUBLIC -- VIDEO (TikTok / Reels / Shorts)
------------------------------------------------------------
Rule:     Pain-first hook. Tech visibly does the diagnosis on screen. SnapAI assists. Never a
          caption/voiceover saying "SnapAI diagnoses."
Hook ex:  "$9,000 quote. It was a $14 part."
Body ex:  Tech Tom snaps the nameplate, the app walks him to the fault, he finds it.
Voice:    Dry, seen-it-all (Zaria). "Yeah. Fourteen bucks. Weird how that works."
CTA:      Try free -> snapai.mainnov.tech

------------------------------------------------------------
4. AUTHENTICATED GATE (prerequisite -- finding C3)
------------------------------------------------------------
Attestation (REQUIRED checkbox):
  [ ] I'm a licensed HVAC contractor, or an authorized employee of one, using SnapAI in my business.
License #:  REQUIRED field (currently OPTIONAL -- change this).
Acknowledgment (REQUIRED checkbox):
  [ ] I understand SnapAI is a decision-support tool for my professional use. It doesn't diagnose
      equipment -- I do, as the licensed pro. (links to ToS Sec 2A-2C)
Enforcement: block app access in middleware.ts until attestation + license present.

------------------------------------------------------------
5. HOMEOWNER OUTPUT -- REPORT PAGE (/r/...)
------------------------------------------------------------
Title:        Contractor Assessment Report   (flat label; emotion carried by first content line)
First line:   The fix was a $14 part -- not the $9,000 system. Here's what [Company] found today. (example)
Condition:    "Your Carrier AC is 9 years old. Here's what [Company] checked today and what they recommend."
Condition enum (H7):  operating normally / showing wear / needs service / end-of-life
              (retire excellent/good/fair/poor/critical -- medical grading)
Urgency enum (H8):    neutral, contractor-attributed (retire none/monitor/soon/immediate medical urgency)
Tier label:   [Company]'s recommendation      (retire "* RECOMMENDED" and algorithmic authority)
Banned:       "Equipment Health Report", "prevent system failure", "prevent further issues",
              specific efficiency %, 5-year savings projections.

------------------------------------------------------------
6. HOMEOWNER OUTPUT -- SHARE LINK (/d/[token])
------------------------------------------------------------
Header:   Contractor Assessment Report   (retire "Diagnostic Report")
Errors:   "This assessment link is not valid or has expired." (retire "diagnosis link")

------------------------------------------------------------
7. HOMEOWNER OUTPUT -- PDF (contractor_estimate.html)
------------------------------------------------------------
Footer:   Prepared by [Company], License #[...], using SnapAI field tools.
          (retire "prepared using SnapAI HVAC Intelligence")
Disclaimer block (add above signature):
  About this estimate: This estimate reflects the professional judgment of [Company]
  (License #[...]), a licensed HVAC contractor. SnapAI is a decision-support tool used by
  [Company]; it does not perform diagnoses. Findings require independent verification by your
  licensed contractor. SnapAI does not perform combustion, heat exchanger, or carbon monoxide
  safety diagnostics -- request a full safety inspection separately. This estimate is not a
  certification of equipment condition or performance.

------------------------------------------------------------
8. HOMEOWNER OUTPUT -- EMAILS (services/email.py)
------------------------------------------------------------
From:     keep SnapAI as technical sender; make CONTRACTOR the visible principal --
          From display name + Reply-To = [Company]; body opens 'Your contractor [Company]
          has prepared your report'; transactional-only; CAN-SPAM compliant; kill
          'Welcome to SnapAI' homeowner subject (Alfred-approved config, Shoab 2026-07-06)
Subject:  Your service report from [Company] is ready.
Body:     neutral status only. Remove: "5-year savings", "HVAC issues get worse",
          "could save you money", "last follow-up", "60 seconds away".
Footer:   decision-support disclaimer ("SnapAI is a decision-support tool used by
          [Company]; it does not diagnose equipment") + CAN-SPAM: accurate headers,
          working unsubscribe link, physical postal address.

------------------------------------------------------------
9. LLM PROMPTS
------------------------------------------------------------
cascade_prompts.py: "You are a decision-support assistant for licensed HVAC technicians. Provide
  preliminary findings for the technician's independent verification. Never state a definitive
  diagnosis. Always frame outputs as recommendations subject to professional review."
  Fields: confirmed_fault -> suggested_finding_for_review; sensor_diagnosis_correct ->
  sensor_reading_appears_consistent; visual_findings_correct -> visual_scan_supports_finding.
homeowner_narrative.py: decision-support framing; NO "doctor visit summary"; NO "honest";
  NO specific efficiency/cost/life claims; attribute all recommendations to "your contractor".

------------------------------------------------------------
10. AUTHENTICATED CONTRACTOR APP (Bucket 1 -- KEEP as-is)
------------------------------------------------------------
Sidebar "Diagnoses", "Cancel diagnosis", in-app flow, DB/API/event names: KEEP "diagnose".
Protected by ToS Sec 2A-2C once the gate (section 4) is live. Do NOT rename for "consistency"
(destroys trade authenticity for no legal gain -- Jake's standing dissent).

------------------------------------------------------------
TWO HARD GATES BEFORE ANY CLAIM SHIPS
------------------------------------------------------------
GATE 1: "no upsell" / "honest" as a SnapAI claim is PARKED until Will's algo-bias substantiation
        file proves it true. Until then, sell it as demonstrated customer story only.
GATE 2: Alfred signs off the homeowner REPORT wording individually (it's signed and paid against).

============================================================
ADDENDUM (2026-07-06) -- consolidation + gate + ToS + disclaimers
============================================================

SINGLE PUBLIC LANDING PAGE (Shoab 2026-07-06):
- /tech is the ONLY public landing page. It carries the hero H1 + subhead + CTA above.
- Root `/` (the homepage without "tech" in the path) -> 301 redirect to /tech.
- /homeowner -> 301 redirect to /tech (page removed/blocked).
- Result: one page. No separate homeowner or generic homepage.

CONTRACTOR GATE (C3) -- onboarding copy:
- Attestation (REQUIRED): "I'm a licensed HVAC contractor, or an authorized employee of one,
  using SnapAI in my business."
- License #: REQUIRED field (currently optional).
- Acknowledgment (REQUIRED): "I understand SnapAI is a decision-support tool for my professional
  use. It doesn't diagnose equipment -- I do, as the licensed pro." (links to /tos Sec 2A-2C)
- Enforce in middleware/Clerk: no app access until attestation + license present.

TERMS OF SERVICE (/tos):
- Deploy v1 ToS (framework DRAFT) incl. Sec 2A-2C definitional clause + Sec 7 indemnification.
- Visible ToS footer link on EVERY page.

LAYER 1 -- /tech landing disclaimer (near the fold):
  "SnapAI is a decision-support tool for licensed HVAC contractors. It supports the contractor's
   professional judgment; it does not diagnose equipment or replace a licensed technician."

LAYER 4 -- in-app output disclaimer (FaultResolutionScreen, inline, ALWAYS visible, not behind a
  link): "Preliminary decision-support output. Verify independently. You, the licensed technician,
  make the final call."

CONFIDENCE BANDS (C12): PUBLISH /methodology defining High/Medium/Low numerically (SHOAB
  DECIDED 2026-07-06 -- do not remove the bands).

PRE-COMMIT HOOK: block new "diagnos*" / DEC-088 banned words / city names in app/homeowner/,
  app/d/, app/r/, templates/, homeowner sections of services/email.py, and the /tech public page.

TWO HARD GATES (unchanged): (1) "no upsell"/"honest" parked until substantiation file; (2) Alfred
  signs off the homeowner report copy AND the /tos text before prod.
