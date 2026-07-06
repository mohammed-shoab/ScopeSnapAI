# SnapAI New-Card Wordings v2 -- COMPLETE SET (Gate 3/6)

Date: 2026-07-06  (supersedes v1, which covered only #20/#22/#24 + Reading Receipt)
Copy lead: Codie (/snapai-copywriting). Legal guardrails: Alfred (US/TX). Verified angle: Bryan Orr + Mark Delgado.
Scope: EVERY new/expanded card and flow in the v7.1 tree, EXCEPT Card #21 (permanently excluded).
Status: Alfred reviewed + CONDITIONALLY signed off 2026-07-06 (3 code-side conditions -- see bottom). #24 attribution tightened.

Surface rule:
- CONTRACTOR-FACING = authenticated app (login + signed ToS + verified contractor). "diagnose" OK. Technical.
- HOMEOWNER-FACING = report / PDF / share link. Consumer rules: no "diagnosis", no medical grading, no
  future-tense outcome promise (DEC-088), all conclusions attributed to the licensed contractor ([Company]).
- Geo-neutral: no city/region name in any string.
- Confidence: tail cards (10a/d/e, 15b/c/d) default to LOW until field-validated.

Alfred-flag legend:  [A!] = high-liability, Alfred individual sign-off required (expensive recommendation or
performance claim).  [A] = standard review.  (no flag) = low-risk.

================================================================
0. SHARED -- THE "READING RECEIPT" (every terminal card, inline on FaultResolutionScreen)
================================================================
  You entered:        {reading_value} {unit}
  Compared against:   {target_low}-{target_high} {unit}  ({source})
  Result:             {low | within range | high}
  Why this card:      {one plain line}
  Ruled out:          {sibling fault} -- {the reading that excludes it}
  Confidence:         {High | Medium | Low}
  [inline Layer 4]:   Preliminary decision-support output. Verify independently.
                      You, the licensed technician, make the final call.

================================================================
A. NEW QUESTION TEXT (contractor-facing -- asked to the tech in the field)
================================================================
A1. Not Cooling -- superheat/subcool discrimination (new reading gate after low/high suction)
  Q:    Enter superheat and subcool.
  Hint: Suction line temp minus saturation, and liquid saturation minus liquid line. Discriminates leak vs
        metering vs compression.
A2. Not Cooling / High Bill -- TESP capture (routes to Airflow Assessment)
  Q:    Enter total external static pressure (TESP).
  Hint: Across the air handler. Design budget is 0.5 in.w.c. for most residential systems.
A3. Not Turning On -- thermostat / 24V branch (after capacitor reads OK)
  Q:    Check 24V control voltage and C-wire. Enter reading.
  Hint: Meter R-to-C at the board and at the thermostat. Watch for phantom voltage.
A4. Comfort Complaint (Tab J) -- NEW flow
  q1:   Which comfort issue?   [Clammy / sticky] [Rooms uneven -- some hot, some cold] [Short-cycling]
  q2 (clammy): Read return wet-bulb and indoor RH.
        Hint: Compare RH to the 45-55% comfort band.
  q3 (clammy): Enter blower speed (CFM/ton) and confirm load basis.
        Hint: Low airflow and oversizing both drive high latent load -- this separates them.

================================================================
B. CROSS-CUTTING SUB-FLOW QUESTION TEXT (contractor-facing)
================================================================
B1. Airflow Assessment sub-flow
  step 1: Enter total external static pressure (TESP).   [target 0.5 in.w.c.]
  step 2: 4-point static profile: read before/after filter and before/after coil.
          Hint: The highest single drop tells you where the restriction is.
  Returns to parent flow with: filter / coil / duct / system-wide.
B2. Vacuum Validation sub-flow (injected before any "charge system" action)
  step 1: Enter final micron reading before opening the service valves.   [pass <= 500 microns]
  step 2: Standing decay test, 15 minutes. Enter the rise.   [pass <= 100 microns rise]
  HOLD if > 500 microns or rise > 100: do not charge -- moisture or a leak remains.

================================================================
C. CARD OUTPUTS -- LOW / MODERATE RISK
================================================================
CARD #23 -- Thermostat / Low-Voltage
  CONTRACTOR:  Title: Thermostat / low-voltage fault
               Why:  24V control voltage present but the call is not reaching the equipment.
               Ruled out: Capacitor -- uF within spec.
  HOMEOWNER:   Header: Thermostat / control wiring
               Body:  [Company] checked the low-voltage control side of your system. The reading points to
                      the thermostat or its wiring rather than the outdoor equipment. [Company] has listed
                      the correction below.

CARD #10d -- Compressor Start Components  (the "do not condemn the compressor" card)
  CONTRACTOR:  Title: Compressor start components
               Why:  Compressor starts with a hard-start assist -- start components are the fault, not the
                     compressor itself.
               Ruled out: Grounded/mechanical compressor -- unit starts and runs with the assist.
  HOMEOWNER:   Header: Compressor start parts
               Body:  [Company] found the compressor starts once a start component is assisted. That points
                      to an inexpensive start part rather than the compressor. [Company] has listed the
                      correction below.

CARD #10e -- Crankcase Heater
  CONTRACTOR:  Title: Crankcase heater
               Why:  Crankcase heater open/cold -- refrigerant slugging risk on start.
  HOMEOWNER:   Header: Crankcase heater
               Body:  [Company] found the crankcase heater is not warming the compressor as intended.
                      [Company] has listed the part and correction below.

CARD #15b -- TXV Bulb Loss  [A]
  CONTRACTOR:  Title: Metering valve -- bulb charge loss
               Why:  Superheat near zero -- the metering valve is overfeeding the coil.
               Ruled out: Refrigerant leak -- a leak shows high superheat, not low.
  HOMEOWNER:   Header: Metering valve -- sensing bulb
               Body:  [Company] measured how the metering valve is controlling refrigerant flow. The reading
                      shows the valve is letting too much through. [Company] has listed the correction below.

CARD #15c -- TXV Hunting  [A]
  CONTRACTOR:  Title: Metering valve -- unstable (hunting)
               Why:  Superheat swings widely -- the valve is hunting rather than holding.
  HOMEOWNER:   Header: Metering valve -- unstable
               Body:  [Company] measured the metering valve holding refrigerant flow unevenly. [Company] has
                      listed the correction below.

CARD #15d -- EEV Controller  [A]
  CONTRACTOR:  Title: Electronic metering (EEV) controller
               Why:  Electronic metering valve not responding to its controller.
  HOMEOWNER:   Header: Electronic metering control
               Body:  [Company] checked the electronic metering control and found it is not responding as
                      intended. [Company] has listed the correction below.

================================================================
D. CARD OUTPUTS -- HIGH RISK (expensive recommendation -- Alfred sign-off)
================================================================
Alfred hard rule (applies to all D-cards): SnapAI is never the grammatical subject; the recommendation is
[Company]'s professional judgment, stated as an OPTION; no predictive savings; no "will"; no efficiency %.
For any card that leads to compressor or system replacement, present repair-vs-replace as [Company]'s options,
never as an app directive.

CARD #10a -- Grounded Compressor  [A!]
  CONTRACTOR:  Title: Grounded compressor
               Why:  Winding-to-ground resistance below threshold -- the compressor has an electrical fault
                     to ground.
               Ruled out: Start components -- fault persists with confirmed start parts.
  HOMEOWNER:   Header: Compressor -- electrical fault
               Body:  [Company] tested the compressor's electrical windings and found a fault to ground.
                      [Company] has listed repair and replacement options below; any equipment recommendation
                      reflects [Company]'s professional judgment as a licensed contractor.
               Required note: This assessment is not a certification of equipment condition or performance.
                      Findings require independent verification by your licensed contractor.

CARD #10b -- Mechanical / Locked Rotor  [A!]
  CONTRACTOR:  Title: Compressor -- mechanical / locked rotor
               Why:  Locked-rotor amps with confirmed start components -- internal mechanical fault.
  HOMEOWNER:   Header: Compressor -- mechanical fault
               Body:  [Company] tested the compressor and found it is not turning under power with the start
                      parts confirmed. [Company] has listed repair and replacement options below, reflecting
                      [Company]'s professional judgment.
               Required note: (same Layer 5 note as #10a)

CARD #10c -- Compression Ratio Problem  [A!]
  CONTRACTOR:  Title: Compressor -- internal wear (compression ratio)
               Why:  High discharge with normal subcool and normal charge -- internal valve wear.
               Ruled out: Overcharge -- subcool is normal.
  HOMEOWNER:   Header: Compressor -- internal wear
               Body:  [Company] measured the compressor's pumping performance and found it is not building
                      pressure as intended. [Company] has listed repair and replacement options below,
                      reflecting [Company]'s professional judgment.
               Required note: (same Layer 5 note as #10a)

CARD #20 -- System Under-Airflow   (from v1)
  CONTRACTOR:  Title: System under-airflow
               Why:  Total external static above the design budget -- air moves through the system harder
                     than intended.
               Ruled out: Dirty filter/coil -- highest static drop is not localized there.
  HOMEOWNER:   Header: Airflow assessment
               Body:  [Company] measured the air pressure your system works against. The reading is higher
                      than the range [Company] targets, which means the system is moving air harder than
                      intended. [Company] has listed what they found and the options to improve it below.

CARD #22 -- Latent Capacity Deficit   (from v1)  [A!]
  CONTRACTOR:  Title: Low latent capacity for current conditions
               Why:  Indoor humidity above target while sensible cooling is adequate -- removing heat but not
                     enough moisture.
               Ruled out: Under-airflow -- static within budget. Undercharge -- subcool normal.
  HOMEOWNER:   Header: Humidity assessment
               Body:  [Company] measured the temperature and humidity inside your home. The reading shows
                      indoor humidity above the comfort range [Company] targets, even while the system is
                      cooling. That is what makes rooms feel clammy or sticky. [Company] has noted options
                      below for improving moisture control.
               Banned here: "will keep your home dry", "eliminates humidity", any future-tense outcome.

CARD #24 -- System Oversizing   (from v1)  [A!]  HIGHEST EXPOSURE
  CONTRACTOR:  Title: Suspected system oversizing
               Why:  Short run cycles with static within budget and normal charge -- capacity exceeds the
                     home's load.
               Ruled out: Under-airflow -- static within budget. Overcharge -- subcool normal.
               Gate (hard): No replacement option presented until a Manual J load calc is entered AND two
                     supporting readings are present AND the system age gate is met.
  HOMEOWNER:   Header: Sizing assessment
               Body:  [Company] measured how often your system turns on and off and compared it to the
                      cooling load this home needs. Based on these readings, [Company] believes the system is likely larger than the
                      home requires. Before discussing any options, [Company] recommends a load calculation
                      to confirm. Any equipment recommendation below reflects [Company]'s professional
                      judgment as a licensed contractor.
               Required note: This assessment is not a certification of equipment condition or performance.
                      Findings require independent verification by your licensed contractor.
               Banned here: "you'll save", "your bill will drop", any number tied to future savings, "will".

================================================================
ALFRED SIGN-OFF -- 3 CONDITIONS (must be true before any [A!] string ships)
================================================================
Statutory basis: Texas DTPA, Tex. Bus. & Com. Code ch. 17. Sec 17.46(b) laundry-list
misrepresentations are actionable EVEN IF innocent; Sec 17.50 treble (up to 3x economic damages,
incl. cost of replacement) on knowing/intentional conduct; Sec 17.505 60-day pre-suit notice.
A general disclaimer REDUCES but does NOT waive the DTPA (a Sec 17.42 waiver needs a specific
written, conspicuous form with the consumer represented by counsel -- not available at a service call).
FTC Act Sec 5 + Endorsement Guides (16 CFR 255): a deceptive app output can pull SnapAI in as a party.

C1. #24 Manual J gate ENFORCED IN CODE, not merely displayed. The replacement option must be
    unreachable until (Manual J load calc entered) AND (two supporting readings present) AND
    (system age gate met). If the output can render before the gate, the output IS the misrepresentation.
C2. Layer 4 (inline) + Layer 5 (report) disclaimers must ACTUALLY RENDER on every [A!] surface.
    A specced-but-not-rendered disclaimer is worth nothing.
C3. Attribution tightened on [A!] homeowner bodies -- every conclusion is [Company]'s, never the app's.
    (Applied to #24 in this file; hold the same bar for #10a/b/c/#22 in implementation.)
With C1+C2+C3 met, Alfred signs off the full set. Ceiling ~95%, not 100%. Risk moves on deployment.

================================================================
COMPLIANCE CHECKLIST (run before any string ships)
================================================================
[ ] DEC-088 banned words -> zero in homeowner strings.
[ ] No city / region name in any string.
[ ] No "honest"/"no upsell" self-claim (Gate 1 parked).
[ ] Every homeowner conclusion attributed to [Company]; SnapAI never the subject of "diagnose".
[ ] #24 replacement option gated behind Manual J + two readings + age gate.
[ ] #10a/b/c present repair-vs-replace as [Company]'s options, never an app directive.
[ ] Layer 4 inline disclaimer on all new fault-resolution surfaces; Layer 5 note on #10a/b/c, #22, #24 reports.
[ ] Pre-commit hook extended to scan every new card output string above.
[ ] Alfred individual sign-off on all [A!] cards (Gate 2) before prod.
