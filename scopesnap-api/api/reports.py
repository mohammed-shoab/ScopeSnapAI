"""
SnapAI — Public Homeowner Report Endpoints
These endpoints are PUBLIC (no auth required) — homeowners access via magic link.
The report_token in the URL is the security layer.

WP-06: Full report data + approval implementation.
"""

import json
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from rate_limit import limiter
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import sentry_sdk
from sqlalchemy import select, text

from api.dependencies import get_tables, MarketTables, tables_for_market
from api.estimates import _enrich_tco_from_db
from db.database import get_db
from db.models import (
    Assessment, AssessmentPhoto, Company, Estimate,
    EquipmentInstance, FollowUp, Property, User
)

router = APIRouter(prefix="/api/reports", tags=["reports"])

logger = logging.getLogger(__name__)

# Level 2 footer disclaimers (Codie-authored, DEC-088 compliant). Loaded once.
try:
    _L2_UNIVERSAL = json.load(open(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "data",
                     "level2_universal_strings.json"), encoding="utf-8"
    ))
    _L2_FOOTERS = _L2_UNIVERSAL.get("footers", {}) or {}
except Exception as _exc:  # pragma: no cover - defensive
    logging.getLogger(__name__).warning("Level 2 footers load failed: %s", _exc)
    _L2_FOOTERS = {}


# ── Request Models ────────────────────────────────────────────────────────────

class ApproveRequest(BaseModel):
    selected_option: str  # 'good' | 'better' | 'best'


class CorrectAgeRequest(BaseModel):
    # Homeowners aren't logged in: this endpoint is public (token-gated).
    # The live frontend posts {install_year, source, corrected_by}; the Stage 3B
    # plan also allows {corrected_year} or {relative_age_years}. Accept all —
    # install_year and corrected_year are equivalent (the corrected install year),
    # relative_age_years derives corrected_year = current_year - relative_age_years.
    install_year:       Optional[int] = None
    corrected_year:     Optional[int] = None
    relative_age_years: Optional[int] = None
    source:             Optional[str] = None
    corrected_by:       Optional[str] = "homeowner"


# ── GET /api/reports/{report_token} ──────────────────────────────────────────

