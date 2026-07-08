# Bryan Orr HVAC School - Compendium: Metering Devices

**Version:** v1.0  
**Date:** 2026-07-08  
**Source episodes:** 28 (of 959 total in corpus)  
**Cross-references (most co-occurring topics):** Refrigeration Cycle (24), Diagnostics Methodology (16), Compressor (5), Electrical and Controls (4), Tools and Instruments (3), Vacuum and Recovery (2)

**Attribution:** Synthesized from Bryan Orr's public HVAC School podcast for SnapAI internal reference only. Attribute Bryan Orr / HVAC School (hvacrschool.com) in any downstream use; do not imply endorsement.

---

## Overview - scope of Bryan's teaching on this topic

This compendium aggregates 28 episodes whose primary emphasis is **Metering Devices**. Content is extracted verbatim-faithful from the transcripts; every item cites its source episode by title and YouTube video id. No numbers or claims were invented at merge time.

Dominant secondary threads in this bucket: Refrigeration Cycle (24), Diagnostics Methodology (16), Compressor (5), Electrical and Controls (4), Tools and Instruments (3), Vacuum and Recovery (2), Comfort and Latent (2), Guest Wisdom (1).

## Key technical points (Bryan's core teaching, by episode)

### (Podcast) TXV Operation, Diagnosis, and Failure w⧸ Jamie Kitchen  
*Source id: B7PLADtN06c*

- A TXV is NOT a constant-superheat valve. It requires superheat to INCREASE to open against the spring, so superheat is an indicator of evaporator load - higher under high/latent load, lower when near-satisfied. It holds much closer superheat than a piston but never constant.
- Three superheats: static (factory) is the superheat needed just to overcome the spring before the valve starts to open; opening is the extra degrees above static to reach rated capacity; operating (what you measure at the evaporator outlet) equals static plus opening. Turning the adjustment screw changes the STATIC setting, not a maintained value.
- The TXV is rarely the actual fault - it is usually the collector of upstream problems (contamination/plugged screen, no nitrogen while brazing, a bulb cracked by vibration, or a diaphragm/bulb ruined by overheating during brazing). Diagnose systematically: confirm charge with condenser subcool, then determine a load (airflow) problem vs a refrigerant-flow problem via superheat.
- Use an externally equalized valve on any multi-circuit (distributor) evaporator, because the distributor's pressure drop (up to ~20 psi) makes an internally equalized valve chronically under-feed; and never seal off the external equalizer line.

### Capillary Tube Repair and Brazing Class  
*Source id: DtINXanblJw*

- A capillary tube meters refrigerant by friction: high-pressure liquid collides with the porous inner copper wall along the tube's length, creating friction and heat, choking and dropping the pressure until a two-phase change turns it into a low-pressure saturated vapor.
- Inner diameter (not outer diameter) determines the refrigerant flow; outer diameter minus inner diameter gives the wall thickness, which varies by application (thicker for high-pressure, high-vibration systems like 410A).
- When repairing or rebrazing a cap tube, match the inner diameter and overall length; trimming a couple inches on a ~10 ft line is fine, but cutting it in half and reconnecting changes the metering drastically.

### Common Refrigeration TXV Issue  
*Source id: CvqE7RbYL-g*

- On a wet produce case not making temperature, two low-hanging-fruit checks are the inlet screen and the TXV power head; once the power-coating on the power head starts coming loose the integrity is compromised and it's a matter of time before it loses its charge and rusts out.

### Demystifying the Thermostatic Expansion Valve w⧸ Jim Jansen  
*Source id: RIa2Xhzp5qs*

- A TXV's only job is to control superheat where the bulb is located; only three forces tell it what to do: bulb pressure opens it, spring pressure closes it, and equalizer (evaporator) pressure closes it.
- Adjusting the valve only adds/subtracts preload on the closing spring (changing superheat), not capacity; capacity is set by port diameter, pin angle and push-rod length.
- An externally equalized valve is mandatory when a distributor is present because of the extra pressure drop, and you can always substitute an external for an internal but not vice versa.

### Diagnosing a Failed TXV  
*Source id: 9Hz0af0fnsg*

