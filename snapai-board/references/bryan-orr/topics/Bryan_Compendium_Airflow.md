# Bryan Orr HVAC School - Compendium: Airflow

**Version:** v1.0  
**Date:** 2026-07-08  
**Source episodes:** 88 (of 959 total in corpus)  
**Cross-references (most co-occurring topics):** Tools and Instruments (51), Diagnostics Methodology (47), Comfort and Latent (33), Business and Trade (17), Refrigeration Cycle (5), Electrical and Controls (4)

**Attribution:** Synthesized from Bryan Orr's public HVAC School podcast for SnapAI internal reference only. Attribute Bryan Orr / HVAC School (hvacrschool.com) in any downstream use; do not imply endorsement.

---

## Overview - scope of Bryan's teaching on this topic

This compendium aggregates 88 episodes whose primary emphasis is **Airflow**. Content is extracted verbatim-faithful from the transcripts; every item cites its source episode by title and YouTube video id. No numbers or claims were invented at merge time.

Dominant secondary threads in this bucket: Tools and Instruments (51), Diagnostics Methodology (47), Comfort and Latent (33), Business and Trade (17), Refrigeration Cycle (5), Electrical and Controls (4), Guest Wisdom (3), Combustion and HX (2).

## Key technical points (Bryan's core teaching, by episode)

### #BertLife - Flex Duct Repair Terror  
*Source id: Rl2Ej7fdy1U*

- Flex duct repair under a trailer: line the metal rim with mastic, slide the inner liner over the mastic, then pull the outer jacket up and secure with panduit straps, insulate the Y, and strap the duct to keep it off the ground.
- Repair with what you have on the truck today, but quote the customer for a proper code-compliant upgrade (existing indoor-rated flex was installed outdoors/unprotected).

### (Podcast) Blower Door Testing, Building Performance & More w⧸ Corbett Lunsford  
*Source id: IlrHazYv84M*

- A home has two systems: the ENCLOSURE (air-sealing + insulation) and the ENGINES (heating/cooling/dehum/ventilation/water heating plus ducts and pipes). The enclosure is primary and wins every time, so HVAC gets blamed for comfort/noise/smell problems that are really enclosure problems.
- The blower door is the central tool to diagnose a home's enclosure: replace the front door with a calibrated fan + manometer, depressurize the house to 50 pascals (~0.2 inch w.c.), and read CFM50 (fan airflow holding 50 Pa), comparable house-to-house. It's driven by codes (2009 IECC / ARRA) and underpins IR scans, zonal pressure diagnostics, and Manual J infiltration.
- Metrics are the differentiator: testing (not opinion) wins arguments and sells work. Measure your own duct tightness, static pressure, blower door, ventilation, air balancing, and delivered capacity and you have no competition.
- Diagnostics is a distinct mindset (relationships + sequence/consequence); assign ONE person to own it rather than nominally training everyone.

### (Podcast) Common Duct Design Mistakes w⧸ Jack Rise  
*Source id: X2Y1KNFoxug*

