# Task: Write Houston HVAC Better-Tier Estimate Copy for 19 Fault Cards

## What you are doing

You are writing two text fields — `description` and `why_recommended` — for the **Better (mid-tier) repair option** for each of 19 HVAC fault cards used in the Houston, Texas market of a contractor app called SnapAI.

This data will be inserted into a PostgreSQL table (`fault_cards`) via a Python/Alembic migration script. You must produce a single Python dictionary at the end that I can drop directly into that script with zero editing.

---

## The three-tier estimate structure

Every fault card has three repair options. You are writing the **middle one (Better)**:

| Tier | Label (age 6–10 yrs) | What it is |
|------|----------------------|------------|
| Good (A) | "Fix Today" | Minimum repair to restore operation |
| **Better (B)** | **"Fix + Prevent Next Failure"** | Fix + one or two add-ons that prevent the most likely follow-on failure |
| Best (C) | "Consider Replacing" or "Full Service" | Comprehensive overhaul or full system replacement |

The Better tier is the **RECOMMENDED** option in the app — it carries a "★ RECOMMENDED" badge. The `why_recommended` field powers a collapsible "Why recommended? ▾" section that only appears on the Better card.

---

## Market context — Houston, Texas

- Climate: Hot-humid Gulf Coast. Summers 95–105°F, high humidity. AC runs 8–9 months/year.
- Primary refrigerant: R-410A (new systems). R-22 in units 10+ years old (phased out, costs $150+/lb).
- Typical installs: Split systems. Many in attics (attic heat = extra stress on equipment).
- Pricing: USD. Typical service call $150–$300. Capacitor $200–$400. Coil clean $250–$500. Compressor $1,500–$3,000+. Full system replacement $6,000–$12,000.
- Customer tone: Direct, value-focused. They want to know the consequence of NOT doing the Better option.
- Do NOT use: Pakistan-specific language, load-shedding, voltage stabilizers, monsoon, Lahore, PKR/Rs, R-32 inverters, or any non-US framing.

---

## Field specs

### `description` field
- What the Better option actually includes (work + parts)
- 1–3 sentences, max **180 characters**
- Start with the primary repair, then add the preventive add-on(s)
- Example pattern: "[Primary fix] plus [preventive add-on]. [Outcome sentence]."

### `why_recommended` field
- WHY Better beats just Good — the failure-cascade argument
- 2–3 sentences, max **180 characters**
- Must explain: what breaks next if you only do the Good fix, the statistical/industry reason, and why doing it now in one visit is cheaper
- Do NOT start with "I" or "We"
- Do NOT repeat the description — explain the logic, not the work

---

## Style guide — match this voice exactly

Read these existing fields from the same table to calibrate your tone:

**Card 1 — Capacitor Failure**
- Good description: "Replace the failed dual-run capacitor. Restart the system and verify proper cooling. Quick fix that gets your AC running again today."
- Good why_recommended: "Your unit is under warranty / under 3 years old. The capacitor is a routine replacement — no need for combo work or upgrades. The simple fix is the right fix."
- Best comp description: "Full electrical service: cap, contactor, disconnect inspection, tighten all terminals, verify 24V control voltage. Eliminates all near-term electrical failures."
- Best comp why: "Pitting visible on the contactor + capacitor failure together = the entire electrical circuit is fatigued. One visit clears all of it. Highest-reliability option for the next 3 [years]."

**Card 5 — Drain Clog**
- Good description: "Clear the condensate drain line with wet/dry vac. Add an algaecide tablet to prevent regrowth. Stops the indoor water leak."
- Good why: "This is the first drain clog this assessment cycle. Simple flush works. The algaecide tablet handles biological regrowth for the next season."
- Best comp description: "Full drain system rebuild: new PVC drain line, P-trap, drain pan safety switch, dual coil clean, UV light installation to prevent biological regrowth."
- Best comp why: "Recurring drain clogs (2+ in 12 months) signal a deeper problem — corroded P-trap, dirty coil, or attic-mount slope issue. Rebuilding the system once costs less than three [separate calls]."

