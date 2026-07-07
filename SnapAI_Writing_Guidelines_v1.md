# SnapAI Writing Guidelines v1 — the canonical reference for every SnapAI string

**Version:** v1.0
**Date:** 2026-07-06
**Owners:** Alfred (nav — legal, US/TX) · Bryan Orr (board — HVAC domain) · Mark Delgado (board — brand + product strategy) · Codie (snapai-copywriting skill — copy lead) · Shoab (final approval)
**Status:** Canonical. Every SnapAI string in every medium follows this file.
**Consolidates:** SnapAI_Legal_Safe_Wordings_v1_2026-07-06.md · SnapAI_NewCard_Wordings_v2_COMPLETE_2026-07-06.md · SnapAI_Legal_Framework_ToS_and_Disclaimers_v1_DRAFT.md · SnapAI_Legal_UI_Audit_v2_DEEP_2026-07-05.md · SnapAI_Project_Instructions.md §6 sensitive rules · personas/_banned_phrases.md · snapai-copywriting skill · scripts/check_legal_banned_strings.py (machine-enforced subset)

---

## 1. Purpose + scope

**Purpose.** Every SnapAI-branded string in any medium — app UI, homeowner report, marketing page, email, social post, cold outreach, video script, press quote, investor deck, contractor onboarding, legal doc — is governed by this file. When in doubt, this file is the authority.

**Why one file.** Fragmented guidance creates drift. Drift creates inconsistency. Inconsistency is legal evidence of deception under DTPA §17.46 and FTC Section 5, and it undermines every downstream defense. Unified guide = defensible discipline.

**Scope — every surface:**
- Contractor-authenticated app UI · Homeowner-facing surfaces · Public marketing pages · Legal docs · Sales collateral · Outreach content · Social + video · Investor / press

**Scope — every author:** AI in Cowork chats · Codie · Sajan · Azhan · Murtaza · Shoab · future hires, contractors, or ghost-writers.

---

## 2. The audience matrix — different rules per surface

### 2A. Contractor — authenticated app
Voice: Technical, direct, HVAC-authentic. Legal-safe: "diagnose"/"diagnosis"/"superheat"/"TESP" OK inside the authenticated app per ToS §2A definitional clause. Attribution: "SnapAI recommends…" OK. Layer 4 disclaimer required on every terminal card.

### 2B. Homeowner — anything the homeowner sees
Voice: Warm, jargon-free, non-technical. **DTPA §17.42 applies** — Texas consumers cannot waive DTPA rights regardless of ToS.
- ❌ NO "diagnosis"/"diagnostic"/"diagnose"/"diagnosed" in any homeowner-facing string
- ❌ NO medical grading ("critical," "poor" as consumer-visible severity)
- ❌ NO future-tense outcome promises (DEC-088)
- ❌ NO specific efficiency claims without substantiation
- ❌ NO "the app determined" or "SnapAI diagnosed"
- ✅ ALL conclusions attributed to `[Company]` (the licensed contractor)
- ✅ Layer 5 disclaimer required
- Applies to: homeowner report PDF, homeowner email, `/r/[slug]/[reportId]` web page, homeowner correction flow, public share `/d/[share_token]`

### 2C. Public marketing — pre-login pages, blog, social
Voice: Founder-credible, understated, technically honest. Every claim needs a substantiation file (§6). DTPA §17.46 triggers on unsubstantiated superlatives → treble damages + attorneys' fees.

### 2D. Legal docs — ToS, Privacy, disclaimers
Voice: Formal, precise. No plain-language rewrites of ToS clauses without counsel review. Definitional clause language (ToS §2A-2C) exact — don't paraphrase. All ToS-facing surfaces reference `Mainnov` as legal entity name (pending Wyoming LLC formation).

### 2E. Contractor onboarding
6 positive-affirmation checkboxes: License # + State + ToS acceptance + Decision-support acknowledgment + Independent-verification obligation + CO/HX/combustion safety scope exclusion acknowledgment.

### 2F. Email
Homeowner emails follow §2B; contractor emails follow §2A. NEVER mix.

