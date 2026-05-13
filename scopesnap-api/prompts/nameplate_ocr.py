"""
WS-B -- Nameplate OCR Prompt
Sent to Gemini 2.5 Flash with 1-2 nameplate photos.

Extracts the 10 Step Zero fields from HVAC equipment nameplates.
Returns structured JSON that is cross-referenced against brands.series
and legacy_model_prefixes to auto-detect refrigerant type, metering device,
and year of manufacture.
"""

NAMEPLATE_OCR_PROMPT = """
You are an expert HVAC nameplate reader. Analyze the provided nameplate photo(s)
and extract ALL visible specifications. Return ONLY a valid JSON object -- no markdown,
no explanation, no code blocks.

PHOTO CONTEXT:
- Photo 1 (if provided): Outdoor unit (condenser/heat pump) nameplate
- Photo 2 (if provided): Indoor unit (air handler/furnace) nameplate

EXTRACTION RULES:
1. Read EVERY character exactly as printed -- do not guess or round.
2. For Model # and Serial #: extract the COMPLETE string including all letters,
   numbers, and separators. Example: "24ACC636A003" not "24ACC636".
3. For tonnage -- check in this exact order:
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

BTU code -> tons table:
  018 -> 1.5 tons
  024 -> 2.0 tons
  030 -> 2.5 tons
  036 -> 3.0 tons
  042 -> 3.5 tons
  048 -> 4.0 tons
  060 -> 5.0 tons

Brand-specific examples:
  Carrier    : 24ACC6[36]A003  -> digits 7-8 = "36" -> 3.0 tons
  Bryant     : LCA[036]A003    -> "036" -> 3.0 tons  (identical to Carrier)
  Payne      : PA14[036]JK     -> "036" -> 3.0 tons  (identical to Carrier)
  Trane      : 4TTR60[36]L     -> "036" or "36" -> 3.0 tons
  Am. Std.   : 4A7A[036]A      -> "036" -> 3.0 tons  (identical to Trane)
  Lennox     : 16ACX[036]-230  -> "036" -> 3.0 tons
  Goodman    : GSX14[036]      -> "036" -> 3.0 tons
  Amana      : ASX14[036]      -> "036" -> 3.0 tons  (identical to Goodman)
  Daikin     : DN14[036]       -> "036" -> 3.0 tons  (identical to Goodman)
  Rheem      : RA14AZ[036]JK   -> "036" -> 3.0 tons
  Ruud       : UA14[036]       -> "036" -> 3.0 tons  (identical to Rheem)
  York       : YCC[036]        -> "036" -> 3.0 tons
  Heil       : HCA[036]        -> "036" -> 3.0 tons  (identical to York/JCI)
  Coleman    : TCA[036]        -> "036" -> 3.0 tons  (identical to York/JCI)

Mitsubishi Electric ONLY (mini-splits use 2-digit kBTU codes):
  MSZ-GS[09]NA -> 9k BTU -> 0.75 tons
  MSZ-GS[12]NA -> 12k BTU -> 1.0 ton
  MSZ-GS[18]NA -> 18k BTU -> 1.5 tons
  MSZ-GS[24]NA -> 24k BTU -> 2.0 tons
  MXZ-3C[30]   -> 30k BTU -> 2.5 tons

FURNACE NOTE: Do NOT decode tonnage from furnace model numbers (Carrier 58xxx,
Goodman GMEC/GMVC, Rheem RPGE/RGPJ, Trane TUSx, Lennox SL2xx, York YHJF).
Furnace BTU codes are heat input capacity, not cooling tonnage.

RETURN THIS EXACT JSON STRUCTURE:
{
  "outdoor": {
    "model_number": "<exact string or null>",
    "serial_number": "<exact string or null>",
    "tonnage": <number in tons, e.g. 3.0, or null>,
    "tonnage_source": "<nameplate_btu | nameplate_label | model_decode | null>",
    "refrigerant": "<R-410A | R-22 | R-32 | R-454B | other or null>",
    "factory_charge_oz": <number in oz or null>,
    "rla": <number in amps or null>,
    "lra": <number in amps or null>,
    "capacitor_uf": "<e.g. '45/5' or '40 MFD' or null>",
    "mca": <number in amps or null>,
    "mocp": <number in amps or null>,
    "voltage": "<e.g. '208/230' or '240' or null>",
    "confidence": <0-100>,
    "notes": "<any relevant observations about nameplate condition, legibility, etc.>"
  },
  "indoor": {
    "model_number": "<exact string or null>",
    "serial_number": "<exact string or null>",
    "tonnage": <number or null>,
    "tonnage_source": "<nameplate_btu | nameplate_label | model_decode | null>",
    "voltage": "<or null>",
    "blower_motor_hp": <number or null>,
    "blower_motor_amps": <number or null>,
    "confidence": <0-100>,
    "notes": "<or null>"
  }
}

IMPORTANT:
- Return ONLY the JSON object. No other text.
- Use null (not "null") for missing fields.
- Numbers must be numeric, not strings (e.g. 3.0 not "3.0").
- outdoor.model_number is the most important field -- read it very carefully.
- Always set tonnage_source so downstream code knows how reliable the tonnage is.
"""