- A failing-closed TXV always causes high superheat; never condemn a TXV with normal or low superheat (that's usually airflow or overcharge).
- A failing-closed TXV also gives a low temp split with a good/normal-to-high subcool and normal-to-high head pressure, because there's enough refrigerant in the system.
- Always check airflow first before condemning a TXV; take all readings (split, superheat, suction, head, subcool) rather than assuming from one or two.

### Does a TXV Shut under Vacuum？  
*Source id: r18UybHTvv4*

- A TXV (even a hard-shutoff/non-bleed valve) goes wide open under vacuum or with no refrigerant in the system because the bulb force above the diaphragm overcomes the absent external-equalizer force.
- With the system off you also get a warm suction line (high bulb pressure) and no system pressure to work against, which drives the valve open.
- This is why the one-hose vacuum setup works well: pulling on the suction line while the micron gauge reads on the liquid line still pulls through a wide-open valve, provided the suction-line Schrader is removed.

### EEV Troubleshooting in 3D： A Guide for HVAC Techs  
*Source id: fd0kGz0XckE*

- An EEV is a metering device that modulates its orifice for constant superheat using a PCB reading entering/leaving line sensors and sending pulses to energize windings; unlike a TXV it doesn't rely on pressures. (Video covers unipolar HVAC EEVs, not bipolar commercial-refrigeration ones.)
- Two construction types: an indirect stepper-motor EEV (permanent magnet + iron teeth, ~480 pulses to fully open/close, common at the outdoor unit) and a direct/gear-driven EEV (gear train for more torque and finer control, ~2000 pulses, sometimes 0-3000 or 6000, common in indoor VRV/VRF units).
- Troubleshoot electrically first: power off, unplug the EEV from the PCB, ohm each coil wire to its common (e.g. one red common, ~45 ohms +/-10%); low or open reading = replace the valve. Then check for a mechanical stick with a manual actuator or EEVMate.

### Electronic Expansion Valves (EEV) w⧸ Jamie Kitchen (Podcast)  
*Source id: ibZN1vzyPHU*

- A metering device's primary job is to create a pressure drop so you can control the temperature at which the refrigerant boils; the application's required pressure drop (wine cooler ~50F evap vs low-temp refrigeration -10 to -20F) dictates the device, and a fixed orifice/cap tube is ideal only where high-side and load conditions are stable.
- A TXV opens roughly linearly with superheat, but an evaporator's minimum stable superheat is a curve that changes with capacity; a straight line against a curve forces excess superheat at high and low load, so you can't just dial a TXV down or it hunts.
- An EEV uses algorithms to continuously track just to the dry side of the minimum stable superheat curve across all loads, maintaining the lowest stable superheat automatically — lowering average evaporator temperature for better dehumidification at high load and, by allowing a slightly warmer saturation, lowering compression ratio to save energy.

### Finding Target Superheat  
*Source id: Xuy4mtdXlRI*

- Target superheat is where superheat should be for a fixed-orifice/piston system; you must know the target before hooking up or the reading test isn't meaningful. Superheat protects the compressor from flooding (liquid) and confirms the evaporator is being fed efficiently.
- Compute target superheat from outdoor dry-bulb (sensible heat) and return wet-bulb (accounts for latent/moisture load) using a target superheat calculator, slider, manufacturer chart, or MeasureQuick (enter tonnage, set piston, probe on outdoor air).
- Target superheat is variable because outdoor temperature changes the liquid pressure/flow through the fixed orifice — as outdoor temp rises, more refrigerant is pushed through the same piston hole, so the target superheat number actually goes down (counterintuitive).

### HVACR Metering Device Basics  
*Source id: qV-DIqIxPGk*

- The metering device is a pressure dropper: the compressor pressurizes refrigerant before the condenser to get heat out, the metering device drops pressure before the evaporator to get heat in (drop pressure = drop temperature).
- There are four common types: capillary tubes and pistons (fixed orifices) and TXVs and electronic expansion valves (modulating valves that measure superheat at the evaporator outlet to keep from feeding liquid to the compressor).
- A metering device needs an appropriate pressure difference across it AND a full line of 100% liquid entering it to do its job; if inlet pressure gets too low you lose control.

### How to Adjust a TXV, TEV or TX Valve  
*Source id: IPMIv-ro3kg*

- TXV, TEV, and TX valve are all the same thing - a thermostatic expansion valve; it balances three forces: bulb pressure (opening force), the internal/external equalizer (closing force), and the adjustable spring (closing force).
- Turning the spindle clockwise compresses the spring -> more closing force -> HIGHER superheat (less feeding); counterclockwise -> LOWER superheat (more feeding); adjust only a quarter turn at a time and let it stabilize.
- You almost never need to adjust a TXV; misdiagnosed 'valve' problems are usually low load/airflow, no full line of liquid, or contamination - so verify subcooling (full line of liquid) and everything else first.

### How to Find Target Superheat  
*Source id: K0WeVON0B5o*

- Target superheat applies ONLY to fixed-metering-device (fixed orifice) air conditioning systems - not refrigeration, and not TXV/EEV systems (where the valve sets superheat at the evaporator outlet); it is mostly older R22 equipment but teaches how superheat works.
- Find target superheat from a chart using outdoor dry bulb AND indoor WET bulb (wet bulb is a better indicator of total coil load); charge total/compressor superheat measured on the suction line outside near the compressor to that target.
- Charge slowly and stop a few degrees before the target (the system takes time to acclimate); target superheat is a moving target that changes as wet bulb drops and outdoor temperature changes.

### How to Properly Diagnose a Failed TXV  
*Source id: IfLfXx9CsGs*

- A TXV is a constant superheat valve (CSV): the bulb is the opening force, the external equalizer and spring are the closing forces; it maintains superheat mechanically via pressures.
- To diagnose: confirm the valve is fed a full line of liquid (subcool), has ~100 psi pressure drop (head pressure) available, then measure superheat and subcool both outside AND inside; condemn only after re-checking superheat inside and ruling out inlet screen/line-dryer restrictions.
- A failed-closed (underfeeding) TXV shows HIGH superheat; low superheat means the coil is already fully fed - do not add charge or drive the valve open.

### How to Replace a TXV  
*Source id: FDG0e6wCUiM*

- Replacing a TXV: recover the refrigerant (know factory charge + line-set add), relocate the filter dryer to the indoor/liquid line near the coil (replacing the old one), flow nitrogen while brazing, pressure test, deep-evacuate below target with a decay test, then charge and verify subcool/superheat.
- Bolt-on (flare) TXVs avoid soldering; foam the bulb even when the manufacturer says it's out of the airflow (Lennox) - couldn't hurt.

### Metering Device Troubleshooting： Subcooling, Sight Glasses & Restrictions  
*Source id: hPAvI0eIXQk*

- The metering device meters LIQUID, so you must confirm subcooled liquid is arriving at it — verify two ways: measure subcooling OR use a sight glass. A sight glass lets you see if you have a full column of liquid, contamination, or bubbles even when your subcooling number says you're 'good' (e.g., with non-condensables you can read subcooling but still see flashing).
- A fixed-orifice metering device passes more refrigerant as outdoor pressure/temperature rises, so you must know outdoor temperature; the house's temperature and humidity (captured by return-air wet bulb) sets how fast refrigerant boils away in the evaporator. Charge a piston by target superheat (from a chart/app using outdoor temp + return wet bulb), not by the subcooling table at the bottom of the chart.
- A fixed orifice 'never fails' but will flood and kill the compressor at low indoor wet bulb + high outdoor temp; the TXV solves this by modulating to keep the evaporator full without overfilling and protects superheat. TXVs are usually condemned wrongly — the real cause is most often airflow, non-condensables, or a restriction; brazing without nitrogen causes the oxidation that actually clogs valves.

### Q&A - EPR and Pressure Limiting Valves w⧸ Matthew Taylor  
*Source id: c5d6KGB7s7A*

- An MOP (maximum operating pressure) valve is a normal TXV body with a different powerhead: a 'vapor charged' head has only a tiny drop of liquid, so once the bulb boils it all off the PT chart stops applying and the valve simply stops pushing harder (it holds, it does NOT shut off), thereby starving refrigerant and limiting suction pressure - used on small self-contained low-temp boxes and, as the 'VGA' valve, in air conditioning.
- The 'P + number' rating is a lab MOP; the real limiting pressure is usually ~10 psi lower and is a RANGE that shifts with superheat/flooding/starving - and an AC VGA valve adds a chemical to damp hunting, which makes its limit unpredictable and its superheat artificially stable (so an AC tech shouldn't condemn a normally-hunting refrigeration TXV).
- MOP, CPR, and EPR all manipulate suction but differently: MOP starves LIQUID into the evaporator (raising superheat); a CPR (crankcase pressure regulator, e.g. CROT) restricts VAPOR at the compressor OUTLET side to cap compressor pressure without touching superheat; an EPR (evaporator pressure regulator) does the opposite of a CPR - it holds the evaporator INLET pressure from falling too low to keep multiple evaporators at different precise temperatures.

### Rack Refrigeration Cycle Part 10 - Electronic Expansion Valves  
*Source id: wqDGfQHpcu0*

- Electronic expansion valves (EEVs) use a stepper (bipolar) motor turning a screw to raise/lower a pin in an orifice; they measure superheat directly with a pressure transducer + temperature sensor and a PT chart rather than simulating it with springs/pressure like a TXV.
- The valve cannot report its own position — the controller only KNOWS position by counting steps, so error accumulates over thousands of moves; the industry fix is to overdrive past zero (drive to mechanical stop plus extra steps) on a schedule to re-sync.
- Pulse (pulse-width-modulation) valves are on/off only, oversized orifice, controlling superheat by pulsing (typically a 6-second cycle) — jagged superheat vs the smooth waves of a modulating EEV; most controllers can run pulse valves via a relay.

### Rack Refrigeration Cycle Part 12 - EPR  
*Source id: 4VnKZXFXnAo*

- An EPR (evaporator pressure regulator) controls the pressure — and therefore the saturation temperature — of the evaporator; because the coil is at saturation the PT chart applies, so setting the EPR is effectively dialing in coil temperature, always to the midpoint (bubble) with glide refrigerants.
- EPRs are mandatory on parallel racks (not optional) — running a case at rack pressure instead causes mechanical cycling of the case, which cycles compressors on/off, wrecks oil return, kills energy efficiency, shortens compressor life, and warms core product.
- The Sorit (Sporlan) / A8 (Parker) EPRs open on rise of inlet and control that inlet pressure; the pilot-operated Sori valve gives near-zero pressure drop (worth running hot-gas lines all over the rack for), can act as its own suction stop, and can even do dual-temp with just a solenoid in the pilot line.

### Rack Refrigeration Cycle Part 8 - Sight Glass and Liquid Line Solenoid  
*Source id: sPRmJQj5QbE*

- Sight-glass placement determines its meaning: after a mechanical subcooler it should be DOWNSTREAM of the subcooler (and downstream of any LPR, which would otherwise flood it clear and hide low charge); a clear glass is either 100% good (solid liquid) or 100% bad (all vapor) — check case temp to know which.
- Mount sight glasses SIDEWAYS (rivering shows the liquid/vapor line clearly); the moisture-indicator dot is a replaceable chemical paper (6-hour book time) that reactivates green under vacuum until it expires.
- Liquid-line solenoids are sized by BTU load, not pipe size — the port number is a 1/32-inch orifice increment; too big and it won't reliably close (skips defrost, ices the case), too small and its pressure drop starves the TXV; aim for the ~3-psi-drop middle.

### Rack Refrigeration Cycle Part 9 - Mechanical Expansion Valves  
*Source id: vG1KKcrtwAI*

- Before taking superheat, confirm three liquid conditions AT the valve: a solid column of liquid, subcooling (even a tenth of a degree below saturation), and enough pressure differential — if any fails, the superheat reading is meaningless.
- The TXV has SOLE responsibility for a rack's superheat — nothing else (EPR, hold-back) can make superheat too high or low; and supermarkets should use BALANCED-port valves (Sporlan SBQ/SBQE) so a change in discharge/liquid pressure doesn't shift the superheat setting.
- A TXV's stamped tonnage is heavily modified by four factors: refrigerant type, evaporator temperature, liquid-temp (subcooling) correction, and pressure-drop across the valve — a 1.5-ton valve can be worth 4 tons after corrections, so you can easily mis-size it.

### Rack Refrigeration Evaporator Pressure Regulation  
*Source id: OEI56EuoJtg*

- Evaporator pressure regulation achieves 100% run time between defrosts by throttling the suction gas to hold the evaporator saturation (temperature) fixed, using either mechanical or electronic valves.
- A mechanical EPR: adjust the stem to set evaporator saturation and it holds there as long as rack pressure stays below that; an electronic EPR references a temperature sensor + pressure transducer and modulates to hold a constant temperature.
- For the strategy to work, the main suction-header pressure must sit a little below the coldest evaporator's setting to leave wiggle room for variation.

### Replacing a Piston with a TXV Using the Danfoss TR6 Kit  
*Source id: M-_Zi123GtI*

- The Danfoss TR6 universal TXV kit ships three valve sizes plus fittings and a selection table; installing a TXV where the condenser data tag calls for one lets you control refrigerant flow (and set subcool) over a much wider range of conditions than a fixed piston.
- A TXV sets superheat at the air handler, not at the condenser, so a higher superheat outside due to a long line set is normal; charge a TXV system to the data-tag subcool (here 12F).
- Don't adjust a TXV unless the superheat is well outside range; give the system time to run since the TXV self-adjusts toward a constant superheat.

### TXV Diagnosis: Superheat, Subcool & Split Temps  
*Source id: M-Z72kAPTbM*

- TXV diagnosis gate: you may only quote a TXV as failed if subcool is normal-or-high AND superheat is normal-or-high (over 25) AND the split is normal-or-high; low superheat, low subcool, or a big split take the TXV off limits.
- To prove a TXV is actually stuck (vs airflow/charge), pull the sensing bulb and warm it in your hand - if the valve works, superheat drops dramatically; if the numbers don't change, it's stuck.
- A wide-open/overfeeding TXV always shows very low (near-zero) superheat with low subcool; adding refrigerant to a CLOSED-down TXV makes subcool respond immediately (stacking against a closed door).

### What a TXV Does (and why techs need to stop replacing them with a piston)  
*Source id: optoVysiApE*

- A TXV controls superheat, filling the evaporator with saturated refrigerant for maximum heat absorption; stop replacing failed TXVs (or new-install TXVs) with pistons - modern TXV designs are reliable and efficient
- Even on a TXV system you still check total superheat at the outdoor unit to confirm the valve is doing its job; a lost bulb charge or clogged inlet strainer starves the coil and shows very high superheat with low saturation
- The TXV bulb is the opening force; balanced against spring pressure and external equalizer force to control superheat - a poorly mounted bulb causes overfeeding/flooding, not a restriction

### Why a Hard Shut Off TXV Closes  
*Source id: hZR_k_G3lZM*

- A hard shut-off TXV closes when the spring force plus the external equalizer (evaporator outlet) force overcome the bulb force; when the system shuts off, evaporator pressure quickly rises above the bulb's saturation temperature and the valve closes fully.
- When the system is off the superheat is zero (measure it — suction line temp equals suction saturation), and a constant-superheat valve throttles fully closed to try to maintain superheat.
- The valve also closes fully during nitrogen pressurization: as you add pressure to the liquid line, the external equalizer eventually exerts enough closing force that suction-side pressure stops rising, forcing you to pressurize from both sides.

### Why a TXV instead of a TEV？.. or a CSV？  
*Source id: j23fGgK4_t4*

- A TXV (which Bryan likes to call a CSV, constant superheat valve) maintains a constant superheat at the evaporator outlet using the sensing bulb (opening force) and the external equalizer (closing force) — mechanically doing what you do with a thermometer and gauge.
- The valve needs a full line of subcooled liquid to work; low suction pressure with correct subcool and correct outlet superheat means a low-LOAD evaporator (airflow, dirty filter, coil not getting heat), not a bad valve — so stop misdiagnosing/replacing TXVs.
- Predecessors were the piston/fixed orifice/capillary tube and the automatic expansion valve (AEV, which held a constant inlet pressure instead of constant superheat and couldn't handle varying load conditions).

### Why and How to Adjust a TXV ⧸ TEV  
*Source id: fmYnQu7utIQ*

- A TXV/TEV maintains constant superheat at the evaporator outlet; it needs a full line of properly subcooled liquid and a sufficient pressure drop (differential between liquid pressure and target suction pressure) to function — low ambient/low head pressure keeps it from working.
- Adjust a valve only because it's not meeting the target outlet superheat (typically 6-8°F), measured at the evaporator outlet, not at the condenser; tightening (clockwise) raises superheat/reduces flow, loosening (counterclockwise) lowers superheat/increases flow.
- The spring is a closing force opposed to the bulb opening force (with the external equalizer also a closing force); make adjustments a half turn at a time and let the system run ~15-30 minutes before re-checking.

## Canonical field stories

### The overheated wet-wrapped valve
- **Setting:** Danfoss warranty returns; valves returned with distorted diaphragms and leaking bulbs
- **Diagnosis chain:** Techs wet-wrap the valve heavily then heat slowly -> the wet rag races to carry heat away, the moisture against the valve dries out, and heat climbs until the diaphragm distorts and the sensing bulb leaks.
- **Root cause:** Overheating during brazing (slow heat lets the valve temperature climb once the rag dries against it)
- **Lesson:** Apply MORE heat quickly to the joint before it travels up to the wet-wrap, and practice brazing valves in to eliminate ~half of failures.
- **Source:** [(Podcast) TXV Operation, Diagnosis, and Failure w⧸ Jamie Kitchen] (id: B7PLADtN06c)

### The five-ton valve on a flatbed
- **Setting:** Military base officer's mess, rooftop unit down over a weekend
- **Diagnosis chain:** A snapped cap tube on the expansion valve required a 'five ton' replacement valve; the motor pool sent a flatbed truck to pick it up
- **Root cause:** Confusion that a ton of capacity equals a ton of weight
- **Lesson:** A 'ton' of cooling comes from the ice-harvesting era (one ton of ice = 12,000 BTU/hr), not weight
- **Source:** [Demystifying the Thermostatic Expansion Valve w⧸ Jim Jansen] (id: RIa2Xhzp5qs)

### Cell-tower computer room compressor overload
- **Setting:** Bryan on a poorly-designed cell-tower system: ~8 tons of cooling in a tiny computer room with pancake units recirculating into each other
- **Diagnosis chain:** Suction pressure dove immediately -> Bryan 'had the bright idea' to crank down the suction service valve at the condensing unit to hold suction pressure up -> the compressor quickly went out on overload
- **Root cause:** Throttling the suction to prop up pressure starved and overheated the compressor; the room was massively oversized in cooling
- **Lesson:** You can't fix an oversized single system by throttling suction (an EPR-style move on a 1:1 system); the right fix was a smaller compressor
- **Source:** [Q&A - EPR and Pressure Limiting Valves w⧸ Matthew Taylor] (id: c5d6KGB7s7A)

### K2 valve reads 120% open
- **Setting:** Shop bench with SMA-12 tool and a K2 controller
- **Diagnosis chain:** Tech drove a spoiling valve fully open with SMA-12, plugged into K2 which then displayed 120% open
- **Root cause:** Controller was guessing/counting position (no feedback); a parameter had told it to drive to 120% — the fact it was physically open was coincidence
- **Lesson:** Electronic valves have no position feedback; the controller only counts steps, so displayed position can be spoofed/wrong
- **Source:** [Rack Refrigeration Cycle Part 10 - Electronic Expansion Valves] (id: wqDGfQHpcu0)

### 38-to-38 solenoids that wouldn't make VPR
- **Setting:** New-case startups; solenoids sized by pipe not load
- **Diagnosis chain:** Cases wouldn't pass VPR because a 3/8 pipe simply got a 3/8 solenoid; the spec called for a larger-capacity valve (e.g. E5 -> E14) once liquid-temp correction was applied
- **Root cause:** Solenoid sized by copper size instead of BTU load + liquid subcooling correction
- **Lesson:** Startup techs must verify solenoid tonnage against the chart with the liquid-temp correction factor, not just match copper
- **Source:** [Rack Refrigeration Cycle Part 8 - Sight Glass and Liquid Line Solenoid] (id: sPRmJQj5QbE)

### One empty Q-body took down the rack
- **Setting:** Vendor tech soldered in a Q-body ~2 a.m. and forgot the cartridge
- **Diagnosis chain:** Rack down by ~6 a.m., wouldn't run; a single 3/8-line Q-body with no cartridge dumped liquid straight into suction — couldn't build suction on one compressor
- **Root cause:** Empty Q body flooding suction
- **Lesson:** One wide-open/empty TXV can flood and sink the whole rack's average superheat
- **Source:** [Rack Refrigeration Cycle Part 9 - Mechanical Expansion Valves] (id: vG1KKcrtwAI)

### The underground line sets packed with sand plugging TXV strainers
- **Setting:** Bryan's early trainer job doing residential new-construction installs; installers pushed underground line sets using plastic caps, packing them with sand
- **Diagnosis chain:** TXV strainers plugged constantly → Bryan got fast at knocking out the screen and adding a new liquid line drier to catch the rest
- **Root cause:** Unsealed underground line sets filling with sand plugged the TXV inlet strainer, mimicking a failed valve
- **Lesson:** Bad install practices (unsealed lines, no nitrogen, copper shavings) clog strainers and get blamed on the TXV; place the liquid line drier close to the indoor unit
- **Source:** [What a TXV Does (and why techs need to stop replacing them with a piston)] (id: optoVysiApE)

### Case coil installed on the wrong side of the furnace
- **Setting:** A furnace years earlier where a tech installed the cased coil on the wrong side
- **Diagnosis chain:** Proper airflow through the unit but the coil wasn't getting proper load because air wasn't going over the coil; the CSV kept throttling down to hold superheat while the coil froze to a ball of ice
- **Root cause:** coil not receiving proper heat/load despite adequate airflow
- **Lesson:** Low suction with good subcool and correct outlet superheat is a low-load condition, not a bad valve
- **Source:** [Why a TXV instead of a TEV？.. or a CSV？] (id: j23fGgK4_t4)

### Factory units with zero superheat in heat mode
- **Setting:** Joe Shearer's rash of new units, condenser in heat mode
- **Diagnosis chain:** Units coming off the factory floor showed zero superheat (liquid into the suction line) in heat mode; adjusted the valve to raise superheat above 5-6°F
- **Root cause:** factory valve set too open giving zero superheat
- **Lesson:** Tighten the stem clockwise a half turn at a time to raise superheat to the 6-8° target
- **Source:** [Why and How to Adjust a TXV ⧸ TEV] (id: fmYnQu7utIQ)

## Contrarian takes (where Bryan / guests diverge from common teaching)

- **Common teaching:** A TXV maintains constant superheat (and a constant evaporator temperature).
  **Bryan's position:** False - a TXV requires RISING superheat to open (spring force grows as it compresses), so superheat varies with load.
  **Reasoning:** The sensing bulb must get a few degrees warmer to hold the valve open against increasing spring force; superheat drops as the load is satisfied.
  **Source:** [(Podcast) TXV Operation, Diagnosis, and Failure w⧸ Jamie Kitchen] (id: B7PLADtN06c)

- **Common teaching:** Low suction plus some subcool means replace the TXV.
  **Bryan's position:** Confirm subcool (charge), then determine load vs flow; a working TXV correctly throttles down on low airflow.
  **Reasoning:** On low airflow the TXV throttles closed and suction drops (the only way a fixed-speed compressor balances) - replacing it drops the coil colder and makes freezing worse.
  **Source:** [(Podcast) TXV Operation, Diagnosis, and Failure w⧸ Jamie Kitchen] (id: B7PLADtN06c)

- **Common teaching:** A crimped/plugged external equalizer makes the valve go wide open.
  **Bryan's position:** In practice trapped static refrigerant can make the valve slam shut or go very laggy - it depends on the situation.
  **Reasoning:** You can't compress a trapped liquid under the diaphragm, so the valve stays put and reacts very slowly.
  **Source:** [(Podcast) TXV Operation, Diagnosis, and Failure w⧸ Jamie Kitchen] (id: B7PLADtN06c)

- **Common teaching:** Adjust superheat or warm the bulb and you've fixed it.
  **Bryan's position:** Those are diagnostics; warming the bulb only checks the charge and can temporarily un-stick a gummy valve.
  **Reasoning:** The root cause (contamination, airflow) remains; you've only identified where to look.
  **Source:** [(Podcast) TXV Operation, Diagnosis, and Failure w⧸ Jamie Kitchen] (id: B7PLADtN06c)

- **Common teaching:** You can assume a capillary tube's outer diameter tells you its flow (one size fits all).
  **Bryan's position:** You cannot assume outer diameter tells you the inner diameter; inner diameter determines flow, so measure it with calipers or a cap-tube gauge and size length to capacity and refrigerant.
  **Reasoning:** Different inner diameters mean different refrigerant flow even at the same outer diameter, so ID and length must be matched to the design.
  **Source:** [Capillary Tube Repair and Brazing Class] (id: DtINXanblJw)

- **Common teaching:** Adjust the TXV to set suction pressure, amp draw or box temperature
  **Bryan's position:** The valve's only job is to control superheat where the bulb is; adjust it for that or the whole system won't work right
  **Reasoning:** He admits making that mistake early on; the valve controls superheat, full stop
  **Source:** [Demystifying the Thermostatic Expansion Valve w⧸ Jim Jansen] (id: RIa2Xhzp5qs)

- **Common teaching:** Replace a bleed-port valve with a standard non-bleed-port valve from the wholesaler
  **Bryan's position:** Don't; there's a reason it had a bleed port (off-cycle equalization or fine-tuning capacity)
  **Reasoning:** You can approximate a bleed port by adding a sized cap tube from inlet to outlet if you only have a standard valve
  **Source:** [Demystifying the Thermostatic Expansion Valve w⧸ Jim Jansen] (id: RIa2Xhzp5qs)

- **Common teaching:** High superheat / low suction means condemn the TXV
  **Bryan's position:** Assume it's airflow first; a failing-closed TXV has high superheat but a low split and good subcool, while airflow or low charge presents differently
  **Reasoning:** Low or normal superheat and a normal/high split are not symptoms of a failing-closed TXV
  **Source:** [Diagnosing a Failed TXV] (id: 9Hz0af0fnsg)

- **Common teaching:** You can't effectively pull a vacuum through a hard-shutoff TXV / pulling through the valve is a problem.
  **Bryan's position:** The valve goes completely open under vacuum, so a one-hose setup on the suction line (gauge on liquid line) is a very fast connection.
  **Reasoning:** With no external-equalizer pressure, the bulb force dominates and drives even a hard-shutoff valve fully open; there is only minor pressure drop across it.
  **Source:** [Does a TXV Shut under Vacuum？] (id: r18UybHTvv4)

- **Common teaching:** If a TXV's superheat seems high, just turn the adjustment down to a low value like 2 degrees.
  **Bryan's position:** You can't drive a TXV below the evaporator's minimum stable superheat — the setting must keep the linear TXV line on the dry/stable side of the curve, so there's an irreducible minimum superheat with a TXV.
  **Reasoning:** Below minimum stable superheat, liquid droplets break off the meniscus and travel down the pipe center, surging and warming/cooling the sensing bulb, causing the valve to hunt across the 60-90% load range where AC spends most of its time.
  **Source:** [Electronic Expansion Valves (EEV) w⧸ Jamie Kitchen (Podcast)] (id: ibZN1vzyPHU)

- **Common teaching:** Freeze fresh product in your home freezer to preserve it.
  **Bryan's position:** Don't freeze fresh product in a cap-tube freezer unless you must — buy pre-frozen; the fixed orifice can't increase flow to match the added load, so it freezes slowly with larger ice crystals and more tissue damage.
  **Reasoning:** A cap tube is designed for a fixed load; added warm product underfeeds the coil, unlike a flash-freeze (e.g., McDonald's) that preserves texture.
  **Source:** [Electronic Expansion Valves (EEV) w⧸ Jamie Kitchen (Podcast)] (id: ibZN1vzyPHU)

- **Common teaching:** Just set 10 degrees of superheat every time on a piston system.
  **Bryan's position:** Target superheat is variable, not a fixed 10 degrees — it depends on outdoor dry-bulb and indoor wet-bulb.
  **Reasoning:** Outdoor temperature changes liquid pressure/flow (e.g., ~400 PSI on a 100-degree day vs ~200 on a cool day), so a 10-degree setting on a 65-degree day could drop to 0-3 degrees at 100 degrees, flooding the compressor.
  **Source:** [Finding Target Superheat] (id: Xuy4mtdXlRI)

- **Common teaching:** A TXV maintains one fixed exact superheat.
  **Bryan's position:** A TXV operates over a RANGE - superheat runs a little higher at high load and lower at low load; dialing it in during a hot pull-down leads to zero superheat later once the case cools.
  **Reasoning:** The balance of forces shifts with load, so target a range (6-12 at the evap outlet) rather than a single number.
  **Source:** [How to Adjust a TXV, TEV or TX Valve] (id: IPMIv-ro3kg)

- **Common teaching:** Superheat should always be measured/charged at the evaporator coil.
  **Bryan's position:** For these fixed-orifice charging charts we use TOTAL/compressor superheat measured on the suction line outside near the compressor, not evaporator superheat (which is for TXV/EEV systems).
  **Reasoning:** On a fixed orifice there is no valve setting superheat at the coil, so charge to total system superheat.
  **Source:** [How to Find Target Superheat] (id: K0WeVON0B5o)

- **Common teaching:** Low suction pressure while adding refrigerant that won't come up means a bad TXV
  **Bryan's position:** A TXV throttling down as you add refrigerant is proof it is working properly, the exact opposite of a failure.
  **Reasoning:** The valve responds to added charge by throttling to hold superheat.
  **Source:** [How to Properly Diagnose a Failed TXV] (id: IfLfXx9CsGs)

- **Common teaching:** A restriction causes high head pressure
  **Bryan's position:** A big restriction (or an underfeeding/throttling TXV) actually causes head pressure to go DOWN, not up.
  **Reasoning:** Pumping down proves a 100% restriction doesn't spike head pressure - refrigerant just condenses; head pressure rises only from heat being rejected, so a restriction lowers it.
  **Source:** [How to Properly Diagnose a Failed TXV] (id: IfLfXx9CsGs)

- **Common teaching:** Freezing / low suction means add charge to get out of the freezing zone
  **Bryan's position:** Most freezing is caused by airflow (dirty filters, undersized ducts, closed vents); if superheat is normal or low do not add charge.
  **Reasoning:** Below ~300-350 CFM per ton you risk freezing regardless of charge.
  **Source:** [How to Properly Diagnose a Failed TXV] (id: IfLfXx9CsGs)

- **Common teaching:** I've brazed for 30 years without nitrogen and never had a problem; and TXVs are junk that always fail.
  **Bryan's position:** Those two statements are connected — no nitrogen causes oxidation that clogs the metering device, so the 'always failing' TXVs are caused by the no-nitrogen brazing.
  **Reasoning:** Humans respond to what they can see; in refrigeration the damage is hidden, so cutting open compressors reveals the oxidation and poor vacuums people didn't believe mattered.
  **Source:** [Metering Device Troubleshooting： Subcooling, Sight Glasses & Restrictions] (id: hPAvI0eIXQk)

- **Common teaching:** The filter drier location matters a lot (must be inside/before the metering device).
  **Bryan's position:** Location matters less than making sure it actually gets changed — just never put it behind the valves.
  **Reasoning:** Behind the valves you must recover all refrigerant to change it, raising contamination risk; climate (rust belt vs dry Vegas) drives inside-vs-outside more than performance.
  **Source:** [Metering Device Troubleshooting： Subcooling, Sight Glasses & Restrictions] (id: hPAvI0eIXQk)

- **Common teaching:** A TXV that hunts/swings is bad and should be condemned.
  **Bryan's position:** Normal swing is expected on a real (refrigeration) TXV; AC techs are used to the artificially-stable VGA valve, so they wrongly condemn a normally-hunting valve.
  **Reasoning:** The VGA has an added damping chemical; away from it, some hunting is how the valve is supposed to behave.
  **Source:** [Q&A - EPR and Pressure Limiting Valves w⧸ Matthew Taylor] (id: c5d6KGB7s7A)

- **Common teaching:** A 'P40' valve limits at 40 psi; a TXV is a constant-superheat device.
  **Bryan's position:** The real limit is ~10 psi less and is a range, not a fixed number; a TXV is only a 'constant superheat' valve as a teaching simplification - there's a minimum stable superheat and a hot-pulldown limiting zone.
  **Reasoning:** Superheat setting, flooding, and starving all shift the actual limiting pressure; Danfoss/Sporlan correct the 'constant superheat' language.
  **Source:** [Q&A - EPR and Pressure Limiting Valves w⧸ Matthew Taylor] (id: c5d6KGB7s7A)

- **Common teaching:** An EPR and an MOP both control evaporator pressure, so they're the same thing.
  **Bryan's position:** They're opposites: MOP limits pressure from going too HIGH (protecting a small compressor after hot start), while an EPR keeps evaporator pressure from falling too LOW to hold precise multi-evaporator temperatures.
  **Reasoning:** Different sides of the valve and opposite goals; EPR does nothing to protect the compressor.
  **Source:** [Q&A - EPR and Pressure Limiting Valves w⧸ Matthew Taylor] (id: c5d6KGB7s7A)

- **Common teaching:** A strainer built into the expansion valve is a good feature
  **Bryan's position:** Instructor calls the internal strainer on some EEVs 'a terrible design' because you must take the flare/whole valve apart to service it
  **Reasoning:** Serviceability — an external or accessible screen is far better than one requiring full disassembly
  **Source:** [Rack Refrigeration Cycle Part 10 - Electronic Expansion Valves] (id: wqDGfQHpcu0)

- **Common teaching:** An EPR changes superheat
  **Bryan's position:** An EPR has nothing to do with superheat — only the metering device (TXV/EEV) controls superheat
  **Reasoning:** Changing the EPR briefly shows a superheat change only until copper temperature stabilizes, then it's the same; the EPR controls flow-back pressure, not the amount of refrigerant fed
  **Source:** [Rack Refrigeration Cycle Part 12 - EPR] (id: 4VnKZXFXnAo)

- **Common teaching:** You can just open the EPR / run at rack pressure to save a valve
  **Bryan's position:** Never run without the EPR
  **Reasoning:** It causes mechanical cycling, compressor staging, oil problems and warm product — EPRs exist because they're mandatory to parallel-rack operation
  **Source:** [Rack Refrigeration Cycle Part 12 - EPR] (id: 4VnKZXFXnAo)

- **Common teaching:** Running cases on cut-in/cut-out scores 100% on Tech Assist, so it's good
  **Bryan's position:** Opening the EPR and letting cases cut-in/cut-out to score 100% Tech Assist will destroy the rack
  **Reasoning:** Mechanical case cycling swings suction, stages/cycles compressors, wrecks oil return and shortens compressor life; the cut-out is a SAFETY, not a control mode — set the EPR to the manufacturer target instead
  **Source:** [Rack Refrigeration Cycle Part 8 - Sight Glass and Liquid Line Solenoid] (id: sPRmJQj5QbE)

- **Common teaching:** Put the external equalizer bulb downstream of the equalizer line
  **Bryan's position:** Both bulb positions are defensible; engineers say UPSTREAM (best case control), field techs move it DOWNSTREAM to protect the rack if the equalizer leaks
  **Reasoning:** If the valve leaks liquid out the equalizer line, an upstream bulb misses it and floods the rack; a downstream bulb protects the rack but slightly mis-controls the case — choose and be able to defend it
  **Source:** [Rack Refrigeration Cycle Part 9 - Mechanical Expansion Valves] (id: vG1KKcrtwAI)

- **Common teaching:** Set superheat to the middle of the swing
  **Bryan's position:** In refrigeration set to the BOTTOM of the swing (Hill Phoenix/Tyler/Zero Zone spec that); AC uses the midpoint
  **Reasoning:** Equipment manufacturers spec superheat to the coldest momentary point; low-temp valves are oversized to recover from door openings, so 15-20 degree swings on at-temp ice cream cases are normal
  **Source:** [Rack Refrigeration Cycle Part 9 - Mechanical Expansion Valves] (id: vG1KKcrtwAI)

- **Common teaching:** Pistons fail
  **Bryan's position:** Pistons don't fail - a piston is just a hunk of brass; it can clog or get stuck but doesn't fail. It also unseats one direction on a heat pump for unrestricted reverse flow.
  **Reasoning:** Understanding it's a fixed orifice explains its behavior.
  **Source:** [Replacing a Piston with a TXV Using the Danfoss TR6 Kit] (id: M-_Zi123GtI)

- **Common teaching:** Low suction with a slightly high superheat means the TXV is failing - replace it
  **Bryan's position:** Not necessarily - high or normal split means the TXV is off limits; a cold coil (airflow issue) slams the TXV shut and mimics a failed valve
  **Reasoning:** The TXV closes in response to a cold coil from low airflow; the pressures lie, so check split and get manometers on airflow
  **Source:** [TXV Diagnosis: Superheat, Subcool & Split Temps] (id: M-Z72kAPTbM)

- **Common teaching:** Replace a failed or new-install TXV with a piston because TXVs fail (rust, lost bulb charge)
  **Bryan's position:** Craig/Bryan: newer TXV designs last a long time and are efficient - don't downgrade to a piston; install them properly (nitrogen flow/purge, tight insulated bulb)
  **Reasoning:** Old-style rusting stainless heads losing bulb charge gave TXVs a bad rap; a lost bulb removes the opening force and starves the coil, but modern designs and good practice solve it
  **Source:** [What a TXV Does (and why techs need to stop replacing them with a piston)] (id: optoVysiApE)

- **Common teaching:** Low suction pressure on a TXV system means the valve is bad or the system needs charge
  **Bryan's position:** If subcool is correct and the valve holds proper outlet superheat, it's a low-load condition; adding charge is the common misdiagnosis
  **Reasoning:** The CSV is doing its job maintaining superheat; the coil just isn't getting enough heat
  **Source:** [Why a TXV instead of a TEV？.. or a CSV？] (id: j23fGgK4_t4)

- **Common teaching:** A negative superheat reading means you actually have negative superheat
  **Bryan's position:** Negative superheat almost always means a miscalibrated gauge and/or thermometer; you likely have a zero superheat (mixed liquid/vapor)
  **Reasoning:** A couple PSI and a couple degrees of tool error combine to read ~4° low; calibrate your tools
  **Source:** [Why a TXV instead of a TEV？.. or a CSV？] (id: j23fGgK4_t4)

- **Common teaching:** Adjust the TXV to raise suction pressure
  **Bryan's position:** The valve maintains constant superheat, not constant suction pressure; low suction from low airflow/low load is the valve doing its job — don't adjust to chase suction pressure without measuring superheat
  **Reasoning:** With low airflow the valve sees low superheat and closes down, dropping suction; adjusting for suction is the wrong reason
  **Source:** [Why and How to Adjust a TXV ⧸ TEV] (id: fmYnQu7utIQ)

## Diagnostic reasoning chains

**(Podcast) TXV Operation, Diagnosis, and Failure w⧸ Jamie Kitchen** (id: B7PLADtN06c)
- Low suction + normal subcool -> is superheat low (e.g. 8F at a 28F evap = airflow/load problem) or high (e.g. 30F at a 28F evap = refrigerant-flow problem)? Fix accordingly; don't replace a working valve
- Refrigerant-flow suspected -> check upstream first (liquid-line temp drop / flash gas hiss, plugged filter drier showing ice on its last 1/2 inch, a closed valve) before condemning the TXV; feel or thermocouple each component
- Warm the bulb in your hand -> valve opens = good bulb charge and it's a superheat/sticking issue; no response = plugged/stuck/lost charge, so pull the orifice, inspect the screen, and find WHY it plugged before replacing (relocate the drier, flow nitrogen, flush)
- Multi-circuit evaporator with low suction -> scan circuits with an IR thermometer for a starved circuit (cold-inlet to warm-outlet profile) - a distribution problem, not the TXV

**Capillary Tube Repair and Brazing Class** (id: DtINXanblJw)
- High-pressure liquid enters the cap tube -> collides with the porous inner copper wall -> friction creates heat and slows the flow -> flow chokes and pressure drops along the length -> near the end a two-phase change begins -> exits as a low-pressure saturated vapor for the evaporator.

**Demystifying the Thermostatic Expansion Valve w⧸ Jim Jansen** (id: RIa2Xhzp5qs)
- Troubleshoot by symptom: starving = high superheat + low suction pressure; overfeeding = low superheat + high suction pressure; hunting = excessive modulation (often low load or oversized valve, contamination on all lists).
- Adjust in small quarter-turn increments and let the system run 15-20 minutes between adjustments; it's not a light switch.

**Diagnosing a Failed TXV** (id: 9Hz0af0fnsg)
- Airflow confirmation: shut off, let the coil warm and pressures equalize, turn on and wait ~5 minutes; if airflow, it runs like a cold line right after with a high split and normal-to-low superheat.
- Heat-mode check: run heat mode on common suction; low pressures point away from the TXV (low charge), normal/high suction points to the cool-mode TXV. Also remove the bulb and hang it outside the panel: if it opens it's not the TXV, if it stays closed it's mechanically failed.

**Does a TXV Shut under Vacuum？** (id: r18UybHTvv4)
- Bulb pressure (P1, above diaphragm) vs external-equalizer + spring force (below): normal run = liquid metered; system off with equalizer pressure > bulb = hard shutoff closed; under vacuum/no charge = maximum bulb pressure, no equalizer pressure, valve goes wide open.

**EEV Troubleshooting in 3D： A Guide for HVAC Techs** (id: fd0kGz0XckE)
- If coils ohm good but symptoms persist, drive the valve mechanically (manual actuator or EEVMate for its full pulse range) and confirm open/close by measuring temperature entering vs exiting the valve while running.

**Electronic Expansion Valves (EEV) w⧸ Jamie Kitchen (Podcast)** (id: ibZN1vzyPHU)
- Reduce airflow on a cap-tube system (paper against the coil): superheat drops toward zero and liquid floods out of the evaporator; on a TXV the superheat only drops a couple degrees but evaporator pressure falls substantially (can drop below freezing and ice up) — that's the TXV doing its job, not a TXV fault.
- Reduce load on a fixed-orifice system (shut off the blower): head pressure drops almost proportionally with suction pressure because you're absorbing less heat, so there's less to reject — a counterbalancing effect people don't expect.
- Under high humidity/load a TXV sees higher superheat, opens, raises evaporator pressure AND runs more superheat, raising average evaporator temperature — which decreases dehumidification exactly when you need it most; an EEV instead lowers superheat and average evaporator temperature under high load.

**Finding Target Superheat** (id: Xuy4mtdXlRI)
- High superheat = refrigerant boils off too early, leaving part of the coil warm/superheated with poor heat transfer, plus a warm suction line that overheats the (refrigerant-cooled) compressor and hurts efficiency.
- Low superheat with LOW suction pressure = low load on the evaporator (e.g., restricted airflow moving only 2 of 3 tons of heat) so refrigerant doesn't finish boiling and pressure falls.
- Low superheat with HIGH suction pressure = overfed coil, still liquid (e.g., a wide-open TXV reads ~0 superheat and raises pressure, warming the whole coil so it dehumidifies poorly).

**HVACR Metering Device Basics** (id: qV-DIqIxPGk)
- The TXV/EEV senses superheat at the evaporator outlet (TXV via a refrigerant-filled bulb plus an external equalizer tapping the suction line; EEV via an electronic temperature sensor and pressure transducer) and modulates its orifice to keep just enough boiling liquid in the coil without letting liquid run down the suction line into the compressor.

**How to Adjust a TXV, TEV or TX Valve** (id: IPMIv-ro3kg)
- Before adjusting: confirm a full line of liquid entering the valve via subcooling (factory value, above zero) or a full sight glass in refrigeration -> measure superheat at the outlet of the evaporator coil (saturated suction temp vs suction line temp) -> only then adjust a quarter turn at a time, waiting ~15 minutes to stabilize, watching that you never drive to zero superheat and slug the compressor.

**How to Find Target Superheat** (id: K0WeVON0B5o)
- Stabilize the system ~20 minutes -> read outdoor dry bulb (in shade) and indoor wet bulb -> look up target superheat -> if measured superheat is higher than target, add charge slowly; if lower, recover slowly.
- Higher indoor wet bulb raises target superheat (more coil load); higher outdoor temperature lowers target superheat (higher head pressure feeds more through the orifice).

**How to Properly Diagnose a Failed TXV** (id: IfLfXx9CsGs)
- Low suction pressure (e.g. 105 psi = 33.6F evaporator on R410A, 75F indoor, only ~40F split expected) with superheat IN RANGE (14 out / 10 in) -> airflow problem, not the TXV.
- Same low suction but 27F outside / 23F inside superheat, adequate subcool in, ~100 psi headroom, inlet screen ruled out -> condemn the TXV as underfeeding.
- Heating the bulb (opening force) and seeing suction rise slightly is normal on a functioning valve; the test has little diagnostic value versus measuring superheat/subcool accurately.

**Metering Device Troubleshooting： Subcooling, Sight Glasses & Restrictions** (id: hPAvI0eIXQk)
- Subcooling reads fine but sight glass shows bubbles -> suspect restriction, non-condensables, mixed refrigerants, or (on a long attic line set) the liquid line reaching its saturation point and flashing.
- Long line set through a 120F attic with a 110F liquid line at 10 degrees subcool -> heat absorbs into the liquid line, subcooling drops toward zero and flashes -> add a service port + sight glass in the attic to see and measure subcooling right there; insulate the liquid line.

**Q&A - EPR and Pressure Limiting Valves w⧸ Matthew Taylor** (id: c5d6KGB7s7A)
- Small self-contained low-temp box comes out of defrost hot -> without MOP the suction rides far above the tiny compressor's operating range, driving superheat and discharge (hot-gas) temp too high and cooking the oil -> an MOP head starves the valve so the compressor easily pulls suction back into range (slower pulldown, but it protects the compressor).
- Long line set (e.g. 200 ft) -> MOP's starving would delay refrigerant reaching the compressor and over-starve it -> instead use a CPR at the compressor to limit outlet pressure while a plain liquid-filled TXV controls superheat accurately.
- Rack startup after a power outage -> circuits all come back at once and run compressors at too-high suction -> a tech 'plays the piano', bringing on one small compressor, letting it pull down, then staging circuits/compressors manually to balance.

**Rack Refrigeration Cycle Part 10 - Electronic Expansion Valves** (id: wqDGfQHpcu0)
- If a tech changes valve position with the SMA-12 while it's unplugged from the controller, then reconnects, the controller thinks the valve is where IT last counted (e.g. 100%) when it's actually elsewhere (0%) — spoofed location that won't self-correct until an overdrive-to-zero event.
- Testing an EEV motor without disassembly: measure motor windings — black/white ~100 ohms +/-10%, red/green also; SMA-12's four lights pulse to show continuity — a steadily-on light = short, an unlit light = open; slow the step rate to see LEDs pulse.

**Rack Refrigeration Cycle Part 12 - EPR** (id: 4VnKZXFXnAo)
- Setting an EPR: take the required SST from the rack legend, convert to pressure via PT chart at midpoint for the refrigerant type, account for pressure drop between EPR location (rack) and the evaporator, dial it in as a STARTING point, let the case run, then fine-tune — never set-and-walk.
- If a Sorit won't adjust and a case is cycling wildly/wide open, suspect a pilot-pressure problem (no pilot pressure to the valve, or pilot not reaching P3) — the CROT (crankcase pressure regulator) that sets the Sorit pilot pressure must be dialed in FIRST because changing it changes every Sorit's setting.

**Rack Refrigeration Cycle Part 8 - Sight Glass and Liquid Line Solenoid** (id: sPRmJQj5QbE)
- Sight-glass flashing after the subcooler -> look for a restriction (liquid-line drier) between the sight glass and receiver, or truly low charge; before the subcooler, flashing is meaningless/expected on a hot day (no subcooling yet in the receiver).
- Solenoid liquid-temp correction: a chart '3-ton' valve fed 50F subcooled liquid (x1.5 correction) is actually ~5-ton — so a solenoid engineered WITH the subcooler will be under/over-sized if the subcooler is off (100F liquid), giving big pressure drops and starving/flooding.

**Rack Refrigeration Cycle Part 9 - Mechanical Expansion Valves** (id: vG1KKcrtwAI)
- Swing tells you sizing: oversized valve = hunting/big swing (normal on cold cases and walk-ins that recover heavy loads); perfectly sized = little swing; undersized = no swing but high superheat (coupled with high superheat + low liquid = a real problem).
- Cross-charge head selection: C-charge stays ~flat across -20 to +30F evaporator (why bunkers/dual-temp still work without re-setting at low temp); a straight VG or Z head varies more — pick VGA/C heads to span the supermarket range.
- Distributor: one warm tube among cold ones = stopped-up (wax on mineral oil, or POE gunk) — hot water clears it, then change driers because the system is dirty; distributor tonnage uses the liquid-temp correction but NOT the pressure-drop correction (already past the expansion).

**Rack Refrigeration Evaporator Pressure Regulation** (id: OEI56EuoJtg)
- Mechanical EPR holds a set pressure; electronic modulates slightly around a target temperature — both aim to keep evaporator saturation fixed for constant run time.

**Replacing a Piston with a TXV Using the Danfoss TR6 Kit** (id: M-_Zi123GtI)
- Before/after check: piston system read ~3 subcool and adequate superheat; after TXV install, set to 12F subcool per data tag with delivered capacity actually higher (~33,000 BTU) and superheat set at the air handler.

**TXV Diagnosis: Superheat, Subcool & Split Temps** (id: M-Z72kAPTbM)
- High superheat + low suction + high subcool (screenshot) = restriction / failing (closing) TXV - but if split is high/normal it's NOT the TXV, it's an airflow issue closing the valve on a cold coil
- Very high suction + low head + low subcool + low superheat = likely slipping compressor or reversing valve, NOT a wide-open TXV (a TXV can't push suction to ~170 psi)
- Overfeeding/open TXV: ~0-5 superheat, low subcool (refrigerant whizzes by, can't stack); adding refrigerant drives superheat to zero fast without helping subcool

**What a TXV Does (and why techs need to stop replacing them with a piston)** (id: optoVysiApE)
- High total superheat + very low saturation on a TXV = clogged inlet strainer or a TXV that lost its bulb charge (liquid-line restriction starving the coil)
- A poorly mounted bulb causes overfeeding/flooded condition (low superheat), not a restriction - don't waste time insulating the bulb when superheat is already high

**Why a Hard Shut Off TXV Closes** (id: hZR_k_G3lZM)
- When pressurizing a TXV system with nitrogen, liquid-line pressure keeps rising but the suction-line pressure you're reading at the condenser stops going up — that's the external equalizer force closing the valve; pressurize from both sides.

**Why a TXV instead of a TEV？.. or a CSV？** (id: j23fGgK4_t4)
- TXV fails shut more often than open because the bulb is the opening force — a bulb losing its charge leaves no opening force and the valve slams closed (high superheat).
- Valve open too far (high suction, low/zero superheat) can happen if the external equalizer closing force is blocked (solder in the equalizer tube) or after overheating.
- Check superheat even on TXV systems (set charge by subcool per manufacturer) to verify the valve and detect restrictions; a clogged inlet screen can mimic a bad valve.

**Why and How to Adjust a TXV ⧸ TEV** (id: fmYnQu7utIQ)
- Before adjusting: confirm full subcooled liquid in, no frost before the valve, adequate head pressure (run 15-30 min), and read superheat at the evaporator outlet (accounting for suction-line pressure drop when reading at the condenser). If it can't hit target after gentle adjustment, suspect a stuck valve, lost bulb charge, blocked external equalizer, or debris/screen restriction.

## Specific numbers Bryan cites

| Metric | Value | Context | Bryan cited a source | Episode id |
|---|---|---|---|---|
| R-410A latent heat of evaporation | ~120 BTU/lb; ~100 lb/hr per ton | how much refrigerant a ton circulates | yes | B7PLADtN06c |
| example static superheat | 7F at a 45F AC evaporator | valve won't start opening until static superheat is reached | yes | B7PLADtN06c |
| SEER 13 mandate | 2006 (flipped most units from pistons to TXVs) | why TXVs became common | yes | B7PLADtN06c |
| Florida airflow / dehumidification | often ~289-320 CFM/ton (enhanced mode below 300) | why Florida coils run near freezing | yes | B7PLADtN06c |
| superheat adjustment rate | varies by model: some AC valves ~1F/turn, some ~4F/turn | read the datasheet before adjusting | yes | B7PLADtN06c |
| cap tube outer diameter (Supco BS2) | 0.93 in (as stated in class) | measured outer diameter of the example capillary tube | no | DtINXanblJw |
| cap tube inner diameter (Supco BS2) | 0.04 in | inner diameter of the same example cap tube | no | DtINXanblJw |
| cap tube length example | about 10 to 12 feet | length of the coiled cap tube when rolled out | no | DtINXanblJw |
| capacity sizing example | 12,000 BTU (or two 6,000 BTU cap tubes in a distribution network) | sizing cap tubes to capacity | no | DtINXanblJw |
| insertion depth rule of thumb | about 1/4 to 1/2 inch past the joint | how far to insert the cap tube into the pipe/joint | no | DtINXanblJw |
| caliper cost | $8 on Amazon | tool to measure cap tube inner and outer diameter | no | DtINXanblJw |
| power head size | 43 mm | the produce-case TXV power head being replaced | yes | CvqE7RbYL-g |
| Ton definition | 1 ton = 12,000 BTU/hr | From melting/freezing a one-ton block of ice | yes | RIa2Xhzp5qs |
| AC superheat range | ~8-12 degrees, evaporator up to ~52F | Depends on application; refrigeration can run lower | yes | RIa2Xhzp5qs |
| Airflow test wait | ~5 minutes | Restart after equalizing to see if it runs like a cold line (airflow) | no | 9Hz0af0fnsg |
| Drive voltage | 5-12 VDC | stepper motor windings, varies by manufacturer | yes | fd0kGz0XckE |
| Stepper full travel | 480 pulses | indirect EEV fully open/close | yes | fd0kGz0XckE |
| Gear-drive full travel | 2000 pulses (some 0-3000 or 6000) | direct-drive EEV, finer control | yes | fd0kGz0XckE |
| Coil resistance example | 45 ohms +/-10% | one red common wire; low or open = replace | yes | fd0kGz0XckE |
| wine cooler evaporator temp | ~50F (high evap temp) | example of a very high evaporator temperature application with a low pressure drop | no | ibZN1vzyPHU |
| low-temp refrigeration | -10 to -20F | low-temp refrigeration determined by a large pressure drop across the metering device | no | ibZN1vzyPHU |
| TXV static/factory superheat | ~7 degrees static, opens to ~12-14 operating | the value on the side of the box; valve goes closed-to-open between ~7 and ~14 degrees | no | ibZN1vzyPHU |
| minimum stable superheat | ~4-5 degrees (evaporator-dependent) | the minimum superheat needed to ensure droplets fully evaporate; varies with capacity and coil design | no | ibZN1vzyPHU |
| pulse-width valve cycle | 6-second period | a Danfoss pulse-width EEV opens a fraction of a 6-second window proportional to load (e.g., 3 of 6 sec at 50%) | yes | ibZN1vzyPHU |
| piston high-superheat example | ~20-24 degrees superheat at 66-68F indoor wet bulb, 75F outdoor dry bulb | from a piston charging chart under high wet-bulb/cool-outdoor conditions, driving up average evaporator temp | yes | ibZN1vzyPHU |
| efficient coil superheat example | 8 degrees (40F sat in, 48F out) | 8 degrees of superheat means the coil only warmed at the very end — a very efficient coil | no | Xuy4mtdXlRI |
| outdoor liquid pressure swing | ~400 PSI on a 100-degree day vs ~200 on a cool day | outdoor temperature dramatically changes how much liquid is pushed through the piston | no | Xuy4mtdXlRI |
| wide-open TXV coil temp | ~52F saturation vs proper 40F | a wide-open TXV raises pressure, warming the whole coil from ~40F to ~52F saturation | no | Xuy4mtdXlRI |
| required pressure drop across metering device | commonly ~100 PSI (some say 80 psi) | varies by business segment and valve type; there must be a pressure difference for the valve to work | yes | qV-DIqIxPGk |
| evaporator outlet superheat target | 6 to 12 F | sweet spot at the outlet of the evaporator coil | yes | IPMIv-ro3kg |
| compressor superheat target | ~20 F | Copeland's general call at the compressor | yes | IPMIv-ro3kg |
| adjustment increment | quarter turn at a time (~1/4 degree change on many valves) | manufacturer recommendation | yes | IPMIv-ro3kg |
| max valve temperature | 210 F / 110 C (as stated) | keep the valve below this when brazing | yes | IPMIv-ro3kg |
| target superheat example | 95 deg outdoor dry bulb + 67 deg indoor wet bulb -> 12 deg target superheat | universal target-superheat chart | yes | K0WeVON0B5o |
| danger zone | below ~6 deg superheat is a danger zone; 0 = flooded operation | risk of liquid to the compressor | yes | K0WeVON0B5o |
| chart limit | a dash at 63 deg wet bulb / 95 deg outdoor = zero target superheat (unsafe condition) | system not designed to run there | yes | K0WeVON0B5o |
| required pressure differential for TXV control | ~100 psi between evaporator and liquid-line inlet | below this (e.g. outdoor below ~65F) the TXV loses control | yes | IfLfXx9CsGs |
| residential AC evaporator superheat target | 6-14F (most fall 8-12F) | at the outlet of the evaporator coil | yes | IfLfXx9CsGs |
| low-suction example | 105 psi R410A = 33.6F evaporator temp, ~35F design split at 400 CFM/ton | illustration | yes | IfLfXx9CsGs |
| insulating a factory bulb | raised superheat by ~3F | bulb strapping/insulation matters | yes | IfLfXx9CsGs |
| freezing threshold | below ~300-350 CFM per ton risks freezing | airflow | yes | IfLfXx9CsGs |
| minimum outdoor ambient for standard AC | ~65F | below this you lose control of evaporator-to-liquid differential | yes | IfLfXx9CsGs |
| factory charge | 7 lb 13 oz | recovery hit factory charge on the nose | yes | FDG0e6wCUiM |
| evacuation | stayed below 1,000 microns after 10-minute hold | decay/leak check via true blue kit | yes | FDG0e6wCUiM |
| charge added | factory 3 lb back into the machine | hit subcool on the head, superheat trending down from ~30 | yes | FDG0e6wCUiM |
| Target superheat example (74 wet bulb, 105 outdoor) | ~18.5 | from the superheat chart | yes | hPAvI0eIXQk |
| Target superheat (75/75) | ~35 | chart example | yes | hPAvI0eIXQk |
| Target superheat (56 wet bulb, 75 outdoor) | ~6.5 | chart example | yes | hPAvI0eIXQk |
| Refrigerant velocity | suction line ~800 ft/min, liquid line ~100-400 ft/min | Ty cites this is from Google/AI, not memorized | yes | hPAvI0eIXQk |
| Liquid line sizing | 3/8 liquid line used from 1.5 ton to 5 ton | refrigerant flows faster on the 5 ton | no | hPAvI0eIXQk |
| ZP100 valve actual limit | rated 100 psi but limits closer to ~90 psi | a less common commercial MOP valve | yes | c5d6KGB7s7A |
| P-number vs actual | actual max is usually ~10 psi below the labeled number (a range, not fixed) | e.g. a 'P40' really limits around 30 psi | yes | c5d6KGB7s7A |
| dual-temp case example | one case running 28F or -7F on a switch; a pure-R22 valve would show ~40F superheat at 28F if dialed in at -7F | why cross-charge (glide) valves give stable superheat across temperatures | no | c5d6KGB7s7A |
| line-length guidance | ~25 ft AC line set suits MOP; ~200 ft favors a CPR | when starving at the valve becomes a disadvantage | no | c5d6KGB7s7A |
| rack defrost blip | a rack at 20 psi might blip to ~21 psi when a circuit leaves defrost | why racks don't need MOP valves | no | c5d6KGB7s7A |
| Motor winding resistance (small EEV) | 100 ohms +/- 10% | black-to-white testing motor integrity | yes | wqDGfQHpcu0 |
| Degrees rotation per step | 3.6 degrees | 360/100; ~2500 steps = 25 rotations stop-to-stop on small valves | yes | wqDGfQHpcu0 |
| Common step counts | 2500 (small) / 6386 (large) | full open to full closed step count by valve size | yes | wqDGfQHpcu0 |
| Overdrive setting on startup (Danfoss guidance cited) | set 2500-step valve to 3500 steps; set 6386 valve to ~6500 and force closed | synchronizing/overdriving valve to zero | yes | wqDGfQHpcu0 |
| Pulse valve controller cycle | 6-second pulses (50% = on 3s / off 3s) | pulse-width-modulation timing | yes | wqDGfQHpcu0 |
| Digital compressor IDCM cycle example | 20-second cycle (50% = 10s loaded / 10s unloaded) | another PWM example | yes | wqDGfQHpcu0 |
| Modern EPR cost | ~$1000 (electronic even more) | why customers wouldn't use them if not required | yes | 4VnKZXFXnAo |
| Refrigerant glide examples | R22 = 0; 404A ~0.5-1 psi at midpoint; 407/448A/449A ~11-12 degrees glide | how critical midpoint is when setting EPR | yes | 4VnKZXFXnAo |
| A8 orifice sizing | orifice number = 1/8 inch increments (e.g. sport 8 = 1 inch, sport 16 = 2 inch) | A8/sport valve port sizing | yes | 4VnKZXFXnAo |
| Sorit pilot pressure (CROT) setting | printed minimum 50 psi over suction; best practice 90 psi over high suction | hot-gas pilot pressure for pilot-operated EPR | yes | 4VnKZXFXnAo |
| Standard CROT pressure range | 30-110 psi (standard); special Hill Phoenix X55 CROT 80-200 psi | low temp uses 110 max; medium temp may need the 200 special | yes | 4VnKZXFXnAo |
| A8 minimum pressure drop | ~1 psi minimum required (Sorit can go to 0.5/near zero) | A8 gets its energy from the differential; Sorit is pilot-operated | yes | 4VnKZXFXnAo |
| Solenoid port sizing | port number = 1/32-inch orifice increment | solenoids sized by BTU load, not pipe size | yes | sPRmJQj5QbE |
| Solenoid target pressure drop | 1-5 psi acceptable; ~3 psi is ideal (middle) | too big won't close, too small starves TXV | yes | sPRmJQj5QbE |
| Sight-glass moisture paper | replaceable, ~6-hour book time, up to 1-7/8 inch | reactivates green under vacuum until expired | yes | sPRmJQj5QbE |
| Cut-in / cut-out strategy | manufacturer target +2 / -2 degrees (e.g. 31 target = 29 cut-out / 33 cut-in) | liquid-line solenoid freeze-protection safety | yes | sPRmJQj5QbE |
| Liquid-temp correction | x1.5 at 50F subcooled liquid (1.0 at 100F) | solenoid AND TXV sizing | yes | sPRmJQj5QbE |
| RCU liquid design temp | ~95F central FL (100F near Miami, ~90F Georgia) | remote condensing unit liquid correction | yes | sPRmJQj5QbE |
| Pressure-drop correction | 1.0 at 100 psi across valve; ~90 psi is the working edge | below 100 psi the valve shrinks and controls poorly | yes | vG1KKcrtwAI |
| Liquid-temp correction | ~1.5 at 50F liquid (1.0 at 100F) | subcooling enlarges valve capacity | yes | vG1KKcrtwAI |
| Evaporator-temp effect | 1.5-ton valve at 40F ~1.53 ton; at -40F ~1 ton (~33% loss) | low evaporator temp shrinks capacity | yes | vG1KKcrtwAI |
| TXV hunting threshold (AC context cited) | below ~6 degrees superheat TXVs get unstable/hunt | minimum stable superheat | yes | vG1KKcrtwAI |
| Normal at-temp swing | 15-20 degrees on at-temp ice cream (~5 on a medium open case, ~1-2 on meat prep) | oversized low-temp valves swing more by design | yes | vG1KKcrtwAI |
| Superheat / TD alignment | 10 degrees superheat + 10 degree TD -> supply air = superheat temp (why bulbs aren't insulated in supermarkets) | insulate the bulb only when superheat/TD differ a lot (e.g. 4-degree superheat) | yes | vG1KKcrtwAI |
| target subcool with TXV | 12F (data-tag spec) | charging the TXV conversion | yes | M-_Zi123GtI |
| delivered capacity | ~31,500-33,000 BTU (3-ton, ~350 CFM/ton, ~1050 CFM) | Testo 605i cooling/heating power mode | yes | M-_Zi123GtI |
| nitrogen pressure test | ~154 PSI held (pumped down and recovered first) | standing pressure test then evacuation to ~300 microns | yes | M-_Zi123GtI |
| superheat gate for quoting TXV | over 25 degrees (with split over 20) | Superheat normal-or-low (under 25) or split over 20 means TXV is doing its job - off limits | no | M-Z72kAPTbM |
| slipping-compressor suction | often above 160-170 psi | A slipping compressor pushes suction higher than a wide-open TXV can | no | M-Z72kAPTbM |
| factory superheat range | ~8 to 14 degrees | typical non-adjustable AC TXV factory setting | no | optoVysiApE |
| TXV rust-through timeline | usually at least 5 years | how long before a rusting head leaks/loses charge, worse in coastal/high-moisture | no | optoVysiApE |
| bulb mounting positions | 10 & 2 or 9 & 3 o'clock on a 7/8 line; toward the middle on larger lines; never on the bottom | proper TXV bulb clocking for heat transfer | yes | optoVysiApE |
| superheat when system off | zero degrees | suction line temp equals suction saturation when off | yes | hZR_k_G3lZM |
| typical TXV outlet superheat | manufacturer ~5-12°F at evaporator outlet | Les sees 6-15° at the condenser depending on line set length | yes | j23fGgK4_t4 |
| target superheat range | 6-8°F (Parker: 6-8, 6-12 for AC/R410A) | manufacturer outlet superheat targets | yes | fmYnQu7utIQ |
| adjustment increment | half turn (180°) at a time | one flip of the wrench per test | yes | fmYnQu7utIQ |
| run time before adjusting/re-checking | at least 15 minutes, more likely 30 | let head pressure build and settle | yes | fmYnQu7utIQ |
| example valve capacity | 1.5 to 3 tons | the Parker adjustable kit valve shown | yes | fmYnQu7utIQ |
| factory stem default | 50% stem height | most valves come set at 50% | yes | fmYnQu7utIQ |

## Field tips (the trick that saves time)

- Practice brazing valves in until you can do it in your sleep, keeping heat away from the bulb and diaphragm (high-carbon heat-treated steel loses its temper if overheated).  *(id: B7PLADtN06c)*
- Place the field filter drier in the liquid line close to the evaporator/TXV, and flow nitrogen while brazing.  *(id: B7PLADtN06c)*
- Warm the bulb in your hand as a diagnostic (checks bulb charge and can un-stick a gummy valve) but understand it doesn't fix the root cause.  *(id: B7PLADtN06c)*
- Read the valve's degrees-per-turn adjustment rate first; many AC valves are set by backing all the way in then out a specified number of turns.  *(id: B7PLADtN06c)*
- Unhook the blower and watch the freeze pattern to spot irregular restrictions.  *(id: B7PLADtN06c)*
- Measure cap tube ID and OD with a caliper (about $8) or a dedicated cap-tube gauge set to size a replacement.  *(id: DtINXanblJw)*
- Insert the cap tube about 1/4 to 1/2 inch past the joint/insertion point, not to the bottom of the pipe (which restricts flow and creates noise) and not blocking it.  *(id: DtINXanblJw)*
- Prefer going back with a thicker-wall cap tube of the same inner diameter; wall thickness doesn't change flow, inner diameter does.  *(id: DtINXanblJw)*
- When rebrazing, tack the tube with a small dab of solder (or hold it with needle-nose pliers) and apply just enough heat, since cap tubes bend, twist, or crack easily when hot or under stress.  *(id: DtINXanblJw)*
- Clear drilled shavings out of the insertion point before brazing.  *(id: DtINXanblJw)*
- Power heads are inexpensive, so if the screen is good and the power head's coating is failing, just change the 43 mm power head and clean the screen - that will likely solve the not-making-temperature problem.  *(id: CvqE7RbYL-g)*
- Mount the bulb at the 4/8 o'clock (or 9/3) position on a horizontal free-draining suction line; if you can see daylight between bulb and line it won't work well.  *(id: RIa2Xhzp5qs)*
- Orient the bulb, suction line and fastener so you can tighten without crushing the bulb; tap the external equalizer into the top of the suction line downstream of the bulb to avoid contamination.  *(id: RIa2Xhzp5qs)*
- Check airflow again before quoting; an internally impacted or fouled coil screws up all readings.  *(id: 9Hz0af0fnsg)*
- A low subcool with high superheat and low suction indicates low charge, not a TXV; a TXV issue shows normal-to-high subcool and head.  *(id: 9Hz0af0fnsg)*
- For a fast one-hose evacuation, connect the hose to the suction line, read the micron gauge on the liquid line, and pull the Schrader on the suction line.  *(id: r18UybHTvv4)*
- Consult manufacturer literature to identify which wires are which and the expected resistance before testing.  *(id: fd0kGz0XckE)*
- Get rid of component-focus: diagnose the whole system — ambient conditions, load, airflow, cleanliness — a callout for one thing often reveals other issues that pay for themselves in energy savings.  *(id: ibZN1vzyPHU)*
- Aim for the lowest stable superheat and lowest sub-cool practical: a colder coil removes more moisture, and lower liquid-line temp entering the metering device means less flash gas.  *(id: ibZN1vzyPHU)*
- Consider 'evaporator temperature' instead of 'suction saturation' — more superheat means more of the coil is dedicated to superheating (warmer) rather than boiling, raising the average coil temperature and hurting efficiency/dehumidification.  *(id: ibZN1vzyPHU)*
- In low-temp refrigeration the enemy is low load (low mass flow can't cool the compressor); lower superheat and adjusted compression ratio aid compressor cooling and longevity.  *(id: ibZN1vzyPHU)*
- Going from a piston to a TXV usually gives the biggest bang for the buck (especially under high wet-bulb); an EEV adds incremental benefit plus data (percent-open logging) and eliminates the fragile sensing bulb.  *(id: ibZN1vzyPHU)*
- EEVs enable floating head pressure control (let condensing pressure drop at night/low ambient) and variable-speed condenser fans, saving energy — supermarkets adopted first because of high energy cost and thin margins.  *(id: ibZN1vzyPHU)*
- Measure superheat at the air handler for a clear picture of what just happened in the coil, or at the compressor to see how refrigerant returns to it.  *(id: Xuy4mtdXlRI)*
- Don't confuse outdoor dry-bulb with indoor — a common calculator error is entering a measurement in the wrong slot.  *(id: Xuy4mtdXlRI)*
- Setting charge on a piston is harder than a TXV (which self-adjusts): add refrigerant slowly and let the coil come down to temperature before judging, because it overshoots easily.  *(id: Xuy4mtdXlRI)*
- If measured superheat is below target while setting charge on a fixed orifice, recover refrigerant into a recovery machine.  *(id: Xuy4mtdXlRI)*
- A piston is a small hunk of brass that slides back and forth to seat/unseat with the mode of operation and can be swapped for different sizes; a capillary tube is just a length of tubing that creates the pressure drop.  *(id: qV-DIqIxPGk)*
- The TXV is one of the most misunderstood and often-blamed components.  *(id: qV-DIqIxPGk)*
- Make a mark up the spindle to count turns accurately when making many small adjustments.  *(id: IPMIv-ro3kg)*
- Mount the bulb on the suction line at the evap outlet per the diameter guide (10-and-2 position for 3/8-5/8, side for 3/4-7/8+, never the bottom) and insulate it well.  *(id: IPMIv-ro3kg)*
- Most valves that 'need adjusting' actually failed from overheating during brazing, no nitrogen flow (cupric oxide), improper line dryers, or a poor evacuation - fix the real cause.  *(id: IPMIv-ro3kg)*
- In built-up/refrigeration systems, don't let the valve run too open and cause flood-back to the compressors.  *(id: IPMIv-ro3kg)*
- Measure wet bulb with a good digital psychrometer at/near the return grille (old sling psychrometers are too slow as conditions change).  *(id: K0WeVON0B5o)*
- Take temperature measurements where air is well mixed and not exposed to radiant hot/cold surfaces.  *(id: K0WeVON0B5o)*
- Apps like Field Piece JobLink or MeasureQuick continuously track the moving target superheat for accuracy.  *(id: K0WeVON0B5o)*
- Exercise a valve in a heat-pump market by running it back and forth heat-to-cool rather than heating the bulb by hand.  *(id: IfLfXx9CsGs)*
- Listen at the valve for a hissing/flashing sound indicating vapor in the liquid line, regardless of outdoor subcool.  *(id: IfLfXx9CsGs)*
- Zero/calibrate your manifold (even Testo 550s) to atmosphere every time; analog gauges can be 4-5F off, which is the whole difference between a good and failed superheat reading.  *(id: IfLfXx9CsGs)*
- Strap the bulb snug with brass/copper and insulate it; if the flare port has no core depressor make sure the Schrader core is removed or the external equalizer won't work.  *(id: IfLfXx9CsGs)*
- Replace the liquid line dryer whenever you replace a valve because you don't know what got into it (moisture, carbon, acids, corrosion-inhibitor additives).  *(id: IfLfXx9CsGs)*
- Keep a bucket of rags to keep the filter dryer ends cool while brazing so corrosion isn't a problem.  *(id: FDG0e6wCUiM)*
- Put the dryer filter outside the condenser so the circuit can be pumped down and serviced next time without opening the whole system.  *(id: FDG0e6wCUiM)*
- Pull the Schrader cores during evacuation so they don't impede the vacuum.  *(id: FDG0e6wCUiM)*
- Anytime you change a TXV, add a sight glass so you can see what's actually happening inside; also consider a service port before the metering device (especially on long attic line sets) to measure subcooling right there.  *(id: hPAvI0eIXQk)*
- The subcooling table at the bottom of the fixed-orifice chart is NOT for charging — it just gives an idea; subcooling drops as outdoor temp rises and rises as outdoor temp drops.  *(id: hPAvI0eIXQk)*
- When training, say 'subcooled LIQUID', 'superheated VAPOR', and 'saturated = P-SAT converted temperature' so people connect the states faster.  *(id: hPAvI0eIXQk)*
- Airflow is the first thing to check — most TXVs are condemned because of airflow; second question is always 'what metering device is it?'  *(id: hPAvI0eIXQk)*
- Flowing nitrogen while brazing, a good vacuum, and changing the filter drier keep the metering device clean.  *(id: hPAvI0eIXQk)*
- Match the valve/powerhead to the application: liquid-filled for full-range single-superheat, vapor-charged MOP for small low-temp boxes and AC (VGA), cross-charged for blended-refrigerant/glide (dual-temp) cases.  *(id: c5d6KGB7s7A)*
- On parallel rack systems don't use MOP; use EPRs to hold evaporators at fixed temperatures and keep circuits running continuously (not cycling) - starting/stopping is one of the worst things for a compressor and its oil system.  *(id: c5d6KGB7s7A)*
- Pull compressor operating-envelope data (Copeland, Carlyle, Bitzer) to pick a valve whose limiting range is just above your expected operating pressure, not far above it.  *(id: c5d6KGB7s7A)*
- Best practice with stepper EEVs: if the valve is assembled, put SMA-12 on it, drive to zero/closed, then force the controller to 0% before reconnecting so controller and valve agree.  *(id: wqDGfQHpcu0)*
- NEVER drive the valve to (or past) zero with it disassembled — you can push the pin off the end and ruin a ~$1000 valve; if apart, only move it to 30-40%.  *(id: wqDGfQHpcu0)*
- When unplugging a valve to check wiring, force the valve in the controller first so it won't try to move (and lose count) while disconnected.  *(id: wqDGfQHpcu0)*
- Insulate temperature sensors on electronic valves (they work better); check/clean the internal screen and verify the correct orifice size is installed on pulse valves — wrong orifice = can't make superheat at 100%.  *(id: wqDGfQHpcu0)*
- Many controllers drive the valve to 0% once a day (often midnight) to overdrive/re-sync — a daily dip on the subcooler temp graph is normal; a dry-contact input can trigger this on demand.  *(id: wqDGfQHpcu0)*
- On a sport/Sorit valve the service tap ('T') is on the evaporator/inlet side you're controlling — screw your gauge there to set the pressure; if you can't find a fitting on the evaporator side it's on the valve.  *(id: 4VnKZXFXnAo)*
- A8 valves are fully rebuildable in place and you can change the cartridge to change the orifice size without replacing the whole valve — a spare cartridge must match the orifice size.  *(id: 4VnKZXFXnAo)*
- Set the CROT pilot pressure first (90 over high suction) before adjusting any Sorit EPRs; the pilot line must carry superheated discharge gas — if that half-inch pilot line feels hot, a Sorit is blowing hot gas into suction (internal mini-EPR stuck open); if it feels cold/sweating you're condensing and have no valve control.  *(id: 4VnKZXFXnAo)*
- If a CROT fails and you're a week out, drop a quarter-inch hose between an A9's two ports (Outlet-operated A9) as a field substitute pilot regulator rather than straight-piping and losing regulation.  *(id: 4VnKZXFXnAo)*
- Turn sight glasses sideways so you can read rivering (Kaiser mounts them all the same way on the subcooler end, so half face into the rack — use a mirror or phone camera).  *(id: sPRmJQj5QbE)*
- Size solenoids from the Sporlan chart using the BTU load AND the liquid-temp correction factor; the ones causing VPR failures were sized by pipe.  *(id: sPRmJQj5QbE)*
- Set EPRs to the manufacturer TARGET temperature (the cut-in/cut-out is a freeze safety); running on cut-in/cut-out means the product's cold but you're cycling and destroying the rack.  *(id: sPRmJQj5QbE)*
- For RCU (remote condensing unit) sizing there's no rack legend — read the print or tag off the case BTUs; size the load on the evaporators, and the condenser should be larger, not the sizing basis.  *(id: sPRmJQj5QbE)*
- Carry balanced-port SBQE Q-bodies (change the cartridge to change tonnage) rather than a bag of valves; never remove the $1 strainer off a Danfoss valve without a crush washer.  *(id: vG1KKcrtwAI)*
- For a stable superheat reading you must have a stable suction pressure held ~15-20 minutes (copper lags); if suction is moving, the reading is meaningless.  *(id: vG1KKcrtwAI)*
- The external equalizer line should carry NO liquid — if it's flowing refrigerant/frosting back to the rack, the valve is worn and leaking past the pin; replace it.  *(id: vG1KKcrtwAI)*
- Bulb at 3-9 o'clock (or ~4-5 o'clock), clean/sanded copper, clamped hard — never on a fitting, never zip-tied; insulating/mastic is best-practice but rarely worth it in supermarkets because superheat and supply-air temps match.  *(id: vG1KKcrtwAI)*
- Remove the little in-case liquid-line driers on new cases before final piping if the system is dirty (they're one-and-done desiccant with no way to reactivate).  *(id: vG1KKcrtwAI)*
- Keep the main suction-header pressure below the coldest evaporator's regulated setting so every EPR can control.  *(id: OEI56EuoJtg)*
- Make the external-equalizer port by grooving the copper with a file then piercing with a scratch awl/nail set - never a drill (shavings) - and remove the Schrader core from the equalizer or it won't work.  *(id: M-_Zi123GtI)*
- Cut line dryers out rather than unsweat; use a chatleff fitting with Nylog on threads and leave teflon overhang off when soldering; strap and insulate the sensing bulb.  *(id: M-_Zi123GtI)*
- Pump down and hold the system under nitrogen (braze setting) before opening so lines stay dry when you swap the metering device.  *(id: M-_Zi123GtI)*
- Pull the vacuum through core-removal tools with big hoses, not through the manifold gauges.  *(id: M-_Zi123GtI)*
- On a heat pump you can also run it in heat mode to help diagnose/break a slightly stuck TXV free.  *(id: M-Z72kAPTbM)*
- A closed-down TXV makes subcool respond immediately to added refrigerant ('stacking against a closed door') - a fast way to confirm.  *(id: M-Z72kAPTbM)*
- Capture split AND return temperature (not just the total split number) so you can distinguish an airflow-closed TXV from a truly failed one.  *(id: M-Z72kAPTbM)*
- Revisit HVAC School's ~6 TXV videos/podcasts - each pass unlocks another layer as your experience grows.  *(id: M-Z72kAPTbM)*
- Mount the bulb tight on a straight section (not an elbow/braze joint), upstream of the external equalizer, insulated, and clean the copper first  *(id: optoVysiApE)*
- Adjustment rule: don't touch the valve - turn clockwise increases spring pressure/superheat, counterclockwise lowers it; only adjust as the last resort in refrigeration  *(id: optoVysiApE)*
- To tap a small line into a larger one, score with a file edge and punch with an awl (not a drill) to avoid copper shards; leave extra cap tube inserted so braze doesn't close it off  *(id: optoVysiApE)*
- Don't braze over a rub-out leak on distributor tubes/equalizer lines - it sucks braze in and closes the small line; cut in a coupling instead  *(id: optoVysiApE)*
- Place the liquid line drier close to the indoor unit (inside in salt/coastal environments) to protect the metering device and avoid rust  *(id: optoVysiApE)*
- A hard shut-off TXV is desirable because it prevents refrigerant migration to the compressor crankcase (oil has an affinity for refrigerant) when the system is off.  *(id: hZR_k_G3lZM)*
- Downside: the compressor starts under slightly more imbalance/load — suction drops quickly on startup then rises as the valve reopens.  *(id: hZR_k_G3lZM)*
- The bulb-warm/ice-water test (warm in hand vs cup of ice water) confirms the valve and bulb are acting, but doesn't rule out internal clogging or a plugged inlet screen.  *(id: j23fGgK4_t4)*
- Properly insulate and snugly strap the sensing bulb so it reads the line temperature, not the air.  *(id: j23fGgK4_t4)*
- Internally-equalized valves read pressure at the valve (less accurate); externally-equalized read at the evaporator outlet (more accurate) — the vast majority are externally equalized.  *(id: j23fGgK4_t4)*
- Don't adjust a valve with panels off making rapid back-and-forth changes — put everything back together and monitor 15 minutes between half-turn adjustments to avoid overshooting and damaging the valve.  *(id: fmYnQu7utIQ)*
- The most common real TXV failures are foreign matter jamming it, sticking (usually closed = high superheat), and the bulb losing its charge (slams shut); adjusting the spring won't fix those.  *(id: fmYnQu7utIQ)*
- Install the liquid line filter dryer as close as possible to the valve inlet to protect it.  *(id: fmYnQu7utIQ)*

## Bryan's characteristic phrases on this topic

- "it requires an increase in superheat in order to open the valve"  *(id: B7PLADtN06c)*
- "It's a heart because I love it."  *(id: DtINXanblJw)*
- "As it collides, it creates friction. Friction creates heat. Creates energy. Slows it down even more. And it drops the pressure because now it's getting choked"  *(id: DtINXanblJw)*
- "a thermostatic expansion valve's job is to control superheat where that bulb's located"  *(id: RIa2Xhzp5qs)*
- "it's not a light switch"  *(id: RIa2Xhzp5qs)*
- "Never quote a TXV that has a normal or low super heat"  *(id: 9Hz0af0fnsg)*
- "It takes 480 pulses for the valve to fully open or fully close."  *(id: fd0kGz0XckE)*
- "get rid of this component focus"  *(id: ibZN1vzyPHU)*
- "why is it variable why why not just always put it at 10"  *(id: Xuy4mtdXlRI)*
- "if you are new to the trade under no circumstances are you allowed to condemn or replace a TXV unless you fully understand it because it is very misunderstood"  *(id: qV-DIqIxPGk)*
- "you almost never need to adjust to TX v almost never unless you're working in like commercial grocery refrigeration"  *(id: IPMIv-ro3kg)*
- "target superheat is a moving target"  *(id: K0WeVON0B5o)*
- "zero superheat is flooded operation"  *(id: K0WeVON0B5o)*
- "If you have low super heat, do not add more charge."  *(id: IfLfXx9CsGs)*
- "I call it a constant superheat valve"  *(id: IfLfXx9CsGs)*
- "it's this beautiful beautiful dance"  *(id: hPAvI0eIXQk)*
- "You got to chart your pants"  *(id: hPAvI0eIXQk)*
- "Do you see a connection"  *(id: hPAvI0eIXQk)*
- "we kill compressors... compressors don't die we murder them... one of the worst things we can do to a compressor start it"  *(id: c5d6KGB7s7A)*
- "When the TXV closes down more, the refrigerant backs up against it, and that's where we get our higher pressure and higher subcool"  *(id: M-Z72kAPTbM)*
- "maybe don't pull them out and replace them with pistons"  *(id: optoVysiApE)*
- "stop touching valves"  *(id: optoVysiApE)*
- "Let's start a revolution of calling them CSVs."  *(id: j23fGgK4_t4)*
- "the job of the expansion valve is to maintain a constant superheat not a constant suction pressure"  *(id: fmYnQu7utIQ)*

## Guest wisdom on this topic

- **Jamie Kitchen:** Superheat is your friend for diagnosing a TXV: after eliminating charge and upstream obstructions, high superheat = a refrigerant-flow problem, low superheat = an airflow/load problem.  *(id: B7PLADtN06c)*
- **Jamie Kitchen:** An internally equalized valve behind a distributor under-feeds because the distributor's pressure drop makes the valve read a higher evaporator pressure than reality; use externally equalized valves on multi-circuit coils.  *(id: B7PLADtN06c)*
- **Jim Jansen:** Contamination is the single biggest cause of TXVs not working; the TXV also acts as a good secondary filter  *(id: RIa2Xhzp5qs)*
- **Jamie Kitchen:** Superheat removes capacity and raises the average evaporator temperature above saturation — from an energy standpoint you want the minimum superheat that keeps the system stable and protects the compressor, and no more.  *(id: ibZN1vzyPHU)*
- **Jamie Kitchen:** An EEV maintains minimum stable superheat automatically (Danfoss holds the patent on minimum-stable-superheat control; others do fixed superheat), saving tech time fine-tuning and taking the discomfort out of superheat for techs.  *(id: ibZN1vzyPHU)*
- **Matthew Taylor:** A CPR restricts vapor at the compressor outlet side to cap compressor pressure without affecting superheat, whereas an MOP starves liquid into the evaporator and raises superheat - so on larger systems/long lines the CPR is preferred (though not economical on tiny systems).  *(id: c5d6KGB7s7A)*
- **Matthew Taylor:** On a rack you want the circuits feeding refrigerant almost constantly; the EPR just holds each evaporator at a fixed boiling temperature and lets the compressors 'eat', because cycling circuits on and off is what murders compressors.  *(id: c5d6KGB7s7A)*
- **Corey Cruse:** EPRs throttle suction gas to hold evaporator saturation fixed and achieve constant run time between defrosts  *(id: OEI56EuoJtg)*
- **Austin:** You'll never have superheat on a wide-open TXV, so if you see superheat with a really high suction/low head/low subcool, suspect a slipping compressor or reversing valve  *(id: M-Z72kAPTbM)*
- **Craig Migliaccio:** If a poorly mounted bulb reads warmer it overfeeds/floods the coil; heat picked up in a long suction line (attic/underground) shows as total superheat higher than evaporator superheat - back up and measure inside too  *(id: optoVysiApE)*
- **Craig Migliaccio:** Heat-pump TXVs come in pairs with a check-valve bypass so the inactive-mode TXV (indoor for heating, outdoor for cooling) flows freely in one direction and restricts in the other  *(id: optoVysiApE)*
- **Les Broadbent:** An automatic expansion valve held a constant inlet pressure and couldn't regulate superheat/subcool across varying load conditions, which is why the TXV solved the problem.  *(id: j23fGgK4_t4)*
- **Les Broadbent:** TXVs most often fail shut, and the bulb losing its charge is one of the most common failures.  *(id: j23fGgK4_t4)*

## Episodes in this compendium

| Title | Video id | Guests |
|---|---|---|
| (Podcast) TXV Operation, Diagnosis, and Failure w⧸ Jamie Kitchen | B7PLADtN06c | Jamie Kitchen |
| Capillary Tube Repair and Brazing Class | DtINXanblJw | (solo) |
| Common Refrigeration TXV Issue | CvqE7RbYL-g | (solo) |
| Demystifying the Thermostatic Expansion Valve w⧸ Jim Jansen | RIa2Xhzp5qs | Jim Jansen |
| Diagnosing a Failed TXV | 9Hz0af0fnsg | (solo) |
| Does a TXV Shut under Vacuum？ | r18UybHTvv4 | (solo) |
| EEV Troubleshooting in 3D： A Guide for HVAC Techs | fd0kGz0XckE | (solo) |
| Electronic Expansion Valves (EEV) w⧸ Jamie Kitchen (Podcast) | ibZN1vzyPHU | Jamie Kitchen |
| Finding Target Superheat | Xuy4mtdXlRI | (solo) |
| HVACR Metering Device Basics | qV-DIqIxPGk | (solo) |
| Hard Shut Off TXVs | SnBnvL0u_9A | (solo) |
| How to Adjust a TXV, TEV or TX Valve | IPMIv-ro3kg | (solo) |
| How to Find Target Superheat | K0WeVON0B5o | (solo) |
| How to Properly Diagnose a Failed TXV | IfLfXx9CsGs | (solo) |
| How to Replace a TXV | FDG0e6wCUiM | (solo) |
| Metering Device Troubleshooting： Subcooling, Sight Glasses & Restrictions | hPAvI0eIXQk | Ty Branaman |
| Q&A - EPR and Pressure Limiting Valves w⧸ Matthew Taylor | c5d6KGB7s7A | Matthew Taylor |
| Rack Refrigeration Cycle Part 10 - Electronic Expansion Valves | wqDGfQHpcu0 | Matthew Taylor |
| Rack Refrigeration Cycle Part 12 - EPR | 4VnKZXFXnAo | Matthew Taylor |
| Rack Refrigeration Cycle Part 8 - Sight Glass and Liquid Line Solenoid | sPRmJQj5QbE | Matthew Taylor |
| Rack Refrigeration Cycle Part 9 - Mechanical Expansion Valves | vG1KKcrtwAI | Matthew Taylor |
| Rack Refrigeration Evaporator Pressure Regulation | OEI56EuoJtg | Corey Cruse |
| Replacing a Piston with a TXV Using the Danfoss TR6 Kit | M-_Zi123GtI | (solo) |
| TXV Diagnosis: Superheat, Subcool & Split Temps | M-Z72kAPTbM | Austin |
| What a TXV Does (and why techs need to stop replacing them with a piston) | optoVysiApE | Craig Migliaccio |
| Why a Hard Shut Off TXV Closes | hZR_k_G3lZM | (solo) |
| Why a TXV instead of a TEV？.. or a CSV？ | j23fGgK4_t4 | Les Broadbent |
| Why and How to Adjust a TXV ⧸ TEV | fmYnQu7utIQ | (solo) |

## Change log

- 2026-07-08: Initial extraction from 28 episodes (parallel-subagent structured extraction, Opus).
