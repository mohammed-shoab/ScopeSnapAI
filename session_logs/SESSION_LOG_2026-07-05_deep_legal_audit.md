# SESSION LOG — Deep Legal Audit (v1 UI + v2 code) + ToS Framework — 2026-07-05

**Duration:** ~4 hours
**Participants:** Shoab + Alfred (nav — US HVAC legal counsel) + Bryan Orr (board — HVAC domain) + Mark Delgado (board — product strategy)
**Related workstream:** Legal cover + wordings update (workstream #1 of the 4 active)
**Related files:**
- v1 UI audit: `SnapAI_Legal_UI_Audit_2026-07-05.md` (172 lines)
- v2 deep audit: `SnapAI_Legal_UI_Audit_v2_DEEP_2026-07-05.md` (472 lines — authoritative current state)
- v1 ToS framework: `SnapAI_Legal_Framework_ToS_and_Disclaimers_v1_DRAFT.md`
- Legal continuation prompt: `SnapAI_Legal_Discussion_Continuation_Prompt.md`
- Legal verbatim transcript: `SnapAI_Legal_Discussion_Verbatim_Transcript_2026-07-05.md`

## Context (what we started with)

Bryan raised Card #21 Heat Exchanger CO liability as one of five issues with "build everything at once." Shoab asked Alfred for a specific legal take. What began as a single-card review became a full legal-cover system audit — the app has zero deployed ToS, homeowner page markets directly to consumers, LLM prompts frame the AI as "the diagnosis system," and the DB/API schemas embed "diagnostic" throughout.

## Goal (what we tried to accomplish)

1. Assess Card #21 Heat Exchanger CO liability specifically
2. Build a ToS + disclaimer framework that maximizes protection
3. Audit the live app against that framework
4. Identify all Critical findings that must fix before scale

## What we tried (chronological)

1. **Alfred's Card #21 legal take** — six-gate framework (insurance rider, ToS rewrite, homeowner report language, threshold recalibration, PE engineering review, full audit trail). Concluded Card #21 = Tier D indefinite hold, not Tier C.
2. **Full ToS + 5-layer framework draft** — Shoab asked "zero legal issue via strong ToS?" Alfred pushed back that zero is impossible in the US, but ~95% is achievable via 5-layer defense (Homepage disclaimer + Contractor ToS + Onboarding acknowledgment + In-app Output disclaimer + Homeowner report disclaimer). Saved as `SnapAI_Legal_Framework_ToS_and_Disclaimers_v1_DRAFT.md`.
3. **5 non-disclaimable risks + preventive design principles** — Shoab asked "how can my app trigger those?" Alfred derived 5 preventive design principles (no safety-critical diagnostics, no direct-to-consumer relationship, language consistency, documented QA + accuracy monitoring, substantiation files).
4. **v1 UI audit** (Chrome walk) — 12 URLs audited. Found 4 Critical (C1-C4): no ToS deployed (`/tos` returns 404), homeowner page violates DTPA §17.42 with direct-to-consumer diagnostic marketing, no onboarding acknowledgment + License optional, no in-app Output disclaimer on assess flow.
5. **Shoab pushed for deeper audit** — "have you audited the code and app language too?" Alfred acknowledged v1 was surface-level marketing only.
6. **v2 deep code audit** — grep + read across `scopesnap-web/` + `scopesnap-api/`. Found 8 more Critical findings (C5-C12) at deeper layers: LLM prompt frames AI as "expert HVAC fault diagnosis system" (highest-leverage finding), homeowner LLM prompt uses "doctor visit summary" analogy, DB tables + API + events named "diagnostic," PDF template has zero disclaimers, report titled "Equipment Health Report" with predictive claims, homeowner emails include predictive claims + urgency, "Diagnoses" sidebar nav, "Cancel diagnosis" button + "Confidence" bands without substantiation.
7. **Definitional-clause strategy** — Shoab asked "can we keep the word 'diagnosis' if the ToS defines it as 'assists tech'?" Alfred confirmed YES for contractor-facing surfaces (~55-60% of rename work drops off) but NO for homeowner-facing surfaces (DTPA §17.42 voids consumer waivers). Drafted Section 2A-2C definitional clause for the ToS.

## What worked

1. **5-layer defense framework** — clean structural approach; each layer has distinct disclaimability characteristics.
2. **5 preventive design principles** — turns "cannot be disclaimed" risks into "will not be triggered" via product design.
3. **Chrome walk for v1 UI audit** — grounded findings in what's actually deployed.
4. **Grep + code read for v2 deep audit** — surfaced the LLM system prompt as the highest-leverage single fix (6 code edits touching 2 files eliminates the "diagnosis system" framing).
5. **Definitional-clause B2B/B2C split** — smart compromise; keeps field-authentic contractor language while protecting homeowner-facing surfaces.
6. **Board diversity** — Alfred on legal, Bryan on HVAC-field-authenticity, Mark on product-strategy each contributed non-overlapping layers.

## What DIDN'T work

1. **Initial v1 audit was too shallow.** Only walked marketing pages — missed the LLM prompts, DB schema, PDF template, emails, and fault-resolution UI. Shoab had to push for the deeper pass.
2. **"Zero legal issue" is not achievable in the US.** Alfred had to correct Shoab's initial framing; gross negligence, willful misconduct, personal injury under §402A, and DTPA §17.42 consumer waivers are non-disclaimable regardless of ToS quality.
3. **NFPA 54 threshold (100 ppm CO) is too permissive for product liability defense.** Alfred recommended tiered thresholds — 9 ppm ambient (investigate), 35 ppm (advisory + notification), 100 ppm (mandatory red-tag).

## Root causes

1. **The v1 audit's shallowness was a scope-underestimation** — I audited what was easy to see (marketing pages) not what carried actual liability (LLM prompts, DB schema, report template).
2. **"Zero legal issue" ambition** was a US-legal-context misconception — some risks are structurally non-disclaimable.
3. **The 100 ppm CO threshold** was designed for emergency-service response (evacuation), not product-liability defense. Wrong optimization target.

## Resolution

- Card #21 = Tier D indefinite hold. 6 gates before ship (insurance rider, ToS, homeowner report language, threshold recalibration, PE engineering review, full audit trail).
- 5-layer defense framework drafted and saved to canonical location.
- 12 Critical findings documented in v2 deep audit with per-file, per-string severity ratings.
- Definitional-clause strategy (Section 2A-2C) offered as engineering-cost tradeoff.

## Lessons for next time

1. **Audit scope = audit depth × audit surface.** Marketing pages alone are not a full legal audit; must include code, DB, prompts, templates, emails.
2. **"Zero legal issue" is a founder trap.** ~95% protection is the realistic ceiling; be honest early.
3. **LLM system prompts are the deepest liability layer.** They frame the AI's self-conception; every downstream response inherits that framing. Prompt-audit is critical.
4. **DTPA §17.42** voids consumer waivers regardless of ToS wording. Homeowner-facing surfaces need substantive change, not just legal disclaimers.
5. **Field-authentic language ≠ legally safe language.** "Diagnosis" is authentic tech vocabulary but consumer-visible on homeowner surfaces = DTPA trigger. B2B/B2C split resolves the tension.

## Follow-up items

- [ ] Retain Texas SaaS attorney to review v1 ToS draft ($3-8K, Baker Botts / Winstead PC / Jackson Walker)
- [ ] Get tech E&O insurance broker quotes ($5-25K/yr, Hiscox / Founder Shield / Vouch)
- [ ] Deploy v1 ToS at `/tos` (blocker on scale)
- [ ] Rewrite `/homeowner` per C2 (blocker on DTPA exposure)
- [ ] Rewrite both LLM system prompts (`cascade_prompts.py` + `homeowner_narrative.py`) — highest-leverage single change
- [ ] Add PDF disclaimer block to `contractor_estimate.html`
- [ ] Rewrite homeowner report title from "Equipment Health Report" to "Contractor Assessment Report"
- [ ] Route homeowner emails through contractor domain OR add SnapAI decision-support disclaimer

## References

- Related DECs: none new this session; audit references DEC-088 (no future-tense homeowner copy)
- Related brain files: none updated this session (updated later in brain-files-cleanup session on 2026-07-06)
- Related legal citations: Texas DTPA §17.42 (consumer waiver void), §17.46 (unsubstantiated superlatives → treble damages), Restatement 2d §402A (product liability cannot be waived), Texas §16.012 (15-year statute of repose), Meyer v. Uber / Cullinane v. Uber (ToS enforceability), Wickline v. State / Wilson v. Blue Cross (learned intermediary doctrine), FTC v. Amazon / FTC v. Tapjoy (UI overrides disclaimer), NFPA 54 (100 ppm emergency), EPA §608 (refrigerant handling), Illinois BIPA (biometric)
- Legal continuation: `SnapAI_Legal_Discussion_Continuation_Prompt.md`
- Legal verbatim: `SnapAI_Legal_Discussion_Verbatim_Transcript_2026-07-05.md`

## Change log

- **2026-07-06:** Backdated session log created during Phase 3 retrofit (Option B). Content derived from `SnapAI_Legal_Discussion_Verbatim_Transcript_2026-07-05.md` + `SnapAI_Legal_UI_Audit_v2_DEEP_2026-07-05.md`.