### 2G. Social + outreach
Founder-authentic (Sajan). Data-scientist background, trades-respectful, no LinkedIn-influencer voice. Every cold email references a specific dossier finding.

---

## 3. Alfred's flag system — signals liability level

- **`[A!]`** — high-liability. Alfred sign-off required. Examples: expensive recommendations ($5K+), performance claims, health/safety-adjacent, Cards #22/#24/#10a/b/c-family.
- **`[A]`** — standard legal review. Recurring copy, marketing pages, blog posts.
- **(no flag)** — low-risk. Internal Slack, non-user-facing docs.

**When to flag:** if wondering, flag it. False positives cost minutes; false negatives cost millions.

---

## 4. Language do's and don'ts — the substitution table

**Enforcement note:** `scripts/check_legal_banned_strings.py` (pre-commit hook) blocks a SUBSET of these tokens on 8 file paths. This guide is the HUMAN-READABLE SUPERSET. When you add a rule here, sync it to the script within 1 week.

### Diagnostic language

| ❌ Banned (homeowner-facing or public marketing) | ✅ Preferred |
|---|---|
| SnapAI diagnoses your HVAC | SnapAI supports your contractor's diagnostic process |
| The app tells you what's wrong | Your contractor uses SnapAI to identify potential issues |
| Diagnostic report | Contractor assessment report |
| Equipment health report | Contractor assessment summary |
| We diagnosed your unit | Your contractor observed the following |
| Certified diagnosis | Preliminary finding |
| The AI determined the fault | Preliminary finding for your contractor to review |
| Health rating: Critical/Poor/Fair/Good/Excellent (consumer-visible) | Your contractor's assessment: [specific observation + recommendation] |

### Superlatives and absolute claims (DTPA §17.46 triggers)

