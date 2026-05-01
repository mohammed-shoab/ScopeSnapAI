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
3. For tonnage: look for BTU/h first (12000 BTU = 1 ton), then "tons" label,
   then decode from model number (common pattern: digit 7-8 in model = tons x 12).
4. For refrigerant: look for "R-410A", "R-22", "R-32", "R-454B" labels.
5. For electrical specs: MCA = "Minimum Circuit Ampacity", MOCP = "Max Overcurrent".
6. For RLA/LRA: these are on the compressor section. RLA = "Rated Load Amps",
   LRA = "Locked Rotor Amps".
7. For factory charge: look for "Factory Charge", "Refrigerant Charge", or oz/lbs weight.
8. If a field is not visible or not readable, set it to null.
9. Confidence: your 0-100 confidence that each field is correctly read.

RETURN THIS EXACT JSON STRUCTURE:
{
  "outdoor": {
    "model_number": "<exact string or null>",
    "serial_number": "<exact string or null>",
    "tonnage": <number in tons, e.g. 3.0, or null>,
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
- outdoor.model_number is the most important field — read it very carefully.
"""
