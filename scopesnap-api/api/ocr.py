"""
WS-B — Step Zero OCR API
POST /api/ocr/nameplate  — extract 10 fields from nameplate photo(s)
PATCH /api/assessments/{id}/nameplate — persist OCR result on assessment

Flow:
  1. Tech takes photo(s) of outdoor (+ optional indoor) unit nameplate
  2. Frontend sends image bytes to POST /api/ocr/nameplate
  3. Gemini 2.5 Flash extracts 10 fields (model, serial, tonnage, refrigerant, etc.)
  4. Backend cross-references:
       - Model # prefix against brands.series.model_prefixes → refrigerant/metering_device
       - Model # prefix against legacy_model_prefixes → is_legacy / R-22 alert
       - Serial # against SerialDecoder → year_of_manufacture
  5. Returns enriched result; frontend shows with edit-in-place
  6. On confirm, frontend calls PATCH /api/assessments/{id}/nameplate to persist
"""

import base64
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from db.database import get_db
from db.models import Assessment, EquipmentModel
from api.auth import get_current_user, AuthContext
from services.vision import get_vision_service, VisionAnalysisError
from services.serial_decoder import decode_serial
from prompts.nameplate_ocr import NAMEPLATE_OCR_PROMPT
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/ocr", tags=["ocr"])

# D-7 brands deferred for manual entry (no nameplate decoder yet)
D7_BRANDS = {"lg", "samsung", "gree", "pioneer", "mrcool", "bosch"}


# ── Response schemas ───────────────────────────────────────────────────────────

class NameplateUnitResult(BaseModel):
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    tonnage: Optional[float] = None
    refrigerant: Optional[str] = None
    factory_charge_oz: Optional[float] = None
    rla: Optional[float] = None
    lra: Optional[float] = None
    capacitor_uf: Optional[str] = None
    mca: Optional[float] = None
    mocp: Optional[float] = None
    voltage: Optional[str] = None
    # Enriched fields (from brand cross-reference)
    brand_id: Optional[str] = None
    series_id: Optional[str] = None
    charging_method: Optional[str] = None
    metering_device: Optional[str] = None
    is_legacy: bool = False
    year_of_manufacture: Optional[int] = None
    r22_alert: bool = False
    confidence: int = 0
    notes: Optional[str] = None


class NameplateOCRResponse(BaseModel):
    outdoor: NameplateUnitResult
    indoor: Optional[NameplateUnitResult] = None
    captured_at: str
    capture_method: str = "photo"
    d7_brand_detected: bool = False
    d7_brand_name: Optional[str] = None


class NameplateSaveRequest(BaseModel):
    """Request body for PATCH /api/assessments/{id}/nameplate"""
    ocr_result: dict  # The full NameplateOCRResponse as dict


# ── Helpers ────────────────────────────────────────────────────────────────────

async def _lookup_brand_series(
    model_prefix: str,
    db: AsyncSession,
) -> dict:
    """
    Cross-reference a model number prefix against brands.series.model_prefixes
    to detect refrigerant type, metering device, and charging method.

    Returns dict with: brand_id, series_id, refrigerant, metering_device,
                       charging_method, is_legacy, r22_alert
    """
    if not model_prefix:
        return {}

    prefix_upper = model_prefix.strip().upper()
    result = {}

    # 1. Check legacy_model_prefixes first (pre-2010 / R-22 units)
    from sqlalchemy import text as sql_text
    legacy_row = await db.execute(
        sql_text("""
            SELECT prefix, brand_id, brand_name, years, refrigerant
            FROM legacy_model_prefixes
            WHERE :prefix LIKE (prefix || '%')
            ORDER BY length(prefix) DESC
            LIMIT 1
        """),
        {"prefix": prefix_upper},
    )
    legacy = legacy_row.fetchone()
    if legacy:
        result["brand_id"] = legacy.brand_id
        result["is_legacy"] = True
        result["r22_alert"] = (legacy.refrigerant or "").upper().find("R-22") != -1
        result["refrigerant"] = legacy.refrigerant

    # 2. Check brands.series model_prefixes for current units
    brands_row = await db.execute(
        sql_text("""
            SELECT
                b.id as brand_id,
                s->>'id' as series_id,
                s->>'refrigerant' as refrigerant,
                s->>'metering_device' as metering_device,
                s->>'charging_method' as charging_method
            FROM brands b,
                 jsonb_array_elements(b.series) s
            WHERE b.series != '[]'::jsonb
              AND EXISTS (
                SELECT 1 FROM jsonb_array_elements_text(s->'model_prefixes') pfx
                WHERE :prefix LIKE (pfx || '%')
              )
            ORDER BY length(s->>'id') DESC
            LIMIT 1
        """),
        {"prefix": prefix_upper},
    )
    brand_match = brands_row.fetchone()
    if brand_match:
        result["brand_id"] = brand_match.brand_id
        result["series_id"] = brand_match.series_id
        result["refrigerant"] = result.get("refrigerant") or brand_match.refrigerant
        result["metering_device"] = brand_match.metering_device
        result["charging_method"] = brand_match.charging_method
        result["is_legacy"] = result.get("is_legacy", False)

    return result


