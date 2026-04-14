"""
SnapAI — AI Cascade Service
Master router implementing the Dual-Track Cascade.

Track A (Sensor-First): When tech has field readings.
  A1 — XGBoost sensor model (< 1ms, 90.09% accuracy)
  A2 — YOLO cross-check if photo available
  A3a — Confirmed: confidence >= 85% AND YOLO agrees → return immediately (93-95% accuracy)
  A3b — Escalate: conflict or low confidence → Gemini tiebreaker (88-92% accuracy)

Track B (Visual-First): Photo only, no sensor readings.
  B1 — Corrosion v4 + Multi-class v1 YOLO in parallel
  B2a — Confirmed: any detection above threshold → return YOLO result (85% accuracy)
  B2b — Escalate: all below threshold → Gemini with YOLO context pre-loaded (75-82% accuracy)

Target: < 20% of inspections reach Gemini.
"""
import json
import logging
from dataclasses import dataclass, field
from typing import Optional, List

logger = logging.getLogger(__name__)


@dataclass
class CascadeResult:
    fault_label: str
    confidence: float
    track_used: str     # 'A' or 'B'
    method: str         # 'sensor_confirmed' | 'sensor_yolo_agreement' |
                        # 'gemini_tiebreak' | 'yolo_confirmed' | 'gemini_fallback'
    bounding_boxes: list = field(default_factory=list)
    gemini_report: Optional[dict] = None
    sensor_result: Optional[object] = None   # SensorResult
    yolo_result: Optional[object] = None     # YOLOResult
    gemini_called: bool = False


class AICascadeService:
    """
    Orchestrates the Dual-Track Cascade: XGBoost + YOLO + Gemini.
    Each service is a singleton loaded once at startup.
    """

    def __init__(self):
        from services.sensor_service import SensorService
        from services.yolo_service import YOLOService
        self._sensor_cls = SensorService
        self._yolo_cls = YOLOService
        self._sensor = None
        self._yolo = None

    @property
    def sensor(self):
        if self._sensor is None:
            self._sensor = self._sensor_cls()
        return self._sensor

    @property
    def yolo(self):
        if self._yolo is None:
            self._yolo = self._yolo_cls()
        return self._yolo

    async def analyze(
        self,
        photos: Optional[List[bytes]] = None,
        sensor_readings: Optional[object] = None,  # SensorReadings pydantic model
    ) -> CascadeResult:
        """
        Entry point. Routes to Track A or B based on available inputs.
        Both tracks can run simultaneously when both readings and a photo exist.
        """
        if sensor_readings and _has_required_readings(sensor_readings):
            return await self._track_a(photos, sensor_readings)
        elif photos:
            return await self._track_b(photos)
        else:
            raise ValueError("Must provide photos or sensor_readings to analyze.")

    # ── TRACK A: Sensor-First ───────────────────────────────────────────────
    async def _track_a(self, photos, readings) -> CascadeResult:
        logger.info("[Cascade] Track A — sensor-first")

        # A1: Run XGBoost sensor model
        try:
            sr = self.sensor.predict(
                outdoor_ambient_temp=readings.outdoor_ambient_temp or 0,
                supply_air_temp=readings.supply_air_temp or 0,
                return_air_temp=readings.return_air_temp or 0,
                suction_pressure=readings.suction_pressure or 0,
                discharge_pressure=readings.discharge_pressure or 0,
                unit_age_years=readings.unit_age_years or 0,
            )
        except Exception as e:
            logger.warning(f"[Cascade] Sensor model failed: {e}. Falling back to Track B.")
            if photos:
                return await self._track_b(photos)
            raise

        # A2: Cross-check with YOLO if photo available
        yr = None
        if photos and self.yolo.is_available():
            try:
                yr = self.yolo.detect(photos[0])
            except Exception as e:
                logger.warning(f"[Cascade] YOLO cross-check failed (non-fatal): {e}")

        # A3a: Sensor high-confidence AND YOLO agrees (or no photo) → done
        if sr.high_confidence:
            if yr is None or not yr.has_high_confidence:
                # No photo or YOLO found nothing — trust sensor at 90%
                logger.info(f"[Cascade] A3a: Sensor confirmed ({sr.fault_label} @ {sr.confidence:.0%})")
                return CascadeResult(
                    fault_label=sr.fault_label,
                    confidence=sr.confidence,
                    track_used="A",
                    method="sensor_confirmed",
                    sensor_result=sr,
                    yolo_result=yr,
                )

            if yr.has_high_confidence and _yolo_agrees_with_sensor(yr, sr.fault_label):
                # Sensor + YOLO agree → 93-95% accuracy
                logger.info(f"[Cascade] A3a: Sensor + YOLO agreement ({sr.fault_label})")
                return CascadeResult(
                    fault_label=sr.fault_label,
                    confidence=min(0.97, sr.confidence + 0.05),
                    track_used="A",
                    method="sensor_yolo_agreement",
                    bounding_boxes=_extract_bboxes(yr),
                    sensor_result=sr,
                    yolo_result=yr,
                )

        # A3b: Conflict or low confidence → Gemini tiebreaker
        logger.info(f"[Cascade] A3b: Escalating to Gemini (sensor={sr.fault_label} @ {sr.confidence:.0%})")
        gemini_result = await _call_gemini_track_a(photos, sr, yr, readings)

        return CascadeResult(
            fault_label=gemini_result.get("confirmed_fault", sr.fault_label),
            confidence=gemini_result.get("confidence", sr.confidence),
            track_used="A",
            method="gemini_tiebreak",
            bounding_boxes=gemini_result.get("bounding_boxes", []),
            gemini_report=gemini_result,
            sensor_result=sr,
            yolo_result=yr,
            gemini_called=True,
        )

    # ── TRACK B: Visual-First ───────────────────────────────────────────────
    async def _track_b(self, photos) -> CascadeResult:
        logger.info("[Cascade] Track B — visual-first")

        # B1: Run both YOLO models
        yr = None
        if self.yolo.is_available():
            try:
                yr = self.yolo.detect(photos[0])
            except Exception as e:
                logger.warning(f"[Cascade] YOLO failed: {e}. Going straight to Gemini.")

        # B2a: YOLO above threshold → return directly
        if yr and yr.has_high_confidence:
            best = yr.best_detection
            logger.info(f"[Cascade] B2a: YOLO confirmed ({best.label} @ {best.confidence:.0%})")
            return CascadeResult(
                fault_label=best.label,
                confidence=best.confidence,
                track_used="B",
                method="yolo_confirmed",
                bounding_boxes=_extract_bboxes(yr),
                yolo_result=yr,
            )

        # B2b: YOLO uncertain → Gemini with YOLO context
        logger.info("[Cascade] B2b: YOLO uncertain → Gemini fallback")
        gemini_result = await _call_gemini_track_b(photos, yr)

        return CascadeResult(
            fault_label=gemini_result.get("confirmed_fault", "unknown"),
            confidence=gemini_result.get("confidence", 0.7),
            track_used="B",
            method="gemini_fallback",
            bounding_boxes=gemini_result.get("bounding_boxes", []),
            gemini_report=gemini_result,
            yolo_result=yr,
            gemini_called=True,
        )