@router.get("/{report_token}")
@limiter.limit("30/minute")  # throttle report_short_id brute-force enumeration (PII) per IP
async def get_public_report(
    request: Request,
    report_token: str,
    db: AsyncSession = Depends(get_db),
    tables: MarketTables = Depends(get_tables),
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

    # ── A.3 fix: Step 1 ─ query diagnostic session first ─────────────
    # Diagnostic tree result is the primary issue source. Must be queried first
    # so it can serve as primary issues data rather than a fallback.
    diagnostic_resolved = False
    photo_skipped_flag = False
    ds_row = None
    if assessment:
        ds_result = await db.execute(
            text(
                "SELECT resolved_card_id, photo_skipped FROM diagnostic_sessions "
                "WHERE assessment_id = :aid AND resolved_card_id IS NOT NULL "
                "ORDER BY created_at DESC LIMIT 1"
            ),
            {"aid": str(assessment.id)},
        )
        ds_row = ds_result.fetchone()
        diagnostic_resolved = ds_row is not None
        photo_skipped_flag = bool(ds_row[1]) if ds_row is not None else False

    complaint = (assessment.tech_overrides or {}).get("complaint_type", "") if assessment else ""

    # ── A.3 fix: Step 2 ─ primary issues from fault card ─────────────────
    # If the diagnostic tree resolved a fault card, that IS the issue the
    # homeowner called about. Show it first. Service/tune-up visits are
    # excluded -- they have no fault, they get the fallback below.
    issues_data = []
    if (diagnostic_resolved and ds_row
            and complaint not in ("service", "tune_up", "maintenance")):
        # Trusted market: select market-dependent tables from estimate.market (the
        # market this estimate was priced in), NOT the spoofable X-Market header on
        # this public route. Mirrors the currency stamp which already trusts it.
        report_tables = tables_for_market(getattr(estimate, "market", "US") or "US")
        fc_table = "pak_fault_cards" if report_tables.market == "PK" else report_tables.fault_cards
        fc_result = await db.execute(
            text(f"SELECT card_name FROM {fc_table} WHERE card_id = :cid LIMIT 1"),
            {"cid": ds_row[0]},
        )
        fc_row = fc_result.fetchone()
        if fc_row:
            issues_data = [{
                "component": "system",
                "issue": fc_row[0],
                "severity": "high",
                "color": "red",
                "description": (
                    f"Your technician diagnosed: {fc_row[0]}. "
                    "See the recommended repair options below."
                ),
                "description_plain": (
                    f"Your technician diagnosed: {fc_row[0]}. "
                    "See the recommended repair options below."
                ),
            }]

    # ── Step 3 ─ supplementary: AI photo analysis issues (append) ───────────
    # Append any AI-detected visual issues after the primary fault card.
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

    # ── Step 4 ─ fallback when no diagnostic resolution and no ai_issues ──────
    if not issues_data and assessment:
        has_cost = bool(
            estimate.options and
            any(opt.get("total", 0) or 0 > 0 for opt in estimate.options)
        )

        if complaint in ("service", "tune_up", "maintenance"):
            # Legitimate no-fault outcome for service/tune-up visits
            issues_data = [{
                "component": "system",
                "issue": "Preventive service completed",
                "severity": "low",
                "color": "green",
                "description": "Recommended preventive service to keep your system running well.",
                "description_plain": "Recommended preventive service to keep your system running well.",
            }]
        elif complaint in ("not_cooling", "water_dripping", "not_turning_on") and has_cost:
            # Real app gap -- diagnostic tree did not resolve but estimate was generated
            sentry_sdk.capture_message(
                f"Estimate generated without diagnostic resolution for complaint type: {complaint}",
                level="warning",
                extras={"assessment_id": str(assessment.id), "complaint_type": complaint},
            )
            issues_data = [{
                "component": "system",
                "issue": "Technician diagnostic",
                "severity": "medium",
                "color": "orange",
                "description": "Your technician identified the issue during the on-site visit. Contact us if you have questions.",
                "description_plain": "Your technician identified the issue during the on-site visit. Contact us if you have questions.",
            }]

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
    # Q.4: Always show contractor branding — removed PAID_PLANS gate (DEC-016).
    # Pre-send modal in Estimate Builder ensures contractor profile is complete
    # before any report reaches a homeowner. See Track R.7 for the modal itself.
    company_data = {}
    if company:
        company_data = {
            "name": company.name,
            "slug": company.slug,
            "logo_url": company.logo_url if company.logo_url else None,
            "phone": company.phone,
            "email": company.email,
            "license_number": company.license_number,
            "custom_branding": True,
            # DEC-088: contractor-controlled warranty terms. Only shown when the
            # owner has filled the field in; None/blank => no warranty language.
            "warranty_text": (getattr(company, "warranty_text", None) or None),
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

        # R.8: Site visit fee footer disclaimer (US default; PK follow-up in Track P)
        # Future: read from company.site_visit_fee_text when column is added
        "site_visit_fee_text": "Diagnostic visit fee $89 — waived upon repair approval.",

        # Level 2 footer disclaimers (cost transparency + written-estimate
        # validity). Conservative, FTC §5-aware wording; "final price may vary"
        # is permitted industry practice, not a statutory requirement.
        "cost_transparency_footer": _L2_FOOTERS.get("cost_transparency"),
        "estimate_validity_footer": _L2_FOOTERS.get("estimate_validity"),

        # R.9 (track-f-a.1): Seasonal labor surcharge disclosure for homeowner report.
        # Reads estimate.seasonal_modifier_pct (frozen at generation time, migration 029).
        "seasonal_note": (
            f"Includes {estimate.seasonal_modifier_pct}% peak-season labor surcharge."
            if (getattr(estimate, 'seasonal_modifier_pct', 0) or 0) > 0
            else None
        ),

        # B.6: on-site photo not captured — triggers disclosure on homeowner report
        "photo_skipped": photo_skipped_flag,

        # BUG-037: market stamp — 'US' | 'PK' — tells the report viewer which
        # currency to use regardless of which domain serves the page.
        "market": getattr(estimate, "market", "US") or "US",
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

    # G.4 BUG-029: enrich options[].five_year_comparison from TCO tables
    response = await _enrich_tco_from_db(response, estimate, db, tables)

    return response


# ── POST /api/reports/{report_token}/approve ──────────────────────────────────

@router.post("/{report_token}/approve")
@limiter.limit("10/minute")  # tighter cap on the state-changing approve-by-short_id path
async def approve_report(
    request: Request,
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
    if body.selected_option not in ("good", "better", "best", "A", "B", "C"):
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

    # WP-09: Cancel homeowner follow-ups (but NOT tech_confirm_24h)
    from sqlalchemy import and_
    fu_result = await db.execute(
        select(FollowUp).where(
            and_(
                FollowUp.estimate_id == estimate.id,
                FollowUp.sent_at.is_(None),
                FollowUp.cancelled == False,
                FollowUp.template != "tech_confirm_24h",
            )
        )
    )
    for fu in fu_result.scalars().all():
        fu.cancelled = True

    # WS-M3: Schedule tech confirmation email 24 h after homeowner approves
    # The cron (process-followups) will send it to the company/tech email
    now_utc = datetime.now(timezone.utc)
    tech_fu = FollowUp(
        estimate_id=estimate.id,
        type="email",
        scheduled_at=now_utc + timedelta(hours=24),
        template="tech_confirm_24h",
        cancelled=False,
    )
    db.add(tech_fu)

    await db.commit()

    # C.4: Fire-and-forget broadcast approval notification via Supabase Realtime
    try:
        import asyncio
        from httpx import AsyncClient
        from config import get_settings as _get_settings
        _settings = _get_settings()
        if _settings.supabase_service_role_key:
            async def _broadcast():
                try:
                    async with AsyncClient() as _client:
                        await _client.post(
                            f"{_settings.supabase_url}/realtime/v1/api/broadcast",
                            headers={
                                "apikey": _settings.supabase_service_role_key,
                                "Content-Type": "application/json",
                            },
                            json={"messages": [{
                                "topic": f"approval-{estimate.company_id}",
                                "event": "assessment_approved",
                                "payload": {
                                    "estimate_id": str(estimate.id),
                                    "report_short_id": estimate.report_short_id,
                                    "selected_option": body.selected_option,
                                    "option_name": selected_option_data.get("name") or body.selected_option.title(),
                                    "total": selected_option_data.get("total"),
                                    "company_id": str(estimate.company_id),
                                },
                            }]},
                            timeout=3.0,
                        )
                except Exception as _e:
                    print(f"[reports] Realtime broadcast failed (non-fatal): {_e}")
            asyncio.create_task(_broadcast())
    except Exception as _e:
        print(f"[reports] Realtime setup failed (non-fatal): {_e}")

    return {
        "message": "Estimate approved",
        "selected_option": body.selected_option,
        "selected": selected_option_data,
        "total": selected_option_data.get("total"),
        "deposit_amount": estimate.deposit_amount,
        "approved_at": estimate.approved_at.isoformat(),
        "status": "approved",
    }



# ── POST /api/reports/{report_token}/correct-age ─────────────────────────────
# Stage 3B: public (token-gated) homeowner install-year correction.
# Records the correction + returns a recomputed remaining-life BAND for display.
# Does NOT mutate the saved estimate snapshot (historical estimates are frozen).

def _remaining_life_band_for_year(install_year: Optional[int],
                                  avg_lifespan_years: float = 18.0) -> Optional[str]:
    """Houston-adjusted remaining-life RANGE string (never year-exact).

    Mirrors the frontend recompute: remaining = lifespan - age, rendered as a
    +/-2 band floored at 0. None when the install year is unknown.
    """
    if install_year is None:
        return None
    current_year = datetime.now(timezone.utc).year
    age = max(0, current_year - int(install_year))
    remaining = max(0.0, float(avg_lifespan_years) - age)
    lo = max(0, int(round(remaining - 2)))
    hi = max(lo, int(round(remaining + 2)))
    return f"{lo}-{hi} years"


def _resolve_corrected_year(body: "CorrectAgeRequest") -> Optional[int]:
    """Resolve the corrected install year from whichever field the client sent.

    Precedence: explicit corrected_year/install_year, else derive from
    relative_age_years (current_year - relative_age_years). Returns None if none
    were provided (caller raises 400).
    """
    if body.corrected_year is not None:
        return body.corrected_year
    if body.install_year is not None:
        return body.install_year
    if body.relative_age_years is not None:
        return datetime.now(timezone.utc).year - int(body.relative_age_years)
    return None


@router.post("/{report_token}/correct-age")
async def correct_report_age(
    report_token: str,
    body: CorrectAgeRequest,
    db: AsyncSession = Depends(get_db),
):
    """Homeowner corrects the equipment install year (Stage 3B, public).

    - Looks up the estimate by report_token / report_short_id (same lookup as the
      public report-fetch + approve endpoints).
    - Reads the ORIGINAL install year + confidence + source from stored data
      (EquipmentInstance, else assessment.ai_equipment_id).
    - Fires services.analytics.fire_age_corrected(corrected_by="homeowner") best-effort.
    - Returns the original/corrected years, signed delta, and a RECOMPUTED
      remaining-life band (display only) — it never overwrites the saved estimate.
    """
    corrected_year = _resolve_corrected_year(body)
    if corrected_year is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide one of: corrected_year, install_year, or relative_age_years.",
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found."
        )

    # Resolve the assessment + original equipment data (EquipmentInstance first,
    # then the assessment's stored AI equipment blob).
    original_year: Optional[int] = None
    original_confidence = None
    original_source: Optional[str] = None
    assessment = None
    if estimate.assessment_id:
        a_res = await db.execute(
            select(Assessment).where(Assessment.id == estimate.assessment_id)
        )
        assessment = a_res.scalar_one_or_none()

    if assessment and assessment.equipment_instance_id:
        eq_res = await db.execute(
            select(EquipmentInstance).where(
                EquipmentInstance.id == assessment.equipment_instance_id
            )
        )
        eq = eq_res.scalar_one_or_none()
        if eq:
            original_year = eq.install_year
            original_confidence = (
                float(eq.ai_confidence) if eq.ai_confidence is not None else None
            )

    if original_year is None and assessment and assessment.ai_equipment_id:
        ai_eq = assessment.ai_equipment_id or {}
        original_year = ai_eq.get("install_year")
        if original_confidence is None:
            original_confidence = ai_eq.get("confidence")
        original_source = ai_eq.get("age_source") or ai_eq.get("source")

    # Best-effort analytics event — never block the response.
    try:
        from services.analytics import fire_age_corrected, correction_delta_years
        fire_age_corrected(
            assessment_id=str(estimate.assessment_id) if estimate.assessment_id else str(estimate.id),
            original_year=original_year,
            corrected_year=corrected_year,
            original_confidence=original_confidence,
            original_source=original_source or body.source,
            corrected_by=body.corrected_by or "homeowner",
            distinct_id=estimate.report_short_id,
        )
        delta = correction_delta_years(original_year, corrected_year)
    except Exception:
        try:
            delta = (corrected_year - original_year) if original_year is not None else None
        except Exception:
            delta = None

    return {
        "original_year": original_year,
        "corrected_year": corrected_year,
        "correction_delta_years": delta,
        "remaining_life_band": _remaining_life_band_for_year(corrected_year),
    }
