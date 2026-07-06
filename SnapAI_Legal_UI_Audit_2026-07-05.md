# SnapAI Live App — Legal & UI Audit Report

**Date:** 2026-07-05
**Auditor:** Alfred (US HVAC legal counsel — snapai-nav)
**Verified by:** Bryan Orr + Mark Delgado (snapai-board)
**Live target:** https://snapai.mainnov.tech (prod)
**Method:** End-to-end Chrome navigation across 8 URLs while logged in as Shoab
**Scope:** Marketing/UI language, legal-doc coverage, DTPA compliance, decision-support positioning, license verification, disclosure architecture

---

## Overall risk rating: **CRITICAL — SHIP-BLOCKING FOR SCALE**

The app has **zero deployed Terms of Service**, no contractor acknowledgment click-through, no in-app output disclaimer, no license verification, and multiple pieces of marketing copy that directly contradict the decision-support positioning Alfred's legal framework requires. In its current live state, SnapAI carries **substantially higher legal exposure than any competitor** (ServiceTitan, Housecall Pro, FieldEdge) because structured-diagnostic-output plus unhedged marketing plus no legal terms creates traceable liability with no defense.

**Immediate implication for Tier A ship (v6 → v7 promotion):** DO NOT ship Tier A features until at least the four Critical findings below are resolved. Each Tier A card increases traceable liability under the current framework.

**Estimate to fix Critical findings:** 2-3 weeks of engineering + $3-8K legal counsel (Baker Botts / Winstead / Jackson Walker) + $5-25K/yr tech E&O insurance placement.

---

## Pages audited

| URL | Status | Key concern |
|---|---|---|
| `/` (homepage) | LIVE | Marketing overstates AI capability + no ToS link |
| `/homeowner` | LIVE | **DTPA violation — direct-to-consumer diagnostic claims** |
| `/tech` | LIVE | Language violates decision-support positioning |
| `/privacy` | LIVE | Basic PP; missing CCPA/GDPR/TCPA |
| `/tos` | **404** | Not deployed |
| `/terms` | **404** | Not deployed |
| `/legal` | **404** | Not deployed |
| `/disclaimer` | **404** | Not deployed |
| `/onboarding` | LIVE | No ToS acceptance, no license verification, no acknowledgment |
| `/dashboard` | LIVE | Marketing claims in operational UI |
| `/settings` | LIVE | Empty — no ToS mgmt, no license mgmt |
| `/assess` (Step Zero) | LIVE | No in-app output disclaimer |

---

## CRITICAL findings — fix before ANY new user acquisition

### C1. Zero Terms of Service deployed

**Verified:** `/tos`, `/terms`, `/legal`, `/disclaimer` all return 404.

**Legal exposure:** No liability cap. No indemnification. No class-action waiver. No arbitration clause. No warranty disclaimer. No limitation of liability. Every contractor and every homeowner interacting with SnapAI has NO contractual limitation on damages. A single successful lawsuit becomes an existential event for the company.

**Fix:** Publish the v1 ToS from `SnapAI_Legal_Framework_ToS_and_Disclaimers_v1_DRAFT.md` (after Texas counsel review) at `/tos` and link from every page footer + onboarding.

**Priority:** IMMEDIATE. Every new signup between now and ToS deployment is an uncapped liability event.

### C2. Homeowner page (`/homeowner`) violates DTPA §17.42 — direct-to-consumer diagnostic marketing

**Verbatim from live page:**
- "A diagnostic report explaining what is wrong"
- "The app identifies the problem — no guessing, no vague answers"
- "You see what is wrong, what each fix costs"
- "Your contractor's SnapAI estimate marks one option as ★️ Recommended based on your unit's age and condition"
- "A 5-year outlook showing future repair risk"
- "Ask your contractor if they use SnapAI. If they do not, share this page with them."

