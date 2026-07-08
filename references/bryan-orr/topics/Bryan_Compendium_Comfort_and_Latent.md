# Bryan Orr HVAC School - Compendium: Comfort and Latent

**Version:** v1.0  
**Date:** 2026-07-08  
**Source episodes:** 63 (of 959 total in corpus)  
**Cross-references (most co-occurring topics):** Diagnostics Methodology (36), Airflow (36), Business and Trade (17), Tools and Instruments (9), Refrigeration Cycle (7), Combustion and HX (5)

**Attribution:** Synthesized from Bryan Orr's public HVAC School podcast for SnapAI internal reference only. Attribute Bryan Orr / HVAC School (hvacrschool.com) in any downstream use; do not imply endorsement.

---

## Overview - scope of Bryan's teaching on this topic

This compendium aggregates 63 episodes whose primary emphasis is **Comfort and Latent**. Content is extracted verbatim-faithful from the transcripts; every item cites its source episode by title and YouTube video id. No numbers or claims were invented at merge time.

Dominant secondary threads in this bucket: Diagnostics Methodology (36), Airflow (36), Business and Trade (17), Tools and Instruments (9), Refrigeration Cycle (7), Combustion and HX (5), Guest Wisdom (4), Electrical and Controls (4).

## Key technical points (Bryan's core teaching, by episode)

### (Podcast) Drying Stuff vs. Drying Air - Humidification, Dehumidification, and Ventilation  
*Source id: R77L6dsEE50*

- First decide whether you're drying AIR (dehumidification/comfort) or drying STUFF (a wet material) - confusing the two causes most humidity confusion. Water constantly moves both ways between air and materials.
- Absolute humidity does NOT stay constant with temperature in a house (contrary to the engineering assumption): in a house full of absorptive materials a small dry-bulb rise pulls a lot of moisture out of stuff (e.g. 70F to 80F can move dew point from ~45F to ~65F).
- To dry air, target the source: in a residence the biggest source is COOKING (long duration), more than showers - exhaust at the source. The steady load is ventilation air; in most climates you must remove 3-5x more moisture (latent) than sensible heat from incoming ventilation air, yet nothing dries ventilation air by code.
- To dry stuff: 'get the heat in to get the moisture out' (add thermal energy to mobilize water), supply dry air moved gently across the surface (not too fast, or you crack wood); mobilized moisture goes everywhere but STAYS in the cold places (less energy there to keep it airborne).

### (Podcast) Psychrometrics for Fun and Profit w⧸ Jamie Kitchen  
*Source id: ULg2hC4trUc*

- Humidity is energy in the air - water vapor is essentially steam (same tables). Warmer air holds exponentially more moisture and latent energy, so on a hot day the moisture energy runs nearly off the chart.
- Moist air is LIGHTER (less dense) than dry air but contains MORE heat energy - dispelling the 'heavy humid air' myth; treating density backwards leads to misunderstanding the air equations.
- Master the scales: dry bulb (temperature), wet bulb (evaporation/body-cooling effectiveness; equals dry bulb at 100% RH, and the wet-bulb depression indicates humidity), relative humidity (a ratio that changes with temperature at constant moisture), absolute moisture (grains, 7000/lb), and dew point (where moisture condenses, fixed for a given grains regardless of starting temperature; grains and dew point line up on the right side of the chart).
- Apparatus dew point: dew point sets the evaporator coil temperature needed to dehumidify. To pull MORE moisture use a colder coil and lower air velocity (air dwells longer, lower bypass factor); for sensible-only cooling use higher velocity and a warmer coil. Variable fan/compressor speed lets you tailor latent vs sensible.

### A Duct Moisture Problem Diagnosis (Short)  
*Source id: NtMoOU5fQu4*

- Mold/growth on duct joints in an interior closet is caused by a cold duct surface exposed to warm, dusty, humid attic air condensing on it.
- The fix is to replace the affected duct/flue piece and seal any gap to the attic so warm humid air can't reach the cold surface.

### A Few Condensate Considerations  
*Source id: -JSdAMuwbig*

- The evaporator/blower puts the drain on negative pressure ('the drain sucks'), so the trap must have enough water column to overcome the system's negative static or it will suck the trap dry; use a proper P-trap.
- When water reaches the float switch, find WHY (double trap, platform sag, high static, or a mis-reconfigured horizontal pan) - just re-leveling the float only hides the symptom.
- Maintain 1/4 inch per foot of fall on horizontal drains, brace at least every 4 feet, and run the float switch to the platform top rather than relying on pan level.

### A Walk Through the Residential Design Series (ACCA Manuals J, S, and D) with Ed Janowiak  
*Source id: qRhSAfirHJE*

- The ACCA residential design series is the 'math of HVAC': Manual J (load - BTUs in/out), Manual S (equipment/coil/airflow selection), Manual D (duct design), Manual T (register selection); follow ALL the rules to get 'predictable results'.
- Define comfort with numbers (70F winter design; 75F/50% RH = ~62-63F wet bulb indoor summer) and design to the 99%/1% temperatures, not worst case; don't oversize AC because a bigger unit runs less and removes less humidity at part load.
- Select equipment on expanded performance data (sensible and latent BTUs), not nominal tons - meet the sensible, meet the latent, and don't exceed total by 15% (single-stage), 20% (two-stage), or 30% (VRF/inverter).

### Advanced Ventilation w⧸ CERV2  
*Source id: 5lyiz-YjwmQ*