def _detect_d7_brand(model_number: Optional[str]) -> Optional[str]:
    """Check if model number matches a D-7 brand that needs manual entry."""
    if not model_number:
        return None
    model_upper = model_number.upper()
    d7_prefixes = {
        "MSZ": "mitsubishi", "MUZ": "mitsubishi", "MXZ": "mitsubishi",
        "CH": "lg", "LG": "lg",
        "AR": "samsung", "MH": "samsung",
        "GWH": "gree", "GIC": "gree",
        "WYS": "pioneer",
        "DIY": "mrcool", "MRCOOL": "mrcool",
        "CLIMATE": "bosch", "IDS": "bosch",
    }
    for prefix, brand in d7_prefixes.items():
        if model_upper.startswith(prefix):
            return brand
    return None


def _enrich_unit(raw: dict, brand_data: dict) -> dict:
    """Merge Gemini OCR output with brand cross-reference data."""
    unit = {**raw}
    unit["brand_id"] = brand_data.get("brand_id")
    unit["series_id"] = brand_data.get("series_id")
    unit["is_legacy"] = brand_data.get("is_legacy", False)
    unit["r22_alert"] = brand_data.get("r22_alert", False)
    unit["charging_method"] = brand_data.get("charging_method")
    unit["metering_device"] = brand_data.get("metering_device")
    # Prefer Gemini-extracted refrigerant if present; else use brand lookup
    if not unit.get("refrigerant"):
        unit["refrigerant"] = brand_data.get("refrigerant")
    # Force R-22 if legacy prefix matched
    if unit["r22_alert"]:
        unit["refrigerant"] = "R-22"
    return unit


# ── POST /api/ocr/nameplate ────────────────────────────────────────────────────

