"""
WS-B — Nameplate OCR Prompt
Sent to Gemini 2.5 Flash with 1-2 nameplate photos.

Extracts the 10 Step Zero fields from HVAC equipment nameplates.
Returns structured JSON that is cross-referenced against brands.series
and legacy_model_prefixes to auto-detect refrigerant type, metering device,
and year of manufacture.
"""

NAMEPLATE_OCR_PROMPT = """
You are an expert HVAC nameplate reader. Analyze the provided nameplate photo(s)
and extract ALL visible specifications. Return ONLY a valid JSON object — no markdown,
no explanation, no code blocks.

PHOTO CONTEXT:
- Photo 1 (if provided): Outdoor unit (condenser/heat pump) nameplate
- Photo 2 (if provided): Indoor unit (air handler/furnace) nameplate

EXTRACTION RULES:
1. Read EVERY character exactly as printed — do not guess or round.
2. For Model # and Serial #: extract the COMPLETE string including all letters,
   numbers, and separators. Example: "24ACC636A003" not "24ACC636".
3. For tonnage — check in this exact order:
   a. BTU/h label on the nameplate (18000=1.5t, 24000=2t, 30000=2.5t, 36000=3t, 42000=3.5t, 48000=4t, 60000=5t)
   b. "Tons" label on the nameplate
   c. Decode from model number using brand-specific pattern (see MODEL DECODE RULES below)
4. For refrigerant: look for "R-410A", "R-22", "R-32", "R-454B" labels.
5. For electrical specs: MCA = "Minimum Circuit Ampacity", MOCP = "Max Overcurrent".
6. For RLA/LRA: these are on the compressor section. RLA = "Rated Load Amps",
   LRA = "Locked Rotor Amps".
7. For factory charge: look for "Factory Charge", "Refrigerant Charge", or oz/lbs weight.
8. If a field is not visible or not readable, set it to null.
9. Confidence: your 0-100 confidence that each field is correctly read.

MODEL DECODE RULES (use when tonnage not printed on nameplate):
All standard brands except Mitsubishi encode tonnage as a 3-digit BTU/1000 code
embedded in the model number. Divide by 12 to get tons.

BTU code → tons table:
  018 → 1.5 tons
  024 → 2.0 tons
  030 → 2.5 tons
  036 → 3.0 tons
  042 → 3.5 tons
  048 → 4.0 tons
  060 → 5.0 tons

Brand-specific examples:
  Carrier    : 24ACC6[36]A003  → digits 7-8 = "36" → 3.0 tons
  Bryant     : LCA[036]A003    → "036" → 3.0 tons  (identical to Carrier)
  Payne      : PA14[036]JK     → "036" → 3.0 tons  (identical to Carrier)
  Trane      : 4TTR60[36]L     → "036" or "36" → 3.0 tons
  Am. Std.   : 4A7A[036]A      → "036" → 3.0 tons  (identical to Trane)
  Lennox     : 16ACX[036]-230  → "036" → 3.0 tons
  Goodman    : GSX14[036]      → "036" → 3.0 tons
  Amana      : ASX14[036]      → "036" → 3.0 tons  (identical to Goodman)
  Daikin     : DN14[036]       → "036" → 3.0 tons  (identical to Goodman)
  Rheem      : RA14AZ[036]JK   → "036" → 3.0 tons
  Ruud       : UA14[036]       → "036" → 3.0 tons  (identical to 