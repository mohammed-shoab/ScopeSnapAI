"""
ScopeSnap — Assessment API Endpoints
WP-02: Photo Upload + Vision AI Analysis
"""

import uuid
import json
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Form, Body
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel

from db.database import get_db
from db.models import Assessment, AssessmentPhoto, Property, EquipmentInstance
from api.auth import get_current_user, AuthContext
from services.storage import get_storage
from services.vision import get_vision_service, VisionAnalysisError
from prompts.equipment_analysis import EQUIPMENT_ANALYSIS_PROMPT
from config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/assessments", tags=["assessments"])


# ── Pydantic Schemas ───────────────────────────────────────────────────────────

class AssessmentOverride(BaseModel):
    """Fields a tech can override after AI analysis."""
    brand: Optional[str] = None
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    install_year: Optional[int] = None
    overall_condition: Optional[str] = None
    equipment_type: Optional[str] = None
    notes: Optional[str] = None


class AssessmentResponse(BaseModel):
    id: str
    status: str
    photo_urls: list
    ai_equipment_id: Optional[dict] = None
    ai_condition: Optional[dict] = None
    ai_issues: Optional[dict] = None
    ai_analysis: Optional[dict] = None
    tech_overrides: dict = {}
    property_id: Optional[str] = None
    equipment_instance_id: Optional[str] = None
    message: Optional[str] = None

    class Config:
        from_attributes = True


# ── Helper: compress image ─────────────────────────────────────────────────────

def compress_image(image_bytes: bytes, max_width: int = 1200) -> tuple[bytes, str]:
    """
    Compress image to max_width px using Pillow. Returns (bytes, mime_type).
    Preserves aspect ratio. Always outputs JPEG for consistency + smaller size.
    """
    try:
        from PIL import Image
        img = Image.open(BytesIO(image_bytes))

        # Convert RGBA / P modes to RGB for JPEG
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")

        # Resize if wider than max_width
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.LANCZOS)

        # Save to bytes
        out = BytesIO()
        img.save(out, format="JPEG", quality=85, optimize=True)
        return out.getvalue(), "image/jpeg"

    except Exception as e:
        print(f"[Compress] Warning: could not compress image: {e}. Using original.")
        return image_bytes, "image/jpeg"


