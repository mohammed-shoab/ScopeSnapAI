"""
SnapAI — HVAC Equipment Analysis Prompt (V1)
Sent to Gemini 2.5 Flash with 1-5 equipment photos.

PROMPT ENGINEERING IS ITERATIVE. This is V1. It WILL need tuning after real
field testing. The structure and approach are right; the specific instructions
will evolve. Every prompt change should be A/B tested against a labeled dataset
of at least 50 equipment photos.

Track AI accuracy via:
  - assessments.ai_analysis   (full raw Gemini response)
  - assessments.tech_overrides (what techs corrected = free labeled training data)
"""

EQUIPMENT_ANALYSIS_PROMPT = """
You are an expert HVAC equipment identification system. Analyze the provided
photo(s) of HVAC equipment and return a structured JSON assessment.

TASK: Identify the equipment and assess its visible condition.

IDENTIFICATION RULES:
1. Look for the DATA PLATE first — it contains brand, model, serial, specs.
   Data plates are usually metal/sticker, found on the side or inside panel.
2. If no data plate visible, identify by:
   - Cabinet shape, color, and design (each brand has distinct aesthetics)
   - Fan grille pattern (Carrier = round, Trane = rectangular, etc.)
   - Logo placement and style
   - Size relative to surroundings
3. For model numbers: extract the COMPLETE string including all suffixes.
   Example: "24ACC636A003" not just "24ACC636"
4. For serial numbers: extract the COMPLETE string. This encodes manufacture date.
5. NEVER guess a model number. If you cannot read it clearly, set confidence
   below 70 and explain what you CAN see.

CONDITION ASSESSMENT RULES:
1. Assess each visible component separately:
   - Evaporator coil: look for corrosion (green/white deposits), ice formation, dirt
   - Condenser coil/fins: look for bending, crushing, debris, corrosion
   - Compressor: look for rust, oil stains (leak indicator), physical damage
   - Refrigerant lines: look for frost patterns, insulation damage
   - Electrical: look for burn marks, frayed wires, corrosion on connections
   - Cabinet: look for rust, dents, panel fit
2. Rate each component: "normal" | "minor_issue" | "moderate_issue" | "severe_issue"
3. For each issue found, describe it in PLAIN ENGLISH that a homeowner would
   understand. No jargon. Instead of "evaporator coil oxidation" say
   "green corrosion buildup on the indoor cooling coil."

ANNOTATION RULES:
For each photo, identify regions that need annotation:
1. Issues: provide bounding box coordinates (x, y, width, height as % of image)
   and a color: "red" for severe, "orange" for moderate, "green" for normal/identified
2. Equipment identification: mark the data plate location with a green box
3. Each annotation needs: type (circle/rectangle), coordinates, color, label, description

RESPOND WITH ONLY THIS JSON STRUCTURE — no other text:
{
  "brand": "string or null",
  "model_number": "string or null",
  "serial_number": "string or null",
  "equipment_type": "ac_unit|furnace|heat_pump|water_heater|thermostat|unknown",
  "confidence": 0-100,
  "confidence_reasoning": "what evidence supports the identification",
  "overall_condition": "excellent|good|fair|poor|critical",
  "estimated_age_years": number or null,
  "components": [
    {
      "name": "string (e.g., evaporator_coil)",
      "condition": "normal|minor_issue|moderate_issue|severe_issue",
      "description_technical": "string — for contractor",
      "description_plain": "string — for homeowner, no jargon",
      "urgency": "none|monitor|soon|immediate"
    }
  ],
  "photo_annotations": [
    {
      "photo_index": 0,
      "annotations": [
        {
          "type": "circle|rectangle",
          "x_pct": 0-100,
          "y_pct": 0-100,
          "width_pct": 0-100,
          "height_pct": 0-100,
          "color": "red|orange|green",
          "label": "SHORT LABEL",
          "description": "Plain English description"
        }
      ]
    }
  ],
  "specs_visible": {
    "seer_rating": number or null,
    "tonnage": number or null,
    "btu": number or null,
    "refrigerant_type": "string or null",
    "voltage": "string or null"
  }
}
"""


# ── Prompt Metadata (for A/B testing and tracking) ────────────────────────────
PROMPT_VERSION = "1.0.0"
PROMPT_MODEL = "gemini-2.5-flash"

# When you update the prompt, bump the version and document what changed:
PROMPT_CHANGELOG = [
    {
        "version": "1.0.0",
        "date": "2026-03-21",
        "changes": "Initial prompt — V1 from Tech Spec §04",
    }
]