**Legal exposure:** This page creates a direct consumer relationship with the homeowner. Under Texas DTPA §17.42, any consumer waiver of DTPA rights is void. The homeowner is being *sold to* — not merely informed — which makes them a "consumer" of SnapAI. If the app ever misdiagnoses a case where the homeowner acted on the report and suffered damages, the homeowner has a direct DTPA claim against SnapAI (treble damages + attorneys' fees). No ToS eliminates this.

**Alfred's Principle 2 violation:** "No direct-to-consumer relationship" — this page IS the direct-to-consumer relationship.

**Fix:** Rewrite `/homeowner` from "here's what SnapAI does for you" to "here's how your contractor uses professional decision-support tools." Every sentence must position SnapAI as *contractor's* tool, not homeowner's. Delete "share this page with your contractor" language — that's the recruitment pipeline that makes homeowners into SnapAI consumers.

**Suggested replacement hero:**
> **Ask your HVAC contractor about their diagnostic tools.**
> Modern HVAC contractors use professional diagnostic software to support their inspection work. If your contractor uses SnapAI, they may provide you with a written estimate reflecting their professional assessment. SnapAI is a tool used by licensed HVAC contractors — it does not diagnose HVAC problems. Only your licensed contractor can do that.

**Priority:** IMMEDIATE. Every homeowner viewing this page is a potential DTPA plaintiff.

### C3. No contractor onboarding acknowledgment / no license verification

**Verified:** `/onboarding` Step 2 of 2 asks for Company Name + Phone + License # (**marked optional**) + Logo. No ToS acceptance. No click-through affirming decision-support role. No license verification. "I'll finish this later" allows account creation without even filling the License # field.

**Legal exposure:**
- License # optional = unlicensed users can access the tool = EPA §608 refrigerant guidance goes to non-certified people (federal offense for the user, contributory issue for SnapAI)
- No ToS acceptance = contractors have never agreed to any limits on SnapAI's liability
- No decision-support acknowledgment = contractors can honestly claim they thought the tool was diagnostic

**Alfred's Layer 3 completely missing.**

**Fix:** Rebuild onboarding with mandatory:
1. ToS acceptance checkbox (linked to /tos)
2. Positive-affirmation click-through (6 checkboxes from Layer 3 in the v1 framework)
3. License # + State (required, verified against state licensing DB where possible)
4. Cannot advance to app without all four

**Priority:** IMMEDIATE. Every contractor signed up under current flow has no acknowledgment on file.

### C4. No in-app output disclaimer on assessment / diagnostic UI

**Verified:** `/assess` Step Zero shows nameplate scan + spec entry with no disclaimer language visible. Sidebar navigation says "Diagnoses" (banned verb per Principle 3).

**Legal exposure:** When a contractor uses the tool and sees an Output, there is no visible reminder that the Output is decision-support only. Plaintiff's counsel will argue in discovery that no reasonable contractor would have known the Output was advisory.

**Alfred's Layer 4 missing.**

**Fix:** Every fault card view, every estimate output, every homeowner report must display in-line (not in a footer, not behind a link):
> **SnapAI recommendation only — NOT a certified diagnosis.**
> Verify all findings independently before acting. Do not present this Output to a Homeowner as a certified diagnosis.

Enhanced version on any >$5K recommendation (system replacement, ductwork rework):
> **This is a preliminary finding requiring independent Manual J load calculation and licensed inspection before any equipment replacement or major service recommendation is presented to the Homeowner.**

Rename sidebar "Diagnoses" → "Assessments" or "Assist History."

**Priority:** IMMEDIATE — before ANY Tier A card ships.

---

## HIGH findings — resolve within 2-4 weeks

### H1. `/tech` page uses banned "diagnostic" language throughout

Verbatim from live page:
- "**AI HVAC diagnostic tool** built for Houston contractors"
- "**Diagnose**, estimate, and close before you leave the driveway"
- "**App walks the diagnostic**"
- "system follows the same fault tree your best senior tech has in his head"
- "Diagnostic logic validated against real residential split-system calls"

**Violates:** Alfred's Principle 3 (language consistency). If a plaintiff finds mismatch between marketing ("diagnostic tool") and ToS ("decision-support only"), courts often side with the marketing — leading to Risk 2 (willful misconduct / fraud).

**Fix:** Rewrite hero to:
> **Support your diagnosis with structured decision-support built for Houston contractors.**
> AI-assisted equipment identification. Guided fault-tree questions your team walks through. Three context-aware options priced with your markup. Homeowner-approved PDF. Every recommendation reviewed and finalized by your licensed technician.

Global search-replace across `/tech` page:
- "diagnostic tool" → "decision-support tool"
- "diagnose" → "assist with diagnosis"
- "the app diagnoses" → "your technician diagnoses with SnapAI's assistance"
- "system follows the fault tree" → "system presents the fault tree for your technician to work through"

### H2. Unsubstantiated superlatives across marketing

Every instance triggers DTPA §17.46 risk without a substantiation file:
- "one **honest** recommendation" (homepage, /homeowner, /tech, dashboard)
- "no guessing" (homepage, /homeowner)
- "no upsell pressure" (homepage, /homeowner)
- "**Accuracy Tracking**" (onboarding welcome card)
- "**90 seconds**" (homepage, /tech, dashboard)
- "before you leave the driveway" (multiple pages)
- "**Diagnostic logic validated**" (/tech)

**Fix:**
- Remove all superlatives that cannot be backed by a documented substantiation file
- OR create the substantiation files (Alfred's Principle 5) with 7-year retention
- "90 seconds" and "before you leave the driveway" — if these are unreliable in practice, remove or soften ("in minutes, not hours")
- "Accuracy Tracking" — either publish accuracy methodology + numbers, or rename to "Assessment Review"
- "honest recommendation" — remove; unsubstantiated superlative

### H3. Homeowner-directed forward-looking claims

`/homeowner` page includes:
- "A 5-year outlook showing future repair risk"
- "Each option shows the projected repair cost and energy savings over the next five years"

**Legal exposure:** Forward-looking claims to consumers are DTPA red flags. If a projection turns out wrong, the consumer has a claim. No ToS eliminates this.

**Fix:** Reframe as:
> "Each option includes an *illustrative* 5-year cost estimate based on average patterns for equipment of this age. Actual future costs depend on your specific system and cannot be guaranteed."

Add explicit disclaimer near the projection: *"5-year projections are illustrative estimates from your contractor's professional judgment supported by SnapAI. Actual costs may vary."*

### H4. Privacy Policy missing modern compliance

Deployed Privacy Policy (dated March 23, 2026) omits:
- **CCPA** (California Consumer Privacy Act) — required if any CA residents sign up
- **CPRA** (California Privacy Rights Act, effective 2023) — required extension
- **GDPR** — required if any EU residents sign up (Sajan is founder; PK team members)
- **TCPA** — no opt-in disclosure for the homeowner phone number field, exposing SnapAI/contractors to TCPA class actions if any auto-dialer or SMS is used
- **BIPA** (Illinois Biometric Information Privacy Act) — if photos ever contain people's faces, IL residents have private cause of action ($1,000-$5,000 per violation)
- **Texas SB 300** biometric consent language
- **Data breach notification** procedures per state

**Fix:** Rewrite Privacy Policy with counsel to include multi-state compliance. Estimated cost: $2-5K legal review. Requires disclosure of state-specific rights, right-to-know procedures, opt-out mechanisms, and biometric handling.

### H5. No visible ToS link anywhere

Verified: Only `Privacy` and `Sign In` appear in nav. No ToS link on homepage, footer, `/homeowner`, `/tech`, dashboard, or onboarding.

Even IF a ToS existed at /tos, courts have voided ToS enforcement when links were not "reasonably conspicuous" (*Meyer v. Uber*, *Cullinane v. Uber*). Users must have reasonable notice of the terms.

**Fix:** After deploying ToS at /tos, add link to:
- Homepage footer (always visible)
- Every landing page footer
- Sign-up flow (checkbox: "I have read and agree to the [Terms of Service](/tos)")
- Onboarding step
- Settings page ("Legal → View Terms of Service")

---

## MEDIUM findings — resolve within 6-8 weeks

### M1. Sidebar navigation uses "Diagnoses"
Change to "Assessments" or "Assist History" per Principle 3.

### M2. Homepage uses "AI identifies everything"
Softens Principle 3 language rules. Change to "AI-assisted equipment identification for your technician's review."

### M3. Dashboard summary uses "AI-powered · three options, one recommendation"
Change to "AI-assisted assessment tool for licensed technicians."

### M4. No documented substantiation file for any marketing claim
Per Principle 5, every marketing claim needs a linked methodology file with 7-year retention. Start the substantiation habit now — every future claim gets a file.

### M5. No accuracy monitoring / auto-suspend visible in operational tooling
Per Principle 1, every fault card needs an accuracy monitor and auto-suspend threshold. Not visible in the deployed operational UI. Build internal admin tooling for this before Tier A ships.

### M6. No incident response protocol documented externally
Per Principle 1, contractor + homeowner should know how to report a safety-adjacent incident. Add a "Report a Concern" link in footer with 24-hour triage commitment.

### M7. No cookie banner
Even with only session cookies, EU visitors expect a cookie banner. If any EU traffic (Sajan/team), add banner.

### M8. No age gating on `/homeowner`
Homeowner-facing pages should include age verification or minor exclusion language.

### M9. No published "Known Limitations" page
Per Principle 5, publish a `/limitations` page listing what the app does not do (combustion, HX, CO, etc.). Reduces FTC deception risk.

---

## LOW findings — nice-to-fix

### L1. Privacy Policy contact email is `hello@mainnov.tech` not `privacy@snapai.mainnov.tech`
Small brand inconsistency; consider dedicated privacy email.

### L2. No published data retention schedule
Privacy Policy says "we store data" but not for how long. Add explicit retention periods.

### L3. Homepage footer says "SnapAI by Mainnov"
Confirm entity structure. Mainnov is the parent brand; SnapAI is the product. Legal entity for ToS must be clarified — is Mainnov Inc. the party contracting with contractors?

### L4. Assessment sidebar count "EARLY ACCESS" pill
Reduces implied warranty when users see beta framing — actually helpful legally. Keep.

---

## Comparison against Alfred's v1 Legal Framework

| Layer | Framework requires | Live state | Gap |
|---|---|---|---|
| Layer 1 — Homepage disclaimer | Prominent + footer | **Neither present** | CRITICAL |
| Layer 2 — Contractor ToS | 16 sections deployed | **/tos returns 404** | CRITICAL |
| Layer 3 — Onboarding acknowledgment | 6-checkbox click-through + license verification | **None; License optional** | CRITICAL |
| Layer 4 — In-app Output disclaimer | Inline on every fault card view | **Not present anywhere** | CRITICAL |
| Layer 5 — Homeowner report disclaimer | Attached to every report | **Not verifiable (report gen requires assessment)** | HIGH (verify separately) |

**Five out of five layers missing or incomplete.** This is the entire legal shield structure — not deployed.

---

## Recommended action plan

### Week 1 (immediate — stop-the-bleed)
1. Publish a bare-minimum ToS at `/tos` (even the v1 draft, unreviewed, is better than nothing). Add link to homepage footer.
2. Add homepage prominent disclaimer above fold on `/`, `/homeowner`, `/tech`.
3. Suspend the "Share with your contractor" CTA on `/homeowner` page (highest DTPA exposure).
4. Contact 3 Texas-licensed SaaS attorneys for engagement quote. Recommended: Baker Botts, Winstead PC, Jackson Walker.
5. Contact 3 tech E&O insurance brokers for quote. Recommended: Hiscox, Founder Shield, Vouch.

### Week 2-3 (foundational fixes)
6. Rewrite `/homeowner` per C2 to shift positioning to "your contractor's tool"
7. Rewrite `/tech` per H1 to remove "diagnostic tool" language
8. Rebuild onboarding per C3 with ToS acceptance + acknowledgment + required license
9. Add in-app output disclaimer per C4 to every fault card view + assessment output
10. Retain Texas counsel for ToS final review
11. Retain E&O insurance broker for policy placement

### Week 4-6 (substantiation + compliance)
12. Build substantiation file habit — every marketing claim gets a file
13. Rewrite Privacy Policy for multi-state compliance (H4)
14. Publish `/limitations` page (M9)
15. Deploy accuracy monitoring + auto-suspend infrastructure (M5)
16. Publish "Report a Concern" flow (M6)
17. Add ToS acceptance to all sign-up entry points

### Ongoing
18. Marketing accuracy review before every homepage/collateral change
19. Annual ToS review with counsel
20. Annual insurance renewal + scope confirmation

---

## Bottom line — Alfred's verdict

**Current state is not safe to scale.** The app is a professional decision-support tool wearing consumer-diagnostic marketing clothes, with no legal foundation underneath. Every day of continued operation in current state accumulates liability exposure that no ToS applied later can retroactively fix.

**Ship-blocking for scale:** Yes. Tier A cannot ship until Critical findings C1-C4 are resolved.

**Ship-blocking for current beta operation:** Not immediately, but every new signup between now and remediation is an uncapped liability event. Fix within 30 days.

**Estimated remediation cost:** $10-40K one-time (counsel + insurance placement) + 3 weeks of engineering. Small relative to the cost of a single lawsuit.

**Bryan Orr — HVAC field addition:**
The "Diagnoses" tab and "Diagnostic engine" language would embarrass this product in front of any senior HVAC tech. In the field, a diagnostic is what the tech does — not what the tool does. Fixing the language isn't just legal hygiene, it's product-authenticity discipline. Contractors will trust the tool more when it positions itself accurately.

**Mark Delgado — product strategy addition:**
The `/homeowner` page is doing the *opposite* of what a decision-support tool should do — it's marketing directly to the consumer, which is both a legal problem AND a channel-conflict problem with your contractor customers. Fix this page and you simultaneously solve DTPA exposure AND strengthen contractor relationships. The rewrite Alfred suggested is *stronger positioning*, not weaker: "your contractor's professional tool" is a better story than "the AI that diagnoses your HVAC."

---

## Change log

- **2026-07-05:** Initial audit report. Alfred + Bryan + Mark reviewed. No production writes made. Awaiting Shoab's decisions on remediation priority.