# ── POST /api/assessments ──────────────────────────────────────────────────────

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_assessment(
    photos: List[UploadFile] = File(..., description="1-5 HVAC equipment photos"),
    property_id: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    property_address: Optional[str] = Form(None),  # Alias used by mobile app
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    zip_code: Optional[str] = Form(None, alias="zip"),
    customer_name: Optional[str] = Form(None),
    homeowner_name: Optional[str] = Form(None),    # Alias used by mobile app
    homeowner_email: Optional[str] = Form(None),   # Alias used by mobile app
    homeowner_phone: Optional[str] = Form(None),   # Alias used by mobile app
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload 1-5 equipment photos → create assessment record → return assessment_id.

    - Accepts 1-5 images (JPEG, PNG, HEIC, WEBP)
    - Compresses to 1200px wide server-side (Pillow)
    - Saves to LocalStorage (dev) or R2 (prod)
    - Creates assessment record in DB with status='pending'
    - Returns assessment_id for subsequent /analyze call
    """
    # Validate photo count
    if not photos:
        raise HTTPException(status_code=400, detail="At least 1 photo required.")
    if len(photos) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 photos per assessment.")

    # Validate file types
    allowed_types = {"image/jpeg", "image/png", "image/heic", "image/heif", "image/webp"}
    for photo in photos:
        ct = photo.content_type or ""
        if ct and ct.lower() not in allowed_types:
            # Accept anyway — don't block on content type alone
            pass

    # Normalize aliases
    address = address or property_address
    customer_name = customer_name or homeowner_name
    customer_email = homeowner_email
    customer_phone = homeowner_phone

    # Parse city/state/zip from address string if not provided separately
    if address and not city and not state and not zip_code:
        parts = address.split(",")
        if len(parts) >= 2:
            address = parts[0].strip()
            # Try to parse "Dallas, TX 75201" format
            rest = ",".join(parts[1:]).strip()
            rest_parts = rest.split()
            # Look for 2-letter state and 5-digit zip
            for i, part in enumerate(rest_parts):
                if len(part) == 2 and part.isalpha():
                    state = part.upper()
                elif len(part) == 5 and part.isdigit():
                    zip_code = part
                elif len(part) > 2:
                    city = (city or "") + part + " "
            city = city.strip() if city else None

    # ── Find or create property ──────────────────────────────────────────────
    prop = None
    if property_id:
        result = await db.execute(
            select(Property).where(
                Property.id == property_id,
                Property.company_id == auth.company_id
            )
        )
        prop = result.scalar_one_or_none()
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found.")
    elif address:
        # Try to find existing property by address (+ ZIP if available)
        query = select(Property).where(
            Property.company_id == auth.company_id,
            Property.address_line1 == address,
        )
        if zip_code:
            query = query.where(Property.zip == zip_code)
        result = await db.execute(query)
        prop = result.scalar_one_or_none()

        if prop:
            # Update visit tracking for returning customer
            prop.visit_count = (prop.visit_count or 1) + 1
            prop.last_visit_at = datetime.now(timezone.utc)
            # Update customer info if provided
            if customer_name and not prop.customer_name:
                prop.customer_name = customer_name
            if customer_phone and not prop.customer_phone:
                prop.customer_phone = customer_phone
            if customer_email and not prop.customer_email:
                prop.customer_email = customer_email
        else:
            # Create new property
            prop = Property(
                id=str(uuid.uuid4()),
                company_id=auth.company_id,
                address_line1=address,
                city=city,
                state=state,
                zip=zip_code,
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_email=customer_email,
                visit_count=1,
                last_visit_at=datetime.now(timezone.utc),
            )
            db.add(prop)
            await db.flush()

    # ── Upload photos ────────────────────────────────────────────────────────
    storage = get_storage()
    photo_urls = []
    photo_records = []
    assessment_id = str(uuid.uuid4())

    for i, photo_file in enumerate(photos):
        raw_bytes = await photo_file.read()

        # Compress
        compressed, mime_type = compress_image(raw_bytes)

        # Build storage path: assessments/{assessment_id}/photo_{i}.jpg
        storage_path = f"assessments/{assessment_id}/photo_{i}.jpg"
        url = await storage.upload(compressed, storage_path)

        photo_urls.append(url)
        photo_records.append({
            "url": url,
            "sort_order": i,
            "original_name": photo_file.filename or f"photo_{i}.jpg",
        })

    # ── Create assessment record ─────────────────────────────────────────────
    assessment = Assessment(
        id=assessment_id,
        company_id=auth.company_id,
        user_id=auth.user_id,
        property_id=prop.id if prop else None,
        photo_urls=photo_urls,
        status="pending",
        tech_overrides={},
    )
    db.add(assessment)

    # Create assessment_photos records
    for rec in photo_records:
        ap = AssessmentPhoto(
            id=str(uuid.uuid4()),
            assessment_id=assessment_id,
            photo_url=rec["url"],
            sort_order=rec["sort_order"],
        )
        db.add(ap)

    await db.commit()

    return {
        "id": assessment_id,
        "status": "pending",
        "photo_count": len(photo_urls),
        "photo_urls": photo_urls,
        "property_id": prop.id if prop else None,
        "message": f"Assessment created. Call /api/assessments/{assessment_id}/analyze to start AI analysis.",
    }


# ── POST /api/assessments/{id}/analyze ────────────────────────────────────────

@router.post("/{assessment_id}/analyze")
async def analyze_assessment(
    assessment_id: str,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Run Gemini Vision AI analysis on uploaded photos.

    - Loads photos from storage
    - Sends to Gemini 2.5 Flash with EQUIPMENT_ANALYSIS_PROMPT
    - Parses JSON response
    - Stores results in assessment (ai_analysis, ai_equipment_id, ai_condition, ai_issues)
    - Creates/updates equipment_instance record
    - Updates status to 'analyzed'
    """
    # Load assessment
    result = await db.execute(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.company_id == auth.company_id
        )
    )
    assessment = result.scalar_one_or_none()

    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found.")

    if assessment.status == "analyzed":
        # Re-analyze is allowed (tech might want fresh analysis)
        pass

    if not assessment.photo_urls:
        raise HTTPException(status_code=400, detail="No photos uploaded for this assessment.")

    # ── Load photo bytes from storage ────────────────────────────────────────
    storage = get_storage()
    image_bytes_list = []
    content_types = []

    for url in assessment.photo_urls:
        try:
            img_bytes = await storage.get_bytes(url)
            if img_bytes:
                image_bytes_list.append(img_bytes)
                content_types.append("image/jpeg")
        except Exception as e:
            print(f"[Analyze] Warning: could not load photo {url}: {e}")

    if not image_bytes_list:
        raise HTTPException(status_code=400, detail="Could not load photos for analysis.")

    # ── Call Gemini Vision AI ────────────────────────────────────────────────
    vision = get_vision_service()
    try:
        ai_result = await vision.analyze_equipment_photos(
            image_bytes_list=image_bytes_list,
            prompt=EQUIPMENT_ANALYSIS_PROMPT,
            image_content_types=content_types,
        )
    except VisionAnalysisError as e:
        # Store error state but don't crash — tech can still manually enter data
        assessment.status = "analysis_failed"
        assessment.ai_analysis = {"error": str(e), "raw": None}
        await db.commit()
        raise HTTPException(
            status_code=502,
            detail=f"AI analysis failed: {str(e)}. You can manually enter equipment details."
        )

    # ── Parse AI response into structured fields ─────────────────────────────
    ai_equipment_id = {
        "brand": ai_result.get("brand"),
        "model": ai_result.get("model_number"),
        "serial": ai_result.get("serial_number"),
        "confidence": ai_result.get("confidence", 0),
        "confidence_reasoning": ai_result.get("confidence_reasoning", ""),
        "equipment_type": ai_result.get("equipment_type", "unknown"),
        "estimated_age_years": ai_result.get("estimated_age_years"),
    }

    ai_condition = {
        "overall": ai_result.get("overall_condition", "unknown"),
        "components": ai_result.get("components", []),
    }

    ai_issues = []
    for comp in ai_result.get("components", []):
        if comp.get("condition") not in ("normal", None):
            ai_issues.append({
                "component": comp.get("name"),
                "condition": comp.get("condition"),
                "description_technical": comp.get("description_technical", ""),
                "description_plain": comp.get("description_plain", ""),
                "urgency": comp.get("urgency", "monitor"),
            })

    # ── Update assessment_photos with annotations ────────────────────────────
    photo_annotations = ai_result.get("photo_annotations", [])

    result = await db.execute(
        select(AssessmentPhoto)
        .where(AssessmentPhoto.assessment_id == assessment_id)
        .order_by(AssessmentPhoto.sort_order)
    )
    ap_records = result.scalars().all()

    for ann_data in photo_annotations:
        photo_idx = ann_data.get("photo_index", 0)
        if photo_idx < len(ap_records):
            ap_records[photo_idx].annotations = ann_data.get("annotations", [])
            ap_records[photo_idx].ai_raw_response = ann_data

    # ── Update assessment record ─────────────────────────────────────────────
    assessment.ai_analysis = ai_result          # Full raw response
    assessment.ai_equipment_id = ai_equipment_id
    assessment.ai_condition = ai_condition
    assessment.ai_issues = ai_issues
    assessment.status = "analyzed"

    # ── Create or update equipment_instance ─────────────────────────────────
    if assessment.property_id:
        equip_result = await db.execute(
            select(EquipmentInstance).where(
                EquipmentInstance.property_id == assessment.property_id,
                EquipmentInstance.brand == ai_equipment_id.get("brand"),
            )
        )
        equip_inst = equip_result.scalar_one_or_none()

        if not equip_inst:
            equip_inst = EquipmentInstance(
                id=str(uuid.uuid4()),
                property_id=assessment.property_id,
                equipment_type=ai_equipment_id.get("equipment_type", "unknown"),
                brand=ai_equipment_id.get("brand"),
                model_number=ai_equipment_id.get("model"),
                serial_number=ai_equipment_id.get("serial"),
                condition=ai_condition.get("overall"),
                condition_details={c.get("name", c.get("component", "unknown")): c.get("condition") for c in ai_condition.get("components", [])},
                photo_urls=assessment.photo_urls,
                ai_confidence=ai_equipment_id.get("confidence"),
            )
            db.add(equip_inst)
            await db.flush()
        else:
            # Update existing
            equip_inst.condition = ai_condition.get("overall")
            equip_inst.ai_confidence = ai_equipment_id.get("confidence")
            equip_inst.last_assessed_at = datetime.now(timezone.utc)

        assessment.equipment_instance_id = equip_inst.id

    await db.commit()

    # ── Trigger WP-03 equipment matcher (if available) ───────────────────────
    try:
        from services.equipment_matcher import match_equipment_model
        from services.serial_decoder import decode_serial
        matched = await match_equipment_model(
            brand=ai_equipment_id.get("brand", ""),
            model_number=ai_equipment_id.get("model", ""),
            db=db
        )
        if matched:
            ai_equipment_id["matched_model_id"] = matched.id
            ai_equipment_id["avg_lifespan_years"] = matched.avg_lifespan_years
            ai_equipment_id["known_issues"] = matched.known_issues
            assessment.ai_equipment_id = ai_equipment_id

        # Decode serial number
        serial = ai_equipment_id.get("serial", "")
        brand = ai_equipment_id.get("brand", "")
        if serial and brand:
            decoded = decode_serial(brand, serial)
            if decoded:
                ai_equipment_id["serial_decoded"] = decoded
                assessment.ai_equipment_id = ai_equipment_id

        await db.commit()
    except ImportError:
        pass  # WP-03 not yet implemented — that's OK
    except Exception as e:
        print(f"[Analyze] WP-03 integration warning: {e}")

    low_confidence = ai_result.get("_low_confidence", False)
    confidence = ai_equipment_id.get("confidence", 0)

    return {
        "id": assessment_id,
        "status": "analyzed",
        "ai_equipment_id": ai_equipment_id,
        "ai_condition": ai_condition,
        "ai_issues": ai_issues,
        "photo_annotations": photo_annotations,
        "low_confidence": low_confidence,
        "confidence": confidence,
        "message": (
            f"Analysis complete. Confidence: {confidence}%. "
            + ("⚠️ Low confidence — consider requesting additional photos." if low_confidence else "")
        ),
    }


