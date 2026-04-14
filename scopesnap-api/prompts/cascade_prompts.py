"""
SnapAI — Guided Gemini Prompt Templates for the AI Cascade.

Gemini is NEVER called blindly — it always receives structured context
from the YOLO and/or sensor models before being asked to analyze.

Track A Conflict: sensor and YOLO disagree → Gemini resolves
Track B Uncertain: YOLO confidence too low → Gemini with YOLO context pre-loaded
"""


def format_yolo_findings(yolo_result) -> str:
    """
    Convert a YOLOResult into a human-readable string for Gemini prompts.
    """
    if yolo_result is None:
        return "  No visual pre-scan available."

    lines = []

    if yolo_result.corrosion:
        for d in yolo_result.corrosion:
            bbox = d.bbox
            lines.append(
                f"  - CORROSION detected: '{d.label}' "
                f"confidence={d.confidence:.0%} "
                f"bbox=[x1={bbox[0]:.0f}, y1={bbox[1]:.0f}, x2={bbox[2]:.0f}, y2={bbox[3]:.0f}]"
            )
    else:
        lines.append("  - Corrosion model: no detection above 75% threshold")

    if yolo_result.multiclass:
        for d in yolo_result.multiclass:
            bbox = d.bbox
            lines.append(
                f"  - FAULT detected: '{d.label}' "
                f"confidence={d.confidence:.0%} "
                f"bbox=[x1={bbox[0]:.0f}, y1={bbox[1]:.0f}, x2={bbox[2]:.0f}, y2={bbox[3]:.0f}]"
            )
    else:
        lines.append("  - Multi-class model: no detection above 80% threshold")

    return "\n".join(lines) if lines else "  No detections above threshold."


TRACK_A_CONFLICT_PROMPT = """\
You are an expert HVAC fault diagnosis system acting as a senior reviewer.

SENSOR MODEL DIAGNOSIS:
  Fault detected: {sensor_fault}
  Confidence: {sensor_confidence:.0%}
  Sensor readings:
    Outdoor ambient temp: {outdoor_ambient_temp}°F
    Supply air temp:      {supply_air_temp}°F
    Return air temp:      {return_air_temp}°F
    Suction pressure:     {suction_pressure} PSI
    Discharge pressure:   {discharge_pressure} PSI
    Unit age:             {unit_age_years} years

VISUAL MODEL FINDINGS (YOLO):
{yolo_findings}

These findings conflict or the sensor confidence is below 85%.
Analyze the attached HVAC inspection photo and the sensor data above.

Return ONLY this JSON structure — no other text:
{{
  "confirmed_fault": "fault_name_or_normal",
  "confidence": 0.0,
  "sensor_diagnosis_correct": true,
  "visual_findings_correct": true,
  "explanation": "plain English explanation for the technician",
  "recommendation": "specific next steps for the technician",
  "bounding_boxes": [{{"label": "...", "x1": 0, "y1": 0, "x2": 100, "y2": 100, "confidence": 0.0}}]
}}
"""

TRACK_B_UNCERTAIN_PROMPT = """\
You are an expert HVAC fault diagnosis system acting as a senior reviewer.

VISUAL MODEL PRE-SCAN (YOLO — below confidence threshold, needs verification):
{yolo_findings}

The visual models could not make a high-confidence determination.
Analyze the attached HVAC inspection photo.
Pay special attention to the regions flagged by the YOLO models above, even if confidence was low.

Return ONLY this JSON structure — no other text:
{{
  "confirmed_fault": "fault_name_or_normal",
  "confidence": 0.0,
  "explanation": "plain English explanation for the technician",
  "recommendation": "specific next steps for the technician",
  "bounding_boxes": [{{"label": "...", "x1": 0, "y1": 0, "x2": 100, "y2": 100, "confidence": 0.0}}]
}}
"""