- 0.1 is NOT how you design a duct system. Static pressure is a point-in-time reading; the FRICTION RATE = available static (after subtracting coil/filter/UV drops) x 100 / total effective length, and it's almost never 0.1 - usually 0.06 to 0.18 (the ACCA wedge), with 0.1 just the midpoint.
- Manual D uses the equal-friction method on the CRITICAL PATH (the supply outlet and return inlet with the greatest resistance, not necessarily the furthest), applies that friction rate to all runs, and balances with dampers (only one damper fully open).
- Control air with velocity differences: trunk 700-900 fpm, branch 400-600 fpm. Equal velocity means no control over where air goes. Register FACE VELOCITY is what mixes room air (primary air entrains 10-20x its volume as secondary air); returns barely move room air.
- Select the furnace blower from the 0.8 column (you'll never see 0.5 with a coil), subtract coil (~0.3) and filter (~0.25) drops for available static; below ~0.4 available static you won't land in the wedge. Fan-coil/one-piece units are stuck with the blower, so stay in the rated 0.5 column.

### (Podcast) Measuring Air Flow - Air Density and Direct Air Flow Measurement Part 2 w⧸ Jim Bergmann  
*Source id: 7lEhrcbaeGM*

- Almost no airflow tool measures volume directly - they measure velocity and convert it to volume (even a capture hood uses a pitot array). The only true volume measurement is the (approved but poor) garbage-bag fill method.
- Density dependence differs by tool: a vane anemometer measures CFM independent of air density (it's a fan, very repeatable), a hot-wire is density-DEPENDENT (it senses the mass of air cooling the wire and reads high in turbulence because spinning air crosses it repeatedly), and pitot tubes and total external static are density-dependent and need density corrections.
- Psychrometrics: an air conditioner lowers ABSOLUTE humidity but raises RELATIVE humidity in the duct (cold compact air approaching ~90% RH), which reverses as the air mixes and warms in the room. The specific heat of air (~0.24) is constant; water vapor's specific heat is about half of liquid water and a tiny fraction of the air, so humidity's effect on a hot-wire reading is minor compared to temperature.
- K-factor applies only on the grille's outlet (supply) side, where the register covers part of the free area; on the return INLET side the K-factor is 1 because all the air passes before it reaches the grille.

### (Podcast) Measuring Air Flow - Static ⧸ Capacity & ECM Motors Part 1 w⧸ Jim Bergmann  
*Source id: ryTchnFMem0*

- Static pressure is NOT a measurement of airflow; it is an indirect estimation. You need pressure to have flow but pressure doesn't guarantee flow. Total external static pressure is accurate enough only to pick the right blower tap, not to measure capacity (it can be off 10-20%).
- Measuring air is easy; measuring it accurately is hard. Static pressure, hot-wire, vane, pitot, temperature rise, and TrueFlow grid each have their own uncertainty and corrections, and some are air-density-dependent while others are independent, so you must know each method's limits and what you're measuring FOR.
- Everything comes back to mass flow: we heat/cool the mass (pounds) of air, not CFM. Standard air is 0.075 lb/ft3, 400 CFM/ton equals 30 lb/min/ton; a fan moves constant CFM at variable mass flow as density changes.
- ECM (variable-speed) motors speed up to hold constant mass flow across the coil as static/density changes, making static pressure more usable (near-constant CFM up to ~0.9 inch TESP), but ECMs overspeed and can blow apart on high-static duct systems - it's the ductwork, not the motor.

### A Common Cased Coil Issue  
*Source id: PjWScoD3NH4*

- N-shaped cased coils installed lopsided/shifted to the right starve about a third of the coil of airflow; they must be pushed to the LEFT so the drain pan overhangs and every section of the coil gets airflow.
- Correcting coil position restored performance without adding any refrigerant, proving the fault was airflow, not charge.

### A Commonly Missed Airflow Issue w⧸ Bert  
*Source id: HvhaFcc7cLQ*

- On front-facing fan coils, loose back insulation/panels get sucked against the blower and block a large portion of the intake - a super common, easily-missed airflow problem.
- Fixing it means securing the loose insulation behind the blower (strapping, glue, metal tape); you often have to remove the blower wheel to access the back.

### A Duct Up Situation with Sam Myers and Eric Kaiser  
*Source id: wmJ0QBKEbB8*

- Static pressure tells the story of restrictions in a duct system; you want a smooth decrease of static toward the end, and a sudden large change means a problem inside the duct.
- Sealing a leaky duct RAISES static pressure (leaks are a pressure relief), so low static can indicate a leaky system - always re-measure after air sealing.
- Velocity problems come from small ducts, not big ones; more free area lets air get around corners smoothly (the 'race cars around a corner' analogy).

### ACFM vs SCFM 3D  
*Source id: GgvSnm_gqt8*

- SCFM is CFM of standard air (68.3F, 0% RH, 0.075 lb per cubic foot); ACFM is the actual CFM given real temperature, humidity, and elevation, which change air weight.
- For proper system operation we really want a fairly fixed MASS flow rate (pounds of air per minute) over the coil, not just volumetric CFM - so 400 CFM/ton is only a rule of thumb.
- Humid air is LIGHTER than dry air because a water molecule (18) is lighter than nitrogen (28) and oxygen (32); hotter air and higher altitude are also less dense.

### Air Filters, They are More Complex Than You Knew w⧸ Lee Andrews  
*Source id: s4EGvkZPqgo*

- MERV (ASHRAE 52.2) rates capture across small/medium/large particles; most air is <1 micron (average ~0.4 micron), and a standard MERV 8 pleat only catches ~5-15% at 0.4 micron.
- Electrostatically-charged (coarse-fiber) filters lose their charge three ways - humidity/moisture, particulate insulating the fiber, and alcohols/diesel exhaust - dropping a MERV 8 to MERV 5-6; fine-fiber media (more, smaller fibers with loft) hold performance without relying on charge.
- Buy on total cost of ownership (TCO), not initial cost - a better filter with more surface area/pleats has lower pressure drop, lasts longer, cuts labor/disposal in half, and saves ~$13-15/year/hole in energy.

### Air Flow Diagnostics w⧸ Joseph C Henderson  
*Source id: wWN2IKAqpy4*

- Static pressure is the pressure pushing against the duct walls (velocity is through the center); duct static is like blood pressure - the silent killer - and you MUST have laminar (straight) airflow with 3-5 feet of straight duct before/after to get accurate static readings (turbulence = 'system effect').
- Measure supply and return static SEPARATELY and ADD them (return is the minus side, supply the plus side); aim for return static LOWER than supply (~0.1 return / ~0.2 supply) so the return is quiet/low-and-slow and the supply has throw.
- Amp draw is a quick airflow check: a PSC or X13 (constant-torque) motor pulling BELOW rated amps is moving less air; a constant-CFM (variable-speed) motor pulling MAX amps is ramped up like a hurricane (inefficient, no room for dirty coils).

### Air Is Stuff  
*Source id: I1jYv-jetNY*

- Air is 'stuff' - it takes up space and has mass; understanding that air is matter is key to understanding air pressure (the Earth's gravity gives air weight only because it's something).
- The balloon-in-a-bottle-with-fire demo is explained by the Ideal Gas Law (PV = nRT), not Dalton's law of partial pressures - as the fire goes out the temperature drops, so pressure drops, and high-pressure air is drawn toward the low-pressure air.
- In HVAC, high air pressure is always drawn to low air pressure - a blower wheel creates a pressure differential (low-pressure inlet side, high-pressure outlet side) that moves room air.

### Air Sealing and Static Pressure Diagnostics  
*Source id: AWecM1MfuEE*

- When you hear a whistle/abnormal noise at an air handler, think air sealing - gaps and cracks are 'straws' pulling in moist, dirty, post-filter/post-coil air, causing condensation, growth, and filter bypass; seal them (silver tape inside, masking tape on removable seams, silicone worked with alcohol).
- The blower cares about what IT sees (blower static, including the evaporator coil on a fan coil), not total external static; high static or blower-wheel fins coming apart points to airflow/static problems first.
- Zonal pressure imbalance: a closed bedroom pressurized >3 Pascals vs the rest of the house causes negative pressure elsewhere, driving attic infiltration, higher humidity, dust, and power bills - measure and advise even if the room itself is comfortable.

### Airflow & Static Pressure with Matt Bruner & Bryan Orr  
*Source id: eHzYalJXE88*

- Static pressure is NOT airflow - it's just pressure (a static pressure tip has no end hole, unlike a pitot tube); as a service tech, use static to say 'my ducts/filter/coil have too much resistance,' and use a true flow grid (or manufacturer/Evolution readout) if you want actual CFM.
- Take a doctor's mentality: diagnose and inform ('this room is hot because a 3-ton is moving 800 CFM = a 2-ton'), tell customers what a new box will and won't fix, then let them decide.
- Fan Law 2: static pressure rises with the SQUARE of airflow change - a 30% airflow increase is a ~50-60% static increase, so you can't just drop in a bigger filter and assume it's solved.

### Airflow Before Charging  
*Source id: FFYvSwCIYho*

- Get airflow right (or have solid confidence it's right) BEFORE putting gas in a system - set up air handlers/controllers correctly first, because static pressure only means something if the system is actually producing the airflow it should.
- Static tells you nothing if the equipment isn't set up for the right airflow (e.g. a fan coil left on a lower/higher tonnage tap) - low static can just mean it's making half the air; probe placement matters (a Carrier/Bryant Evolution 'total external static' readout is really blower static, so it includes a dirty coil).
- In a humid market, too much airflow is very bad (no dehumidification) - target ~350 (even 325) CFM/ton for better latent removal, accepting the trade-off that lower airflow makes the air handler/ducts/vents more likely to sweat.

### Better Duct Installation Practices - Kalos Meeting  
*Source id: 3m1eRBXDM5I*

- Flex duct performs well when fully extended (inner liner not compressed), run straight with only gentle bends, and sealed properly - think of it like a pipe with water: every bend, size change, or rib impingement creates turbulence and resistance.
- Restrictions matter most closest to the system (return, filter, main plenum); fix those first to cut total system static, and it's fine to slightly oversize runouts with a balancing damper as long as the register/diffuser is sized for the right velocity.
- You seal a flex duct at the INNER liner (air seal at the collar and duct-board connection) - mastic on the OUTSIDE is only an inspector convention, not how the Air Duct Council says to seal it; the outer jacket's job is a continuous vapor barrier.

### Blower Door Test w⧸ Chris Hughes  
*Source id: i4YuqUPmwHs*

- A depressurization blower-door test measures house tightness; ACH50 is the leakage at a 50-pascal test pressure (roughly a 20 mph wind), while ACH natural is the leakage under normal conditions (~4 pascals).
- Run a multi-point test (baseline zero, then up through ~10/25/35/45/75 pascals) so you can draw a line and INTERPOLATE back to natural infiltration - you interpolate, you don't extrapolate.

### Boost Your HVAC Ticket Size： Deploying Static Pressure Probes with MeasureQuick  
*Source id: y4y1EtgEs9w*

- Static pressure is simply how much pressure is in the duct - it's to the airflow side what suction/head pressure is to the refrigerant side; high static strains the blower and compressor, burns up motors, and costs the customer efficiency.
- Total External Static Pressure (TESP) = the return (negative) plus the supply (positive) numbers added together ignoring the signs; measure the return ABOVE the filter (to capture the filter's drop) and the supply on top of the unit.
- Deploy all 9-10 probes on every stop and feed measureQuick (TESP + tonnage + system profile) to get estimated airflow - this shifts the tech from just 'fixing the machine' to solving whole-home comfort/airflow, which is what the customer actually pays for.

### Building Science 101 for HVAC Contractors w⧸ Bill Spohn and Joe Medosch  
*Source id: jMTxblZcTzE*

- Building performance is about controlling heat, air, and moisture across a continuous enclosure; the air barrier must be continuous and in direct contact with the insulation, otherwise insulation just acts as a filter and does nothing.
- The duct system is effectively the next air barrier: supply-duct leakage depressurizes the house (pulling in attic/outdoor air and unconditioned load) while return leakage pressurizes it, so fixing one leak in isolation can create a worse problem elsewhere.
- Once you build a house tight you must ventilate it right with balanced ventilation plus dehumidification; an exhaust-only bath fan is not a ventilation strategy.

### Cutting & Installing a Rectangle Duct Connection  
*Source id: y_aTNtv_2bM*

- Measure the fill piece raw-to-raw plus 2 inches (duct slides into the drive cleats) or drive-cleat to drive-cleat directly.
- A canvas connector gives vibration isolation and the flexibility to slide a new rigid piece in where two rigid pieces wouldn't fit.
- Tape the joint for air sealing (some run a screw); keep the piece straight and leave room for drive cleats.

### Delivered Capacity Basics - Kalos Meeting  
*Source id: EJVRhznC_Ts*

- Delivered capacity needs total external static pressure (supply + return) cross-referenced to the fan/airflow chart to get system airflow, plus psychrometers in supply and return; MeasureQuick does the math.
- Put the return psychrometer in the filter door so any duct gains in the return section are reflected in a true reading.
- Do delivered capacity on every install (detailed report proving the equipment works as designed) and on AOR/callbacks to see if the equipment is doing all it can before deciding to reduce load.

### Discussing Ducts Types and Tips  
*Source id: VDJotlJj3Mo*

- Black flex vs silver flex is a trade-off: silver rejects radiant attic heat (cooler delivered air, more efficient) but is more likely to sweat; black picks up radiant heat so its jacket stays warmer and sweats less but delivers warmer air.
- Duct sweats wherever it is coolest and hits dew point: at connections, where insulation is compressed, and anywhere it touches a truss, another duct, or shades an air handler.
- Seal the inner liner to the collar properly (tape, squeegee, mastic, let it dry) and keep the outer vapor barrier fully intact and uncompressed, because a compromised vapor barrier lets water vapor in to condense on the inner liner.

### Drain Traps & Static： Q&A with Bryan Orr  
*Source id: zOpdAbQuBXM*

- On negatively pressurized air handlers (evap below the blower), high static creates high negative pressure at the condensate trap, pulling water out of the pan and overflowing the secondary switch; the fix is a deeper trap.
- Rule of thumb for negative-pressure trap depth: hold roughly double the inches of water column of negative return static (0.5 in w.c. return ~ a 1-inch trap), but the two numbers have no real physical relationship, it's a rule of thumb with a built-in safety factor.
- Return static isn't fixed (rises as filters load, especially with ECM motors), so build in a safety factor; make the trap as big as you realistically can.

### Duct DISASTER at an NBA Players Home  
*Source id: 75Q15TVoazE*

- Attic heat enters the space three ways - convection (attic air infiltrating around vents/can lights), conduction (missing insulation), and radiation (black flex picking up roof-deck heat) - and it's the cumulative load, not one thing, that causes discomfort and high bills.
- Manufacturers rate capacity at very low test static (e.g., 0.2 in w.c.), so a good clean filter alone (0.29 drop) can already put you behind the rated airflow before the ductwork is even considered.
- A poorly designed supply (flex squeezed into a small triangular box on top of the air handler) plus thermal gains creates turbulence, restriction, and a real airflow problem confirmed by the refrigerant readings and a 20F delta T that shouldn't exist.

### Duct Design for Great Results w⧸ Ed Janowiak (ACCA)  
*Source id: -KqmAQgUXY4*

- Manual D forces good duct design: the friction rate worksheet makes you fill in external static pressure, component (device) losses, available static pressure, and total effective length so the friction rate is calculated, not a magic 0.08/0.1.
- Available static pressure = external static pressure minus component losses; never start on the blower's high speed, use real coil/filter pressure drops, and compute the friction rate from ASP x 100 / TEL.
- Filter velocity and duct/fitting effective length drive real performance: keep filter face velocity to ~300 fpm, don't exceed velocity limits (return 700 fpm, supply 700-900 fpm, filter grill 300 fpm), and pick registers by throw/terminal velocity, not looks.

### Duct Prep Tips and Tricks with Elliot  
*Source id: hz-R4InhRBM*

- Clean the collars with denatured alcohol first (manufacturers oil them to condition the metal) so you get a good bond, and stretch/expand the flex before installing so the insulation won't keep expanding and sag after strapping.
- The collar-to-box connection is the most important for preventing leakage: cut the hole slightly smaller than the collar, bed the collar in mastic, push the tabs down tight, then seal the inner liner with three rings deep, mechanical tape, squeegee, a Panduit strap forward of the ridge, and a layer of mastic.

### Ductboard Plenum Replacement： Measuring, Cutting & Installing  
*Source id: DgxhPFfPlEs*

- Fabricate a duct-board plenum as four pieces where front/back are mirror images and the two sides are mirror images - flip the pieces (black side to black side) rather than cutting each individually to save time.
- Score the duck board about halfway through and slit down the middle to create a locking 'Lego-piece' lip on each side; keep the plenum face 2-4 inches back from the front so the door clears it.

### Fan Law 2 for Techs with Adam Mufich  
*Source id: NzlsB9R6mbc*

- Static pressure and airflow move together but not proportionally: Fan Law 2 says the new pressure = (CFM2/CFM1) squared x measured pressure ('what I want divided by what I have, squared, times measured duct pressure'), so a small airflow change causes a much larger static-pressure change.
- Because of the square relationship, correctly sizing (usually downsizing) equipment to reduce required airflow swings static pressure dramatically in the favorable direction across the filter, coil, and duct — and the biggest lever is dropping the required airflow.
- You can back into total external static pressure from just the duct pressures (before any equipment), then hand-select the lowest-pressure-drop coil and filter for the AHRI match so the installed system delivers correct airflow within manufacturer static-pressure specs.

### Flow Hood： How to Properly Balance an HVAC System  
*Source id: XeanFStDbyY*

- Balance a system by first measuring CFM at every supply grille with a flow hood before adjusting any manual dampers.
- Intentionally oversize/over-supply a room and add dampers so you have full control to damper down; you can always damper down but can't add air you didn't supply.
- Dampers are interactive on a shared junction/trunk: lowering one run raises the others, so you must overshoot and go back and forth to converge on target CFM.

### HVAC Belt Tension  
*Source id: rNBt7LN-8ao*

- Ideal belt tension is the LOWEST tension at which the belt will not slip at peak conditions (motor start); anything tighter just wears the belt, pulleys, and motor bearings.
- Set belt tension by adjusting the motor foot mount, NOT by adjusting the adjustable drive pulley (sheave). The sheave is only for setting airflow (halves closer = more airflow) during test-and-balance/commissioning.
- Inspect the drive and driven pulleys before replacing or adjusting a belt; worn/smooth/mis-shaped pulleys eat belts and cause squeal -- replace them (a pulley gauge helps).

### HVAC Commissioning on Steroids w⧸ Jim Bergmann & Chris Hughes  
*Source id: lvMjm3YwUY8*

- Return duct leakage is worse than supply leakage: it pulls ~120 F attic air into the return, robbing SENSIBLE capacity (which the thermostat controls), raising supply dew point and run time. Even 88 CFM of return leakage caused ~12% capacity loss (a 3-ton acting like 2.5).
- Measure delivered capacity (return-to-supply, inlet-to-outlet), not just equipment capacity. TrueFlow measures air across the filter and MeasureQuick estimates air across the evaporator coil; if they disagree (~15%) you have duct leakage between them (or a misplaced probe), and when they agree you can trust the capacity numbers.
- Airflow and duct leakage are the biggest problems in the industry, yet techs try to fix them with refrigerant charge; follow a commissioning process (ANSI/RESNET/ACCA 310: design review, total duct leakage, blower airflow, blower watt draw, refrigerant charge).

### HVAC Condensate Drain Troubleshooting： Traps, Vents & Static Pressure  
*Source id: LGgET3gRY20*

- Trap depth must match cabinet static pressure: ~2.5 in of static can suck the water out of a shallow trap, and large commercial units (5-10 ton) can need up to ~4 in of trap depth to keep from pulling air through the drain line.
- What holds a trap is the vertical WATER COLUMN (weight/gravity), not its width or length -- a 1-in-wide x 6-in-deep trap beats a 6-in-wide x 1-in-deep trap.
- Vent placement differs by equipment: on a split system the vent goes ABOVE the drain pan (so a backup trips the float switch instead of silently overflowing); on an RTU the vent goes BELOW the drain pan (so it spills onto the roof rather than backing up inside).

### Heat Rise Airflow Calculation  
*Source id: aRJH-wJZ1Gs*

- The heat-rise (temperature-rise) method solves for airflow: CFM = sensible heat capacity / (delta T x 1.08).
- The 1.08 constant is derived from air density at sea level (0.075 lb/ft3) x 60 min/hr x specific heat of dry air (0.24 BTU/lb/F).
- With electric (resistive) heat, sensible capacity is found from watts (volts x amps x power factor, PF=1 for resistive) x 3.413 BTU per watt, then plugged into the airflow formula.

### High Quality DIY Box Fan Air Purifier ＂Comparetto Cube＂  
*Source id: Y7eL2OAnqc8*

- A DIY box-fan air cleaner using four filters instead of one dramatically increases filter surface area, so the fan overcomes the airflow restriction and moves/filters far more air.
- Mounting the filter cube vertically (fan on top, filters as the base) keeps floor pollutants from being disturbed and reintroduced, and the filters serve as the base so no separate stand is needed.

### Highwall Ductless Blower Wheel Cleaning  
*Source id: 2VvoER81-co*

- How to remove and clean a highwall ductless (mini-split) blower wheel; in heavily soiled cases (common in Florida) removing the wheel gets it far cleaner than in-place cleaning.
- Disassembly order on a Mitsubishi head: flip the shroud, remove filters both sides, front cover, horizontal directional vanes, plastic clips and Phillips screws, release and drain the drain pan, loosen the blower-wheel set screw, then slide the coil forward to extract the wheel.

### How to Build a Sheet Metal Coil Case From Scratch  
*Source id: hgFafh_AFLU*

- Field-fabricating a sheet-metal coil case/plenum from scratch when replacing only the furnace under an uncased coil that must stay: build it in two pieces - a U-shape screwed in first, plus a removable front door panel.
- Because it was raining (couldn't pump down) and the system was a scroll, the coil was dropped rather than disconnecting the lineset (enough slack ~5 ft to bend it).

### How to Checkout Blower Settings Using a Manometer  
*Source id: wdnaeZkstXI*

- Use a single-port manometer comparatively: pick one measurement point, get a baseline, then watch the number go up (more airflow) or down (less airflow) as the system stages.
- Practical way to confirm a blower ramps up/down with staging, dehumidification mode, or heat/cool changes on Nest/Ecobee or communicating systems.
- As blower RPM/airflow rises, total external static across the blower also rises; verify staging at any single fixed point.

### How to Clean an Air Conditioner Blower Wheel (Fan Coil Blower Pull and Clean in 3D)  
*Source id: YwFkhTqgazM*

- A dirty blower wheel is one of the single most overlooked residential problems; dirt filling the blower cups impedes airflow and increases amperage on some motors (ECM), while PSC motors can see a rapid airflow reduction.
- Keeping the wheel clean improves blower longevity, capacity, and efficiency, so pull and clean when it starts to get dirty.

### How to Confidently Create a Duct Renovation Scope of Work w/ David Richardson  
*Source id: 5eiv-0518mQ*

- Duct renovation is a product you bring into existence through Testing -> Diagnosis -> Prescription; do NOT jump straight to repairs (that just installs a new screwed-up duct system). Measurements determine the customized scope of work.
- Two approaches: an 'air upgrade' focuses on the equipment (static pressure and fan airflow improvements), while 'duct system optimization' focuses on delivered BTUs at the register (equipment/coil selection, fitting/grille selection, balancing dampers, performance registers).
- Involve the customer - make them a detective in their own home so the scope is THEIR idea; focus on ONE thing (usually air or static pressure) because information overload makes customers freeze and default to price.

### How to Fabricate a Metal Supply Plenum From Scratch  
*Source id: EgFAL_z7P2o*

- Fabricating a supply plenum from a flat sheet: cut to size, form step tabs for screwing/slip-and-end-cap connections, and crease all bend lines so the box does not inflate or deflate when the system turns on.

### How to Make a Leak Free Canvas Duct Connector  
*Source id: gE3Dnn0u3kA*

- Fabricating a leak-free canvas (flex) duct connector: measure and cut the canvas to wrap the duct (with an overlap), form the corners with V-notches, and secure the seam so it's air-tight.
- The trick for a leak-free seam is to use super-sticky tape to hold everything together and take stress off the caulk, so the caulk does the actual air sealing; add a few screws through the caulk without over-tightening.

### How to Make a Metal Duct Transition in the Field  
*Source id: rO4yqiWjOtU*

- Building a sheet-metal transition in the field (e.g. furnace to coil/plenum): put S-locks/strips around both openings (S pointed to the outside so metal slides in easily), measure height and widest points adding an inch each way, cut, mark where the S-locks hit, fold, notch corners, and slide the pieces in.
- Start with the hardest piece to reach (usually the back) and finish on the easiest side (front or a side); pre-fold back corners so the side pieces slide into the fold.

### How to Make an Indoor Air Cleaner the Cheap and Easy Way  
*Source id: gToHQvORNHs*

- A box-fan filter is a cheap, fast way to filter indoor air (created during the IAQ/COVID concern when people couldn't get in-duct filtration installed): tape a deep MERV 13 filter to the intake side of a box fan and air-seal all four sides so nothing bypasses the filter.
- Run it on a lower speed (speed 2) to protect the fan motor, because as the filter loads the pressure drop rises and a small fan motor run continuously could burn up.

### How to Measure Air Filter Static Pressure Drop  
*Source id: zkPcIKKGwwc*

- Measuring pressure drop across a component (filter, coil, heat exchanger, reheat coil) is a very practical test; for a filter, zero the sensor, place one probe on the negative (higher-negative) side and one on the other side of the filter to read the drop.
- A restrictive filter can be caused by dirt OR by more airflow moving over it than it's designed for (more common than techs realize); a static-pressure-drop test shows the source of an airflow problem.

### How to Measure CFM w/ The Testo 420 Flow Hood  
*Source id: kAjT-VujA6I*

- The Testo 420 flow hood measures CFM at diffusers/registers; it's light (~6 lb), reads accurately ~50 to 2000+ CFM, and its flow straighteners reduce turbulence so the pitot array at the bottom (where the reading actually happens) reads accurately.
- Use it to total system airflow (sum all diffusers) or compare against plans for test-and-balance; for very low flow (e.g. a 30 CFM bath vent) use a vane anemometer instead since the hood needs ~50+ CFM to read accurately.
- Take readings in a couple orientations (rotate 90 degrees); if the reading changes significantly, try different positions and average.

### How to Measure Fan Efficacy (Blower Performance)  
*Source id: 8ANRxjC6xs8*

- Fan efficacy = CFM divided by watts; it measures how effectively the blower moves air per watt consumed.
- You must measure true wattage as volts x amps x power factor, not just volts x amps (which gives VA), because ECM blower motors have very low power factors.
- As a blower wheel or evaporator coil gets dirty, ECM motors ramp up wattage to hold constant airflow, so efficacy decreases.

### How to Measure Total External Static Pressure (TESP)  
*Source id: 6uMqw69XkRw*

- Total external static pressure is the total static the air handler/fan coil sees external to the unit; measure it only on clean, like-new equipment (clean blower, coil, filter).
- On a fan coil put the negative port under the coil above the filter; on a gas furnace put the negative above the blower and the positive between the furnace and the (cased/uncased) coil - furnace and fan coil probe positions differ.
- Zero the manometer to atmosphere before inserting probes and plug any holes you drill.

### How to Measure Total Static Pressure w⧸ Testo 510i  
*Source id: E3-lpHKCjiQ*

- Zero the 510i manometer, point static tips into the airflow direction, connect supply to positive and return to negative to read total external static.
- Probe tip orientation makes little difference at low residential/light-commercial velocities but pointing into the airstream is still the correct method.

### How to Predict Air Flow Issues in the Sales Process  
*Source id: cGT6ZA3bcIg*

- TrueFlow's new forecasting feature applies Fan Law 2 (from Bernoulli's equation) to predict what static pressure a new system will see at the correct airflow, using a real measured TrueFlow airflow plus static-pressure map.
- Static pressure alone is meaningless without a real airflow measurement; a dirty coil/blower can show 0.5 static while moving half the CFM.
- Reducing loads (envelope, ductwork) should be the number-one priority so equipment can be downsized; upsizing to cover load is a bad idea.

### How to Use a Blower Door (Como usar el Blower Door)  
*Source id: 0YnhnPTkyU0*

- A blower door creates a pressure difference between the house and outside to measure infiltration; set up the frame/fan in an exterior door, close exterior doors, open interior doors, and turn off mechanical systems (AC, fans).
- Testing at 50 pascals (about the pressure of an 18-20 mph wind) is roughly the maximum pressure difference usable without damaging the structure.
- Room-by-room, measure each room's pressure relative to the house to find where it is most connected to outside (higher % = more infiltration / more opportunity to improve).

### How to use Static Pressure to Measure and Set Air Flow  
*Source id: ddhQrxuIbUI*

- External static = the sum of the positive (supply) and negative (return) readings; the + and - only indicate which side of the blower, they are not math signs, so you ADD the two numbers.
- Use static pressure + the factory blower chart (from the install manual) to set constant-torque/PSC or ECM blower speeds; get the design equipment airflow from the equipment performance data (Manual S) using the required sensible heat ratio, not a rule of thumb.
- ECM constant-volume (variable speed) motors should be set to run at less than 70% of their max external static rating; high static builds heat in these air-cooled motors and shortens their life.

### Impact of Airflow on Refrigerant Measurements and Performance  
*Source id: hCZEg_DGCf0*

- The number-one refrigerant-side indicator of low airflow is a low suction-line temperature (a suction line below ~50F with normal conditions strongly suggests low airflow) — preferred over superheat because a TXV holds superheat while evaporator temp still falls.
- Measuring static pressure is NOT measuring airflow; after checking filter/coil/blower you must also check blower programming (wrong terminal, pin settings, missing G-call, wrong tap) or actually measure flow (TrueFlow grid).
- Low airflow lowers coil temp, suction and head pressure, drops compressor amps and mass flow, and can overheat the compressor even with cold light suction gas.

### Installing a Rectangle to Round Transition into an Existing Metal Duct  
*Source id: md1OyUs-tcA*

- Cutting a prefabricated rectangle-to-round transition into existing metal duct with drives and slips when there's no room for a start collar and it must remain removable (for water-heater access).
- Account for the ~3/8 in. lost on each bend and make the opening ~2 in. smaller than the piece; bend drives first then slips.

### Is a House Really just a Big Duct System？ w⧸ Eric Kaiser  
*Source id: YUjv96bbQOM*

- The house shell behaves like the biggest 'duct': one CFM out equals one CFM in, so duct leakage or exhaust forces unconditioned infiltration air into the house somewhere (e.g., the dirty attic insulation acting as a whole-house filter).
- Supply air's real job is to condition the surfaces (about 60% of comfort is radiant), so select and place registers to wash the heat-conducting surfaces rather than blow air on people (50-100 fpm pleasant, under 50 unnoticed).
- A closed door on a room with no return over-conditions it: a tiny pressure rise (~4.2 Pa) barely cuts airflow (~10%) but greatly increases dwell time and heat transfer, so the room gets too hot in heating while the rest of the house pulls in infiltration.
- Ventilation is the 'V' in HVAC: provide filtered, controlled makeup air (oversize the filter, low pressure drop), interlock it with the most-used exhaust, aim for neutral house pressure, and don't rely on ERV/HRV for makeup air.

### Make Field Transitions on Prefabricated Metal Duct  
*Source id: UKdV16U6JrI*

- Field transitions/reductions on prefabricated metal duct can be made with off-the-shelf universal transition/reducer pieces (2", 4", 6") or built on-site from flat sheet metal; the site-built version is unlimited in size while pre-fab reducers are limited to specific sizes.
- Connections (drives and slips/sleeves) between duct sections must be sealed with mastic or tape, especially the corner gaps/holes.
- How much you reduce (2", 4", or 6") depends on the Manual D duct design.

### Measuring Air Velocity using Testo 410i  
*Source id: WTEoz7P3QDM*

- The Testo 410i vane anemometer measures air velocity at a supply outlet and can convert velocity to volume flow (CFM) if you enter the vent's area and free-area percentage.
- In a residential supply duct/outlet, target velocities are roughly 300 to 700 feet per minute.
- Use a timed-average traverse, painting the whole vent, to average the velocity across the outlet.

### Measuring Duct Leakage To Outside  
*Source id: FtPWajjm1Q0*

- Duct leakage to outside is measured by pressurizing/depressurizing the house envelope to -25 Pascals with a blower door, masking all registers/returns, then running a duct blaster to 'cruise zero' (matching the duct system to house pressure = -25 Pa reference to outside); the resulting CFM is the leakage to outside the thermal boundary.
- 'Cruise zero' neutralizes the pressure difference between duct and house so you isolate only the leakage crossing the thermal boundary, not total duct leakage.
- Leakage inside the thermal envelope causes comfort problems; leakage to outside the envelope is a double-whammy — every CFM out brings a CFM in, losing capacity and increasing load, and can lead to moisture/mold/destruction.

### Measuring In-Duct Airflow with the Testo 405i  
*Source id: 29sNEDcQJTc*

- The Testo 405i hot-wire in-duct anemometer measures air velocity and volume flow inside a duct.
- The practical residential/light-commercial method is a timed traverse: set the duct length/width in the app, insert the probe fully with the tip open, use the same pacing to slowly draw it out and back across equidistant ports, then complete the average.
- A full log-Tchebycheff traverse is the rigorous method; look up an article on exactly how to do it.

### Mini-Split Cleaning & Maintenance  
*Source id: GRhAWA4tz1I*

- Ductless blower wheels get very dirty in humid climates (static cling on non-metallic wheels, thin cups); clean them ~once a year by pulling the wheel and brushing, or use a bib kit — dry climates rarely have this issue.
- Be extremely careful with the blower-wheel set screw: over-tighten it or put a burr in the wrong spot on the hardened/stainless shaft and the wheel will never come off (a nightmare requiring grinding); use a little grease and set the wheel centered so it spins freely before gently tightening.
- Dilute cleaners properly — improperly diluted (usually over-concentrated) cleaners don't work better, take longer to rinse, leave damaging residue, and cost more; when in doubt go LESS concentrated. Never run cleaner through a condensate pump.

### MiniSplit Air Conditioning Cleaning Practices  
*Source id: DHWcSYPLLVw*

- Ductless cleaning 'best practices' are what you do when a unit needs it — a discerning tech decides; you don't do the full teardown on a clean 6-month-old unit. A good single-head ductless maintenance with a bib kit (including pulling the blower wheel when needed) runs about an hour to an hour and a half.
- Do no harm: use neutral / non-caustic (non-acid, mildly-or-non-alkaline) cleaners properly diluted because ductless evaporator copper and micro-channel aluminum are very thin and prone to formicary corrosion; a coil-cleaning tool (Speedclean CoilJet) gives enough flow to clean without pressure-washer damage and, with a bib kit, keeps water off finished walls.
- Run-test before removing the bib (or you'll blow water everywhere) and allow ~10 minutes of run time so the condenser coil dries before testing performance.

### Practical Training on Manometers  
*Source id: QHHMC5K2moU*

- Static pressure is the resistance to airflow the blower creates; supply is positive pressure (pushing against surfaces) and return is negative (pulling on filter/coil/duct), and total external static adds the positive supply and negative return readings.
- Measure total external static ABOVE the filter and above the blower/before the duct — testing only on the return (behind the restriction) gives a false low even when the blower is under severe high static.
- A restricted filter or coil reduces airflow, which drops static in the ducts (false low) but creates a large pressure DROP across the restriction — measure across the coil (both readings negative, so do the math) to prove an impacted coil.

### Pro Tips for Perfect Flex Duct to Duct Board Connections with Bert  
*Source id: iygU_hFM9Os*

- On a flex-to-collar connection the INNER liner is the crucial airtight seal (the outer layer only prevents sweating/heat loss); fully extend the flex first so the compressed inner ridges don't create turbulence and excessive static.
- Mastic is NOT the seal - it only holds a MECHANICAL seal in place. Duct-board connections must be mechanically tight (insulation-to-insulation), with the Panduit strap landing on the ridge/lip over multiple inner layers; you can't fall back on mastic to jam air leaks (it stays wet/cold and sweats).
- On splice connections (the number-one duct failure), make the inner seal in the DIRECTION of airflow - the upstream inner layer goes on first and overlaps so any leak vents into the next duct rather than into the insulation (where it would sweat and leak at many points).

### Proper Use of Manometers for HVAC Technicians  
*Source id: a9tX40eOJfw*

- Static pressure is the pressure pushing on all sides of a container (balloon analogy) - it is RESISTANCE to airflow, NOT a measurement of airflow; with no container (probes in open air) there is zero static.
- Total external static pressure is measured only across the EQUIPMENT: above the filter (return) and above the blower (supply) on a fan coil, or above the heat exchanger and above the filter on a furnace; static is additive TOWARD the blower, so the highest reading is at the blower and it drops the farther away you measure.
- Manufacturers rate efficiency at a design external static (e.g. 0.5 in WC), so a system running higher isn't achieving its rated SEER; use the factory blower chart plus your static reading to set the fan for the target CFM/ton (350 CFM/ton in Florida), and use pressure DROP across the coil or filter as a diagnostic.

### Rack Refrigeration Cycle Part 11 - Evaporator Airflow  
*Source id: RI1wD7nyGL4*

- Refrigeration evaporators run far fewer fins per inch than AC coils because the coil runs below freezing and must leave room for frost — tighter fins per inch (high-efficiency 'H' cases) grow frost faster, demand more defrosts, and are far more sensitive to store humidity and air spillage.
- Every case has a load limit (the inside line of the air curtain); breaking it with product opens the 'refrigerator door' — air spills to the sales floor and pulls in 75F/55% store air, so core product runs warm (mid-40s) even without triggering a case alarm.
- Shelves are structural to airflow: about half the air comes out of the back-wall perforations at a steep angle and must hit a shelf to deflect down — missing/wrong shelves ruin the air curtain, so never do final EPR/TXV settings without shelves in place.

### Residential AC System Installation  
*Source id: gZQqjXhuMTI*

- Static pressure is not airflow - it only reflects airflow if the blower is actually delivering its CFM; a wire on Y1 instead of Y/Y2 gives low airflow AND low static, so measure real airflow (TrueFlow Grid, ~plus/minus 6%) or be very good at catching the many things that reduce blower output.
- Dehumidification is a function of evaporator temperature and run time; put dehumidifiers in the SUPPLY (not return) so you don't de-rate the AC's own moisture removal, and add whole-house dehumidification to humid-climate designs.
- Structure and equipment are inseparable: unvented/vented attics, tongue-and-groove ceilings, can lights, radiant barriers, and customer set-point behavior drive most humidity/mold problems; address the envelope, don't just swap equipment.

### Retrotec Duct Leakage & House Pressure Demo  
*Source id: _oJOBSJW0kA*

- Understanding the relationship between the mechanical system and the building it serves is the way HVAC contractors get into home performance; the 'mad house' model demonstrates the same pressure dynamics as a real house (named after the MAD AIR paper by John Tooley and Neil Moyer).
- More supply-side than return-side duct leakage pulls the house negative, drawing in hot humid air through walls, insulation and cracks; a closed bedroom with no return path/transfer grille/jumper duct goes positive while the main body goes negative, so the house and system fight each other.
- Aim to keep a building slightly positive so opening a door pushes air out, not sucks untreated air in.

### Sealing Ducts From the Inside w⧸ Sean Harris  
*Source id: bj962pMF1-Q*

- Sealing ducts tightly controls house pressures: supply-duct leakage puts the house under negative pressure, pulling in nasty humid air, which is bad for controlling relative humidity - in humid climates you want neutral to slightly positive pressure.
- Aeroseal does not coat the duct interior; the system is isolated and pressurized, and the aerosol is drawn to the leaks (up to 5/8 inch) and builds on itself to seal them.
- Aeroseal is not a cure-all - undersized ducts, needed duct replacement, and poor design still need real fixes; hand-sealing accessible leaks first plus Aeroseal gets the rest.

### Short 10 - Air Has Weight and Takes up Space  
*Source id: tXFHPWkUAOA*

- Air has weight and takes up space; we measure volume in CFM (cubic feet per minute) but a coil cares about mass flow rate (pounds per minute), not just volume.
- Standard air weighs 0.075 lb/cubic foot, so 400 CFM/ton = 30 lb/min/ton; but real conditions change density (75F/50%RH is ~0.0731 lb/cf, altitude thins it).
- A blower and a vane anemometer measure volume (density-independent); static pressure, pitot, and hot-wire measure what's IN the box (density-dependent) - so the same volume flow moves less mass at altitude.

### Short 16 - Air Velocity is Useful  
*Source id: Sz6A9-ihX-g*

- Distinguish air velocity (speed, FPM), air pressure (static/velocity pressure), CFM (volume/'boxes'), and mass (pounds, density-dependent by altitude/temperature).
- A vane anemometer (e.g. Testo 405i) measures true air velocity directly with no free-area/K-factor math needed, and true air velocity is density-independent.
- You can diagnose airflow problems by comparing velocities room-to-room without calculating CFM - registers are usually sized consistently, so an outlier velocity tells you something.

### Short 2 - Delta T  
*Source id: c1LCnU3lO-M*

- Delta T (return-to-supply air temperature split) is not a fixed 20 degrees; the target curves with enthalpy — mainly humidity/latent load — and airflow, ranging roughly 14 to 24 degrees.
- Measure with good air probes placed out of the line-of-sight of the cold coil (to avoid radiant error) and where the air has mixed (a foot or two downstream); never use an infrared/laser thermometer, which reads surface, not air.
- Low airflow or dry air raises delta T; high airflow, high return relative humidity, or anything that reduces capacity lowers delta T.

### Short 4 - Blower Taps (Audio Only)  
*Source id: 2kgNFetuWKs*

- Look up the manufacturer's expanded fan performance data (blower charts) to set blower taps — you can't know the right tap for an application without them, and a '36,000 BTU' unit rarely delivers a full 3 tons of sensible capacity.
- Set heating and cooling airflow separately: heating by temperature rise (aim mid-range of the rise window), cooling by design sensible/latent capacity — you can't assume one setting is right for the other, especially with an oversized furnace and smaller A/C.
- Measure total external static pressure (return before appliance, supply between appliance and coil, plus added resistances) to set fan speed from the charts; for non-factory/constant-torque motors (Evergreen, Flex) you MUST measure actual airflow (duct traverse, TrueFlow grid, or temperature-rise method).

### Static Pressure Fundamentals  
*Source id: o6OVAUJXeuU*

- Total external static pressure is a factory benchmark (industry standard ~0.5 in wc) measured top-of-unit to bottom-of-unit; test with no filter (true-flow grid) first, then optionally with the filter to see its restriction.
- Static pressure is like blood pressure for the system: too high on either supply or return signals a duct/design problem (pinched, crushed, undersized, too few returns).
- You can't fudge the numbers - the data is the proof; use it to question design and to have the hard duct conversations with homeowners.

### Static Pressure and Manometer Basics  
*Source id: Jp2pZydCp28*

- Two manometer families: utility/service manometers read inches of water column (static, velocity, gas pressure); precision manometers read the much smaller Pascal scale for blower-door, duct-leakage and room-depressurization tests.
- Every pressure measurement is a differential - either against a real-time atmospheric reference (dual-port) or against a previously-zeroed baseline (single-port); so zero the tool right before you test, don't rely on yesterday's zero.
- Static pressure is a pressure, not a flow, measurement - meaningless unless the system is producing full airflow (highest blower speed, correct settings, not in dehumidification mode).

### Symptoms of Low Evaporator Airflow  
*Source id: x4_FkNNGzFo*

- Simplest rule: low suction pressure AND low suction temperature (i.e. low/normal superheat) means look at airflow - that's what differentiates low airflow from undercharge or a restriction.
- Most common cause is a dirty filter; always start with visual inspection (filter, evaporator coil, ductwork, return grills) before in-depth diagnosis.
- Icing (below 32 F evaporator, i.e. below ~101 psi suction on R-410A for long enough) and an abnormally cold suction line are the walk-up indicators of low airflow.

### System Airflow Measurement w/ TEC TrueFlow  
*Source id: USMxJexJvbo*

- Total external static pressure is a PRESSURE, not a FLOW, measurement - it correlates to flow via a blower chart but misleads badly when the indoor coil/blower is dirty (pressures drop, so the fan chart wrongly reads MORE airflow).
- The TEC TrueFlow grid measures actual system airflow directly (with a correction factor from the DG8 manometer), so it works whether the coil is clean or dirty; set airflow BEFORE setting charge.
- Airflow drives everything: too low = colder evaporator, lower suction pressure, lighter suction gas, less refrigerant moved = lost efficiency and capacity plus condensation risk; too high loses latent capacity in humid climates.

### Testing Home Pressure Imbalance w⧸ Genry Garcia (Spanish)  
*Source id: 27AoOAVSaM0*

- When opening a house door, feel whether the space is predominantly negative or positive relative to outside — a strongly negative house indicates supply air being lost/not returned, driving humidity and infiltration problems.
- A disconnected/poorly-installed duct in the attic caused strong decompression into the house, producing the measured low (negative) pressure and the musty-smell / humidity problem.

### Testing out a High Performance HVAC Installation  
*Source id: DhXYd2Um1uE*

- You do not need exotic materials to build a tight, high-performing duct system — flex duct pulled tight with rigid elbows at every turn delivered required airflow with extremely low leakage.
- Balanced ventilation via an ERV (fresh air to bedrooms/living, exhaust from bathrooms and kitchen) is a superior alternative to traditional bath fans because it recovers heat and moisture.
- An oversized, sealed 2-inch-deep MERV 13 filter grille gives excellent filtration with very low pressure drop and zero bypass.

### The Duct We Tend to Forget w⧸ Joe Medosch  
*Source id: DpX20OkmgoU*

- The largest, most-forgotten 'duct' in a house is the building envelope; infiltration is always estimated in Manual J and can be 40-60% of the load in existing homes — measure it with a blower door instead of guessing.
- Seal the envelope (top plates, chases, fireplace chases, receptacle/switch penetrations to the attic) at the source rather than gasketing receptacles; a pressure pan with a running blower door locates leakage (>5 Pa connected outside) and duct leakage (>2 Pa) to a specific run.
- When you tighten a house you must add designed, treated, filtered outdoor-air ventilation (ASHRAE 62) and protect combustion appliances — sealing can backdraft natural-draft appliances (it takes less than 5 Pa).

### The Flaw With Zonal Pressure Diagnosis  
*Source id: 7bXPNva82qc*

- Zonal Pressure Diagnostics (ZPD) is only a ratio of two openings (room-to-house vs room-to-outside); it does not tell you the actual hole size or CFM50, so claiming a room is 'X% connected to outside' is technically meaningless.
- Changing only the room-to-inside opening (opening a door a couple inches) swings the ZPD reading dramatically (from mid/high 40s down to 27 Pa) without touching the room-to-outside leakage — proving the reading's fallacy.

### The Great Heat Pump Revolt of 2026 and How To Avoid It with Steve Rogers, Russ King and Chris Hughes  
*Source id: OioG8T_zwaA*

- Four action items to install heat pumps right and avoid a 'revolt': do a proper Manual J load calc (500 sq ft/ton is AC-only and doesn't work for heat pumps), confirm duct sizing, check for duct tightness/leakage to outside, and set the controls properly.
- A heat pump too big for the duct system fails: with a PSC motor airflow nose-dives; with an ECM motor airflow holds but static pressure goes off the charts, burning out ECM motors that run at 1.3 in wc — in cold climate 6 use a dual-fuel backup instead of oversizing.
- Set the swap-over using the balance point worksheet: draw a line through the design-load point and 60°F at zero load to find the thermal balance point; run the heat pump well below that (down to its rated -5 to 0°F) and only bring on auxiliary heat where the load line crosses above capacity.

### The Impact of Static Pressure on Fan and Blower Motors w⧸ Rick Streacker  
*Source id: 1X9cXMrWc1o*

- Static pressure affects axial fans and centrifugal blowers oppositely: adding static to an axial fan (condenser) increases load and amps and slows it; adding static to a forward-curve blower restricts airflow, reducing load so a PSC blower speeds up and amps DROP.
- Air is the load on an air-over motor; a dirty filter on a blower does NOT raise amps — it restricts air, reducing load and lowering amps, but the motor runs inefficiently, winding temperature rises, and life shortens (a 10°C / 18°F rise cuts motor life ~50%).
- Always check amps with everything in place (doors, panels, filters, guards, deck trap doors) because those change static and thus the true load; you can't fix a bad static condition by swapping to an ECM or a higher-horsepower motor — fix the duct work.

### Total Furnace Airflow and Precision Manometer w⧸ TEC TrueFlow  
*Source id: pYA2xv0cukA*

- A manometer's two ports read duct pressure referenced against the room; you need a reference (the second, hose-less port) to define what the duct pressure is measured against.
- The TEC TrueFlow grid and DG-8 manometer measure static pressures and system airflow: it takes readings with the filter in, then again with the TrueFlow grid in its place, and calculates total external static and CFM.
- Pascals are a powerful, underused diagnostic for room pressurization and building pressure (negative/makeup-air) that typical field manometers can't read.

### Understanding Airflow: David Bowie, a Used Car Lot, and a 40 cent Tool with Alex Meaney  
*Source id: uIXfiuY3i9U*

- Duct size is cross-sectional area, not a linear dimension: a 6-inch vs 7-inch duct is a ~36% change in area, not a 17% change in diameter - size increases geometrically, on the square.
- Friction, not pressure, is the enemy of airflow. Static pressure is energy lost to friction; velocity pressure is the energy actually doing the work of moving air; the two are always in balance at any point in the duct.
- Static pressure drop between two points of equal duct size and airflow is a direct measure of the friction between them; most duct friction comes from fittings (changes of direction), quantified as equivalent length (an elbow ~ the friction of a length of straight duct).

### Volume Flow Rate vs Mass Flow Rate w⧸ Jim Bergmann  
*Source id: FMSl9qexPRw*

- Air conditioning is all about pounds of air (mass), not volume: Q = mass x specific heat x delta T, so 400 standard CFM = 400 x 0.075 = 30 lb/min per ton
- Standard CFM (SCFM) has a weight associated with it; Actual CFM (ACFM) is just a cubic foot regardless of what's in it - a PSC motor moves constant ACFM while an ECM adjusts to hold constant SCFM by sensing torque
- Adding water vapor makes air lighter (dry air is heavier) because H2O molecules have less mass than the nitrogen/oxygen they displace

### What Air Filter is The Best？  
*Source id: 4R0V6a6Uz3c*

- There is no single 'best filter' answer - it depends on the application; you must measure pressure drop across the current filter and total external static pressure to know your headroom
- The two things that make a filter work well are directly related: low pressure drop and low face velocity - achieve both with the biggest and deepest media you can fit so air moves slowly and gets cleaned better
- A MERV 13 doesn't inherently starve a system - it starves one when the surface area is too small and there's no static headroom; a big 24x24 MERV 13 on a 1.5-ton system is no problem

### What Should the Air Delta T be？ (Air Temperature Split)  
*Source id: _pD-rRCNv8k*

- Delta T (air temperature split) is the difference between air entering and leaving the evaporator coil, measured directly above and below the coil (not at the registers) with proper air mixing and not in the coil's line of sight
- The old 20-degree-split rule of thumb is a poor standalone indicator - real splits run 14-23F and depend on three moving parts: compressor mass flow (capacity), airflow, and return air humidity
- Higher humidity lowers delta T (more work goes to latent/making water); lower airflow raises delta T; lower system capacity lowers delta T

### What is Proper System Airflow  
*Source id: sjZR0bTL1Ig*

- The sensible heat ratio (SHR) of the structure dictates proper airflow, NOT a fixed 400 CFM/ton or a square-foot-per-ton chart; do a load calc, divide total by sensible to get SHR
- Manual S is the selection standard: meet the sensible load, meet the latent load, and don't exceed total capacity by more than 15% (single stage), 20% (two-stage), or 30% (variable) - use extended performance data at the target airflow, not AHRI numbers
- Manipulating airflow trades capacity and efficiency: lower airflow -> lower total/sensible, more latent, lower efficiency; higher airflow -> higher total/sensible/efficiency, less latent

### When a Variable Blower Runs Too Slow  
*Source id: M99zS-5yeSs*

- A variable-speed (Carrier ECM) blower running too slow is usually a control/wiring issue, not a motor failure — check pin settings (kW/tonnage, heat pump vs AC, comfort vs efficiency, nominal/low/high airflow) first.
- Make sure Y is on Y/Y2 not Y1 — a Y1 call on single-stage equipment makes the blower run near half speed; confirm a G (blower) call and a dehumidification (DH/DHUM) call, since missing either drops the blower to a reduced speed.
- If the blower oscillates back and forth for an extended time, that indicates a motor module problem — run the full ECM motor diagnosis.

## Canonical field stories

### The trailer flex-duct repair
- **Setting:** Under a mobile home in Central Florida; homeowner's electric bill $100 higher than normal
- **Diagnosis chain:** Found second-stage heat not working (little heat usage in Central Florida), but the real issue was damaged/unrated flex duct under the trailer needing repair.
- **Root cause:** Damaged, unstrapped, non-weather-rated flex duct under the trailer (pinched/kinked where not strapped high enough)
- **Lesson:** Cut a clean access point, repair correctly with mastic and straps, keep duct off the ground, and quote the proper upgrade to code.
- **Source:** [#BertLife - Flex Duct Repair Terror] (id: Rl2Ej7fdy1U)

### Hot top floor, cool basement
- **Setting:** The classic summer complaint - homeowner moves to the basement because the top floor is unbearable
- **Diagnosis chain:** Homeowner calls the AC guy, who suggests the AC is undersized/broken -> but it's interlinked airflows, air pressures, and heat bleed (stack effect that reverses under cooling) -> a complex enclosure problem, not an AC problem.
- **Root cause:** Enclosure/stack-effect interaction, not AC capacity
- **Lesson:** Only diagnostics (testing) can guarantee a fix; upsizing the AC won't solve an enclosure problem.
- **Source:** [(Podcast) Blower Door Testing, Building Performance & More w⧸ Corbett Lunsford] (id: IlrHazYv84M)

### The sagging return flex demonstration
- **Setting:** Jack training a new installer on a 3-ton air handler with a 16-18 inch flex return off a ceiling box
- **Diagnosis chain:** Hooked a magnehelic to supply and return, started the unit, then pushed the sagging return flex up into a smooth 90-degree turn -> static dropped from ~0.5-0.6 to ~0.02-0.03.
- **Root cause:** Flex-duct sag/compression, not duct size
- **Lesson:** Straightening/pulling flex taut dramatically improves airflow; treat the cause (flex handling) not the symptom (size).
- **Source:** [(Podcast) Common Duct Design Mistakes w⧸ Jack Rise] (id: X2Y1KNFoxug)

### The Kent State natatorium pool losing water
- **Setting:** A pool-pack unit at a Kent State University natatorium with high water loss and chlorine smell
- **Diagnosis chain:** Staff cranked open outside air in Ohio winter to clear the chlorine smell -> heating that cold outside air dried it to ~10% RH -> the very dry air drove rapid pool evaporation (and the chlorine smell) -> Jim closed the outside-air damper, raised room humidity to spec, and evaporation and smell stopped.
- **Root cause:** Over-ventilation with heated, dried outside air driving pool evaporation (a psychrometrics error)
- **Lesson:** Psychrometrics 101: cranking outside air in winter dries the space and increases evaporation; control humidity instead.
- **Source:** [(Podcast) Measuring Air Flow - Air Density and Direct Air Flow Measurement Part 2 w⧸ Jim Bergmann] (id: 7lEhrcbaeGM)

### The lab that couldn't get a repeatable capacity reading
- **Setting:** Jim teaching, running furnaces/AC in a large connected shop with a student (Matt Shuffler)
- **Diagnosis chain:** Tried to calculate CFM and capacity from total external static pressure and temperature rise -> results were all over the place and non-repeatable -> concluded it was bad MEASUREMENTS, not that field capacity testing is impossible; accurate Testo temperature/humidity instruments made the math work.
- **Root cause:** Inaccurate field instruments (temperature/humidity), not the physics
- **Lesson:** Accurate capacity/airflow work requires accurate instruments and understanding each method's variables.
- **Source:** [(Podcast) Measuring Air Flow - Static ⧸ Capacity & ECM Motors Part 1 w⧸ Jim Bergmann] (id: ryTchnFMem0)

### The lopsided cased coil
- **Setting:** Florida furnace with flexible rated flue; a quick-connect cased coil installed incorrectly for years
- **Diagnosis chain:** Coil sitting shifted right, starving one-third of the N-coil of airflow; suction ~115 psi with only ~6F superheat; shifted the new coil left so the drain pan overhangs -> suction 155 with 15F superheat, 20F split.
- **Root cause:** Cased coil installed shifted to the right rather than to the left where the drain pan hangs over
- **Lesson:** Push N-shaped cased coils to the left; a misinstalled coil starves airflow and masquerades as a charge/performance problem.
- **Source:** [A Common Cased Coil Issue] (id: PjWScoD3NH4)

### Insulation sucked into the blower intake
- **Setting:** Front-facing fan coil, called out only for leak detection following another company
- **Diagnosis chain:** Noticed the interior/back panel and insulation being pulled against the sideways blower, blocking half of the air intake on the backside; removed the blower wheel, secured the loose insulation with plumbing strapping in an X, glued and metal-taped it.
- **Root cause:** Loose back insulation panel pulled by the blower over the intake, blocking airflow
- **Lesson:** Always look at a front-facing unit for insulation pulling into the blower even when you're there for something else.
- **Source:** [A Commonly Missed Airflow Issue w⧸ Bert] (id: HvhaFcc7cLQ)

### Repeated blower-motor failures from a turbulent S-turn takeoff
- **Setting:** Live duct demo/trouble job; a pretty sheet-metal plenum with a double-elbow S-turn takeoff
- **Diagnosis chain:** System had high static and repeated blower-motor failures; an upper probe read 0.12, so a second port was drilled lower and a differential manometer between the two ports read 0.08 differential within the same duct - proving turbulence in the lower half from the sharp back-to-back turns.
- **Root cause:** Sharp double-elbow/S-turn takeoff creating turbulence and high static despite good-looking sheet metal
- **Lesson:** Pretty ductwork can perform terribly - unless you're testing, you're guessing; use two test ports to reveal turbulence.
- **Source:** [A Duct Up Situation with Sam Myers and Eric Kaiser] (id: wmJ0QBKEbB8)

### The loading/unloading electrostatic filter
- **Setting:** a Florida college with two identical air handlers
- **Diagnosis chain:** electrostatic filter's pressure drop went up then DROPPED week to week (0.5 -> 0.35 -> 0.625 -> 0.4); downstream light showed dust all over the window vs a clean window on the fine-fiber unit
- **Root cause:** coarse-fiber electrostatic filter loaded then unloaded particles back into the airstream
- **Lesson:** if static pressure stops climbing, the filter is releasing particles - a real filter's pressure drop keeps rising as it loads
- **Source:** [Air Filters, They are More Complex Than You Knew w⧸ Lee Andrews] (id: s4EGvkZPqgo)

### 10-degree winter temperature drop through a single return flex
- **Setting:** a home with a ~20 ft flex return in a crawl space
- **Diagnosis chain:** measured a 10-degree temperature drop before the air hit the furnace; the return flex had all the static, so it sucked crawlspace air through a ~1-inch gap in the return pan
- **Root cause:** undersized/restrictive return holding all the static, pulling infiltration
- **Lesson:** if all the static is on the return you suck in everything through every crevice - balance the static and seal the return
- **Source:** [Air Flow Diagnostics w⧸ Joseph C Henderson] (id: wWN2IKAqpy4)

### Master bedroom at 7 Pascals
- **Setting:** a home Adriel tested after adding air to a warm room
- **Diagnosis chain:** closed the master bedroom door and measured ~7 Pascals room-to-house; homeowner didn't mind the coolest room, but the rest of the house is now negatively pressurized 7 Pa, pulling attic air -> higher humidity, dust, bills
- **Root cause:** more supply air into a room without matching return -> positive pressure -> negative pressure everywhere else
- **Lesson:** advise on the whole-house consequence, not just the one room; the fresh air comes from a very unfresh place (the attic)
- **Source:** [Air Sealing and Static Pressure Diagnostics] (id: AWecM1MfuEE)

### Matt's honest airflow retrofit that missed target
- **Setting:** a 3-ton PSC system, hot upstairs room, homeowner asking for a bigger unit
- **Diagnosis chain:** 0.59 total static but only ~265 CFM/ton (~800 CFM = really a 2-ton); planned to upsize return + big filter to hit 1200 CFM; a beam forced a weird plenum and ~25% of the filter taped off, plus coil/plenum drops; ended at ~1100 CFM with static beyond predicted
- **Root cause:** front-end planning gap (beam) + fan-law square effect
- **Lesson:** even with good tools airflow fixes aren't mistake-free; testing out on the back end reveals what you got wrong - and keeps the job interesting
- **Source:** [Airflow & Static Pressure with Matt Bruner & Bryan Orr] (id: eHzYalJXE88)

### The measureQuick ticket-size case study
- **Setting:** A New York technician, June-August, before vs after adopting measureQuick
- **Diagnosis chain:** By simply deploying 9-10 probes and following measureQuick's guided workflows, his numbers changed year over year.
- **Root cause:** Getting the data surfaced solvable whole-home problems he was previously missing.
- **Lesson:** Total sales went from $288k ($2,800 avg ticket) to $465k ($4,600 avg ticket) - roughly a 50-60% jump - because customers paid for the SOLUTIONS he found, not the probes.
- **Source:** [Boost Your HVAC Ticket Size： Deploying Static Pressure Probes with MeasureQuick] (id: y4y1EtgEs9w)

### Finding a collapsed flex liner under a trailer with a static probe
- **Setting:** A trailer with a mysterious airflow problem; Bert was the third tech out
- **Diagnosis chain:** Supply static read outrageously high and return static low, indicating a supply blockage; probing individual branches, one side had very high static and the other didn't, pointing to the blocked direction.
- **Root cause:** A broken internal flex liner had pulled back and blocked one branch.
- **Lesson:** Static pressure localizes hidden blockages you can't see through sealed duct.
- **Source:** [Boost Your HVAC Ticket Size： Deploying Static Pressure Probes with MeasureQuick] (id: y4y1EtgEs9w)

### The half-inch hole that added a quarter ton
- **Setting:** Bill Spohn's own house with panned returns (high and low return in the wall), cooling season
- **Diagnosis chain:** One bedroom was always hotter -> thermal imager showed a red/orange stripe of heat radiating down the wall -> traced to a roughly half-inch hole where a wire ran through into the pan return, continuously pulling load from the attic -> Allison Bailes calculated the added load
- **Root cause:** Small wiring penetration into a panned return duct pulling hot attic air into the return
- **Lesson:** Tiny penetrations into the duct/air barrier have an outsized effect on load and comfort
- **Source:** [Building Science 101 for HVAC Contractors w⧸ Bill Spohn and Joe Medosch] (id: jMTxblZcTzE)

### Upstairs bonus room that couldn't keep up
- **Setting:** 1.5-ton system in a 600 sq ft upstairs bonus room, multiple prior visits
- **Diagnosis chain:** Delivered capacity measured ~10-11k BTU against a required true 18k; moving the probe into the return box showed 82F hot spots vs 76F in the room
- **Root cause:** System delivering far below rated capacity / high heat load in the space
- **Lesson:** Delivered capacity shows whether the system is doing everything it can; if it is, look at reducing load
- **Source:** [Delivered Capacity Basics - Kalos Meeting] (id: EJVRhznC_Ts)

### Boxed-in flex plenum restricting a whole system
- **Setting:** Ex-NBA player Bo Outlaw's home; two ~2008-2009 systems plus older black-flex systems
- **Diagnosis chain:** Upstairs uncomfortable -> thermal imaging shows hot vents (duct gains + infiltration), black flex radiant gains, missing/pulled-back attic insulation, an open uninsulated duct chase -> refrigerant readings poor with low suction, yet a 20F delta T -> pushing a screwdriver through the plenum finds the installers boxed duct board around an existing small flex plenum, choking airflow since installation.
- **Root cause:** Restricted airflow from a flex plenum boxed inside duct board (plus black-flex thermal gains and a leaking, unsealed refrigerant cap), forcing the X13 blower to run high its whole life.
- **Lesson:** Low airflow raises delta T; poor refrigerant readings plus a high delta T and thermal gains together indicate an airflow problem. Set subcool first, then re-check split, then pull heat strips to inspect.
- **Source:** [Duct DISASTER at an NBA Players Home] (id: 75Q15TVoazE)

### The 'you can beat 0.5 external static' bet
- **Setting:** A homeowner's system Ed designed partly out of spite to prove a point
- **Diagnosis chain:** Used an oversized evaporator coil with an adjustable TXV paired to a smaller outdoor unit (large filter surface area) to drop wet-coil pressure drop under 0.1 and filter drop under 0.1, landing external static at ~0.52.
- **Root cause:** Conventional oversized-drive/undersized-filter designs create huge component losses and near-zero available static.
- **Lesson:** A big external static number isn't inherently bad and a small one isn't inherently good - it's relative; you can achieve very low pressure drops with enough surface area and correct component selection.
- **Source:** [Duct Design for Great Results w⧸ Ed Janowiak (ACCA)] (id: -KqmAQgUXY4)

### The homeowner who taught Adam to measure gas pressure
- **Setting:** Adam's early career (~1999) running a maintenance call for his dad at an older gentleman's house
- **Diagnosis chain:** The homeowner asked if Adam would check the gas pressure; Adam had never heard of it or a manometer, so the homeowner grabbed a vinyl hose, hooked it to the gas valve, filled it with water, and measured with a ruler
- **Root cause:** Adam had no business working on equipment yet and didn't understand inches of water column
- **Lesson:** Inches of water column is literally the height of a water column; a humbling reminder to understand what your measurements mean
- **Source:** [Fan Law 2 for Techs with Adam Mufich] (id: NzlsB9R6mbc)

### Balancing an oversupplied master suite
- **Setting:** Whole-house retrofit with new equipment and ductwork, manual dampers on each supply run; 3-ton upstairs system
- **Diagnosis chain:** Measured each vent (e.g., ~60 CFM, 152, 175); found nearly two tons of the 3-ton upstairs system was going into the master suite
- **Root cause:** Master bedroom was oversized/oversupplied on airflow
- **Lesson:** Oversize and add dampers, then balance down to target (~150 CFM here); most of the airflow change happens in the last bit before fully closed
- **Source:** [Flow Hood： How to Properly Balance an HVAC System] (id: XeanFStDbyY)

### 88 CFM of return leakage at grandma's house
- **Setting:** Chris (a 20-year tech) testing his grandmother's attic Carrier/Comfortmaker system with TrueFlow + MeasureQuick
- **Diagnosis chain:** The tools flagged large return leakage he insisted was 'not possible'; Steve Rogers asked 'did you measure it?'; he isolated the blower, capped the supply, and measured 88 CFM; the leak was behind the caulk where the plenum was screwed to wood and the insulation was caulked to the wood, so all four plenum sides sucked past the caulk line
- **Root cause:** Return plenum leaking behind the caulk into the attic insulation, next to the blower (highest suction)
- **Lesson:** You cannot eyeball whether ductwork leaks -- you must measure; they sealed it down to ~8 CFM
- **Source:** [HVAC Commissioning on Steroids w⧸ Jim Bergmann & Chris Hughes] (id: lvMjm3YwUY8)

### Rick the sheet-metal tech and the phantom duct problem
- **Setting:** A store with humidity issues; a test-and-balance company was brought in
- **Diagnosis chain:** TrueFlow measurements showed the ductwork was fine; the real problem was makeup air disabled during a remodel, causing building negative pressure; the emailed report proved it objectively
- **Root cause:** Non-functioning makeup air after a remodel (not the ductwork)
- **Lesson:** A measured report ends opinion-vs-opinion arguments and points to the true problem
- **Source:** [HVAC Commissioning on Steroids w⧸ Jim Bergmann & Chris Hughes] (id: lvMjm3YwUY8)

### How duct renovation saved David's career
- **Setting:** January 2000, Energy Management Conference, Louisville KY; David one foot out of the trade
- **Diagnosis chain:** Rob 'Doc' Falk introduced David to airflow testing/diagnostics and duct renovation -> work became fun again; his father gambled a gifted $5,000 on test instruments instead of paying bills -> the instruments paid for themselves within three duct renovation jobs.
- **Root cause:** Getting undersold and treated as a box-swapper
- **Lesson:** Measurement-driven duct renovation differentiates you from low-price competitors and makes the work profitable; test instruments are an investment, not an expense.
- **Source:** [How to Confidently Create a Duct Renovation Scope of Work w/ David Richardson] (id: 5eiv-0518mQ)

### Room in a vacuum - HVAC-induced infiltration (Lexington KY)
- **Setting:** A house in Lexington KY with a bedroom pulling triple the air out that was supplied in
- **Diagnosis chain:** Return pulled ~3x the supply into the room -> room in a vacuum -> HVAC-induced infiltration affecting surface temperatures, visible with a thermal camera.
- **Root cause:** Return/supply airflow imbalance in the room
- **Lesson:** Airflow imbalance drives comfort and infiltration problems you cannot see without instruments; a thermal camera in the customer's hands becomes your best salesperson.
- **Source:** [How to Confidently Create a Duct Renovation Scope of Work w/ David Richardson] (id: 5eiv-0518mQ)

### Live airflow demo on a 2-ton TXV system
- **Setting:** Training lab running MeasureQuick
- **Diagnosis chain:** Found low superheat/hunting from an unsealed TXV bulb access; sealed it; then progressively blocked supply and plugged the return with cardboard, watching suction-line temp fall, subcooling rise, delta-T rise, and TESP exceed 1 in.wc
- **Root cause:** Induced airflow restriction
- **Lesson:** Suction-line temp is the primary tell; superheat holds on a TXV
- **Source:** [Impact of Airflow on Refrigerant Measurements and Performance] (id: hCZEg_DGCf0)

### Over-conditioned closed-door room
- **Setting:** A normal house layout with a bedroom whose door closes fairly tight and has no return, in heating season
- **Diagnosis chain:** Closed room measures +4.2 Pa with reference to the house while the rest of the house is -6 Pa and another opening is 3.3 Pa; the small pressure rise only cuts airflow ~10% but doubles dwell time so the air sheds more heat into the room
- **Root cause:** No low-resistance return path from the room, so air makes more laps and over-conditions the space
- **Lesson:** A closed door makes a room hotter (not colder) in heating because of dwell time; design low-resistance return paths (Bryan/Russ King prompted the testing)
- **Source:** [Is a House Really just a Big Duct System？ w⧸ Eric Kaiser] (id: YUjv96bbQOM)

### The cat in the duct
- **Setting:** A furnace pulled out for service
- **Diagnosis chain:** A cat crawled into the duct while the furnace was out and went in too far
- **Root cause:** Open duct during service
- **Lesson:** Animals and toys end up in ducts; almost couldn't get the cat back out
- **Source:** [Is a House Really just a Big Duct System？ w⧸ Eric Kaiser] (id: YUjv96bbQOM)

### The 68-degree hot dogs
- **Setting:** Grocery store Saturday morning, overstocked case
- **Diagnosis chain:** Stock associate said product would sell out in an hour; cart-temp probe between two packs of precooked hot dogs read 68F
- **Root cause:** Case over-blocked past load limit, air curtain washed out, product not refrigerated
- **Lesson:** Over-blocking looks great but defeats the load limit and endangers core product temperature
- **Source:** [Rack Refrigeration Cycle Part 11 - Evaporator Airflow] (id: RI1wD7nyGL4)

### Duct washing out a case from 60 paces
- **Setting:** Grab-and-go case near store entrance, RTU overhead
- **Diagnosis chain:** Case wouldn't hold temp; measured ~60 paces to an RTU supply grill overhead blowing ~1000 CFM per grill that washed out the fragile air curtain
- **Root cause:** Distant HVAC supply air disturbing the case air curtain — often revealed after a sign/billboard that used to deflect the air was removed in a remodel
- **Lesson:** When chasing air infiltration, look in the distance (ducts, signs) not just at the case
- **Source:** [Rack Refrigeration Cycle Part 11 - Evaporator Airflow] (id: RI1wD7nyGL4)

### Mold on the vent over Mark O'Meara's bed
- **Setting:** high-end home in a golf subdivision (Tiger Woods's neighborhood)
- **Diagnosis chain:** New systems, vents kept growing mold; young Bryan piled insulation over vents, then set a ladder on a California-king bed to bleach mold right over the master bed
- **Root cause:** Envelope/humidity problem he didn't yet understand (low set point, attic conditions)
- **Lesson:** That embarrassment drove him to learn how moisture works so he'd never do that again - fix the root envelope cause, not the symptom.
- **Source:** [Residential AC System Installation] (id: gZQqjXhuMTI)

### Room supply/return balance check
- **Setting:** Bryan and Max at a house questioning whether a room has balanced supply and return
- **Diagnosis chain:** Shut the door, put a hose under it, measure pressure differential with a precision manometer
- **Root cause:** Need to confirm return pathway keeps the room from pressurizing
- **Lesson:** Differential should not exceed ~3 Pascal - too small for a normal Testo/Fieldpiece to read
- **Source:** [Static Pressure and Manometer Basics] (id: Jp2pZydCp28)

### Musty rental house running strongly negative
- **Setting:** Miami rental the client suspected wasn't right
- **Diagnosis chain:** Felt negative pressure at the door; measured house pressure vs outside with a precision gauge referencing outdoor pressure; read about -9.8 Pa; checked humidity ~59% RH; found a completely disconnected duct in the attic
- **Root cause:** Poorly done/disconnected duct causing supply loss and strong decompression
- **Lesson:** Pay attention to details when entering any space; door resistance or ease of opening tells you if a space is predominantly negative (supply loss) or positive (return loss) — both are bad
- **Source:** [Testing Home Pressure Imbalance w⧸ Genry Garcia (Spanish)] (id: 27AoOAVSaM0)

### Door-mask demonstration of ZPD fallacy
- **Setting:** House at -50 Pa with a blower door; internal laundry room with vent removed
- **Diagnosis chain:** ZPD implied the room was ~84-86% connected to outside; opening the door mask a couple inches (changing only room-to-inside opening) dropped the reading to 27 Pa (would imply ~54%); replacing the mask returned it to the original
- **Root cause:** The reading is only a ratio of two openings, not an absolute leakage measurement
- **Lesson:** ZPD readings on interior rooms lack technical legitimacy; if you believe you're quantifying outside connection you're playing yourself
- **Source:** [The Flaw With Zonal Pressure Diagnosis] (id: 7bXPNva82qc)

### Tricked into presenting to a room of engineers
- **Setting:** Wrightsoft trainer teaching Manual D without truly understanding it
- **Diagnosis chain:** Pulled an all-nighter watching YouTube on pressure the night before, realized static and velocity pressure are always in balance and that pressure loss = friction
- **Root cause:** Rote teaching of Manual D without conceptual understanding of what happens inside the duct
- **Lesson:** You can understand most of airflow without a single number; visualize the balance of velocity vs static pressure.
- **Source:** [Understanding Airflow: David Bowie, a Used Car Lot, and a 40 cent Tool with Alex Meaney] (id: uIXfiuY3i9U)

### The Ace Hardware filter screaming on Bryan's Mitsubishi
- **Setting:** Bryan's own upstairs Mitsubishi vertical system; grabbed a filter from Ace Hardware instead of the office
- **Diagnosis chain:** Installed the filter → heard it screaming (high velocity noise) → pulled it and read the on-package guide → based on his system airflow it was rated for ~0.25 in pressure drop new
- **Root cause:** Undersized off-the-shelf filter with too-high face velocity for the system airflow, causing high pressure drop and noise
- **Lesson:** Off-the-shelf filters list airflow vs static-drop guides; a whistling/noisy return signals high air velocity - go bigger/deeper media
- **Source:** [What Air Filter is The Best？] (id: 4R0V6a6Uz3c)

### The 2.5-ton system running 1200 CFM (400 CFM/ton) that surprises people
- **Setting:** Long Branch NJ, 90F design temp, green-grass climate; worked example selecting equipment via Manual S
- **Diagnosis chain:** Load calc gives SHR ~0.88 → SHR chart gives a 17-degree design delta → CFM = sensible BTU / (1.1 x delta) = ~1200 CFM → go to extended performance data in the 1200 CFM column, apply half of excess latent to sensible
- **Root cause:** People use rules of thumb instead of the SHR-driven design series, so a 2.5-ton at 1200 CFM looks wrong to them
- **Lesson:** Follow the SHR-driven math and extended performance data; a 2.5-ton at 1200 CFM is correct when SHR dictates it
- **Source:** [What is Proper System Airflow] (id: sjZR0bTL1Ig)

## Contrarian takes (where Bryan / guests diverge from common teaching)

- **Common teaching:** Hot top floor / cool basement means upsize the AC.
  **Bryan's position:** It's an enclosure problem (airflows, pressures, stack effect), not an AC-capacity problem.
  **Reasoning:** The interlinked pressures and heat bleed can only be found by testing.
  **Source:** [(Podcast) Blower Door Testing, Building Performance & More w⧸ Corbett Lunsford] (id: IlrHazYv84M)

- **Common teaching:** Home performance is about energy efficiency.
  **Bryan's position:** Clients care about comfort, air quality, health, smell, noise, and control - not energy efficiency.
  **Reasoning:** Energy efficiency doesn't enter most clients' minds; give them metrics they care about.
  **Source:** [(Podcast) Blower Door Testing, Building Performance & More w⧸ Corbett Lunsford] (id: IlrHazYv84M)

- **Common teaching:** Use total external static pressure on old systems.
  **Bryan's position:** Prefer component pressure drops (coil/filter/duct) plus supply/return static on older systems.
  **Reasoning:** A dirty blower wheel LOWERS static (won't show as high), so pair readings with visual inspection.
  **Source:** [(Podcast) Blower Door Testing, Building Performance & More w⧸ Corbett Lunsford] (id: IlrHazYv84M)

- **Common teaching:** Just borrow a blower door and start using it.
  **Bryan's position:** It's dangerous - it can cause flame rollout, pull in sewer gas, or set a house on fire; train first.
  **Reasoning:** Depressurizing can back-draft a water heater; practice on your own house and get hands-on training.
  **Source:** [(Podcast) Blower Door Testing, Building Performance & More w⧸ Corbett Lunsford] (id: IlrHazYv84M)

- **Common teaching:** Design ducts at a 0.1 friction rate.
  **Bryan's position:** 0.1 is a myth from the ACCA-wedge midpoint; calculate the real friction rate (0.06-0.18), almost never 0.1.
  **Reasoning:** Friction rate depends on available static and total effective length, which vary per job.
  **Source:** [(Podcast) Common Duct Design Mistakes w⧸ Jack Rise] (id: X2Y1KNFoxug)

- **Common teaching:** Ceiling streaking around supply vents means the ducts need cleaning.
  **Bryan's position:** It's secondary air entraining against the ceiling (like a shower curtain pulling in), not dirty ducts.
  **Reasoning:** If dirt were in the ducts it would coat the furniture; streaking is the entrainment pattern.
  **Source:** [(Podcast) Common Duct Design Mistakes w⧸ Jack Rise] (id: X2Y1KNFoxug)

- **Common teaching:** Upsize the duct to fix an airflow problem.
  **Bryan's position:** Often the real problem is flex compression/sag; fixing/cutting excess flex can solve it.
  **Reasoning:** Upsizing treats the symptom; you're still leaving the compressed/sagging flex.
  **Source:** [(Podcast) Common Duct Design Mistakes w⧸ Jack Rise] (id: X2Y1KNFoxug)

- **Common teaching:** A trained ductulator beats Manual D.
  **Bryan's position:** No - poor execution of a flex system (not Manual D) causes the failures.
  **Reasoning:** Manual D done right works; the losses come from bad flex installation.
  **Source:** [(Podcast) Common Duct Design Mistakes w⧸ Jack Rise] (id: X2Y1KNFoxug)

- **Common teaching:** Compare register capture-hood CFM to furnace static-pressure CFM to find duct leakage.
  **Bryan's position:** You're comparing an inaccurate method to an accurate one; the difference may just be measurement uncertainty, not leakage.
  **Reasoning:** Each method has its own uncertainty; assuming both are perfect leads to false leakage conclusions.
  **Source:** [(Podcast) Measuring Air Flow - Air Density and Direct Air Flow Measurement Part 2 w⧸ Jim Bergmann] (id: 7lEhrcbaeGM)

- **Common teaching:** Apply the grille K-factor when measuring a return-air (inlet) reading.
  **Bryan's position:** No - K-factor only applies on the supply/outlet side; on the inlet side it's 1.
  **Reasoning:** All the air passes before the return grille, so using a <1 K-factor there gives falsely low airflow (the listener Neil's exact problem).
  **Source:** [(Podcast) Measuring Air Flow - Air Density and Direct Air Flow Measurement Part 2 w⧸ Jim Bergmann] (id: 7lEhrcbaeGM)

- **Common teaching:** Techs who measure without knowing what they're doing are more dangerous than those who don't measure.
  **Bryan's position:** (Jim's correction) Not more dangerous - more confused, drawing wrong conclusions.
  **Reasoning:** At least beer-can-cold guys aren't charging customers a lot of money on a wrong conclusion.
  **Source:** [(Podcast) Measuring Air Flow - Air Density and Direct Air Flow Measurement Part 2 w⧸ Jim Bergmann] (id: 7lEhrcbaeGM)

- **Common teaching:** Water vapor has high heat content so humidity strongly affects a hot-wire.
  **Bryan's position:** That's confusing latent heat with specific heat.
  **Reasoning:** Water vapor's specific heat is only ~half of liquid water and a tiny fraction of air, so its effect is negligible.
  **Source:** [(Podcast) Measuring Air Flow - Air Density and Direct Air Flow Measurement Part 2 w⧸ Jim Bergmann] (id: 7lEhrcbaeGM)

- **Common teaching:** A static pressure reading tells you the airflow.
  **Bryan's position:** Static pressure is only an estimation good for selecting the blower tap; it can't measure capacity.
  **Reasoning:** Velocity pressure and duct turbulence skew static readings, throwing capacity off 10-20%.
  **Source:** [(Podcast) Measuring Air Flow - Static ⧸ Capacity & ECM Motors Part 1 w⧸ Jim Bergmann] (id: ryTchnFMem0)

- **Common teaching:** ECM motors are garbage - I've changed 13 this month.
  **Bryan's position:** ECMs fail because of high-static duct systems, not because they're bad motors.
  **Reasoning:** Appliance fixation blames the motor; a well-ducted ECM lasts 20+ years, but high static makes it overspeed and break.
  **Source:** [(Podcast) Measuring Air Flow - Static ⧸ Capacity & ECM Motors Part 1 w⧸ Jim Bergmann] (id: ryTchnFMem0)

- **Common teaching:** You can match an ECM/X13 motor by model number.
  **Bryan's position:** Model number doesn't work; it's the program in the motor and the matched fan/housing.
  **Reasoning:** ECMs are engineered systems (RPM + torque programmed to a specific fan); a look-alike won't move the same CFM.
  **Source:** [(Podcast) Measuring Air Flow - Static ⧸ Capacity & ECM Motors Part 1 w⧸ Jim Bergmann] (id: ryTchnFMem0)

- **Common teaching:** The best filter is the one that catches the most.
  **Bryan's position:** A brick wall catches the most but no air gets through - balance filtration against pressure drop.
  **Reasoning:** A high-MERV/high-pressure-drop filter changes static readings and starves airflow.
  **Source:** [(Podcast) Measuring Air Flow - Static ⧸ Capacity & ECM Motors Part 1 w⧸ Jim Bergmann] (id: ryTchnFMem0)

- **Common teaching:** Low static pressure is good; pretty ductwork works great
  **Bryan's position:** Low static can mean a leaky duct (leaks relieve pressure), and appearance doesn't equal performance - 'unless you're testing you're guessing'.
  **Reasoning:** Sealing leaks raises static; measured performance beats looks (people judge on appearance ~20:1).
  **Source:** [A Duct Up Situation with Sam Myers and Eric Kaiser] (id: wmJ0QBKEbB8)

- **Common teaching:** Humid air is heavier than dry air
  **Bryan's position:** Humid air is LIGHTER than dry air
  **Reasoning:** water vapor's atomic mass (18) is lower than N2 (28) and O2 (32)
  **Source:** [ACFM vs SCFM 3D] (id: GgvSnm_gqt8)

- **Common teaching:** A MERV 8 filter is a MERV 8 in the field
  **Bryan's position:** Charged 'MERV 8' filters drop to MERV 5-6 within days/weeks; MERV-A (52.2J/addendum) test strips the charge to show real efficiency, which is worse in the field
  **Reasoning:** field charge loss is worse than lab results
  **Source:** [Air Filters, They are More Complex Than You Knew w⧸ Lee Andrews] (id: s4EGvkZPqgo)

- **Common teaching:** Electrostatic filters regenerate their charge from airflow
  **Bryan's position:** No known mechanism - especially in humid Florida, moisture and loading particulate destroy the charge
  **Reasoning:** humidity and insulating particulate discharge the fiber
  **Source:** [Air Filters, They are More Complex Than You Knew w⧸ Lee Andrews] (id: s4EGvkZPqgo)

- **Common teaching:** A thicker (4-inch) filter fixes restriction
  **Bryan's position:** Thicker filters lower pressure drop via surface area but 'deleted pleats' (fewer pleats per foot) reduce surface area and load faster - and cheap recycled cardboard/backing collapses
  **Reasoning:** surface area, fiber quality, loft, and structure matter more than thickness alone
  **Source:** [Air Filters, They are More Complex Than You Knew w⧸ Lee Andrews] (id: s4EGvkZPqgo)

- **Common teaching:** A handometer ('good air') confirms proper airflow
  **Bryan's position:** The handometer misses everything - you can't see air, but you can measure it; guys installed $12-14k systems with duct problems and never checked
  **Reasoning:** you must measure static/airflow, not feel it
  **Source:** [Air Flow Diagnostics w⧸ Joseph C Henderson] (id: wWN2IKAqpy4)

- **Common teaching:** An X13 (constant-torque) motor performs like a variable-speed motor
  **Bryan's position:** An X13 has the SAME airflow capability as a PSC (just more efficient) and loses airflow past ~0.5 static - it is NOT a variable-speed motor
  **Reasoning:** constant torque isn't constant CFM
  **Source:** [Air Flow Diagnostics w⧸ Joseph C Henderson] (id: wWN2IKAqpy4)

- **Common teaching:** 0.5 in. total static is fine to start
  **Bryan's position:** Start at ~0.3 - starting at 0.5 means you're already maxed with no room for a dirty filter/coil
  **Reasoning:** you'll only lose airflow from there and never get it back
  **Source:** [Air Flow Diagnostics w⧸ Joseph C Henderson] (id: wWN2IKAqpy4)

- **Common teaching:** The balloon gets sucked in because burning oxygen lowers total air pressure (Dalton's law)
  **Bryan's position:** Wrong - oxygen converts to CO2 (conservation of energy) so pressure stays the same; it's the Ideal Gas Law - cooling after the fire goes out lowers pressure
  **Reasoning:** energy can't be destroyed, oxidation makes CO2 canceling the oxygen loss; temperature drop is what drops pressure
  **Source:** [Air Is Stuff] (id: I1jYv-jetNY)

- **Common teaching:** A whistling filter door is just a filter door
  **Bryan's position:** Noise means unsealed straws pulling moisture/dirt in - seal the cabinet and you can visibly see the temperature split change
  **Reasoning:** the louder it whistles the more air it's pulling through gaps
  **Source:** [Air Sealing and Static Pressure Diagnostics] (id: AWecM1MfuEE)

- **Common teaching:** A blower wheel with broken fins just needs a new wheel
  **Bryan's position:** Broken blower-wheel fins are a static-pressure symptom (pulsation) - find the cause (static), don't just sell the wheel
  **Reasoning:** high static pulsation pushes the fins loose
  **Source:** [Air Sealing and Static Pressure Diagnostics] (id: AWecM1MfuEE)

- **Common teaching:** A static pressure probe is a pitot tube
  **Bryan's position:** It is NOT - a pitot tube has an end hole (tube within a tube) to read velocity pressure; a static tip only reads static
  **Reasoning:** residential techs don't do pitot traverses/CFM math; use static for resistance, true flow grid for CFM
  **Source:** [Airflow & Static Pressure with Matt Bruner & Bryan Orr] (id: eHzYalJXE88)

- **Common teaching:** Just put a bigger filter in to fix airflow
  **Bryan's position:** Fixing one part of the equation isn't that simple - raising airflow raises static everywhere (fan law square)
  **Reasoning:** static goes up with the square of airflow, and the coil/transition add drops
  **Source:** [Airflow & Static Pressure with Matt Bruner & Bryan Orr] (id: eHzYalJXE88)

- **Common teaching:** To improve airflow you must replace all the ductwork
  **Bryan's position:** Not true - replacing the accessible portion with bigger duct (adapted down where you can't) still improves flow, like upsizing part of an undersized water line
  **Reasoning:** pursuit of the perfect stops you from delivering the good; balancing dampers make it work
  **Source:** [Airflow Before Charging] (id: FFYvSwCIYho)

- **Common teaching:** Design ducts tight to spec / lower velocity is a problem
  **Bryan's position:** Make ducts BIGGER and use balancing dampers - Manual D says too-low velocity really isn't a problem
  **Reasoning:** oversized ducts + balancing dampers solve many problems and are how commercial does it
  **Source:** [Airflow Before Charging] (id: FFYvSwCIYho)

- **Common teaching:** Mastic on the outside of a flex duct is what seals it (inspectors look for it).
  **Bryan's position:** External mastic is just a shortcut inspectors in Florida adopted; neither of the Air Duct Council's two approved methods includes outside mastic - flex leaks at the inner-liner-to-collar and collar-to-duct-board connections.
  **Reasoning:** Seal the inner liner for the air seal; use the outer jacket only for a continuous vapor barrier. (Still apply external mastic when needed just to pass inspection.)
  **Source:** [Better Duct Installation Practices - Kalos Meeting] (id: 3m1eRBXDM5I)

- **Common teaching:** An outer panduit/drawband strap on the jacket is fine, and mastic fills any gap.
  **Bryan's position:** An outer panduit compresses the insulation - which is why the Flex Duct Council doesn't show it; compressed insulation loses R-value and sweats.
  **Reasoning:** Insulation needs trapped air to insulate (like stomping down blown R30); you need the insulation butted fully to the duct board and an intact vapor barrier, not crushed.
  **Source:** [Better Duct Installation Practices - Kalos Meeting] (id: 3m1eRBXDM5I)

- **Common teaching:** Getting the equipment running again is the job done.
  **Bryan's position:** That's only 'servicing the machine' - the bigger win is reading static/whole-home airflow to find design problems (returns, filters, duct) and solve them.
  **Reasoning:** 7 of 10 homes have HVAC/airflow issues; fixing them helps the customer and grows the ticket honestly (vs scaring/upselling).
  **Source:** [Boost Your HVAC Ticket Size： Deploying Static Pressure Probes with MeasureQuick] (id: y4y1EtgEs9w)

- **Common teaching:** Air leakage matters because it wastes energy (a few dollars a month on the meter).
  **Bryan's position:** Joe Medosch: stop framing air leakage as an energy penalty; it is primarily a contaminant/exposure pathway and health issue.
  **Reasoning:** Homes act like a sponge that concentrates indoor pollutants; the health impact (asthma, days off work) is what customers actually value and will pay to fix, not the ~$5/month energy savings.
  **Source:** [Building Science 101 for HVAC Contractors w⧸ Bill Spohn and Joe Medosch] (id: jMTxblZcTzE)

- **Common teaching:** Insulation acts as an air barrier.
  **Bryan's position:** Insulation is not an air barrier unless it is a rigid foam or is in tight contact with a dedicated air barrier; loose fiberglass with an air gap becomes a filter.
  **Reasoning:** Air moves through fiberglass, so it must be pressed against a sealed air barrier (e.g., drywall/rigid foam) to be effective.
  **Source:** [Building Science 101 for HVAC Contractors w⧸ Bill Spohn and Joe Medosch] (id: jMTxblZcTzE)

- **Common teaching:** Just add more holes/vents so the blower-door number comes in above the threshold and you avoid installing a ventilation fan.
  **Bryan's position:** Do not drill holes to fail-pass a blower-door test; if you build tight you must ventilate right with a real (balanced) strategy.
  **Reasoning:** Uncontrolled leakage brings contaminants in from unknown places; balanced ventilation plus dehumidification gives a controlled, healthier result.
  **Source:** [Building Science 101 for HVAC Contractors w⧸ Bill Spohn and Joe Medosch] (id: jMTxblZcTzE)

- **Common teaching:** Rely on spray/contact glue and a Panduit strap to hold and seal duct connections long-term.
  **Bryan's position:** Contact cement is only a temporary hold and a Panduit strap is just a basic mechanical connection; use cleaned surfaces plus mastic/foil tape (and an outward-cinching stapler) for a lasting seal.
  **Reasoning:** Contact cement dries out, becomes brittle and separates; the mastic (or the tape adhesive), not the fab tape or glue, is what actually holds long-term.
  **Source:** [Discussing Ducts Types and Tips] (id: VDJotlJj3Mo)

- **Common teaching:** Just do the specific repair the customer called about and nothing more.
  **Bryan's position:** Look at the whole system and honestly report what you find; when you take off panels to reach the problem, tell the customer what you saw and give them the menu to decide.
  **Reasoning:** Providing premium, thorough, honest service (vs competing only on price) is what value looks like and drives referrals; the customer said prior techs did only the required task and never mentioned obvious issues.
  **Source:** [Duct DISASTER at an NBA Players Home] (id: 75Q15TVoazE)

- **Common teaching:** Use a fixed friction rate (0.08 or 0.1) and a 0.5-inch external static from the furnace; set your duck slide at 0.1 and you get 0.1 static in the supply.
  **Bryan's position:** (via Janowiak) That's wrong - fixating on 0.5 external static is 'a load of crap'; friction rate must be calculated from available static and total effective length, and modern furnaces publish operation from 0.15 to a full inch.
  **Reasoning:** External static is relative: seeing 0.7-0.9 is normal once real coil (0.3) and filter (up to 0.4) drops are included; a random 0.08 friction can't be assumed because if available static is too low, a predictable airflow won't be delivered.
  **Source:** [Duct Design for Great Results w⧸ Ed Janowiak (ACCA)] (id: -KqmAQgUXY4)

- **Common teaching:** Brand X furnace/equipment is junk (blames the manufacturer for nuisance limit trips, cracked heat exchangers, failed blowers).
  **Bryan's position:** It's usually low airflow / high static pressure, not the brand — installing the same-size Brand Y with the same low airflow will fail the exact same way.
  **Reasoning:** High total external static pressure causes high blower watt draw, nuisance limit trips, frozen coils, and heat exchanger/compressor failures regardless of brand; ignoring how the equipment operates guarantees recurring problems.
  **Source:** [Fan Law 2 for Techs with Adam Mufich] (id: NzlsB9R6mbc)

- **Common teaching:** Just order the cheapest coil that matches the tonnage from the supply house.
  **Bryan's position:** Select the coil (and filter) by lowest rated pressure drop for the AHRI match, not by price or cabinet width — the same coil often comes in multiple slab sizes, and nobody ever asks the counter for the lowest pressure drop.
  **Reasoning:** A high-pressure-drop coil (e.g., 0.379 vs 0.20) can nearly equal your whole target static by itself; a wider low-pressure-drop coil with a transition keeps static within spec and extends equipment life.
  **Source:** [Fan Law 2 for Techs with Adam Mufich] (id: NzlsB9R6mbc)

- **Common teaching:** Tension a belt to 1/2 in (or 1 in) of deflection
  **Bryan's position:** That's a myth -- there's no fixed force behind the squeeze
  **Reasoning:** Deflection depends on hand strength, belt length, and belt type; use a proper tensioning tool
  **Source:** [HVAC Belt Tension] (id: rNBt7LN-8ao)

- **Common teaching:** Set belt tension based on blower motor amperage
  **Bryan's position:** A terrible idea -- over-tightening binds the bearings and raises amp draw, damaging the motor
  **Reasoning:** A motor can run well below FLA depending on sheave setting, so amperage isn't a tension proxy
  **Source:** [HVAC Belt Tension] (id: rNBt7LN-8ao)

- **Common teaching:** The airflow is good (eyeballed/felt)
  **Bryan's position:** Airflow is measured; low superheat, low suction, and low head pressure mean the airflow is NOT good
  **Reasoning:** 'Good' is a measurement, not a feeling
  **Source:** [HVAC Commissioning on Steroids w⧸ Jim Bergmann & Chris Hughes] (id: lvMjm3YwUY8)

- **Common teaching:** Fix performance problems by adjusting refrigerant charge
  **Bryan's position:** Airflow and duct leakage are the real problems; charge is the lowest tier
  **Reasoning:** We replace under-performing equipment without fixing airflow/leakage
  **Source:** [HVAC Commissioning on Steroids w⧸ Jim Bergmann & Chris Hughes] (id: lvMjm3YwUY8)

- **Common teaching:** Supply duct leakage is the main concern
  **Bryan's position:** Return leakage is worse because it draws hot attic air (vs milder infiltration on the supply side)
  **Reasoning:** 120 F attic air into the return hits the coil directly
  **Source:** [HVAC Commissioning on Steroids w⧸ Jim Bergmann & Chris Hughes] (id: lvMjm3YwUY8)

- **Common teaching:** You can look at ductwork and tell it doesn't leak
  **Bryan's position:** Even a 20-year veteran got burned -- you must duct-leakage test
  **Reasoning:** The grandma's-house leak was invisible behind caulk
  **Source:** [HVAC Commissioning on Steroids w⧸ Jim Bergmann & Chris Hughes] (id: lvMjm3YwUY8)

- **Common teaching:** Pre-made traps are fine (and they look nice)
  **Bryan's position:** In high-static/commercial applications they're often not deep enough; size trap depth to the cabinet static
  **Reasoning:** As filters load, static rises and shallow traps get sucked dry
  **Source:** [HVAC Condensate Drain Troubleshooting： Traps, Vents & Static Pressure] (id: LGgET3gRY20)

- **Common teaching:** A wide or long trap holds water well
  **Bryan's position:** It's the vertical depth (water column) that keeps a trap sealed, not width/length
  **Reasoning:** A shallow trap shifts with static pressure no matter how wide
  **Source:** [HVAC Condensate Drain Troubleshooting： Traps, Vents & Static Pressure] (id: LGgET3gRY20)

- **Common teaching:** Fix the ducts on whatever equipment is there.
  **Bryan's position:** Rule 1: do NOT fix ducts on grossly oversized equipment - up to 40% of the load can be through the duct work, so renovating ducts reduces the load and the oversized equipment then short-cycles and leaves people clammy or overshooting. Get equipment size right first.
  **Reasoning:** Reducing duct losses changes the load; oversized equipment becomes a manufactured problem you now own.
  **Source:** [How to Confidently Create a Duct Renovation Scope of Work w/ David Richardson] (id: 5eiv-0518mQ)

- **Common teaching:** Provide design/airflow diagnostics for free to win the job; if you test your own install and find problems you must fix them free.
  **Bryan's position:** Get paid for your designs (Rule 4) and for airflow diagnostics; finding problems on your own past install is not a free-fix obligation - the customer paid for your knowledge and techniques improve over time (like surgery advancing to two small incisions).
  **Reasoning:** Too much knowledge and time go into design to give it away; free design gets undercut by cheaper competitors.
  **Source:** [How to Confidently Create a Duct Renovation Scope of Work w/ David Richardson] (id: 5eiv-0518mQ)

- **Common teaching:** A flow hood gives an accurate reading no matter what.
  **Bryan's position:** Not necessarily - as air enters it bounces and creates eddy currents; the flow straightener is what makes it more accurate, and every hood has a minimum/maximum range.
  **Reasoning:** Turbulence hitting the pitot array skews readings; you need straightened flow and enough velocity.
  **Source:** [How to Measure CFM w/ The Testo 420 Flow Hood] (id: kAjT-VujA6I)

- **Common teaching:** High static pressure means a ductwork problem
  **Bryan's position:** Don't assume a high static number is a ductwork problem - it can be caused by a system producing too much airflow.
  **Reasoning:** Excess airflow raises both supply and return static.
  **Source:** [How to Measure Total External Static Pressure (TESP)] (id: 6uMqw69XkRw)

- **Common teaching:** A good salesperson taking static pressure is enough to size the replacement
  **Bryan's position:** Static pressure tells you almost nothing about whether a new system will work unless you also know the actual CFM.
  **Reasoning:** Fan Law 2 makes static rise nonlinearly with airflow, so an assumed CFM leads to surprises.
  **Source:** [How to Predict Air Flow Issues in the Sales Process] (id: cGT6ZA3bcIg)

- **Common teaching:** 400 CFM per ton is the airflow to set
  **Bryan's position:** The 400 CFM/ton rule of thumb does not always apply; select the design airflow from the equipment performance data based on the load's sensible heat ratio.
  **Reasoning:** Humid climates want ~350 CFM/ton for latent removal; the manufacturer table and Manual J drive the number.
  **Source:** [How to use Static Pressure to Measure and Set Air Flow] (id: ddhQrxuIbUI)

- **Common teaching:** Filter velocity is what matters for sizing
  **Bryan's position:** Focus on pressure differential, not velocity - the blower cares about pressure drop; keep filters at ~0.1 in w.c. or less.
  **Reasoning:** Low pressure differential automatically means low velocity.
  **Source:** [How to use Static Pressure to Measure and Set Air Flow] (id: ddhQrxuIbUI)

- **Common teaching:** 'I checked the airflow and it's fine' after inspecting filter/coil/blower and static
  **Bryan's position:** You didn't check airflow — static pressure and clean components don't confirm delivered CFM
  **Reasoning:** A misprogrammed blower (wrong terminal, pin, G-call) can deliver low airflow with clean parts and normal static
  **Source:** [Impact of Airflow on Refrigerant Measurements and Performance] (id: hCZEg_DGCf0)

- **Common teaching:** Closing a door on a room makes it cold because it gets less air.
  **Bryan's position:** It usually makes the room too hot (over-conditioned) in heating.
  **Reasoning:** The pressure rise barely reduces airflow (~10%) but increases dwell time, so the air spends longer shedding heat into the room.
  **Source:** [Is a House Really just a Big Duct System？ w⧸ Eric Kaiser] (id: YUjv96bbQOM)

- **Common teaching:** A moldy house was set too warm / left the thermostat up too high.
  **Bryan's position:** Setting the house too cold (below the outdoor dew point) often makes it worse.
  **Reasoning:** Interior surfaces drop below outdoor dew point, so infiltrating humid air condenses in walls and hidden spaces.
  **Source:** [Is a House Really just a Big Duct System？ w⧸ Eric Kaiser] (id: YUjv96bbQOM)

- **Common teaching:** The inches-of-water-column gauge you set gas pressure with is fine for house pressures.
  **Bryan's position:** You need a Pascal-resolution, autozeroing manometer for house pressure diagnostics.
  **Reasoning:** House pressures are tiny (single Pascals) over a huge surface area, and cheap gauges drift 0.2-0.4 in and lack resolution.
  **Source:** [Is a House Really just a Big Duct System？ w⧸ Eric Kaiser] (id: YUjv96bbQOM)

- **Common teaching:** High-SEER numbers (e.g., a 30-SEER ductless) mean a great unit.
  **Bryan's position:** Those numbers can be gamed by artificially raising suction pressure/evaporator temperature so the unit cools but doesn't dehumidify.
  **Reasoning:** Sensible BTUs (cooling) are cheap; latent BTUs (drying) are expensive — a unit good at cooling and bad at drying shows nice numbers.
  **Source:** [Mini-Split Cleaning & Maintenance] (id: GRhAWA4tz1I)

- **Common teaching:** Always do the full cleaning process the same way every time.
  **Bryan's position:** You clean things when they get dirty; a rigid always-the-same process disenfranchises techs because in the field it's not always necessary — you can't replace a discerning technician with a process.
  **Reasoning:** Frequency depends on the market and how dirty the unit actually is (every 6 months vs every 3 years).
  **Source:** [MiniSplit Air Conditioning Cleaning Practices] (id: DHWcSYPLLVw)

- **Common teaching:** A low static reading on the return means you have good airflow.
  **Bryan's position:** Testing behind the point of restriction (e.g. a clogged filter or coil) gives a false low — the blower can be under severe high static and you won't see it there.
  **Reasoning:** A restriction eliminates airflow before that point, lowering duct pressure, while a much stronger vacuum exists just after the restriction where you should actually measure.
  **Source:** [Practical Training on Manometers] (id: QHHMC5K2moU)

- **Common teaching:** The HVAC School 9-panel method: wipe down the metal, tape and squeegee the connection.
  **Bryan's position:** Kalos doesn't clean unconditioned collars or rely on tape-and-squeegee; they mastic between the collar and inner liner and Panduit-strap on the ridge, because the collar sizes leave no clean area for tape.
  **Reasoning:** Mastic holds a mechanical bond; tape-and-squeegee doesn't suit their collars, and the mechanical seal on the ridge is what actually makes it airtight.
  **Source:** [Pro Tips for Perfect Flex Duct to Duct Board Connections with Bert] (id: iygU_hFM9Os)

- **Common teaching:** Low static pressure means good airflow; moving the return probe below the filter shows lower static, so the filter's fine.
  **Bryan's position:** Static is not airflow - low static can mean the blower isn't at full speed, a module failed, it's in dehum/stage-1, a dirty blower wheel, or leaking ducts; and static is always higher closer to the blower, so 'lower below the filter' proves nothing.
  **Reasoning:** Like head pressure with a non-pumping compressor, low pressure can be a sign of a problem, not health; static must be read with the blower on high and interpreted against a baseline.
  **Source:** [Proper Use of Manometers for HVAC Technicians] (id: a9tX40eOJfw)

- **Common teaching:** Match a burned-out EBM fan motor by wattage
  **Bryan's position:** Do NOT match an EBM (pulsed, efficient) motor to a cannonball by wattage — a 31W EBM does not equal a 31W cannonball
  **Reasoning:** The EBM's wattage rating is a max; it pulses and burns a fraction of it. Match the fan BLADE exactly (blade determines RPM/airflow), and a generic 'rescue' variable motor (4-25W, 1515-1725 RPM) covers ~90% of cases with one part
  **Source:** [Rack Refrigeration Cycle Part 11 - Evaporator Airflow] (id: RI1wD7nyGL4)

- **Common teaching:** Ductless systems dehumidify amazingly / a good properly-sized AC never needs a dehumidifier
  **Bryan's position:** Ductless dehumidifies well only at full speed; as it stages down the compressor spins slower, suction pressure rises, evaporator warms, SHR climbs (one Mitsubishi 'Arizona' model match has SHR of 1 = zero moisture removal). And an AC only dehumidifies while it's cooling, so part-load and off-seasons need a dedicated dehumidifier.
  **Reasoning:** Select ductless on tested SHR at unloaded condition; an air conditioner is a great dehumidifier but only when there's a cooling call.
  **Source:** [Residential AC System Installation] (id: gZQqjXhuMTI)

- **Common teaching:** Aeroseal is like fix-a-flat gimmickry / coats the inside of the ducts.
  **Bryan's position:** Bryan was initially skeptical but changed his mind; it only bonds at leak points in the pressurized (fog-like) system, not as a coating.
  **Reasoning:** Bill Spohn, Eric, and Jim Bergman (people who won't back junk) had it done and speak highly of it.
  **Source:** [Sealing Ducts From the Inside w⧸ Sean Harris] (id: bj962pMF1-Q)

- **Common teaching:** You should always measure actual CFM at registers.
  **Bryan's position:** Measuring velocity is far better than measuring nothing; many techs skip the vane anemometer because free-area/K-factor math overwhelms them, and lots who think they've done K-factor correctly haven't.
  **Reasoning:** Velocity comparisons give useful qualitative info and flag over/under-fed rooms and noise issues.
  **Source:** [Short 16 - Air Velocity is Useful] (id: Sz6A9-ihX-g)

- **Common teaching:** You should always see about a 20-degree delta T.
  **Bryan's position:** Delta T follows a curve based on humidity and airflow, not a single number; 20 is only a rough midpoint.
  **Reasoning:** Latent heat of vaporization means moist (high-enthalpy) air yields a lower delta T; dry air a higher one.
  **Source:** [Short 2 - Delta T] (id: c1LCnU3lO-M)

- **Common teaching:** Set fan speeds the way the furnace came from the factory, or one tap for cool and one for heat because you were told to.
  **Bryan's position:** That's guessing; look up the fan charts and set airflow to the actual capacity and application (sensible/latent, temperature rise).
  **Reasoning:** Equipment rarely delivers nameplate BTUs, so the CFM/BTU ratio must be set from real data, not defaults.
  **Source:** [Short 4 - Blower Taps (Audio Only)] (id: 2kgNFetuWKs)

- **Common teaching:** A brand-new high-end system will fix a bad back room
  **Bryan's position:** It won't - a 5-ton Infinity on bad ducts still leaves a 4-degree difference
  **Reasoning:** You get great dehumidification but the airflow/duct problem remains
  **Source:** [Static Pressure Fundamentals] (id: o6OVAUJXeuU)

- **Common teaching:** A static-pressure tip is a pitot tube
  **Bryan's position:** It is NOT - a pitot tube is a tube-within-a-tube that measures velocity/airflow and needs a precision manometer
  **Reasoning:** A static tip has a closed end with side ports pointed against flow to read only balloon (static) pressure
  **Source:** [Static Pressure and Manometer Basics] (id: Jp2pZydCp28)

- **Common teaching:** Low suction pressure means add refrigerant
  **Bryan's position:** On a TXV system don't add refrigerant based on low suction pressure alone - also measure superheat
  **Reasoning:** Low suction pressure with normal-to-low superheat points to low indoor airflow or low load, not undercharge
  **Source:** [Symptoms of Low Evaporator Airflow] (id: x4_FkNNGzFo)

- **Common teaching:** Use total external static pressure + a fan table to determine airflow
  **Bryan's position:** That method fails when internal components (coil/blower) are dirty - and not by a little
  **Reasoning:** Dirty components lower the measured pressures; going to the fan table then reports MORE airflow, so you're off in the opposite direction, a lot
  **Source:** [System Airflow Measurement w/ TEC TrueFlow] (id: USMxJexJvbo)

- **Common teaching:** Flex duct is inferior and should be avoided
  **Bryan's position:** Flex works fine if installed correctly — pulled tight with hard-pipe elbows at turns; a ducted mini-split ran 92 CFM through 35 ft of 6-inch flex quietly
  **Reasoning:** Installation quality matters more than material; results can't be disputed
  **Source:** [Testing out a High Performance HVAC Installation] (id: DhXYd2Um1uE)

- **Common teaching:** Replacing windows saves significant energy
  **Bryan's position:** Joe: you will not benefit energy-wise from replacing windows — they're low R-value, payback is ~40 years; sunshades/screens give quicker payback and the real gain is sealing the envelope
  **Reasoning:** Extensive research shows window energy-savings claims are false
  **Source:** [The Duct We Tend to Forget w⧸ Joe Medosch] (id: DpX20OkmgoU)

- **Common teaching:** You can seal a building too tight
  **Bryan's position:** Joe: the issue isn't too tight — it's whether you know where your make-up air comes from; you seal the envelope to control the hole, then provide designed ventilation
  **Reasoning:** There is always a hole; controlling and treating it is the point
  **Source:** [The Duct We Tend to Forget w⧸ Joe Medosch] (id: DpX20OkmgoU)

- **Common teaching:** ZPD tells you how connected a room is to outside (e.g., 50% connected)
  **Bryan's position:** Genry: it doesn't — it's just a ratio; it lacks legitimacy technically, though it can still legitimately help present proof of leakage to a client
  **Reasoning:** Same ZPD value can come from a 3-foot hole or a 1-inch hole
  **Source:** [The Flaw With Zonal Pressure Diagnosis] (id: 7bXPNva82qc)

- **Common teaching:** If you have a bad static condition, put in an ECM motor to fix it
  **Bryan's position:** That's hogwash — ECM motors are air-over motors with the same restrictions; you must fix the duct work, not swap the motor or add horsepower
  **Reasoning:** Air is the load that cools the motor; higher horsepower on bad static fails prematurely
  **Source:** [The Great Heat Pump Revolt of 2026 and How To Avoid It with Steve Rogers, Russ King and Chris Hughes] (id: OioG8T_zwaA)

- **Common teaching:** Just focus on picking the right capacity equipment
  **Bryan's position:** Always consider the other side of the equation — the load; the house load is not cast in stone (add insulation, air-seal the lid) so a single-speed unit can match, sometimes avoiding VRF
  **Reasoning:** Permanent load reduction (air-seal the lid first) improves comfort and lets simpler equipment work
  **Source:** [The Great Heat Pump Revolt of 2026 and How To Avoid It with Steve Rogers, Russ King and Chris Hughes] (id: OioG8T_zwaA)

- **Common teaching:** Prioritize keeping static pressure under control
  **Bryan's position:** Maintain proper airflow first — let the equipment suffer before you break the house (mold/humidity); replace a motor rather than damage the house
  **Reasoning:** The house needs the delivered airflow; equipment is replaceable
  **Source:** [The Great Heat Pump Revolt of 2026 and How To Avoid It with Steve Rogers, Russ King and Chris Hughes] (id: OioG8T_zwaA)

- **Common teaching:** A dirty filter overloads the blower motor and raises amps
  **Bryan's position:** Rick: on a blower, a dirty filter restricts air, removes load, so amps DROP and the motor speeds up — but low amps are still bad (inefficient, overheating windings, failing capacitor)
  **Reasoning:** Fewer 'boxes of air' = less load on the air-over blower motor
  **Source:** [The Impact of Static Pressure on Fan and Blower Motors w⧸ Rick Streacker] (id: 1X9cXMrWc1o)

- **Common teaching:** If you have a bad static condition, put in an ECM
  **Bryan's position:** Rick: that's hogwash — ECMs have the same air-over restrictions; correct static by fixing duct work, not the motor
  **Reasoning:** These are all air-over motors needing the designed air load to cool
  **Source:** [The Impact of Static Pressure on Fan and Blower Motors w⧸ Rick Streacker] (id: 1X9cXMrWc1o)

- **Common teaching:** 0.1 in.w.c. per 100 ft is a magic friction rate that always tells you the air in a duct.
  **Bryan's position:** 0.1 is not magic and no longer works reliably on modern residential systems; forced to pick a rule of thumb, use ~0.06.
  **Reasoning:** Modern houses are bigger, filters are restrictive, coils are denser and blowers are weaker; 0.1 worked when houses/coils/filters were smaller. Managing friction (duct sizing, dampers) is cheaper and easier than managing blower power in residential.
  **Source:** [Understanding Airflow: David Bowie, a Used Car Lot, and a 40 cent Tool with Alex Meaney] (id: uIXfiuY3i9U)

- **Common teaching:** The homeowner isn't complaining, so the job is fine.
  **Bryan's position:** Homeowner-not-complaining is an incredibly low bar; judge yourself with tools (TrueFlow grid, MeasureQuick, verifiable data), not the homeowner.
  **Reasoning:** An oversized system on undersized ducts fails in ways the homeowner never notices, which bleeds bad practice into everyday work.
  **Source:** [Understanding Airflow: David Bowie, a Used Car Lot, and a 40 cent Tool with Alex Meaney] (id: uIXfiuY3i9U)

- **Common teaching:** A capture-hood reading of 440 CFM means airflow is 10% high
  **Bryan's position:** Jim: it may just be air density - an ECM holds 400 SCFM, so if air density is off you can read higher ACFM while mass flow is correct
  **Reasoning:** ECM motors work off RPM and torque and speed up as air gets lighter to hold constant standard CFM, so an actual-CFM reading can mislead you about mass flow
  **Source:** [Volume Flow Rate vs Mass Flow Rate w⧸ Jim Bergmann] (id: FMSl9qexPRw)

- **Common teaching:** You can never double-filter / never put two filters in series
  **Bryan's position:** You can double filter as long as total static pressure drop doesn't push the system above design; a low-resistance carbon pre-filter plus a 4-inch media is fine
  **Reasoning:** It's only a matter of the static pressure drop, not a hard rule; filtration strategy is flexible if you have surface area and watch static
  **Source:** [What Air Filter is The Best？] (id: 4R0V6a6Uz3c)

- **Common teaching:** A MERV 13 filter will always starve a system of air and freeze it up
  **Bryan's position:** It could, but only when surface area is too small and headroom is gone - a large-surface-area MERV 13 has plenty of surface area and won't be a problem
  **Reasoning:** You've seen it freeze in a specific application without enough headroom, not because MERV 13 is inherently bad
  **Source:** [What Air Filter is The Best？] (id: 4R0V6a6Uz3c)

- **Common teaching:** Look for a 20-degree delta T and you're good
  **Bryan's position:** You can have a 20-degree delta T and the system may not be working at all - your target might be 23-24 or as low as 15 in dehumidification/low airflow; delta T alone can't confirm operation
  **Reasoning:** Delta T is a ratio of mass flow, airflow, and humidity - all three must be known to interpret it; you can't trust it when the system is staged down or in dehumidification mode
  **Source:** [What Should the Air Delta T be？ (Air Temperature Split)] (id: _pD-rRCNv8k)

- **Common teaching:** Set airflow at 400 CFM per ton (or 350 in wet markets) as a default
  **Bryan's position:** Ed: that's the beer-can-cold of airflow; the SHR of the structure sets the target airflow - arbitrarily starting at 350 CFM/ton in a wet market designs a less efficient system
  **Reasoning:** Doing airflow on total capacity at 400 CFM/ton can actually move MORE air than the Manual S process; SHR below 0.8 means more than 400, above 0.85 means less
  **Source:** [What is Proper System Airflow] (id: sjZR0bTL1Ig)

- **Common teaching:** Oversizing is fine because it's two-stage or variable, or round the design temp up for more capacity
  **Bryan's position:** Don't exceed 15/20/30% oversizing by compressor type; Manual J already rounds design temps in 5-degree deltas, so gaming the temp gains you nothing
  **Reasoning:** Manual J codes everything in 5-degree deltas (rounds down 1 or up 3); intentional oversizing puts you in the 'butt-kicking line' or requires ancillary dehumidification with documentation
  **Source:** [What is Proper System Airflow] (id: sjZR0bTL1Ig)

## Diagnostic reasoning chains

**#BertLife - Flex Duct Repair Terror** (id: Rl2Ej7fdy1U)
- High bill -> found 2nd stage heat not working -> deeper inspection under trailer -> damaged/unrated flex duct is the real story

**(Podcast) Blower Door Testing, Building Performance & More w⧸ Corbett Lunsford** (id: IlrHazYv84M)
- Comfort/odor/noise complaints blamed on HVAC -> often the enclosure (air leakage) is the cause -> blower door + IR + zonal pressure diagnostics to locate it
- CFM50 = fan airflow holding the house at 50 Pa; 1 CFM in = 1 CFM out so it quantifies total leakage; divide by house volume for ACH50
- Failed third-party duct-tightness test -> own the tester and test before leaving so you never get called back

**(Podcast) Common Duct Design Mistakes w⧸ Jack Rise** (id: X2Y1KNFoxug)
- Existing duct measures 24x8 and lands opposite 0.1 on a ductulator -> someone just used 0.1; likely undersized (basement/furnace runs) or oversized (overhead runs)
- High supply/return static -> check flex for compression/sag first (straighten it) before condemning duct size
- Room too hot/cold = not enough airflow (BTUs ride on CFM): CFM = sensible BTU / (1.1 x delta-T x altitude factor)

**(Podcast) Measuring Air Flow - Air Density and Direct Air Flow Measurement Part 2 w⧸ Jim Bergmann** (id: 7lEhrcbaeGM)
- Humidity probe reads higher RH in the supply than the return -> not a broken probe; cooling raises relative humidity while lowering absolute humidity
- Furnace heat-exchanger crack check -> plug the flue, put a hot-wire inside the heat exchanger, run the blower; any detectable air movement indicates a leak

**(Podcast) Measuring Air Flow - Static ⧸ Capacity & ECM Motors Part 1 w⧸ Jim Bergmann** (id: ryTchnFMem0)
- Non-repeatable capacity readings -> traced to inaccurate instruments, not impossible physics
- Blower over-amps with the door off, drops with the door on -> door off removes duct/coil restriction, giving the blower more mass to move (amp draw tracks mass flow)
- 7 of 10 systems have incorrect airflow (mostly poor duct design) -> don't try to fix it at the appliance; treat the whole system

**A Common Cased Coil Issue** (id: PjWScoD3NH4)
- Lopsided coil starves ~1/3 of the coil -> low suction (~115) and low superheat (~6F) -> repositioning the coil restores suction (155) and superheat (15F), 20F split, with no refrigerant added.

**A Commonly Missed Airflow Issue w⧸ Bert** (id: HvhaFcc7cLQ)
- Front-facing unit -> inspect for back insulation being sucked into the blower -> half the intake blocked -> secure the insulation to restore airflow.

**A Duct Up Situation with Sam Myers and Eric Kaiser** (id: wmJ0QBKEbB8)
- Repeated blower-motor failures -> deeper diagnostics -> high static from a sharp S-turn takeoff -> two-port differential (0.12 upper vs 0.08 between ports) reveals turbulence in the lower half of the duct.
- Add kinks/turns to a duct -> flow collapses; straighten/pull flex tight -> static drops and flow rises.

**ACFM vs SCFM 3D** (id: GgvSnm_gqt8)
- Hot/dry climate -> lighter air -> may target more than 400 ACFM to hit the same lb/min over the coil.
- Cold/dry climate -> denser air -> may target less than 400 ACFM; humid or high-altitude air -> lighter -> higher ACFM.

**Air Filters, They are More Complex Than You Knew w⧸ Lee Andrews** (id: s4EGvkZPqgo)
- Filter static pressure stops rising over time -> filter is unloading (releasing particles) -> low real efficiency despite looking dirty.
- Coarse large-diameter fibers -> lower 0.4-micron capture (~35-40%) -> not acceptable for healthcare/critical applications (need fine fiber ~60-75%).

**Air Flow Diagnostics w⧸ Joseph C Henderson** (id: wWN2IKAqpy4)
- Point the static tip INTO the airflow; too many turns near inlet/outlet = system effect = garbage static readings even if they look low (dead air).
- PSC/X13 below rated amps = moving less air; constant-CFM at max amps = right airflow but too costly with no headroom.
- All static on the return (e.g. 0.4 of 0.5) = undersized return -> infiltration and comfort loss even if coil airflow is okay.

**Air Is Stuff** (id: I1jYv-jetNY)
- Fire heats air in bottle -> goes out -> temperature drops -> per PV=nRT pressure drops -> higher-pressure outside air pushes the balloon in.

**Air Sealing and Static Pressure Diagnostics** (id: AWecM1MfuEE)
- Low suction pressure + cold suction line -> low evaporator temperature due to airflow -> check airflow first before charge/TXV.
- High total external static -> check filter (size/dirty), then blower settings, then coil (but total external static won't show a dirty fan-coil coil since it's inside the device).

**Airflow & Static Pressure with Matt Bruner & Bryan Orr** (id: eHzYalJXE88)
- 3-ton unit at ~800 CFM (~265 CFM/ton) = effectively a 2-ton -> the room is hot from airflow, not necessarily needing a bigger unit.
- Improve the filter -> airflow rises -> static rises everywhere else (measure static AFTER, it can be higher than before).

**Airflow Before Charging** (id: FFYvSwCIYho)
- System not set up for the right airflow (wrong tap/tonnage) -> static looks great but airflow is half -> static is meaningless until setup is corrected.
- Too much airflow -> raises coil/saturation temperature -> less dehumidification (bad in a humid market).

**Better Duct Installation Practices - Kalos Meeting** (id: 3m1eRBXDM5I)
- You can prove flex-duct turbulence in the field: with an airflow hood on a register, put a few bends in the flex and watch the delivered CFM drop from the added back pressure.
- Condensation at a flex connection doesn't require an air leak - if high-dew-point air reaches the inner/outer interface through a broken vapor barrier or crushed insulation, it sweats regardless of the air seal.

**Boost Your HVAC Ticket Size： Deploying Static Pressure Probes with MeasureQuick** (id: y4y1EtgEs9w)
- To localize high static, don't just take TESP - walk the probe along the ductwork: if static is still high past the filter, the restriction is downstream, not the filter; a high supply/low return split means a supply blockage (and vice versa).
- A big imbalance (e.g. 0.43 on the return, near-zero on the supply) means the return is choked, so little air is being pushed - could point to a restricted return or dirty evaporator coil (drill a careful hole above the coil, avoiding the drain pan, to isolate it).

**Building Science 101 for HVAC Contractors w⧸ Bill Spohn and Joe Medosch** (id: jMTxblZcTzE)
- Fixing dominant return leakage removes the positive pressure -> the house goes net negative from remaining supply leakage -> the path of least resistance becomes the water-heater flue -> water heater backdrafts -> CO alarms trip, so the whole distribution system must be addressed together.
- Run a blower door to depressurize the house, then move a pressure pan over receptacles, can lights, and ducts; a pressure reading means that point is connected to the outside, letting you locate and prioritize leakage (and prove whether or not you are the source of a failure).

**Delivered Capacity Basics - Kalos Meeting** (id: EJVRhznC_Ts)
- Check TESP, look up airflow on the fan chart at the speed tap, aim for CFM-per-ton, run ~15 minutes, then read supply and return psychrometers for delivered capacity.

**Discussing Ducts Types and Tips** (id: VDJotlJj3Mo)
- See a duct sweating -> check the coolest/most-likely points first: connections, compressed insulation, contact with trusses/other ducts, or a compromised outer vapor barrier -> confirm inner liner is sealed and outer vapor barrier is intact and uncompressed.

**Drain Traps & Static： Q&A with Bryan Orr** (id: zOpdAbQuBXM)
- Nuisance secondary-switch trips on retrofit jobs that won't get static below ~1 inch -> high negative pressure at the drain trap pulls water into the pan and overflows -> fabricate a deeper trap sized to the worst-case return static (a 1-inch trap is only enough for ~0.5 in w.c.).

**Duct DISASTER at an NBA Players Home** (id: 75Q15TVoazE)
- Uncomfortable upstairs -> thermal image vents/can lights/attic -> hot centers = duct gains, hot edges = infiltration -> confirm black flex radiant gains + missing insulation + open chase -> refrigerant low + poor readings + 20F delta T (too high for the readings) = airflow problem -> find boxed-in restricted flex plenum -> set subcool, recheck split, pull heat strips.

**Duct Design for Great Results w⧸ Ed Janowiak (ACCA)** (id: -KqmAQgUXY4)
- Manual D flow: external static (e.g., 0.75 at 1000 CFM, interpolated, medium speed) - component losses (wet coil 0.2, filter ~0.19-0.21, plus 0.03 each supply/return/damper) = available static (0.21) -> find total effective length of the longest circulation path (supply + return, e.g., 220 + 63 = 283 ft) -> friction rate = 0.21 x 100 / 283 = 0.074 -> size ducts on the duct slide, rounding up where return velocity would exceed 700 fpm.
- Grade the install after the fact: measure external static, filter drop, and coil drop against the design; if measured static is lower than designed, slow the fan; if higher, hunt the problem (usually flex compression).

**Fan Law 2 for Techs with Adam Mufich** (id: NzlsB9R6mbc)
- Reducing airflow from 1151 to 800 CFM drops a 0.579 filter pressure drop far more than linearly (via the squared ratio ~0.483x) because pressure follows the square of the airflow ratio.
- Installing an oversized variable-speed blower left maxed on high speed into an undersized (e.g., 2-ton) system sends static pressure 'off the rails'; setting the correct speed swings it back dramatically.
- Backing into TESP: solve new duct pressures for the new airflow, add the hand-selected coil pressure drop to the supply-duct pressure (before-coil) and the filter pressure drop to the return-duct pressure (after-filter), then sum absolute values to get TESP.

**Flow Hood： How to Properly Balance an HVAC System** (id: XeanFStDbyY)
- Overcooling a shared space skewed the hallway thermostat, so airflow to that shared space was intentionally reduced during the redesign.

**HVAC Belt Tension** (id: rNBt7LN-8ao)
- Belt squeals on motor start -> under-tensioned OR worn/greasy pulleys; inspect and clean pulleys and address the source before re-tensioning
- Belt keeps stretching and needing adjustment -> stop chasing it; replace the belt and check pulley condition

**HVAC Commissioning on Steroids w⧸ Jim Bergmann & Chris Hughes** (id: lvMjm3YwUY8)
- TrueFlow and MeasureQuick airflow disagree (~15%) -> return duct leakage between the filter and the coil, OR a misplaced probe -> follow up with a duct-tightness (duct blaster) test to locate it
- Return leakage screen in MeasureQuick -> suction pressure reads higher than calculated + temperature split drops (drawing hot attic air) -> deploy mixed-air probes on BOTH sides of the blower to catch a hot stream traveling down one side of the duct

**HVAC Condensate Drain Troubleshooting： Traps, Vents & Static Pressure** (id: LGgET3gRY20)
- Rust around the bottom of the air handler + a drip that appears only when running and drains out when off -> the trap is too shallow for the cabinet static; as the filter loads, rising static pulls air through the line and backs water up

**Heat Rise Airflow Calculation** (id: aRJH-wJZ1Gs)
- Run air handler with electric heat strips ~10 min until delta T is steady -> measure return 77F dry bulb and supply ~105F (delta T ~28) -> measure 243V and 19.5A on the heat strips -> watts = 243 x 19.5 = ~4739, x 3.413 = ~16,174 BTU/hr sensible -> 16,174 / (1.08 x 28) = ~535 CFM -> cross-check with rotating vane anemometer traverse of return grille gave ~550 CFM (close).

**How to Checkout Blower Settings Using a Manometer** (id: wdnaeZkstXI)
- To confirm airflow changes you do not need full total external static - measure one consistent point, establish a baseline, and watch it rise or fall with staging.

**How to Clean an Air Conditioner Blower Wheel (Fan Coil Blower Pull and Clean in 3D)** (id: YwFkhTqgazM)
- Dirt in blower cups -> impeded air movement -> ECM draws more current / PSC loses airflow -> reduced capacity and efficiency -> pull, wash, reassemble.

**How to Confidently Create a Duct Renovation Scope of Work w/ David Richardson** (id: 5eiv-0518mQ)
- Seven steps: 1) technician visual/overview of equipment -> 2) measure the system (four vital signs) -> 3) identify duct deficiencies/diagnose vs manufacturer targets -> 4) conduct customer interview -> 5) create scope of work (customer first, then team) -> 6) do the renovation -> 7) test out and verify before/after.
- Start with total external static (flags a restriction but not where) -> measure component pressure drops (filter, coil) and supply/return duct pressures -> the highest area of resistance vs where it ought to be is where you focus the renovation -> measure fan airflow (true flow) vs design.

**How to Measure Air Filter Static Pressure Drop** (id: zkPcIKKGwwc)
- High filter pressure drop -> is it dirty, or is airflow over the filter higher than its design? -> the static drop test points to the source of the airflow problem.

**How to Measure CFM w/ The Testo 420 Flow Hood** (id: kAjT-VujA6I)
- Put the system into high-stage cool (max airflow) and disconnect the condenser so air density isn't affected by temperature change -> measure each register with the hood -> hold/save readings into the Bluetooth app report.

**How to Measure Total External Static Pressure (TESP)** (id: 6uMqw69XkRw)
- High negative return static -> dirty filter, undersized return duct, or airflow set too high.
- High positive supply static -> undersized/kinked/improperly strapped supply duct, closed vents, or too much airflow overall.

**How to Predict Air Flow Issues in the Sales Process** (id: cGT6ZA3bcIg)
- Furnace-to-heat-pump retrofit example: 38,400 BTU output furnace at 652 CFM target -> a 3-ton heat pump needs 1,200 CFM (nearly double) -> by Fan Law 2 static would rise to ~1.7 in w.c., which the ECM will refuse to hit, so you get reduced flow and reduced capacity.
- TrueFlow static-pressure map breaks total external static into supply, return, evaporator coil drop, and filter drop to find the biggest restriction (most commonly undersized returns and undersized filters).

**How to use Static Pressure to Measure and Set Air Flow** (id: ddhQrxuIbUI)
- Static seesaw: on PSC/ECM constant-torque motors, if return static rises, airflow drops and supply static falls; fix a return problem and re-measure because supply static can then swing high (ECM constant-volume holds volume by changing RPM and drawing more amps).
- If a dirty internal component (blower wheel, secondary HX) restricts flow, BOTH sides go low (the seesaw breaks) because total air volume drops.
- Turbulence near fittings/corners falsely raises static; take readings 2-3 duct diameters downstream of a fitting (1-1.5 after turning vanes).

**Impact of Airflow on Refrigerant Measurements and Performance** (id: hCZEg_DGCf0)
- Symptoms: ~90 suction, ~8F superheat, delta-T ~25F, slightly low head on a TXV system => root problem is low indoor airflow, not the TXV or compressor.
- 40F evap + 10F superheat = 50F suction; drop evap to 35F and suction-line temp falls to ~45F.

**Is a House Really just a Big Duct System？ w⧸ Eric Kaiser** (id: YUjv96bbQOM)
- Closed door: +4.2 Pa in the room, house at -6 Pa, 3.3 Pa at another opening, so most of the room's air exits to outside (lower pressure-drop path) and the room over-conditions from increased dwell time.
- Depressurization: an exhaust fan pulling ~50 CFM must be replaced by ~50 CFM in (1 CFM out = 1 CFM in), so if there's no controlled makeup path the house pulls unconditioned infiltration air through the walls.

**Mini-Split Cleaning & Maintenance** (id: GRhAWA4tz1I)
- Carrier X-Power inverter won't restart after cleaning -> possible cause: spinning the permanent-magnet blower motor fast (e.g., with compressed air/nitrogen) generates a high-frequency electrical signal that back-feeds and can burn the board, even with power off.

**MiniSplit Air Conditioning Cleaning Practices** (id: DHWcSYPLLVw)
- Confirm ductless performance under load: use two psychrometers (return intake + outlet) and the manufacturer's CFM-at-high-speed chart in delta-H x CFM x 4.5 = BTU; when everything is clean the unit produces very close to the charted CFM (verified against vane anemometer on Mitsubishi/Carrier).

**Practical Training on Manometers** (id: QHHMC5K2moU)
- Suspect impacted/dirty coil you can't see -> pressure-drop across the coil (probe below coil / above filter and above coil in blower compartment) -> ~0.1 in on a clean wet coil vs >0.5 in (up to 1+ in) if impacted.
- Suspect restrictive filter -> measure across filter, then pull filter and compare the static difference.

**Pro Tips for Perfect Flex Duct to Duct Board Connections with Bert** (id: iygU_hFM9Os)
- Outer layer peeled back but no air leak -> the airtight seal was correctly made on the INNER layer -> but the exposed metal is at dew point, so attic humidity condenses and drips -> that's why the outer insulated seal still matters.

**Proper Use of Manometers for HVAC Technicians** (id: a9tX40eOJfw)
- High external static -> measure DROP across the coil (both probes negative under the blower, subtract): a big drop (e.g. ~1 inch vs ~0.1 normal) reveals an internally-impacted dirty coil you can't see; do the same across the filter to find restriction/high MERV.
- High return static + very low supply static -> a restriction on the return side (e.g. a media filter under the unit) is straining the blower and pulling cabinet/attic air in; even if total is under 0.5, it's a problem and airflow to the house is poor.

**Rack Refrigeration Cycle Part 11 - Evaporator Airflow** (id: RI1wD7nyGL4)
- Case sweating/condensation video: deck pan too low (gap) + fan blowing up caved-in ductwork = disturbed air curtain and sweating — trace deck pan and plenum sealing before blaming refrigeration.
- Reading CFM: the manufacturer spec (e.g. 140 CFM) is a lab number taken with a specific hood on an Alnor Jr on a spotless coil right after defrost — you'll always read LESS; reading 200 = someone changed blade/motor wrong; reading 40 = a problem; copy the neighboring identical case as the baseline (+/-10%).

**Residential AC System Installation** (id: gZQqjXhuMTI)
- Radiant barrier lowers all attic surface temperatures including the ductwork; if surfaces were near dew point you create a rainforest and everything sweats - watch for radiant barriers when ducts suddenly start sweating.
- Every CFM out of a house forces a CFM back in; range hoods/bath fans/attic ventilators that depressurize the space pull humid attic or outdoor air in through cracks - seal the attic to the house and make outdoor makeup air easy.

**Retrotec Duct Leakage & House Pressure Demo** (id: _oJOBSJW0kA)
- Demo readings: main body slightly negative (~ -0.5) with supply leakage; closed bedroom with no return path jumped to +3.2, confirming exfiltration in the bedroom and infiltration in the main body.

**Sealing Ducts From the Inside w⧸ Sean Harris** (id: bj962pMF1-Q)
- Common leak locations: connections, especially where flex duct meets a starting collar with no fluid-applied sealant (the collar ovalizes under the panduit strap); the aerosol fog reveals leaks in the attic.

**Short 10 - Air Has Weight and Takes up Space** (id: tXFHPWkUAOA)
- Same undercharged system freezes more in humid low-altitude Florida; in Colorado a system freezes more from low airflow because you must exceed 400 CFM/ton to move the same mass ('stuff in the box') in thin air.
- At 5000 ft use a ~0.83 correction factor - the blower moves the same CFM/vane reading but fewer molecules per cubic foot.

**Short 16 - Air Velocity is Useful** (id: Sz6A9-ihX-g)
- Compare register velocities across a home; an outlier high velocity on a room that's too hot in winter/cold in summer flags a room being over-fed that you can throttle with a balancing damper.
- High filter-grille face velocity (above ~400 FPM) causes noise and the center-dirty-spot pattern - proof of undersized grille/duct.

**Short 2 - Delta T** (id: c1LCnU3lO-M)
- Higher-than-target delta T -> suspect low airflow first (dirty filter, dirty coil, or setup below 400 CFM/ton) or abnormally dry air, or intentional dehumidification mode ramping the blower down.
- Lower-than-target delta T -> suspect high airflow or reduced capacity (undercharge, overcharge, weak compressor, TXV issue) or high return humidity.

**Short 4 - Blower Taps (Audio Only)** (id: 2kgNFetuWKs)
- Higher airflow per BTU -> more sensible, less latent (good for dry/high-altitude climates like Colorado); lower airflow per BTU -> more latent, less sensible — but latent capacity also depends on actual moisture in the return air.
- Match the Manual J design-day sensible/latent requirement to set airflow; when equipment has variable-speed controls for humidity events you gain further control.

**Static Pressure Fundamentals** (id: o6OVAUJXeuU)
- 5-ton rated 0.5 in wc -> measure return -0.31 and supply +0.19 = 0.5 (healthy) -> but pinched/restrictive ducts give e.g. -0.78 return and high supply = ~1.4 total -> 'hypertension' = big problem both sides
- High total static -> inspect attic: is it sealed/strapped, where's the first takeoff, bad hangers, crushed duct -> talk to homeowner about recent plumber/electrician work

**Static Pressure and Manometer Basics** (id: Jp2pZydCp28)
- Gas furnace -> evaporator coil is a separate box the manufacturer didn't rate -> measure total external static BELOW the coil (across only what's in the furnace box), and measure the coil's pressure drop separately
- ECM/variable-speed blower on higher-than-rated static -> spins faster to hold airflow -> higher amperage, higher operating cost, shortened motor life

**Symptoms of Low Evaporator Airflow** (id: x4_FkNNGzFo)
- Low evaporator airflow -> colder evaporator coil -> low evaporator temp -> low suction pressure + low suction temp (low superheat on fixed orifice; normal-to-low on TXV) -> high delta T; if below 32 F long enough -> icing creeping down the suction line
- Iced-up compressor -> ice didn't start there, it started at the evaporator coil (below 32 F) and crept back down the suction line

**System Airflow Measurement w/ TEC TrueFlow** (id: USMxJexJvbo)
- Low indoor airflow -> colder evaporator coil -> lower evaporator pressure -> lighter/less-dense return gas -> compressor moves less refrigerant per stroke -> lower efficiency and capacity
- TrueFlow workflow: measure return static, supply static (with filter), then swap filter for the grid and measure -> app applies correction factor -> reports actual CFM with the filter installed + diagnostic screen flags low flow / high supply pressure

**Testing Home Pressure Imbalance w⧸ Genry Garcia (Spanish)** (id: 27AoOAVSaM0)
- Predominantly negative house = loss on the supply side (air not returning to equipment); predominantly positive house = loss on the return side. Neither is better; more important not to have the leak at all.

**Testing out a High Performance HVAC Installation** (id: DhXYd2Um1uE)
- Duct leakage tested with a duct blaster on Ring 4 (measures leakage under 10 CFM) at 25 Pascals; balancing airflow room-by-room using a powered flow hood, then re-verifying total flow after each adjustment.

**The Duct We Tend to Forget w⧸ Joe Medosch** (id: DpX20OkmgoU)
- Blower door depressurizes the house to 50 Pa, measures CFM50 leaving; divide by house volume and multiply by 60 for air changes per hour; measure the outside of the house (subtract garage) for volume using a laser measure.
- Sealing a leaky return can make supply leakage now dominant, putting the house more negative and increasing the risk of backdrafting a natural-draft water heater.

**The Flaw With Zonal Pressure Diagnosis** (id: 7bXPNva82qc)
- A 25 Pa ZPD reading only means the collective room-to-inside opening equals the collective room-to-outside opening — it says nothing about actual hole size or CFM50.

**The Great Heat Pump Revolt of 2026 and How To Avoid It with Steve Rogers, Russ King and Chris Hughes** (id: OioG8T_zwaA)
- Duct leakage to outside is a double whammy: leaking a quarter of a 4-ton's capacity into the attic delivers only 3 tons AND the make-up air pulled from outside raises the load — shrinking the heat pump's margin so it can't keep up and runs expensive resistance heat.
- Use the manufacturer balance point worksheet: plot capacity vs outdoor temp for the chosen tonnage, mark the design-load point; if it's above the capacity line the system needs aux heat — draw the load line through 60°F/zero to find the thermal balance point (e.g., 39°F).

**The Impact of Static Pressure on Fan and Blower Motors w⧸ Rick Streacker** (id: 1X9cXMrWc1o)
- Low amps on a blower motor indicate too little load (too much restriction/static), causing inefficient operation, higher winding temperature, and higher capacitor volts — so both high AND low amps are problems.

**Total Furnace Airflow and Precision Manometer w⧸ TEC TrueFlow** (id: pYA2xv0cukA)
- Throw a tube under a closed bedroom door and read Pascals referenced to the room with the return; a highly pressurized room (e.g., ~22 Pa) means air goes in but can't get back to the return, starving the return or forcing outdoor infiltration and pushing conditioned air out through leaks.
- On the demo 3-ton gas furnace: total external static was good but airflow was borderline-low; the return-duct measurements showed the return (specifically the filter) as the restriction, and swapping in a lower-restriction filter grid changed the result (supply plenum pegged, static too high) confirming undersized duct/blockage.

**Understanding Airflow: David Bowie, a Used Car Lot, and a 40 cent Tool with Alex Meaney** (id: uIXfiuY3i9U)
- Airflow is a traffic jam, not a race: the duct is already full of air, so friction at a fitting is felt almost instantly all the way back, not encountered like a car reaching a corner.
- Scale-on-a-crate analogy: push a crate on ice (low friction) and the scale barely moves because energy goes into motion; push it on gravel (high friction) and the scale number spikes - the same energy split between velocity and static in a duct.
- Resistance adds in series (not parallel) like an electrical circuit, so a longer airflow path (corner unit location) has more fittings and more accumulated friction, requiring larger ducts.

**Volume Flow Rate vs Mass Flow Rate w⧸ Jim Bergmann** (id: FMSl9qexPRw)
- Q = mass x specific heat x delta T: 12,000 BTU / (30 lb-min x 0.24) = 27.5F if all energy were sensible; x 0.75 typical sensible split ≈ the magic 20-degree delta T
- The density of air = 1 / specific volume; find specific volume on the psychrometric chart (e.g. 13.33 ft3/lb at 68F, 0% RH) and take the inverse to get lb/ft3

**What Air Filter is The Best？** (id: 4R0V6a6Uz3c)
- To answer 'best filter': know where the current filter is, measure pressure drop across the current (clean) filter, measure total external static, compare to design TESP and the fan curve to know headroom
- Return velocity should be ~300-500 fpm; a whistling/noisy return is a practical tech signal of too-high velocity

**What Should the Air Delta T be？ (Air Temperature Split)** (id: _pD-rRCNv8k)
- All else equal: higher capacity -> higher delta T; higher airflow -> lower delta T; higher return humidity -> lower delta T. Know all three to make sense of a reading
- System capacity drops as indoor temp drops and/or outdoor temp rises (higher compression ratio, lower mass flow), so a 115F Phoenix day yields less capacity than 95F

**What is Proper System Airflow** (id: sjZR0bTL1Ig)
- Selection: total gain vs capacity, sensible gain vs sensible capacity, latent gain vs latent capacity; if short on sensible, apply HALF of excess latent capacity to sensible per Manual S guidance
- Interpolate capacity between published design temps (add the 85F and 95F values, divide by two) when your design temp isn't tabulated
- Measure delivered latent with a red solo cup: fill it in 15 minutes = ~4000 BTU (a pint is a pound is ~1000 BTU)

**When a Variable Blower Runs Too Slow** (id: M99zS-5yeSs)
- Blower running slow: verify 24V between C and Y (or Y2), 24V between C and G, and 24V between C and DH; check all pin settings before condemning the motor. Only if it oscillates for an extended period do you go to ECM motor diagnosis.

## Specific numbers Bryan cites

| Metric | Value | Context | Bryan cited a source | Episode id |
|---|---|---|---|---|
| electric bill increase | $100 higher this month than normal | homeowner complaint that opened the call | no | Rl2Ej7fdy1U |
| blower door test pressure | 50 pascals = ~0.2 inch (1/5 inch) water column | standard depressurization for CFM50 | yes | IlrHazYv84M |
| equipment cost | entry blower door ~$2000-3000; duct-tightness tester ~$2500 | getting into diagnostics | yes | IlrHazYv84M |
| code mandate | 2009 IECC / ARRA 2009: 90% compliance by 2017 | why blower-door testing is spreading | yes | IlrHazYv84M |
| HRV prevalence | <5% of US houses (~1%) | most houses lack heat-recovery ventilation | no | IlrHazYv84M |
| friction-rate wedge | 0.06 to 0.18 (ACCA wedge), midpoint ~0.12 rounded to 0.1 | why 0.1 is a myth | yes | X2Y1KNFoxug |
| duct velocities | trunk 700-900 fpm; branch 400-600 fpm | velocity difference gives control | yes | X2Y1KNFoxug |
| secondary-air entrainment | primary air moves 10-20x its volume; return effective reach ~30-36 inches | why supply registers, not returns, mix room air | yes | X2Y1KNFoxug |
| flex compression limit | 4% max (ADC); a 25ft flex in a 20ft span = 25% compression | flex handling ruins airflow | yes | X2Y1KNFoxug |
| coil pressure drop | ~0.3+ (W/A coils start ~0.45) | why you're never in the 0.5 column with a coil | yes | X2Y1KNFoxug |
| specific heat of air | 0.24 BTU/lb-F (constant ~ -58 to 104F) | why humidity barely affects heat capacity | yes | 7lEhrcbaeGM |
| specific heat comparison | water 1.0, ice ~0.5, water vapor/steam ~0.5 | water vapor is a small fraction of air's heat effect | yes | 7lEhrcbaeGM |
| air density vs humidity | ~0.075 to 0.073 lb/ft3 across 0-100% RH (about an 11F equivalent) | humidity's small density effect vs temperature | yes | 7lEhrcbaeGM |
| residential duct velocity | below ~700 fpm in a well-designed system | why pitot tubes are impractical residentially | yes | 7lEhrcbaeGM |
| CPS micro-hood capacity limit | ~150 CFM | cheap supply-register airflow measurement option | no | 7lEhrcbaeGM |
| standard airflow per ton | 400 CFM/ton = 30 lb/min/ton (0.075 lb/ft3) | mass-flow basis of airflow | yes | ryTchnFMem0 |
| standard air definition | 68F, 0% RH, sea level; 13.33 ft3/lb | basis of standard air formulas | yes | ryTchnFMem0 |
| systems with incorrect airflow | 7 of 10 | multiple studies (California, Energy Star), mostly poor duct design | yes | ryTchnFMem0 |
| ECM constant-CFM range | near-constant CFM up to ~0.9 inch total external static | why static is more usable with ECM/X13 | yes | ryTchnFMem0 |
| added-filter static allowance | ~0.02 to 0.1 inch w.c. | normalizing static for an aftermarket filter | yes | ryTchnFMem0 |
| sensible/standard-air capacity formula | 4.5 x CFM x change in enthalpy | standard-air equation carrying airflow error straight through | yes | ryTchnFMem0 |
| before | ~115 psi suction, ~6 F superheat | coil shifted right | no | PjWScoD3NH4 |
| after | 155 psi suction, 15 F superheat, 20 F split | coil shifted left, no refrigerant added | no | PjWScoD3NH4 |
| two-port duct readings | 0.12 in wc (upper) vs 0.08 differential between ports | turbulence in a sharp-turn plenum | no | wmJ0QBKEbB8 |
| 50 ft of 6-inch flex at ~100 CFM | 1.15 in static coiled -> 0.94 in / 103 CFM straightened | flex must be pulled tight | no | wmJ0QBKEbB8 |
| appearance vs performance | ~20:1 people judge on appearance | argument for testing | no | wmJ0QBKEbB8 |
| return velocity limit | 700 fpm | duct velocity guidance | no | wmJ0QBKEbB8 |
| standard air conditions (SCFM) | 68.3F, 0% RH, 0.075 lb per cubic foot | reference for standard air | yes | GgvSnm_gqt8 |
| atomic masses | N2=28, O2=32, H2O=18 units | why humid air is lighter | yes | GgvSnm_gqt8 |
| sea level pressure | 14.7 psi | air weighs less/less dense at elevation | yes | GgvSnm_gqt8 |
| humid-climate ACFM example | ~405-410 ACFM to hit the same mass flow as 400 SCFM | lighter humid air | no | GgvSnm_gqt8 |
| particles in a cubic meter of air | ~1 billion, 99% under 1 micron, average ~0.4 micron | why 0.4 micron capture matters | yes | s4EGvkZPqgo |
| MERV 8 pleat capture at 0.4 micron | ~5-15% | vs MERV 14 at ~60-75% | yes | s4EGvkZPqgo |
| high-efficiency box filter media | 24x24x12 = 200 sq ft of media, lasts 2-4 years, lower initial drop than a MERV 8 pleat | surface area value | yes | s4EGvkZPqgo |
| final filter change-out pressure drop | MERV 8 / 2-inch pleats ~0.9 in.; final filters ~1.5 in. | commercial change-out points (not residential) | yes | s4EGvkZPqgo |
| energy savings of a better filter | ~$13-15/year per filter hole | TCO argument; HVAC uses 40-50% of building electricity | yes | s4EGvkZPqgo |
| straight duct needed for accurate reading | 3-5 feet of straight duct before any change | laminar airflow for accurate static | no | wWN2IKAqpy4 |
| target startup static (PSC/X13) | ~0.3 total (max 0.5); balance ~0.1 return / ~0.2 supply | leaves room for dirt | no | wWN2IKAqpy4 |
| constant-CFM target static | ~0.35-0.5 total, pulling ~half rated amps | efficient with room for dirt | no | wWN2IKAqpy4 |
| some low-cost air handlers rated static | as low as 0.3 in. | low-horsepower blower motors | yes | wWN2IKAqpy4 |
| variable-speed static capability | 0.8 to 1.0 in. static (manufacturer dependent) | vs 0.5 for PSC/X13 | yes | wWN2IKAqpy4 |
| room-to-house pressure limit | 3 Pascals max (prefer less) | zonal pressure imbalance rule of thumb | no | AWecM1MfuEE |
| master bedroom measured | 7 Pascals | pressurized room example | yes | AWecM1MfuEE |
| ECM airflow taper | airflow tapers off around 0.8 in. static | modern ECM/X13 self-limit to protect the blower | yes | AWecM1MfuEE |
| rated max static | commonly 0.5 in. (old ones as low as 0.2) | keep below manufacturer max | yes | eHzYalJXE88 |
| Fan Law 2 example | 800 -> 1200 CFM (1.5x) squared = 2.25x static; ~0.11 predicted supply | square-effect calculation | yes | eHzYalJXE88 |
| coil pressure drops offered | a smaller coil ~0.33 vs a bigger BC-cabinet coil ~0.28 | bigger coil = lower drop, like a filter | yes | eHzYalJXE88 |
| humid-market airflow target | ~350 (down to 325) CFM/ton | better dehumidification vs sweating trade-off | no | FFYvSwCIYho |
| modern rated static | ~0.5 in. (SEER2), some older 0.3 | keep total external static within range | yes | FFYvSwCIYho |
| flex duct strapping | every 4 ft on center, straps 1.5 in wide or wider | more surface area prevents collapse/sag | yes | 3m1eRBXDM5I |
| flex-specific tape | UL 181 FX (FX = flex) | tape designed for flex duct | yes | 3m1eRBXDM5I |
| test house | 2750 sq ft (guessed ~2700) | the house under test | no | i4YuqUPmwHs |
| test vs natural pressure | ACH50 = 50 pascals (~20 mph wind); natural ~4 pascals | benchmark vs real-world infiltration | no | i4YuqUPmwHs |
| normal TESP | ~0.5 in w.c. upper limit (data tags rate 0.25-0.5) | above ~0.5 the blower is straining; equipment matrices are built on <=0.5 | yes | y4y1EtgEs9w |
| weight/volume of air | a pound of air occupies ~13 cubic feet | physics basis for airflow calcs (from measureQuick training) | yes | y4y1EtgEs9w |
| homes with HVAC issues | ~7 of 10 (Houston-area survey) | often overcharge and airflow problems | yes | y4y1EtgEs9w |
| case-study sales | $288k/$2,800 avg -> $465k/$4,600 avg | NY tech before/after measureQuick, June-Aug | yes | y4y1EtgEs9w |
| Cooling load from one small hole | ~1/4 ton | Load added by a single ~half-inch wire penetration into a pan return, calculated by Allison Bailes | yes | jMTxblZcTzE |
| Moisture through a 1-inch hole in drywall | ~30 quarts (28 liters) over a heating season | Diffusion plus a single 1-inch hole in a mixed climate; more in high-moisture climates | yes | jMTxblZcTzE |
| Average house leakage area | ~3 square feet | Approximate total leakage area of an average house | no | jMTxblZcTzE |
| Dryer airflow | ~200 cfm | Air a clothes dryer exhausts (and pulls back into the house) while running | yes | jMTxblZcTzE |
| Range hood airflow | up to ~1200 cfm | Large/downdraft range hoods; bath fans ~50-150 cfm | yes | jMTxblZcTzE |
| ACH50 code progression | IECC 2009 = 7, many states = 5, 2018 IECC = 3, Passive House = 0.6 | Air changes per hour at 50 pascals blower-door test pressure; tightening over time | yes | jMTxblZcTzE |
| Bill Spohn's house | 1 ACH50; 4400 sq ft on a 2-ton air-source heat pump | Example of a tight house with a low heating/cooling load | yes | jMTxblZcTzE |
| Florida ventilation trigger | 3 ACH | FRACA rule: below ~3 air changes per hour an exhaust/whole-house ventilation fan may be required | yes | jMTxblZcTzE |
| Fit allowance | raw-to-raw + 2 inches | Because the duct slides into the drive cleats on each side | no | y_aTNtv_2bM |
| Drive-cleat notch | between 1/2 and 3/4 inch | Notch depth so the snap-lock seats without over-cutting | no | y_aTNtv_2bM |
| Runtime before reading | ~15 minutes | Let the system run before taking psychrometer readings | yes | EJVRhznC_Ts |
| Nominal vs actual | 3-ton may deliver ~34.5-35k BTU nominal (not always 36k) | Varies with equipment match and indoor/outdoor conditions | yes | EJVRhznC_Ts |
| Callback example | ~25% low, fixed by dialing in the charge | AOR job on a long line-set application | yes | EJVRhznC_Ts |
| Trap depth rule of thumb | 1-inch trap for ~0.5 in w.c.; double the inches of return static | Negative-pressure air-handling systems; already has a built-in safety factor | no | zOpdAbQuBXM |
| Practical residential maximum trap | ~2-inch trap | For up to ~1 inch return static; more than 1 inch of return water column would mean massive system problems | no | zOpdAbQuBXM |
| Filter pressure drop at rated airflow | ~0.29 in w.c. at ~1050 CFM (3-ton, Florida rating) | A clean filter already restricts airflow | yes | 75Q15TVoazE |
| System test static | 0.2 in w.c. | Rated with no ductwork and only the filter you're already behind | yes | 75Q15TVoazE |
| Measured delta T | ~20F | Higher than the refrigerant readings justify, indicating low airflow | yes | 75Q15TVoazE |
| Filter face velocity limit | 300 fpm (filter grill); 500 fpm stamped grill; 500 fpm across return grill | Manual D velocity guidance to avoid noise | yes | -KqmAQgUXY4 |
| Duct velocity limits | return 700 fpm max; supply 700-900 fpm; branch runs 600-700 fpm | Run max in unconditioned space, conservative in conditioned space | yes | -KqmAQgUXY4 |
| Filter surface rule | two square inches per CFM (~200 sq in/ton, ~150 fpm) | Quality rule of thumb for filter grills; ASHRAE 52.2 lets manufacturers publish drop at low velocities (118-295 fpm) you rarely achieve | yes | -KqmAQgUXY4 |
| Worked friction rate | 0.074 (ASP 0.21, TEL 283 ft) | Calculated, not assumed; round to 0.07 or 0.08 | yes | -KqmAQgUXY4 |
| NCI measured average airflow | 298 CFM/ton across 16,000 data points | Industry reality of under-delivered airflow | yes | -KqmAQgUXY4 |
| Side-piece measurement allowance | ~1/4 to 1/8 inch over on the inside; sides cut 1/2 to 3/4 inch back for the lip | For a tight fit accounting for the locking lip | yes | DgxhPFfPlEs |
| Plenum face setback | 2 inches minimum, 3-4 inches preferred | So the air handler door doesn't hit the plenum | yes | DgxhPFfPlEs |
| Flap length | ~3 inches | Sealing flaps left on the pieces | yes | DgxhPFfPlEs |
| Fan Law 2 example filter pressure drop | 0.579 in wc at 1151 CFM | real true-flow-grid customer data; a high filter pressure drop (most systems rated ~0.5 in total) | yes | NzlsB9R6mbc |
| airflow vs static swing | +16% CFM (860->1000) = +33% static (0.15->0.20) | illustrates static pressure moving farther than airflow due to the square law | yes | NzlsB9R6mbc |
| good vs bad coil pressure drop | 0.20 vs 0.379 in wc at 1000 CFM | hand-selected low-drop AMANA/Goodman coil vs the cheaper high-drop coil the supply house gives you | yes | NzlsB9R6mbc |
| good vs bad filter pressure drop | 0.04 vs 0.22 in wc at 1000 CFM | hand-selected large Aprilaire media filter vs an off-the-shelf stock filter | yes | NzlsB9R6mbc |
| resulting good TESP | 0.64 in wc | gas furnace with coil, correct airflow, hand-selected low-drop components (rated ~0.5) | yes | NzlsB9R6mbc |
| typical modern ECM/variable-speed static | ~1 inch wc | common when people aren't paying attention to component selection | no | NzlsB9R6mbc |
| damper control range | most control near closed; opened ~15% for target | most of your control happens when it's nearly closed | no | XeanFStDbyY |
| Leak per screw hole | ~1 CFM per 1/4-in hole at 0.1 in WC | Via 1.07 x area x sqrt(deltaP) (Steve Rogers) | yes | lvMjm3YwUY8 |
| Furnace door gasket crack | ~40 CFM | Leak right next to the blower (highest resistance) | no | lvMjm3YwUY8 |
| Return leakage impact | 88 CFM -> ~12% capacity loss | Attic 120 F/35% RH into 74 F/60% return; mixed air 73->77 F | no | lvMjm3YwUY8 |
| Prior-year supply leak example | 384 CFM -> ~80% load increase | Steve/Bill's supply-leakage class | yes | lvMjm3YwUY8 |
| Delivered capacity example | 30,000 BTU losing 6,000 -> 3 ton acts like 2.5 ton | Equipment vs delivered capacity | no | lvMjm3YwUY8 |
| Tool agreement threshold | ~15% TrueFlow vs MeasureQuick | Triggers a duct-leakage alarm; leakage normalized to 25 Pascals | no | lvMjm3YwUY8 |
| Example repair price / healthy business | $835 return-duct repair; ~$2M healthy business example | Selling the value / business benchmarks | no | lvMjm3YwUY8 |
| Static that empties a shallow trap | ~2.5 in | Can suck the water out of a pre-made trap | no | LGgET3gRY20 |
| Trap depth for large commercial units | up to ~4 in (5-10 ton) | Higher blower horsepower/static needs a deeper trap | no | LGgET3gRY20 |
| airflow constant | 1.08 | from 0.075 lb/ft3 x 60 min/hr x 0.24 BTU/lb/F | yes | aRJH-wJZ1Gs |
| air density at sea level | 0.075 lb/ft3 | component of the 1.08 constant | yes | aRJH-wJZ1Gs |
| specific heat of dry air | 0.24 BTU/lb/F | heat to raise one pound of air one degree F at sea level | yes | aRJH-wJZ1Gs |
| BTU per watt | 3.413 | converting electric watts to BTU/hr sensible | yes | aRJH-wJZ1Gs |
| measured voltage / amperage | 243 V, 19.5 A | load side of contactor / on the heat strips on a Goodman air handler | yes | aRJH-wJZ1Gs |
| delta T | 28 F (77 return, 105 supply) | measured across return and supply | yes | aRJH-wJZ1Gs |
| calculated airflow | ~535 CFM | heat-rise result | yes | aRJH-wJZ1Gs |
| anemometer airflow | ~550 CFM | rotating vane traverse of return grille (15.5 x 20 in) | yes | aRJH-wJZ1Gs |
| filters used | four 20x20x2 MERV 13 filters | vs a single filter on a standard 20x20 box fan | yes | Y7eL2OAnqc8 |
| cardboard base cut size | 21.5 x 21.5 in | platform for a ~22x22 box | yes | Y7eL2OAnqc8 |
| Phillips head screws behind clips | 3 | on this Mitsubishi model | yes | 2VvoER81-co |
| plenum height | 32.5 in (plus a 3/8 in flange) | measured for the new coil case | yes | hgFafh_AFLU |
| box dimensions | 20 x 21.5 in | coil width ~20, depth ~21.25 | yes | hgFafh_AFLU |
| lineset slack | ~5 ft | enough to bend and drop the coil without disconnecting | yes | hgFafh_AFLU |
| manometer wireless range | ~350 feet | Field Piece JobLink JL3KM-2 kit | yes | wdnaeZkstXI |
| stage 5 reading | 1241 CFM, 0.54 in wc total static | Carrier Infinity system in 5th stage | no | wdnaeZkstXI |
| filter pressure drop (Delta P) | 0.17 in wc | difference across the air filter | no | wdnaeZkstXI |
| pressure above filter at full speed | -0.29 in wc | single-point baseline that dropped when staging down to stage 4 | no | wdnaeZkstXI |
| average delivered system performance | 57% | NCI field testing over ~17-18 years | yes | 5eiv-0518mQ |
| code-approved system performance | ~63% (only 6% better than the worst allowed) | code minimum | yes | 5eiv-0518mQ |
| performance achievable with verified renovation | up to 88% | with measurement and verification | yes | 5eiv-0518mQ |
| example restriction | total external 0.9 in wc while fan only moves rated air at 0.5 | indicator of a problem to dig deeper | no | 5eiv-0518mQ |
| example filter restriction | 170% of its rating | bad filter or undersized filter (visual inspection decides) | no | 5eiv-0518mQ |
| example duct restriction | return duct at 200% of where it should be | more restrictive than supply in that example | no | 5eiv-0518mQ |
| load fraction through duct work | up to 40% of the building load | depending on duct location | yes | 5eiv-0518mQ |
| common wrong assumption | 6-inch duct delivers 100 CFM | competitors' airflow misconception used against them | no | 5eiv-0518mQ |
| plenum dimensions | 12.5 x 18.75 x 32 inches high | for a 14-inch cabinet upflow furnace | no | EgFAL_z7P2o |
| tab sizes | 3/8-inch triangles on the bottom (for screws), 1-inch triangles on top (for slip and end cap) | forming the box | no | EgFAL_z7P2o |
| example duct / cut length | 24x8 duct -> 24+8+24+8 + 2 extra = 66 inches of canvas | measuring the wrap | no | gE3Dnn0u3kA |
| example measurements | S-locks cut at 19.5 in; transition piece 17 x 22.5 in | furnace-to-coil transition in this demo | no | rO4yqiWjOtU |
| folding bar folds | 1-inch fold on one side, 1/2-inch on the other | use the 1-inch fold | no | rO4yqiWjOtU |
| components / cost | 20x24x4 MERV 13 filter + 20x20 box fan, ~$50 total (under $100) | box-fan filter build | yes | gToHQvORNHs |
| cleaner dilution | 20 to 1 (water to cleaner) | EvapPlus enzyme cleaner used around the house per John Pastorello | yes | gToHQvORNHs |
| filter pressure drop | 0.13 in wc | good drop for a MERV 11 high-efficiency filter | no | zkPcIKKGwwc |
| weight | just over 6 pounds | industry-leading light flow hood | yes | kAjT-VujA6I |
| accurate range | ~50 CFM up to over 2000 CFM | below ~50 CFM use a vane anemometer | yes | kAjT-VujA6I |
| example register readings | ~98-117 CFM (varied ~103-117 by orientation); commercial supply ~179-182 CFM | residential + commercial demos | no | kAjT-VujA6I |
| minimum fan efficacy (California requirement) | 0.58 (i.e. 1000 CFM for 580 watts) | California requires blower fan efficacy of at least 0.58 | yes | 8ANRxjC6xs8 |
| measured power factor on ECM | 0.46 | demonstration ECM blower, 1.13 amps at 213V gave ~110-111 watts because of the low power factor | yes | 8ANRxjC6xs8 |
| measured airflow / wattage in demo | ~700 CFM at 111 watts | 208V building; system learns ~0.3 external static | yes | 8ANRxjC6xs8 |
| example total external static | 0.15 return + 0.15 supply = 0.30 in w.c. | illustration of adding the two port readings | no | 6uMqw69XkRw |
| typical equipment design external static | 0.8 to 0.2 depending on equipment; SEER2 equipment 0.5+; many fan coils rated down to 0.2 | design ranges | yes | 6uMqw69XkRw |
| measured TESP vs rating | 0.34 in w.c. measured vs 0.5 rated on data tag | within specification | yes | E3-lpHKCjiQ |
| Fan Law 2 relationship | double the airflow -> quadruple the static; +50% airflow -> ~2.25x static | Bernoulli/Fan Law 2 | yes | cGT6ZA3bcIg |
| heat pump airflow requirement | ~400 CFM per ton (1,200 CFM for 3 tons) | retrofit example | yes | cGT6ZA3bcIg |
| example furnace | Goodman GCVC800603, 48,000 input, 80% AFUE = 38,400 output, 35-65 temp rise, 652 CFM at 0.5 external static | worked heat-pump-retrofit example | yes | cGT6ZA3bcIg |
| largest heat pump vs furnaces | biggest heat pump ~60k output; furnaces run 40k-120k | retrofit must use the two smallest furnace-equivalent sizes | yes | cGT6ZA3bcIg |
| manometer resolution | minimum 0.01 in w.c. | required to measure static pressure accurately | yes | ddhQrxuIbUI |
| ECM constant-volume static target | less than 70% of max external static rating | e.g. under 0.7 on a 1.0-rated unit | yes | ddhQrxuIbUI |
| filter design target | ~0.1 in w.c. or less; face velocity ~300 fpm max | focus on pressure drop | yes | ddhQrxuIbUI |
| louvered door static | ~0.18-0.19 in w.c. across a louvered door (total external 0.844) | Jamie Garcia's South Florida photos - think outside the duct | yes | ddhQrxuIbUI |
| AHRI design conditions | 95F outdoor, 80F indoor dry bulb, 67F wet bulb | where equipment capacity is rated | yes | ddhQrxuIbUI |
| Suction-line temp rule | below ~50F suggests low airflow | Normal indoor/outdoor conditions | no | hCZEg_DGCf0 |
| Target airflow (Florida latent) | ~350 CFM/ton | Baseline vs 400 CFM/ton | no | hCZEg_DGCf0 |
| Restricted airflow | ~249 CFM/ton, TESP >1 in.wc | After plugging the return | yes | hCZEg_DGCf0 |
| Bend allowance | lose 3/8 in. on the bend | Sizing the opening | no | md1OyUs-tcA |
| Opening vs piece | ~2 in. smaller than the duct width | Marking the cut | no | md1OyUs-tcA |
| share of comfort that is radiant | ~60% | why supply air should condition surfaces, not people | no | YUjv96bbQOM |
| pressure unit conversion | 2.5 pascals = 1/100 inch water column | house pressures are a much finer scale | no | YUjv96bbQOM |
| closed-room pressures | +4.2 Pa room, house -6 Pa, 3.3 Pa at another opening (~0.015 in WC) | over-conditioned room diagnosis | no | YUjv96bbQOM |
| cheap gauge drift | 0.2 to 0.4 inch (up to 1 inch) | why autozeroing gauges matter | no | YUjv96bbQOM |
| louver door resistance | up to 24 inches of water column | high-resistance return path found by Jenry Garcia | yes | YUjv96bbQOM |
| room color perceived temperature | up to 7 degrees | warm vs cool colors affect mean radiant/perceived temperature | no | YUjv96bbQOM |
| Coanda effect | adds ~25% to register throw | register selection/throw | no | YUjv96bbQOM |
| comfortable air velocity | 50 to 100 pleasant, under 50 unnoticed | don't blow air on humans | no | YUjv96bbQOM |
| example static pressures | 0.12 supply, 0.2 return (higher due to remote filter grille) | circulating air with zero net house pressure | no | YUjv96bbQOM |
| example duct leakage | 50 CFM | illustrating 1 CFM out = 1 CFM in | no | YUjv96bbQOM |
| Target residential supply outlet velocity | 300-700 ft/min | general guideline | no | WTEoz7P3QDM |
| Measured example | 106 CFM average, 193 ft/min average velocity | 12x12 vent at 55% free area, intentionally low velocity | yes | WTEoz7P3QDM |
| House envelope test pressure | -25 Pascals reference to outside | blower door setting | yes | FtPWajjm1Q0 |
| Example total duct leakage | ~60 CFM total vs leakage-to-outside measured separately | this house | yes | FtPWajjm1Q0 |
| Hypothetical example | 200 CFM total leakage but only 50 CFM to outside | illustrating why to test leakage to outside | no | FtPWajjm1Q0 |
| Example measurement | 755 CFM, 388 ft/min average velocity | 20x14 inside dimension duct, 5 equidistant ports | yes | 29sNEDcQJTc |
| Ductless discharge air temp when working | 40-50 F (fairly consistent at high stage) | performance check | yes | DHWcSYPLLVw |
| Suction line temp threshold | should drop below 55 F | field test on suction line | yes | DHWcSYPLLVw |
| Superheat at high stage | ~0-5 degrees typical | ductless at full cooling | no | DHWcSYPLLVw |
| Capacity formula | delta-H x CFM x 4.5 = operating BTU | under-load capacity test | yes | DHWcSYPLLVw |
| design max total external static | 0.5 in w.c. | typical system design maximum | yes | QHHMC5K2moU |
| static that burns motors | above ~0.8 up to ~1.0 in w.c. | cuts CFM, raises amps, pulls warm air into crevices | yes | QHHMC5K2moU |
| clean-coil pressure drop | about 0.1 in (less than 0.1 dry) | wet clean coil; ~0.1 measured in demo (0.31 below / 0.43 above) | yes | QHHMC5K2moU |
| impacted-coil pressure drop | over 0.5 in, up to 1+ in | clogged/algae-impacted coil | yes | QHHMC5K2moU |
| flex strapping interval | every ~4 feet (there is a code sag limit) | keep flex straight to avoid airflow loss from sag | yes | iygU_hFM9Os |
| inner rings behind the strap | minimum 2, 3 is better | pull multiple inner layers over the lip before Panduit-strapping | no | iygU_hFM9Os |
| pressure unit conversion | 1 PSI = 27.71 inches of water column | why inches of water column is the fine-scale manometer unit | yes | a9tX40eOJfw |
| design external static example | 0.5 in WC | the static the equipment was rated/tested at; efficiency is based on it | no | a9tX40eOJfw |
| target airflow | 350 CFM per ton (Florida) | set fan speed from the factory blower chart to hit this | no | a9tX40eOJfw |
| coil pressure drop | ~0.1 in WC normal (wet coil), up to ~1 inch when internally clogged | diagnostic drop across the evaporator coil | no | a9tX40eOJfw |
| Case-manufacturer design ambient | 75F / 55% RH (54F dew point) | standard store condition all case manufacturers spec; exceeding it overwhelms designed defrost | yes | RI1wD7nyGL4 |
| Fins per inch examples | 4-6 fpn shown; high-efficiency ~8 medium / 6 low temp | more fpn = more defrost needed | yes | RI1wD7nyGL4 |
| Efficiency gain from electronic valves | ~3-3.5% | minor efficiency change vs energy mandates driving fin count up | yes | RI1wD7nyGL4 |
| Rescue/replacement motor range | 4-25 watts, 1515-1725 RPM | one universal 'rescue' motor covers most refrigerated case fan motors | yes | RI1wD7nyGL4 |
| Food-safety core product limit | below 41F always | even in defrost; a case at 35-37F (no alarm) can leave core product mid-40s | yes | RI1wD7nyGL4 |
| Example spec CFM | 140 CFM | lab value with hood; field reading will be lower | yes | RI1wD7nyGL4 |
| Airflow acceptance rule of thumb | +/- 10% | like electrical; beyond that, investigate / compare to neighbor case | no | RI1wD7nyGL4 |
| total external static target | 0.5 in w.c. | target static; efficiency/capacity hit above it | no | gZQqjXhuMTI |
| attic dew point | can approach 100F absolute moisture | why ducts and surfaces in attics sweat | no | gZQqjXhuMTI |
| supply duct relative humidity | ~90-98% RH (but low absolute moisture) | why dehumidifier air goes in the supply | no | gZQqjXhuMTI |
| supply air temp shift with set point | 75F room -> 55F supply; 68F room -> 48F supply (20F split) | low set points make ducts/walls sweat | no | gZQqjXhuMTI |
| demo pressures | main body ~ -0.5 Pa; closed no-return bedroom ~ +3.2 Pa | mad house pressure demo | yes | _oJOBSJW0kA |
| static-pressure access hole | size of a #8 self-tapper hole | multiprobe magnetic static pressure probe | no | _oJOBSJW0kA |
| Model 7000 blower door fan | ~30% lighter, soon battery-capable | new Retrotec fan | yes | _oJOBSJW0kA |
| Max sealable leak size | up to 5/8 inch | Aeroseal | yes | bj962pMF1-Q |
| Example duct leakage | ~250 CFM, ~60 CFM tapeable at the unit | illustrating hand-seal plus Aeroseal | yes | bj962pMF1-Q |
| Aerosol suspension time | ~20 minutes airborne | protect furniture / use air scrubbers | yes | bj962pMF1-Q |
| Standard airflow rule | 400 CFM/ton (350 CFM/ton in humid Gulf Coast climates) | lower CFM/ton = colder coil, more moisture removal | yes | tXFHPWkUAOA |
| Standard air density | 0.075 lb/cubic foot | = 30 lb/min/ton at 400 CFM/ton | yes | tXFHPWkUAOA |
| 75F / 50% RH density | 0.0731 lb/cubic foot | not the standard 0.075 | yes | tXFHPWkUAOA |
| Altitude correction | 0.83 factor at 5000 ft | less mass for same volume | yes | tXFHPWkUAOA |
| Ton | 12,000 BTU/hr | definition | yes | tXFHPWkUAOA |
| Residential supply register velocity | ~300-600 FPM (300 quieter, 600 noisier/more throw) | rule of thumb | yes | Sz6A9-ihX-g |
| Return filter grille face velocity | keep below ~300 FPM; noise above 350-400 FPM | noise control | yes | Sz6A9-ihX-g |
| Trunk line velocity | ~700-1000 FPM (up to 1200 max) residential | above 1000 = high static/problems | yes | Sz6A9-ihX-g |
| Branch line velocity | ~500-700 FPM | typical residential | yes | Sz6A9-ihX-g |
| Regular (non-filter) grille | up to ~400-450 FPM without noise | return grille | yes | Sz6A9-ihX-g |
| nominal cooling airflow | 400 CFM per ton | Baseline used by the HVACRschool delta T calculator | no | c1LCnU3lO-M |
| southern/high-humidity airflow | often below 400 CFM/ton (~350) | Run lower to remove more latent heat | no | c1LCnU3lO-M |
| arid/high-altitude airflow | up to 500-550, more commonly ~450 CFM/ton | Higher airflow where dehumidification isn't wanted | no | c1LCnU3lO-M |
| delta T range | 14 to 24 degrees | 14 in extreme high-airflow cases up to 24 in low-humidity, low-airflow cases | no | c1LCnU3lO-M |
| nominal cooling airflow | 400 CFM/ton (1 CFM per 30 BTU) | Reframed as BTUs per CFM; fewer BTU/CFM = higher airflow | no | 2kgNFetuWKs |
| constant-torque motor airflow constancy | relatively constant up to ~0.9 inches of static | But actual CFM unknown without measuring | no | 2kgNFetuWKs |
| example furnace vs A/C mismatch | 70,000 BTU furnace vs 36,000 BTU A/C | Different temperature-rise vs CFM criteria; can't share a setting | no | 2kgNFetuWKs |
| total external static standard | 0.5 in wc | Industry-standard factory test static for many systems | yes | o6OVAUJXeuU |
| airflow rule of thumb | 350 CFM per ton | 5-ton = 1750 CFM; a balanced system returns what it supplies | no | o6OVAUJXeuU |
| example healthy split | -0.31 return + 0.19 supply = 0.5 | Perfect-world balanced static readings | no | o6OVAUJXeuU |
| room balance limit | 3 Pascal | Max pressure differential across a closed door for acceptable return balance | no | Jp2pZydCp28 |
| filter pressure-drop target | below 0.1 in wc | Keep filter pressure drop under 0.1; ideally use a 4-inch media filter in the return riser | no | Jp2pZydCp28 |
| typical test static values | 0.2, 0.3 or 0.5 in wc | Many systems are rated below 0.5, so exceeding rating worsens performance | no | Jp2pZydCp28 |
| freezing suction pressure | 101 psi = 32 F saturation (R-410A) | Running below 101 psi suction long enough freezes the evaporator coil | yes | x4_FkNNGzFo |
| expected suction line range | ~50-60 F | 75 F indoor minus 35 F TD = 40 F evaporator, plus 10-20 F superheat | no | x4_FkNNGzFo |
| high delta T indicator | 24-25 degrees | A split of 24-25 is a good (secondary) indication of low airflow; normal target range 16-22 | no | x4_FkNNGzFo |
| target airflow (humid climate) | 350 CFM per ton | Entered in the app; Arizona/dry climate runs ~500 CFM per ton for sensible-only cooling | no | USMxJexJvbo |
| example good install | ~344 CFM/ton, 0.56 in wc total external static | A 'dynamite install' reading on the diagnostic screen | no | USMxJexJvbo |
| TrueFlow plate capacity | up to 2,000 CFM | Same plate calculates up to 2000 CFM; cut-to-fit adapter for oddball grille sizes | no | USMxJexJvbo |
| aggressive/busted duct example | supply plenum ~0.7 in wc | Way outside the ~0.1-0.2 normal supply static, indicating undersized/crushed supply duct | no | USMxJexJvbo |
| measured house-to-outside pressure | about -9.8 Pa (near -10) | strongly negative rental house | yes | 27AoOAVSaM0 |
| indoor conditions | about 59% RH, ~67/23° | measured after stabilizing ~13-14 minutes | yes | 27AoOAVSaM0 |
| duct leakage system 1 | 6.8-7.2 CFM at 25 Pa (Ring 4) | duct blaster test, 3000 sq ft house, ducted 1-ton mini-splits | yes | DhXYd2Um1uE |
| duct leakage system 2 | about 4.6 CFM (~5 CFM total) | second heat pump system | yes | DhXYd2Um1uE |
| flex duct delivery | 90-92 CFM through 35 ft of 6-inch round flex | ducted mini-split branch | yes | DhXYd2Um1uE |
| filter grille pressure drop | 0.05-0.06 in wc at 400 CFM, 20x20 2-inch MERV 13 | oversized sealed filter grille | yes | DhXYd2Um1uE |
| infiltration share of load | 15-20% typical in Manual J, up to 40-60% in existing homes | why measuring infiltration matters | yes | DpX20OkmgoU |
| pressure pan thresholds | envelope leakage: >5 Pa connected outside, >10 Pa needs fixing; duct leakage: >2 Pa look into it, 3-5 issues, >7-8 significant | locating leakage with a running blower door | yes | DpX20OkmgoU |
| backdraft pressure | less than 5 Pa (1 in wc = 249 Pa) can backdraft a natural-draft appliance | combustion safety when sealing | yes | DpX20OkmgoU |
| Florida code ventilation trigger | blower door must be <7 ACH; below 3 ACH requires mechanical ventilation | new Florida code | yes | DpX20OkmgoU |
| house reference pressure | -50 Pa relative to outside | blower door setup for the demonstration | yes | 7bXPNva82qc |
| ZPD swing | from mid/high 40s Pa to 27 Pa by opening the door mask a couple inches | demonstrating the ratio fallacy | yes | 7bXPNva82qc |
| Minneapolis design temp | -8 to -20°F depending on version | climate zone 6 heating-dominated | yes | OioG8T_zwaA |
| furnace-to-heat-pump airflow jump | ~1200 CFM (heating) to ~1600 CFM (4-ton HP) through the same duct | why oversized HP overloads existing ducts | yes | OioG8T_zwaA |
| acceptable static ceiling | keep under 0.8 in wc; example ECM ran at 1.3 in wc off the charts | duct/blower limits | yes | OioG8T_zwaA |
| balance point construction | line through design-load point and 60°F at zero load; example thermal balance point 39°F, unit rated to -5°F | setting swap-over/aux heat | yes | OioG8T_zwaA |
| zero-load temperature by house type | ~60°F typical, ~52°F for a super-efficient/passive house | internal gains offset heating until this outdoor temp | yes | OioG8T_zwaA |
| motor life vs winding temp | 10°C (18°F) rise cuts life ~50% | rule of thumb for winding temperature | no | 1X9cXMrWc1o |
| typical condenser static | ~0.3 in wc residential | axial fan loading | no | 1X9cXMrWc1o |
| typical furnace static | 0.4 to 0.8 in wc | blower operating range | no | 1X9cXMrWc1o |
| replacement motor rule | match FLA, not more than 25% stronger; running amps OK slightly over name plate but not more than 10% high, never more than 25% below | selecting a replacement air-over motor | no | 1X9cXMrWc1o |
| blower catalog example | rated 1000 CFM free air drops to 850 CFM at 0.4 in wc on high | specify CFM at the required static | yes | 1X9cXMrWc1o |
| Demo system capacity | 3 ton | Gas furnace, side return | yes | pYA2xv0cukA |
| Heavily pressurized room threshold | ~22 Pascals | Indicates air can't get back to the return | yes | pYA2xv0cukA |
| 6 in vs 7 in duct area | ~36% (28 vs 38 sq in), not 17% | cross-sectional area change vs linear diameter change | no | uIXfiuY3i9U |
| typical elbow equivalent length | ~30 ft | most elbows are worth about 30 feet of straight duct | no | uIXfiuY3i9U |
| commercial design friction rate | 0.1 in per 100 ft | starting friction rate for commercial duct calc | no | uIXfiuY3i9U |
| Alex's residential rule-of-thumb friction rate | ~0.06 | what he'd pick over 0.1 if forced, because resistance is cheap to add | no | uIXfiuY3i9U |
| standard air density | 0.075 lb/ft3 at sea level, 68.3F, 0% RH | definition of standard air used in mass-flow calcs | yes | FMSl9qexPRw |
| mass flow per ton | 30 lb/min per ton | 400 SCFM x 0.075; a 5-ton = 150 lb/min across the coil | yes | FMSl9qexPRw |
| 1924 standard air revision | 70F at 50% RH | heating and ventilating society definition; difference from 68F/0% is <2% | yes | FMSl9qexPRw |
| specific volume example | 13.33 ft3/lb at 68F, 0% RH | inverse gives density; interchangeable via reciprocal | yes | FMSl9qexPRw |
| problem pressure drop | over 0.2 in w.c. across a filter is almost always a problem | though a MERV 13 24x24 can still be fine if velocity/headroom allow | no | 4R0V6a6Uz3c |
| typical headroom | ~0.5 in total external static is about all the headroom on their equipment | some air handlers rated at only 0.2 TESP means the filter alone eats it | no | 4R0V6a6Uz3c |
| return face velocity target | 300-500 fpm | keep return velocity low so air is easier to clean | no | 4R0V6a6Uz3c |
| desired filter pressure drop | 1.0 in w.c. or less (prefer well under) | goal for filter pressure drop | no | 4R0V6a6Uz3c |
| Kalos airflow rule of thumb | 350 CFM per ton | sizing filters/airflow for imperfect Florida houses favoring latent removal | no | 4R0V6a6Uz3c |
| typical delta T range | 14 to 23 degrees | normal equipment vs the old 20-degree rule of thumb | no | _pD-rRCNv8k |
| standard rule-of-thumb conditions | 400 CFM per ton, 12,000 BTU per ton | conditions where the old charts only really work | no | _pD-rRCNv8k |
| measureQuick normalized target example | target 20.8 on a 2-ton variable speed unit | measureQuick normalizes for capacity given current conditions vs universal 400 CFM/ton charts | no | _pD-rRCNv8k |
| oversizing limits | 115% single-stage, 120% two-stage, 130% variable | Manual S max capacity vs calculated cooling gain | yes | sjZR0bTL1Ig |
| heat-pump oversizing | up to 15,000 BTU (condition A/B), hard stop beyond | condition B is SHR > 0.95 (extremely tight), HDD/CDD ratio > 2 | yes | sjZR0bTL1Ig |
| CFM formula | sensible BTU / (1.1 x altitude correction x delta T) | 1.1 rounds 1.08 standard-air factor; 17-degree design delta from SHR 0.88 | yes | sjZR0bTL1Ig |
| latent measurement | a pint is a pound; red solo cup filled in 15 min = ~4000 BTU | quantifying latent removal at steady state | yes | sjZR0bTL1Ig |
| dehumidifier max size | 85% of latent gain | engineered dehumidification in a heating-dominated climate per Manual S appendix | yes | sjZR0bTL1Ig |
| furnace oversizing | no more than 140% of calculated loss | Manual S heating in a nutshell | yes | sjZR0bTL1Ig |
| control voltage checks | 24 volts | measured C to Y/Y2, C to G, and C to DH to confirm full-speed operation | yes | M99zS-5yeSs |

## Field tips (the trick that saves time)

- Giving yourself a clean access point is key to quality service; cut a new hole rather than fight a bad one.  *(id: Rl2Ej7fdy1U)*
- Always wear a mask when working under a trailer (wet, dusty, 'cat poopy' conditions).  *(id: Rl2Ej7fdy1U)*
- Put mastic on the inner liner first to make sliding the flex easier.  *(id: Rl2Ej7fdy1U)*
- Strap duct up high to keep it off the ground and prevent pinching/kinking.  *(id: Rl2Ej7fdy1U)*
- How you put things back (closing out the call) is what the customer judges, since they can't see the hidden work.  *(id: Rl2Ej7fdy1U)*
- Buy an entry-level blower door and do 50-100 tests to get good; you learn something every time.  *(id: IlrHazYv84M)*
- Measure your own duct tightness before leaving the job so you never pay for a failed third-party retest.  *(id: IlrHazYv84M)*
- Own the testing and market with proof ('scientifically proven best - ask us how') instead of opinion.  *(id: IlrHazYv84M)*
- A manometer is the entry tool (gas pressure, static, pitot velocity); read total external static on both sides of what's in the box.  *(id: IlrHazYv84M)*
- Assign one dedicated diagnostician rather than nominally training the whole crew.  *(id: IlrHazYv84M)*
- Measure register face velocity (vane anemometer timed-traverse / Testo 417) to confirm proper mixing without knowing exact CFM.  *(id: X2Y1KNFoxug)*
- Pull flex taut (60 seconds per 25ft), minimize turns, and cut excess length; size the trunk right so noise stays in the trunk.  *(id: X2Y1KNFoxug)*
- Use flat tabbed collars WITH a built-in damper so balancing turbulence/noise stays in the trunk, not the branch.  *(id: X2Y1KNFoxug)*
- Rule 1: don't blow air on people (it makes them angry); Rule 2: more outlets = more comfort.  *(id: X2Y1KNFoxug)*
- Use software (Rhvac) with the modified-equal-friction method for precise per-branch sizing.  *(id: X2Y1KNFoxug)*
- Use a vane anemometer for density-independent, repeatable CFM; use the timed-traverse ('paint the grille') method with a Testo 417 (large) or 410i.  *(id: 7lEhrcbaeGM)*
- A hot-wire is very turbulence-susceptible (useless in a flex-duct return) but great for tiny velocities and as a heat-exchanger leak detector.  *(id: 7lEhrcbaeGM)*
- Don't put the 417 cone adapter on a supply register (too much back pressure); use a hood or micro-hood instead.  *(id: 7lEhrcbaeGM)*
- Always ask 'what am I making this measurement for?' before choosing a method.  *(id: 7lEhrcbaeGM)*
- Measure static on both sides of what's in the box: a furnace is rated alone (measure in the cabinet above and below the coil), while an air handler/RTU is rated with coil and factory filter; adding strip heat or an aftermarket filter changes the rating chart.  *(id: ryTchnFMem0)*
- Place static tips in a low-turbulence (laminar) spot, away from the blower-inlet vortex and the corners where air turns; wrap tape on the drill bit to stop at ~1/4 inch and drill in a corner away from wiring; use a static-pressure tip (holes around it), not a pitot.  *(id: ryTchnFMem0)*
- Set up equipment in a stable-temperature space to practice and get repeatable readings.  *(id: ryTchnFMem0)*
- Think of the whole system (air, refrigerant, and electrical distribution), not just the appliance - avoid 'appliance fixation'.  *(id: ryTchnFMem0)*
- Push N-shaped cased coils to the left so the drain pan overhangs and the whole coil gets airflow.  *(id: PjWScoD3NH4)*
- Pull the blower wheel via the oversized washer/ring (bigger than the wheel) to access the back of the housing.  *(id: HvhaFcc7cLQ)*
- Secure loose insulation with plumbing strapping in an X, then glue and metal-tape.  *(id: HvhaFcc7cLQ)*
- Kill power - note that some terminals stay live even with that breaker off.  *(id: HvhaFcc7cLQ)*
- A ratcheting nut driver is great for tight spots.  *(id: HvhaFcc7cLQ)*
- Draw the duct system out and take good notes as you take readings.  *(id: wmJ0QBKEbB8)*
- Drill high and low test ports and read the differential to detect turbulence a single reading would miss.  *(id: wmJ0QBKEbB8)*
- Re-measure static pressure after air-sealing ducts (it will go up).  *(id: wmJ0QBKEbB8)*
- Pull flex duct tight and straight; a kink or coiled 'spaghetti' run destroys performance.  *(id: wmJ0QBKEbB8)*
- Use a pressure pan (plastic box + weatherstrip) with a blower door and high-res manometer to estimate duct leakage.  *(id: wmJ0QBKEbB8)*
- Blower motor type also affects how air weight impacts performance and how you measure air.  *(id: GgvSnm_gqt8)*
- Look for fine-fiber media with loft; do the palm-press test to feel a filter's structure (cheap expanded-metal backing crushes vs 100,000-lb tensile welded wire).  *(id: s4EGvkZPqgo)*
- Sell filtration on total cost of ownership plus energy savings and sustainability (fewer landfill trips).  *(id: s4EGvkZPqgo)*
- Take static AFTER the filter (filter/furnace pressure drops are massive - 'furnace killers').  *(id: wWN2IKAqpy4)*
- Pull flex duct straight and tight - reach inside and pull the inner vinyl liner off the boot; extra slack kills airflow.  *(id: wWN2IKAqpy4)*
- Change meter batteries seasonally - a weak/corroded battery gives inaccurate readings and can destroy the meter.  *(id: wWN2IKAqpy4)*
- Use a straight tube at ~45 degrees to the airflow as a field static tip if you don't have one.  *(id: wWN2IKAqpy4)*
- Seal orientation plugs permanently with silver tape on the inside once the system is installed upright (they're only needed for other orientations).  *(id: AWecM1MfuEE)*
- Clean a metal surface with alcohol and squeegee tape so it adheres; masking tape for removable seams, foam tape (ugly) only where needed.  *(id: AWecM1MfuEE)*
- When moving to a media filter in the return riser, seal the old filter door and clean out the previously-unfiltered return.  *(id: AWecM1MfuEE)*
- Measure static on the top side of the filter (a Bryant/Evolution controller reporting 'total external static' is really blower static).  *(id: eHzYalJXE88)*
- In residential you only get what the manufacturer gives (0.5), so budget: big return + gigantic filter to offset a weak supply.  *(id: eHzYalJXE88)*
- Supply vents are sized for velocity/throw (Bernoulli entrainment mixes room air), which is different from velocity inside the duct.  *(id: eHzYalJXE88)*
- Set up dehumidification/DH terminals and blower taps correctly, or dehumidification mode ramps the blower down all the time.  *(id: FFYvSwCIYho)*
- Put one static probe under and one on top of the coil to trend coil fouling; a screw-hole and flexible probe is fine (position affects reading only ~0.01).  *(id: FFYvSwCIYho)*
- Oversize ducts + use balancing dampers; a bigger return budgets static so you can accept worse supply ducts; a vane anemometer on a selfie stick sets velocity room-to-room.  *(id: FFYvSwCIYho)*
- Instead of jamming flex around a tight corner, extend the plenum box or use an adjustable snap-lock 90, then attach flex and pull the excess flex insulation over the fitting; strap/support any heavier hard fitting so it doesn't pull out.  *(id: 3m1eRBXDM5I)*
- Clean fittings with isopropyl/denatured alcohol first - factory oil on the metal hurts tape and mastic adhesion.  *(id: 3m1eRBXDM5I)*
- Seal the collar to duct board by painting mastic around the cut hole before setting the collar; for the inner liner, 'Grant's method' is mastic on the inner liner, pull it over, tape to the collar (mastic inside) plus a panduit strap.  *(id: 3m1eRBXDM5I)*
- Reduce excess flex length (don't leave 25 ft where 10 is needed); fully extend it but not banjo-tight so it doesn't pull off the fitting.  *(id: 3m1eRBXDM5I)*
- Avoid wet mastic on a job that will run cold air immediately - pressurization can blow it out around the still-wet seal and cause condensation.  *(id: 3m1eRBXDM5I)*
- Use a speed controller to 'cruise' the fan and hold 50 pascals.  *(id: i4YuqUPmwHs)*
- Run the DG-1000 gauge's auto-test app: select the standard, and it runs the multi-point test, graphs it, geofences the location and altitude, and prints a report.  *(id: i4YuqUPmwHs)*
- Deploy all probes every stop and save a measureQuick screenshot as your readings to build reps on what 'normal' looks like.  *(id: y4y1EtgEs9w)*
- Measure TESP: return above the filter + supply on the unit; probe orientation (up/down) barely matters in residential (test it yourself to confirm).  *(id: y4y1EtgEs9w)*
- Fix a dirty coil or blower wheel before trusting measureQuick's airflow estimate - the probes sit between them and can't see that fouling.  *(id: y4y1EtgEs9w)*
- Verify BOTH inlet and outlet gas pressure at the valve's rating before condemning a gas valve - wrong inlet pressure means it's not the valve.  *(id: y4y1EtgEs9w)*
- A filter in a small (18x18) return grille plus the grille itself is a major restriction; moving to a media filter at the (20x20) unit can greatly cut static.  *(id: y4y1EtgEs9w)*
- Upgrading filtration (low static, high-quality filter) is the single highest-leverage change a contractor can make on the very first visit.  *(id: jMTxblZcTzE)*
- Carry a pressure pan and use it alongside a blower door to find duct leakage and to prove whether or not you are the source of a comfort/pressure problem.  *(id: jMTxblZcTzE)*
- Seal top and bottom plates to stop the stack (chimney) effect; focus air sealing at the top and bottom of the enclosure.  *(id: jMTxblZcTzE)*
- Do infrared imaging early in the day (or track the sun) so solar gain does not mask the thermal signatures of leakage.  *(id: jMTxblZcTzE)*
- Partner with air-sealing/insulation contractors for referral revenue and to fix envelope problems you do not do yourself.  *(id: jMTxblZcTzE)*
- Don't push the snips all the way through when notching drive cleats or you cut a huge notch that causes an air-sealing issue.  *(id: y_aTNtv_2bM)*
- Install the bottom S-slip first (gravity is your friend); keep the canvas connector relatively tight.  *(id: y_aTNtv_2bM)*
- Beware older equipment: harder to get airflow dialed in (dirty coils, blowers, restricted returns/supplies) than brand-new equipment where TESP + airflow chart gets you close.  *(id: EJVRhznC_Ts)*
- Adds only ~10 minutes to the day once it's part of your workflow.  *(id: EJVRhznC_Ts)*
- Before taping to existing duct board, clean it with alcohol; do not rely on spray glue to make it stick.  *(id: VDJotlJj3Mo)*
- Suspend flex in the air strapped properly; don't let it lay on trusses or other ducts (every sag/compression point is prone to sweating).  *(id: VDJotlJj3Mo)*
- Run only straight, tight runs of flex; where you must turn, install a metal fitting and attach flex to it to cut insulation compression, turbulence and friction.  *(id: VDJotlJj3Mo)*
- Use an outward-cinching stapler on staple-flap/fab connections, especially on boxes going into the attic.  *(id: VDJotlJj3Mo)*
- This applies to negatively pressurized systems (air handlers, pancakes, heat pumps), not gas furnaces/positively pressurized coils where air pushes water out.  *(id: zOpdAbQuBXM)*
- Build a standard P-trap holding a 1-2 inch water column; higher return static pushes toward the 2-inch size.  *(id: zOpdAbQuBXM)*
- Follow manufacturer literature for commercial or non-standard (running/UT) traps.  *(id: zOpdAbQuBXM)*
- Silver (reflective) flex rejects roof-deck radiant heat; black flex picks it up and dumps hot air from the vents when the unit cycles off.  *(id: 75Q15TVoazE)*
- Seal and insulate around vents and can lights, and close/insulate open duct chases, to cut cumulative attic gains.  *(id: 75Q15TVoazE)*
- Check refrigerant caps for the missing seal (a cheap part) that can leak; a slight freeze-up can drop water into the return box.  *(id: 75Q15TVoazE)*
- Never start a blower-table lookup on high speed; use medium or lower.  *(id: -KqmAQgUXY4)*
- Flex duct slides assume 0-4% compression; use a flex-specific slide and account for 15%/30% compression - a 110 CFM run needs 7-inch metal, 8-inch flex at 4%, or 10-inch flex at 30% compression.  *(id: -KqmAQgUXY4)*
- Pick registers so they hit terminal velocity at ~3/4 of the room throw, and blow air in the direction it doesn't want to go to promote mixing.  *(id: -KqmAQgUXY4)*
- Give the air two turns with no line of sight to the blower to reduce noise; use a digital TrueFlow/DG8 to verify airflow via the filter slot after taking a supply static reading.  *(id: -KqmAQgUXY4)*
- Align the inner and outer collar (often installed in different positions) and let the flex expand fully before connecting.  *(id: hz-R4InhRBM)*
- Put the inner liner three rings deep over the collar ridge, tape and squeegee it, then Panduit forward of the ridge so if the rings slip the strap holds them.  *(id: hz-R4InhRBM)*
- Install manual dampers with handles so each run's airflow can be balanced and set.  *(id: hz-R4InhRBM)*
- Measure from the plenum down to the top of the unit; keep the level line true first.  *(id: DgxhPFfPlEs)*
- Seal with silver tape, then spray glue, then fab tape and mastic (or from the inside: fab, spray glue, mastic if you can't reach the back).  *(id: DgxhPFfPlEs)*
- Use small plywood risers/strips to keep the plenum off the platform so it doesn't get painted-in and fail inspection.  *(id: DgxhPFfPlEs)*
- If you have gaps, remake the piece; get the seal as tight as possible.  *(id: DgxhPFfPlEs)*
- Measure static pressure with a manometer using a static pressure tip (closed on the end) to capture outward force, not velocity pressure; supply side reads positive, return side negative — pressure drop is an absolute value (drop the sign).  *(id: NzlsB9R6mbc)*
- Highest pressure is always nearest the fan; lowest is on the opposite side of the filter/coil.  *(id: NzlsB9R6mbc)*
- When plotting fan airflow from the fan table, be careful on a dirty system — plotted airflow won't be accurate.  *(id: NzlsB9R6mbc)*
- When squaring the CFM ratio in Fan Law 2, multiply the number by itself — the most common mistake is multiplying by 2 instead of squaring.  *(id: NzlsB9R6mbc)*
- Use a TrueFlow grid (Energy Conservatory) to measure fan airflow; hand-select the lowest-pressure-drop coil and largest/lowest-drop media filter (e.g., go to 20x25) even if the cabinet is narrower, using a pre-made transition.  *(id: NzlsB9R6mbc)*
- Size equipment to the load (right-size/downsize) to increase comfort, reduce duct pressure and leakage, and swing static pressure favorably.  *(id: NzlsB9R6mbc)*
- Let the flow hood reading settle/stabilize before recording a CFM value.  *(id: XeanFStDbyY)*
- When you oversize a run, install a damper so you can dial it back precisely.  *(id: XeanFStDbyY)*
- Adjust in tiny increments near the target CFM; small damper moves make large changes when nearly closed.  *(id: XeanFStDbyY)*
- Loosen the drive fully before rolling a belt on or off so you don't stretch it.  *(id: rNBt7LN-8ao)*
- Use a proper tensioning tool (apply a set force, read a fixed deflection) at least a few times to calibrate your feel for a given belt width.  *(id: rNBt7LN-8ao)*
- Re-check tension a few hours/days after install as the belt seats in (if you're in a maintenance/facilities setting), but never over-tighten.  *(id: rNBt7LN-8ao)*
- Clean greasy/oily belts and fix the contamination source rather than repeatedly adjusting or replacing belts.  *(id: rNBt7LN-8ao)*
- Place a mixed-air probe on EACH side of the blower -- a hot leak can travel down one side of the duct and not mix until the fan.  *(id: lvMjm3YwUY8)*
- MeasureQuick requires good probe placement; when it agrees with TrueFlow you also know your probes are placed right.  *(id: lvMjm3YwUY8)*
- Use a duct-tightness (duct blaster) test as the tie-breaking third measurement to locate leakage two measurements can't pin down.  *(id: lvMjm3YwUY8)*
- You don't have to train everyone to commission -- designate one or two commissioning specialists to vet installers' work, then train out recurring deficiencies.  *(id: lvMjm3YwUY8)*
- The solutions to the problems you'll find are in ACCA Manual J, D, and S.  *(id: lvMjm3YwUY8)*
- Actually clean drains with brushes on a PM -- don't just pour water down and change the filter and call it good.  *(id: LGgET3gRY20)*
- Cut the drain pipe end at an angle so it can't suction flat against the bottom of a pump/pan and can keep draining.  *(id: LGgET3gRY20)*
- Where maintenance is poor, oversize the trap depth ('better safe than sorry').  *(id: LGgET3gRY20)*
- Treat rust at the base of an air handler as a red flag to investigate trap depth / static.  *(id: LGgET3gRY20)*
- Measure supply air temperature out of the line of sight of the coil/blower, ideally ~5 feet away, so radiant heat and turbulence don't corrupt the reading.  *(id: aRJH-wJZ1Gs)*
- A return grille needs no AK factor when using a vane anemometer; a supply duct/register requires the manufacturer's printed AK factor.  *(id: aRJH-wJZ1Gs)*
- Let delta T stabilize (steady) before recording measurements.  *(id: aRJH-wJZ1Gs)*
- Attach the filter box to the suction (intake) side of the box fan; confirm direction by running the fan and feeling which way air moves.  *(id: Y7eL2OAnqc8)*
- Stagger the filter seams so they line up square, and tape all seams to prevent air bypass.  *(id: Y7eL2OAnqc8)*
- Use a sharp knife because cardboard dulls a blade quickly.  *(id: Y7eL2OAnqc8)*
- Loosen the Phillips set screw nearly all the way so the blower wheel releases easily.  *(id: 2VvoER81-co)*
- Spray a coil/wheel cleaner such as Viper Evap Plus before washing; the demo cleaned the wheel with just a garden hose.  *(id: 2VvoER81-co)*
- Confirm all electrical power is off before starting, and empty water from the drain pan before dropping it.  *(id: 2VvoER81-co)*
- Use drop cloths and protect surfaces when doing this work indoors; don't wash grime onto the customer's driveway.  *(id: 2VvoER81-co)*
- Let the wheel dry fully before reinstalling.  *(id: 2VvoER81-co)*
- Start by measuring plenum height, then cut a U-shape (three sides) and a separate door panel with ~1 in extra on each side for overlap.  *(id: hgFafh_AFLU)*
- Cut small triangular tabs (~1/4 in opening, ~1 in deep) to form the bottom flanges.  *(id: hgFafh_AFLU)*
- Mark and cut the drain-line hole, then seal around the connections.  *(id: hgFafh_AFLU)*
- When it's raining and you can't pump down (and it's a scroll), bend the lineset with available slack rather than opening the system.  *(id: hgFafh_AFLU)*
- Single-port manometers let you place the probe exactly where you test but still compare points like a dual manometer.  *(id: wdnaeZkstXI)*
- When only looking for a differential (e.g. across a filter), probe orientation/P1-P2 matters less than the delta.  *(id: wdnaeZkstXI)*
- Zero the manometers by pressing the button (flashes blue then zeros).  *(id: wdnaeZkstXI)*
- Push the wheel back toward the motor and expose the shaft end to clean it with emery cloth/brushes/steel wool and penetrating lubricant.  *(id: YwFkhTqgazM)*
- Rinse wheel and housing outside; if on grass, wet the grass first so it absorbs water before chemicals.  *(id: YwFkhTqgazM)*
- Use non-caustic cleaners like Viper HD diluted per label; never get water inside the blower motor; grease the shaft before reinstalling.  *(id: YwFkhTqgazM)*
- After reassembly, run-test for abnormal noises and check current.  *(id: YwFkhTqgazM)*
- Don't measure every room's airflow unless you are getting paid (that is a chargeable airflow diagnostic); David priced systems ~$295 (~$495 for extras) and refunded it if they proceeded so the customer has skin in the game.  *(id: 5eiv-0518mQ)*
- Use a true-flow grid / direct airflow tool (not just plotting fan tables) and a good manometer - a cheap manometer can be a random number generator.  *(id: 5eiv-0518mQ)*
- Put a balancing hood or thermal camera in the customer's hands with a target to aim for; they become your best salesperson.  *(id: 5eiv-0518mQ)*
- Get paid for designs; use all the puzzle pieces (leave none out); for entry-level workers use 'duct innovators' as pre-installers.  *(id: 5eiv-0518mQ)*
- Never promise perfection - promise a noticeable, documented improvement; if you offer balancing you must install balancing dampers.  *(id: 5eiv-0518mQ)*
- Crease where all bends will be so the box stays rigid under system pressure.  *(id: EgFAL_z7P2o)*
- Add mastic and insulation if the installation calls for it.  *(id: EgFAL_z7P2o)*
- Use a flexible caulk (Durling 50), double-sided/super-sticky tape, vice grips, and tin snips.  *(id: gE3Dnn0u3kA)*
- The sticky tape holds the seam so the caulk (bead in the seam) takes the sealing load; let it dry in the sun before installing.  *(id: gE3Dnn0u3kA)*
- Leave enough room for two screws and the S-slip/drive cleat when folding the connector edges.  *(id: gE3Dnn0u3kA)*
- Point the S of the S-lock toward the outside so you can work metal into the 1-inch gap.  *(id: rO4yqiWjOtU)*
- Mark corners where S-locks hit on all four sides, then use a spare S-lock to mark the extra inch for the fold.  *(id: rO4yqiWjOtU)*
- Notch corners a quarter-inch past your line at an angle; then screw together and mastic the seams in the field.  *(id: rO4yqiWjOtU)*
- Air-seal all four sides so air can't bypass the filter; keep the fan feet folded out so it stands.  *(id: gToHQvORNHs)*
- Higher MERV catches more particulate; activated carbon adds VOC capture but higher pressure drop (watch fan speed).  *(id: gToHQvORNHs)*
- This is NOT protection from a virus/COVID - just practical air filtration; an alternative is taping a filter over a window with bath fans creating negative pressure.  *(id: gToHQvORNHs)*
- Zero the sensor first; put the probe with higher negative pressure on the negative side.  *(id: zkPcIKKGwwc)*
- Uses the Testo 510i smart probe from the smart-probes kit.  *(id: zkPcIKKGwwc)*
- Set the device: volume flow to CFM, differential pressure to inches of water column, temperature to Fahrenheit.  *(id: kAjT-VujA6I)*
- Hold the reading for ~5 seconds, press to hold, then save into the report; connect via Bluetooth later to pull the full flow report.  *(id: kAjT-VujA6I)*
- Swivel handles let you reach ~10-foot ceilings without a ladder.  *(id: kAjT-VujA6I)*
- Use a power-quality meter (e.g. Redfish IDVM550) that accounts for power factor to get true wattage.  *(id: 8ANRxjC6xs8)*
- On new equipment, get CFM from the manufacturer fan tables using measured static pressure; otherwise use a TrueFlow grid, duct traverse, or airflow hood.  *(id: 8ANRxjC6xs8)*
- MeasureQuick brings CFM and wattage together and calculates fan efficacy for you.  *(id: 8ANRxjC6xs8)*
- Point the static probe opposite/into the airflow direction; ball needles or a straight probe also work fine on residential.  *(id: 6uMqw69XkRw)*
- Put the return probe into a laminar (low-turbulence) straight run, not a corner where reverse airflow occurs.  *(id: 6uMqw69XkRw)*
- Keep the probe perpendicular to the duct walls so velocity pressure doesn't affect the static reading.  *(id: 6uMqw69XkRw)*
- Forecasting only unlocks in TrueFlow workflows that include a real (filter-corrected) raw flow measurement - not static-pressure-only workflows.  *(id: cGT6ZA3bcIg)*
- Flat-rate common add-ons (like a return drop) so comfort consultants can add them without doing the math on the spot.  *(id: cGT6ZA3bcIg)*
- If no budget for envelope/duct work in a cold climate, go dual fuel; if there is budget, address duct leakage to outside first, then envelope leakage.  *(id: cGT6ZA3bcIg)*
- Use a smaller fan ring for a tight house and a fully open fan for a leaky/large house.  *(id: 0YnhnPTkyU0)*
- The test helps you understand how much water vapor/latent load you must deal with in a house with humidity or comfort problems - so you don't just keep upsizing equipment and dehumidifiers without fixing the envelope.  *(id: 0YnhnPTkyU0)*
- A ball inflator needle fits through a screw hole to measure in tight spots (between furnace and coil); prove any alternate tip against a known static tip - a good tip reads zero differential.  *(id: ddhQrxuIbUI)*
- Write the heating and cooling static pressures on the duct next to the test port with a sharpie - static pressure is like blood pressure; you can take four readings in under two minutes on a return visit.  *(id: ddhQrxuIbUI)*
- Back the round-to-square transition away from a filter (18-24 in) so air uses the full filter surface; a dirt pattern the size of the inlet duct means air isn't hitting the whole filter.  *(id: ddhQrxuIbUI)*
- For higher MERV ratings put in a LARGER filter (e.g. 20x25x4 for a 2.5-ton at ~0.1) or static goes through the roof.  *(id: ddhQrxuIbUI)*
- Insulate the TXV sensing bulb and strap it with a conductive strap (not bare zip tie) at the proper location.  *(id: hCZEg_DGCf0)*
- Measure condensate and use a TrueFlow grid to actually quantify airflow when readings say low but nothing obvious is found.  *(id: hCZEg_DGCf0)*
- Don't cut the sleeve all the way through — leave a bit so you can bend and get identical-length pieces repeatedly without a tape measure.  *(id: md1OyUs-tcA)*
- Install the slip on the piece that has a cut for easier drive-in; orient the sleeve considering airflow direction, which matters on high-static duct.  *(id: md1OyUs-tcA)*
- Carry a Pascal-resolution autozeroing manometer for house pressures (TEC DG-8 or DG-1000, Retrotec DM32).  *(id: YUjv96bbQOM)*
- Oversize the makeup-air filter (e.g., 20x20 high-MERV, low pressure drop) so you can add a damper and dial airflow down; don't undersize it and have to redo it.  *(id: YUjv96bbQOM)*
- Use central returns for low-airflow rooms and ducted returns for high-airflow rooms; always ensure a low-resistance return path and watch high-resistance louver doors.  *(id: YUjv96bbQOM)*
- Balance makeup air to the most-used exhaust (watch high-CFM kitchen hoods; count the clothes dryer as an exhaust fan) and interlock makeup air with exhaust for neutral house pressure.  *(id: YUjv96bbQOM)*
- Blow air across/at heat-conducting surfaces (walls, windows), not on people, and use register selection/placement (Manual T); consider the Coanda effect.  *(id: YUjv96bbQOM)*
- Bath fans and dryer venting are HVAC's job (the 'V' in HVAC), not the plumber's.  *(id: YUjv96bbQOM)*
- Use dedicated dehumidification and filter incoming air separately in humid climates.  *(id: YUjv96bbQOM)*
- Some prefab duct comes with sealant already in the seam so you don't need to seal that seam; not all does.  *(id: UKdV16U6JrI)*
- To mark a reducer for cutting, imagine the piece in place and match the lines to get a straight line, marking where the sleeve ends.  *(id: UKdV16U6JrI)*
- To cut an already-assembled duct section (hard to take apart when it has sealant), use two aviation snips (green-handle and red-handle) to make two cuts about an inch-and-eighth apart; you lose about one inch of duct in the cut.  *(id: UKdV16U6JrI)*
- Cutting with a grinder or sawzall works but the two-snip method is cleaner/better.  *(id: UKdV16U6JrI)*
- You must look carefully at the vent's specifications to find the free-area percentage in order to convert velocity to CFM.  *(id: WTEoz7P3QDM)*
- Low velocity was set intentionally here to reduce air noise, but oversizing duct/low velocity in many cases results in insufficient throw.  *(id: WTEoz7P3QDM)*
- You can alternatively run a reference tube to outside and drive the duct blaster to -25 Pa, which some find easier to understand but is more work.  *(id: FtPWajjm1Q0)*
- Duct leakage to outside is conceptually hard to read about but makes sense once you run the workflow one good time.  *(id: FtPWajjm1Q0)*
- Hold the probe very flat and use consistent pacing across all measurements for an accurate timed traverse.  *(id: 29sNEDcQJTc)*
- Make roughly equidistant ports across the duct for the traverse.  *(id: 29sNEDcQJTc)*
- Use nickel-safe, food-grade cleaners for coils/ice machines; use products rated for the application (a non-rated antimicrobial once caused a client allergic reaction).  *(id: GRhAWA4tz1I)*
- Coat UV lamp assemblies with a circuit shield / use CorrosionX-type coatings because they corrode and fail when they get wet.  *(id: GRhAWA4tz1I)*
- Blow condensate pump lines out with nitrogen/CO2 (carefully with poly tube) — even pumped lines can restrict on long/high-lift runs.  *(id: GRhAWA4tz1I)*
- Keep contact cleaner on the truck; consider silicone conformal-coating boards to help resist bugs/lizards/ants that take out ductless boards.  *(id: GRhAWA4tz1I)*
- Do a pre-inspection to establish the system was already working before you touch it, so any issue isn't blamed on you.  *(id: GRhAWA4tz1I)*
- Verify ductless operation with probes + a core depressor (not hoses every time) to avoid refrigerant loss on small critical charges; ramp to high speed and check discharge air temp and suction temp, tracking trends over time.  *(id: GRhAWA4tz1I)*
- Pre-inspect and communicate prior issues (missing screw covers, torn filters) BEFORE cleaning so problems aren't blamed on you.  *(id: DHWcSYPLLVw)*
- Look for signs of oil (flare leaks are the #1 leak point on ductless) and tubing rub-outs / chafed wires — preventing a future breakdown is often the biggest value.  *(id: DHWcSYPLLVw)*
- Use the bib kit's deflector back-plates and bag tucked behind the unit to keep walls clean; wear PPE, especially safety glasses.  *(id: DHWcSYPLLVw)*
- Clean drains/pan/condensate pump reservoir and screen thoroughly (brush the port before flushing); if the reservoir can't be serviced it's installed wrong — quote a fix.  *(id: DHWcSYPLLVw)*
- Steam/dry-steam cleaning is the way to go for chemical-sensitive customers, dirty-sock odors, and grease (restaurants).  *(id: DHWcSYPLLVw)*
- Only use the least-caustic cleaner necessary; for condensers usually water or a very mild/highly-diluted cleaner, especially on thin micro-channel aluminum.  *(id: DHWcSYPLLVw)*
- Let cleaner dwell at least 5 minutes before rinsing; never spray viscous silicone-enzyme products directly onto standing water in a pan or into a pump.  *(id: DHWcSYPLLVw)*
- Aim the static tip's arrow INTO the airflow so it reads space pressure, not velocity pressure (matters more on larger, higher-airflow systems).  *(id: QHHMC5K2moU)*
- When both probes are on the negative (return/coil) side, total external static is the sum of the two negatives — do the math yourself; measure-quick tools may not handle two negatives automatically.  *(id: QHHMC5K2moU)*
- You can pull the filter and measure to see how much the filter alone is restricting the system.  *(id: QHHMC5K2moU)*
- A collapsed/water-filled return duct shows high static up the line that drops further down — sometimes you'll find it visually faster.  *(id: QHHMC5K2moU)*
- Land the Panduit strap on the collar ridge/lip with multiple inner layers pulled over it (so a metal ring is tucked under the strap), and tuck the joint so an inspector never even sees it - the insulation seals everything.  *(id: iygU_hFM9Os)*
- Don't over-tighten Panduit on large duct (14-20 in) or you crush it; over-tightening also compresses insulation R-value (only a real problem in already-sweating attics).  *(id: iygU_hFM9Os)*
- Keep a marker and pre-cut strapping in your attic bag; make your first strap before you start so the duct doesn't pull away while you work.  *(id: iygU_hFM9Os)*
- Metal ('silver') tape is only for metal-to-metal bonds; use duct tape (not mastic) on splices where there isn't room for a clean mastic bond; Fab-wrap the outer joint front-to-back for a clean insulated seal (required by code even though the inner seal does the sealing).  *(id: iygU_hFM9Os)*
- Zero the manometer to atmosphere before every use (and when moving it); take external static with the blower on HIGH/full stage, just like checking charge.  *(id: a9tX40eOJfw)*
- 'Taking a measurement is better than taking no measurement' - don't let perfection stop you; tape a probe under the filter door if you must (clunky but valid), and probe position barely changes a utility-manometer reading.  *(id: a9tX40eOJfw)*
- Never drill into a heat exchanger (you'll replace the furnace) or the evaporator drain pan; use the metal-to-metal sealed spots or a pre-drilled port.  *(id: a9tX40eOJfw)*
- Fix a high filter drop by enlarging filter surface area (wider media filter / transition) for better filtration at lower resistance, rather than dropping to a lower MERV, unless the static is actually causing a problem.  *(id: a9tX40eOJfw)*
- Motor rotation labels have no industry standard: CW/CCW may be viewed from shaft end or back — newer labels add O (opposite), SE (shaft end), P (pulley/plate); learn the convention for the brands you stock (US Motors example: CW opposite shaft end).  *(id: RI1wD7nyGL4)*
- Deck pans and a sealed plenum are critical — if the plenum isn't sealed flush and to the pan, the fan recirculates instead of pulling through the coil; check coil-to-back-wall seal after de-icing (ice can break clips and push the coil forward unnoticed).  *(id: RI1wD7nyGL4)*
- Help the store fix load-limit / unauthorized-merchandiser problems; unapproved pushers/shelves change the designed air wall and may require product (water jugs) in the case to make temp — a sign something is off.  *(id: RI1wD7nyGL4)*
- To relocate a duct washing out a case, coordinate with the store to use their lift during the day once the project is over (service mode), rather than forcing a night AC-contractor call.  *(id: RI1wD7nyGL4)*
- Upsize duct nearest the equipment (return riser, filter-back grille) - biggest impact, and you can't meaningfully hurt a return by making the trunk bigger (ACCA Manual D).  *(id: gZQqjXhuMTI)*
- Bigger filter cabinet slows air over the media = filter lasts longer, catches more, lower pressure drop, longer motor life, better IAQ - one move helps efficiency, longevity, capacity and air quality.  *(id: gZQqjXhuMTI)*
- Downsizing equipment (e.g. 5-ton to 3.5-4) instantly right-sizes undersized duct; if the half-ton short shows on the hottest days, add attic insulation rather than upsizing back.  *(id: gZQqjXhuMTI)*
- Flow nitrogen (barely, ~5 SCFH; if it blows the last joint you're using too much/pressurizing) and pull/hold a deep vacuum - it prevents plugged TXVs, filter dryers and compressor issues in the POE-oil era. Purge before pressurizing.  *(id: gZQqjXhuMTI)*
- Stay Brite 8 stays below the copper-oxide level so you skip nitrogen while brazing, but still purge with nitrogen.  *(id: gZQqjXhuMTI)*
- The Solo high-resolution auto-zeroing manometer measures house pressures; the multiprobe doubles as a magnetic static-pressure probe through insulation.  *(id: _oJOBSJW0kA)*
- Add return-air pathways (transfer grilles/jumper ducts) to bedrooms so closed doors don't pressurize the room and depressurize the house.  *(id: _oJOBSJW0kA)*
- Prefer bringing in outdoor air via a dehumidifier or ERV rather than through imbalanced pressures pulling air through wall cavities.  *(id: bj962pMF1-Q)*
- Cover furniture, couches, artwork before an Aeroseal job since the fog can settle if it doesn't find a leak fast enough.  *(id: bj962pMF1-Q)*
- Lower CFM/ton runs a colder coil with longer dwell time = more moisture removal (why the Gulf Coast uses 350 CFM/ton).  *(id: tXFHPWkUAOA)*
- Vane anemometers measure volume (unchanged by density); to hit a fixed mass flow you must raise the volume flow at altitude.  *(id: tXFHPWkUAOA)*
- Put a Testo 405i vane anemometer on a selfie stick/PVC to read register velocity via the app without measuring CFM.  *(id: Sz6A9-ihX-g)*
- Bigger supply ducts/registers aren't always better - they lower static but also lower throw; use a large duct with a balancing damper (per Jack Rise) to tune throw and noise.  *(id: Sz6A9-ihX-g)*
- Bring the supply probe a couple feet away from the unit (or to the first register) so air can mix before you read.  *(id: c1LCnU3lO-M)*
- Use good air probes (Bryan favors Testo 605i), not dial probes or infrared guns.  *(id: c1LCnU3lO-M)*
- Use the HVACRschool resources-tab delta T calculator to get in the ballpark, remembering it assumes 400 CFM/ton.  *(id: c1LCnU3lO-M)*
- Set heating airflow so temperature rise lands mid-window (too low = poor comfort; too high = overload trips on a dirty filter).  *(id: 2kgNFetuWKs)*
- Measure total external static with a manometer and use the fan tables; clean the blower wheel before measuring.  *(id: 2kgNFetuWKs)*
- For aftermarket/constant-torque motors, measure airflow directly (duct traverse, TrueFlow grid, or temperature-rise sensible-heat method).  *(id: 2kgNFetuWKs)*
- On a brand-new clean commissioning you can rely on charts + total external static; once dirty or with non-factory motors, direct airflow measurement becomes essential.  *(id: 2kgNFetuWKs)*
- Zero the manometer (via MeasureQuick or by holding the button) before testing - a non-zeroed probe skews everything.  *(id: o6OVAUJXeuU)*
- Test in the airstream: negative in the return (sucking through), positive at the top of the supply, both at the little test ports.  *(id: o6OVAUJXeuU)*
- Get at least a nine-probe deployment into MeasureQuick as a benchmark before doing the full true-flow-grid workup.  *(id: o6OVAUJXeuU)*
- Measure static ABOVE the filter (closer to the blower) - measuring below a clogged filter falsely shows better static.  *(id: Jp2pZydCp28)*
- Insert the static tip pointing against the flow (or crosswise), never sideways.  *(id: Jp2pZydCp28)*
- Put a bigger 4-inch media filter in the return riser (more surface area = less pressure drop, better filtration, longer life) rather than a dense 1-inch filter under the unit.  *(id: Jp2pZydCp28)*
- Tape loose filters in return grilles with masking tape (not duct tape) to stop bypass.  *(id: Jp2pZydCp28)*
- Check equipment settings: Y/G on the correct terminals, a G call in cooling, dehumidification terminal energized - wrong settings on variable-speed equipment cause low airflow.  *(id: x4_FkNNGzFo)*
- Put static-pressure probes in the return and supply to see which side has the higher reading.  *(id: x4_FkNNGzFo)*
- There's no such thing as 'good airflow' - measure it (hot-wire anemometer, flow hood, or best the TrueFlow grid from the Energy Conservatory).  *(id: x4_FkNNGzFo)*
- Use MeasureQuick - it adjusts targets to your indoor/outdoor conditions and suggests other things to check.  *(id: x4_FkNNGzFo)*
- Point the static-pressure probe in the direction of airflow (holes to the side) so you read static, not static+velocity pressure.  *(id: USMxJexJvbo)*
- The app rejects an upside-down TrueFlow grid ('check plate orientation') - it won't give a reading.  *(id: USMxJexJvbo)*
- For double-return systems, put the grid at one grille and block off the other so all system airflow moves through the grid; the correction factor handles it.  *(id: USMxJexJvbo)*
- Set airflow first (for the climate's dehumidification target), then set refrigerant charge.  *(id: USMxJexJvbo)*
- The diagnostic screen is 'training wheels' - over time you'll learn what supply/return static should be and can diagnose with just a manometer.  *(id: USMxJexJvbo)*
- Make it a habit to take a pressure reading (or just feel the door) whenever you enter a residential or commercial space to sense predominant positive/negative pressure.  *(id: 27AoOAVSaM0)*
- Set up a reference to outdoor pressure before reading the house-to-outside differential with a precision manometer.  *(id: 27AoOAVSaM0)*
- Seal the mini-split cabinet, penetrations, and even the copper with foil/stretch tape to minimize air-handler leakage (achieved ~5 CFM total).  *(id: DhXYd2Um1uE)*
- Use a canvas/flex connector at the equipment and vibration isolation plus silencers to reduce noise and vibration transmitted to rooms.  *(id: DhXYd2Um1uE)*
- Set the fan tap first (get total system CFM right), then balance individual rooms with opposable-blade dampers, then re-check total.  *(id: DhXYd2Um1uE)*
- Use a laser measuring device (Bosch/Disto, ~$200) that calculates volume as you go to speed up the blower door air-change calculation.  *(id: DpX20OkmgoU)*
- Seal envelope leaks at the source in the attic (fire-rated material and spray foam on top plates/chases), not by gasketing receptacles.  *(id: DpX20OkmgoU)*
- Prioritize air-sealing the lid (attic) first — that's where most leakage is — then crawlspaces; and confirm combustion appliances still draft after sealing.  *(id: DpX20OkmgoU)*
- ZPD can still be used to help present proof of leakage and close a job for the client's benefit — just don't believe it quantifies outside connection.  *(id: 7bXPNva82qc)*
- In climate zone 6, choose a cold-climate variable-capacity heat pump that delivers rated capacity down to -5 to -15°F, or use dual-fuel (gas backup) rather than oversizing.  *(id: OioG8T_zwaA)*
- Replacement motor rule: match name-plate FLA, not more than 25% stronger; after install, check amps with all doors/panels/filters in place — amps up to 10% over name plate is fine, never more than 25% below.  *(id: OioG8T_zwaA)*
- Air-seal the lid (attic) first to permanently reduce load; a single-speed unit still meets Manual S if loads match — don't assume you need VRF.  *(id: OioG8T_zwaA)*
- Use the thermostat 'droop' setting or a 90-minute run-without-satisfy trigger to bring on auxiliary heat instead of a fixed outdoor temperature lockout.  *(id: OioG8T_zwaA)*
- When buying a replacement blower wheel, know you can't state its CFM until it's matched with the housing; specify the CFM needed AT the required static pressure.  *(id: 1X9cXMrWc1o)*
- Total static is the negative inlet-side static (sign changed) added to the positive outlet-side static.  *(id: 1X9cXMrWc1o)*
- Constant-airflow ECMs increase torque/speed as static rises to hold CFM (so amps go up), but you still can't overcome bad duct with any motor.  *(id: 1X9cXMrWc1o)*
- Set the system to highest cooling speed and shut off any fresh-air intake or bypass filter so all airflow goes through the main filter before measuring.  *(id: pYA2xv0cukA)*
- Put the positive tube in the room being measured; use the DG-8 in Pascals for room-pressure and building negative/positive (makeup air) diagnostics.  *(id: pYA2xv0cukA)*
- Install the TrueFlow grid with the arrow oriented for correct airflow direction; the magnet mount makes it easy.  *(id: pYA2xv0cukA)*
- Build a manometer from ~40 cents of vinyl tubing and some water to read inches of water column directly.  *(id: uIXfiuY3i9U)*
- Measure velocity pressure with a pitot tube using a tool that averages a transverse across the duct (air moves at different speeds across the cross-section).  *(id: uIXfiuY3i9U)*
- Locate the air handler centrally ('central air, not corner air') to halve the longest airflow path and cut resistance so everything can be sized smaller.  *(id: uIXfiuY3i9U)*
- 6-inch oval duct is usually not close to a real 6-inch round - size it to the next size up.  *(id: uIXfiuY3i9U)*
- Flex duct is not the devil; it works fine if you upsize it to account for its higher friction.  *(id: uIXfiuY3i9U)*
- In measureQuick always know whether you're looking at ACFM (volume/actual) or SCFM (mass/standard) so you know if you're talking mass flow or volume  *(id: FMSl9qexPRw)*
- measureQuick uses ASHRAE Fundamentals moist-air (Hyland-Wexler) psychrometric equations, not standard-air formulas like Manual D/J/S  *(id: FMSl9qexPRw)*
- Return air density shows at the bottom of measureQuick (e.g. 0.072) - multiply ACFM by it to get pounds, divide by 0.075 to convert to SCFM  *(id: FMSl9qexPRw)*
- Measure pressure drop across the filter with a manometer before and after (polarity doesn't matter - use the differential)  *(id: 4R0V6a6Uz3c)*
- Deeper pleated media increases surface area and lowers pressure drop; bigger + deeper lets you use higher-MERV media and change less often  *(id: 4R0V6a6Uz3c)*
- Carbon/charcoal filters adsorb odors/VOCs but look black (hard to see when dirty) and cheap ones don't last; electrostatic-charge ratings often fade in days  *(id: 4R0V6a6Uz3c)*
- Seal filter doors (thumb gum/tape) to stop bypass air that dirties coils/blowers and draws in moisture; recessed 3-4 inch return-grille filters are a good option  *(id: 4R0V6a6Uz3c)*
- Installers must measure TESP before leaving a system - high static means less airflow, more motor failures, less efficiency  *(id: 4R0V6a6Uz3c)*
- Measure directly above/below the coil with enough distance for mixing, keeping the probe out of the coil's line of sight (cold/hot surface 'looking at' the probe skews it)  *(id: _pD-rRCNv8k)*
- Don't trust delta T when the system is in dehumidification mode or staged down below full speed  *(id: _pD-rRCNv8k)*
- Use JobLink probes with FieldPiece/measureQuick apps to auto-calculate a target delta T that normalizes for capacity, conditions, and estimated airflow  *(id: _pD-rRCNv8k)*
- Don't judge cooling by shooting a supply grille with an infrared thermometer - wrong tool, wrong place, emissivity/distance affected  *(id: _pD-rRCNv8k)*
- Know your available static pressure before designing ductwork - a friction-rate rule of thumb without it is meaningless  *(id: sjZR0bTL1Ig)*
- Use extended performance data (blower + capacity tables), not AHRI ratings, to select equipment; use ACCA speed sheets or manufacturer tools (e.g. Carrier) to convert to your conditions  *(id: sjZR0bTL1Ig)*
- Codes are minimums; ACCA publishes what the code official should ask for (available static pressure, load calc, duct design)  *(id: sjZR0bTL1Ig)*
- A leakier house has a lower SHR (more moisture) and benefits from lower airflow; pair a variable/humidistat strategy (e.g. run 1200 CFM normally, drop to 1000 CFM when humid) for best of both worlds  *(id: sjZR0bTL1Ig)*
- Carrier's 'super dehumidify' mode gives a Y call with no G call to run a very low blower speed; not very practical because the system will likely freeze up if run long.  *(id: M99zS-5yeSs)*
- Enhanced mode starts the blower very slow to pull moisture — desirable in a high-humidity market.  *(id: M99zS-5yeSs)*

## Bryan's characteristic phrases on this topic

- "giving yourself a clean access point it's key to Quality Service take the time"  *(id: Rl2Ej7fdy1U)*
- "closing out a call is everything when it comes to customer service no matter how good of a job you did where they can't see all they care about is how well you put back"  *(id: Rl2Ej7fdy1U)*
- "ducts are Plumbing for air you do not want them leaking"  *(id: IlrHazYv84M)*
- "the enclosure wins every single time"  *(id: IlrHazYv84M)*
- "rule number one is don't blow air on people it makes them angry"  *(id: X2Y1KNFoxug)*
- "you're treating the symptoms not the cause"  *(id: X2Y1KNFoxug)*
- "everything in our industry we have to go back to mass flow"  *(id: 7lEhrcbaeGM)*
- "making measurements is easy. Making them correctly is pretty darn hard"  *(id: ryTchnFMem0)*
- "seven out of 10 systems today do not have correct air flow"  *(id: ryTchnFMem0)*
- "When you have the proper tools the job goes easier."  *(id: HvhaFcc7cLQ)*
- "unless you're testing you're guessing"  *(id: wmJ0QBKEbB8)*
- "velocity problems come from small Ducks not not big"  *(id: wmJ0QBKEbB8)*
- "we want a fairly fixed mass flow rate over the evaporator coil or pounds of air per minute rather than CFM for proper system operation"  *(id: GgvSnm_gqt8)*
- "it was always just you know to stop rocks and bumblebees"  *(id: s4EGvkZPqgo)*
- "you do not want to look at initial cost you want to look at annual cost and you want to look at your TCO or your total cost of ownership"  *(id: s4EGvkZPqgo)*
- "high blood pressure is a silent killer ... that's what happens ... with the airflow"  *(id: wWN2IKAqpy4)*
- "the minus sign just tells you to put it on the return side and the plus side just tells you put on the supply side"  *(id: wWN2IKAqpy4)*
- "air is in fact stuff it takes up space and it has mass and it's actual matter"  *(id: I1jYv-jetNY)*
- "the motor does not see total external ... the blower cares about what it sees right at the blower and that includes your evaporator coil"  *(id: AWecM1MfuEE)*
- "air flow. air flow. air flow. that's the thing that you guys miss most"  *(id: AWecM1MfuEE)*
- "static pressure does not measure air flow it just measures pressure"  *(id: eHzYalJXE88)*
- "the squared thing really kills you"  *(id: eHzYalJXE88)*
- "your static pressure only tells you anything if the system is producing the air flow it's supposed to produce"  *(id: FFYvSwCIYho)*
- "just put in bigger Ducks that's the answer"  *(id: FFYvSwCIYho)*
- "when you compress insulation it ceases to be insulation"  *(id: 3m1eRBXDM5I)*
- "you don't need an air leak to have condensation"  *(id: 3m1eRBXDM5I)*
- "You can't manage what you don't measure"  *(id: y4y1EtgEs9w)*
- "becoming masters of the obvious"  *(id: y4y1EtgEs9w)*
- "think of your homes as a sponge"  *(id: jMTxblZcTzE)*
- "supply leakage sucks and he really sucks because they both start with s"  *(id: jMTxblZcTzE)*
- "stop using air leakage as an energy penalty that's a minor issue"  *(id: jMTxblZcTzE)*
- "if you build it tight you got to ventilate it right"  *(id: jMTxblZcTzE)*
- "a tape measure is slow"  *(id: y_aTNtv_2bM)*
- "that's what value looks like"  *(id: 75Q15TVoazE)*
- "trust the math trust the process"  *(id: -KqmAQgUXY4)*
- "when you have static pressure and air flow, they move in the same direction, but one moves farther than the other"  *(id: NzlsB9R6mbc)*
- "if we're not paying attention to how the equipment is operating and under what conditions, we're going to continue having the same thing and recurring problems over and over again"  *(id: NzlsB9R6mbc)*
- "most of your control happens when it's nearly closed"  *(id: XeanFStDbyY)*
- "ideal tension is the lowest tension at which the belt will not slip at peak conditions"  *(id: rNBt7LN-8ao)*
- "when you have low superheat low suction pressure low head pressure the flow of air is not good it's measured"  *(id: lvMjm3YwUY8)*
- "you need to become the doctor the house doctor"  *(id: lvMjm3YwUY8)*
- "but did you did you measure it"  *(id: lvMjm3YwUY8)*
- "I'll take a 1-in wide trap with a 6-in depth over a 6-in wide 1-in trap"  *(id: LGgET3gRY20)*
- "it takes .24 btus to heat one pound of air at sea level one degree fahrenheit so that's how we get 1.08"  *(id: aRJH-wJZ1Gs)*
- "by having four filters instead of one we have a lot more filter surface area and we're able to move a lot more air and filter a lot more air"  *(id: Y7eL2OAnqc8)*
- "the closer you get to the blower the higher your pressures are going to be"  *(id: wdnaeZkstXI)*
- "if you don't measure you're just guessing"  *(id: 5eiv-0518mQ)*
- "nothing happens until you sell something"  *(id: 5eiv-0518mQ)*
- "the biggest variation in measurements wins"  *(id: 5eiv-0518mQ)*
- "if you were to just do volts times amps that would be VA not wattage"  *(id: 8ANRxjC6xs8)*
- "if we're not testing we're just guessing"  *(id: ddhQrxuIbUI)*
- "light in the loafers"  *(id: hCZEg_DGCf0)*
- "if we don't pay attention to the V in HVAC, you're an HAC in my opinion"  *(id: YUjv96bbQOM)*
- "One CFM out equals 1 CFM in."  *(id: YUjv96bbQOM)*
- "60% roughly of human comfort is comes from radiant heat"  *(id: YUjv96bbQOM)*
- "It's the whole house air filter. It's dirty."  *(id: YUjv96bbQOM)*
- "every CFM that goes out brings one CFM in it's a double whammy situation you lose capacity and you increase the load"  *(id: FtPWajjm1Q0)*
- "sensible BTUs are cheap latent BTUs are expensive"  *(id: GRhAWA4tz1I)*
- "mastic is not designed to be our seal... mastic holds our mechanical seal in place"  *(id: iygU_hFM9Os)*
- "static is not a measurement of air flow. Static is a measurement of pressure"  *(id: a9tX40eOJfw)*
- "Taking a measurement is better than taking no measurement"  *(id: a9tX40eOJfw)*
- "static pressure alone is reliant on the air flow output of the blower"  *(id: gZQqjXhuMTI)*
- "money buys you a really good air conditioner. It does not buy you me solving the issue"  *(id: gZQqjXhuMTI)*
- "dehumidification is a function of evaporator temperature and run time. Full stop."  *(id: gZQqjXhuMTI)*
- "the mechanical system and the house fighting each other instead of working in unison"  *(id: _oJOBSJW0kA)*
- "You can't fudge numbers. The proof is in the data. The data is the numbers."  *(id: o6OVAUJXeuU)*
- "don't rely on yesterday's zero"  *(id: Jp2pZydCp28)*
- "it does come down to the way that you install it that's what matters more"  *(id: DhXYd2Um1uE)*
- "the duct we don't consider is the envelope"  *(id: DpX20OkmgoU)*
- "if you watch the house very carefully and it doesn't implode then the airf flow in equals the airf flow out"  *(id: DpX20OkmgoU)*
- "maybe it helps you with the cell like i said but in reality from a technical standpoint if you've begun to believe that you're just playing yourself"  *(id: 7bXPNva82qc)*
- "let the equipment suffer first don't break the house"  *(id: OioG8T_zwaA)*
- "do you even load Cal bro"  *(id: OioG8T_zwaA)*
- "Air is the load. So, if I don't have the proper load on it, then that motor's not going to get the right amount of air to keep it from overheating."  *(id: 1X9cXMrWc1o)*
- "It's not a race, it's a traffic jam."  *(id: uIXfiuY3i9U)*
- "It's called central air, not corner air."  *(id: uIXfiuY3i9U)*
- "You can't manage what you can't measure."  *(id: uIXfiuY3i9U)*
- "you could have a 20 degree delta T and the system may not be working properly at all"  *(id: _pD-rRCNv8k)*
- "a pound of air weighs a pound"  *(id: sjZR0bTL1Ig)*

## Guest wisdom on this topic

- **Corbett Lunsford:** The enclosure is the most important system and wins every time; HVAC keeps taking the heat for comfort/smell/noise problems that are really enclosure problems.  *(id: IlrHazYv84M)*
- **Corbett Lunsford:** Metrics govern everything (fitness trackers, sports stats); without measured data you can't stand up to someone who has more information than you.  *(id: IlrHazYv84M)*
- **Jack Rise:** Friction rate (not static pressure) drives duct sizing: available static x 100 / total effective length, entered into a ductulator on the critical path.  *(id: X2Y1KNFoxug)*
- **Jack Rise:** Register face velocity mixes room air by entraining 10-20x as secondary air; returns have almost no effect on room air movement.  *(id: X2Y1KNFoxug)*
- **Jim Bergmann:** Everything comes back to mass flow - heat transfer to a hot-wire depends on the mass (pounds) of air, not the CFM, so density-dependent tools mislead if uncorrected.  *(id: 7lEhrcbaeGM)*
- **Jim Bergmann:** An AC removes absolute humidity but a duct probe shows higher RELATIVE humidity because the cold air is compact and near saturation.  *(id: 7lEhrcbaeGM)*
- **Jim Bergmann:** A fan moves constant CFM independent of density but variable mass flow; evaporator coils are actually rated by mass of air, not CFM.  *(id: ryTchnFMem0)*
- **Jim Bergmann:** If you truly understand airflow you'll be one of the most sought-after techs, because 7 of 10 systems have incorrect airflow that goes unresolved.  *(id: ryTchnFMem0)*
- **Jesse:** Demonstrates that an N-coil shifted right starves a third of the coil; push it left where the drain pan hangs over for proper airflow.  *(id: PjWScoD3NH4)*
- **Bert:** Whenever you see a front-facing unit, look at it - the back insulation pulling into the blower and blocking the intake is a super common problem.  *(id: HvhaFcc7cLQ)*
- **Eric Kaiser:** Unless you're testing, you're guessing; pretty ductwork can perform poorly and ugly ductwork can perform well - measured performance matters more than appearance.  *(id: wmJ0QBKEbB8)*
- **Sam Myers:** Static regain (pressure higher farther from the fan when going small-to-large duct) and duct leaks acting as a pressure relief mean you must re-measure after changes; make changes anywhere and it changes everything downstream.  *(id: wmJ0QBKEbB8)*
- **Lee Andrews:** Filters were never meant to be IAQ devices - originally just to 'stop rocks and bumblebees' and protect the blower; the industry is now leaning toward human health.  *(id: s4EGvkZPqgo)*
- **Lee Andrews:** Don't look at initial cost - look at annual cost and total cost of ownership.  *(id: s4EGvkZPqgo)*
- **Joe Henderson:** You want the return static lower than the supply so return air is quiet ('low and slow') while the supply keeps velocity/throw - a rule he derived from field measurements, not a textbook.  *(id: wWN2IKAqpy4)*
- **Joe Henderson:** Manual D is the standard for duct design; Manual ZR was written because zone systems were screwed up by duct design, not the zoning itself.  *(id: wWN2IKAqpy4)*
- **Ty:** You can visibly see the temperature split change just by sealing the whole air handler - proof of how much air the straws pull.  *(id: AWecM1MfuEE)*
- **Matt Bruner:** Adopt a doctor mentality - tell the homeowner the hot room won't be fixed by a newer box, quote the real fix (~$3-4k), and let them decide.  *(id: eHzYalJXE88)*
- **Matt (referenced):** A bigger return budgets static so you can take a little more on the supply side in your design.  *(id: FFYvSwCIYho)*
- **Joe Medosch:** Homes are a sponge: indoor pollutants stick to every surface, and indoor air can be hundreds of times worse than outdoor air. The EPA regulates outdoor air, not the air inside your home.  *(id: jMTxblZcTzE)*
- **Joe Medosch:** The number one contractor who can change occupants' lives on the first visit is the HVAC contractor, by upgrading filtration.  *(id: jMTxblZcTzE)*
- **Bill Spohn:** Use data and test instruments (blower door, pressure pan) to back up your recommendations, the same way you use digital gauges on an AC system.  *(id: jMTxblZcTzE)*
- **Stephen:** On retrofits stuck above ~1 inch static, high negative pressure at the trap pulls water into the pan and overflows the secondary switch, suggesting a deeper trap is needed.  *(id: zOpdAbQuBXM)*
- **Bo Outlaw:** Prior techs did only what they were called for and never mentioned obvious problems they exposed while getting to the job; customers just want the honest 'menu' to choose from.  *(id: 75Q15TVoazE)*
- **Ed Janowiak:** Predictable results come from following the rules; a duct system is fairly forgiving on sizing but people go to great lengths to do things wrong (e.g., all-same-length 6-inch flex is not self-balancing).  *(id: -KqmAQgUXY4)*
- **Ed Janowiak:** Filter manufacturers publish MERV/pressure drop at velocities we rarely hit (~118-295 fpm); a 14x25x1 opening on a 3-ton drive approaches 600 fpm and 0.3-0.4 drop, so you need double/triple filter surface area.  *(id: -KqmAQgUXY4)*
- **Elliot:** Stretch and fully expand the flex before strapping so the insulation doesn't keep expanding and cause sagging.  *(id: hz-R4InhRBM)*
- **Adam Mufich:** Commissioning changes everything — you can build beautiful straight sheet metal, but if you don't measure how the equipment operates you'll get your butt handed to you; backing into TESP from duct pressures changed his install outcomes.  *(id: NzlsB9R6mbc)*
- **Jim Bergmann:** Return leakage adds latent load and robs sensible cooling, which is what the (sensible-sensing) thermostat controls, so run time and energy use climb.  *(id: lvMjm3YwUY8)*
- **Chris Hughes:** Sell diagnostics with a doctor's confidence: the MeasureQuick report is your objective 'lab result,' delivering perceived value (like a doctor's chart app), versus a vague 'everything looks fine.'  *(id: lvMjm3YwUY8)*
- **Chris Hughes:** Run the business by two numbers: your gross revenue target and whether it's reasonable to ask that of your field techs -- get those from your CPA.  *(id: lvMjm3YwUY8)*
- **Neil Comparetto:** Four filters instead of one give much more surface area so the box fan moves and filters far more air despite the restriction.  *(id: Y7eL2OAnqc8)*
- **Neil Comparetto:** Vertical mounting avoids blowing floor pollutants back into the breathing zone the way horizontally-mounted fans can.  *(id: Y7eL2OAnqc8)*
- **David Richardson:** We went from high-pressure sales to static-pressure sales - present the measurements and let the customer decide.  *(id: 5eiv-0518mQ)*
- **David Richardson:** Progress, not perfection - perfectionism keeps you staring at the target instead of shooting the arrow; you improve by doing.  *(id: 5eiv-0518mQ)*
- **David Richardson:** Focus on one thing (the lion-tamer/chair analogy) - overloading a customer makes them freeze and default to price.  *(id: 5eiv-0518mQ)*
- **John Pastorello (cited):** Founder of Refrigeration Technologies uses EvapPlus (pH-neutral enzyme cleaner) at a 20:1 ratio around his own house.  *(id: gToHQvORNHs)*
- **Steve Rogers:** If airflow doubles the static pressure quadruples; +50% airflow more than doubles static - this is why upsizing to cover load is a bad idea.  *(id: cGT6ZA3bcIg)*
- **Chris Hughes:** Strip away the math so the salesperson can focus on the customer's emotions; perfectionists who go home to do the math lose more jobs than those who close at the kitchen table.  *(id: cGT6ZA3bcIg)*
- **Steve Rogers:** TrueFlow can advise how much electric resistance heat can run simultaneously with the heat pump safely, letting you back down tonnage and add Delta.  *(id: cGT6ZA3bcIg)*
- **Eric Kaiser:** The + and - on static readings only tell you which side of the blower you measured; drop them and add the two numbers together for external static.  *(id: ddhQrxuIbUI)*
- **Eric Kaiser:** Static pressure is like taking a human's blood pressure - record it on the duct so any change (smashed duct, closed registers, hole in a duct that drops it) is immediately visible on a return visit.  *(id: ddhQrxuIbUI)*
- **Eric Kaiser:** They got what they paid for - it's not your responsibility to make the customer's choices; tell them it's not done the best way, give the benefit and the price, and let them decide.  *(id: ddhQrxuIbUI)*
- **Eric Kaiser:** Always be willing to change your views when presented with good information; if you won't look at something else, you stay stuck.  *(id: YUjv96bbQOM)*
- **Eric Kaiser:** If you ignore the V (ventilation) in HVAC you're just an HAC; dirty black attic insulation is the whole-house air filter that never gets changed.  *(id: YUjv96bbQOM)*
- **Eric Kaiser:** You may have to redefine a home's pressure boundaries for comfort, but ducts run outside the shell expand the pressure envelope, so seal ducts tightly and control where air enters and leaves.  *(id: YUjv96bbQOM)*
- **Adam:** Duct leakage to outside is a tough concept to read about but becomes clear once you watch/do it — reading alone makes it a mountain.  *(id: FtPWajjm1Q0)*
- **Bert:** A full single-head ductless maintenance with the bib kit, including pulling the blower wheel, is about an hour to an hour and a half.  *(id: DHWcSYPLLVw)*
- **Bert:** The whole inner layer start-to-finish is the most crucial, most-likely-to-be-wrong connection; you can pile mastic on the outside and strap it poorly and still leak air everywhere if the inner seal is bad.  *(id: iygU_hFM9Os)*
- **Sam (Retrotec):** When there's more supply leakage than return, the house goes negative and pulls in hot humid air; the mechanical system and house end up fighting instead of working in unison.  *(id: _oJOBSJW0kA)*
- **Sean Harris:** Aeroseal is not a band-aid; he turns down work where ducts should be replaced or are undersized because sealing makes undersizing worse.  *(id: bj962pMF1-Q)*
- **Chris:** TrueFlow gives you the confidence and a homeowner report to have the hard duct conversation - you're no longer 99% sure, you're 110% because a manufacturer that studies airflow is standing with you  *(id: USMxJexJvbo)*
- **Genry Garcia:** The problem is often more serious than expected; pay attention to little details on every comfort/humidity call.  *(id: 27AoOAVSaM0)*
- **John Semmelhack:** Specify a heat pump water heater for the best combination of efficiency, low operating cost, and safety — and it helps dehumidify.  *(id: DhXYd2Um1uE)*
- **Joe Medosch:** The largest duct system in the house is the envelope, and sealing it (not swapping windows) is the biggest comfort/energy payoff.  *(id: DpX20OkmgoU)*
- **Genry Garcia:** If it helps you sell the job that ultimately benefits the consumer (lower bills, comfort), using ZPD is fine — but don't fool yourself about its technical meaning.  *(id: 7bXPNva82qc)*
- **Russ King:** Three Bears framing: mama-bear (cooling-dominated), papa-bear (heating-dominated), baby-bear (balanced) climates — a heat pump has a fixed heating:cooling relationship you must fit to the climate; use the new Manual S guidance and variable-speed to fit.  *(id: OioG8T_zwaA)*
- **Russ King:** Do a room-by-room load calc if you want to size ducts (a room that's 10% of the load gets 10% of the airflow); if you're not doing load calcs you're not measuring at all — you can't call yourself a professional.  *(id: OioG8T_zwaA)*
- **Chris Hughes:** Maintain airflow over static — let equipment fail before the house grows mold; heat pumps don't freeze at 32°F, so don't set the swap-over there.  *(id: OioG8T_zwaA)*
- **Rick Streacker:** Think of blower load as 'boxes of air' (cubic feet) — a half-horsepower motor is designed to move a certain number; restrict the air and it moves fewer boxes, so it's underloaded.  *(id: 1X9cXMrWc1o)*
- **Alex Meaney:** Residential duct design feels like working backwards: pick your fixed blower, subtract friction of coil/filter to get available static pressure, add up fitting equivalent lengths, then compute the friction rate to size ducts.  *(id: uIXfiuY3i9U)*
- **Alex Meaney:** The name-plate airflow on the unit is garbage; use the external static pressure table in the data to find actual airflow at a given speed.  *(id: uIXfiuY3i9U)*
- **Jim Bergmann:** One BTU = heat to raise one pound of water one degree F; everything we do is about pounds of air, so we're cooling the mass of the air not the volume of it  *(id: FMSl9qexPRw)*
- **Jim Bergmann:** ECM motors work off RPM and torque; as air gets lighter (less torque needed) they speed up to move more actual CFM and hold standard CFM constant  *(id: FMSl9qexPRw)*
- **Ed Janowiak:** The sensible heat ratio of the structure dictates our airflow - it's third-grade math and sixth-grade science, and following it puts you in the top 10% of the industry  *(id: sjZR0bTL1Ig)*
- **Ed Janowiak:** Manual J is not a standalone product - if someone explains it without at least touching Manual S they're doing you a disservice; it's an all-or-nothing design series, don't cherry-pick  *(id: sjZR0bTL1Ig)*

## Episodes in this compendium

| Title | Video id | Guests |
|---|---|---|
| #BertLife - Flex Duct Repair Terror | Rl2Ej7fdy1U | Bert (Elijah Burt) |
| (Podcast) Blower Door Testing, Building Performance & More w⧸ Corbett Lunsford | IlrHazYv84M | Corbett Lunsford |
| (Podcast) Common Duct Design Mistakes w⧸ Jack Rise | X2Y1KNFoxug | Jack Rise |
| (Podcast) Measuring Air Flow - Air Density and Direct Air Flow Measurement Part 2 w⧸ Jim Bergmann | 7lEhrcbaeGM | Jim Bergmann |
| (Podcast) Measuring Air Flow - Static ⧸ Capacity & ECM Motors Part 1 w⧸ Jim Bergmann | ryTchnFMem0 | Jim Bergmann |
| A Common Cased Coil Issue | PjWScoD3NH4 | Jesse |
| A Commonly Missed Airflow Issue w⧸ Bert | HvhaFcc7cLQ | Bert, Jessica |
| A Duct Up Situation with Sam Myers and Eric Kaiser | wmJ0QBKEbB8 | Sam Myers, Eric Kaiser |
| ACFM vs SCFM 3D | GgvSnm_gqt8 | (solo) |
| Air Filters, They are More Complex Than You Knew w⧸ Lee Andrews | s4EGvkZPqgo | Lee Andrews |
| Air Flow Diagnostics w⧸ Joseph C Henderson | wWN2IKAqpy4 | Joseph 'Joey' C Henderson |
| Air Is Stuff | I1jYv-jetNY | Jeff |
| Air Sealing and Static Pressure Diagnostics | AWecM1MfuEE | Ty (Branaman), Adriel, Eli |
| Airflow & Static Pressure with Matt Bruner & Bryan Orr | eHzYalJXE88 | Matt Bruner |
| Airflow Before Charging | FFYvSwCIYho | Matt |
| Better Duct Installation Practices - Kalos Meeting | 3m1eRBXDM5I | (solo) |
| Blower Door Test w⧸ Chris Hughes | i4YuqUPmwHs | Chris Hughes, Dustin Cole, Adam |
| Boost Your HVAC Ticket Size： Deploying Static Pressure Probes with MeasureQuick | y4y1EtgEs9w | (solo) |
| Building Science 101 for HVAC Contractors w⧸ Bill Spohn and Joe Medosch | jMTxblZcTzE | Bill Spohn, Joe Medosch |
| Cutting & Installing a Rectangle Duct Connection | y_aTNtv_2bM | (solo) |
| Delivered Capacity Basics - Kalos Meeting | EJVRhznC_Ts | (solo) |
| Discussing Ducts Types and Tips | VDJotlJj3Mo | (solo) |
| Drain Traps & Static： Q&A with Bryan Orr | zOpdAbQuBXM | Stephen |
| Duct DISASTER at an NBA Players Home | 75Q15TVoazE | Bo Outlaw |
| Duct Design for Great Results w⧸ Ed Janowiak (ACCA) | -KqmAQgUXY4 | Ed Janowiak |
| Duct Prep Tips and Tricks with Elliot | hz-R4InhRBM | Elliot |
| Ductboard Plenum Replacement： Measuring, Cutting & Installing | DgxhPFfPlEs | (solo) |
| Fan Law 2 for Techs with Adam Mufich | NzlsB9R6mbc | Adam Mufich |
| Flow Hood： How to Properly Balance an HVAC System | XeanFStDbyY | (solo) |
| HVAC Belt Tension | rNBt7LN-8ao | (solo) |
| HVAC Commissioning on Steroids w⧸ Jim Bergmann & Chris Hughes | lvMjm3YwUY8 | Jim Bergmann, Chris Hughes |
| HVAC Condensate Drain Troubleshooting： Traps, Vents & Static Pressure | LGgET3gRY20 | (solo) |
| Heat Rise Airflow Calculation | aRJH-wJZ1Gs | (solo) |
| High Quality DIY Box Fan Air Purifier ＂Comparetto Cube＂ | Y7eL2OAnqc8 | Neil Comparetto |
| Highwall Ductless Blower Wheel Cleaning | 2VvoER81-co | (solo) |
| How to Build a Sheet Metal Coil Case From Scratch | hgFafh_AFLU | (solo) |
| How to Checkout Blower Settings Using a Manometer | wdnaeZkstXI | (solo) |
| How to Clean an Air Conditioner Blower Wheel (Fan Coil Blower Pull and Clean in 3D) | YwFkhTqgazM | (solo) |
| How to Confidently Create a Duct Renovation Scope of Work w/ David Richardson | 5eiv-0518mQ | David Richardson |
| How to Fabricate a Metal Supply Plenum From Scratch | EgFAL_z7P2o | (solo) |
| How to Make a Leak Free Canvas Duct Connector | gE3Dnn0u3kA | (solo) |
| How to Make a Metal Duct Transition in the Field | rO4yqiWjOtU | (solo) |
| How to Make an Indoor Air Cleaner the Cheap and Easy Way | gToHQvORNHs | (solo) |
| How to Measure Air Filter Static Pressure Drop | zkPcIKKGwwc | (solo) |
| How to Measure CFM w/ The Testo 420 Flow Hood | kAjT-VujA6I | Sean, Mike |
| How to Measure Fan Efficacy (Blower Performance) | 8ANRxjC6xs8 | (solo) |
| How to Measure Total External Static Pressure (TESP) | 6uMqw69XkRw | (solo) |
| How to Measure Total Static Pressure w⧸ Testo 510i | E3-lpHKCjiQ | (solo) |
| How to Predict Air Flow Issues in the Sales Process | cGT6ZA3bcIg | Chris Hughes, Steve Rogers |
| How to Use a Blower Door (Como usar el Blower Door) | 0YnhnPTkyU0 | (solo) |
| How to use Static Pressure to Measure and Set Air Flow | ddhQrxuIbUI | Eric Kaiser |
| Impact of Airflow on Refrigerant Measurements and Performance | hCZEg_DGCf0 | (solo) |
| Installing a Rectangle to Round Transition into an Existing Metal Duct | md1OyUs-tcA | (solo) |
| Is a House Really just a Big Duct System？ w⧸ Eric Kaiser | YUjv96bbQOM | Eric Kaiser |
| Make Field Transitions on Prefabricated Metal Duct | UKdV16U6JrI | (solo) |
| Measuring Air Velocity using Testo 410i | WTEoz7P3QDM | (solo) |
| Measuring Duct Leakage To Outside | FtPWajjm1Q0 | Chris Hughes, Adam, George |
| Measuring In-Duct Airflow with the Testo 405i | 29sNEDcQJTc | (solo) |
| Mini-Split Cleaning & Maintenance | GRhAWA4tz1I | (solo) |
| MiniSplit Air Conditioning Cleaning Practices | DHWcSYPLLVw | Bert |
| Practical Training on Manometers | QHHMC5K2moU | (solo) |
| Pro Tips for Perfect Flex Duct to Duct Board Connections with Bert | iygU_hFM9Os | Bert |
| Proper Use of Manometers for HVAC Technicians | a9tX40eOJfw | (solo) |
| Rack Refrigeration Cycle Part 11 - Evaporator Airflow | RI1wD7nyGL4 | Matthew Taylor |
| Residential AC System Installation | gZQqjXhuMTI | (solo) |
| Retrotec Duct Leakage & House Pressure Demo | _oJOBSJW0kA | Sam |
| Sealing Ducts From the Inside w⧸ Sean Harris | bj962pMF1-Q | Sean Harris |
| Short 10 - Air Has Weight and Takes up Space | tXFHPWkUAOA | (solo) |
| Short 16 - Air Velocity is Useful | Sz6A9-ihX-g | (solo) |
| Short 2 - Delta T | c1LCnU3lO-M | (solo) |
| Short 4 - Blower Taps (Audio Only) | 2kgNFetuWKs | (solo) |
| Static Pressure Fundamentals | o6OVAUJXeuU | Dre |
| Static Pressure and Manometer Basics | Jp2pZydCp28 | Bert |
| Symptoms of Low Evaporator Airflow | x4_FkNNGzFo | (solo) |
| System Airflow Measurement w/ TEC TrueFlow | USMxJexJvbo | Chris, Steve |
| Testing Home Pressure Imbalance w⧸ Genry Garcia (Spanish) | 27AoOAVSaM0 | Genry Garcia |
| Testing out a High Performance HVAC Installation | DhXYd2Um1uE | Neil Comparetto, John Semmelhack |
| The Duct We Tend to Forget w⧸ Joe Medosch | DpX20OkmgoU | Joe Medosch |
| The Flaw With Zonal Pressure Diagnosis | 7bXPNva82qc | Genry Garcia |
| The Great Heat Pump Revolt of 2026 and How To Avoid It with Steve Rogers, Russ King and Chris Hughes | OioG8T_zwaA | Steve Rogers, Russ King, Chris Hughes |
| The Impact of Static Pressure on Fan and Blower Motors w⧸ Rick Streacker | 1X9cXMrWc1o | Rick Streacker |
| Total Furnace Airflow and Precision Manometer w⧸ TEC TrueFlow | pYA2xv0cukA | (solo) |
| Understanding Airflow: David Bowie, a Used Car Lot, and a 40 cent Tool with Alex Meaney | uIXfiuY3i9U | Alex Meaney |
| Volume Flow Rate vs Mass Flow Rate w⧸ Jim Bergmann | FMSl9qexPRw | Jim Bergmann |
| What Air Filter is The Best？ | 4R0V6a6Uz3c | Sam, Jessica |
| What Should the Air Delta T be？ (Air Temperature Split) | _pD-rRCNv8k | (solo) |
| What is Proper System Airflow | sjZR0bTL1Ig | Ed Janowiak |
| When a Variable Blower Runs Too Slow | M99zS-5yeSs | (solo) |

## Change log

- 2026-07-08: Initial extraction from 88 episodes (parallel-subagent structured extraction, Opus).