| ❌ Banned everywhere | ✅ Preferred |
|---|---|
| Honest recommendation | Recommendation based on the readings your contractor entered |
| No guessing | Structured diagnostic process |
| No upsell pressure | (delete — SnapAI doesn't control contractor pricing) |
| Guaranteed savings | Estimated savings based on typical usage |
| The best HVAC diagnostic tool | Decision-support built specifically for HVAC contractors |
| Instant diagnosis | Immediate structured findings for your contractor's review |
| 100% accurate | (delete — no accuracy claim without substantiation file per §6) |
| Only tool that does X | (delete — competitive claims need substantiation) |
| Never miss a fault | (delete — non-disclaimable outcome promise) |
| Most honest | (delete) |

### Future-tense outcome promises (DEC-088)

**Machine-enforced tokens** (blocked by `check_legal_banned_strings.py`): `prevent`, `guarantee`, `ensure`, `will not`, `lasts`, `eliminates`, `stop forever`, `save you $`, `bill will drop`, `5-year savings`, `issues get worse`.

| ❌ Banned in homeowner-facing copy | ✅ Preferred |
|---|---|
| Your bill will drop by X% | (delete or reframe as illustrative + contractor-verified) |
| You'll save $X per year | Estimated typical savings for equipment of this age. Your contractor will verify. |
| Your system will run better | Your contractor recommends this to improve system performance |
| You'll never need to replace this | (delete) |
| This will prevent breakdowns | (delete — "prevent" is machine-blocked) |
| Guaranteed to work | (delete — "guarantee" is machine-blocked) |
| Ensures a quiet unit | (delete — "ensure" is machine-blocked without disclaimer signal) |
| Lasts 20+ years | (delete — "lasts" is machine-blocked) |
| Eliminates humidity issues | (delete — "eliminates" is machine-blocked) |
| Fix your problem for good | (delete) |
| Stop forever | (delete) |
| 5-year savings guaranteed | (delete — machine-blocked) |
| Issues get worse if you wait | (delete — machine-blocked, DTPA scarcity trigger) |

### Timing / speed claims

| ❌ Banned unless substantiated | ✅ Preferred |
|---|---|
| Diagnose in 60 seconds | (delete or replace with "in minutes") |
| Instant analysis | Fast structured analysis |
| Before you leave the driveway | (delete or replace with "on-site") |
| 30-second setup | Quick setup |

### City / region names (geo-neutral rule)

**Machine-enforced on public paths** (`scopesnap-web/app/tech/`, `/methodology/`): tokens `houston`, `katy`, `sugar land`, `cypress`, `pasadena tx`.

**Never name a city, state, or region in any user-facing string.** Use "your area" or "your region."

- ❌ "Built for Houston HVAC contractors" · ✅ "Built specifically for residential HVAC contractors"
- ❌ "Serving Texas HVAC pros" · ✅ "Built for HVAC professionals working in residential markets"

### Attribution rule (ALFRED C3)

| ❌ Banned in homeowner-facing surfaces | ✅ Preferred |
|---|---|
| SnapAI recommends replacing your compressor | `[Company]` recommends replacing your compressor after reviewing the readings |
| The app found a refrigerant leak | Your contractor `[Company]` found evidence of a refrigerant leak |
| SnapAI thinks you need a new unit | Your contractor `[Company]` recommends a full replacement based on the following |

### Diagnos* family — allow-signals

The check_legal_banned_strings.py script uses a regex on `diagnos*` and ALLOWS the token when the same line contains a disclaimer signal: "not " · "does not" · "no " · "isn't" · "n't" · "your contractor" · "the contractor" · "the technician" · "the tech" · "licensed" · "certified".

When you write a disclaimer that legitimately uses "diagnosis" (e.g., *"This is not a diagnosis"*), keep both the disclaimer word and the allow-signal on the same line.

---

## 5. DTPA red flags to avoid

Texas DTPA §17.46 triggers on: (1) unsubstantiated superlatives, (2) health/medical claims, (3) comparative claims without data, (4) certification claims without certification, (5) endorsement claims without FTC-compliant documentation, (6) price/value claims without audited survey, (7) guarantee language, (8) time-bound urgency without deadline, (9) fake scarcity, (10) fake social proof.

**Rule of thumb:** if a competitor's law firm could screenshot your copy and win a $100K settlement, don't ship it.

---

## 6. Substantiation file rule (Alfred's Preventive Principle 5)

Every marketing/product claim needs a corresponding substantiation file:
- Exact source · Date gathered · Named verifier · Confidence (H/M/L) · Retention 7 years

Location: `Personal Claude/marketing/substantiation/{claim_slug}_YYYY-MM-DD.md`

Discipline: if substantiation file doesn't exist, claim doesn't ship. Missing file = FTC deceptive-practices finding.

Grandfathered claims: any live marketing claim lacking a substantiation file = retirement candidate. Weekly audit will flag.

---

## 7. Geo-neutral rule

Locked standing rule:
- Public-facing pages: no city, state, region, or country name
- Homeowner-facing surfaces: no city name anywhere
- Contractor-authenticated app: geo OK for backend routing, never user-facing
- Sales/marketing collateral: geo-neutral decks
- Investor materials: geo-neutral
- Cold email: no geo in body
- Video scripts: no geo mention

Exceptions: onboarding form asks for state (form field, not marketing). Legal ToS names Texas (enforceability, not marketing).

Machine-enforced tokens: `houston`, `katy`, `sugar land`, `cypress`, `pasadena tx`. Human rule broader: no city/state/region anywhere user-facing.

---

## 8. Attribution rule (ALFRED C3, elevated)

On homeowner-facing surfaces, ALL conclusions attributed to `[Company]`, never to the app. `[Company]` = the licensed HVAC contractor's business name.

Why: DTPA §17.42 protects consumer expectations. Under contra proferentem doctrine, ambiguity resolves against SnapAI. Attribution to `[Company]` puts liability on the contractor.

---

## 9. Reading Receipt canonical format (GATE-5)

Every terminal card renders inline (never behind "learn more"):

```
You entered:        {reading_value} {unit}
Compared against:   {target_low}-{target_high} {unit}  ({source})
Result:             {low | within range | high}
Why this card:      {one plain line — max 12 words}
Ruled out:          {sibling fault} — {the reading that excludes it}
Confidence:         {High | Medium | Low}
[Layer 4 disclaimer text]
```

Every threshold cites the source (ASHRAE, ACCA Manual J, manufacturer bulletin, NIST FDD).

Confidence banding:
- High = ≥100 field cases validated, sourced, false-positive rate <5% documented
- Medium = 25-100 field cases
- Low = <25 field cases (default for tail cards #10a, #10d, #10e, #15b, #15c, #15d)

Never fabricate "High Confidence." If field data thin, ship at Low or Medium.

Reference: `tierA_build/ReadingReceipt.tsx`.

---

## 10. Layer 4 + Layer 5 disclaimer canonical text (ALFRED C2)

### Layer 4 — inline app Output disclaimer (every fault card)

**Exact text (do not rephrase):**
> **SnapAI recommendation only — NOT a certified diagnosis.**
> Verify all findings independently before acting. Do not present this Output to a Homeowner as a certified diagnosis.

**Enhanced version** (required on >$5K recommendations — Cards #24, #22, #10a-c-e):
> **This is a preliminary finding requiring independent Manual J load calculation and licensed inspection before any equipment replacement or major service recommendation is presented to the Homeowner.**

Always inline, always visible, never behind "learn more," never below fold.

### Layer 5 — homeowner report disclaimer (every homeowner-visible surface)

**Exact text:**
> **About this report.**
> This report contains preliminary findings generated by SnapAI, a diagnostic decision-support tool used by your HVAC contractor. **SnapAI does not perform HVAC diagnoses.** Your licensed HVAC contractor is solely responsible for interpreting these findings, verifying them independently, and recommending any service action.
>
> Any recommended repair, replacement, or service must be verified by the licensed contractor performing the work. **Do not rely on this report as a certification of HVAC equipment condition, safety, or performance.**
>
> **For your safety:** SnapAI does not currently perform combustion, heat exchanger, or carbon monoxide safety diagnostics. Always ensure a licensed HVAC contractor performs a full combustion safety inspection on gas-fired equipment. Install and maintain functioning carbon monoxide detectors on every level of your home.
>
> **Questions or concerns:** Contact your HVAC contractor directly.

Always at top of homeowner report, in body-text size (not fine print).

---

## 11. Confidence banding rules

- High = ≥100 Houston field cases + sources + false-positive <5% documented
- Medium = 25-100 field cases + sources + FP rate documented
- Low = <25 field cases (default tail cards)

Never claim "Accuracy: 99%" in user-facing text without substantiation file (§6).

---

## 12. Brand voice tone (Codie)

- Data-scientist founder building from scratch — technical credibility without hype
- Trades-respectful — HVAC professionals are the audience
- Understated over hyperbolic — one superlative = zero credibility with trades
- Numbers over adjectives ("8% higher first-call resolution" beats "much better")
- No LinkedIn-influencer voice

Full voice guide: `snapai-copywriting` skill.

**Contractor-facing** (in-app + tech marketing): direct, technical, HVAC-authentic. Trade vocabulary preserved. "Diagnose" OK inside app.

**Homeowner-facing** (report + email): warm, non-technical. "Your contractor" as actor. Under 40 words per paragraph. Sixth-grade reading level. No medical analogies.

**Marketing** (public pages, social): founder-authentic (Sajan-tone). Data-scientist background surfaces naturally. Never "we're disrupting HVAC." Never "AI will replace techs." SnapAI supports contractors; positioning is *for* techs, not *against* them.

---

## 13. The 5-step approval SOP

Every outbound message follows:
1. **Prompt-craft** — AI or Codie drafts using this guide + specific skill
2. **Shoab review** — first human pass
3. **@board review** — Bryan (HVAC), Mark (brand/product), Diana Cole, Rory, etc.
4. **@nav review** — Alfred (legal), Chris Voss, Andy Raskin, etc.
5. **Shoab finalize + send**

No exceptions. Even small landing-page tweaks follow this.

---

## 14. Emergency-language rules (CO / gas / fire / electrocution / HX)

**Structural exclusions:**
- Combustion Safety Check sub-flow — permanently excluded (Alfred + Bryan 2026-07-06)
- Card #21 Heat Exchanger Damage — permanently excluded (structural, not Tier D hold)
- Carbon monoxide diagnosis — never in any homeowner-facing surface
- Gas line / gas valve diagnostic — never in any homeowner-facing surface
- Live high-voltage panel work — never recommended to homeowners
- Refrigerant handling — only to verified-licensed contractors (EPA §608)

**Copy rules:**
- Homeowner report Layer 5 disclaimer includes CO detector recommendation regardless of findings
- Never write "your unit is safe" — instead: "your contractor `[Company]` will complete a full safety inspection"
- Any surface mentioning CO/HX/combustion in a diagnostic role → STOP → escalate to Alfred BEFORE ship
- Emergency callouts direct to 911 + gas company, not to `[Company]`

**When in doubt on safety language: don't write. Escalate.**

---

## 15. Change log + version discipline + machine-enforcement sync

**Version 1.0 (2026-07-06)** — Initial canonical guide. Consolidated 7+ scattered docs. Alfred reviewed + signed off. Bryan + Mark + Codie contributed. Cross-referenced with `scripts/check_legal_banned_strings.py`.

**Version discipline:**
- File always semantic-versioned in filename
- Rule addition = minor bump (v1.1)
- DTPA-material change = major bump (v2.0)
- Every change logged at top
- Retired rules move to "Retired" section, never deleted

**Machine-enforcement sync rule:**
- This guide = CANONICAL SUPERSET (human-readable)
- `scripts/check_legal_banned_strings.py` = SUBSET (machine-enforced at pre-commit on 8 file paths)
- When guide adds a rule, sync script within 1 week
- When script updates, reflect in guide first (guide authoritative)
- Weekly audit checks drift between guide §4 banned lists and script's DEC088_TOKENS / SELF_CLAIM_TOKENS / GEO_TOKENS

**Escalation:**
- Legal / DTPA / disclaimer / attribution → Alfred
- HVAC domain / field-authenticity / trade vocabulary → Bryan
- Brand voice / product positioning / marketing narrative → Mark
- Specific copy / landing pages / blog / social → Codie
- Comprehensive review → all four via 5-step SOP §13

---

## Related files

- `scripts/check_legal_banned_strings.py` — machine-enforced subset (pre-commit)
- `tierA_build/compliance_scan.py` — broader compliance scanner (QA-time)
- `tierA_build/ReadingReceipt.tsx` — reference component for §9 format
- `tierA_build/card24_gate.py` — ALFRED C1 Manual J server-side gate
- `SnapAI_Legal_Safe_Wordings_v1_2026-07-06.md` — applied wordings (DEC-130)
- `SnapAI_NewCard_Wordings_v2_COMPLETE_2026-07-06.md` — new-card wordings (Alfred cond signed off)
- `SnapAI_Legal_Framework_ToS_and_Disclaimers_v1_DRAFT.md` — 5-layer defense + ToS
- `SnapAI_Legal_UI_Audit_v2_DEEP_2026-07-05.md` — audit findings that motivated this guide
- `SnapAI_Project_Instructions.md` — router; Section 8 points here for copy work
- `personas/_banned_phrases.md` (marketing) — supplementary, deferred to this file
- `snapai-copywriting` skill — Codie's fuller voice + tone spec
- DEC-088 (no future-tense homeowner promises) · DEC-070 (staging-first) · DEC-123 (PK dormant) · DEC-129 (verify live Supabase) · DEC-130 (legal-safe-wordings v1)

---

## Ownership + escalation

- **Sole final authority:** Shoab
- **Legal escalation:** Alfred (nav)
- **HVAC domain escalation:** Bryan Orr (board)
- **Brand + product escalation:** Mark Delgado (board)
- **Copy execution:** Codie (snapai-copywriting)
- **Board reviewers:** Diana Cole, Rory Sutherland, Chris Voss, Andy Raskin per §13

**Any rule ambiguity → escalate. Do not paraphrase this guide.**