- The CERV (smart ventilation) senses CO2 and VOCs and actively manages fresh air, using a small inverter heat pump (instead of an ERV core) to decouple the two airstreams - conditioning incoming air (dehumidifying/cooling in summer, heating in winter) and recirculating to even out air quality and remove particulates.
- Smart ventilation is more energy efficient because it doesn't blindly exchange energy or bring in outside air when it's disadvantageous (e.g. bypass at 2-6am, or don't add humid outside air) - you cannot SMELL healthy air, so odor-based ASHRAE 62.1/62.2 standards (from 1930s Yale sniff tests) are inadequate.
- Micro-channel + ultra-low charge (~134a here) makes the heat pump 'bulletproof' - no defrost/sump heaters, inherently protected from slugging/oil foaming; you can let the coil freeze and pass liquid to the compressor without harm.

### Changing a Drain Pan the Easier Way  
*Source id: qytos4XIlPE*

- You can clean or replace a drain pan without pumping the system down or pulling the coil: remove the front (and sometimes rear) screws, lift the coil a couple inches, and snake clear condensate-pump tubing underneath to vacuum the pan clean.

### Cleaning Best Practices： Condensate Drain Lines and Pans  
*Source id: cqCjZ8Lnwuo*

- There is no single silver-bullet drain-cleaning strategy; forcing water through at a reasonable flow rate is one of the best methods. Be responsible for how clean the drain is AT the unit - you can't control downstream.
- Clean the drain until it is actually clean; standing water in an out-of-level pan is the fastest way to grow biofilm, so proper leveling matters as much as cleaning.
- All-aluminum coils grow 'bacterial zoogleal' (elephant snot) because aluminum releases no ions to inhibit bacteria; 15% silver rods (silver + copper) in the drain pan are a preventative that lasts the life of the unit.
- Seal the cabinet penetrations ('straws') so a negatively-pressurized cabinet doesn't suck in outside moist air that hits dew point and condenses/molds inside the unit.

### Cleaning a Difficult AC Condensate Drain  
*Source id: ttfXcWIOHmM*

- All-aluminum coils produce a white sludge that builds up quickly in drain lines; the industry doesn't fully understand the cause.
- Don't just follow a single procedure - keep cleaning the drain line until you can tell it's actually clean. Even cleaning every six months, inattention can leave the line badly backed up.

### Condensating Vents： Q&A with Bryan Orr  
*Source id: gjFb7u7LD-g*

- Condensation around supply registers is driven by the dew point of the air and the surface temperature of the surface, not simply 'where hot meets cold'; first determine whether the moisture sources from the attic (high dew point) or from the space.
- Solve these by controlling moisture, not by chasing one spot: seal and dehumidify the attic if the source is the attic, hermetically seal boots/cans, and control indoor humidity by running equipment long at a low evaporator temperature.
- Water vapor is lighter than air and rises, so dew points are higher near the ceiling - another reason vents sweat and why whole-structure sealing beats spot fixes.

### Copeland's Revolutionary Liquid Desiccant Technology ｜ HVAC School at AHR 2025  
*Source id: WeUL1D1UQdI*

- Liquid desiccant in a modular block does the same moisture-grabbing work as a solid desiccant wheel but has no moving parts (no belt, chain, rollers, rotation).
- A highly engineered hydrophobic membrane keeps the desiccant out of the airstream (closed loop) while letting only water vapor pass, so it can't contaminate supply air or disintegrate into it.
- Regeneration still happens: concentrated desiccant is piped to a regenerator with a water/glycol circuit (~60F cold side, ~120-140F hot side) that can use waste heat.

### Customers Buy Comfort—Why Matt Risinger Uses Dehumidification in his Homes  
*Source id: bHG2e1XGG5E*

- Right-sizing equipment alone does not control humidity; even perfectly matched equipment forces a sensible-vs-latent dance, and VRF 'dry mode' does not truly control humidity.
- Controlling humidity independently with a standalone dehumidifier lets you keep a higher thermostat setpoint and stay comfortable (solving the husband/wife thermostat conflict).
- Have the comfort talk during a system replacement and sell the dehumidifier as an inexpensive add-on relative to the whole-system cost; also frames the IAQ/health angle.

### DUCTLESS Control and Humidity Hack with Cielo Breez  
*Source id: oF1T5EH_xWg*

- The Cielo Breez sends IR signals to ductless equipment and can switch modes and set temperature more easily than the stock remote.
- Ductless dry mode dehumidifies well but doesn't let you control humidity or temperature directly; the Breez's built-in humidity sensor doesn't directly set humidity in dry mode either.
- Using the e-saver 'my rules' feature you can trigger the equipment on humidity or temperature (e.g. above 72F power on in dry mode with low airflow), giving indirect humidity-based control.

### Dedicated Outdoor Air System (DOAS) 101 with Roman Baugh  
*Source id: 7ThhG_bDPtc*

- A DOAS brings in 100% outdoor air (no return duct), overcools with 2-3 coils to wring out humidity, then reheats to a neutral ~70-72F discharge so it treats ventilation air without overcooling the space.
- The digital/unloader (Copeland) compressor varies capacity by redirecting discharge gas back to suction over a ~15-second cycle; you can time the on/off to estimate capacity demand.
- Hot-gas reheat modulating valves are wired reverse-mirrored so one drives open as the other drives closed; a stuck valve gives high-pressure faults.

### Dehumidification Hootenanny w⧸ Chris Conway, Dustin Cole, Tim De Stasio, Chris Hughes, Nikki Krueger  
*Source id: FhZt9xa22AI*

- A whole-house dehumidifier is an air conditioner in a box focused on a very cold coil (near freezing) to remove maximum water, integrated with the ductwork but dehumidifying independent of the AC.
- Higher-SEER equipment usually removes less water (higher sensible heat ratio); since the AC runs at design load only ~1% of the year, partial-load and shoulder seasons need dedicated dehumidification.
- Size by pints at real design conditions (not square footage), watch derating from temperature and static pressure, and treat/filter fresh ventilation air before delivering it.

### Do Furnaces Dry Out The Air？  
*Source id: S9N14YBE2Ok*

- Heating air does not change the absolute moisture content (pounds/grains); it only lowers relative humidity by raising the temperature and the air's saturation capacity.
- A furnace does not burn or directly dry the air; the dry feeling comes from the low relative humidity that heating produces.
- Forced-air/oversized systems tend to feel drier because they move more air, run higher static, and pull in dry outdoor air through leaky ducts and non-sealed combustion, not because the furnace removes moisture.

### Drain Planning and Fabrication  
*Source id: oBb3E7qQh8c*

- Plan the drain first: end location must satisfy customer and code, avoid slip hazards (algae on concrete months later) and avoid staining/pooling water against the structure.
- Every drain needs at least one trap; add a trap with a vent (vent above the pan level) to avoid double-trapping when the existing line already traps through walls/attic, and put the drain on the correct primary port (elevated/bridged) for the application.
- Modern aluminum coils no longer keep the drain clean like old copper coils, and new higher-efficiency equipment moves more condensate, so drains have become the most common post-install callback in Florida - disclose this to the homeowner up front.

### Healthy Air & Your Home (Homeowner Education)  
*Source id: RVOT6s6bjkg*

- Store chemical cleaners (VOC sources like bleach/chlorine) outside the home, ideally in a separate structure or at least the garage, away from spills and from pets/children.
- Code-required UL-listed CO detectors only alarm at very high levels (~400 ppm), so also install a low-level CO detector (e.g. Defender brand) because chronic low-level CO exposure can cause respiratory issues like asthma; CO (carbon monoxide, poisonous, odorless) is completely different from CO2 (carbon dioxide, exhaled naturally).
- For particulates, filter well and change filters regularly: start with a good MERV-8 pleated filter and change it monthly, but higher MERV/greater surface area is better as long as you don't choke the equipment's airflow; exhaust kitchen and bath moisture and cooking contaminants OUTSIDE, not with recirculating hoods.

### Healthy Housing Principals for HVAC Contractors w⧸ Joe Medosch  
*Source id: bxxjx7aSYYQ*

- Healthy homes is the HVAC contractor's next frontier (like heat pumps 25 years ago): BPI's new Healthy Housing Principles reference guide is built on 8 HUD-derived fundamentals - keep a home clean, dry, pest-free, contaminant-free, safe, ventilated, maintained, and comfortable - and most already overlap what techs do.
- You are the biggest health influence in the home (per Joseph Allen, whoever controls heating/cooling determines sick days and health more than the doctor): people take ~20,000 breaths a day (~30,000 gallons/day), and in a leaky house that air comes through the walls/attic/crawlspace, so infiltration is a CONTAMINANT PATHWAY, not just an energy penalty.
- Particulates are the key issue: PM10 vs PM2.5 (25x smaller than a hair) down to PM1 and PM0.3 (behaves almost like a gas) penetrate progressively deeper - PM2.5 and smaller diffuse through the alveoli into the bloodstream and reach the brain, heart and immune system.

### Heat and Comfort Basics 3D  
*Source id: zVEkVL36Ni4*

- Heat moves into/out of a home three ways: conduction (direct molecular contact, opposed by R-value insulation), convection (heat carried by moving air/fluid, i.e. infiltration/exfiltration), and radiation (electromagnetic waves, line of sight).
- Sensible heat can be measured with a thermometer; latent heat cannot, because the energy goes into a phase change rather than a temperature change.
- To dehumidify, the evaporator coil must be below the dew point of the air passing over it; the colder the coil, the more moisture it removes, and moisture is only removed while the system runs.

### Home Performance AC Changeout w⧸ UltraAire SD12  
*Source id: Mt-ytfX9H-c*

- In an oversized, high-humidity home, the fix was to do a load calc, downsize all three AC systems, seal the attic vents, and add a ducted dehumidifier (UltraAire SD12) to the now-conditioned attic.
- The SD12 has a remote condenser and only slightly reheats (a slight sensible decrease at the supply), so it removes moisture without adding much sensible heat to a space that already had most of its load removed.
- A dehumidifier's performance is verified via measureQuick using entering/leaving air (grains removal), since the SD12 has no refrigerant ports to connect to.

### Hot Gas Reheat Dehumidification  
*Source id: eZR1JY_duOU*

- Hot gas bypass and hot gas reheat are NOT the same: bypass controls suction pressure to keep a compressor running at low load; reheat adds discharge heat back to the conditioned space after cooling to dehumidify without over-cooling.
- Over-cooling to dehumidify backfires: as you sensibly cool, RH rises toward dew point, and exterior glass/walls can hit dew point and sweat, so you only cool as much as comfort needs and reheat to drop RH.
- Reheat always happens AFTER the evaporator coil; placing reheat before the coil just adds sensible load to the evaporator.

### How Humidity Impacts The Weight of Air  
*Source id: o1MHTQSeQ20*

- Moist air (higher water-vapor content) is actually LIGHTER / less dense than dry air, because water vapor (0.0472 lb/ft3) weighs less than dry air (0.0807 lb/ft3), driven by the light hydrogen atom in the water molecule.
- Even though humid air is lighter, it carries more enthalpy because of the latent heat in the water vapor, which shows up when that air crosses an evaporator coil below dew point.
- Because latent heat is released as vapor condenses, it holds up the evaporator coil surface temperature, so humid return air produces a LOWER delta T than dry air, all else equal.

### How to Deploy a Dehum： Q&A with Bryan Orr  
*Source id: oMBYL2iiCnQ*

- Only deploy a dehumidifier AFTER confirming the fundamentals: the AC is properly sized (most common problem is it is oversized), it is set up for dehumidification (cold coil during ramp-down), and ventilation is proper but not excessive (bath/kitchen fans not run all day, no dryers venting inside).
- For a sealed/closed-cell-foam attic, Bryan prefers a dedicated dehumidifier just in the attic; water vapor is lighter than air ('hygric buoyancy') and gathers in the peaks, so pulling from the top and blowing down controls the whole house.
- If bringing in outdoor air, bring it in THROUGH the dehumidifier - but then attic-only design does not work, so use dampered systems (Tim DiStasio), two dehumidifiers, or an ERV (Neil at Comfort Squad) depending on climate/budget.

### How to Fix Attic Humidity Problems with Santa Fe Ultra Series Dehumidifier  
*Source id: lSQ0fbalQd0*

- In a closed-cell-foam (sealed) attic, moisture gathers in the peaks because water vapor is lighter than air ('hygric buoyancy'), so pull from the top of the attic and blow it down into the rest of the (open-communicating) house.
- Bryan's own home uses a dedicated attic dehumidifier because most of the home's latent load (10 kids, laundry, cooking, showers) plus the high-dew-point attic air drives moisture; drying the attic solves many downstream problems.
- Best attachment is pulling from the return and pushing directly into the supply; dumping into the AC return derates the equipment's latent capacity.

### How to Prevent Double Trapping Issues  
*Source id: uLz-tzJyeek*

- A double trap prevents drainage because it traps an air pocket in a high section; water fills both sides and pushes against the trapped air (which is lighter than water) instead of pushing it through.
- The most common cause is pushing the drain tee/90 down to the floor when setting the air handler for better pitch, creating an unintended second trap.
- Attic long runs sag over trusses and drop into a wall - after any change you must chase, pitch, strap, and support the whole run; never assume years of draining means it's fine.

### How to Properly Pipe a Drain on a Fan Coil  
*Source id: 3sbrTLwmNRo*

- Fan coil drains are often under negative pressure (air pulling on the line), which makes a proper trap essential; install into the PRIMARY drain port, not the secondary.
- The trap depth is set by the manufacturer based on static pressure - higher static needs a deeper trap; the trap outlet must be lower than the inlet, with a tall vent after the trap (taller than the pan) to prevent double trapping.
- Support and strap the drain (1/4 inch fall per foot typical), insulate horizontal runs in humid climates, install/wire all condensate switches in series so any open switch shuts the system down, and always test with large volumes of water.

### How to Stop Drain Snot (Bacterial Zoogloea)  
*Source id: 5VOffWjmWkk*

- Bacterial zoogloea ('elephant snot') is an emerging fast-growing drain-pan/drain-line blockage; it seems linked to all-aluminum coils losing copper's antibacterial (ion-producing) properties.
- First distinguish it from manufacturing oil residue on new coils (thorough coil cleaning fixes that), then use source control: good MERV-11 4-inch media filters, sealed filter slots, minimizing bypass and organic material reaching the coil.
- Adjuncts: UV lights in close proximity to the coil, bipolar ionization, and placing flattened copper tubing and/or a snipped piece of 15% silver rod in the drain pan to add antibacterial ions.

### Humidity Basics  
*Source id: e6xC7povssE*

- Relative humidity is the amount of moisture relative to the maximum the air could hold (saturation = 100% RH = dew point); warmer air can hold more moisture, colder air less, so RH is always relative to temperature.
- There are two things to track: total moisture content (measured in pounds or grains) and relative humidity - the same air heated in a sealed jar drops in RH even though moisture is unchanged.
- AC dehumidifies at the evaporator coil (air hits dew point and gives up moisture), but simultaneously cooling the air lowers how much moisture it can hold, so supply air RH is high until it mixes with room air.

### IAQ - Humidity and Moisture Control  
*Source id: x0ytMSfouaQ*

- Solve moisture/sweating problems by dealing with the moisture at its source (usually attic air infiltration and pressure imbalances), not by manipulating airflow.
- In humid climates, running the blower in the ON position raises indoor humidity (duct leakage/pressure imbalance and coil re-evaporation).
- Raising blower speed to warm a sweating vent temporarily stops sweating but then raises space RH and worsens dehumidification, making it worse.

### IAQ Basics： Understanding Indoor Air Quality  
*Source id: VxW2JLgGv7U*

- Have humility about IAQ — most harmful issues are long-term/chronic and hard to measure; source control is the biggest lever.
- Distinguish contaminants: heavy particles (dander/dust, PM10) settle and aren't much helped by the AC filter; PM2.5 and VOCs are the dangerous fine stuff; know CO vs CO2 (CO2 indicates poor ventilation, CO kills).
- Best fixes: high-quality 4-inch MERV 14+ media filters, sealing/balancing pressures, and reducing duct leakage; UV/bipolar/ozone products are low priority and can produce ozone.

### Indoor Air Quality (IAQ) Basics 3D  
*Source id: Q51KtAtmNag*

- Primary indoor pollutants: particulate matter (PM2.5/PM10), VOCs, humidity, CO, CO2, ozone, and radon — controlled through source control, pathways, filtration, ventilation, and humidity.
- Use MERV 13+ (ideally 4-inch+) filtration, keep RH 35-60% with whole-home dehumidifiers/humidifiers, and use balanced ventilation (ERV/HRV or ventilating dehumidifiers).

### Installation Best Practices： Drains and Drain Lines  
*Source id: tYs2dqoh4Xk*

- Use one trap and a vent after the trap that is taller than the drain pan; a drain tied into plumbing/sewer needs a trap but NO vent (to keep sewer gas out).
- Wire float switches in series (not parallel), add redundancy (secondary pan + drain-pan switch), and in humid climates break R (not C) so the customer knows when a float trips.
- Clean drains until they're actually clean (look with a flashlight), maintain 1/4-inch-per-foot fall, and insulate horizontal runs in unconditioned space.

### Installing a Whole-Home Dehumidifier  
*Source id: Y-OH6DLJ_RE*

- Duct a supplementary dehumidifier for least static pressure and good distribution — commonly a separate return near the unit ducting into the supply with a required backdraft damper so air doesn't force back through it when off.
- Get the drain right: if it backs up it must shut off the equipment (pan switches wired in series), and remember a dehumidifier ADDS sensible heat (~1860 BTU/hr) — it removes latent, not sensible, load.

### Intro to Psychrometrics w⧸ Eugene Silberstein  
*Source id: DDFhTjW4cWc*

- Air has real weight (~0.075 lb/ft^3, ~1.2 oz per cubic foot); blowers move enormous mass — a 2000 CFM blower moves ~108 tons of air a day — so the air side is a major system component.
- Counterintuitively, humidifying air LOWERS its density: at constant pressure, adding lighter water molecules (18 amu) pushes out heavier nitrogen (28) and oxygen (32).
- Operating pressures mean nothing without proper airflow, and a gas furnace does not remove moisture — heating just raises the air's capacity so relative humidity drops.

### Inverter Driven Install Considerations Part 1  
*Source id: uLGBRa6Ypq4*

- Weigh the charge on inverter/ductless equipment (keep the scale with the tanks) and stop chasing suction pressure up when adding charge, which causes the massive overcharging commonly seen on inverter systems.
- Verify ductless function without gauges: use air discharge temperature and, for accuracy, delta-T BTU (pyrometer in/out plus the CFM charts into MeasureQuick/Fieldpiece); expect suction/discharge temps in range (roughly 40-55° fully ramped) and a sane superheat.
- Inverter capacity turndown floats the evaporator (saturated suction) temperature up for efficiency, which hurts dehumidification; lock in a cold coil (e.g., 39-42°) at the outdoor unit and, in humid climates, keep it as cold as possible without freezing.
- The best dehumidifier is a big AC running full-tilt with reheat, not a throttled-down small one; and you must not overcool a space below the outdoor dew point or you condense moisture on hidden interior surfaces and grow mold.

### Is There Mold in my Ducks! 🦆(Ducts)  
*Source id: kPXSy-6uHGg*

- Growth around supply vents is almost never inside the ductwork; the duct interior is clean, and the growth is surface condensation on the ceiling/boot where cold supply air hits and reaches dew point.
- The dust that feeds the growth comes from an unsealed boot connecting to the hot, humid, dirty attic, so the fix is sealing every gap between the boot and the ceiling (from the attic if accessible) and redirecting airflow that hits the ceiling.

### Manual J Load Calculations 3D  
*Source id: Gb2DyjTeJ_M*

- Manual J (from ACCA) calculates residential heat losses and gains; software does the math but Manual J tells you which field measurements/data to collect for an accurate load calculation.
- You must account for surface areas and R-values of walls (deducting studs, windows, doors), windows (U-factor, orientation, panes, solar gain), doors, ceilings, floors, and duct insulation R-value, plus duct leakage, ventilation, appliances, and occupants.
- Occupant count for Manual J is number of bedrooms + 1; a single person adds ~230 sensible and ~200 latent BTU/hr.

### Pressures in the Home Matter w⧸ Sam Myers at IBS  
*Source id: zDHtjndtZsQ*

- The building envelope is part of the HVAC system; it is the container for the conditioned air, and duct/room pressure imbalances push and pull on it.
- Room-level pressure imbalance (too much supply into a room with no return path) over-pressurizes the room and forces conditioned air out through leaks, while under-pressurized rooms draw in unconditioned (often attic) air, causing humidity/comfort problems.
- You cannot oversize TOTAL system return, but you CAN oversize ZONAL return in one area, pulling that room negative.

### Psychrometrics and The Magic Line 3D  
*Source id: kZHIDD0qYH8*

- The psychrometric chart maps the invisible relationship between air and water; sensible heat moves you horizontally (temperature), latent heat moves you vertically (moisture), and a real cooling coil moves diagonally (both).
- The dew point line (the saturated curve on the left edge) is the 'real boss of comfort': any surface colder than the dew point becomes a dehumidifier - which is why a beer can sweats and attic ducts drip. Surfaces care about absolute saturation (dew point), not relative humidity.
- 'Psychro' means cold and 'metric' means measurement; the wet-bulb/dry-bulb spread indicates how dry the air is - though more precisely it's about the vapor pressure of the water vapor, not 'how much water the air can hold.'

### Psychrometrics, Humidity and Moisture Control Part 1  
*Source id: zDnsJ4kWzxI*

- Air is 'stuff' (mostly nitrogen, plus oxygen, CO2 and water vapor); hotter air is less dense, and - counterintuitively - humid air is LIGHTER than dry air because water vapor (H2O, atomic weight 18) is lighter than nitrogen (28) and oxygen (32).
- Relative humidity is how much moisture the air holds versus how much it CAN hold at that temperature (coffee-and-sugar analogy); absolute moisture, best read via DEW POINT, matters more - attic air at a modest RH but high temperature holds a lot of moisture and 'rains' the moment you cool it in the house.
- Anything sweats when its surface temperature reaches the dew point of the surrounding air, so you solve any mold/moisture problem exactly two ways: raise the surface temperature or lower the dew point of the air.

### Psychrometrics, Humidity and Moisture Control Part 2  
*Source id: yYVThICJKbQ*

- An air conditioner only dehumidifies two ways: a colder evaporator coil and longer runtime; lower fan speed makes a colder coil, and multi-stage/inverter equipment helps by extending runtime (peg the coil ~40F and never shut off).
- Right-size equipment - oversized systems short-cycle and never run long enough for the coil to reach dew point; old, weak, dirty units are often excellent dehumidifiers (low coil temp + long runtime), which is why a shiny new inverter system frequently dehumidifies WORSE.
- Solve moisture with source control and 'death by a thousand cuts': seal all the 'straws' (gasketed LED can lights, boots, duct penetrations), use humidity-sensing bath fans, don't run huge kitchen exhaust on high, and in humid climates keep ventilation minimal, demand-controlled, and ducted into the SUPPLY (never the return).

### Q&A - System Won't Dehumidify？ - Short #214  
*Source id: nEiesh6lZGo*

- When a system cools but won't dehumidify (homeowner Tim: 74F but 80-90% RH), you must systematically test, not just look at temperature split and pressures the way most companies do.
- First confirm the equipment is actually removing latent, not just cooling: run a MeasureQuick report / probes to see delivered capacity and sensible heat ratio (SHR should be easily below 0.7 at high RH for a properly set-up system); then confirm airflow is ~350 CFM/ton in a humid climate and that dehumidification/staging settings are correct.
- Then move to the house: a real duct-leakage test (duct blaster, not visual), a blower door for envelope leakage, and source control - dryer/bath fans venting inside, bath fans running constantly, whole-house fans, powered attic (solar) fans causing pressure imbalances, and 'mad air'.

### Santa Fe SmartAire Remote Sensor ｜ Whole Home Dehumidifier Control Made Easy  
*Source id: 8x7aRDMxdyM*

- Humidity issues (sweating ducts, high indoor RH, dripping vents) are widespread; if you have green grass outside you likely have humidity issues inside.
- The Santa Fe SmartAire wired remote sensor (two wires on RS terminals, up to 100 ft) lets you control humidity from the occupied space without adding a separate display or homeowner confusion.
- The updated Ultra V-Series has an upsized 8-inch outdoor-air ventilation duct to fix under-ventilation.

### Santa Fe Ultra V-Series Dehumidifiers： Digital Controls & Enhanced Ventilation  
*Source id: xJyMoR4B3rk*

- The Ultra V-Series (V = ventilation) moved from a 6-inch to an 8-inch ventilation duct with a more powerful fan to bring in enough outdoor air for the dehumidifier's capacity.
- Oversizing a dehumidifier just to get the right ventilation rate is just as bad; the bigger fan also handles more static on the supply side.
- New digital control adds an optional low-voltage (not battery) remote sensor wired to the RS terminals, a built-in float switch, and secondary drain pan.

### Santa Fe V155 Whole House Dehumidifier Install  
*Source id: r0MtEiJ5MYw*

- An oversized AC short-cycles and never runs long enough to dehumidify on its own; in Florida you need long run times to pull humidity out, which is why a dedicated dehumidifier is added.
- When tying the dehumidifier supply into the main HVAC duct, you must install a backdraft damper so AC supply air doesn't push back through the dehumidifier when it's off.
- Check supply static is below 0.5 in wc before tying the dehumidifier into the system, or it works against that pressure and can't function to full potential.

### Setting Up Residential Demand Ventilation with Laser Egg  
*Source id: 0IAo0mFJMbs*

- CO2 is a good proxy for ventilation; the Kaiterra Laser Egg (CO2 model) can trigger demand ventilation (ERV, fresh-air damper, or ventilating dehumidifier) via a smart plug and a home automation platform.
- Bringing in outdoor air dropped indoor CO2 but raised PM2.5 particles - a trade-off to be aware of in demand ventilation.

### Short 31 - U-Factor and R-Value  
*Source id: FxY95_ImuKM*

- R-value and U-value are inverse coefficients of the same thing: R = resistance to conductive heat flow, U = coefficient of heat transfer; convert with 1/U = R and 1/R = U.
- Higher R-value is better (more resistance), lower U-value is better (less heat transfer); both apply to conductive gains (molecule-to-molecule), not radiant gains through glass.
- Load-calc heat gain/loss: BTU/hr = square feet x U-value x delta T — the math a Manual J program does for you.

### Short 36 - Stack Effect  
*Source id: gFmmswBXSqw*

- It's clearer to say hot air FLOATS on cooler (denser) air and cold air SINKS, rather than 'heat rises' — heating raises molecular velocity, separates molecules, and lowers density.
- Heating a house creates stack effect: warm low-density air lifts to the top, drawing colder infiltration in low (around doors/windows) — so seal LOW areas (door sweeps) in heating climates.
- Cooling creates reverse stack effect: cool air sinks and creates negative pressure at the ceiling, drawing hot attic air in around can lights and ceiling boots — so seal HIGH areas (ceilings) in cooling climates like Florida.

### Short 7 - A Moisture Problem  
*Source id: WgONpSfzo7Y*

- Don't say mold, mildew, or even 'biological growth' — say the customer has a MOISTURE PROBLEM; it's fact-based, and in states like Florida techs aren't licensed to comment on or test for mold.
- Growth means something is hitting dew point or water is leaking/being added; you get condensation not simply where hot meets cold but where moisture-laden (higher-dew-point) air meets a surface at or below its dew point.
- HVAC pros can and should fix the moisture source (compressed/lost duct insulation, unsealed/uninsulated plenum, leaking boots, over-cooling below outdoor dew point) and improve IAQ starting with good filtration.

### Should I Fog or ＂Sanitize＂ My Ducts？ - Short #220  
*Source id: dLkSTsF1FKU*

- Adding chemicals to a duct system (fogging/sanitizing) should be a last resort; per NADCA's white paper, chemical labels require hard, non-porous surfaces, so only flex duct and externally-wrapped sheet-metal interiors are suitable — never fog internal liner or ductboard.
- Fogging leaves a sticky oily residue that dust adheres to, and you can't reliably coat the entire interior for the chemical to work as labeled — Zach calls it largely a feel-good/placebo gimmick.
- Only consider it with a specific documented cause (e.g. suspect microbial growth confirmed by a bore-scope AND an industrial-hygienist lab report, for a mold-sensitive but not chemical-sensitive occupant), and physically cleaning (whiffle-ball rags, then dry rags) is preferable to spraying-and-leaving.

### Smelly Ductless  
*Source id: oJXjQBAAQeg*

- Ductless (mini-split) systems in humid climates like Florida commonly develop a funky sweet odor even when not visibly dirty — clean the evaporator coil with Refrigeration Technologies Evap+ (enzyme-based, no-rinse, safe) and treat the drain pan/last coil row with Viper pan & drain treatment.
- Evap+ goes on straight (no dilution); the condensate running down the coil rinses it, and because both products are enzyme-based and non-toxic they don't interact negatively and can be used together.
- Manage blow-off after applying: either let it dwell while you do something else and give it time to run down the drain, or catch it with a rag/towel over a drop cloth; applying to the coil (rather than soaking everything) minimizes blow-off.

### Stop Sweaty Ducts, Vents and Systems  
*Source id: Vufih-WN5R4*

- Sweating happens when a surface drops below dew point; the real fix for moisture is SEALING and DEHUMIDIFICATION, not insulation, venting or radiant barrier (those only change temperature/heat).
- Cooling anything without dehumidifying it makes sweating WORSE - lowering an attic/garage/space temperature lowers surface temperatures and makes ducts/air handlers condense more.
- The refrigerant-side air temperature inside a duct changes surface temp only ~2 degrees; the attic temperature and radiant gains dominate - so mess with the space around the duct, not the air in it.

### Stop Vent Sweating After HVAC Installation - Proper Sealing Methods  
*Source id: AEr7-aQtfHk*

- Offer boot-to-drywall sealing as an install upgrade option to prevent post-install vent sweating; if declined in writing it's no longer your liability, and you can still fix it later for a cost.
- Vent sweating after a new high-performing system is 'hydric buoyancy' - hot, humid ~100+ degree attic air meets ~56 degree vent air at an unsealed/oversized boot and immediately sweats.
- Seal boots airtight with caulk all around, spray antimicrobial while grills are down, and seal boxes with fabric+mastic; Kalos owns its work and won't want to eat callbacks 6 years later.

### Testing Dehumidifiers： Q&A with Bryan Orr  
*Source id: 7JF4pbMKk_c*

- To prove a dehumidifier is dehumidifying, the air leaving it must have lower grains/pounds of moisture and lower dew point than the entering air — sensible temperature actually rises because the condenser reheats the air.
- The point of a dehumidifier is to remove moisture (and add sensible heat), not to lower temperature; that added sensible load actually helps the AC run more, and runtime plus low evaporator temperature drive good dehumidification.
- To verify performance properly you must know the unit's rating at specific entering-air conditions, measure static pressure, power consumption, and airflow against the manufacturer's charts.

### UV light and Petri Dish Demo  
*Source id: ZveGEenhiv4*

- UVC has been demonstrated effective against living organisms (bacteria, fungus) and viruses containing genetic material by deactivating that genetic material.
- The issue with UV isn't whether it works but whether there is enough intensity and dwell time for the specific organism; UV is more effective on surfaces (e.g. an evaporator coil) where dwell time is higher than on fast-moving air.
- A total-count agar gel in a petri dish is a simple in-home demo to show whether something is growing in a customer's air (not a specific identification test).

### Variable Speed Motors and Why They Matter w⧸ Jamie Kitchen  
*Source id: ddQEQxIvjhw*

- Variable speed technology exists to handle varying conditions: it matches capacity to the actual load instead of applying one fixed profile 365 days a year
- Dropping evaporator temperature and reducing CFM shifts a system to latent-focused: latent heat removal increases far more per degree of evap drop than the sensible load increases, lowering the sensible heat ratio
- You can maintain the same human comfort at a higher dry-bulb temperature by holding relative humidity lower - controlling humidity gives leeway on the thermostat set point

### Ventilation in Humid Climates  
*Source id: 4xX7xr2HT_U*

- Bring in outdoor air to dilute VOCs and CO2, but in Florida the only strategy Bryan will stand behind is filtration plus a ventilating dehumidifier
- When the outdoor dew point is higher than the indoor temperature, bringing that air straight in makes it 'rain' inside - raising relative humidity and growing mold where you can't see it
- A filter alone will not remove fungus spores from ventilation air; you need a combination of a good filter and a ventilating dehumidifier

### Ventilation w⧸ John Semmelhack  
*Source id: 1ubHRgL8AB4*

- Build tight and ventilate right: a tighter house plus a good ventilation system gives full control over the amount, temperature, quality, and energy impact of outdoor air
- Whole-house ventilation dilutes indoor pollutants (particulates, odors, moisture, VOCs, CO2) with cleaner outdoor air; CO2 is the one thing you cannot filter away and must dilute with outdoor air
- The ASHRAE standard tells you the required airflow and filtration but not HOW to do it for your climate - practitioners must think about the house as a system

### Why Air Conditioning Ducts, Units, and Vents Sweat  
*Source id: aJYC3Z3xFJM*

- Condensation happens when a surface (vent, duct, cabinet) reaches the dew point of the surrounding air — solve it by either raising the surface temperature or lowering the dew point of the air, and lowering dew point is usually the better bet.
- For sweating vents, seal humid-air intrusion around the boot first; controlling space relative humidity (keep 40-55%) usually beats raising fan speed, because raising airflow warms the vent but reduces dehumidification (raises sensible heat ratio).
- For sweating ducts/equipment in attics, it's the attic dew point (not attic temperature or wet bulb) versus the duct surface temperature that matters; best long-term fix is to seal the attic (foam/Icynene) and dehumidify/condition it (e.g. Ultra-Aire SD12).

### Why Ducts Drip - Conductsation w⧸ Rick Sims  
*Source id: LYKqGQozW8c*

- 'Conductation' (Rick's coined term) is about dew point versus surface temperature: since you usually can't control the dew point of unconditioned space, the strategies are about limiting how cool the duct surface gets.
- The single biggest factor in duct surface temperature is the air temperature AROUND the duct (radiant heat), not the air inside it — a 5°F rise in surrounding air raises duct surface temp ~4°F, while going R6 to R8 gains under 2°F and only ~1°F where you need it.
- Never let a cold duct touch a building component — a half inch of air gap is worth ~R1 (as much as going R6 to R8); piling mastic (which is a sealer, not insulation) creates thermal bridging that makes sweating worse.
- Moisture molecules prefer surfaces, not air; permeable materials absorb/adsorb moisture internally (which is why you need R13+ non-permeable closed-cell foam to insulate your way out), and cabinet air infiltration is the biggest thing techs can fix immediately with closed-cell foam tape gaskets.

### Why is The Supply Relative Humidity so High？  
*Source id: kn8KeumYfaM*

- High supply relative humidity (near 88-100%) is normal and not a problem — air touching the coil must reach 100% RH (dew point) to drop moisture, so the supply leaves near saturation; as it warms in the duct/space the RH drops again.
- Sponge analogy (from Jim Bergman): the sponge is the air, its size is the temperature (smaller = colder), and the water is the moisture — squeezing (cooling) it drops water at 100% saturation, and letting it expand (warming) lets it hold much more, dropping RH.
- The difference between the supply's measured RH and 100% is the coil bypass factor (air not making full contact with the coil), plus small duct and blower heat gains; dehumidification is proven by the drop in grains of moisture per pound, not by RH.

## Canonical field stories

### The 400-apartment return-plenum dehumidifier design
- **Setting:** A Florida forensic-engineer colleague called to 400 apartments using a plug-in dehumidifier in the return plenum
- **Diagnosis chain:** A hole in the exterior wall feeds a plenum with a Kenmore-type dehumidifier below the air handler to dry blended return+incoming air -> often fails because the dehumidifier's humidistat is mounted inside the cabinet (cycles on the cold coil), or the filter clogs, so it doesn't dehumidify when needed.
- **Root cause:** Uncontrolled/mis-sensed plug-in dehumidifier (humidistat placement, clogged filter)
- **Lesson:** The real need is a small residential makeup-air unit that heats/cools/humidifies/dehumidifies within a range - a product that doesn't exist yet.
- **Source:** [(Podcast) Drying Stuff vs. Drying Air - Humidification, Dehumidification, and Ventilation] (id: R77L6dsEE50)

### The muggy Florida ECM retrofit
- **Setting:** Replacing old PSC / undersized-duct systems with 400-CFM/ton variable-speed units in high-humidity Florida
- **Diagnosis chain:** The old inefficient system had a colder coil and lower airflow (a good latent-removal machine) -> the new 400-CFM/ton ECM unit moved design airflow with a warmer coil -> the house became muggy/moldy and the customer was less comfortable than before.
- **Root cause:** Sizing airflow to 400 CFM/ton in a high-latent climate raised the coil temperature and cut moisture removal
- **Lesson:** In high-latent climates favor a colder coil / lower airflow (even a smaller coil + TXV) for latent removal, accepting a small energy penalty for comfort and health.
- **Source:** [(Podcast) Psychrometrics for Fun and Profit w⧸ Jamie Kitchen] (id: ULg2hC4trUc)

### Growth from an unsealed duct-to-attic gap
- **Setting:** Interior closet with a system whose ductwork comes out of the attic
- **Diagnosis chain:** Growth worst on a floor/flue piece where a ~4-inch gap to the attic was only taped; the taped ring gets cold, moisture in the air condenses on it, dust sticks, and growth starts.
- **Root cause:** Warm dusty humid attic air reaching a very cold duct surface through an unsealed ~4-inch taped gap
- **Lesson:** Cold duct surfaces plus infiltrating humid attic air condense and grow; seal the gaps to the attic.
- **Source:** [A Duct Moisture Problem Diagnosis (Short)] (id: NtMoOU5fQu4)

### The drain that clogs but isn't dirty
- **Setting:** Florida platform air handler drain teaching class
- **Diagnosis chain:** A drain keeps backing up but the water isn't very dirty when cleaned; suspect a double trap (sagged PVC or a chase-pipe misalignment pushing the drain down and back up) that seals with a water column and traps air pockets.
- **Root cause:** Double trap from sagging/unbraced PVC or chase misalignment
- **Lesson:** Repeated 'clean the drain' calls on a not-very-dirty drain point to a double trap; find and correct it (cut the tee, raise the drain).
- **Source:** [A Few Condensate Considerations] (id: -JSdAMuwbig)

### Bren Cookie's offer-refuse approach in Detroit
- **Setting:** Family HVAC business in a tough market (Detroit, MI)
- **Diagnosis chain:** Runs a few standard tests every job - static pressure and a 'duct deficiency' test - then asks the client if they want to fix just the basics or go deeper on the other problems found.
- **Root cause:** Techs' own lack of confidence selling solutions, not the client's unwillingness to hear about problems.
- **Lesson:** Almost nobody refuses to hear what's wrong with their home; present findings comfortably and let the client decide.
- **Source:** [Cleaning Best Practices： Condensate Drain Lines and Pans] (id: cqCjZ8Lnwuo)

### Clearing a slime-packed 1-1/4 inch common drain
- **Setting:** Commercial maintenance in a huge building; the entire inch-and-a-quarter common drain filled with slime from aluminum evaporator coils
- **Diagnosis chain:** Tech put a fitting on the 3/4-inch pipe feeding the common drain and repeatedly funneled hot water down; on the previous pass he heard movement, so he kept dumping gallons of hot water until water movement resumed.
- **Root cause:** Slime/biofilm buildup from all-aluminum evaporator coils packing the common drain
- **Lesson:** Persist - keep flushing until you get water movement and the line is truly clear.
- **Source:** [Cleaning a Difficult AC Condensate Drain] (id: ttfXcWIOHmM)

### VRF that couldn't hold humidity
- **Setting:** Matt's first VRF (Mitsubishi) install for a technically savvy client
- **Diagnosis chain:** Client at 72F setpoint struggled to keep humidity low despite VRF running low stages sold as controlling humidity
- **Root cause:** VRF 'dry mode' bill of goods doesn't fully control humidity; sensible heat ratios and equipment matches don't guarantee latent control
- **Lesson:** Started using standalone dehumidification regularly to control latent independently
- **Source:** [Customers Buy Comfort—Why Matt Risinger Uses Dehumidification in his Homes] (id: bHG2e1XGG5E)

### Miami hotel DOAS units and the reheat that was never turned on
- **Setting:** 5-year-old Miami hotel, ~8 DOAS units, sweating hallways, peeling wallpaper
- **Diagnosis chain:** Units discharging 52-54F air; one unit had a compressor replaced four times as 'garbage'. Hooking up the service laptop showed the reheat feature was unchecked at commissioning and the recurring compressor 'failures' were the digital-unloader noise plus a micro-leak on the vibration-cracked discharge line
- **Root cause:** Reheat option never enabled at commissioning (units ran as straight cooling); repeated compressor changes chased a digital-compressor sound and a discharge-line micro leak
- **Lesson:** Turn reheat on and set 70F discharge; use the correct service tool and don't condemn the digital compressor for its normal unloading behavior
- **Source:** [Dedicated Outdoor Air System (DOAS) 101 with Roman Baugh] (id: 7ThhG_bDPtc)

### Duct leakage no dehu can fix
- **Setting:** Humid-climate home with duct leakage outside the thermal envelope
- **Diagnosis chain:** Installed a dehumidifier as a band-aid on a house with ~200 CFM of duct leakage in a vented attic
- **Root cause:** Duct leakage outside the envelope overwhelms any dehumidifier
- **Lesson:** Check total duct leakage; if you have ~200 CFM leakage in a humid climate no dehu will fix it until the leakage is fixed
- **Source:** [Dehumidification Hootenanny w⧸ Chris Conway, Dustin Cole, Tim De Stasio, Chris Hughes, Nikki Krueger] (id: FhZt9xa22AI)

### Upset customer, three callbacks, and the old poly-tube drain
- **Setting:** Attic/upstairs install reusing the old drain
- **Diagnosis chain:** Within 3 months the drain kept backing up; multiple chemical cleans couldn't clear the old under-house poly tube that was clogged with nasty buildup, and the new aluminum-coil system put out roughly twice the water of the old system.
- **Root cause:** Reusing an aged, clogged poly-tube drain with a new aluminum-coil, higher-condensate system 'woke up' the old buildup.
- **Lesson:** Even a correctly done install changes the drain's experience; run a new drain (e.g., out an external wall) and disclose the aluminum-coil/condensate change to the homeowner.
- **Source:** [Drain Planning and Fabrication] (id: oBb3E7qQh8c)

### Oversized 3-system home with attic humidity solved by downsizing + attic dehumidifier
- **Setting:** Very large Florida home, three ACs, indoor and attic RH above 65% on a hot summer day; fairly new but drastically oversized equipment; someone had previously open-cell foamed the attic but left the attic vents open
- **Diagnosis chain:** Load calc showed the equipment was drastically oversized -> downsized all equipment, sealed the attic vents, installed an UltraAire SD12 dehumidifier with remote condenser in the attic to control moisture without over-cooling; used measureQuick to commission each piece
- **Root cause:** Grossly oversized equipment plus an unsealed, humid attic (open vents on a foamed attic)
- **Lesson:** Right-sizing plus dedicated dehumidification turns the attic from the wettest point in the house into a moisture sink; many customers will pay to have the problem truly solved.
- **Source:** [Home Performance AC Changeout w⧸ UltraAire SD12] (id: Mt-ytfX9H-c)

### The Winn-Dixie hot gas reheat that confused a young Bryan
- **Setting:** Bryan's early HVAC-school days; his dad described a Winn-Dixie grocery store that ran store air over the evaporator then over a big coil fed by discharge heat from the refrigeration motor room
- **Diagnosis chain:** Bryan couldn't understand why you'd reheat air you just cooled -> eventually saw that sometimes you must remove moisture without lowering temperature (already at setpoint), so you dehumidify then reheat
- **Root cause:** Conceptual: reheat exists to dehumidify without over-cooling and to reuse otherwise-wasted refrigeration heat
- **Lesson:** Reheat reuses waste heat to dehumidify a space at (or near) setpoint - a 'beautiful circumstance' in grocery refrigeration.
- **Source:** [Hot Gas Reheat Dehumidification] (id: eZR1JY_duOU)

### Restaurant sewer-gas smell from negative pressure
- **Setting:** Restaurant with strong odor near bathrooms and hard-to-open doors
- **Diagnosis chain:** Doors hard to open + sewer smell => negative pressure pulling sewer gas up dried-out floor drains due to insufficient makeup air for the kitchen hood
- **Root cause:** Kitchen exhaust without enough makeup air negatively pressurizing the building
- **Lesson:** Balance building pressures / provide makeup air
- **Source:** [IAQ - Humidity and Moisture Control] (id: x0ytMSfouaQ)

### Danielle's return by the garage door
- **Setting:** Home with a direct return next to a garage door and thermostat above it, teenagers shutting bedroom doors
- **Diagnosis chain:** Lowest-pressure point at that return pulls hard, drawing garage/attic air through the poorly sealed door; thermostat drifts up
- **Root cause:** Pressure imbalance + poorly sealed door pulling in unconditioned air
- **Lesson:** Seal and balance to fix comfort, moisture and IAQ at once
- **Source:** [IAQ - Humidity and Moisture Control] (id: x0ytMSfouaQ)

### Chinese drywall
- **Setting:** Homes built ~15 years ago with cheap imported drywall
- **Diagnosis chain:** Pipes corroding + occupant symptoms within months traced to off-gassing drywall
- **Root cause:** Corrosive off-gassing building material
- **Lesson:** Unregulated imported materials can be harmful; source control matters
- **Source:** [IAQ Basics： Understanding Indoor Air Quality] (id: VxW2JLgGv7U)

### Fertilizer/dead-rat odor drawn into air handler
- **Setting:** Home with a persistent smell concentrated in one area
- **Diagnosis chain:** Odor source (stored fertilizer / dead rat) near the air handler being pulled into the cabinet and distributed
- **Root cause:** Contaminant source near return being circulated
- **Lesson:** Take odor complaints seriously; find and remove the source
- **Source:** [IAQ Basics： Understanding Indoor Air Quality] (id: VxW2JLgGv7U)

### Genry Garcia 1941 ranch case study
- **Setting:** Older 1941 ranch home with high humidity and pollutant-sensitive client (with Santa Fe dehumidifiers)
- **Diagnosis chain:** Blower-door test revealed attic/crawlspace leakage; zonal pressure diagnostic located leakage; installed whole-house dehumidifier and downsized/right-sized the HVAC with integrated ventilating dehumidification
- **Root cause:** Air leakage + oversized equipment + poor humidity control
- **Lesson:** Even old homes can be fixed with air sealing, right-sizing, and dehumidification/ventilation
- **Source:** [Indoor Air Quality (IAQ) Basics 3D] (id: Q51KtAtmNag)

### Train coil dripping fixed by tipping the coil
- **Setting:** A specific Trane (Tez-era) coil that dripped water off the slant coil into the pan/ceiling
- **Diagnosis chain:** Water dripping off the slant after a while; removed two top screws and raised the coil slightly so water ran off correctly
- **Root cause:** Coil set over too far from the factory
- **Lesson:** Nuisance drain issues usually have a real cause — often airflow/high static or configuration
- **Source:** [Installation Best Practices： Drains and Drain Lines] (id: tYs2dqoh4Xk)

### Bryan's own house creeping to 58% RH
- **Setting:** Bryan's 2-year-old home with good Carrier/Mitsubishi equipment and an ERV, but RH creeping to 58%
- **Diagnosis chain:** Was running electric-heat reheat to dehumidify (costly); installed a Clean Comfort dehumidifier free-drawing return in the attic playroom and ducting into both the upstairs and downstairs supply plenums
- **Root cause:** Insufficient latent removal on edge-season conditions
- **Lesson:** Supplementary dehumidification adds comfort even with high-end equipment; RH trended 55->52 over a week
- **Source:** [Installing a Whole-Home Dehumidifier] (id: Y-OH6DLJ_RE)

### Dumping refrigerant into a choking system
- **Setting:** Classic service call with low operating pressures
- **Diagnosis chain:** Tech adds refrigerant with no pressure change; system keeps 'choking'; finally pulls a 3-inch-thick filter and hears the whoosh — pressures then read high
- **Root cause:** Airflow starvation (plugged filter), not low charge
- **Lesson:** Address airflow before the refrigerant side
- **Source:** [Intro to Psychrometrics w⧸ Eugene Silberstein] (id: DDFhTjW4cWc)

### Instructor throwing charged capacitors
- **Setting:** Bryan's AC school as a teenager
- **Diagnosis chain:** The instructor would charge up capacitors and throw them to new students to shock themselves
- **Root cause:** Bad old-school hazing around stored high voltage
- **Lesson:** Inverter boards store high voltage in capacitors; wait for the DC to discharge (below ~60V on Daikin VRF) before servicing
- **Source:** [Inverter Driven Install Considerations Part 1] (id: uLGBRa6Ypq4)

### Train unit with a discharge indicator
- **Setting:** Bryan working a Train (Trane) system with Gilbert
- **Diagnosis chain:** Bryan reached in and the tech warned him to wait for the DC-discharged indicator or 'you'll get a shot'
- **Root cause:** Residual stored high voltage after power-off
- **Lesson:** Respect the board's discharge indicator; many techs would just watch you get shocked
- **Source:** [Inverter Driven Install Considerations Part 1] (id: uLGBRa6Ypq4)

### Mold around the supply vent
- **Setting:** Homeowner/apartment call, occupant in a panic that mold is growing inside the ductwork and being blown out
- **Diagnosis chain:** Wiped a rag up inside the supply to show the duct interior is clean; identified the boot was not sealed to the attic, letting hot humid dirty attic air/dust settle where cold air condenses
- **Root cause:** The boot is not sealed to the attic space, so attic dust collects on condensation-cooled surfaces and grows
- **Lesson:** Reassure the customer the duct is clean, then seal all gaps at the boot and redirect airflow to stop the condensation growth
- **Source:** [Is There Mold in my Ducks! 🦆(Ducts)] (id: kPXSy-6uHGg)

### Wilmington NC humidity room
- **Setting:** Humid climate home, Wilmington North Carolina; blower-door test plus thermal scan
- **Diagnosis chain:** Customer complained of humidity in one room -> blower door + thermal camera found a very leaky corner -> shut the door with system running and measured room ~5 Pascals negative -> discovered a prior HVAC contractor had added a big return to that room -> a master-bath exhaust fan kicking on pulled the room to ~8 Pascals negative
- **Root cause:** Oversized zonal return (plus bath exhaust fan) drove the room negative, pulling in humid outside/attic air
- **Lesson:** Balance room pressures; damper down the oversized return to even out the room and the humidity issue resolves
- **Source:** [Pressures in the Home Matter w⧸ Sam Myers at IBS] (id: zDHtjndtZsQ)

### What Willis Carrier actually invented
- **Setting:** A New York paper factory, ~1900s
- **Diagnosis chain:** Paper warps at the wrong RH -> Carrier ran cold (~55F) groundwater down a plate and passed air over it -> the cold water surface was at the air's dew point so the air gave up moisture to it (like an evaporator coil using water)
- **Root cause:** Needed humidity control, not cooling
- **Lesson:** Carrier invented a dehumidifier and coined the term 'air conditioning' - he was a great marketer; compression refrigeration had existed ~80 years earlier
- **Source:** [Psychrometrics, Humidity and Moisture Control Part 1] (id: zDnsJ4kWzxI)

### Radiant barrier + vented attic = everything sweats
- **Setting:** Humid-climate homes where a company sold a radiant barrier as an upgrade
- **Diagnosis chain:** Home had no duct-sweat problem -> someone installed a radiant barrier under the roof deck -> suddenly everything sweats
- **Root cause:** The radiant barrier stops the ducts from radiating heat to the hot roof, cooling all attic surfaces below dew point without removing any attic moisture
- **Lesson:** In a humid climate a radiant barrier (and even worse, a powered attic fan) causes sweating; the fix is to seal AND dehumidify the attic, or remove the barrier
- **Source:** [Psychrometrics, Humidity and Moisture Control Part 1] (id: zDnsJ4kWzxI)

### The sweating vent and the pool
- **Setting:** Bryan chasing a single sweating vent in a living-area peak for months at a previous company
- **Diagnosis chain:** Tried a plastic vent, sealing around it, a Rain-X-type coating - nothing worked -> a senior tech asked 'do they have a pool?' -> yes -> 'they're keeping the doors open' -> the client admitted keeping the door open all day when grandkids played
- **Root cause:** Client behavior: open doors letting humid outdoor/pool air in (and moisture that stays in furnishings a long time)
- **Lesson:** Source control and knowing your client is huge; you can't fix sweating if they leave doors/windows open
- **Source:** [Psychrometrics, Humidity and Moisture Control Part 2] (id: yYVThICJKbQ)

### Coils leaking every year in a sealed unused space
- **Setting:** High-end tightly-sealed houses / guest houses above garages / unused outdoor kitchens where coils fail within 6-12 months
- **Diagnosis chain:** Coil leaks repeatedly -> walk in and smell chemicals -> deploy a VOC/CO2 monitor (always reads high in unventilated spaces) -> suspect off-gassing material (improperly applied open-cell foam, Chinese drywall, new materials packed into a sealed room)
- **Root cause:** Off-gassed VOCs/formic acid attacking thin modern coils, not a defective coil
- **Lesson:** When a coil leaks every year it's a house condition, not the coil; identify the unique material, coat coils (fol/e-coat), or flush with ventilation, and don't blindly trust anyone who says 'it's fine'
- **Source:** [Psychrometrics, Humidity and Moisture Control Part 2] (id: yYVThICJKbQ)

### Three companies, ten visits, still 80-90% humidity
- **Setting:** Homeowner Tim's Carrier heat pump with attic air handler; humidity worst in 90F+ weather; evaporator coil had been replaced once
- **Diagnosis chain:** Cools to 74F but 80-90% RH -> 10 visits from 3 companies -> they added a little charge (said it wasn't needed), checked attic-air infiltration into the return and plugged a few holes -> all threw up their hands
- **Root cause:** Not determined by the box-swappers; likely equipment latent-removal, airflow, duct leakage, envelope, or behavior/source-control (or a combination) - none confirmed because nobody tested delivered capacity
- **Lesson:** Three companies all failed because they did the same shallow thing (gauges + temperature split); you don't know until you actually test capacity, airflow, ducts, and envelope
- **Source:** [Q&A - System Won't Dehumidify？ - Short #214] (id: nEiesh6lZGo)

### Oversized unit causing humidity in Kyle's Florida home
- **Setting:** Florida attic install, previous owner installed oversized unit 4 years ago
- **Diagnosis chain:** Oversized unit satisfies quickly -> short run times -> no dehumidification -> humidity hit 67% inside after dropping setpoint for static test
- **Root cause:** Oversized AC with short run times
- **Lesson:** Add a dedicated dehumidifier with long run times to control latent load
- **Source:** [Santa Fe V155 Whole House Dehumidifier Install] (id: r0MtEiJ5MYw)

### Compressed flex duct over a truss
- **Setting:** Florida attic
- **Diagnosis chain:** Flex duct running over a truss is compressed, crushing the insulation; that spot gets moisture and biological growth.
- **Root cause:** Compressed duct insulation creating a cold surface hitting dew point
- **Lesson:** Lift and strap the duct properly to remove the compression and the moisture problem.
- **Source:** [Short 7 - A Moisture Problem] (id: WgONpSfzo7Y)

### Cold glass analogy
- **Setting:** A cold glass set in the room begins to sweat
- **Diagnosis chain:** Air contacting the below-dew-point glass reaches 100% RH and gives up moisture onto the glass
- **Root cause:** Surface below dew point
- **Lesson:** A sweating duct/air handler is dehumidifying the space around it exactly like the glass; heat the surface or dry the air to stop it
- **Source:** [Stop Sweaty Ducts, Vents and Systems] (id: Vufih-WN5R4)

### Gilberto's profusely sweating attic
- **Setting:** A house (Gilberto's call) where the whole attic is sweating
- **Diagnosis chain:** Vents/boots not properly sealed or recessed, oversized holes, hot humid attic air meeting cold vent air -> profuse sweating and growth
- **Root cause:** Unsealed/oversized boots letting 100+ degree humid attic air reach cold vents
- **Lesson:** Drop the vents, seal airtight with caulk, clean/antimicrobial, and re-seal boxes
- **Source:** [Stop Vent Sweating After HVAC Installation - Proper Sealing Methods] (id: AEr7-aQtfHk)

### The oversized fixed-speed unit that runs at rated capacity only 3% of the time
- **Setting:** Commercial building load study comparing a 20-ton fixed-speed unit to a similar variable-speed unit
- **Diagnosis chain:** Accurate degree-day heat profile → installed variable speed of similar capacity → it only ran at the full 20-ton rated capacity ~3% of the time
- **Root cause:** Fixed-speed equipment must be oversized for the rare design day, so it short-cycles and wastes energy the rest of the time
- **Lesson:** Oversized fixed-speed units compromise air treatment off-design and waste huge start/stop energy; variable speed matches capacity to load
- **Source:** [Variable Speed Motors and Why They Matter w⧸ Jamie Kitchen] (id: ddQEQxIvjhw)

### The ERV that Bryan pulled out of his own house
- **Setting:** Bryan's own Florida home, testing ventilation strategies
- **Diagnosis chain:** Installed an ERV → over time was completely unhappy with it → it wasn't doing the job needed in Florida's high dew points
- **Root cause:** HRVs/ERVs and other ventilation strategies that work elsewhere just don't work in Florida's very high dew points
- **Lesson:** In high-dew-point markets a ventilating dehumidifier is the way to bring in outdoor air, not an ERV
- **Source:** [Ventilation in Humid Climates] (id: 4xX7xr2HT_U)

### The Florida vacation-rental petri dish under the air handler
- **Setting:** Florida short-term rental with a fan-cycler outdoor-air duct dumping straight into the return box of an air handler on duct board
- **Diagnosis chain:** Outdoor air dumped into return → guests set 69-70F → outdoor air hits cold return and condenses → cycling the blower re-evaporates coil moisture raising indoor RH → growth on duct board plus low temp plus high RH
- **Root cause:** A ventilation standard meant to make air healthier, implemented without preconditioning in a high-dew-point climate, creates condensation and mold under the air handler
- **Lesson:** In hot humid climates outdoor air must be preconditioned (ventilating dehumidifier or ERV that knocks the dew point below surface temps) before it hits the return; the standard doesn't tell you the climate implications
- **Source:** [Ventilation w⧸ John Semmelhack] (id: 1ubHRgL8AB4)

### Sweating attic ductwork sealed and dehumidified
- **Setting:** Attic with sealed (Icynene) roofline, sweating supply plenum and air handler filling the secondary pan
- **Diagnosis chain:** 77.7°F attic dew point vs ~48°F duct air with only R6 insulation; multiple ridge vents cut into a sealed attic; installed Ultra-Aire SD12 split dehumidifier to bring attic to 40% RH and 71°F
- **Root cause:** high attic dew point on cold duct/cabinet surfaces in a poorly-vented sealed attic
- **Lesson:** Sealing the attic and conditioning/dehumidifying it eliminates sweating on ducts and equipment and lowers space humidity
- **Source:** [Why Air Conditioning Ducts, Units, and Vents Sweat] (id: aJYC3Z3xFJM)

### Wet air handler bottom = drain leak, not sweat
- **Setting:** Rick's demonstration air handler ('I sweat too')
- **Diagnosis chain:** Top and sides dry, only the bottom soaking wet — the bottom insulation got wet (clogged drain / cracked pan), and wet insulation conducts (water conducts better than copper)
- **Root cause:** clogged drain or cracked drain pan soaked the cabinet insulation, turning insulation into a conductor
- **Lesson:** Wet only on the bottom of an air handler points to a drain problem, not condensation; once insulation is wet it's no longer insulation and must be dried or replaced
- **Source:** [Why Ducts Drip - Conductsation w⧸ Rick Sims] (id: LYKqGQozW8c)

### Black stain around ceiling grilles misdiagnosed as duct leak
- **Setting:** Florida homes, grille/diffuser with black staining on drywall
- **Diagnosis chain:** Linear diffusers leak air between the flange and drywall (no gaskets); with thermal imaging the feathered pointed edges show air movement, not a rounded watercolor duct leak
- **Root cause:** air movement between diffuser flange and drywall meeting 120-grain moist air above
- **Lesson:** Stop the air movement with adhesive closed-cell foam tape; don't just mastic everything and create thermal bridging
- **Source:** [Why Ducts Drip - Conductsation w⧸ Rick Sims] (id: LYKqGQozW8c)

## Contrarian takes (where Bryan / guests diverge from common teaching)

- **Common teaching:** Absolute humidity stays constant regardless of temperature throughout a house.
  **Bryan's position:** Wrong - measurement showed a few degrees of dry-bulb change swings the dew point a lot in a house of absorptive materials.
  **Reasoning:** Rising dry-bulb pulls moisture out of stuff (carpet, wallboard, upholstery) into the air.
  **Source:** [(Podcast) Drying Stuff vs. Drying Air - Humidification, Dehumidification, and Ventilation] (id: R77L6dsEE50)

- **Common teaching:** A furnace dries the house; radiant heat keeps it moist.
  **Bryan's position:** Partly true (duct leaks pull in dry winter air) but false in general.
  **Reasoning:** A well-ventilated radiant house can be drier; ventilating to code dries both.
  **Source:** [(Podcast) Drying Stuff vs. Drying Air - Humidification, Dehumidification, and Ventilation] (id: R77L6dsEE50)

- **Common teaching:** An ERV (enthalpy) is the universal best - everyone should use it.
  **Bryan's position:** Not for houses - humidity is usually a pollutant you want OUT; it's about controls (modulating recovery), not the membrane.
  **Reasoning:** Over 8760 hours a year you usually don't want that humidity back inside.
  **Source:** [(Podcast) Drying Stuff vs. Drying Air - Humidification, Dehumidification, and Ventilation] (id: R77L6dsEE50)

- **Common teaching:** Showers are the big residential humidity source.
  **Bryan's position:** Cooking (much longer duration) is the biggest source.
  **Reasoning:** A shower is 10-15 minutes; cooking (curries, sauces) runs far longer, adding much more water.
  **Source:** [(Podcast) Drying Stuff vs. Drying Air - Humidification, Dehumidification, and Ventilation] (id: R77L6dsEE50)

- **Common teaching:** Humid air is heavy and thick.
  **Bryan's position:** Moist air is LESS dense (lighter) than dry air.
  **Reasoning:** Water vapor takes more volume per mass; that's why low-pressure (stormy) systems are moist - it exerts less pressure.
  **Source:** [(Podcast) Psychrometrics for Fun and Profit w⧸ Jamie Kitchen] (id: ULg2hC4trUc)

- **Common teaching:** More moisture means denser air and more heat capacity.
  **Bryan's position:** No - that's density confusion; moist air is lighter yet holds more latent energy.
  **Reasoning:** People wrongly tie specific heat to density; the two must be separated.
  **Source:** [(Podcast) Psychrometrics for Fun and Profit w⧸ Jamie Kitchen] (id: ULg2hC4trUc)

- **Common teaching:** 400 CFM/ton is always the target.
  **Bryan's position:** In high-latent climates a colder coil / lower airflow removes more moisture.
  **Reasoning:** Higher airflow and warmer coils favor sensible cooling and leave the house muggy; oversizing airflow made Florida retrofits moldy.
  **Source:** [(Podcast) Psychrometrics for Fun and Profit w⧸ Jamie Kitchen] (id: ULg2hC4trUc)

- **Common teaching:** A sling psychrometer is the most accurate way to read humidity.
  **Bryan's position:** Modern digital hygrometers (Testo 605i) are more accurate.
  **Reasoning:** Bryan admits he was wrong that nothing beats his mercury sling psychrometer.
  **Source:** [(Podcast) Psychrometrics for Fun and Profit w⧸ Jamie Kitchen] (id: ULg2hC4trUc)

- **Common teaching:** Re-level the float switch and the drain problem is fixed
  **Bryan's position:** That only solves the symptom - the real question is why water is getting to the float (double trap, platform sag, static, pan config).
  **Reasoning:** Keeping the float from tripping doesn't address the cause; the water is still going somewhere it shouldn't.
  **Source:** [A Few Condensate Considerations] (id: -JSdAMuwbig)

- **Common teaching:** Set the float switch flat at the unit and rely on pan level
  **Bryan's position:** Run the float around to the platform top so any water eventually fills and trips it, instead of depending on a shallow pan level.
  **Reasoning:** On some shallow pans the water level won't rise enough to trip a float mounted at the unit.
  **Source:** [A Few Condensate Considerations] (id: -JSdAMuwbig)

- **Common teaching:** A duct can be too big; you need a minimum air velocity
  **Bryan's position:** In the context of Manual D a duct can't be too big - branch-run volume matters, velocity doesn't (as long as you don't exceed the velocity limit); Manual D even says there is no minimum velocity.
  **Reasoning:** The register is the 'thumb over the end of the hose' giving throw and spread; the same CFM out of a 6-inch or 12-inch duct behaves the same.
  **Source:** [A Walk Through the Residential Design Series (ACCA Manuals J, S, and D) with Ed Janowiak] (id: qRhSAfirHJE)

- **Common teaching:** Manual J oversizes the heat loss / does a bad job with thermal mass
  **Bryan's position:** Manual J intentionally lands at the top of a range for a moving target - read the book, it tells you it will do that.
  **Reasoning:** It hits a stationary target (maintain 70F) against variable real conditions, so it manages expectations by design.
  **Source:** [A Walk Through the Residential Design Series (ACCA Manuals J, S, and D) with Ed Janowiak] (id: qRhSAfirHJE)

- **Common teaching:** Bigger air conditioner is better
  **Bryan's position:** Oversized AC runs less at part load and removes less humidity; you'll get more complaints from oversized than undersized equipment, so if you must pick, undersize.
  **Reasoning:** Latent load doesn't change with sun/part load, so a unit that runs less can't dehumidify well.
  **Source:** [A Walk Through the Residential Design Series (ACCA Manuals J, S, and D) with Ed Janowiak] (id: qRhSAfirHJE)

- **Common teaching:** ERV balanced energy recovery is ideal everywhere
  **Bryan's position:** In Florida ERVs often transfer MORE moisture into already-humid air (you usually exhaust from humid bath/kitchen) - smart ventilation with sensors avoids that; ventilating dehumidification is preferred
  **Reasoning:** market humidity + exhaust source make blind energy exchange counterproductive
  **Source:** [Advanced Ventilation w⧸ CERV2] (id: 5lyiz-YjwmQ)

- **Common teaching:** Oil is fully miscible with refrigerant, so oil carry doesn't matter
  **Bryan's position:** POE is miscible in LIQUID refrigerant but NOT with vapor - once refrigerant boils off, the oil stays a viscous liquid; saying oil is miscible in vapor refrigerant is incorrect
  **Reasoning:** in the last ~third of the evaporator the oil grabs the wall as a viscous patch impairing heat transfer
  **Source:** [Advanced Ventilation w⧸ CERV2] (id: 5lyiz-YjwmQ)

- **Common teaching:** Run higher superheat to protect the compressor
  **Bryan's position:** We probably kill as many/more compressors by OVERHEATING (running high superheat) than by flooded running; compressors handle liquid better than we give credit, especially at low charge
  **Reasoning:** high superheat dries out the last third of the coil, holds up oil, and overheats the compressor
  **Source:** [Advanced Ventilation w⧸ CERV2] (id: 5lyiz-YjwmQ)

- **Common teaching:** To clean a filthy drain pan you have to pull the coil (and pump the unit down).
  **Bryan's position:** In most cases you can pull the blower, take the front/rear panels off, and vacuum under and behind the coil without pulling it or pumping down.
  **Reasoning:** On most air handlers the coil slides forward a little; you only need a couple inches of copper play to snake tubing under it and clean the pan.
  **Source:** [Changing a Drain Pan the Easier Way] (id: qytos4XIlPE)

- **Common teaching:** Put pan tabs in the drain to prevent buildup.
  **Bryan's position:** Pan tabs can cause as much heartache as they help - a new guy shoves them near the outlet and blocks the drain.
  **Reasoning:** They're a fine idea but easily misused; there is no silver bullet.
  **Source:** [Cleaning Best Practices： Condensate Drain Lines and Pans] (id: cqCjZ8Lnwuo)

- **Common teaching:** Chemical drain-injection systems keep pans clean.
  **Bryan's position:** One product they examined used 45% vinegar, corrosive to both copper and aluminum, which would eat the coil out - same reason you never pour bleach in the drain pan.
  **Reasoning:** Acidic/corrosive chemicals sitting in the pan destroy the coil.
  **Source:** [Cleaning Best Practices： Condensate Drain Lines and Pans] (id: cqCjZ8Lnwuo)

- **Common teaching:** Jim Bergman: a properly-fitted filter means you'll never have a drain backup.
  **Bryan's position:** 'He's a liar' - he just doesn't live in a tropical market where airborne material isn't all caught by the filter.
  **Reasoning:** Filtration helps but doesn't stop drain problems in high-bioload climates.
  **Source:** [Cleaning Best Practices： Condensate Drain Lines and Pans] (id: cqCjZ8Lnwuo)

- **Common teaching:** Copper and silver kill everything in the drain.
  **Bryan's position:** Copper and silver ions help against bacteria and viruses, but fungus and mold aren't really affected.
  **Reasoning:** Different microbes respond differently; in the tropics everything thrives.
  **Source:** [Cleaning Best Practices： Condensate Drain Lines and Pans] (id: cqCjZ8Lnwuo)

- **Common teaching:** Put the filter in the unit's filter slot.
  **Bryan's position:** The filter slot is the worst place; use 4-inch media filters or 2-inch filter grills throughout the house, in parallel not series, for lower face velocity and more surface area.
  **Reasoning:** Factory filter racks let bypass air around them, worsening coil fouling, IAQ, and drain backups.
  **Source:** [Cleaning Best Practices： Condensate Drain Lines and Pans] (id: cqCjZ8Lnwuo)

- **Common teaching:** Add attic insulation over a sweating register, or increase attic ventilation, to fix vent sweating.
  **Bryan's position:** Piling insulation over the vent lowers its underside surface temperature (worse if the source is underneath), and increasing attic ventilation often creates a pressure imbalance that drives more moist air into the space.
  **Reasoning:** The problem is the total moisture content of the attic air, not just heat.
  **Source:** [Condensating Vents： Q&A with Bryan Orr] (id: gjFb7u7LD-g)

- **Common teaching:** Increase blower speed to warm the vent and stop it sweating.
  **Bryan's position:** Raising blower speed warms the vent temporarily but yields higher space relative humidity long-term, so the problem returns worse because objects have absorbed more moisture.
  **Reasoning:** A warmer evaporator coil dehumidifies less.
  **Source:** [Condensating Vents： Q&A with Bryan Orr] (id: gjFb7u7LD-g)

- **Common teaching:** Liquid desiccant is applied as an open spray that mixes desiccant with the air (and picks up dirt, corrosion, changing specific gravity)
  **Bryan's position:** This is a closed-loop membrane system, not an open spray
  **Reasoning:** The membrane is both a barrier and a breathable wall selective to water vapor, preventing contamination and dilution
  **Source:** [Copeland's Revolutionary Liquid Desiccant Technology ｜ HVAC School at AHR 2025] (id: WeUL1D1UQdI)

- **Common teaching:** Right-size the equipment and you're good; don't oversize
  **Bryan's position:** Right-sizing isn't enough for humidity; you often need dedicated dehumidification
  **Reasoning:** Sensible heat ratios and equipment matches leave a latent gap, especially with VRF/mini splits
  **Source:** [Customers Buy Comfort—Why Matt Risinger Uses Dehumidification in his Homes] (id: bHG2e1XGG5E)

- **Common teaching:** A cycling/pulsing digital compressor is broken and should be replaced
  **Bryan's position:** That on/off is the digital compressor unloading by design; timing it tells you capacity demand
  **Reasoning:** Techs replaced it three years in a row not understanding varying-capacity behavior
  **Source:** [Dedicated Outdoor Air System (DOAS) 101 with Roman Baugh] (id: 7ThhG_bDPtc)

- **Common teaching:** Just dump the dehumidifier into the return (return-to-return)
  **Bryan's position:** Return-to-return is the most inefficient/ineffective install; it heats the AC coil and blows collected moisture back when the AC cycles off
  **Reasoning:** FSEC 2018 study; Florida building code only allows dedicated-return-to-supply or supply-to-supply
  **Source:** [Dehumidification Hootenanny w⧸ Chris Conway, Dustin Cole, Tim De Stasio, Chris Hughes, Nikki Krueger] (id: FhZt9xa22AI)

- **Common teaching:** Size a dehumidifier by square footage
  **Bryan's position:** Don't size dehumidifiers per square foot any more than you'd size an AC from the curb
  **Reasoning:** 70-pint rating is at 80F/60% with no ductwork; it drops to ~55 pints at 73F/60% and ~45 pints at 65F, plus static derates it
  **Source:** [Dehumidification Hootenanny w⧸ Chris Conway, Dustin Cole, Tim De Stasio, Chris Hughes, Nikki Krueger] (id: FhZt9xa22AI)

- **Common teaching:** Supply-to-supply is a great supercharged install
  **Bryan's position:** Interesting in theory, but not proven in practice and problematic in retrofits
  **Reasoning:** Pushing cold air into the dehu exposes the whole unit to cold temps; retrofits end up heating the last rooms on the run
  **Source:** [Dehumidification Hootenanny w⧸ Chris Conway, Dustin Cole, Tim De Stasio, Chris Hughes, Nikki Krueger] (id: FhZt9xa22AI)

- **Common teaching:** Gas furnaces (especially oversized ones) burn or dry the moisture out of the air.
  **Bryan's position:** The furnace does nothing to burn moisture out of the air; it only drops relative humidity by heating.
  **Reasoning:** Absolute moisture in pounds/grains is unchanged by heating; only the percentage relative to saturation drops, and outdoor-air infiltration (worse with forced air/oversizing/sealed-combustion intake) is what actually lowers moisture content.
  **Source:** [Do Furnaces Dry Out The Air？] (id: S9N14YBE2Ok)

- **Common teaching:** Use the small pre-made squiggly trap and reuse the existing drain as-is because it worked for years.
  **Bryan's position:** Pre-made traps are barely enough even level; on high stage or with any return-side static they get sucked dry, and reusing an old drain unchanged ignores that a new system changes the drain's behavior.
  **Reasoning:** High static pulls water out of the shallow pre-made trap (gurgling = air pulling through), tilting it during pitch adjustments drains it, and new equipment/aluminum coils increase condensate; build a bigger trap when you have room.
  **Source:** [Drain Planning and Fabrication] (id: oBb3E7qQh8c)

- **Common teaching:** Filter data tags telling you to change every 3 months, and aiming for perfectly pristine indoor air
  **Bryan's position:** Change intervals on the tag are arbitrary (depends on soil load and runtime) so change monthly; and perfectly clean air is neither possible nor desirable - aim to replicate clean outdoor (beach/mountain) air, not sterile air
  **Reasoning:** Change frequency depends on your home; and future episodes on asthma/immunity explain why some exposure is healthy
  **Source:** [Healthy Air & Your Home (Homeowner Education)] (id: RVOT6s6bjkg)

- **Common teaching:** An exhaust fan running in the house is 'whole-house ventilation,' and outside air is 'fresh air'; and hyper-cleaning/sterilizing makes a home healthier
  **Bryan's position:** An exhaust fan in the middle of the house is a 'fart fan,' not ventilation (real ventilation is balanced: supply + exhaust that talk to each other); it's 'outside air' not 'fresh air'; and over-sterilizing kills normal bacteria and invites something worse
  **Reasoning:** Balanced/smart ventilation is coming (ERVs, paired supply/exhaust fans, CO2-aware smart systems); killing all bacteria disrupts the microbiome you live with
  **Source:** [Healthy Housing Principals for HVAC Contractors w⧸ Joe Medosch] (id: bxxjx7aSYYQ)

- **Common teaching:** Heat rises.
  **Bryan's position:** Heat itself doesn't rise; hotter air is less dense and floats (is buoyant) in colder air, while colder, heavier air sinks.
  **Reasoning:** It is the heated matter that floats or sinks, not heat itself.
  **Source:** [Heat and Comfort Basics 3D] (id: zVEkVL36Ni4)

- **Common teaching:** If it's humid, just run the AC colder to dry the space.
  **Bryan's position:** Over-cooling to dehumidify makes RH climb toward dew point and causes exterior condensation; use reheat to dehumidify at setpoint instead.
  **Reasoning:** Cooling sensibly without removing enough moisture raises RH and risks dew-point condensation in glass and walls.
  **Source:** [Hot Gas Reheat Dehumidification] (id: eZR1JY_duOU)

- **Common teaching:** Humid/damp air is heavier than dry air.
  **Bryan's position:** Water vapor is lighter than air, so more moisture means less-dense (lighter) air; we misjudge it because we picture liquid water (fog) and because humid air feels oppressive when our bodies can't evaporate sweat.
  **Reasoning:** Water vapor 0.0472 vs dry air 0.0807 lb/ft3; clouds float, proving vapor is lighter.
  **Source:** [How Humidity Impacts The Weight of Air] (id: o1MHTQSeQ20)

- **Common teaching:** Use the air conditioner itself to condition/dry the encapsulated attic (mix attic and house air).
  **Bryan's position:** Bryan is not a fan of mixing attic air with house air; he seals the ceiling and dehumidifies the attic separately. Dustin Cole's approach of conditioning the attic works, but only because he controls moisture during construction so the attic starts dry.
  **Reasoning:** Foam can off-gas and attics have high-dew-point air; drying the attic solves many house moisture problems in a hurricane/humid market.
  **Source:** [How to Deploy a Dehum： Q&A with Bryan Orr] (id: oMBYL2iiCnQ)

- **Common teaching:** Adding a trap to make a drain look nicer is fine
  **Bryan's position:** Don't add extra traps for no reason; if a system visually has no trap it is trapped somewhere in the walls, so adding one creates a double trap.
  **Reasoning:** It wouldn't run/back up without a trap somewhere.
  **Source:** [How to Prevent Double Trapping Issues] (id: uLz-tzJyeek)

- **Common teaching:** Wire condensate switches to break the Y wire
  **Bryan's position:** In humid climates break the R wire (works in all climates); breaking Y in dry climates is a deliberate choice so the condenser cycles off and re-evaporates pan moisture.
  **Reasoning:** Re-evaporation is desirable in dry climates but undesirable in humid ones.
  **Source:** [How to Properly Pipe a Drain on a Fan Coil] (id: 3sbrTLwmNRo)

- **Common teaching:** Copper/silver in the drain pan is snake oil
  **Bryan's position:** It isn't snake oil - copper and silver create ions that inhibit bacteria, fungus, and viruses, which makes sense now that copper has been removed from all-aluminum coils.
  **Reasoning:** Documented antibacterial ion properties of the metals.
  **Source:** [How to Stop Drain Snot (Bacterial Zoogloea)] (id: 5VOffWjmWkk)

- **Common teaching:** Increase airflow/blower speed to stop a vent from sweating
  **Bryan's position:** Don't — it only warms the vent for a few days then RH climbs and sweating returns worse
  **Reasoning:** Higher airflow warms the coil, reduces dehumidification and worsens duct-leakage-driven infiltration
  **Source:** [IAQ - Humidity and Moisture Control] (id: x0ytMSfouaQ)

- **Common teaching:** Pile insulation on a sweating vent/boot to stop it
  **Bryan's position:** That makes it worse
  **Reasoning:** Insulation makes the vent surface colder so it reaches dew point faster
  **Source:** [IAQ - Humidity and Moisture Control] (id: x0ytMSfouaQ)

- **Common teaching:** Powered attic fans / whole-house fans / garage exhaust fans help
  **Bryan's position:** Avoid them in humid climates
  **Reasoning:** They depressurize and pull moist air from attic/outdoors into the house
  **Source:** [IAQ - Humidity and Moisture Control] (id: x0ytMSfouaQ)

- **Common teaching:** A good filter or add-on device will 'solve' IAQ and allergies
  **Bryan's position:** Don't over-promise; heavy allergens live low and aren't captured by the AC filter; you make air 'less dirty,' not 'clean'
  **Reasoning:** Most allergens (dander, dust mites) are heavy and settle; filtration mainly helps PM2.5/PM10
  **Source:** [IAQ Basics： Understanding Indoor Air Quality] (id: VxW2JLgGv7U)

- **Common teaching:** Ozone/'activated oxygen' air cleaners freshen air
  **Bryan's position:** Avoid producing ozone in occupied spaces
  **Reasoning:** Ozone is a reactive irritant that harms mucous membranes and worsens asthma
  **Source:** [IAQ Basics： Understanding Indoor Air Quality] (id: VxW2JLgGv7U)

- **Common teaching:** A tight filter mesh can't catch particles smaller than its pores
  **Bryan's position:** Good MERV14+ media still catches very small particles
  **Reasoning:** Fine particles move via Brownian motion and adhere to fibers
  **Source:** [IAQ Basics： Understanding Indoor Air Quality] (id: VxW2JLgGv7U)

- **Common teaching:** Bolt-on IAQ add-on components fix indoor air
  **Bryan's position:** They are no replacement for IAQ fundamentals and some produce ozone
  **Reasoning:** Fundamentals of source/pathways/filtration/ventilation/humidity are what actually work
  **Source:** [Indoor Air Quality (IAQ) Basics 3D] (id: Q51KtAtmNag)

- **Common teaching:** Tip the float switch up a little to keep the unit running when it's got water
  **Bryan's position:** That's a bad sign masking another problem (usually high static pressure)
  **Reasoning:** High static creates turbulence that jumps water over the dam; find the source
  **Source:** [Installation Best Practices： Drains and Drain Lines] (id: tYs2dqoh4Xk)

- **Common teaching:** Positive-pressure or ductless units 'can't' drain if trapped
  **Bryan's position:** They still drain when trapped, vented, and properly pitched; follow the manufacturer
  **Reasoning:** Manufacturers often recommend trapping for pressure/efficiency; trapping still flows
  **Source:** [Installation Best Practices： Drains and Drain Lines] (id: tYs2dqoh4Xk)

- **Common teaching:** A dehumidifier helps cool the house
  **Bryan's position:** It adds sensible heat — it removes moisture but increases total heat
  **Reasoning:** Compressor/fan energy makes discharge air warmer than intake
  **Source:** [Installing a Whole-Home Dehumidifier] (id: Y-OH6DLJ_RE)

- **Common teaching:** Humidifying air makes it heavier (water is heavier than air)
  **Bryan's position:** Wrong — humidified air is LESS dense; you need more cubic feet to make a pound
  **Reasoning:** At constant pressure water molecules (18 amu) displace heavier N2/O2 molecules
  **Source:** [Intro to Psychrometrics w⧸ Eugene Silberstein] (id: DDFhTjW4cWc)

- **Common teaching:** A gas furnace removes moisture from the air (so you sell a humidifier to put it back)
  **Bryan's position:** The furnace doesn't remove moisture — heating raises the air's capacity, lowering relative humidity
  **Reasoning:** Absolute humidity is unchanged; capacity increases so RH drops
  **Source:** [Intro to Psychrometrics w⧸ Eugene Silberstein] (id: DDFhTjW4cWc)

- **Common teaching:** Check the current on the blower to diagnose it.
  **Bryan's position:** Measuring current on a blower means almost nothing (and with the panel off on a variable-speed motor it isn't even a true current).
  **Reasoning:** The panel must be on for correct airflow/current, and blower amps rarely tell you anything useful.
  **Source:** [Inverter Driven Install Considerations Part 1] (id: uLGBRa6Ypq4)

- **Common teaching:** Turn the system down to run long and dehumidify better.
  **Bryan's position:** Running a system down low makes a small dehumidifier and dehumidifies very little; keep it running full-tilt and add heat back (reheat).
  **Reasoning:** You make a cold coil by starving airflow, but you also gut capacity and moisture removal; a big AC plus reheat removes far more water.
  **Source:** [Inverter Driven Install Considerations Part 1] (id: uLGBRa6Ypq4)

- **Common teaching:** A room got too humid/moldy because it was set too warm.
  **Bryan's position:** Setting the space too cold (below outdoor dew point) is often what makes it worse.
  **Reasoning:** Every interior surface drops below the outdoor dew point, so infiltrating humid air condenses in walls and hidden spaces.
  **Source:** [Inverter Driven Install Considerations Part 1] (id: uLGBRa6Ypq4)

- **Common teaching:** Whatever is growing around the vent is being blown out of the dirty ductwork.
  **Bryan's position:** The ductwork interior is clean; the growth is surface condensation fed by attic dust through an unsealed boot.
  **Reasoning:** Wiping a rag inside the supply shows a clean surface, and the growth is only where cold air reaches dew point on the ceiling/boot.
  **Source:** [Is There Mold in my Ducks! 🦆(Ducts)] (id: kPXSy-6uHGg)

- **Common teaching:** You can't oversize returns.
  **Bryan's position:** True only for overall system return; you CAN have too much zonal return in a particular area, which drives that room to negative pressure.
  **Reasoning:** Zonal over-return creates local negative pressure that pulls in unconditioned air even though total return is fine.
  **Source:** [Pressures in the Home Matter w⧸ Sam Myers at IBS] (id: zDHtjndtZsQ)

- **Common teaching:** Warm air 'holds' more water / humidity is about how much water the air can hold.
  **Bryan's position:** That's not scientifically correct; it's really about the vapor pressure of the water vapor itself, not the air's capacity.
  **Reasoning:** The wet/dry bulb relationship reflects vapor pressure fractions, not air acting as a sponge.
  **Source:** [Psychrometrics and The Magic Line 3D] (id: kZHIDD0qYH8)

- **Common teaching:** Humid air is heavier than dry air.
  **Bryan's position:** Humid air is LIGHTER than dry air.
  **Reasoning:** Water vapor (18) is lighter than N2 (28) and O2 (32), so moist air rises - which is why moisture content is higher near a room's peak and why clouds form.
  **Source:** [Psychrometrics, Humidity and Moisture Control Part 1] (id: zDnsJ4kWzxI)

- **Common teaching:** Speed up airflow (or use thicker duct insulation) to raise supply temperature and stop duct sweating.
  **Bryan's position:** That's a fool's errand; the duct's exterior surface temperature depends on the conditions AROUND the duct, not the air inside it or the R-value.
  **Reasoning:** Per the CondEx data: R6->R8 raises surface temp <2F, outdoor temp +5F raises it 4F, but supply air +5F raises surface temp only 1F.
  **Source:** [Psychrometrics, Humidity and Moisture Control Part 1] (id: zDnsJ4kWzxI)

- **Common teaching:** Powered attic ventilation fans / bringing in outdoor 'fresh' air fix attic moisture; a variable-speed AC will solve the humidity problem.
  **Bryan's position:** Powered attic fans depressurize the house and spike indoor RH/loads; outdoor air adds moisture; a variable-speed AC helps comfort/RH a little but won't solve a real moisture problem.
  **Reasoning:** You must remove moisture (seal + dehumidify the attic), not just move air or match load.
  **Source:** [Psychrometrics, Humidity and Moisture Control Part 1] (id: zDnsJ4kWzxI)

- **Common teaching:** Leaving the fan in the ON position causes humidity mainly from re-evaporation off the coil and drain pan.
  **Bryan's position:** That's only a fraction; the main problem is the all-day mechanical pressure driver pulling outdoor air in through never-perfectly-sealed ducts.
  **Reasoning:** A 100 CFM bath fan left on all day means 100 CFM of humid outdoor air infiltrating all day.
  **Source:** [Psychrometrics, Humidity and Moisture Control Part 1] (id: zDnsJ4kWzxI)

- **Common teaching:** Increase airflow to warm the supply and stop vent/duct sweating.
  **Bryan's position:** That only helps locally and temporarily - it raises the space dew point (less moisture removed) and can make the whole house 'rain.'
  **Reasoning:** Warming the surface fixes one side of the equation but a warmer coil dehumidifies less, raising indoor RH.
  **Source:** [Psychrometrics, Humidity and Moisture Control Part 2] (id: yYVThICJKbQ)

- **Common teaching:** Mini-splits / variable-speed / multi-stage / inverter systems solve humidity and let you ignore bad ductwork.
  **Bryan's position:** Each was oversold and is false; mini-splits especially are often BAD dehumidifiers because they run high evaporator temps (low compression ratio) chasing high SEER.
  **Reasoning:** High evaporator temperature = poor latent removal; efficiency and dehumidification pull in opposite directions unless the coil is pegged cold.
  **Source:** [Psychrometrics, Humidity and Moisture Control Part 2] (id: yYVThICJKbQ)

- **Common teaching:** A new high-end system will dehumidify better than the old unit; close the blinds to reduce load.
  **Bryan's position:** Old weak units are often great dehumidifiers, and radiant/solar gain is actually fine (heat without moisture, increases runtime) - remove uncontrolled CONVECTIVE gains (leaks) instead.
  **Reasoning:** Long runtime + cold coil is what dehumidifies; solar load adds sensible heat that helps runtime without adding moisture.
  **Source:** [Psychrometrics, Humidity and Moisture Control Part 2] (id: yYVThICJKbQ)

- **Common teaching:** Add a little refrigerant charge to help a humidity problem / diagnose by air-temperature split.
  **Bryan's position:** 'It's either needed or it isn't - adding a little bit's not going to help anything.' Temperature split alone is inadequate; measure delivered latent capacity.
  **Reasoning:** A humidity problem is about latent removal (SHR), airflow, ducts, and envelope - not a splash of charge or a temp split.
  **Source:** [Q&A - System Won't Dehumidify？ - Short #214] (id: nEiesh6lZGo)

- **Common teaching:** A manufacturer's published U-value for a component is the whole assembly.
  **Bryan's position:** Beware — some ratings (e.g. a window) cover only the glass, not the frame; you need the whole assembly averaged (per the National Fenestration Rating Council).
  **Reasoning:** Diverse assemblies (windows, doors) must be rated over the entire surface, not just one part (per Jack Rise).
  **Source:** [Short 31 - U-Factor and R-Value] (id: FxY95_ImuKM)

- **Common teaching:** Heat rises.
  **Bryan's position:** Heat doesn't rise by itself; hotter (less dense) air floats on colder (denser) air, and the two happen simultaneously.
  **Reasoning:** Temperature is average molecular velocity; faster molecules separate, lowering density, so the parcel floats like a ball in water.
  **Source:** [Short 36 - Stack Effect] (id: gFmmswBXSqw)

- **Common teaching:** You get moisture where hot meets cold.
  **Bryan's position:** You get a moisture problem where moisture-laden air hits a lower (dew-point) temperature — dew point tracks with moisture content, not simply a hot/cold meeting.
  **Reasoning:** Warmer air holds more moisture (higher dew point) so it condenses more easily, which creates the hot-meets-cold impression.
  **Source:** [Short 7 - A Moisture Problem] (id: WgONpSfzo7Y)

- **Common teaching:** Pay ~$50 to have your ducts fogged/sanitized as a routine feel-good service.
  **Bryan's position:** Don't; if you fog internal liner or ductboard you may create a multi-thousand-dollar problem by giving microbes a substrate, and the residue just collects dust.
  **Reasoning:** Chemicals only work on hard non-porous surfaces you can fully coat; on porous liner you feed growth, and the risk (adverse reactions, residue) outweighs the reward without a clear cause.
  **Source:** [Should I Fog or ＂Sanitize＂ My Ducts？ - Short #220] (id: dLkSTsF1FKU)

- **Common teaching:** Add insulation / radiant barrier / attic ventilation to stop ducts from sweating
  **Bryan's position:** That makes ducts sweat MORE, not less
  **Reasoning:** Radiant barrier and ventilation lower attic temperature, which lowers duct surface temperature below dew point; the worst-sweating attics are well-ventilated ones with radiant barrier
  **Source:** [Stop Sweaty Ducts, Vents and Systems] (id: Vufih-WN5R4)

- **Common teaching:** A brand-new efficient system lets you set the thermostat lower ('cold enough to hang meat')
  **Bryan's position:** Lowering the setpoint makes walls, ducts and air handler more likely to condensate
  **Reasoning:** Colder everything without better dehumidification pushes surfaces below dew point
  **Source:** [Stop Sweaty Ducts, Vents and Systems] (id: Vufih-WN5R4)

- **Common teaching:** Duct the dehumidifier into the return
  **Bryan's position:** Ducting into the supply is generally preferred; ducting into the return derates the air conditioner's capacity and has been shown to be a bad way to do it in most cases
  **Reasoning:** Return ducting hurts AC capacity
  **Source:** [Testing Dehumidifiers： Q&A with Bryan Orr] (id: 7JF4pbMKk_c)

- **Common teaching:** UV doesn't do anything.
  **Bryan's position:** UV does work - UVC has been shown to deactivate genetic material of microbes; the real variables are intensity and dwell time.
  **Reasoning:** A cheap 3W USB UV light held 20 seconds over one of two identical agar dishes produced visibly less growth after 5 days.
  **Source:** [UV light and Petri Dish Demo] (id: ZveGEenhiv4)

- **Common teaching:** X13 and ECM motors are a waste of time / bad technology because some had failures
  **Bryan's position:** X13 is a great idea that solves the airside-output problem (PSC motors lose airflow as static rises); a few technical bugs don't make the technology bad
  **Reasoning:** X13 constant-torque motors produce designed CFM even under high static and use electrical energy more efficiently; early bugs (like the Trane 1500 variable-speed scroll) got worked out over time
  **Source:** [Variable Speed Motors and Why They Matter w⧸ Jamie Kitchen] (id: ddQEQxIvjhw)

- **Common teaching:** Set the dry-bulb thermostat and comfort follows
  **Bryan's position:** Swap the dry-bulb stat for one that measures both sensible and latent (wet bulb) so the system treats the air the way it actually needs, not just chasing a dry-bulb number
  **Reasoning:** In humid climates you must over-cool to dehumidify with a fixed dry-bulb stat; a total-energy sensor lets you dry the air and hold a slightly warmer, equally comfortable dry-bulb
  **Source:** [Variable Speed Motors and Why They Matter w⧸ Jamie Kitchen] (id: ddQEQxIvjhw)

- **Common teaching:** ASHRAE 62.2 says bring in outdoor air, so just dump it inside or into the AC duct
  **Bryan's position:** In Florida that unintended consequence increases home relative humidity and grows mold in the air conditioner and home; run outdoor air through filtration and a ventilating dehumidifier
  **Reasoning:** Florida outdoor dew points reach ~81F; dumping that into a house kept below 81F condenses moisture and creates growth in hidden places
  **Source:** [Ventilation in Humid Climates] (id: 4xX7xr2HT_U)

- **Common teaching:** The problem is we build houses too tight; we should go back to the good old loose houses (Jack Rise's position)
  **Bryan's position:** John: tightness plus good ventilation gives control; a leaky house gives random amounts of unfiltered air at random times at extra cost
  **Reasoning:** Leaky houses pull air across dirty wall cavities and you can't control where it comes from or goes; tight + controlled ventilation lets you deliver clean air where people are
  **Source:** [Ventilation w⧸ John Semmelhack] (id: 1ubHRgL8AB4)

- **Common teaching:** Good filtration means you don't need outdoor air
  **Bryan's position:** You cannot filter away CO2 - Bryan measured spiking CO2 at Thanksgiving dinner to headache levels; you must bring in outdoor air
  **Reasoning:** CO2 build-up from occupants and combustion (candles/chafing dishes) can only be diluted with outdoor air
  **Source:** [Ventilation w⧸ John Semmelhack] (id: 1ubHRgL8AB4)

- **Common teaching:** Raise the fan speed to stop a sweating vent
  **Bryan's position:** Raising fan speed warms the vent but hurts dehumidification; better to reduce space RH while keeping vent temperature the same
  **Reasoning:** Lower airflow gives a colder coil that removes more latent heat (lower sensible heat ratio); higher airflow warms the vent but leaves more moisture in the space
  **Source:** [Why Air Conditioning Ducts, Units, and Vents Sweat] (id: aJYC3Z3xFJM)

- **Common teaching:** Power vent an attic to cool it and stop sweating
  **Bryan's position:** Do not use power-vented attics — negative pressure draws house air into the attic and reduces home efficiency
  **Reasoning:** Well-sealed, well-insulated, radiant-barrier attics that are cooler actually trap moisture and sweat ducts worse
  **Source:** [Why Air Conditioning Ducts, Units, and Vents Sweat] (id: aJYC3Z3xFJM)

- **Common teaching:** Insulate ducts more (R6 to R8) or pile on mastic to stop sweating
  **Bryan's position:** Going R6 to R8 gains under 2°F (only ~1°F where needed); mastic is a sealer not insulation and creates thermal bridging — instead keep an air gap and control the surrounding temperature/dew point
  **Reasoning:** A half-inch air gap is ~R1; touching a cold duct to wood/drywall composites them and drops surface temperature
  **Source:** [Why Ducts Drip - Conductsation w⧸ Rick Sims] (id: LYKqGQozW8c)

- **Common teaching:** Radiant barriers and reflective/cool roofs are always beneficial
  **Bryan's position:** In hot-humid climates (Florida up to Jacksonville) expect ducts to sweat if you add a radiant barrier because you lose the radiant heat that kept ducts above dew point
  **Reasoning:** A cooler attic has less heat conducting into the duct jacket, so the surface drops to dew point
  **Source:** [Why Ducts Drip - Conductsation w⧸ Rick Sims] (id: LYKqGQozW8c)

- **Common teaching:** Bury/lay ducts under blown insulation to insulate them
  **Bryan's position:** Don't bury or lay ducts on the ceiling in climate zone 1/2 — the fluffy insulation itself gets soaking wet (80° dew point down in the fluff) unless it's R14 non-permeable
  **Reasoning:** Molecules prefer surfaces; a psychrometer stuck in the fluff reads far wetter than the attic air
  **Source:** [Why Ducts Drip - Conductsation w⧸ Rick Sims] (id: LYKqGQozW8c)

- **Common teaching:** High supply relative humidity (88%+) indicates a problem with the system
  **Bryan's position:** It's expected — the coil is at dew point so the air leaves near saturation; look at grains per pound to confirm dehumidification
  **Reasoning:** Air must reach 100% RH to condense; the inside of the duct doesn't mold because in cooling mode it gains heat, not loses it
  **Source:** [Why is The Supply Relative Humidity so High？] (id: kn8KeumYfaM)

## Diagnostic reasoning chains

**(Podcast) Drying Stuff vs. Drying Air - Humidification, Dehumidification, and Ventilation** (id: R77L6dsEE50)
- House warms 70F to 80F with no HVAC -> dew point jumps ~45F to ~65F as moisture leaves absorptive materials (small sensible change, big latent swing)
- Muggy house when ventilating -> exhaust pulls in humid outside air with no makeup-air dehumidification
- Drying a wet material -> add heat + move dry air gently across the surface, but watch that mobilized moisture doesn't condense in a cooler part of the building

**(Podcast) Psychrometrics for Fun and Profit w⧸ Jamie Kitchen** (id: ULg2hC4trUc)
- Customer says the house is cool but muggy -> the evaporator coil is too warm (above dew point) so cooling is nearly all sensible and relative humidity rises -> lower coil temperature/airflow or add dehumidification
- Replaced a PSC/undersized-duct system with a 400-CFM/ton ECM unit and comfort got worse -> the old colder-coil/low-airflow system removed more latent -> consider a smaller coil + TXV to drop the coil temperature
- SEER-13 retrofit that kept the small CR10/CR8 coil + a TXV -> became a strong latent-removal machine but sacrificed rated SEER because the coil ran colder

**A Duct Moisture Problem Diagnosis (Short)** (id: NtMoOU5fQu4)
- Growth at duct joints -> a cold surface exposed to warm humid attic air through a taped gap -> condensation + dust -> mold.

**A Few Condensate Considerations** (id: -JSdAMuwbig)
- Drain repeatedly clogs but isn't dirty -> suspect a double trap from sagged/unbraced PVC or chase misalignment.
- Water at the float switch but the drain isn't backed up -> platform sag, high negative static (sucking air/turbulence), or a mis-reconfigured horizontal pan.

**A Walk Through the Residential Design Series (ACCA Manuals J, S, and D) with Ed Janowiak** (id: qRhSAfirHJE)
- AC observed short-cycling on a 'design day' -> are you accounting for sun (a 3.5-ton full-sun load is a 2.5-ton cloudy load in the same house)? It's a moving target, so design to the design-day target.
- Sensible heat ratio: a 10K unit at 0.75 SHR (~400 CFM/ton) makes 7500 sensible + 2500 latent; speed the air up = more total/sensible, less latent, more efficient; slow it down = more latent, less efficient (why mini-splits in basements aren't dehumidifiers).

**Advanced Ventilation w⧸ CERV2** (id: 5lyiz-YjwmQ)
- Reversing-valve heat pump replaces the ERV core: extract heat from exhaust air (below freezing when cold) and move it to incoming fresh air; in summer condense water out of incoming air and reject to exhaust.
- Recirculation mode contributes ~1/3 ton of heating/cooling and reduces contagion spread by circulating and filtering particulates.

**Cleaning Best Practices： Condensate Drain Lines and Pans** (id: cqCjZ8Lnwuo)
- If you find condensation behind the electrical/air-supply panel (downstream of the evap coil), moisture is entering from outside via unsealed 'straws' - nothing should squeeze more water out of the air past the coil, so new water means an outside leak (Bergman's sponge metaphor).
- Repeated quick coil failures in tight/newer homes: stop and put an IAQ monitor in the space; elevated CO2 can form carbonic acid on coils, or open-cell foam can off-gas VOCs. Proving an IAQ cause removes the failure obligation from you.

**Cleaning a Difficult AC Condensate Drain** (id: ttfXcWIOHmM)
- Listen for movement/water flow as feedback: after flushing hot water the tech heard the slime start to move, confirming progress before the line finally cleared.

**Dedicated Outdoor Air System (DOAS) 101 with Roman Baugh** (id: 7ThhG_bDPtc)
- A 'bad contactor' fault on a digital compressor points you toward it, not tells you it's bad: the controller senses no amp draw, so check the low-voltage safeties (often a discharge-line micro leak leaving the circuit flat) before changing the contactor.
- Stuck hot-gas reheat valve: high-pressure fault when it won't call for reheat; verify by feeling if it modulates, or check for a large temperature split across the valve indicating it's not open.

**Dehumidification Hootenanny w⧸ Chris Conway, Dustin Cole, Tim De Stasio, Chris Hughes, Nikki Krueger** (id: FhZt9xa22AI)
- Before quoting a dehumidifier, take static pressure on the main system and check duct leakage; high static means run a dedicated return/supply rather than tapping the existing return, or sell duct modifications.

**Drain Planning and Fabrication** (id: oBb3E7qQh8c)
- Test drainage by pouring a large volume of water into the drain pan (not just the line) so you catch double traps, bad float-switch design, or wrong pitch the way the system actually drains.
- Angle the float switch down (with a little PVC cup/trap) rather than straight in, so a real drain problem floods the switch immediately instead of periodically overflowing the pan behind the air handler as the unit settles.

**Healthy Housing Principals for HVAC Contractors w⧸ Joe Medosch** (id: bxxjx7aSYYQ)
- The house is the largest, most-forgotten duct system: when a blower-door test fails, the plumber and electrician seal their small holes and blame the HVAC contractor - your unsealed boots/joints and duct chases running between floors are usually the leaks. Prove it (or find it) with a pressure pan while the blower door is running.
- Duct leakage drives infiltration: RETURN leakage pulls unfiltered attic/crawlspace air into the house (and can bypass the filter), while SUPPLY leakage pressurizes the house and forces makeup air in through the envelope - and over-sealing a big return can shift the dominant leak to the supply or even cause back-drafting of a nearby water-heater vent.

**Home Performance AC Changeout w⧸ UltraAire SD12** (id: Mt-ytfX9H-c)
- Verify dehumidifier is working with measureQuick: 6.2 lb/hr moisture removal x 24 = ~148 lb/day, at/near the ~150 lb/day max at those conditions -> unit performing to spec; supply air 61.4F at 64.8% RH, ~48.7F dew point confirms very dry, slightly cooled air.

**Hot Gas Reheat Dehumidification** (id: eZR1JY_duOU)
- Suspect a stuck reheat valve on an AAON unit -> force the modulating valve fully open with the controller, unplug it, drive the controller the other way while unplugged, replug and re-drive so you know the physical position matches the controller -> confirmed the valve was stuck (overshooting reheat setpoint, overheating the space).
- Diagnosing sensors on reheat controls: with ~5VDC supplied, most sensors return ~2-3VDC; a sensor reading 0V or 5V is the suspect - test each without needing to know its function; you can fake a signal with 1.5V AA batteries in series or a 9V to move an actuator and eliminate variables.

**How Humidity Impacts The Weight of Air** (id: o1MHTQSeQ20)
- Run 70F return air at 10% RH vs 70F at 80% RH over the same coil: the humid stream is less dense but its latent heat condensing on the coil holds up the coil temperature, so you measure a lower delta T with the humid air even though it weighs less per cubic foot.

**How to Deploy a Dehum： Q&A with Bryan Orr** (id: oMBYL2iiCnQ)
- Humidity complaint -> first verify AC sizing (usually oversized) and dehumidification setup -> then check ventilation sources (bath fans, kitchen hoods, dryers) -> only then add a dehumidifier -> decide attic-only vs whole-house-with-outdoor-air based on market, budget, and tightness.

**How to Prevent Double Trapping Issues** (id: uLz-tzJyeek)
- Intermittent drip / on-off-on drainage (flows 10 sec, stops 10 sec, bubbling) is the outside sign of a double trap working through a trapped air bubble.
- A system can run 8-10 hours during a big heat load, back water all the way up, then trip the float at 2-3am - so the callback happens only a couple times a month, making it hard to catch.

**IAQ - Humidity and Moisture Control** (id: x0ytMSfouaQ)
- Something sweating inside the house => (1) seal attic-air pathways (cans, vents, gaps) and (2) get RH down by fixing system airflow/dehumidification.
- Priority order in humid market: humidity > filtration > ventilation.

**IAQ Basics： Understanding Indoor Air Quality** (id: VxW2JLgGv7U)
- Pressure imbalance (closed door, more supply than return) pressurizes the room and depressurizes the rest of the house, pulling attic air (particles + moisture) in through gaps.

**Installation Best Practices： Drains and Drain Lines** (id: tYs2dqoh4Xk)
- Multiple units/dehumidifiers into a common drain at different levels => interlock them (e.g., a 9340 relay) so one shutting off doesn't overflow another.

**Intro to Psychrometrics w⧸ Eugene Silberstein** (id: DDFhTjW4cWc)
- Everything about air is on the psychrometric chart; cooling air moves right-to-left and raises RH, which is why supply-air RH reads higher than return.

**Inverter Driven Install Considerations Part 1** (id: uLGBRa6Ypq4)
- At the VRF controller read saturated coil temp (R2), superheat (R3), and EEV opening (0-2000 pulses): high superheat with the EEV wide open (2000) points to low charge or an EEV/strainer restriction.
- Comparison diagnosis: check the next room; if multiple units show high superheat with valves wide open it's a shared-charge (big bucket) issue, but a single unit points to that unit's EEV/strainer or a kink.
- Saturated suction pressure tells you how cold the coil is; superheat tells you how full it is, so a wide-open valve with high superheat means the coil isn't full enough.

**Is There Mold in my Ducks! 🦆(Ducts)** (id: kPXSy-6uHGg)
- Cold supply air contacts the ceiling/boot surfaces, they reach dew point, humidity condenses, and micro-dust from the unsealed attic boot collects on the wet surface and grows over time.

**Pressures in the Home Matter w⧸ Sam Myers at IBS** (id: zDHtjndtZsQ)
- Comfort/humidity complaint in a room -> run the system, shut the door, slide a high-resolution manometer tube under the door -> read the room-to-house pressure difference (in Pascals) -> negative room pressure implies infiltration of unconditioned air; balance supply/return to correct it.

**Psychrometrics and The Magic Line 3D** (id: kZHIDD0qYH8)
- Homeowner says 'it feels clammy' -> translate to 'latent load is too high' -> on the chart decide whether to add reheat or tweak airflow and know which direction the air state moves.
- Sweating surface (diffuser, air handler) -> its surface temperature is at/below dew point -> raise the surface temp (insulate the back of a slot diffuser, warm the room around the air handler) to stop condensation.

**Psychrometrics, Humidity and Moisture Control Part 1** (id: zDnsJ4kWzxI)
- Duct sweating in a vented attic -> the duct surface has reached dew point -> keep the duct suspended (hot air all around), don't compress the insulation (compressed insulation and Panduit-strap spots sweat), and eliminate air leaks; the real fix is to seal and dehumidify the attic.
- House humidity problem -> start with SOURCE CONTROL: humidity-activated bath fans (not left on all day), don't run a huge kitchen exhaust on high, avoid whole-house fans and powered attic ventilation, and add a dehumidifier.

**Psychrometrics, Humidity and Moisture Control Part 2** (id: yYVThICJKbQ)
- Something is sweating -> its surface is below the dew point of the surrounding air -> your only levers are raise the surface temperature or lower the air's dew point (ideally both).
- House won't dehumidify -> confirm long runtime + cold coil (right-size, correct fan speed/airflow) -> hunt source control (bath fans left on, dryer venting inside, big exhaust, open doors) -> add a properly-placed dehumidifier (feed it the wettest air, supply side).

**Q&A - System Won't Dehumidify？ - Short #214** (id: nEiesh6lZGo)
- Won't dehumidify -> MeasureQuick report to confirm delivered capacity and a low sensible heat ratio (<0.7 at high RH) -> verify airflow ~350 CFM/ton and correct staging/dehumidification setup -> duct-leakage test -> blower door -> source control (vents, fans, attic ventilation, mad air) -> can also confirm dehumidification by measuring condensate.

**Santa Fe V155 Whole House Dehumidifier Install** (id: r0MtEiJ5MYw)
- Give the dehumidifier a dedicated return (12x12 to a 10-inch collar) into the main living area, which is how these should always be installed.

**Setting Up Residential Demand Ventilation with Laser Egg** (id: 0IAo0mFJMbs)
- Setup: Laser Egg CO2 threshold set in its app; Apple HomeKit automation turns on the ERV (via a Belkin Wemo Mini smart plug) when high CO2 is detected, and keeps it on until CO2 drops below threshold plus an extra hour.

**Short 31 - U-Factor and R-Value** (id: FxY95_ImuKM)
- To find heat moved through a surface: take its square footage, its U-value (convert from R if needed), and the delta T across it, then multiply — BTU/hr = sq ft x U x delta T.

**Short 36 - Stack Effect** (id: gFmmswBXSqw)
- Air leaving a furnace is greater in volume (lower density) than air entering it, so it floats to the top, leaves a vacuum behind, and pulls colder air in at low leaks — the stack effect.

**Short 7 - A Moisture Problem** (id: WgONpSfzo7Y)
- A sweating supply vent -> ask: is supply air too cold (dirty filter, open bypass damper, restrictions, wrong blower setting) driving the boot below dew point, or is room air leaking around the boot/drywall (infiltration)? Seal and insulate accordingly.
- Over-cooling a Florida house to ~66F drives indoor temp below outdoor dew point; if the vapor barrier isn't intact, condensation forms behind the drywall on interior walls.

**Should I Fog or ＂Sanitize＂ My Ducts？ - Short #220** (id: dLkSTsF1FKU)
- Analogy to line-set flushing: a liquid flush that comes out carrying soil (then chased with a pig) demonstrably cleans; something you spray in that vaporizes and produces nothing out the other end just leaves residue behind — same logic argues against fogging.

**Smelly Ductless** (id: oJXjQBAAQeg)
- If there's visible physical soil on the coil, a light spray isn't enough — use a bib kit (from Speed Clean) to fully wash and capture; the spray-and-dwell method is for a unit that isn't actually dirty.

**Stop Sweaty Ducts, Vents and Systems** (id: Vufih-WN5R4)
- Sweating ducts/air handler (outside conditioned space) -> inspect attic/garage conditions: radiant barrier? new roof/ventilation? -> solution is seal the attic + dehumidify (foam deck or seal soffits/vents + dehumidifier), not add insulation
- Sweating vents (inside conditioned space) -> check indoor humidity: is the space losing moisture control (doors open, kitchen hoods, pool deck, low setpoint)? is the system running long enough with a cold-enough coil to dehumidify? -> seal air infiltration and improve dehumidification

**Stop Vent Sweating After HVAC Installation - Proper Sealing Methods** (id: AEr7-aQtfHk)
- New efficient system -> cold vent air (~50-56 F) -> unsealed/oversized boot lets hot humid attic air (100+ F) contact it -> dew point reached even at 78 F -> immediate dripping/sweating

**Testing Dehumidifiers： Q&A with Bryan Orr** (id: 7JF4pbMKk_c)
- Quick-and-dirty check: measure dew point in and dew point out — out should be lower. For quantitative verification, measure condensate collected over a period (accounting for full P-trap, steady entering conditions, continuous runtime).

**UV light and Petri Dish Demo** (id: ZveGEenhiv4)
- Pour agar into two petri dishes, treat one with UV for ~20 seconds, seal both, store 5 days; compare growth - UV-treated dish showed clearly less growth.

**Variable Speed Motors and Why They Matter w⧸ Jamie Kitchen** (id: ddQEQxIvjhw)
- Fixed fan + fixed compressor + latent load: the TXV/EEV opens to match the extra heat, suction pressure drifts up, evap temp rises, latent removal drops, and you balance at a point accomplishing little on either sensible or latent
- Reheat: over-cool the air to pull moisture, then reheat it with free condenser heat (or grocery rack reheat, gas, hydronic) to avoid over-cooling the space in low-sensible high-latent conditions

**Ventilation in Humid Climates** (id: 4xX7xr2HT_U)
- Old cracker-style Florida houses opened windows/breezeways so inside equaled outside - no cold surfaces, no condensation, high RH but no hidden growth; modern tight houses trap contaminants and need controlled ventilation

**Ventilation w⧸ John Semmelhack** (id: 1ubHRgL8AB4)
- Fan-cycler systems fail because low return-side static (large direct return, low fan-only setting at 25-35%) means little pressure release, so little outdoor air is pulled unless you use a big duct or a powerful dedicated fan
- An ERV's moisture transfer is not a fixed property - it transfers less moisture when indoor air is already moist, so a low-temp high-humidity rental interior won't get much dew-point knockdown

**Why Air Conditioning Ducts, Units, and Vents Sweat** (id: aJYC3Z3xFJM)
- Whenever anything sweats in an attic: check if moisture is being added (dryer/bath/kitchen exhaust venting or leaking into attic), then check vented vs unvented and surface temperature vs attic dew point, then decide whether it's easier to drop the dew point or warm the surface.

**Why Ducts Drip - Conductsation w⧸ Rick Sims** (id: LYKqGQozW8c)
- Sweating duct is rarely a service call — a tech's only real move is raising fan speed, and you need a 5°F supply-air rise for just 1°F of duct warmth; the real fixes (placement, gaps, sealing, conditioning the attic) must happen before install.
- Use data loggers: log 24 hours of attic conditions, then seal the soffit/roof caps with duct mask and watch the attic dry out — this predicts what encapsulation will do.

**Why is The Supply Relative Humidity so High？** (id: kn8KeumYfaM)
- Plot return air (81°F, 40.5% RH = 64 grains, ~54.5°F dew point) and supply air (55°F, 88% RH = 56 grains) on a psychrometric chart: the drop from 64 to 56 grains per pound proves dehumidification; the supply not being 100% RH means coil bypass factor plus duct/blower gains.

## Specific numbers Bryan cites

| Metric | Value | Context | Bryan cited a source | Episode id |
|---|---|---|---|---|
| comfort zone | ~30-60% RH at 68-78F (winter ~30% low, summer ~60% high) | broad human comfort range | yes | R77L6dsEE50 |
| ventilation latent-to-sensible ratio | ~3:1 to 5:1 (Boston ~5x) | most of the load in incoming ventilation air is moisture | yes | R77L6dsEE50 |
| temperature-driven dew point swing | 70F to 80F can move dew point ~45F to ~65F | absolute humidity is not constant with temperature | yes | R77L6dsEE50 |
| HRV prevalence | <5% of US houses | most houses have no heat-recovery ventilation | no | R77L6dsEE50 |
| grains per pound | 7000 grains/lb | absolute moisture unit | yes | ULg2hC4trUc |
| relative humidity vs heating | 70F/50% RH (~60 grains) heated to 100F drops to ~20% RH; 100F/50% RH needs ~160 grains | why heating dries air | yes | ULg2hC4trUc |
| dew point examples | ~60 grains -> ~48-49F dew point; ~80 grains -> ~61-62F | dew point fixed by grains regardless of dry bulb | yes | ULg2hC4trUc |
| comfort/energy tradeoff | a ~10% RH drop feels like a couple degrees lower dry bulb | drier air lets you raise the thermostat and save energy | yes | ULg2hC4trUc |
| measured residential airflow | average ~292 CFM/ton | real-world duct/airflow shortfalls | yes | ULg2hC4trUc |
| unsealed gap | ~4 inches, tape only | duct-to-attic connection | no | NtMoOU5fQu4 |
| horizontal drain fall | 1/4 inch per foot (some codes 1/8) | standard pitch | yes | -JSdAMuwbig |
| drain bracing | at least every 4 feet | prevent PVC sag/double traps | no | -JSdAMuwbig |
| horizontal pan overlap | 3-4 inches every direction | reconfiguring horizontal pans | no | -JSdAMuwbig |
| service call load | 5-6 (or 3-4) thorough calls/day vs 12 | argument for thoroughness | no | -JSdAMuwbig |
| comfort target | 70F winter; 75F/50% RH (~62-63F WB) summer | define comfort with numbers | yes | qRhSAfirHJE |
| design condition | 99% / 1% (not worst case) | Manual J Table 1A | yes | qRhSAfirHJE |
| airflow reference | ~400 CFM/ton | for a 0.75 SHR example | yes | qRhSAfirHJE |
| SHR example | 10,000 BTU at 0.75 SHR = 7500 sensible + 2500 latent | sensible heat ratio | yes | qRhSAfirHJE |
| oversizing limits (Manual S) | 15% single-stage, 20% two-stage, 30% VRF/inverter | don't exceed total load | yes | qRhSAfirHJE |
| sun-load sizing | 3.5 ton (full sun) vs 2.5 ton (cloudy) same house | moving target | yes | qRhSAfirHJE |
| return velocity limit | 700 fpm | Manual D velocity limit | yes | qRhSAfirHJE |
| outdoor design example | 85F | design temperature people scoff at | no | qRhSAfirHJE |
| CERV airflow | ~200 CFM | higher than typical ventilation standards, for fast flush-out | yes | 5lyiz-YjwmQ |
| compressor size | ~400-500 watt inverter reciprocating (Embraco), ~700 watt max draw on 120V | appliance-scale, quiet | yes | 5lyiz-YjwmQ |
| moisture removal | ~10-12 liters/day when very humid | summer dehumidification | yes | 5lyiz-YjwmQ |
| units in field | ~400 units across North America | second-gen CERV2, ~7-8 years on market | yes | 5lyiz-YjwmQ |
| military system example | 30-ton unit using ~12-13 lb of 410A (micro-channel condenser) | low charge lets you freeze coil / pass liquid safely | yes | 5lyiz-YjwmQ |
| coil lift needed to clean pan | a couple inches | enough play in the copper to snake tubing under a lifted coil | no | qytos4XIlPE |
| Corrosive drain-injection chemical | 45% vinegar | eats copper and aluminum coils | yes | cqCjZ8Lnwuo |
| Silver rod for drain pan | 15% silver rods (silver + copper) | preventative placed in pan, lasts life of unit | no | cqCjZ8Lnwuo |
| Prot-treat copper/silver drain rope | ~$100 install cost each | effective but cost-prohibitive | no | cqCjZ8Lnwuo |
| Recommended filter upgrade | 4-inch media filters or 2-inch filter grills | more surface area, lower face velocity | no | cqCjZ8Lnwuo |
| Common drain size | 1-1/4 inch (inch and a quarter) | the packed common drain in a large building | no | ttfXcWIOHmM |
| Feed pipe used to flush | 3/4 inch pipe | fitting + funnel used to dump hot water down | no | ttfXcWIOHmM |
| Regeneration water-circuit temps | ~60F cold side, ~120-140F hot side | Can be generated with a compressor/plate heat exchanger or captured waste heat | yes | WeUL1D1UQdI |
| Reliability target | 15-year life | vs ~10 years for a solid wheel; tested against 100,000x worst-day particulate | yes | WeUL1D1UQdI |
| Dehumidifier add-on cost | ~$2,500-3,000 on an ~$8,000 system | Framing the upsell during a comfort talk | yes | bHG2e1XGG5E |
| Mold/humidity threshold | activates above 60% (80% is where mold happens) | Can keep a vacation home at 45% RH and 90F without the AC | yes | bHG2e1XGG5E |
| Rule example | below 69F power off; above 72F power on in dry mode low airflow | e-saver 'my rules' to signal a Mitsubishi multi-zone high-wall head | no | oF1T5EH_xWg |
| Power | 24V or ~5-6V USB micro | Breez must stay plugged in | no | oF1T5EH_xWg |
| Neutral discharge target | 70-72F | Reheat coil brings ~54F cooled air back up to neutral | yes | 7ThhG_bDPtc |
| Unit size / refrigerant | 6-40 tons, R410A | DOAS/makeup air unit range | yes | 7ThhG_bDPtc |
| High-pressure cutout / demand signal | ~680 psi cutout; 0-5V DC demand (below ~1.4V compressor off) | Copeland digital scroll controller | yes | 7ThhG_bDPtc |
| Digital compressor cycle | ~15-second loaded/unloaded window | Time the on vs off to estimate capacity (e.g. mostly on = high demand) | yes | 7ThhG_bDPtc |
| Sensible heat ratio comparison | 0.62 (2.75-ton AC) vs 0.96 (0.5-ton mini split) | Lower SHR means more BTUs go to water removal | yes | FhZt9xa22AI |
| Dehumidifier derating by temp | 70 pint at 80F/60% (no duct) drops to ~55 pint at 73F/60% and ~45 pint at 65F | DOE whole-house vs portable/crawlspace test conditions | yes | FhZt9xa22AI |
| Ventilation formula (ASHRAE 62.2) | sqft x 0.01 + 7.5 CFM per (bedrooms + 1) | How much fresh air to add; ventilation is for the people | yes | FhZt9xa22AI |
| Dehu heat rejection | ~15-20F temperature rise off the unit | Heat is discharged into the living space, not outside | yes | FhZt9xa22AI |
| Reheat dehumidification cost | ~3-5x the run cost of a dehumidifier | Resistance-reheat dehumidification vs dedicated dehu at AHRI conditions | yes | FhZt9xa22AI |
| Target indoor RH in cold climates | 20s to 30s percent | Comfortable range you often want to raise humidity to using a bypass humidifier | no | S9N14YBE2Ok |
| Drain slope | 1/4 inch drop per foot | Required pitch for the drain line | yes | oBb3E7qQh8c |
| Float switch trip volume target | ~half a gallon | Want the overflow switch to stop the system almost immediately when water backs up | no | oBb3E7qQh8c |
| Trap outlet | outlet at least one pipe-diameter lower than inlet | Rule for building the trap | yes | oBb3E7qQh8c |
| UL CO detector alarm threshold | ~400 ppm carbon monoxide | why a supplemental low-level CO detector is recommended | yes | RVOT6s6bjkg |
| recommended baseline filter | MERV 8 pleated, changed monthly | good starting filtration for most homes without starving the equipment | yes | RVOT6s6bjkg |
| particle sizes discussed | PM10 vs PM2.5 | the smaller 2.5 range particles are often the more dangerous | yes | RVOT6s6bjkg |
| breaths / air volume per day | ~20,000 breaths (~30,000 gallons of air) per day | why air quality matters as much as food/water | yes | bxxjx7aSYYQ |
| house dust composition / skin shed | 70-90% of house dust is skin flakes; ~7 million flakes shed per minute | what we breathe indoors | yes | bxxjx7aSYYQ |
| particulate deaths | ~130,000 deaths attributed to particulate matter (2005 figure) | scale of the health impact | yes | bxxjx7aSYYQ |
| return-swap filtration upgrade | a ~$500-700 same-day upgrade (fans run ~$11-12/month) | low static, full-face filter upgrade as a same-day contractor offering | yes | bxxjx7aSYYQ |
| time spent indoors | ~90% indoors, ~80% at home, half of that in the bedroom | why indoor air quality dominates exposure | yes | bxxjx7aSYYQ |
| definition of a BTU | 1 BTU | heat to change one pound of water by one degree Fahrenheit | yes | zVEkVL36Ni4 |
| latent heat of vaporization of water | ~970 BTU/lb | energy to change one pound of liquid water to vapor | yes | zVEkVL36Ni4 |
| latent heat of fusion of water | ~144 BTU/lb | energy to change one pound of water solid<->liquid | yes | zVEkVL36Ni4 |
| starting relative humidity | >65% | indoor and attic on a hot summer day | yes | Mt-ytfX9H-c |
| SD12 sensible effect | ~6,000 BTU/hr removed (~0.5 ton) | slight sensible cooling rather than reheat | yes | Mt-ytfX9H-c |
| measured moisture removal | 6.2 lb/hr (x24 = ~148 lb/day) | near the ~150 lb/day max at those conditions | yes | Mt-ytfX9H-c |
| supply air condition | 61.4F, 64.8% RH, ~48.7F dew point (54F wet bulb) | cool but very low dew point off the dehumidifier | yes | Mt-ytfX9H-c |
| final space / attic conditions | space ~50% RH, attic ~40% RH with dew point in the 40s | retested a few weeks later | yes | Mt-ytfX9H-c |
| reheat airflow range | 200 to 500 CFM per ton | manufacturer-specific: Morganizer ~200, Reznor ~500 (both 100% OA units near each other) | yes | eZR1JY_duOU |
| sensor signal reference | ~5VDC supply, ~2-3VDC normal return; 0V or 5V suspect | narrowing down a bad sensor without unplugging all of them | yes | eZR1JY_duOU |
| Sporlan stepper motor diagnostic tool cost | ~$300-500 | only worth it if you diagnose stepper valves often | yes | eZR1JY_duOU |
| density of dry air | 0.0807 lb/ft3 | standard equation | yes | o1MHTQSeQ20 |
| density of water vapor | 0.0472 lb/ft3 | lighter than dry air | yes | o1MHTQSeQ20 |
| weight of hydrogen | 0.0051 | ~16x lighter than air; why water vapor is light | yes | o1MHTQSeQ20 |
| air composition | ~78% nitrogen, ~20.9% oxygen | dry air makeup | yes | o1MHTQSeQ20 |
| Bryan's attic dehumidifier duct sizes | 6-inch outdoor-air duct (older Santa Fe) / 8-inch on newer units | Santa Fe Ultra series whole-home dehumidifier | yes | oMBYL2iiCnQ |
| outdoor-air duct size | 6-inch (this older Santa Fe) / 8-inch on newer Ultra series | if an outdoor-air duct is attached | yes | lSQ0fbalQd0 |
| time in service | ~7-8 years | Bryan's home unit since realizing a latent issue | no | lSQ0fbalQd0 |
| comfort RH range | 30-60% RH (aim ~50% in humid climates, ~35-40% in dry climates) | human comfort and indoor air quality | yes | e6xC7povssE |
| sea-level pressure | 14.7 psi | weight of the atmosphere pushing on all sides | yes | e6xC7povssE |
| Target indoor RH | 50-55% | Bryan's goal for his own home | no | x0ytMSfouaQ |
| Filter static example | 20x20 MERV11, ~0.15 in.wc at 875 CFM | Undersized 1-inch filter bowing in | yes | x0ytMSfouaQ |
| PM2.5 size | < 2.5 microns | Fine particles that reach the bloodstream | no | VxW2JLgGv7U |
| Recommended media filter | MERV 14+, 4-inch | Best single IAQ upgrade | no | VxW2JLgGv7U |
| CO2 outdoor baseline | ~500 ppm; 2000 ppm causes drowsiness | Ventilation indicator | no | VxW2JLgGv7U |
| PM sizes | PM2.5 <2.5 microns, PM10 <10 microns | Particulate matter | yes | Q51KtAtmNag |
| Ideal RH | 35-60% | Humidity control | yes | Q51KtAtmNag |
| Filter | MERV 13+ | Capturing PM2.5/PM10 | yes | Q51KtAtmNag |
| Drain fall | 1/4 inch per foot (min ~1/8) | Condensate slope | no | tYs2dqoh4Xk |
| Interlock relay | 9340 relay | Interlocking dehumidifier and AC drains | no | tYs2dqoh4Xk |
| Target RH | 50-55% (set 46-48%) | Bryan's home | no | Y-OH6DLJ_RE |
| Sensible heat added | ~1860 BTU/hr | Dehumidifier reheats air | yes | Y-OH6DLJ_RE |
| RH trend | 55% down to 52% over ~1 week | Fubot monitor | yes | Y-OH6DLJ_RE |
| Density of standard air | 0.075 lb/ft^3 (1.2 oz/ft^3) | Weight of air | yes | DDFhTjW4cWc |
| Air mass moved | 2000 CFM = ~2,880,000 ft^3/day = ~26,000 lb (108 tons)/day | Blower moves massive weight | yes | DDFhTjW4cWc |
| Molecular weights | water 18, nitrogen 28, oxygen 32 amu | Why humid air is lighter | yes | DDFhTjW4cWc |
| safe-to-service voltage | below 60 volts | Daikin VRF spec before working after power-off | no | uLGBRa6Ypq4 |
| ductless discharge/suction range fully ramped | ~40 to 55°F | expected air/suction temps to validate function | no | uLGBRa6Ypq4 |
| superheat sanity check | 40° superheat = a problem; near zero when fully ramped | basic refrigeration check on ductless | no | uLGBRa6Ypq4 |
| R410a example | ~130 psi ≈ 40° saturation | controller reads temps instead of pressure | no | uLGBRa6Ypq4 |
| Daikin superheat target | ~7 to 18°, dropping to 6-7° when far off setpoint and rising to 15-20° near setpoint | variable target based on setpoint deviation to modulate active coil | no | uLGBRa6Ypq4 |
| EEV opening scale | 0 to 2000 pulses | expansion device position at the head | no | uLGBRa6Ypq4 |
| locked coil temperature | 39° or 42° | outdoor-unit setting for consistent dehumidification | no | uLGBRa6Ypq4 |
| Daikin Atmosphere humidity setpoint | ~60% RH (fixed) | drives coil temp down and starves the evaporator to extend runtime | no | uLGBRa6Ypq4 |
| Cayman outdoor dew point | 73 to 79°F | why overcooling below dew point is dangerous | no | uLGBRa6Ypq4 |
| dry-mode overcool | 7 to 8 degrees | dry mode ignores sensible temp and overcools | no | uLGBRa6Ypq4 |
| Common ceiling insulation R-value | R39 | example ceiling insulation | no | Gb2DyjTeJ_M |
| Duct insulation R-value | R4, R6, or R8 (most modern codes call for R8) | duct insulation accounted for in load calc | no | Gb2DyjTeJ_M |
| Default appliance load (Manual J) | 1200 BTU | appliance heat gain | yes | Gb2DyjTeJ_M |
| Occupant sensible gain | 230 BTU/hr per person | occupant load | yes | Gb2DyjTeJ_M |
| Occupant latent gain | 200 BTU/hr per person | occupant load | yes | Gb2DyjTeJ_M |
| 100 CFM exhaust-only ventilation winter loss | 1764 BTU | example ventilation heat loss | yes | Gb2DyjTeJ_M |
| 100 CFM infiltration summer gain | 1198 sensible + 2004 latent BTU | example summer infiltration | yes | Gb2DyjTeJ_M |
| pressure per inch water column | ~250 Pascals in one inch of water | why a high-resolution manometer is needed; room imbalances are only a few Pascals | no | zDHtjndtZsQ |
| blower door test pressure | 50 Pascals | standard blower-door depressurization, still less than one inch of water column | no | zDHtjndtZsQ |
| problem room pressure | -5 Pa (return added), -8 Pa (with bath fan) | Wilmington NC humidity case | no | zDHtjndtZsQ |
| summer comfort return-air target | 75 F at 50% RH (~64 grains/lb, dew point ~55 F) | typical target plotted on the chart | no | kZHIDD0qYH8 |
| coil/supply example | coil drops air to ~55 F (condensation), supply leaves registers ~58 F at ~90% RH | the diagonal cooling path of a forced-air system | no | kZHIDD0qYH8 |
| first psychrometric chart | 1911, Willis Carrier's 'Rational Psychrometric Formulae' paper to ASME | origin of the modern chart | yes | kZHIDD0qYH8 |
| weight of air | ~0.075 lb per cubic foot (stated in the transcript as '75 lbs', a slip) | illustrating that air is 'stuff' with weight | no | zDnsJ4kWzxI |
| molecular weights | H2O = 18, N2 = 28, O2 = 32 | why water vapor is lighter than air | yes | zDnsJ4kWzxI |
| duct surface-temp sensitivities (CondEx) | R6->R8: <2F; outdoor +5F: +4F surface; supply air +5F: +1F surface | exterior conditions dominate duct surface temperature | yes | zDnsJ4kWzxI |
| attic dew-point example | 120F at 70% RH is roughly a 95F dew point | a duct hitting 95F surface starts condensing | no | zDnsJ4kWzxI |
| attic dehumidifier size | 70-98 pint unit dropped in a sealed attic | simplest humid-climate moisture fix | no | zDnsJ4kWzxI |
| vent-sweating RH threshold | ~60% RH or above in the space | when vent sweating generally starts | no | yYVThICJKbQ |
| mini-split coil target | peg evaporator ~40F or lower | how newer units (Daikin Atmosphera) are made to dehumidify well | no | yYVThICJKbQ |
| reheat vs dehumidifier efficiency | electric-strip reheat is ~3x less efficient (a dehumidifier ~3x more efficient) for the same job | why a dedicated dehumidifier beats strip reheat | no | yYVThICJKbQ |
| humid-climate ventilation rate | ~30-40 CFM, demand-controlled (keep CO2 below ~800-1000) | minimal, controlled outdoor air rather than 100-200 CFM continuous | no | yYVThICJKbQ |
| target airflow in humid climate | ~350 CFM per ton | lower airflow favors latent (moisture) removal in humid climates | no | nEiesh6lZGo |
| sensible heat ratio | easily below 0.7 at high RH | for a properly set-up system doing good latent removal | no | nEiesh6lZGo |
| symptom | 74F set point but 80-90% indoor RH | Tim's complaint; abnormally high humidity | no | nEiesh6lZGo |
| Remote sensor wire distance | up to 100 ft | two-wire wired sensor to equipment | yes | 8x7aRDMxdyM |
| Ventilation duct size | 8-inch | upsized outdoor-air inlet on Ultra series | yes | 8x7aRDMxdyM |
| Ultra V155 warranty | 6-year | warranty highlighted | yes | 8x7aRDMxdyM |
| Old vs new ventilation duct | 6-inch to 8-inch | upsized to bring in more outdoor air | yes | xJyMoR4B3rk |
| Remote sensor RH setpoints | 40, 45, 50, 55% RH | selectable on digital control | yes | xJyMoR4B3rk |
| Filter | MERV 13 | standard on all units due to ventilation | yes | xJyMoR4B3rk |
| Indoor temp during static test | 67 degrees | reached within minutes after dropping setpoint | yes | r0MtEiJ5MYw |
| Max supply static for tie-in | 0.5 in water column | per install manual | yes | r0MtEiJ5MYw |
| Breaker/circuit | 15 amp breaker, 120V, 10-ft cord | power requirement for the V155 | yes | r0MtEiJ5MYw |
| CO2 trigger threshold | set from 1000 to 1200 ppm | ERV turn-on point | yes | 0IAo0mFJMbs |
| Run-on time after threshold | 1 hour | ERV stays on after CO2 drops | yes | 0IAo0mFJMbs |
| heat-transfer formula | BTU/hr = sq ft x U-value x delta T | Core conductive load-calc equation | yes | FxY95_ImuKM |
| example delta T | 20 degrees (75F inside, 95F outside) | Temperature difference across a wall | no | FxY95_ImuKM |
| target indoor relative humidity | 55% or below | Ventilating dehumidifier keeps RH in check and adds positive pressure to reduce infiltration | no | WgONpSfzo7Y |
| typical advertised fogging price | ~$50 | Cheap up-front but can cause expensive damage on the wrong duct type | no | dLkSTsF1FKU |
| duct surface temp swing from air temp | ~2 degrees (R8 vs R6 ~half a degree) | Changing the air temperature inside a duct barely moves its surface temperature vs attic conditions | no | Vufih-WN5R4 |
| dew point sweating threshold example | could sweat at 78 degrees | High attic humidity means surfaces can hit dew point and sweat readily | no | Vufih-WN5R4 |
| attic air temp | 100+ degrees | Hot humid latent-heat-filled attic air at the boot | no | AEr7-aQtfHk |
| vent supply air temp | ~50-56 degrees | Average temp coming out of the vents; contrast with attic air causes sweating | no | AEr7-aQtfHk |
| condensate rate example | 65 pints/day ≈ 2.71 lb/hr ≈ 14 oz in 20 minutes | measuring condensate to verify capacity (references Genry Garcia 2018 tech tip) | yes | 7JF4pbMKk_c |
| pints-to-pounds | a pint's a pound the world around (pints ≈ pounds of condensate) | converting dehumidifier rating | no | 7JF4pbMKk_c |
| UV light power | 3 watt | very low-power USB UV lamp used in demo | yes | ZveGEenhiv4 |
| UV intensity | 120 microwatts at 2-5 cm | stated intensity of the demo lamp | yes | ZveGEenhiv4 |
| UV dwell in demo | 20 seconds | exposure time over the treated dish | yes | ZveGEenhiv4 |
| petri dish incubation | 5 days | sealed and stored before checking growth | yes | ZveGEenhiv4 |
| high-humidity design airflow | 320-350 CFM per ton | latent-focused low-airflow setup in humid Florida climate | no | ddQEQxIvjhw |
| efficiency penalty of low evap | ~15-20% more energy | running a 36-38F evap vs 45-46F evap for the same cooling | no | ddQEQxIvjhw |
| condenser fan power saving | slowing a motor to 75% speed uses ~50% of the power | variable speed condenser fan control | no | ddQEQxIvjhw |
| comfort bandwidth | 3 degrees typical, up to 5-6 in some cases | fixed-speed temperature swing vs nailing the set point with variable speed | no | ddQEQxIvjhw |
| Florida outdoor dew point | about 81 degrees | dew points that risk condensing outdoor air brought into a cooled home | no | 4xX7xr2HT_U |
| comfort target | 75 degrees, 50% relative humidity | the pleasant well-filtered indoor condition to aim for | no | 4xX7xr2HT_U |
| passive house airtightness | ~5x tighter than current energy codes | blower-door airtightness target on best new construction | yes | 1ubHRgL8AB4 |
| whole-house continuous rate | ~90-100 CFM for a 3,000 sq ft, 3-4 bedroom house | ASHRAE-based ventilation calc (bedrooms, floor area, airtightness) | yes | 1ubHRgL8AB4 |
| minimum outdoor-air filtration | MERV 8 minimum, prefer MERV 13+/HEPA in fire-prone areas | ASHRAE filtration on outdoor air | yes | 1ubHRgL8AB4 |
| open fireplace exhaust | 300-400 CFM | an open fireplace with a good fire exhausts this much air, back-drafting risk with big range hoods | no | 1ubHRgL8AB4 |
| target space relative humidity | 40-55% | conditioned space comfort/anti-growth range; low 60s okay, higher is a challenge | yes | aJYC3Z3xFJM |
| attic dew point example | 93.5°F | 130°F attic at 35% RH — surfaces below this condense | yes | aJYC3Z3xFJM |
| example attic dew point in a case | 77.7°F | duct air ~48°F, only R6 insulation | yes | aJYC3Z3xFJM |
| sealed-attic conditioned result | 40% RH at 71°F | after Ultra-Aire SD12 install | yes | aJYC3Z3xFJM |
| ideal cooling-mode comfort condition | 75°F at 50% RH = 55°F dew point | sweet spot; attics often unrealistic without dehumidification | yes | aJYC3Z3xFJM |
| Florida outdoor dew points | can reach 80°F | anything under 80 condensates when ventilating with outdoor air | yes | aJYC3Z3xFJM |
| climate zone 1 average dew point | 73°F (Naples airport, 15-yr avg) | surfaces below 73°F in that attic will sweat; daily spikes can hit 80°F | yes | LYKqGQozW8c |
| surrounding-air effect | 5°F rise in surrounding air raises duct surface temp ~4°F | biggest single factor | yes | LYKqGQozW8c |
| R6 to R8 gain | under 2°F (about 1°F at 75°F) | small benefit for the added size/cost | yes | LYKqGQozW8c |
| air gap R value | ~R1 per half inch (1.5 in ≈ R1.08) | just not touching the surface gains as much as R6->R8 | yes | LYKqGQozW8c |
| closed-cell foam requirement | R13 non-permeable (closed cell) | to fully insulate your way out per Dr. Joe Lstiburek | yes | LYKqGQozW8c |
| moisture exposure from moving air | each 110 CFM adds ~1 gallon/hour (24 gal/day) | why sealing soffit/roof caps dries the attic | yes | LYKqGQozW8c |
| wet insulation R loss | 2% water by volume = half the R value; 4% = down to ~30% | once insulation gets wet it stops insulating | yes | LYKqGQozW8c |
| attic ventilation rule | 1 sq ft per 300 sq ft floor, 40% high / 60% low (Lstiburek) | just enough for convection, not wind cross-flow | yes | LYKqGQozW8c |
| return air | 81°F dry bulb, 40.5% RH, 64 grains, ~54.5°F dew point | measured with Testo 605i | yes | kn8KeumYfaM |
| supply air | 55°F dry bulb, 88% RH, 56 grains | measured 2-3 ft above the unit | yes | kn8KeumYfaM |
| coil temperature requirement | colder than 54.5°F | evaporator must be below the dew point for condensation/dehumidification | yes | kn8KeumYfaM |

## Field tips (the trick that saves time)

- Exhaust humidity at the source: run the kitchen exhaust while cooking and the bath exhaust while showering.  *(id: R77L6dsEE50)*
- To dry a wet material: add heat, use dry air, and move it gently across the surface.  *(id: R77L6dsEE50)*
- Bryan tool tip: to check charge without gauges, use an accurate thermistor line clamp (Testo 115i) plus wet/dry-bulb air measurement (Testo 605i); two 605i give delivered capacity.  *(id: R77L6dsEE50)*
- Watch that mobilizing moisture in one spot doesn't just condense in a cooler part of the building.  *(id: R77L6dsEE50)*
- Colder coil + lower air velocity = more latent (moisture) removal; higher velocity + warmer coil = sensible-only cooling.  *(id: ULg2hC4trUc)*
- Use accurate digital hygrometers (Testo 605i) over sling psychrometers, and measure system CFM (Testo 420 flow hood / 417 vane) for capacity math.  *(id: ULg2hC4trUc)*
- Commissioning (getting fan speed right) catches most future failures and comfort complaints; wrong blower settings for years leave customers sweating.  *(id: ULg2hC4trUc)*
- In high-latent climates, select components with a latent focus - a small energy penalty can prevent mold and discomfort.  *(id: ULg2hC4trUc)*
- Swamp/evaporative (adiabatic) coolers work in dry heat (~95F/15% RH) but never in Florida.  *(id: ULg2hC4trUc)*
- Seal any duct-to-attic gaps (not just tape) to keep warm humid attic air off cold duct surfaces and prevent condensation/growth.  *(id: NtMoOU5fQu4)*
- Give more fall where you can; a media/filter rack under the air handler can lift it to gain fall on the horizontal drain section.  *(id: -JSdAMuwbig)*
- Run the float switch to the platform top; quote a new platform (don't just note it) if the platform is sagging.  *(id: -JSdAMuwbig)*
- Spray a surface with rubbing alcohol and wipe with a microfiber before taping; use a tape squeegee; apply spray/contact cement to both sides and let it tack.  *(id: -JSdAMuwbig)*
- Replace saturated horizontal air handler insulation with foam board (duct board just re-saturates); clean drains thoroughly every time and quote a drain cleaning when you see goo.  *(id: -JSdAMuwbig)*
- Put a definition of comfort (specific temperature/humidity) in your contract if you sell comfort.  *(id: qRhSAfirHJE)*
- For infiltration, use a blower door (with the ducts taped off) instead of tight/average/loose guesses; duct leakage does not count as house infiltration.  *(id: qRhSAfirHJE)*
- Select equipment from expanded performance data, not the nominal model number (an '0336' can make 31,000 BTU).  *(id: qRhSAfirHJE)*
- Don't blow air on people in the occupied zone; a return that changes direction twice is quieter; use dampers in duct design.  *(id: qRhSAfirHJE)*
- Understand the fundamentals, then use software (e.g. Kwik Model) rather than doing all the Manual D math by hand.  *(id: qRhSAfirHJE)*
- Micro-channel here is protected (contained) unlike exposed rooftop coils, so its low-charge advantage applies.  *(id: 5lyiz-YjwmQ)*
- Refrigerant is denser than water (liquid phase); POE (miscible) vs alkylbenzene (immiscible, 'Italian salad dressing') behave very differently in the coil.  *(id: 5lyiz-YjwmQ)*
- On a small coil, take the two front and two back screws out and lift the coil straight out of the drain pan.  *(id: qytos4XIlPE)*
- For a bigger coil, use a strap on hook points rather than pumping the unit down.  *(id: qytos4XIlPE)*
- Clear tubing that comes with condensate pumps works well for vacuuming under a lifted coil.  *(id: qytos4XIlPE)*
- Aside on Trane air handlers: rattling check valves are usually on the condenser and are addressed with a magnet kit (not relevant on straight-cool/non-heat-pump units).  *(id: qytos4XIlPE)*
- Pan & drain spray (Refrigeration Technologies) coats the pipe interior with enzymes; glug some in and blow it through, but it's not magic.  *(id: cqCjZ8Lnwuo)*
- Where you can reach the drain end, a shop-vac plus gallons of water works well; where drains are common/go to sewer, forcing water through is the better method.  *(id: cqCjZ8Lnwuo)*
- Keep an inspection mirror and a flashlight on your person; view the evap coil through the filter door.  *(id: cqCjZ8Lnwuo)*
- Never pour bleach in the drain pan - it eats the coil.  *(id: cqCjZ8Lnwuo)*
- Seal every cabinet penetration with 'thumb gum'/sealant (Bryan dislikes cork tape) to eliminate straws.  *(id: cqCjZ8Lnwuo)*
- Bigger + thicker filter = lower face velocity = catches more and flows better.  *(id: cqCjZ8Lnwuo)*
- Leaking ducts cause double loss (lost BTUs plus a pressure imbalance that pushes/pulls air through the envelope); a CFM of air out means a CFM of air in.  *(id: cqCjZ8Lnwuo)*
- For a badly blocked drain sometimes you must cut out a section and force water/CO2/air through, then reassemble - and quote the client for that skilled work.  *(id: cqCjZ8Lnwuo)*
- For aluminum-coil white sludge, experiment with pan tabs, small pieces of copper, or 15% silver brazing-rod pieces in the drain pan; traditional antibacterial pan strips help mitigate it.  *(id: ttfXcWIOHmM)*
- Use pan & drain spray from Refrigeration Technologies regularly.  *(id: ttfXcWIOHmM)*
- Flush with hot water via a fitting/funnel on the feed pipe; give it time (last flush took about a minute to start moving).  *(id: ttfXcWIOHmM)*
- Check for dryer/bath/kitchen exhausts vented into the attic - these are silly moisture sources.  *(id: gjFb7u7LD-g)*
- For attic-sourced problems, seal the attic (closed/open-cell foam) and add a dehumidifier; ducting the dehumidifier's supply into the AC supply duct warms AC supply temps, lowers dew point, and greatly reduces condensation.  *(id: gjFb7u7LD-g)*
- Occupant behavior matters: leaving doors/windows open, and running bath/kitchen exhausts when not needed pulls in outside moisture - use humidity-sensing bath fans and ensure the dryer is properly vented.  *(id: gjFb7u7LD-g)*
- Because it's modular it can stack in different orientations; letting it handle the latent portion lets the rest of the building right-size for sensible only.  *(id: WeUL1D1UQdI)*
- For second/vacation homes, a standalone dehumidifier keeps humidity ~45% at 90F to prevent mold and musty smell while saving cooling energy.  *(id: bHG2e1XGG5E)*
- It works with a wide range of ductless equipment but probably doesn't replace the manufacturer-recommended wall controls.  *(id: oF1T5EH_xWg)*
- A DOAS has no return duct (blockoff plate) and often three coils (cooling plus microchannel reheat); powered exhaust flaps blowing cold air on your feet on the roof are normal.  *(id: 7ThhG_bDPtc)*
- For building-wide humidity or pressurization problems, look at the DOAS, not superheat/subcool on the split systems.  *(id: 7ThhG_bDPtc)*
- Recommended install (Ken Garing's) uses a dedicated return so you don't have to run the air-handler fan; use a backdraft damper set far enough from the main supply to open.  *(id: FhZt9xa22AI)*
- Use ~10-12 in of flex duct off the dehumidifier before rigid duct and soft (not threaded-rod) hangers to cut noise/vibration.  *(id: FhZt9xa22AI)*
- Don't oversize the dehu so it short-cycles; the first minutes make heat with no latent removal, and cycling off re-evaporates a little moisture.  *(id: FhZt9xa22AI)*
- To keep humidity where you want it, use a properly sized furnace or radiant strategy and seal the home and ductwork so you don't draw in outdoor air.  *(id: S9N14YBE2Ok)*
- Bring combustion air directly to the appliance via modern sealed combustion rather than pulling it from inside the space (which sucks outdoor air into the structure).  *(id: S9N14YBE2Ok)*
- Radiant heat can warm objects/occupants without overheating the air, so it drops RH less than forced air.  *(id: S9N14YBE2Ok)*
- Insulate horizontal drain runs (sweating/standing-water dew point, appearance, and code).  *(id: oBb3E7qQh8c)*
- Wire pan and auxiliary float switches in series and adjust the pan switch height so ~half a gallon trips it.  *(id: oBb3E7qQh8c)*
- Support the drain under the return box so pushing the tee down for pitch doesn't create a double trap.  *(id: oBb3E7qQh8c)*
- Bring the vent down to the bottom of the pan; vents are notoriously cut off at the platform.  *(id: oBb3E7qQh8c)*
- Disclose the copper-to-aluminum coil change to homeowners so they expect drain maintenance the old system never needed.  *(id: oBb3E7qQh8c)*
- Use a bagged vacuum (e.g. Hoover Platinum) and keep its filters clean so it doesn't vent dust back into the space.  *(id: RVOT6s6bjkg)*
- Use an indoor air quality monitor (author uses a Foobot; references Nate Adams' review) for particulates/VOCs/approx CO2, but note most don't measure CO, so keep separate UL and low-level CO detectors.  *(id: RVOT6s6bjkg)*
- Run bath fans until the space dries then shut off (humidity-sensing fans help); get regular AC maintenance since most companies don't clean equipment well, which hurts IAQ, efficiency and longevity.  *(id: RVOT6s6bjkg)*
- Before installing a higher-MERV filter, confirm (measure static) the system was designed for it - clients buy dense filters and unknowingly stress the equipment; a low-static, full-face filter area lets you run higher MERV without high static.  *(id: bxxjx7aSYYQ)*
- Cooking is one of the nastiest indoor sources (frying/combustion gases + particulates) - exhaust it outside; gas appliances tuned to cut CO can raise NO2.  *(id: bxxjx7aSYYQ)*
- Use your hypersensitive occupants as a diagnostic tool - they know their home and triggers better than you; don't tell them what they should/shouldn't notice.  *(id: bxxjx7aSYYQ)*
- Air conditioning contractors use Manual J (from ACCA, now usually in software) to calculate the BTU load a system must add or remove.  *(id: zVEkVL36Ni4)*
- Internal gains from human occupants (radiation, conduction, convection, and latent heat from exhaled breath) must be considered in load calcs and equipment sizing.  *(id: zVEkVL36Ni4)*
- Install ICM 493 protectors on the condensers because Florida high-voltage events take out inverter boards.  *(id: Mt-ytfX9H-c)*
- Put filter dryers on the inside so they don't corrode in high outdoor dew points / coastal salt air, and so they protect the indoor TXV during cool-mode run testing.  *(id: Mt-ytfX9H-c)*
- Trap and vent the condensate at the unit with proper drain pitch rather than putting the trap outside.  *(id: Mt-ytfX9H-c)*
- Don't rush a home-performance job; do a full commissioning of every piece of equipment with measureQuick.  *(id: Mt-ytfX9H-c)*
- Check refrigerant charge only in 100% cooling mode, not while modulating reheat, or the numbers are corrupted.  *(id: eZR1JY_duOU)*
- To confirm a system is in full cooling and no refrigerant is going to the reheat coil, just feel/measure the reheat coil line temperature - at ambient/off-coil temp means no reheat.  *(id: eZR1JY_duOU)*
- On very low-temp gear, watch for DC control signals and 4-20 mA loops; a milliamp clamp that reads without breaking the loop (or a signal generator) helps.  *(id: eZR1JY_duOU)*
- Don't distrust your calculations when you find water vapor is lighter than air - it truly is, by a lot.  *(id: o1MHTQSeQ20)*
- Remember humid air yields lower delta T (via latent load) even though it's less dense - relevant for delta T and enthalpy (delta H) calcs.  *(id: o1MHTQSeQ20)*
- True theme is condensate drain cleaning, but the transcript is effectively empty/garbled (single nonsensical line: 'shake the pot stir the pot'); no extractable technical content.  *(id: T7p2bkzDVZw)*
- Dumping outdoor air straight into a return box can cause condensation inside the box; induct it at ~45 degrees into the airstream instead.  *(id: oMBYL2iiCnQ)*
- Do not dump dehumidified/outdoor air into the AC return - it derates the equipment's latent capacity.  *(id: oMBYL2iiCnQ)*
- Consider measuring CO2 and humidity (e.g. Haven controls) to drive ventilation.  *(id: oMBYL2iiCnQ)*
- Use a good MERV 11 filter on the dehumidifier intake.  *(id: lSQ0fbalQd0)*
- Prefer a powered damper (over a backdraft damper) that shuts when the dehumidifier is off, to prevent recycling.  *(id: lSQ0fbalQd0)*
- For noise, set the unit on sound-foam blocks or use a sling installation.  *(id: lSQ0fbalQd0)*
- Dump several gallons of water into the pan (with the tee cap on) to force the double-trap symptom and catch pitch issues before leaving.  *(id: uLz-tzJyeek)*
- Before attaching the drain, lift the drain up and brace/strap it (2x4, vice grip, strap to a stud) so it keeps positive pitch.  *(id: uLz-tzJyeek)*
- If you must add a trap at the air handler, add a vent after it so a trapped bubble can escape and you don't create a double trap with a wall trap.  *(id: uLz-tzJyeek)*
- Always clean out the drain line on every install (non-negotiable) because new efficient systems condense far more and copper-coil antimicrobial protection is gone; use condenser cleaner with enzymes, cap, let it sit ~4 hours, flush, then test with many gallons.  *(id: uLz-tzJyeek)*
- Use a capped cleanout tee on the negative side between the unit and trap so you can run brushes/water through.  *(id: 3sbrTLwmNRo)*
- Dry-fit PVC before gluing; use non-hardening thread sealant (nyllog white) on the male drain fitting and don't overtighten (cracking).  *(id: 3sbrTLwmNRo)*
- On rooftop units vents are sometimes left shorter intentionally so backup water exits the vent rather than the pan - the opposite of an air handler/furnace.  *(id: 3sbrTLwmNRo)*
- Never route the trap or condensate switches where they block filter access; a common error is wiring switches in parallel instead of series.  *(id: 3sbrTLwmNRo)*
- Pan and drain spray and Evap Plus (refrigeration technologies) are enzyme-based, food-safe, low-odor products that break down biofilm.  *(id: 5VOffWjmWkk)*
- Anything placed in the pan (tabs, pads, copper, silver) must not inhibit water flow out of the channels or block the secondary drain / condensate switch.  *(id: 5VOffWjmWkk)*
- The sugar-in-coffee analogy: hot coffee/tea dissolves more sugar just as warmer air holds more moisture.  *(id: e6xC7povssE)*
- Higher RH reduces the body's ability to reject heat via evaporation (sweat), which is why 90F in humid Orlando feels hotter than 100F in dry Phoenix.  *(id: e6xC7povssE)*
- Install the biggest possible media filter in the overhead return riser; taper duct board to fit.  *(id: x0ytMSfouaQ)*
- Use humidity-sensing bath fans; run bath fan during showers but not all day.  *(id: x0ytMSfouaQ)*
- Seal ALL vents/cans in the house, not just the one that's dripping.  *(id: x0ytMSfouaQ)*
- Watch condensate flow as a gauge of how much moisture is actually being removed.  *(id: x0ytMSfouaQ)*
- Balance return vs supply per room (mad air) — closed doors with supply/return imbalance drive whole-house pressure problems.  *(id: x0ytMSfouaQ)*
- Offer low-level CO detectors wherever combustion appliances exist (code detectors alarm too high).  *(id: VxW2JLgGv7U)*
- Deploy before/after test-in/test-out measurements for higher-risk clients.  *(id: VxW2JLgGv7U)*
- Reduce VOCs via source control (low-VOC paints, clay plaster, off-gassed/used furniture) and ventilation.  *(id: VxW2JLgGv7U)*
- DIY box-fan filter / Comparetto cube for budget air cleaning; low-level CO monitors like Defender; in-duct Haven IAQ monitor.  *(id: Q51KtAtmNag)*
- Use a Diversitech wet switch for cases with no good pan location (e.g., downflow into a floor system).  *(id: tYs2dqoh4Xk)*
- Insulate only the horizontal drain portions (where cold water sits) in unconditioned space.  *(id: tYs2dqoh4Xk)*
- They place a float in the secondary plus a pan switch; note the inlet/first section of the drain is what usually clogs.  *(id: tYs2dqoh4Xk)*
- Keep the drain vent tall (above pan level) so a backup trips the pan switch; trim a sticky backdraft damper so it opens/closes easily (a little leakback beats sticking).  *(id: Y-OH6DLJ_RE)*
- Wire hot/common/compressor/fan; fan can run separate from compressor; a remote humidistat puck can read in a return while the controller mounts elsewhere.  *(id: Y-OH6DLJ_RE)*
- Spend ~30 minutes with a psychrometric chart by hand at least once so the tools/apps aren't magic.  *(id: DDFhTjW4cWc)*
- Don't attach tubing/units rigidly to the structure; use isolation and a little loop so inverter frequencies above 60 Hz don't resonate into the building.  *(id: uLGBRa6Ypq4)*
- Ground a cable shield or leftover conductors on one end only.  *(id: uLGBRa6Ypq4)*
- Keep panels/covers on when reading charge or current: a variable-speed blower's current is invalid with the panel off, and an open bottom cover (Lennox) bypasses the condenser and drives head pressure up.  *(id: uLGBRa6Ypq4)*
- Pull the horizontal drain pan out of a Carrier air handler when installed vertically (it just adds turbulence and collects dirt).  *(id: uLGBRa6Ypq4)*
- Never stick a temperature probe straight into a ductless head; you'll ruin the blower wheel and the probe.  *(id: uLGBRa6Ypq4)*
- Aim ductless discharge so it doesn't blow into the next head or a fence, and keep condensers clear of plants.  *(id: uLGBRa6Ypq4)*
- Keep the scale where the tanks are so charge is always weighed.  *(id: uLGBRa6Ypq4)*
- Lock the saturated suction/coil temperature for dehumidification (Daikin set-and-forget; Mitsubishi BACnet humidity point; some units a single switch, e.g., sw68) and use wired controllers with humidity logic; leave fan on Auto to maximize sensible heat ratio.  *(id: uLGBRa6Ypq4)*
- True theme: inverter-driven / ductless install considerations (noise, safety, charging, compression ratio, latent control).  *(id: uLGBRa6Ypq4)*
- Wipe a rag up inside the supply duct to demonstrate to the customer that the duct interior is clean and put their mind at ease.  *(id: kPXSy-6uHGg)*
- Seal the boot from the top (attic) when accessible; screwing the register grill in pulls a loose boot against the ceiling.  *(id: kPXSy-6uHGg)*
- Do not spray foam into the gap; it expands and pushes the boot off the ceiling.  *(id: kPXSy-6uHGg)*
- Redirect airflow so it doesn't hit the ceiling directly, and clean any dirt/growth off the grill.  *(id: kPXSy-6uHGg)*
- True theme: register/boot surface condensation and mold caused by attic air/dust infiltration (drains/condensate-adjacent).  *(id: kPXSy-6uHGg)*
- Partition walls adjacent to unconditioned garages or neighbors have a different delta-T than exterior walls.  *(id: Gb2DyjTeJ_M)*
- Overhang height and depth reduce solar radiation through windows and must be accounted for.  *(id: Gb2DyjTeJ_M)*
- West-facing windows gain the most solar heat in the hours before sundown.  *(id: Gb2DyjTeJ_M)*
- Occupant count = number of bedrooms + 1 (e.g., 3-bedroom home = 4 occupants).  *(id: Gb2DyjTeJ_M)*
- Leaky ductwork can change the load substantially; measure duct leakage with a duct tightness test.  *(id: Gb2DyjTeJ_M)*
- With the system running, shut a room's door and toss a high-resolution manometer tube underneath to read the room pressure difference - an underrated, easy test technicians skip.  *(id: zDHtjndtZsQ)*
- You need a high-resolution manometer (Pascals) - a normal gas/static-pressure manometer won't pick up the few-Pascal differences.  *(id: zDHtjndtZsQ)*
- Pair a blower door with a thermal imaging camera and a good indoor/outdoor delta-T; the blower door acts as an amplifier so leaks show up on the camera.  *(id: zDHtjndtZsQ)*
- Leakiest spots are usually the top and bottom of the envelope, especially attic chases.  *(id: zDHtjndtZsQ)*
- Use the chart's relationships (not just an app) to troubleshoot: insulating the back of a slot diffuser or warming the room around a sweating air handler both raise surface temp above dew point.  *(id: kZHIDD0qYH8)*
- When surfaces start sweating, reason from dew point (absolute saturation), not relative humidity.  *(id: kZHIDD0qYH8)*
- Seal the attic (closed-cell foam preferred in a hurricane market) AND dehumidify it - sealing alone just traps existing moisture; feed the dehumidifier the nastiest, wettest air by pulling from the very top of the attic and supplying far away.  *(id: zDnsJ4kWzxI)*
- Make the INNER duct liner the true airtight/mechanical seal (mastic or alcohol-cleaned tape + squeegee) and don't compress the outer insulation - the fluffy air is what makes insulation work, and compressed insulation/Panduit spots sweat.  *(id: zDnsJ4kWzxI)*
- If you duct a ventilating dehumidifier, put it in the SUPPLY duct, never the return (dumping dry air into the AC return turns your good dehumidifier - the AC - into a bad one).  *(id: zDnsJ4kWzxI)*
- Replace open/unsealed can lights with gasketed LED cans, seal jagged boot edges (mastic from the top or caulk below), and seal return-platform undersides - then also fix bath fans, dryer venting, and oversized kitchen exhaust.  *(id: yYVThICJKbQ)*
- Feed a dehumidifier the nastiest, wettest air (pull from the top of the attic); if ventilating, duct it into the SUPPLY - dumping dry air into the AC return turns your good dehumidifier into a bad one.  *(id: yYVThICJKbQ)*
- Bigger filters and bigger coils give slower face velocity (lower bypass factor), so the same airflow dwells longer and both filters and dehumidifies better - just get the airflow right and use only rated equipment matches.  *(id: yYVThICJKbQ)*
- A VOC/CO2 monitor helps on repeat coil-corrosion houses; the human nose is the best broad-range VOC detector - if it smells 'off,' investigate the unique materials.  *(id: yYVThICJKbQ)*
- Confirm dehumidification by measuring condensate.  *(id: nEiesh6lZGo)*
- Check for bath fans running all the time, dryer/bath fans venting inside, and powered attic (solar) fans on a vented attic - all cause pressure imbalances that drive moisture in.  *(id: nEiesh6lZGo)*
- If a contractor doesn't value airflow/duct/envelope testing, the homeowner needs to find a building-science-minded contractor rather than a box-swapper.  *(id: nEiesh6lZGo)*
- Product mention: Santa Fe 40400 SmartAire two-wire remote sensor; pairs with Ultra V-Series whole-home dehumidifiers.  *(id: 8x7aRDMxdyM)*
- A too-small ventilation duct is a choke point; the fix is a larger duct rather than a booster fan (another component, cost, and static).  *(id: xJyMoR4B3rk)*
- Low-voltage remote sensor avoids the battery-replacement hassle of wireless sensors and is paintable.  *(id: xJyMoR4B3rk)*
- Use Santa Fe's hanging kit in tight attics - clips into trusses and you pull on the ropes to level the unit.  *(id: r0MtEiJ5MYw)*
- Cut wall/ceiling grille holes from up top so a flange doesn't hit a stud you couldn't see from below.  *(id: r0MtEiJ5MYw)*
- Mastic the collar seal is the airtight layer; the outer insulation wrap and final mastic layer are just to hold insulation, not an air seal.  *(id: r0MtEiJ5MYw)*
- The V155 has magnetic filter-door access panels on each side (MERV 13); put a secondary pan and float switch under anything in an attic.  *(id: r0MtEiJ5MYw)*
- Rule of thumb: mastic what's hardest to reach first.  *(id: r0MtEiJ5MYw)*
- Laser Egg has an open API and also reads PM2.5, humidity, and temperature; tested close against Temtop M2000C and IQAir.  *(id: 0IAo0mFJMbs)*
- HomeKit requires an Apple hub (iPad, newer Apple TV, or HomePod); Android users can do similar with Amazon Alexa or Google.  *(id: 0IAo0mFJMbs)*
- In Florida, ERVs aren't ideal, but demand ventilation on CO2 can still be worthwhile.  *(id: 0IAo0mFJMbs)*
- Convert U to R (or vice versa) on the fly with 1/U = R when a load-calc program asks for the value you don't have.  *(id: FxY95_ImuKM)*
- Use whole-assembly (NFRC-rated) U-values for windows/doors, not glass-only manufacturer numbers.  *(id: FxY95_ImuKM)*
- In heating-dominated climates, prioritize sealing low (door sweeps, floor gaps) against cold infiltration.  *(id: gFmmswBXSqw)*
- In cooling-dominated climates (Florida), prioritize sealing high (ceiling penetrations, can lights, ceiling boots) against hot attic infiltration from reverse stack effect.  *(id: gFmmswBXSqw)*
- Tell the customer simply: 'I don't know what it is, ma'am, but you have a moisture problem, and I can help with that.'  *(id: WgONpSfzo7Y)*
- Fix sources: strap compressed ducts, seal/insulate the plenum top and boots, seal the gap between boot and drywall.  *(id: WgONpSfzo7Y)*
- Consider a ventilating dehumidifier to hold RH at/below 55% and lightly pressurize a leaky house.  *(id: WgONpSfzo7Y)*
- Never fog internal liner or ductboard; only flex duct or externally-wrapped sheet metal qualify per label.  *(id: dLkSTsF1FKU)*
- For between-floor flex duct that can't be easily replaced, physically clean with whiffle-ball rag attachments on fiberglass rods, then run dry rags to remove residue.  *(id: dLkSTsF1FKU)*
- Aeroseal (pressurizing and sealing the duct with a glue sealant) is a different thing entirely from antimicrobial fogging.  *(id: dLkSTsF1FKU)*
- Put a drop cloth down; spray the evaporator coil with Evap+ and the bottom row/drain pan (start furthest from the drain outlet) with Viper pan & drain.  *(id: oJXjQBAAQeg)*
- For a full cleaning with real soil, use a Speed Clean bib kit to catch runoff and prevent blow-off; these enzyme products are ideal for restaurants and mission-critical spaces because they're non-caustic and low-odor.  *(id: oJXjQBAAQeg)*
- When tempted to add insulation over a sweating vent/duct, check yourself - it makes sweating worse; seal instead.  *(id: Vufih-WN5R4)*
- Restaurants sweat vents due to doors opening, kitchen hoods and low setpoints - fix with vestibules, air curtains and positive pressurization with dehumidified air.  *(id: Vufih-WN5R4)*
- Offer customers the expensive-but-correct options (foam the deck, seal + dehumidify); it's not your job to set their budget.  *(id: Vufih-WN5R4)*
- Remove the two grill screws - you can usually see/feel hot humid attic air leaking through an improperly recessed or oversized boot hole.  *(id: AEr7-aQtfHk)*
- During service or install pre-walk, probe for concerns ('any rooms hotter?') so nothing is left on the table.  *(id: AEr7-aQtfHk)*
- Plant a seed: tell customers you'll take a look at a problem room during the attic inspection, then present options (extra drop, upsized duct) later - credibility over lack of confidence.  *(id: AEr7-aQtfHk)*
- Use a psychrometric chart or app (e.g., MeasureQuick) to plot wet bulb / dry bulb / RH in and out and read grains or pounds per cubic foot.  *(id: 7JF4pbMKk_c)*
- Higher static pressure (ducting into supply) derates the dehumidifier's capacity, so measure static and consult the manufacturer's charts.  *(id: 7JF4pbMKk_c)*
- Use a good watt meter (Bryan's current favorite: Navigator by Amprobe) to measure power at low current levels.  *(id: 7JF4pbMKk_c)*
- If you try the agar/petri demo, don't remove the lid afterward - it smells rancid.  *(id: ZveGEenhiv4)*
- Airside is the most ignored side of the industry - if you don't know your airflow, every other reading is useless  *(id: ddQEQxIvjhw)*
- A little variable-speed condenser fan control on refrigeration/ice machines maintains condensing pressure, eliminates flash gas and the need for a head-pressure hold-back valve  *(id: ddQEQxIvjhw)*
- Match capacity to load for best comfort and efficiency across residential refrigerators, gas furnaces, and AC  *(id: ddQEQxIvjhw)*
- Seek manufacturer/factory training on variable-speed sequences of operation because diagnosis is manufacturer-specific  *(id: ddQEQxIvjhw)*
- Reduce VOCs at the source: choose low-VOC, naturally sourced, domestically made carpet, paint, and furniture  *(id: 4xX7xr2HT_U)*
- House plants (e.g. a dracaena/'dollar tree') help absorb CO2 but add moisture/RH - don't overdo them  *(id: 4xX7xr2HT_U)*
- Ultra-Aire (Wisconsin, made in America) ventilating dehumidifiers are Bryan's recommended solution for bringing in outdoor air in humid climates  *(id: 4xX7xr2HT_U)*
- Code requires outdoor air once a house reaches a certain tightness - which is the tightness you want for temperature/humidity control  *(id: 4xX7xr2HT_U)*
- In humid climates precondition outdoor air with a ventilating dehumidifier or ERV before it reaches the return; positive pressurization is acceptable in hot-humid climates  *(id: 1ubHRgL8AB4)*
- In cold climates avoid positive pressurization (pushes warm moist air into walls/roof sheathing causing rot); avoid exhaust-only whole-house ventilation that pulls dirty unfiltered air through cracks  *(id: 1ubHRgL8AB4)*
- Insulate the fan-cycler outdoor-air duct to prevent winter condensation; poorly installed flex duct causes low airflow  *(id: 1ubHRgL8AB4)*
- Watch big range hoods with natural-draft combustion appliances (furnaces, water heaters, fireplaces) in tight houses - back-drafting can cause deadly CO; consider dedicated makeup air  *(id: 1ubHRgL8AB4)*
- The ASHRAE standard presumes someone actually measures the airflow to confirm the ventilation system meets design  *(id: 1ubHRgL8AB4)*
- Measure dew point with a good psychrometer (FieldPiece Job Link, Testo 605i where TD = dew point, or UEI Hub kit) and let it acclimate to the space.  *(id: aJYC3Z3xFJM)*
- Air handler radiantly cools an adjacent wall below dew point and grows mold behind it — seal, insulate and condition enclosed closets/spaces.  *(id: aJYC3Z3xFJM)*
- Really hot, well-ventilated attics rarely sweat ducts because roof heat warms the duct jacket above dew point; sweating shows up most in well-sealed, radiant-barrier attics with low attic temps.  *(id: aJYC3Z3xFJM)*
- Use the 'Psychro degree F' app in place of a psychrometric chart to find dew point from temperature and RH.  *(id: aJYC3Z3xFJM)*
- Use a two-head psychrometer (FieldPiece) to compare dew point in the blown insulation vs the open attic air.  *(id: LYKqGQozW8c)*
- Hang ducts and air handlers high on threaded rod/trapeze hangers with metal straps (low thermal mass, non-permeable) instead of laying on cold decking or using 2x4 wood hangers.  *(id: LYKqGQozW8c)*
- Put the supply (cold) duct on top and shade it with the return duct or hang it high; supply duct gain is 'reheat' and fine, but return duct gain hurts performance.  *(id: LYKqGQozW8c)*
- Seal cabinet air infiltration (romex connectors, knockouts, panel gaps) with adhesive closed-cell foam tape to make rubber-to-rubber gaskets and kill thermal bridging.  *(id: LYKqGQozW8c)*
- Replace itchy fiberglass cabinet insulation with plenum-rated closed-cell foam; for the ice-queen customer, build a foam-over-galvanized bottom panel sized to the air handler.  *(id: LYKqGQozW8c)*
- Use the Testo 605i smart probe thermo-hygrometers to verify delivered capacity and read dew point.  *(id: kn8KeumYfaM)*
- The inside of a supply duct doesn't grow mold in cooling mode because it gains (not loses) heat, so it won't condense internally.  *(id: kn8KeumYfaM)*

## Bryan's characteristic phrases on this topic

- "you got to get the heat in to get the moisture out"  *(id: R77L6dsEE50)*
- "it's going to go everywhere but it's going to stay in the cold places"  *(id: R77L6dsEE50)*
- "humidity is actually steam in the air"  *(id: ULg2hC4trUc)*
- "moist air is less dense than dry air"  *(id: ULg2hC4trUc)*
- "you just solved the symptom"  *(id: -JSdAMuwbig)*
- "make work your new favorite"  *(id: -JSdAMuwbig)*
- "a duct can't be too big"  *(id: qRhSAfirHJE)*
- "predictable results"  *(id: qRhSAfirHJE)*
- "you cannot smell healthy air you cannot smell air that has a virus in it"  *(id: 5lyiz-YjwmQ)*
- "that was that was exceptionally informative and exceptionally boring"  *(id: qytos4XIlPE)*
- "clean it till it's clean"  *(id: cqCjZ8Lnwuo)*
- "become masters of the obvious"  *(id: cqCjZ8Lnwuo)*
- "empathy does not mean not telling them the truth"  *(id: cqCjZ8Lnwuo)*
- "don't be afraid of money just say it"  *(id: cqCjZ8Lnwuo)*
- "a CFM of air out means a CFM of air in every time"  *(id: cqCjZ8Lnwuo)*
- "so you gotta do HVAC things"  *(id: ttfXcWIOHmM)*
- "make sure that you clean them until they're clean"  *(id: ttfXcWIOHmM)*
- "hotter air can hold more moisture"  *(id: gjFb7u7LD-g)*
- "stop the presses"  *(id: oF1T5EH_xWg)*
- "AC's king, dehu's queen"  *(id: FhZt9xa22AI)*
- "Let the big dog eat"  *(id: FhZt9xa22AI)*
- "latent heat removal is never efficient"  *(id: FhZt9xa22AI)*
- "cold air is always dry air in terms of absolute moisture content"  *(id: S9N14YBE2Ok)*
- "It's not a mechanical failure. It is a drain line failure."  *(id: oBb3E7qQh8c)*
- "CO and co2 are two completely different gases"  *(id: RVOT6s6bjkg)*
- "the most forgotten and largest duck system in the house is the actual house itself"  *(id: bxxjx7aSYYQ)*
- "it isn't fresh air it's actually outside air"  *(id: bxxjx7aSYYQ)*
- "it takes about 970 BTUs to change that same pound of water from liquid to a vapor"  *(id: zVEkVL36Ni4)*
- "now it acts as a moisture sink meaning that if anything that's one of the driest points in the house versus being one of the wettest points"  *(id: Mt-ytfX9H-c)*
- "you're trying to dehumidify without over cooling the space"  *(id: eZR1JY_duOU)*
- "air that has more water vapor in it if everything else is the same is actually lighter than air that does not"  *(id: o1MHTQSeQ20)*
- "water vapor is actually lighter than air and so water vapor will actually gather up here"  *(id: oMBYL2iiCnQ)*
- "if you dump it into the return of the air conditioning equipment then it derates the capacity of the equipment"  *(id: lSQ0fbalQd0)*
- "double trap issues are monsters because they aren't always showing when you're there"  *(id: uLz-tzJyeek)*
- "an air conditioning expert is someone who's an expert at conditioning air"  *(id: DDFhTjW4cWc)*
- "a pint of pound the world around"  *(id: DDFhTjW4cWc)*
- "your scale stays where your tanks are"  *(id: uLGBRa6Ypq4)*
- "saturated suction temperature suction pressure tells us how cold the evapora coil is superheat tells us how full it is"  *(id: uLGBRa6Ypq4)*
- "it costs money to get water out of the building which is why we want to keep the water from getting in the building in the first place"  *(id: uLGBRa6Ypq4)*
- "do not try to spray foam in there it'll expand and push your boot right off of the ceiling"  *(id: kPXSy-6uHGg)*
- "the building envelope is a part of the hvac system"  *(id: zDHtjndtZsQ)*
- "surfaces don't care about relative humidity, they care about absolute saturation"  *(id: kZHIDD0qYH8)*
- "Dew point is king"  *(id: kZHIDD0qYH8)*
- "facts don't have feelings"  *(id: zDnsJ4kWzxI)*
- "you don't know until you test"  *(id: nEiesh6lZGo)*
- "cold air sinks, hot air floats, just in the same way that things sink and float in water"  *(id: gFmmswBXSqw)*
- "you spend 50 bucks to create a multi thousand issue"  *(id: dLkSTsF1FKU)*
- "the point of a dehumidifier is not to uh decrease the set sensible temperature you're going to see an increase in sensible temperature"  *(id: 7JF4pbMKk_c)*
- "relative humidity is the enemy of indoor air quality"  *(id: 4xX7xr2HT_U)*
- "you build tight and you ventilate right"  *(id: 1ubHRgL8AB4)*
- "If the outside air was perfect, then you'd just open the windows"  *(id: 1ubHRgL8AB4)*
- "It's not the temperature in the attic, it's not the wet-bulb temperature, it is the dew point in the attic."  *(id: aJYC3Z3xFJM)*
- "cold air is not a malfunction"  *(id: LYKqGQozW8c)*
- "it had to be at 100% relative humidity in order to drop moisture"  *(id: kn8KeumYfaM)*

## Guest wisdom on this topic

- **Lou Harman:** Start every humidity question by asking whether you're drying air or drying stuff; the psychrometric confusion comes from mixing the two.  *(id: R77L6dsEE50)*
- **Lou Harman:** To dry stuff you must add thermal energy to mobilize the water, supply dry air, and move it gently across the surface; moisture then stays wherever it's coldest.  *(id: R77L6dsEE50)*
- **Jamie Kitchen:** Humidity is water vapor / steam in the air and carries large latent energy that rises exponentially with temperature; wet bulb (not dry bulb) tracks how the air affects the body's evaporative cooling.  *(id: ULg2hC4trUc)*
- **Jamie Kitchen:** Dew point sets the apparatus (evaporator) temperature needed to dehumidify; a coil above dew point only cools sensibly and raises relative humidity.  *(id: ULg2hC4trUc)*
- **Rick Sims:** Florida contractor's practice (shared at the symposium): when insulation inside a horizontal air handler is saturated, strip it down and replace it with taped foam-board sheets.  *(id: -JSdAMuwbig)*
- **Ed Janowiak:** Follow the whole design series for predictable results; a duct can't be too big (volume matters, velocity doesn't); size AC tight, not oversized, and select on sensible/latent BTUs, not tons.  *(id: qRhSAfirHJE)*
- **Russ King:** You get more complaints from oversized equipment than undersized; blow air in the opposite direction it wants to go so it mixes better.  *(id: qRhSAfirHJE)*
- **Jack Rise:** In the occupied zone, don't blow air on people.  *(id: qRhSAfirHJE)*
- **Build Equinox engineer:** You cannot smell healthy air, air with a virus, or chemicals that harm you over time - odor-based ventilation standards are inadequate; higher CO2/VOCs impair cognition, sleep, and healing.  *(id: 5lyiz-YjwmQ)*
- **Build Equinox engineer:** They run the world's largest residential IAQ experiment via online units - continuous field feedback replaces expensive test chambers.  *(id: 5lyiz-YjwmQ)*
- **Matt:** Designed a system that came out with high static, retested it, and is going back to fix it at a loss to learn what went wrong - treat it like a more expensive version of the mistakes techs make every day. Build confidence by doing it on your own house first (he downsized his own 3-ton to a 2-ton and it's fine).  *(id: cqCjZ8Lnwuo)*
- **class attendee (unnamed):** Drain problems start back at the air handler; on maintenance, look into the drain pan for standing water and confirm it's leveled properly, because standing water is the fastest way to grow biofilm.  *(id: cqCjZ8Lnwuo)*
- **Eric Vincent:** Followed through by dumping gallon after gallon of hot water and listening for the slime to move rather than stopping after one procedure.  *(id: ttfXcWIOHmM)*
- **Nancy:** The membrane is highly hydrophobic and needs no cleaning; it resists everything but water vapor, tested at ~100,000 times the worst day of particulate on the planet  *(id: WeUL1D1UQdI)*
- **Matt Risinger:** The system-replacement quote is the moment to have the comfort talk; if they'll spend $8,000, another ~$2,500-3,000 for a standalone dehumidifier is an easy add for comfort and health  *(id: bHG2e1XGG5E)*
- **Roman Baugh:** A commercial building's health passes or fails based on the DOAS alone; humidity or pressurization issues usually trace to it, not to the split/package units  *(id: 7ThhG_bDPtc)*
- **Chris Hughes:** Fresh-air ventilation can move the neutral pressure plane in a tight house, reducing hot humid infiltration (which mostly comes top-down through can lights in summer, not the front door)  *(id: FhZt9xa22AI)*
- **Dustin Cole:** You don't have to sell a dehumidifier hard; the customer owns the problem, so navigate them to a solution and, above all, succeed at the install to become the local hero  *(id: FhZt9xa22AI)*
- **Joe Medosch:** Infiltration you think of as an energy penalty is really a contaminant pathway - the same leaks hurting efficiency are how outdoor/attic/crawlspace pollutants reach the people breathing inside.  *(id: bxxjx7aSYYQ)*
- **Joe Medosch:** Indoor air can be far worse than the 5-7x or 2-5x figures suggest because we don't regulate or monitor it, and we keep making homes tighter while doing an awful job of ventilation.  *(id: bxxjx7aSYYQ)*
- **Eric Mele:** Common reheat configurations: divert refrigerant to a reheat coil (often a reversing-valve style without the center/suction port), a dedicated reheat circuit (like a built-in dehumidifier), or a constantly-fed reheat coil with a modulating damper (Morganizer/Trane conversion).  *(id: eZR1JY_duOU)*
- **Eric Mele:** The most common reheat faults are sensors, then modulating valves getting physically stuck or out of sync with the controller.  *(id: eZR1JY_duOU)*
- **Jonathan Jones:** Free-draw a return from the highest-humidity point (attic) and split the dehumidified supply ~2/3 to the larger system to distribute evenly.  *(id: Y-OH6DLJ_RE)*
- **Eugene Silberstein:** An air conditioning expert is 'someone who's an expert at conditioning air' — so you must actually understand air.  *(id: DDFhTjW4cWc)*
- **Eugene Silberstein:** Parking-garage analogy: heating air is like opening a second level — same cars (moisture), more capacity, so RH (percent full) drops.  *(id: DDFhTjW4cWc)*
- **Jordan:** You don't always need the fancy software; at the controller you can read the saturated coil temp, superheat and EEV position and diagnose a no-cooling call like any refrigeration system.  *(id: uLGBRa6Ypq4)*
- **Jordan:** Most VRF manufacturers let you eliminate coil-temperature modulation and hold a cold coil year-round (Daikin set-and-forget, Mitsubishi with a BACnet humidity point) to dehumidify better than single-stage equipment.  *(id: uLGBRa6Ypq4)*
- **Jordan:** The Daikin Atmosphere ductless unit has a built-in humidity sensor (fixed ~60% RH) that drives the coil temp down and starves the evaporator to increase runtime for latent removal.  *(id: uLGBRa6Ypq4)*
- **Sam Myers:** The building envelope is the container for conditioned air, so it is inherently part of the HVAC system; leaky supply ducts depressurize the structure while leaky return ducts pressurize it.  *(id: zDHtjndtZsQ)*
- **Sam Myers:** A high-resolution, accurate manometer is essential to reliably read the few-Pascal room imbalances that drive comfort/humidity issues.  *(id: zDHtjndtZsQ)*
- **Nikki:** Contractors were oversizing dehumidifiers or adding booster fans just to get the right ventilation rate; the 8-inch duct and stronger fan solve it while handling more supply static.  *(id: xJyMoR4B3rk)*
- **Jack Rise:** Reminded Bryan that R-value and U-value are the same thing inverted, and that some manufacturers rate only part of a window (glass) rather than the whole assembly.  *(id: FxY95_ImuKM)*
- **Joe Medosch:** Don't even say 'biological/organic growth' — just say they have a moisture problem, because it's factual and you can't be wrong about it or overstep licensing.  *(id: WgONpSfzo7Y)*
- **Zach:** Fogging is a last resort he essentially never does; without a specific underlying cause and a lab-confirmed report, the risk of chemical residue and adverse reactions outweighs any benefit.  *(id: dLkSTsF1FKU)*
- **Zach:** Say 'suspect microbial growth' rather than 'mold' unless there is an actual lab test.  *(id: dLkSTsF1FKU)*
- **Jamie Kitchen:** The biggest pushback on adopting variable speed is 'who's going to service it' - learn it and your job can't be outsourced or automated  *(id: ddQEQxIvjhw)*
- **Jamie Kitchen:** The best maintenance techs and installers are the ones who believe in the value of the technology; understanding the benefit drives doing the job right  *(id: ddQEQxIvjhw)*
- **John Semmelhack:** Air tightness and ventilation are about control: the amount, temperature, quality, and energy impact of outside air  *(id: 1ubHRgL8AB4)*
- **John Semmelhack:** In cold climates in tight homes, the ventilation system is often what keeps the house dry enough in winter - high RH is possible even in cold climates  *(id: 1ubHRgL8AB4)*
- **Rick Sims:** 'Cold air is not a malfunction' — manufacturers' tech support kept asking for static pressure when the real issue is a 50°F cabinet below a 73°F dew point.  *(id: LYKqGQozW8c)*
- **Rick Sims:** You can seal a Florida attic by any means and put a dehumidifier in it while keeping ceiling insulation — same concept as a sealed, dehumidified crawl space.  *(id: LYKqGQozW8c)*
- **Rick Sims:** Water molecules are highly polar and prefer to bond to surfaces; at 20% RH surfaces are already 2-3 molecules deep, and materials wet themselves via capillary action above ~90% RH.  *(id: LYKqGQozW8c)*
- **Jim Bergman:** The sponge analogy: air = sponge, its compressed size = temperature, water = moisture; the air had to be at 100% RH at the coil to drop moisture, then expands and drops RH when it warms.  *(id: kn8KeumYfaM)*

## Episodes in this compendium

| Title | Video id | Guests |
|---|---|---|
| (Podcast) Drying Stuff vs. Drying Air - Humidification, Dehumidification, and Ventilation | R77L6dsEE50 | Lou Harman, Corbett Lunsford |
| (Podcast) Psychrometrics for Fun and Profit w⧸ Jamie Kitchen | ULg2hC4trUc | Jamie Kitchen |
| A Duct Moisture Problem Diagnosis (Short) | NtMoOU5fQu4 | (solo) |
| A Few Condensate Considerations | -JSdAMuwbig | Zach, Bert, Sam |
| A Walk Through the Residential Design Series (ACCA Manuals J, S, and D) with Ed Janowiak | qRhSAfirHJE | Ed Janowiak |
| Advanced Ventilation w⧸ CERV2 | 5lyiz-YjwmQ | Unnamed Build Equinox / Newell Instruments engineer (name not stated in transcript) |
| Changing a Drain Pan the Easier Way | qytos4XIlPE | (solo) |
| Cleaning Best Practices： Condensate Drain Lines and Pans | cqCjZ8Lnwuo | Matt |
| Cleaning a Difficult AC Condensate Drain | ttfXcWIOHmM | Eric Vincent |
| Condensating Vents： Q&A with Bryan Orr | gjFb7u7LD-g | Kenton |
| Copeland's Revolutionary Liquid Desiccant Technology ｜ HVAC School at AHR 2025 | WeUL1D1UQdI | Nancy |
| Customers Buy Comfort—Why Matt Risinger Uses Dehumidification in his Homes | bHG2e1XGG5E | Matt Risinger |
| DUCTLESS Control and Humidity Hack with Cielo Breez | oF1T5EH_xWg | (solo) |
| Dedicated Outdoor Air System (DOAS) 101 with Roman Baugh | 7ThhG_bDPtc | Roman Baugh |
| Dehumidification Hootenanny w⧸ Chris Conway, Dustin Cole, Tim De Stasio, Chris Hughes, Nikki Krueger | FhZt9xa22AI | Nikki Krueger, Tim De Stasio, Dustin Cole, Chris Conway, Chris Hughes |
| Do Furnaces Dry Out The Air？ | S9N14YBE2Ok | (solo) |
| Drain Planning and Fabrication | oBb3E7qQh8c | (solo) |
| Healthy Air & Your Home (Homeowner Education) | RVOT6s6bjkg | (solo) |
| Healthy Housing Principals for HVAC Contractors w⧸ Joe Medosch | bxxjx7aSYYQ | Joe Medosch |
| Heat and Comfort Basics 3D | zVEkVL36Ni4 | (solo) |
| Home Performance AC Changeout w⧸ UltraAire SD12 | Mt-ytfX9H-c | (solo) |
| Hot Gas Reheat Dehumidification | eZR1JY_duOU | Eric Mele |
| How Humidity Impacts The Weight of Air | o1MHTQSeQ20 | (solo) |
| How to Clean Drains the #BERTLIFE way | T7p2bkzDVZw | Bert |
| How to Deploy a Dehum： Q&A with Bryan Orr | oMBYL2iiCnQ | Howard |
| How to Fix Attic Humidity Problems with Santa Fe Ultra Series Dehumidifier | lSQ0fbalQd0 | (solo) |
| How to Prevent Double Trapping Issues | uLz-tzJyeek | (solo) |
| How to Properly Pipe a Drain on a Fan Coil | 3sbrTLwmNRo | (solo) |
| How to Stop Drain Snot (Bacterial Zoogloea) | 5VOffWjmWkk | (solo) |
| Humidity Basics | e6xC7povssE | (solo) |
| IAQ - Humidity and Moisture Control | x0ytMSfouaQ | (solo) |
| IAQ Basics： Understanding Indoor Air Quality | VxW2JLgGv7U | (solo) |
| Indoor Air Quality (IAQ) Basics 3D | Q51KtAtmNag | (solo) |
| Installation Best Practices： Drains and Drain Lines | tYs2dqoh4Xk | (solo) |
| Installing a Whole-Home Dehumidifier | Y-OH6DLJ_RE | Jonathan Jones |
| Intro to Psychrometrics w⧸ Eugene Silberstein | DDFhTjW4cWc | Eugene Silberstein |
| Inverter Driven Install Considerations Part 1 | uLGBRa6Ypq4 | Jordan |
| Is There Mold in my Ducks! 🦆(Ducts) | kPXSy-6uHGg | (solo) |
| Manual J Load Calculations 3D | Gb2DyjTeJ_M | (solo) |
| Pressures in the Home Matter w⧸ Sam Myers at IBS | zDHtjndtZsQ | Sam Myers |
| Psychrometrics and The Magic Line 3D | kZHIDD0qYH8 | (solo) |
| Psychrometrics, Humidity and Moisture Control Part 1 | zDnsJ4kWzxI | (solo) |
| Psychrometrics, Humidity and Moisture Control Part 2 | yYVThICJKbQ | (solo) |
| Q&A - System Won't Dehumidify？ - Short #214 | nEiesh6lZGo | (solo) |
| Santa Fe SmartAire Remote Sensor ｜ Whole Home Dehumidifier Control Made Easy | 8x7aRDMxdyM | (solo) |
| Santa Fe Ultra V-Series Dehumidifiers： Digital Controls & Enhanced Ventilation | xJyMoR4B3rk | Nikki |
| Santa Fe V155 Whole House Dehumidifier Install | r0MtEiJ5MYw | Kyle |
| Setting Up Residential Demand Ventilation with Laser Egg | 0IAo0mFJMbs | (solo) |
| Short 31 - U-Factor and R-Value | FxY95_ImuKM | (solo) |
| Short 36 - Stack Effect | gFmmswBXSqw | (solo) |
| Short 7 - A Moisture Problem | WgONpSfzo7Y | Joe Medosch |
| Should I Fog or ＂Sanitize＂ My Ducts？ - Short #220 | dLkSTsF1FKU | Zach |
| Smelly Ductless | oJXjQBAAQeg | (solo) |
| Stop Sweaty Ducts, Vents and Systems | Vufih-WN5R4 | Bert |
| Stop Vent Sweating After HVAC Installation - Proper Sealing Methods | AEr7-aQtfHk | (solo) |
| Testing Dehumidifiers： Q&A with Bryan Orr | 7JF4pbMKk_c | Stephen |
| UV light and Petri Dish Demo | ZveGEenhiv4 | (solo) |
| Variable Speed Motors and Why They Matter w⧸ Jamie Kitchen | ddQEQxIvjhw | Jamie Kitchen |
| Ventilation in Humid Climates | 4xX7xr2HT_U | (solo) |
| Ventilation w⧸ John Semmelhack | 1ubHRgL8AB4 | John Semmelhack |
| Why Air Conditioning Ducts, Units, and Vents Sweat | aJYC3Z3xFJM | (solo) |
| Why Ducts Drip - Conductsation w⧸ Rick Sims | LYKqGQozW8c | Rick Sims |
| Why is The Supply Relative Humidity so High？ | kn8KeumYfaM | Jim Bergman |

## Change log

- 2026-07-08: Initial extraction from 63 episodes (parallel-subagent structured extraction, Opus).
