"""
WS-E — Thermal Camera Analysis Prompt
Sent to Gemini 2.5 Flash with a FLIR One thermal image.

Detects hotspots on electrical terminals for Card #16 (Loose Terminal / Wiring).
A hotspot >20°F above ambient = wiring fault confirmed.

When YOLO thermal model is available it will be swapped in.
Until then, Gemini handles this as Path B fallback.
"""

THERMAL_ANALYSIS_PROMPT = """
You are an expert HVAC electrical diagnostics system analyzing a thermal infrared image.
The image may be from a FLIR One camera, a thermal screenshot, or a regular photo with visible burn marks.

TASK: Detect electrical hotspots that indicate loose terminals or wiring faults.

ANALYSIS RULES:
1. A hotspot is ANY component visibly hotter than surrounding components:
   - In thermal images: bright white/yellow/red areas vs cooler blue/green areas
   - In regular photos: burn marks, discoloration, melted insulation, carbon deposits
2. Temperature threshold: >20°F (>11°C) above ambient = CONFIRMED fault
3. Focus on: terminal blocks, wire connections, contactors, capacitor terminals, fuse holders
4. Note the LOCATION precisely (e.g., "top-left terminal on contactor", "L1 wire at breaker")
5. If no hotspot is detectable, say so clearly — do not invent findings

RETURN THIS EXACT JSON STRUCTURE (no markdown, no explanation):
{
  "hotspots_detected": true | false,
  "hotspot_count": <integer 0-10>,
  "hotspots": [
    {
      "location": "<precise description of where the hotspot is>",
      "severity": "mild | moderate | severe",
      "temp_delta_estimate": "<e.g. '25-35°F above ambient' or 'burn mark visible'>",
      "likely_cause": "<loose terminal | failed wire | corroded connection | overloaded circuit>",
      "confidence": <0-100>
    }
  ],
  "overall_assessment": "normal | suspect | fault_confirmed",
  "recommended_action": "<specific action to take>",
  "card_16_confirmed": true | false,
  "notes": "<any relevant observations about image quality, camera type, etc.>"
}

IMPORTANT:
- Return ONLY the JSON object. No other text.
- If image quality is too poor to analyze, set hotspots_detected to false and note in notes field.
- card_16_confirmed = true only if you have HIGH confidence of a genuine wiring fault.
"""