**Card 10 — Compressor Failure**
- Good description: "Replace the failed compressor. Recover existing refrigerant, install new compressor, pressure-test the line set, recharge to spec, and verify cooling."
- Good why: "Under-warranty unit (compressor covered). Standard swap with new dryer. Don't pay for combo upgrades or replacement when manufacturer covers the part."

The voice is: **confident, technical, contractor-to-homeowner, no fluff, consequence-driven.**

---

## The 19 cards — full existing data

Below is EVERY field already in the database for each card. Use Good and Best copy as context to write Better copy that fits logically in the middle.

```
Card 1 — Capacitor Failure
  description_good: "Replace the failed dual-run capacitor. Restart the system and verify proper cooling. Quick fix that gets your AC running again today."
  why_recommended_good: "Your unit is under warranty / under 3 years old. The capacitor is a routine replacement — no need for combo work or upgrades. The simple fix is the right fix."
  description_best_comprehensive: "Full electrical service: cap, contactor, disconnect inspection, tighten all terminals, verify 24V control voltage. Eliminates all near-term electrical failures."
  why_recommended_best_comprehensive: "Pitting visible on the contactor + capacitor failure together = the entire electrical circuit is fatigued. One visit clears all of it. Highest-reliability option for the next 3 years."
  description_best_replacement: "At [N] years old, complete system replacement eliminates near-term repair risk and reduces electricity costs by 30-40%. New 10-year manufacturer warranty included."
  why_recommended_best_replacement: "Capacitor failure on a 8+ year unit signals the rest of the electrical and refrigerant circuits are nearing end-of-life. Replacement now beats $200-500 yearly repairs through year 12+."

Card 2 — Dirty Filter
  description_good: "Replace the air filter. Restores proper airflow, prevents coil freeze, and improves cooling efficiency."
  why_recommended_good: "Filter is the only thing flagged in the diagnostic. No secondary issues found. Quick replace + tech leaves you with a 90-day reminder for the next change."
  description_best_comprehensive: "Filter + dual coil cleaning + drain flush + new programmable thermostat. Sets a clean baseline for the next 12 months of operation."
  why_recommended_best_comprehensive: "Diagnostic flagged the filter PLUS coil discoloration or drain biological growth. Addressing all three in one visit costs less than three separate service calls and resets the maintenance clock."
  description_best_replacement: "At [N] years old, complete system replacement eliminates near-term repair risk and reduces electricity costs by 30-40%. New 10-year manufacturer warranty included."
  why_recommended_best_replacement: "Filter-related issues on an 8+ year unit usually mean the indoor coil has been running dirty for years, reducing efficiency by 15-25%. Replacement recovers that efficiency permanently."

Card 3 — Contactor Failure
  description_good: "Replace the failed contactor. Restores power to the outdoor compressor and condenser fan. System cooling restored today."
  why_recommended_good: "Unit is under warranty / under 3 years old. Contactor wear at this age is unusual — replace it and the capacitor is likely still healthy. No combo work needed."
  description_best_comprehensive: "Complete electrical refresh: contactor, capacitor, control transformer test, low-voltage wiring inspection, breaker check. Done in one visit, no follow-up needed."
  why_recommended_best_comprehensive: "Pitted contactor + heat damage at the panel suggests multiple stressed connections. Full electrical refresh prevents the next 2-3 failure callouts and resets the panel for years."
  description_best_replacement: "At [N] years old, complete system replacement eliminates near-term repair risk and reduces electricity costs by 30-40%. New 10-year manufacturer warranty included."
  why_recommended_best_replacement: "Contactor failure on an 8+ year unit means the compressor's startup cycles are stressed. Compressor will likely follow within 12-24 months. Replacement now avoids the bigger bill."

Card 4 — Blower Motor Failure
  description_good: "Replace the failed indoor blower motor. Restores airflow through the supply ducts and resolves the no-cooling complaint."
  why_recommended_good: "Unit is under warranty / motor is the only flagged component. Capacitor reading is healthy. Standard motor swap — no combo work or ECM upgrade needed at this age."
  description_best_comprehensive: "Replace motor with high-efficiency ECM (variable speed), upgrade capacitor, balance airflow per room. ~15-20% lower electric bill from improved blower efficiency."
  why_recommended_best_comprehensive: "Tech noted bearing noise OR uneven airflow during diagnostic. ECM upgrade fixes both, plus delivers measurable bill savings. Best value when the system itself is otherwise in good shape."
  description_best_replacement: "At [N] years old, complete system replacement eliminates near-term repair risk and reduces electricity costs by 30-40%. New 10-year manufacturer warranty included."
  why_recommended_best_replacement: "Blower motor on 8+ year unit shows the air handler is at end-of-life. Outdoor unit is likely similar age. Replacing both as a matched set restores efficiency and warranty across the whole system."

Card 5 — Drain Clog
  description_good: "Clear the condensate drain line with wet/dry vac. Add an algaecide tablet to prevent regrowth. Stops the indoor water leak."
  why_recommended_good: "This is the first drain clog this assessment cycle. Simple flush works. The algaecide tablet handles biological regrowth for the next season. No need for the safety switch on a first clog."
  description_best_comprehensive: "Full drain system rebuild: new PVC drain line, P-trap, drain pan safety switch, dual coil clean, UV light installation to prevent biological regrowth."
  why_recommended_best_comprehensive: "Recurring drain clogs (2+ in 12 months) signal a deeper problem — corroded P-trap, dirty coil, or attic-mount slope issue. Rebuilding the system once costs less than three separate service calls."
  description_best_replacement: "At [N] years old, complete system replacement eliminates near-term repair risk and reduces electricity costs by 30-40%. New 10-year manufacturer warranty included."
  why_recommended_best_replacement: "Drain clogs on 8+ year units often indicate the coil is biologically fouled beyond cleaning. New equipment + UV light gives you a clean slate that lasts the next decade."

Card 6 — Wiring Fault
  description_good: "Locate and repair the faulty wiring. Test all connections and restore power to the affected component."
  why_recommended_good: "Tech identified a single damaged conductor with no evidence of multi-point stress. Simple repair restores power. Adjacent terminals checked and clean — no escalation needed."
  description_best_comprehensive: "Complete electrical overhaul: replace damaged wiring sections, all terminal lugs, upgrade to anti-corrosion connectors, label every conductor."
  why_recommended_best_comprehensive: "Multiple stressed terminals + visible heat damage at the panel = the entire electrical chassis is at risk. Full overhaul is more expensive but ends the failure cycle for the life of the unit."
  description_best_replacement: "At [N] years old, complete system replacement eliminates near-term repair risk and reduces electricity costs by 30-40%. New 10-year manufacturer warranty included."
  why_recommended_best_replacement: "Widespread wiring damage on an 8+ year unit means the entire electrical chassis is approaching end-of-life. Replacement gives you new wiring, new warranty, fresh start."

Card 7 — Control Board / Error Code
  description_good: "Replace the failed control board. Restores system communication, clears the error code, and resumes normal operation."
  why_recommended_good: "Single error code, no thermostat compatibility issues, recent firmware. Board swap and clear is the correct fix at this age. No need to upgrade other components."
  description_best_comprehensive: "Replace board, upgrade to smart thermostat, verify communication on all zones, update firmware where available. Future-proofs the system for 5+ years."
  why_recommended_best_comprehensive: "Board failure plus an old thermostat plus zoning means three integration points at risk. Upgrading them together restores compatibility for the long term and unlocks scheduling and remote diagnostics."
  description_best_replacement: "At [N] years old, complete system replacement eliminates near-term repair risk and reduces electricity costs by 30-40%. New 10-year manufacturer warranty included."
  why_recommended_best_replacement: "Control board failure on an 8+ year unit indicates outdated electronics across the system. New equipment ships with modern boards, full warranty, and current communication protocols."

Card 8 — Refrigerant Leak
  description_good: "Find the leak with UV dye, seal it, recover and recharge the refrigerant. Verify cooling performance returns to manufacturer spec."
  why_recommended_good: "Leak located at a serviceable joint (not the coil or TXV). Standard seal-and-recharge holds. Unit is young enough that the rest of the refrigerant circuit is healthy."
  description_best_comprehensive: "Leak seal + TXV replacement + filter dryer change + full nitrogen pressure test + UV dye injection. Eliminates the leak-source ambiguity for the long term."
  why_recommended_best_comprehensive: "Multiple findings (TXV corrosion + line wear + biological growth in drain) point to refrigerant circuit aging. Comprehensive service resets the circuit so future leaks are easy to find."
  description_best_replacement: "At [N] years old, complete system replacement eliminates near-term repair risk and reduces electricity costs by 30-40%. New 10-year manufacturer warranty included."
  why_recommended_best_replacement: "Refrigerant leak on a 10+ year R-22 unit (R-22 has been phased out, costs $150+/lb). Replacement to R-410A or R-454B eliminates the cost-of-recharge problem entirely."

Card 9 — Coil Freeze
  description_good: "Replace the dirty filter, thaw the coil, and clean the evaporator. Restores airflow and prevents the coil from refreezing in the next few hours."
  why_recommended_good: "Single cause confirmed: dirty filter + dirty indoor coil. Refrigerant pressure is within spec post-thaw. Standard cleaning fully resolves — no need for combo or replacement."
  description_best_comprehensive: "Full thaw + coil cleaning + refrigerant top-up to spec + new high-MERV filter + drain flush. The system runs at design conditions for the rest of the season."
  why_recommended_best_comprehensive: "Diagnostic flagged filter + coil fouling + low charge together = the entire indoor heat-transfer path is degraded. Comprehensive reset restores design efficiency for the rest of the season."
  description_best_replacement: "At [N] years old, complete system replacement eliminates near-term repair risk and reduces electricity costs by 30-40%. New 10-year manufacturer warranty included."
  why_recommended_best_replacement: "Repeated coil freezes on a 10+ year unit signal compressor wear, evaporator restriction, or both. Replacement avoids the cascade of $400-800 repair calls that typically follow."

Card 10 — Compressor Failure
  description_good: "Replace the failed compressor. Recover existing refrigerant, install new compressor, pressure-test the line set, recharge to spec, and verify cooling."
  why_recommended_good: "Under-warranty unit (compressor covered). Standard swap with new dryer. Don't pay for combo upgrades or replacement when manufacturer covers the part."
  description_best_comprehensive: "Compressor + new TXV + filter dryer + nitrogen test + full evacuation and weighed recharge. Resets the entire refrigerant circuit for new-equipment-equivalent reliability."
  why_recommended_best_comprehensive: "Compressor failure on a younger unit (under 8 years) where AI confirms multiple refrigerant-circuit findings. Comprehensive rebuild costs less than full replacement and preserves remaining warranty."
  description_best_replacement: "At [N] years old, full system replacement eliminates near-term repair risk and reduces electricity costs by 30-40%. New 10-year manufacturer warranty included."
  why_recommended_best_replacement: "Compressor failure on an 8+ year unit is the industry-standard trigger for full system replacement. The remaining components are aging on the same clock. Replacement now stops the repair cycle."

Card 11 — Ignitor / Flame Sensor (Gas Furnace)
  description_good: "Replace the hot surface ignitor and flame sensor. Restores ignition sequence and clears the no-heat complaint."
  why_recommended_good: "Diagnostic confirmed sensor-only failure with clean burners and recent service history. Cleaning the sensor (or simple swap) is the right step — no combo work needed at this age."
  description_best_comprehensive: "Full combustion system service: new ignitor, flame sensor, burner cleaning, heat exchanger inspection, gas pressure verification, draft inducer check."
  why_recommended_best_comprehensive: "Multiple combustion findings (dirty burners + cracked heat exchanger risk + uneven flame) indicate the entire combustion side needs attention. One-visit comprehensive service prevents CO risk."
  description_best_replacement: "At [N] years old, full system replacement eliminates near-term repair risk and reduces electricity costs by 30-40%. New 10-year manufacturer warranty included."
  why_recommended_best_replacement: "Heat exchanger cracks or repeated combustion failures on a 10+ year furnace are CO safety issues. Replacement is the only path that fully eliminates the carbon-monoxide risk for the household."

Card 12 — Reversing Valve (Heat Pump)
  description_good: "Replace the failed reversing valve. Recover refrigerant, swap valve, recharge, and verify both heating and cooling modes are working properly."
  why_recommended_good: "Single component failure on a younger unit with clean refrigerant readings. Standard swap restores both modes. No need for combo work at this age and condition."
  description_best_comprehensive: "Full heat pump tune: reversing valve + filter dryer + defrost board test + supplemental heat verification. Restores full year-round heating capability."
  why_recommended_best_comprehensive: "Reversing valve + defrost board issues + uneven supplemental heat = the entire heat-pump system needs review. One-visit comprehensive tune-up restores full operation for both modes."
  description_best_replacement: "At [N] years old, full system replacement eliminates near-term repair risk and reduces electricity costs by 30-40%. New 10-year manufacturer warranty included."
  why_recommended_best_replacement: "Reversing valve failure on a 10+ year heat pump suggests the entire refrigerant circuit is aging. Replacement with a modern variable-speed heat pump unlocks 25-35% additional efficiency."

Card 13 — Ductwork Leak
  description_good: "Seal the duct leak with mastic and reinforce with foil tape. Restores delivered airflow to the affected rooms."
  why_recommended_good: "Single visible leak at an accessible joint. Sealing alone restores delivered airflow to the affected room. No pressure test needed for one isolated finding."
  description_best_comprehensive: "Full duct rebuild for the affected zone: new R-8 insulated flex duct, sealed plenum connections, balanced static pressure, mastic at every joint."
  why_recommended_best_comprehensive: "Attic ductwork is undersized, corroded, OR insulation is compromised. Full zone rebuild costs more upfront but delivers measurable airflow + bill savings every month for the life of the system."
  description_best_replacement: "At [N] years old, full system + duct replacement eliminates near-term repair risk and reduces electricity costs by 30-40%. New 10-year manufacturer warranty included."
  why_recommended_best_replacement: "Ductwork age matches HVAC age. Old leaky ducts on a tired unit means you are paying double to cool the attic. Coordinated replacement (system + ducts) is the maximum-savings path."

Card 14 — Dirty Condenser/Evaporator Coil
  description_good: "Clean the dirty coil with chemical foam. Restores heat transfer and lowers high-pressure trips on hot days."
  why_recommended_good: "Single dirty coil identified, other coil clean, refrigerant readings normal. Standard chemical clean fully resolves. No need for combo cleaning or full system service."
  description_best_comprehensive: "Full coil restoration: chemical clean both coils, comb straightening, fin straightener pass, coat with corrosion protectant, recharge to spec."
  why_recommended_best_comprehensive: "Both coils fouled + bent fins + low charge = the heat-transfer surfaces are at end-of-effectiveness. Full restoration is the last service that meaningfully improves performance before replacement."
  description_best_replacement: "At [N] years old, full system replacement eliminates near-term repair risk and reduces electricity costs by 30-40%. New 10-year manufacturer warranty included."
  why_recommended_best_replacement: "Severe coil fouling + 10+ year age = corrosion is irreversible at the fin level. Cleaning recovers 60-70% of original capacity at best. Replacement recovers 100% and adds modern efficiency."

Card 15 — Fixed Orifice / Piston Mismatch
  description_good: "Replace the incorrect fixed orifice piston with the correctly-sized one for this unit. Recovers full cooling capacity."
  why_recommended_good: "Mismatch found during diagnostic — likely a substitution from a prior service. Correct piston restores design performance. Standard fix on a young unit, no upgrade needed."
  description_best_comprehensive: "Full metering device upgrade: TXV + new filter dryer + nitrogen pressure test + complete recharge. Sets the system up for accurate cooling for 10+ years."
  why_recommended_best_comprehensive: "Mismatch + refrigerant contamination + degraded dryer = the entire metering and filter side needs replacement. One-visit comprehensive service restores design accuracy permanently."
  description_best_replacement: "At [N] years old, full system replacement eliminates near-term repair risk and reduces electricity costs by 30-40%. New 10-year manufacturer warranty included."
  why_recommended_best_replacement: "Piston mismatch + 10+ year age + R-22 phase-out = converting to modern refrigerant + matched components is more cost-effective than spot fixes."

Card 16 — Loose Terminal
  description_good: "Clean and retorque the loose electrical terminal. Stops arcing and prevents the component from failing due to voltage drop at the connection."
  why_recommended_good: "Single terminal identified, no heat damage at adjacent connections, electrical chassis otherwise healthy. Retorque and clean = full fix. No panel-wide work needed at this age."
  description_best_comprehensive: "Complete panel rework: re-lug every connection, replace heat-damaged wire sections, install anti-corrosion compound, label every conductor for the next tech."
  why_recommended_best_comprehensive: "Multiple heat-damaged terminals + corrosion on connections + worn lugs = the electrical chassis itself is fatigued. Full rework is more expensive but the only path to long-term reliability."
  description_best_replacement: "At [N] years old, full system replacement eliminates near-term repair risk and reduces electricity costs by 30-40%. New 10-year manufacturer warranty included."
  why_recommended_best_replacement: "Widespread terminal damage on an 8+ year unit means the entire electrical infrastructure is at end-of-life. New equipment ships with fresh wiring, modern connectors, full warranty."

Card 17 — Refrigerant Overcharge
  description_good: "Recover excess refrigerant to bring the system back to manufacturer spec. Verify cooling performance returns and discharge pressure drops."
  why_recommended_good: "Single overcharge identified, no system damage from the overcharge, refrigerant lines and TXV are healthy. Recovery alone fully resolves. No need for scale install at this age."
  description_best_comprehensive: "Full refrigerant recovery, system evacuation, weighed recharge to nameplate spec, leak check, performance verification. System reset to factory baseline."
  why_recommended_best_comprehensive: "Overcharge plus TXV hunting plus inconsistent superheat readings = the refrigerant circuit needs a clean reset. Full recovery and reweighed charge restores factory performance for years."
  description_best_replacement: "At [N] years old, full system replacement eliminates near-term repair risk and reduces electricity costs by 30-40%. New 10-year manufacturer warranty included."
  why_recommended_best_replacement: "Chronic overcharge problems on a 10+ year R-22 unit signal multiple service histories of bad practice. Replacement to R-410A with modern controls eliminates the failure pattern."

Card 18 — System Undersizing
  description_good: "Inform homeowner: the installed unit is undersized for the cooling load. No repair recovers this — full replacement is needed."
  why_recommended_good: "Tier A is not applicable for system undersizing. The diagnostic is for record-keeping only — flag the issue and consult on replacement timing in Better or Best tiers."
  description_best_comprehensive: "Tier C comprehensive repair not applicable — undersizing cannot be addressed without full replacement."
  why_recommended_best_comprehensive: "Not applicable for this card. System undersizing has no comprehensive-repair path — only full replacement."
  description_best_replacement: "Full replacement with correctly-sized high-efficiency system. Includes Manual J calculation, ductwork verification, and warranty registration."
  why_recommended_best_replacement: "Undersized systems run constantly during peak heat, dramatically reducing component life and driving 40-60% higher cooling bills. Right-sized replacement is the only fix."

Card 19 — Formicary Corrosion
  description_good: "Replace the corroded evaporator coil. Standard repair for formicary corrosion — coatings don't prevent it long term."
  why_recommended_good: "Tier A is unusual for formicary — typically Better or Best wins. If Good is recommended, it is because the coil is the only finding AND indoor air conditions cannot be changed."
  description_best_comprehensive: "Replace evaporator + UV dye + indoor air quality assessment. If VOC levels are high, recommend ventilation upgrade — prevents formicary recurrence."
  why_recommended_best_comprehensive: "Formicary on a younger unit with high VOC indoor air. Coil-only replacement guarantees recurrence. Pairing with ventilation upgrade addresses the root cause and protects the new coil."
  description_best_replacement: "At [N] years old, full system replacement eliminates near-term repair risk and reduces electricity costs by 30-40%. New 10-year manufacturer warranty included."
  why_recommended_best_replacement: "Formicary on an 8+ year unit + aged outdoor unit = the entire refrigerant circuit is at end-of-life. Replacement with a modern micro-channel coil resistant to formicary is the only permanent fix."
```