# ── Helpers ────────────────────────────────────────────────────────────────────

def _has_required_readings(readings) -> bool:
    """Check that at least 4 of 6 sensor readings are non-None."""
    fields = [
        "outdoor_ambient_temp", "supply_air_temp", "return_air_temp",
        "suction_pressure", "discharge_pressure", "unit_age_years",
    ]
    present = sum(1 for f in fields if getattr(readings, f, None) is not None)
    return present >= 4


def _yolo_agrees_with_sensor(yr, sensor_fault: str) -> bool:
    """
    Check if YOLO visual findings are consistent with the sensor diagnosis.
    Corrosion is always visual — sensor doesn't detect it, so any sensor fault
    label alongside corrosion YOLO is treated as 'not conflicting'.
    """
    if yr is None or not yr.has_high_confidence:
        return True  # no conflict if YOLO found nothing

    best = yr.best_detection
    if best is None:
        return True

    # Corrosion is purely visual — sensor models don't detect it
    if best.label == "corrosion":
        return True  # not a conflict, different fault dimension

    # Normalize label names for comparison
    sensor_norm = sensor_fault.lower().replace(" ", "_").replace("-", "_")
    yolo_norm = best.label.lower().replace(" ", "_").replace("-", "_")

    return sensor_norm == yolo_norm or yolo_norm in sensor_norm or sensor_norm in yolo_norm


def _extract_bboxes(yr) -> list:
    if yr is None:
        return []
    bboxes = []
    for d in (yr.corrosion or []) + (yr.multiclass or []):
        bboxes.append({
            "label": d.label,
            "confidence": d.confidence,
            "x1": d.bbox[0], "y1": d.bbox[1],
            "x2": d.bbox[2], "y2": d.bbox[3],
        })
    return bboxes


async def _call_gemini_track_a(photos, sr, yr, readings) -> dict:
    """Call Gemini for Track A conflict resolution."""
    from prompts.cascade_prompts import TRACK_A_CONFLICT_PROMPT, format_yolo_findings
    from services.vision import get_vision_service

    yolo_text = format_yolo_findings(yr)
    prompt = TRACK_A_CONFLICT_PROMPT.format(
        sensor_fault=sr.fault_label,
        sensor_confidence=sr.confidence,
        outdoor_ambient_temp=getattr(readings, "outdoor_ambient_temp", "N/A"),
        supply_air_temp=getattr(readings, "supply_air_temp", "N/A"),
        return_air_temp=getattr(readings, "return_air_temp", "N/A"),
        suction_pressure=getattr(readings, "suction_pressure", "N/A"),
        discharge_pressure=getattr(readings, "discharge_pressure", "N/A"),
        unit_age_years=getattr(readings, "unit_age_years", "N/A"),
        yolo_findings=yolo_text,
    )
    return await _call_gemini(photos, prompt)


async def _call_gemini_track_b(photos, yr) -> dict:
    """Call Gemini for Track B uncertain fallback."""
    from prompts.cascade_prompts import TRACK_B_UNCERTAIN_PROMPT, format_yolo_findings

    yolo_text = format_yolo_findings(yr)
    prompt = TRACK_B_UNCERTAIN_PROMPT.format(yolo_findings=yolo_text)
    return await _call_gemini(photos, prompt)


async def _call_gemini(photos, prompt: str) -> dict:
    """
    Reuses the existing GeminiVisionService and parses JSON from the response.
    """
    from services.vision import get_vision_service
    import json

    vision = get_vision_service()
    try:
        raw = await vision.analyze_equipment_photos(
            image_bytes_list=photos or [],
            prompt=prompt,
            image_content_types=["image/jpeg"] * len(photos or []),
        )
        if isinstance(raw, dict):
            return raw
        # Try to extract JSON from string response
        if isinstance(raw, str):
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start >= 0:
                return json.loads(raw[start:end])
    except Exception as e:
        logger.error(f"[Cascade] Gemini call failed: {e}")

    return {
        "confirmed_fault": "unknown",
        "confidence": 0.6,
        "explanation": "AI analysis unavailable. Please assess manually.",
        "recommendation": "Perform a manual inspection.",
        "bounding_boxes": [],
    }
