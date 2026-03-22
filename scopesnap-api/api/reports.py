"""
ScopeSnap — Public Homeowner Report Endpoints
These endpoints are PUBLIC (no auth required) — homeowners access via magic link.
The report_token in the URL is the security layer.

WP-06: Full report data + approval implementation.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.database import get_db
from db.models import (
    Assessment, AssessmentPhoto, Company, Estimate,
    EquipmentInstance, FollowUp, Property, User
)

router = APIRouter(prefix="/api/reports", tags=["reports"])


# ── Request Models ────────────────────────────────────────────────────────────

class ApproveRequest(BaseModel):
    selected_option: str  # 'good' | 'better' | 'best'


# ── GET /api/reports/{report_token} ──────────────────────────────────────────

@router.get("/{report_token}")
async def get_public_report(
    report_token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Public homeowner report endpoint. No authentication required.

    The report_token (32-char random string) is the security layer.
    Sets estimate.viewed_at on FIRST access only (does not overwrite).

    Returns everything needed to render the homeowner report:
    - Company branding (name, logo, phone, license number)
    - Property address + customer name
    - Equipment details (brand, model, install year, SEER, condition)
    - Annotated photos with issue coordinates
    - AI issues in plain English
    - Good/Better/Best option cards with line items
    - 5-year cost comparison data
    - Report metadata (short_id, status)
    """
    # Resolve by report_short_id (URL-facing) OR report_token (internal)
    # URL uses report_short_id; API calls use report_token
    result = await db.execute(
        select(Estimate).where(
            (Estimate.report_token == report_token) |
            (Estimate.report_short_id == report_token)
        )
    )
    estimate = result.scalar_one_or_none()

    if not estimate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found. The link may be invalid or expired.",
        )

    # ── Set viewed_at on first access (idempotent) ────────────────────────────
    first_view = not estimate.viewed_at
    if first_view:
        estimate.viewed_at = datetime.now(timezone.utc)
        # Commit view tracking immediately (best-effort)

    # ── Load assessment ───────────────────────────────────────────────────────
    assessment_result = await db.execute(
        select(Assessment).where(Assessment.id == estimate.assessment_id)
    )
    assessment = assessment_result.scalar_one_or_none()

    # ── Load company ──────────────────────────────────────────────────────────
    company_result = await db.execute(
        select(Company).where(Company.id == estimate.company_id)
    )
    company = company_result.scalar_one_or_none()

    # ── Load property ─────────────────────────────────────────────────────────
    property_data = None
    if assessment and assessment.property_id:
        prop_result = await db.execute(
            select(Property).where(Property.id == assessment.property_id)
        )
        prop = prop_result.scalar_one_or_none()
        if prop:
            property_data = {
                "address_line1": prop.address_line1,
                "city": prop.city,
                "state": prop.state,
                "zip": prop.zip,
                "customer_name": prop.customer_name,
                "customer_phone": prop.customer_phone,
            }

    # ── Load equipment instance ───────────────────────────────────────────────
    equipment_data = None
    if assessment and assessment.equipment_instance_id:
        eq_result = await db.execute(
            select(EquipmentInstance).where(
                EquipmentInstance.id == assessment.equipment_instance_id
            )
        )
        eq = eq_result.scalar_one_or_none()
        if eq:
            equipment_data = {
                "equipment_type": eq.equipment_type,
                "brand": eq.brand,
                "model_number": eq.model_number,
                "serial_number": eq.serial_number,
                "install_year": eq.install_year,
                "condition": eq.condition,
                "condition_details": eq.condition_details,
                "ai_confidence": float(eq.ai_confidence) if eq.ai_confidence else None,
                "last_assessed_at": eq.last_assessed_at.isoformat() if eq.last_assessed_at else None,
            }

    # If no equipment instance but assessment has AI data, use that directly
    if not equipment_data and assessment and assessment.ai_equipment_id:
        ai_eq = assessment.ai_equipment_id or {}
        equipment_data = {
            "equipment_type": ai_eq.get("equipment_type", "ac_unit"),
            "brand": ai_eq.get("brand"),
            "model_number": ai_eq.get("model"),
            "serial_number": ai_eq.get("serial"),
            "install_year": ai_eq.get("install_year"),
            "condition": assessment.ai_condition.get("overall") if assessment.ai_condition else None,
            "condition_details": assessment.ai_condition.get("components") if assessment.ai_condition else None,
            "ai_confidence": ai_eq.get("confidence"),
        }

    # ── Load annotated photos ─────────────────────────────────────────────────
    photos_data = []
    if assessment:
        photos_result = await db.execute(
            select(AssessmentPhoto).where(
                AssessmentPhoto.assessment_id == assessment.id
            ).order_by(AssessmentPhoto.sort_order)
        )
        photos = photos_result.scalars().all()
        for photo in photos:
            photos_data.append({
                "photo_url": photo.photo_url,
                "annotated_photo_url": photo.annotated_photo_url or photo.photo_url,
                "annotations": photo.annotations or [],
            })

    # Fall back to raw photo_urls if no AssessmentPhoto records
    if not photos_data and assessment and assessment.photo_urls:
        for url in assessment.photo_urls:
            photos_data.append({
                "photo_url": url,
                "annotated_photo_url": url,
                "annotations": [],
            })

    # ── Build AI issues in display format ─────────────────────────────────────
    issues_data = []
    if assessment and assessment.ai_issues:
        raw_issues = assessment.ai_issues
        if isinstance(raw_issues, list):
            for issue in raw_issues:
                severity = issue.get("severity", "medium")
                color_map = {"high": "red", "critical": "red", "medium": "orange", "low": "green"}
                issues_data.append({
                    "component": issue.get("component", ""),
                    "issue": issue.get("issue", ""),
                    "severity": severity,
                    "color": color_map.get(severity, "orange"),
                    "description": issue.get("description", ""),
                    "description_plain": issue.get("description_plain", issue.get("description", "")),
                })

    # ── Calculate remaining life estimate ─────────────────────────────────────
    remaining_life = None
    if equipment_data:
        install_year = equipment_data.get("install_year")
        if install_year:
            age = datetime.now().year - install_year
            avg_lifespan = 15  # Default for AC
            remaining = max(0, avg_lifespan - age)
            remaining_life = {
                "age_years": age,
                "avg_lifespan": avg_lifespan,
                "remaining_years": remaining,
                "remaining_pct": round(remaining / avg_lifespan * 100),
            }

    # ── Company branding ──────────────────────────────────────────────────────
    company_data = {}
    if company:
        company_data = {
            "name": company.name,
            "slug": company.slug,
            "logo_url": company.logo_url,
            "phone": company.phone,
            "email": company.email,
            "license_number": company.license_number,
        }

    # ── Build response ────────────────────────────────────────────────────────
    response = {
        # Report metadata
        "report_short_id": estimate.report_short_id,
        "report_token": estimate.report_token,
        "status": estimate.status,
        "created_at": estimate.created_at.isoformat() if estimate.created_at else None,
        "viewed_at": estimate.viewed_at.isoformat() if estimate.viewed_at else None,
        "approved_at": estimate.approved_at.isoformat() if estimate.approved_at else None,
        "selected_option": estimate.selected_option,

        # Company branding
        "company": company_data,

        # Property / customer
        "property": property_data,

        # Equipment details
        "equipment": equipment_data,
        "remaining_life": remaining_life,

        # Photos with annotations
        "photos": photos_data,

        # AI-identified issues
        "issues": issues_data,

        # Good/Better/Best options
        "options": estimate.options or [],

        # URLs for approval
        "approve_url": f"/api/reports/{estimate.report_token}/approve",
    }

    # ── Commit viewed_at + tech notification on first view ────────────────────
    if first_view:
        try:
            await db.commit()
        except Exception:
            await db.rollback()

        # Fire-and-forget tech notification (best-effort — don't fail the request)
        try:
            from services.email import get_email_sender, EmailMessage
            sender = get_email_sender()
            tech_email = company.email if company else None
            if tech_email:
                customer_name_str = (property_data or {}).get("customer_name") or "the homeowner"
                await sender.send(EmailMessage(
                    to=tech_email,
                    subject=f"Report Viewed — {estimate.report_short_id}",
                    html_body=(
                        f"<p>Good news! {customer_name_str} just opened their estimate report.</p>"
                        f"<p>Report: <strong>{estimate.report_short_id}</strong></p>"
                        f"<p>This is a great time to follow up by phone.</p>"
                    ),
                ))
        except Exception as e:
            print(f"[reports] Tech notification failed (non-fatal): {e}")

    return response


