"""
WS-E — Thermal Camera Analysis (Card #16 Path A)
POST /api/thermal/analyze  — detect hotspots from thermal/regular photo

Card #16: Loose Terminal / Wiring Fault
  - Path A (thermal camera): FLIR One image → hotspot detection
  - Path B (no camera): Gemini multi-input fallback (existing flow)

Current implementation: Gemini 2.5 Flash for analysis.
When YOLO thermal model is trained, it will be added as the primary detector
and Gemini becomes the fallback (as documented in AI Model Map tab).

Web Bluetooth (FLIR One BLE pairing) is handled entirely in the browser.
This endpoint only receives the resulting image bytes.

Acceptance criteria (WS-E M9):
  - thermal .jpg upload returns hot_spots_detected + hotspot details
  - falls back gracefully when no hotspot is detectable
  - card_16_confirmed = true for known terminal-block hot-spot photos
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from db.database import get_db
from api.auth import get_current_user, AuthContext
from services.vision import get_vision_service, VisionAnalysisError
from prompts.thermal_analysis import THERMAL_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/thermal", tags=["thermal"])


# ── Schemas ────────────────────────────────────────────────────────────────────

class ThermalHotspot(BaseModel):
    location: str
    severity: str                       # "mild" | "moderate" | "severe"
    temp_delta_estimate: Optional[str]
    likely_cause: Optional[str]
    confidence: int


class ThermalAnalysisResponse(BaseModel):
    hotspots_detected: bool
    hotspot_count: int
    hotspots: list[ThermalHotspot]
    overall_assessment: str             # "normal" | "suspect" | "fault_confirmed"
    recommended_action: Optional[str]
    card_16_confirmed: bool             # True → route to Card #16 estimate
    notes: Optional[str]
    capture_method: str                 # "flir_ble" | "manual_upload" | "regular_photo"
    analyzed_at: str


# ── POST /api/thermal/analyze ──────────────────────────────────────────────────

@router.post("/analyze", response_model=ThermalAnalysisResponse)
async def analyze_thermal_image(
    photo: UploadFile = File(..., description="Thermal or regular photo to analyze for hotspots"),
    capture_method: str = Form("manual_upload", description="flir_ble | manual_upload | regular_photo"),
    assessment_id: Optional[str] = Form(None, description="Assessment to associate with this analysis"),
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    WS-E Card #16 Path A — Analyze thermal or regular photo for electrical hotspots.

    Accepts:
      - FLIR One thermal .jpg (from BLE capture — Path A1)
      - Manual upload of thermal screenshot/export (Path A2)
      - Regular photo with visible burn marks (Path B fallback)

    Returns hotspot analysis with confidence scores.
    card_16_confirmed=true means route tech directly to Card #16 estimate.

    Note on YOLO thermal model: Not yet trained. When available, it will run first
    and Gemini will be used only if YOLO confidence < 70%.
    See AI Model Map tab ("M") in SnapAI_Decision_Tree.html for architecture.
    """
    image_bytes = await photo.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Photo is empty.")

    content_type = photo.content_type or "image/jpeg"
    vision = get_vision_service()

    # ── TODO: Insert YOLO thermal model here when trained ─────────────────────
    # yolo_result = await yolo_thermal_service.detect_hotspots(image_bytes)
    # if yolo_result.confidence >= 70:
    #     return _build_response_from_yolo(yolo_result, capture_method)
    # ─────────────────────────────────────────────────────────────────────────

    # Current: Gemini handles all thermal analysis
    try:
        raw = await vision.analyze_equipment_photos(
            image_bytes_list=[image_bytes],
            prompt=THERMAL_ANALYSIS_PROMPT,
            image_content_types=[content_type],
        )
    except VisionAnalysisError as e:
        logger.error(f"[Thermal] Gemini failed: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Thermal analysis failed: {e}"
        )

    # ── Parse Gemini response ─────────────────────────────────────────────────
    hotspots_raw = raw.get("hotspots", []) if isinstance(raw, dict) else []
    hotspots = [
        ThermalHotspot(
            location=h.get("location", "unknown"),
            severity=h.get("severity", "mild"),
            temp_delta_estimate=h.get("temp_delta_estimate"),
            likely_cause=h.get("likely_cause"),
            confidence=int(h.get("confidence", 50)),
        )
        for h in hotspots_raw
        if isinstance(h, dict)
    ]

    result = ThermalAnalysisResponse(
        hotspots_detected=bool(raw.get("hotspots_detected", False)) if isinstance(raw, dict) else False,
        hotspot_count=int(raw.get("hotspot_count", len(hotspots))) if isinstance(raw, dict) else 0,
        hotspots=hotspots,
        overall_assessment=str(raw.get("overall_assessment", "normal")) if isinstance(raw, dict) else "normal",
        recommended_action=str(raw.get("recommended_action", "")) if isinstance(raw, dict) else None,
        card_16_confirmed=bool(raw.get("card_16_confirmed", False)) if isinstance(raw, dict) else False,
        notes=str(raw.get("notes", "")) if isinstance(raw, dict) else None,
        capture_method=capture_method,
        analyzed_at=datetime.now(timezone.utc).isoformat(),
    )

    # ── Optionally persist to assessment ─────────────────────────────────────
    if assessment_id and result.hotspots_detected:
        try:
            await db.execute(
                text("""
                    UPDATE assessments
                    SET tech_overrides = COALESCE(tech_overrides, '{}')::jsonb ||
                        jsonb_build_object(
                            'thermal_analysis', :analysis::jsonb,
                            'thermal_analyzed_at', :analyzed_at
                        )
                    WHERE id = :assessment_id
                      AND company_id = :company_id
                """),
                {
                    "analysis": str(result.model_dump()),
                    "analyzed_at": result.analyzed_at,
                    "assessment_id": assessment_id,
                    "company_id": auth.company_id,
                },
            )
            await db.commit()
        except Exception as e:
            logger.warning(f"[Thermal] Failed to persist analysis: {e}")
            # Non-fatal

    return result