---

## Hard constraints — do not violate any of these

1. **Max 180 characters per field** — count carefully. Truncate at a word boundary if needed. No ellipsis.
2. **No Pakistan references** — no monsoon, load-shedding, voltage stabilizers, Rs., PKR, R-32 inverters, Lahore, Karachi, or any non-US framing.
3. **No first-person** — never start `description` or `why_recommended` with "I" or "We".
4. **Escape single quotes** — any apostrophe in the Python string must be escaped as `\'` since strings will use single quotes.
5. **`why_recommended` must be consequence-driven** — it must state what breaks next or what it costs NOT to do Better. Pure feature descriptions are rejected.
6. **Card 18 (System Undersizing)** — the Better tier for this card describes doing a **Manual J load calculation and BTU sizing survey** before committing to replacement. It is NOT another repair option.
7. **Do not invent card names** — use only the 19 cards listed above.
8. **No trailing spaces** — clean strings only.

---

## Output format — exact

Produce a single Python dictionary. No prose before or after it. No markdown fence. Just the dict, starting with `{` and ending with `}`.

The dictionary must match this exact structure:

```python
{
    1: {
        "description": "...",
        "why_recommended": "...",
    },
    2: {
        "description": "...",
        "why_recommended": "...",
    },
    # ... through 19
}
```