# ── GET /api/assessments/{id} ─────────────────────────────────────────────────

@router.get("/{assessment_id}")
async def get_assessment(
    assessment_id: str,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns full assessment details including AI analysis results."""
    result = await db.execute(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.company_id == auth.company_id,
        )
    )
    assessment = result.scalar_one_or_none()

    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found.")

    # Load photos with annotations
    photos_result = await db.execute(
        select(AssessmentPhoto)
        .where(AssessmentPhoto.assessment_id == assessment_id)
        .order_by(AssessmentPhoto.sort_order)
    )
    photos = photos_result.scalars().all()

    return {
        "id": assessment.id,
        "status": assessment.status,
        "photo_urls": assessment.photo_urls,
        "ai_equipment_id": assessment.ai_equipment_id,
        "ai_condition": assessment.ai_condition,
        "ai_issues": assessment.ai_issues,
        "ai_analysis": assessment.ai_analysis,
        "tech_overrides": assessment.tech_overrides,
        "property_id": assessment.property_id,
        "equipment_instance_id": assessment.equipment_instance_id,
        "photos": [
            {
                "id": p.id,
                "url": p.photo_url,
                "annotated_url": p.annotated_photo_url,
                "annotations": p.annotations,
                "sort_order": p.sort_order,
            }
            for p in photos
        ],
    }


# ── PATCH /api/assessments/{id} ───────────────────────────────────────────────

@router.patch("/{assessment_id}")
async def update_assessment(
    assessment_id: str,
    overrides: AssessmentOverride,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Tech overrides AI results. Stores in assessments.tech_overrides JSONB.
    Example: changing brand from 'Carrier' to 'Trane' when AI misidentified.
    """
    result = await db.execute(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.company_id == auth.company_id,
        )
    )
    assessment = result.scalar_one_or_none()

    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found.")

    # Merge new overrides into existing
    existing_overrides = assessment.tech_overrides or {}
    new_values = {k: v for k, v in overrides.model_dump().items() if v is not None}

    # Track what changed vs AI result for training data
    override_log = {}
    if assessment.ai_equipment_id:
        ai_brand = assessment.ai_equipment_id.get("brand")
        if "brand" in new_values and new_values["brand"] != ai_brand:
            override_log["brand_changed_from"] = ai_brand
    if assessment.ai_condition:
        ai_condition = assessment.ai_condition.get("overall")
        if "overall_condition" in new_values and new_values["overall_condition"] != ai_condition:
            override_log["condition_changed_from"] = ai_condition

    merged = {**existing_overrides, **new_values, "_log": override_log}
    assessment.tech_overrides = merged

    # If overriding brand/model, update ai_equipment_id reflected values too
    if assessment.ai_equipment_id:
        updated_ai = dict(assessment.ai_equipment_id)
        if "brand" in new_values:
            updated_ai["brand"] = new_values["brand"]
            updated_ai["tech_corrected_brand"] = True
        if "model_number" in new_values:
            updated_ai["model"] = new_values["model_number"]
        if "install_year" in new_values:
            updated_ai["install_year"] = new_values["install_year"]
        assessment.ai_equipment_id = updated_ai

    if "overall_condition" in new_values and assessment.ai_condition:
        updated_cond = dict(assessment.ai_condition)
        updated_cond["overall"] = new_values["overall_condition"]
        updated_cond["tech_corrected"] = True
        assessment.ai_condition = updated_cond

    await db.commit()

    return {
        "id": assessment_id,
        "tech_overrides": assessment.tech_overrides,
        "message": f"Override saved. {len(new_values)} field(s) updated.",
    }