@router.post("/nameplate", status_code=200)
async def ocr_nameplate(
    outdoor_photo: UploadFile = File(..., description="Outdoor unit nameplate photo"),
    indoor_photo: Optional[UploadFile] = File(None, description="Indoor unit nameplate photo (optional)"),
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Step Zero OCR: extract specs from nameplate photo(s).

    Sends photo(s) to Gemini 2.5 Flash, extracts 10 fields, then:
    - Cross-references Model# against brands.series for refrigerant/metering_device
    - Checks legacy_model_prefixes for R-22 alert
    - Decodes Serial# for year-of-manufacture

    Returns NameplateOCRResponse ready for edit-in-place display.
    """
    # -- Read image bytes --
    outdoor_bytes = await outdoor_photo.read()
    if not outdoor_bytes:
        raise HTTPException(status_code=400, detail="Outdoor photo is empty.")

    indoor_bytes = None
    if indoor_photo:
        indoor_bytes = await indoor_photo.read()
        if not indoor_bytes:
            indoor_bytes = None

    vision = get_vision_service()

    # -- Call Gemini --
    image_list = [outdoor_bytes]
    content_types = [outdoor_photo.content_type or "image/jpeg"]
    if indoor_bytes:
        image_list.append(indoor_bytes)
        content_types.append(indoor_photo.content_type or "image/jpeg")

    try:
        raw_result = await vision.analyze_equipment_photos(
            image_bytes_list=image_list,
            prompt=NAMEPLATE_OCR_PROMPT,
            image_content_types=content_types,
        )
    except VisionAnalysisError as e:
        logger.error(f"[OCR] Gemini failed: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"OCR analysis failed: {e}. Check GEMINI_API_KEY and retry."
        )

    # -- Extract outdoor/indoor from result --
    outdoor_raw = raw_result.get("outdoor", {}) if isinstance(raw_result, dict) else {}
    indoor_raw = raw_result.get("indoor") if isinstance(raw_result, dict) else None

    # -- Cross-reference outdoor model number --
    outdoor_model = outdoor_raw.get("model_number") or ""
    brand_data = {}
    d7_brand = None

    if outdoor_model:
        # Check D-7 brands first
        d7_brand = _detect_d7_brand(outdoor_model)

        if not d7_brand:
            # Look up in brands.series and legacy_model_prefixes
            try:
                brand_data = await _lookup_brand_series(outdoor_model, db)
            except Exception as e:
                logger.warning(f"[OCR] Brand lookup failed: {e}")

    # -- Decode serial numbers for year of manufacture --
    outdoor_serial = outdoor_raw.get("serial_number")
    if outdoor_serial:
        try:
            decode_result = decode_serial(
                brand=brand_data.get("brand_id") or "",
                serial=outdoor_serial,
            )
            if decode_result:
                outdoor_raw["year_of_manufacture"] = decode_result.get("year")
        except Exception:
            pass

    if indoor_raw:
        indoor_serial = indoor_raw.get("serial_number")
        if indoor_serial:
            try:
                indoor_brand = brand_data.get("brand_id")
                decode_result = decode_serial(
                    brand=indoor_brand or "",
                    serial=indoor_serial,
                )
                if decode_result:
                    indoor_raw["year_of_manufacture"] = decode_result.get("year")
            except Exception:
                pass

    # -- Enrich outdoor result with brand data --
    outdoor_enriched = _enrich_unit(outdoor_raw, brand_data)
    indoor_enriched = _enrich_unit(indoor_raw, {}) if indoor_raw else None

    response = {
        "outdoor": outdoor_enriched,
        "indoor": indoor_enriched,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "capture_method": "photo",
        "d7_brand_detected": d7_brand is not None,
        "d7_brand_name": d7_brand,
    }

    return response


# ── PATCH /api/assessments/{id}/nameplate ─────────────────────────────────────

@router.patch("/assessments/{assessment_id}/nameplate", status_code=200)
async def save_nameplate(
    assessment_id: str,
    body: NameplateSaveRequest,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Persist the OCR result (after tech edits) on the assessment record.
    Also updates equipment_instance with detected brand/tonnage/year if found.
    """
    # Verify assessment belongs to this company
    result = await db.execute(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.company_id == auth.company_id,
        )
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found.")

    ocr_data = body.ocr_result
    ocr_data["saved_at"] = datetime.now(timezone.utc).isoformat()

    # Persist on assessment
    await db.execute(
        update(Assessment)
        .where(Assessment.id == assessment_id)
        .values(ocr_nameplate=ocr_data)
    )

    # Update equipment_instance if we detected brand/tonnage/year
    outdoor = ocr_data.get("outdoor", {})
    if assessment.equipment_instance_id and outdoor:
        updates = {}
        if outdoor.get("brand_id"):
            updates["brand"] = outdoor["brand_id"].capitalize()
        if outdoor.get("model_number"):
            updates["model_number"] = outdoor["model_number"]
        if outdoor.get("serial_number"):
            updates["serial_number"] = outdoor["serial_number"]
        if outdoor.get("year_of_manufacture"):
            updates["install_year"] = outdoor["year_of_manufacture"]

        if updates:
            from db.models import EquipmentInstance
            await db.execute(
                update(EquipmentInstance)
                .where(EquipmentInstance.id == assessment.equipment_instance_id)
                .values(**updates)
            )

    await db.commit()

    return {"ok": True, "assessment_id": assessment_id, "ocr_saved": True}