Keys are integers (1 through 19, matching card_id). Each value is a dict with exactly two keys: `"description"` and `"why_recommended"`. All string values use single quotes.

---

## How this dict will be used (for your context only — do not include in output)

The output will be inserted into an Alembic migration script that runs:

```python
for card_id, patch in _CARDS.items():
    j = json.dumps(patch, ensure_ascii=False).replace("'", "''")
    op.execute(
        f"UPDATE fault_cards "
        f"SET better_option_estimate = COALESCE(better_option_estimate, '{{}}'::jsonb) || '{j}'::jsonb "
        f"WHERE card_id = {card_id}"
    )
```

So the values will be JSON-serialised and merged into the existing `better_option_estimate` JSONB column. The Good, Best-comp, and Best-replacement fields already exist — you are adding only `description` and `why_recommended` (the Better tier fields).

---

## Verify before submitting

Before outputting the dict, for every card silently check:
- [ ] `description` ≤ 180 chars
- [ ] `why_recommended` ≤ 180 chars
- [ ] No Pakistan/non-US language
- [ ] `why_recommended` states a consequence or cost of NOT doing Better
- [ ] Single quotes escaped as `\'` where needed
- [ ] Card 18 Better = sizing survey, not repair
- [ ] All 19 cards present (1–19)

Only output the dict after all checks pass.