# ── POST /api/assessments/{id}/complete ──────────────────────────────────────

@router.post("/{assessment_id}/complete")
async def complete_assessment(
    assessment_id: str,
    actual_cost: Optional[float] = Body(None, embed=True),
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark assessment as complete and record actual cost for accuracy tracking."""
    result = await db.execute(
        select(Assessment).where(
            Assessment.id == assessment_id,
            Assessment.company_id == auth.company_id,
        )
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found.")

    assessment.status = "completed"

    # Update estimate if exists
    from db.models import Estimate
    from sqlalchemy import select as sa_select
    est_result = await db.execute(
        sa_select(Estimate).where(Estimate.assessment_id == assessment_id)
    )
    estimate = est_result.scalar_one_or_none()

    if estimate and actual_cost is not None:
        estimate.actual_cost = actual_cost
        # Calculate accuracy: 100 - abs(estimate - actual) / actual * 100
        if estimate.total_amount and actual_cost > 0:
            accuracy = 100 - abs(float(estimate.total_amount) - actual_cost) / actual_cost * 100
            estimate.accuracy_score = max(0, min(100, accuracy))

        # Update tech's running accuracy score
        from db.models import User
        user_result = await db.execute(
            sa_select(User).where(User.id == auth.user_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            user.total_estimates = (user.total_estimates or 0) + 1
            if estimate.accuracy_score is not None:
                old_score = float(user.accuracy_score or 85)
                old_count = user.total_estimates - 1
                # Running average
                new_score = (old_score * old_count + float(estimate.accuracy_score)) / user.total_estimates
                user.accuracy_score = round(new_score, 2)

    await db.commit()
    return {"id": assessment_id, "status": "completed"}


# ── GET /api/assessments/ ─────────────────────────────────────────────────────

@router.get("/")
async def list_assessments(
    limit: int = 20,
    offset: int = 0,
    filter_status: Optional[str] = None,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists all assessments for the current company."""
    query = select(Assessment).where(Assessment.company_id == auth.company_id)

    if filter_status:
        query = query.where(Assessment.status == filter_status)

    query = query.order_by(Assessment.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    assessments = result.scalars().all()

    return {
        "items": [
            {
                "id": a.id,
                "status": a.status,
                "photo_count": len(a.photo_urls) if a.photo_urls else 0,
                "property_id": a.property_id,
                "brand": a.ai_equipment_id.get("brand") if a.ai_equipment_id else None,
                "model": a.ai_equipment_id.get("model") if a.ai_equipment_id else None,
                "condition": a.ai_condition.get("overall") if a.ai_condition else None,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in assessments
        ],
        "total": len(assessments),
        "limit": limit,
        "offset": offset,
    }