# ── POST /api/reports/{report_token}/approve ──────────────────────────────────

@router.post("/{report_token}/approve")
async def approve_report(
    report_token: str,
    body: ApproveRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Homeowner approves the estimate and selects a tier.

    - Sets estimate.selected_option ('good' | 'better' | 'best')
    - Sets estimate.approved_at timestamp
    - Updates estimate.status to 'approved'
    - Returns the selected option details for confirmation display
    """
    if body.selected_option not in ("good", "better", "best"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="selected_option must be 'good', 'better', or 'best'",
        )

    result = await db.execute(
        select(Estimate).where(
            (Estimate.report_token == report_token) |
            (Estimate.report_short_id == report_token)
        )
    )
    estimate = result.scalar_one_or_none()

    if not estimate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        )

    if estimate.status == "approved":
        # Already approved — idempotent
        selected = next(
            (o for o in (estimate.options or []) if o["tier"] == estimate.selected_option),
            None
        )
        return {
            "message": "Already approved",
            "selected_option": estimate.selected_option,
            "selected": selected,
            "approved_at": estimate.approved_at.isoformat() if estimate.approved_at else None,
        }

    # Find the selected option data
    selected_option_data = next(
        (o for o in (estimate.options or []) if o["tier"] == body.selected_option),
        None
    )
    if not selected_option_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Option '{body.selected_option}' not found in this estimate.",
        )

    # Update estimate
    estimate.selected_option = body.selected_option
    estimate.approved_at = datetime.now(timezone.utc)
    estimate.status = "approved"
    estimate.total_amount = selected_option_data.get("total")
    estimate.deposit_amount = round(selected_option_data.get("total", 0) * 0.20, 2)

    # WP-09: Cancel all pending follow-ups for this estimate
    from sqlalchemy import and_
    fu_result = await db.execute(
        select(FollowUp).where(
            and_(
                FollowUp.estimate_id == estimate.id,
                FollowUp.sent_at.is_(None),
                FollowUp.cancelled == False,
            )
        )
    )
    for fu in fu_result.scalars().all():
        fu.cancelled = True

    await db.commit()

    return {
        "message": "Estimate approved",
        "selected_option": body.selected_option,
        "selected": selected_option_data,
        "total": selected_option_data.get("total"),
        "deposit_amount": estimate.deposit_amount,
        "approved_at": estimate.approved_at.isoformat(),
        "status": "approved",
    }
