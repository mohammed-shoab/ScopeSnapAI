# SnapAI New-Card Wordings v1 (Gate 3/6) -- #20, #22, #24 + Reading Receipt

Date: 2026-07-06
Copy lead: Codie (/snapai-copywriting). Legal guardrails: Alfred (US/TX). Verified angle: Bryan Orr + Mark Delgado.
Status: DRAFT. Two hard gates before any string ships (same as Legal-Safe Wordings v1):
  GATE 1 -- no "honest"/"no upsell" self-claim (parked until substantiation file).
  GATE 2 -- Alfred signs off #24, #22 homeowner strings individually before prod (highest-liability outputs).

Surface rule (from the surface taxonomy):
- CONTRACTOR-FACING = authenticated app (login + signed ToS + verified contractor). "diagnose" OK. Technical language.
- HOMEOWNER-FACING = report / PDF / share link. Consumer rules: no "diagnosis", no medical grading, no future-tense
  outcome promise (DEC-088), all conclusions attributed to the licensed contractor ([Company]).
- No city names in any string (geo-neutral, backend-only).

================================================================
0. SHARED -- THE "READING RECEIPT" (Gate 5 design rule, every terminal card)
================================================================
Every sub-mode conclusion renders this block INLINE on FaultResolutionScreen (never behind a link -- Bryan's rule).
Contractor-facing template:

  You entered:        {reading_value} {unit}
  Compared against:   {target_low}-{target_high} {unit}  ({source, e.g. "R-410A, 95F, TXV"})
  Result:             {low | within range | high}
  Why this card:      {one plain line -- what the reading indicates}
  Ruled out:          {sibling fault} -- {the reading that excludes it}
  Confidence:         {High | Medium | Low}
  [inline Layer 4]:   Preliminary decision-support output. Verify independently.
                      You, the licensed technician, make the final call.

Tail cards (10a/d/e, 15b/c/d) default to Confidence: Low until field-validated.

================================================================
1. CARD #20 -- SYSTEM UNDER-AIRFLOW
================================================================
CONTRACTOR-FACING (authenticated app)
  Card title:    System under-airflow
  Receipt Why:   Total external static is above the design budget, so air moves through the system
                 harder than it should.
  Readings:      TESP {value} in.w.c. vs 0.5 budget; highest static drop at {filter|coil|duct|system-wide}; delta-T {value} F.
  Ruled out:     Dirty filter/coil -- highest static drop is not localized there.
  Action line:   Confirm the 4-point static profile before writing the correction.

HOMEOWNER-FACING (report line item)
  Section header:  Airflow assessment
  Body:            [Company] measured the air pressure your system works against. The reading is higher
                   than the range [Company] uses as a target, which means the system is moving air
                   harder than intended. [Company] has listed what they found and the options to
                   improve it below.
  Tier label:      [Company]'s recommendation

================================================================
2. CARD #22 -- LATENT CAPACITY DEFICIT (comfort / clammy)
================================================================
CONTRACTOR-FACING (authenticated app)
  Card title:    Low latent capacity for current conditions
  Receipt Why:   Indoor humidity is above target while sensible cooling is adequate -- the system is
                 removing heat but not enough moisture.
  Readings:      Return wet-bulb {value} F; indoor RH {value}% vs 45-55 target; delta-T {value} F; blower {value} CFM/ton.
  Ruled out:     Under-airflow -- static within budget. Undercharge -- subcool normal.
  Action line:   Confirm blower speed and load before presenting a moisture-control option.

HOMEOWNER-FACING (report line item)   [Alfred sign-off required -- performance-adjacent]
  Section header:  Humidity assessment
  Body:            [Company] measured the temperature and humidity inside your home. The reading shows
                   indoor humidity above the comfort range [Company] targets, even while the system is
                   cooling. That is what makes rooms feel clammy or sticky. [Company] has noted options
                   below for improving moisture control.
  Tier label:      [Company]'s recommendation
  Banned here:     "will keep your home dry", "eliminates humidity", any future-tense outcome. State the
                   measurement; attribute the recommendation.

================================================================
3. CARD #24 -- SYSTEM OVERSIZING (highest-liability -- $8-15K replacement path)
================================================================
Alfred hard rule: SnapAI is NEVER the grammatical subject. Recommendation is [Company]'s, stated as an
OPTION, and only after the guardrail (Manual J load calc + two supporting readings + age gate) is shown.
No predictive savings, no "will", no efficiency %. (Texas DTPA exposure -- verify current statute at sign-off.)

CONTRACTOR-FACING (authenticated app)
  Card title:    Suspected system oversizing
  Receipt Why:   Short run cycles with static within budget and normal charge point to cooling capacity
                 exceeding the home's load.
  Readings:      Run-time {value}%; cycle rate {value}/hr; TESP {value} (within budget); age {value} yrs;
                 installed capacity {value} tons vs Manual J load {value} tons.
  Ruled out:     Under-airflow -- static within budget. Overcharge -- subcool normal. Undersizing -- capacity exceeds load.
  Gate (hard):   This card does not present a replacement option until a Manual J load calculation is
                 entered AND two supporting readings are present AND system age gate is met.
  Action line:   Complete a Manual J load calculation to confirm before discussing any replacement.

HOMEOWNER-FACING (report line item)   [Alfred sign-off required -- highest exposure]
  Section header:  Sizing assessment
  Body:            [Company] measured how often your system turns on and off and compared it to the
                   cooling load this home needs. The readings suggest the system may be larger than the
                   home requires. Before discussing any options, [Company] recommends a load calculation
                   to confirm. Any equipment recommendation below reflects [Company]'s professional
                   judgment as a licensed contractor.
  Tier label:      [Company]'s recommendation
  Required note:   This assessment is not a certification of equipment condition or performance. Findings
                   require independent verification by your licensed contractor. (Layer 5, matches PDF disclaimer.)
  Banned here:     "you'll save", "your bill will drop", "right-sizing pays for itself", any number tied to
                   future savings, any "will".

================================================================
COMPLIANCE CHECKLIST (run before any string ships)
================================================================
[ ] DEC-088 banned words (prevent, guarantee, ensure, will not, lasts X yrs, eliminates, stop forever,
    save you $X, bill will drop, 5-yr savings) -> zero in homeowner strings.
[ ] No city / region name in any string.
[ ] No "honest"/"no upsell" self-claim (Gate 1 parked).
[ ] Every homeowner conclusion attributed to [Company]; SnapAI never the subject of "diagnose".
[ ] #24 replacement option gated behind Manual J + two readings + age gate.
[ ] Layer 4 inline disclaimer renders on the new fault-resolution surfaces.
[ ] Pre-commit hook extended to scan these new card output strings.
[ ] Alfred individual sign-off on #24 + #22 homeowner strings (Gate 2) before prod.
