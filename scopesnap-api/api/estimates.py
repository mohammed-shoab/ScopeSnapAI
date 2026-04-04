"""
SnapAI — Estimate API Endpoints
WP-04: Full estimate generation pipeline + CRUD
WP-05: Document generation + sending (placeholders)
"""

import copy
import secrets
import string
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from sqlalchemy.orm.attributes import flag_modified

from db.database import get_db
from db.models import Assessment, Company, Estimate, EstimateLineItem, FollowUp, Property
from api.auth import get_current_user, AuthContext
from services.estimate_engine import generate_estimate as run_estimate_engine, calculate_line_items, apply_markup, get_pricing_rule
from config import get_settings

router = APIRouter(prefix="/api/estimates", tags=["estimates"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_report_token(n: int = 32) -> str:
    """Generates a cryptographically random URL-safe token."""
    return secrets.token_urlsafe(n)[:n]


def _make_report_short_id() -> str:
    """Generates human-readable short ID like 'rpt-0847'."""
    digits = "".join(secrets.choice(string.digits) for _ in range(4))
    return f"rpt-{digits}"


def _estimate_to_dict(estimate: Estimate) -> dict:
    """Serializes an Estimate ORM record to a response dict."""
    return {
        "id": str(estimate.id),
        "assessment_id": str(estimate.assessment_id),
        "company_id": str(estimate.company_id),
        "report_token": estimate.report_token,
        "report_short_id": estimate.report_short_id,
        "options": estimate.options,
        "selected_option": estimate.selected_option,
        "total_amount": float(estimate.total_amount) if estimate.total_amount else None,
        "deposit_amount": float(estimate.deposit_amount) if estimate.deposit_amount else None,
        "markup_percent": float(estimate.markup_percent),
        "status": estimate.status,
        "viewed_at": estimate.viewed_at.isoformat() if estimate.viewed_at else None,
        "approved_at": estimate.approved_at.isoformat() if estimate.approved_at else None,
        "contractor_pdf_url": estimate.contractor_pdf_url,
        "homeowner_report_url": estimate.homeowner_report_url,
        "sent_via": estimate.sent_via,
        "sent_at": estimate.sent_at.isoformat() if estimate.sent_at else None,
        "created_at": estimate.created_at.isoformat() if estimate.created_at else None,
    }


# ── Request Models ────────────────────────────────────────────────────────────

class GenerateEstimateRequest(BaseModel):
    assessment_id: str
    markup_percent: Optional[float] = Field(None, ge=0, le=200)
    # If not provided, uses company default (usually 35%)


class UpdateEstimateRequest(BaseModel):
    markup_percent: Optional[float] = Field(None, ge=0, le=200)
    selected_option: Optional[str] = Field(None, pattern="^(good|better|best)$")
    options: Optional[list] = None  # Full options array replacement (e.g. to rename option names)
    # Tech can manually choose recommended option


# ── POST /api/estimates/generate ─────────────────────────────────────────────

@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_estimate(
    body: GenerateEstimateRequest,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generates Good/Better/Best estimate options from assessment AI results.

    9-step pipeline (Tech Spec §05) — pure math + DB lookups, zero AI cost:
    1. Load assessment + AI analysis
    2. Determine job types from condition → options mapping
    3. Look up pricing (cascade: company → region → national)
    4. Calculate line items (parts, labor, permits, disposal, refrigerant)
    5. Apply markup percentage
    6. Calculate energy savings (SEER comparison formula)
    7. Check rebate eligibility
    8. Build Good/Better/Best options array
    9. Calculate 5-year total cost per option
    """
    # ── Load assessment ───────────────────────────────────────────────────────
    result = await db.execute(
        select(Assessment).where(
            Assessment.id == body.assessment_id,
            Assessment.company_id == auth.company_id,
        )
    )
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    if not assessment.ai_analysis:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Assessment has not been analyzed yet. Run POST /api/assessments/{id}/analyze first.",
        )

    # ── Check for existing estimate ───────────────────────────────────────────
    existing_result = await db.execute(
        select(Estimate).where(Estimate.assessment_id == body.assessment_id)
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Estimate already exists for this assessment. Use PATCH /api/estimates/{existing.id} to update.",
        )

    # ── Get company for settings ──────────────────────────────────────────────
    company_result = await db.execute(
        select(Company).where(Company.id == auth.company_id)
    )
    company = company_result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    # Determine markup: request body > company default > 35%
    markup_percent = body.markup_percent
    if markup_percent is None:
        company_settings = company.settings or {}
        markup_percent = company_settings.get("default_markup_percent", 35.0)

    company_state = company.state

    # ── Run engine ────────────────────────────────────────────────────────────
    engine_result = await run_estimate_engine(
        assessment_id=body.assessment_id,
        assessment=assessment,
        company_id=auth.company_id,
        company_state=company_state,
        markup_percent=markup_percent,
        db=db,
    )

    # ── Create Estimate record ────────────────────────────────────────────────
    # Ensure unique short IDs with retry
    for _ in range(10):
        short_id = _make_report_short_id()
        exists_check = await db.execute(
            select(Estimate).where(Estimate.report_short_id == short_id)
        )
        if not exists_check.scalar_one_or_none():
            break

    estimate = Estimate(
        assessment_id=body.assessment_id,
        company_id=auth.company_id,
        report_token=_make_report_token(),
        report_short_id=short_id,
        options=engine_result["options"],
        markup_percent=markup_percent,
        status="draft",
    )
    db.add(estimate)
    await db.flush()  # Get ID without full commit

    # ── Create EstimateLineItem records ───────────────────────────────────────
    for sort_idx, option in enumerate(engine_result["options"]):
        tier = option["tier"]
        for item_idx, item in enumerate(option.get("line_items", [])):
            line_item = EstimateLineItem(
                estimate_id=estimate.id,
                option_tier=tier,
                category=item.get("category", "parts"),
                description=item.get("description", ""),
                quantity=item.get("quantity", 1.0),
                unit_cost=item.get("unit_cost", 0.0),
                total=item.get("total", 0.0),
                source=item.get("source", "pricing_db"),
                sort_order=(sort_idx * 100) + item_idx,
            )
            db.add(line_item)

    # ── Update assessment status ──────────────────────────────────────────────
    assessment.status = "estimated"

    # ── Increment company estimate count ─────────────────────────────────────
    company.monthly_estimate_count = (company.monthly_estimate_count or 0) + 1

    await db.commit()
    await db.refresh(estimate)

    return {
        "id": str(estimate.id),
        "assessment_id": str(estimate.assessment_id),
        "report_token": estimate.report_token,
        "report_short_id": estimate.report_short_id,
        "markup_percent": float(estimate.markup_percent),
        "status": estimate.status,
        "equipment_type": engine_result["equipment_type"],
        "overall_condition": engine_result["overall_condition"],
        "estimated_age_years": engine_result["estimated_age_years"],
        "options": estimate.options,
        "created_at": estimate.created_at.isoformat() if estimate.created_at else None,
    }


# ── GET /api/estimates/process-followups (WP-09 cron) — MUST BE BEFORE /{id} ─

@router.get("/process-followups")
async def process_followups_early(
    db: AsyncSession = Depends(get_db),
):
    """
    WP-09: Cron endpoint — processes due follow-up emails.
    Registered here (before /{estimate_id}) so FastAPI matches it correctly.
    """
    from services.email import get_email_sender
    from sqlalchemy import and_

    now = datetime.now(timezone.utc)
    sender = get_email_sender()
    sent_count = 0
    cancelled_count = 0
    errors = []

    due_result = await db.execute(
        select(FollowUp).where(
            and_(
                FollowUp.scheduled_at <= now,
                FollowUp.sent_at.is_(None),
                FollowUp.cancelled == False,
            )
        )
    )
    due_followups = due_result.scalars().all()

    for fu in due_followups:
        est_result = await db.execute(
            select(Estimate).where(Estimate.id == fu.estimate_id)
        )
        estimate = est_result.scalar_one_or_none()
        if not estimate:
            fu.cancelled = True
            cancelled_count += 1
            continue

        if estimate.status in ("approved", "completed"):
            fu.cancelled = True
            cancelled_count += 1
            continue

        assessment = None
        property_record = None
        if estimate.assessment_id:
            assess_result = await db.execute(
                select(Assessment).where(Assessment.id == estimate.assessment_id)
            )
            assessment = assess_result.scalar_one_or_none()
        if assessment and assessment.property_id:
            prop_result = await db.execute(
                select(Property).where(Property.id == assessment.property_id)
            )
            property_record = prop_result.scalar_one_or_none()

        company_result = await db.execute(
            select(Company).where(Company.id == estimate.company_id)
        )
        company = company_result.scalar_one_or_none()
        company_name = company.name if company else "SnapAI HVAC"
        base_url = get_settings().frontend_url

        to_email = (property_record.customer_email if property_record else None) or "homeowner@example.com"
        customer_name = (property_record.customer_name if property_record else None) or "Valued Customer"

        if estimate.homeowner_report_url:
            report_url = (
                estimate.homeowner_report_url
                if estimate.homeowner_report_url.startswith("http")
                else f"{base_url}{estimate.homeowner_report_url}"
            )
        else:
            slug = company.slug if company else "hvac"
            report_url = f"{base_url}/r/{slug}/{estimate.report_short_id}"

        try:
            await sender.send_follow_up(
                to=to_email, company_name=company_name, report_url=report_url,
                template=fu.template, customer_name=customer_name,
            )
            fu.sent_at = now
            sent_count += 1
        except Exception as e:
            errors.append({"follow_up_id": str(fu.id), "error": str(e)})

    await db.commit()

    return {
        "processed_at": now.isoformat(),
        "due_found": len(due_followups),
        "sent": sent_count,
        "cancelled": cancelled_count,
        "errors": errors,
    }


# ── GET /api/estimates/{id} ───────────────────────────────────────────────────

@router.get("/{estimate_id}")
async def get_estimate(
    estimate_id: str,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns full estimate including all Good/Better/Best options and line items."""
    result = await db.execute(
        select(Estimate).where(
            Estimate.id == estimate_id,
            Estimate.company_id == auth.company_id,
        )
    )
    estimate = result.scalar_one_or_none()
    if not estimate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estimate not found")

    data = _estimate_to_dict(estimate)

    # Attach homeowner view count from app_events (report_viewed events)
    try:
        vc_result = await db.execute(
            text(
                "SELECT COUNT(*) FROM app_events "
                "WHERE event_name = 'report_viewed' "
                "AND event_data->>'report_short_id' = :short_id"
            ),
            {"short_id": estimate.report_short_id},
        )
        data["view_count"] = int(vc_result.scalar_one() or 0)
    except Exception:
        data["view_count"] = 0

    return data


# ── PATCH /api/estimates/{id} ─────────────────────────────────────────────────

@router.patch("/{estimate_id}")
async def update_estimate(
    estimate_id: str,
    body: UpdateEstimateRequest,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Tech adjusts estimate details. Recalculates totals when markup changes.

    - markup_percent: recalculates all option totals and line items
    - selected_option: sets recommended option (good/better/best)
    """
    result = await db.execute(
        select(Estimate).where(
            Estimate.id == estimate_id,
            Estimate.company_id == auth.company_id,
        )
    )
    estimate = result.scalar_one_or_none()
    if not estimate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estimate not found")

    updated_fields = []

    # ── Update markup + recalculate ───────────────────────────────────────────
    if body.markup_percent is not None and body.markup_percent != float(estimate.markup_percent):
        old_markup = float(estimate.markup_percent)
        new_markup = body.markup_percent
        estimate.markup_percent = new_markup

        # Recalculate option totals in the stored options JSONB
        # Deep copy required: SQLAlchemy doesn't track mutations on nested JSON objects
        updated_options = copy.deepcopy(estimate.options)
        for option in updated_options:
            subtotal = Decimal(str(option.get("subtotal", 0)))

            new_total = apply_markup(subtotal, new_markup)
            option["total"] = float(new_total)
            option["markup_percent"] = new_markup
            option["total_after_rebate"] = float(new_total) - option.get("rebate_available", 0)

            # Recalculate 5-year total:
            # 5yr = upfront + annual_energy*5 + future_repairs
            # Extract annual_energy*5 + future_repairs by subtracting old upfront
            old_upfront = float(subtotal) * (1 + old_markup / 100)
            old_five_yr = option.get("five_year_total", old_upfront)
            running_costs = old_five_yr - old_upfront  # energy + repairs component
            option["five_year_total"] = round(float(new_total) + running_costs, 2)
            # NOTE: do NOT append here — options are mutated in-place on the deepcopy

        estimate.options = updated_options
        # Force SQLAlchemy to detect the JSON mutation
        flag_modified(estimate, "options")
        updated_fields.append("markup_percent")

    if body.selected_option is not None:
        estimate.selected_option = body.selected_option
        # Set total_amount from selected option
        for option in estimate.options:
            if option["tier"] == body.selected_option:
                estimate.total_amount = option["total"]
                estimate.deposit_amount = round(option["total"] * 0.20, 2)
                break
        updated_fields.append("selected_option")

    if body.options is not None:
        # Allow direct replacement of the options array (e.g. to rename option names)
        # Preserve existing tier/totals structure; only allow safe field overrides
        existing_by_tier = {o["tier"]: o for o in (estimate.options or [])}
        merged = []
        for new_opt in body.options:
            tier = new_opt.get("tier")
            if tier and tier in existing_by_tier:
                # Merge: only allow overriding name and description
                base = copy.deepcopy(existing_by_tier[tier])
                if "name" in new_opt:
                    base["name"] = new_opt["name"]
                if "description" in new_opt:
                    base["description"] = new_opt["description"]
                merged.append(base)
            else:
                merged.append(new_opt)
        estimate.options = merged
        flag_modified(estimate, "options")
        updated_fields.append("options")

    if not updated_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided to update",
        )

    await db.commit()
    await db.refresh(estimate)
    return _estimate_to_dict(estimate)


# ── GET /api/estimates/ ───────────────────────────────────────────────────────

@router.get("/")
async def list_estimates(
    limit: int = 20,
    offset: int = 0,
    status_filter: Optional[str] = None,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lists all estimates for the current company, most recent first."""
    query = select(Estimate).where(Estimate.company_id == auth.company_id)

    if status_filter:
        query = query.where(Estimate.status == status_filter)

    query = query.order_by(Estimate.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    estimates = result.scalars().all()

    return {
        "items": [_estimate_to_dict(e) for e in estimates],
        "count": len(estimates),
        "offset": offset,
        "limit": limit,
    }


# ── POST /api/estimates/{id}/documents ───────────────────────────────────────

@router.post("/{estimate_id}/documents")
async def generate_documents(
    estimate_id: str,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    WP-07: Generates contractor PDF estimate.
    - Loads estimate + related data from DB
    - Renders HTML template via Jinja2
    - Converts to PDF via WeasyPrint
    - Saves to LocalStorage (/tmp/scopesnap_uploads/pdfs/)
    - Updates estimate.contractor_pdf_url
    - Returns {contractor_pdf_url, homeowner_report_url, report_short_id}
    """
    import os
    import logging as _logging
    from config import get_settings

    # Import pdf_generator lazily — WeasyPrint's module-level imports may fail
    # in some Docker environments (missing Cairo/Pango libs). We catch that here
    # so the endpoint still returns a valid HTTP response instead of closing the connection.
    try:
        from services.pdf_generator import generate_contractor_pdf
        _pdf_available = True
    except Exception as _import_err:
        _logging.warning(f"pdf_generator import failed: {_import_err}")
        generate_contractor_pdf = None  # type: ignore
        _pdf_available = False

    # Load estimate
    result = await db.execute(
        select(Estimate).where(
            Estimate.id == estimate_id,
            Estimate.company_id == auth.company_id,
        )
    )
    estimate = result.scalar_one_or_none()
    if not estimate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estimate not found.")

    # Load assessment
    assessment_result = await db.execute(
        select(Assessment).where(Assessment.id == estimate.assessment_id)
    )
    assessment = assessment_result.scalar_one_or_none()

    # Load company
    from db.models import Company, Property, EquipmentInstance
    company_result = await db.execute(select(Company).where(Company.id == auth.company_id))
    company = company_result.scalar_one_or_none()

    # Load property
    property_data = {}
    if assessment and assessment.property_id:
        from db.models import Property
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

    # Load equipment
    equipment_data = {}
    if assessment and assessment.equipment_instance_id:
        from db.models import EquipmentInstance
        eq_result = await db.execute(
            select(EquipmentInstance).where(
                EquipmentInstance.id == assessment.equipment_instance_id
            )
        )
        eq = eq_result.scalar_one_or_none()
        if eq:
            equipment_data = {
                "brand": eq.brand,
                "model_number": eq.model_number,
                "install_year": eq.install_year,
                "condition": eq.condition,
            }

    # Build AI issues for the PDF
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
                    "description_plain": issue.get("description_plain", issue.get("description", "")),
                })

    # Best inspection photo URL — first entry from assessment.photo_urls (R2 or local)
    photo_url = ""
    if assessment and assessment.photo_urls:
        urls = assessment.photo_urls
        if isinstance(urls, list) and urls:
            photo_url = urls[0] or ""

    # Normalize legacy private R2 URLs → public URL.
    # Old uploads mistakenly stored the S3-compatible cloudflarestorage.com endpoint
    # instead of the public r2.dev URL. Convert those so the PDF generator can fetch them.
    _cfg = get_settings()
    if (
        photo_url
        and _cfg.r2_account_id
        and "r2.cloudflarestorage.com" in photo_url
        and _cfg.r2_public_url
    ):
        _private_prefix = f"https://{_cfg.r2_account_id}.r2.cloudflarestorage.com/"
        if photo_url.startswith(_private_prefix):
            photo_url = f"{_cfg.r2_public_url.rstrip('/')}/{photo_url[len(_private_prefix):]}"

    # Assemble data for the PDF generator
    estimate_context = {
        "report_short_id": estimate.report_short_id,
        "report_token": estimate.report_token,
        "assessment_id": str(estimate.assessment_id),
        "photo_url": photo_url,           # inspection photo for annotated embed
        "company": {
            # Phase 1 branding is paid-only — free plan falls back to SnapAI defaults
            **({
                "name": company.name,
                "phone": company.phone,
                "email": company.email,
                "license_number": company.license_number,
                "logo_url": company.logo_url,
            } if company and (company.plan or "free") in {"early_bird", "pro", "team"} else {
                "name": "SnapAI",
                "phone": "",
                "email": "",
                "license_number": "",
                "logo_url": None,
            }),
        },
        "property": property_data,
        "equipment": equipment_data,
        "issues": issues_data,
        "options": estimate.options or [],
    }

    # Generate PDF in a thread then upload to persistent storage (R2 in prod, local in dev)
    import asyncio
    import logging
    import tempfile
    settings = get_settings()
    from services.storage import get_storage, generate_document_path

    pdf_url = None
    pdf_size_kb = 0
    pdf_error = None

    try:
        if not _pdf_available or generate_contractor_pdf is None:
            raise RuntimeError("pdf_generator not available in this environment")

        # Step 1: write PDF to a temp directory (synchronous generator runs in thread)
        tmp_dir = tempfile.mkdtemp()
        loop = asyncio.get_event_loop()
        pdf_path = await loop.run_in_executor(
            None,
            lambda: generate_contractor_pdf(
                estimate_data=estimate_context,
                output_dir=tmp_dir,
                filename=f"estimate-{estimate.report_short_id}.pdf",
            )
        )
        pdf_size_kb = round(os.path.getsize(pdf_path) / 1024, 1)

        # Step 2: upload to R2 (or LocalStorage in dev) so PDF survives redeployments
        with open(pdf_path, "rb") as fh:
            pdf_bytes = fh.read()
        company_slug = company.slug if company else "hvac"
        # Use a timestamp suffix so each generation is stored as a new file.
        # Old files are retained in R2 (10 GB free), so email links to previous
        # versions continue to work even after the estimate is regenerated.
        import datetime as _dt
        _ts = _dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        storage_path = generate_document_path(
            company_slug=company_slug,
            estimate_id=str(estimate.id),
            doc_type=f"estimate-{estimate.report_short_id}-{_ts}.pdf",
        )
        pdf_url = await get_storage().upload(
            file_bytes=pdf_bytes,
            path=storage_path,
            content_type="application/pdf",
        )

        # Step 3: clean up temp file
        try:
            os.unlink(pdf_path)
        except Exception:
            pass

    except Exception as exc:
        # PDF generation or upload failed — log and continue so the rest of
        # the flow (homeowner report URL, Send tab) still works.
        pdf_error = str(exc)
        logging.warning(f"PDF generation failed for {estimate.report_short_id}: {exc}")
        pdf_url = f"/files/pdfs/estimate-{estimate.report_short_id}-unavailable.pdf"

    # Build homeowner report URL (always generated, regardless of PDF success)
    homeowner_url = f"/r/{company.slug if company else 'hvac'}/{estimate.report_short_id}"

    # Update estimate record
    estimate.contractor_pdf_url = pdf_url
    estimate.homeowner_report_url = homeowner_url
    await db.commit()

    response = {
        "contractor_pdf_url": pdf_url,
        "homeowner_report_url": homeowner_url,
        "report_short_id": estimate.report_short_id,
        "pdf_size_kb": pdf_size_kb,
    }
    if pdf_error:
        response["pdf_warning"] = f"PDF rendering unavailable in this environment: {pdf_error}"
    return response


# ── POST /api/estimates/{id}/send (WP-09) ────────────────────────────────────

class SendEstimateRequest(BaseModel):
    homeowner_email: Optional[str] = None
    homeowner_phone: Optional[str] = None
    # If omitted, uses property customer_email / customer_phone from DB


@router.post("/{estimate_id}/send")
async def send_estimate(
    estimate_id: str,
    body: SendEstimateRequest = SendEstimateRequest(),
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    WP-09: Sends estimate to homeowner via email.
    - Emails via ConsoleSender (dev) or ResendSender (prod)
    - Creates 3 FollowUp records: 24h, 48h, 7d
    - Updates estimate.status = 'sent'
    """
    from services.email import get_email_sender

    # ── Load estimate ─────────────────────────────────────────────────────────
    result = await db.execute(
        select(Estimate).where(
            Estimate.id == estimate_id,
            Estimate.company_id == auth.company_id,
        )
    )
    estimate = result.scalar_one_or_none()
    if not estimate:
        raise HTTPException(status_code=404, detail="Estimate not found.")

    # ── Load assessment + property ────────────────────────────────────────────
    assessment = None
    property_record = None
    if estimate.assessment_id:
        assess_result = await db.execute(
            select(Assessment).where(Assessment.id == estimate.assessment_id)
        )
        assessment = assess_result.scalar_one_or_none()
    if assessment and assessment.property_id:
        prop_result = await db.execute(
            select(Property).where(Property.id == assessment.property_id)
        )
        property_record = prop_result.scalar_one_or_none()

    # ── Load company ──────────────────────────────────────────────────────────
    company_result = await db.execute(
        select(Company).where(Company.id == auth.company_id)
    )
    company = company_result.scalar_one_or_none()
    company_name = company.name if company else "SnapAI HVAC"
    base_url = get_settings().frontend_url

    # ── Resolve recipient email ───────────────────────────────────────────────
    to_email = (
        body.homeowner_email
        or (property_record.customer_email if property_record else None)
        or "homeowner@example.com"   # dev fallback
    )
    customer_name = (
        (property_record.customer_name if property_record else None)
        or "Valued Customer"
    )

    # ── Build report URL ──────────────────────────────────────────────────────
    # Ensure documents are generated first (homeowner_report_url may already be set)
    if estimate.homeowner_report_url:
        # Absolute URL for email
        report_url = (
            estimate.homeowner_report_url
            if estimate.homeowner_report_url.startswith("http")
            else f"{base_url}{estimate.homeowner_report_url}"
        )
    else:
        slug = company.slug if company else "hvac"
        report_url = f"{base_url}/r/{slug}/{estimate.report_short_id}"

    # ── Send email ────────────────────────────────────────────────────────────
    sender = get_email_sender()
    # options is a list: [{tier: 'good', total: ...}, ...]
    options_list = estimate.options if isinstance(estimate.options, list) else []
    best_option = next((o for o in options_list if o.get("tier") == "best"), {})
    estimate_total = float(estimate.total_amount or best_option.get("total", 0) or 0)

    await sender.send_estimate(
        to=to_email,
        company_name=company_name,
        report_url=report_url,
        report_short_id=estimate.report_short_id,
        customer_name=customer_name,
        estimate_total=estimate_total,
    )

    # ── Create 3 follow-up records ────────────────────────────────────────────
    now = datetime.now(timezone.utc)
    follow_up_schedule = [
        ("24h_reminder",  now + timedelta(hours=24)),
        ("48h_reminder",  now + timedelta(hours=48)),
        ("7d_last_chance", now + timedelta(days=7)),
    ]
    for template, scheduled_at in follow_up_schedule:
        fu = FollowUp(
            estimate_id=estimate.id,
            type="email",
            scheduled_at=scheduled_at,
            template=template,
            cancelled=False,
        )
        db.add(fu)

    # ── Update estimate status ────────────────────────────────────────────────
    estimate.status = "sent"
    estimate.sent_at = now
    estimate.sent_via = "email"

    await db.commit()

    return {
        "success": True,
        "sent_to": to_email,
        "report_url": report_url,
        "report_short_id": estimate.report_short_id,
        "follow_ups_created": 3,
        "follow_up_schedule": [
            {"template": t, "scheduled_at": s.isoformat()}
            for t, s in follow_up_schedule
        ],
        "status": "sent",
    }


# ── GET /api/estimates/process-followups (WP-09 cron) ────────────────────────

@router.get("/process-followups")
async def process_followups(
    db: AsyncSession = Depends(get_db),
):
    """
    WP-09: Cron endpoint — processes due follow-up emails.
    Call this endpoint on a schedule (e.g., every hour via cron or a task queue).

    - Finds follow-ups where scheduled_at <= now AND sent_at IS NULL AND cancelled = False
    - Cancels follow-ups for already-approved estimates
    - Sends remaining due follow-ups
    """
    from services.email import get_email_sender
    from sqlalchemy import and_

    now = datetime.now(timezone.utc)
    sender = get_email_sender()
    sent_count = 0
    cancelled_count = 0
    errors = []

    # Find all due follow-ups (not yet sent, not cancelled, scheduled in the past)
    due_result = await db.execute(
        select(FollowUp).where(
            and_(
                FollowUp.scheduled_at <= now,
                FollowUp.sent_at.is_(None),
                FollowUp.cancelled == False,
            )
        )
    )
    due_followups = due_result.scalars().all()

    for fu in due_followups:
        # Load estimate
        est_result = await db.execute(
            select(Estimate).where(Estimate.id == fu.estimate_id)
        )
        estimate = est_result.scalar_one_or_none()
        if not estimate:
            fu.cancelled = True
            cancelled_count += 1
            continue

        # Cancel if already approved
        if estimate.status in ("approved", "completed"):
            fu.cancelled = True
            cancelled_count += 1
            continue

        # Load property for recipient info
        assessment = None
        property_record = None
        if estimate.assessment_id:
            assess_result = await db.execute(
                select(Assessment).where(Assessment.id == estimate.assessment_id)
            )
            assessment = assess_result.scalar_one_or_none()
        if assessment and assessment.property_id:
            prop_result = await db.execute(
                select(Property).where(Property.id == assessment.property_id)
            )
            property_record = prop_result.scalar_one_or_none()

        # Load company
        company_result = await db.execute(
            select(Company).where(Company.id == estimate.company_id)
        )
        company = company_result.scalar_one_or_none()
        company_name = company.name if company else "SnapAI HVAC"

        to_email = (
            (property_record.customer_email if property_record else None)
            or "homeowner@example.com"
        )
        customer_name = (
            (property_record.customer_name if property_record else None)
            or "Valued Customer"
        )

        base_url = get_settings().frontend_url
        if estimate.homeowner_report_url:
            report_url = (
                estimate.homeowner_report_url
                if estimate.homeowner_report_url.startswith("http")
                else f"{base_url}{estimate.homeowner_report_url}"
            )
        else:
            slug = company.slug if company else "hvac"
            report_url = f"{base_url}/r/{slug}/{estimate.report_short_id}"

        try:
            await sender.send_follow_up(
                to=to_email,
                company_name=company_name,
                report_url=report_url,
                template=fu.template,
                customer_name=customer_name,
            )
            fu.sent_at = now
            sent_count += 1
        except Exception as e:
            errors.append({"follow_up_id": str(fu.id), "error": str(e)})

    await db.commit()

    return {
        "processed_at": now.isoformat(),
        "due_found": len(due_followups),
        "sent": sent_count,
        "cancelled": cancelled_count,
        "errors": errors,
    }


# ── GET /api/estimates/export/csv ─────────────────────────────────────────────
# SOW Task 1.11: Data export for privacy compliance.
# Returns all estimates for the authenticated company as a CSV download.

import csv
import io
from fastapi.responses import StreamingResponse


@router.get("/export/csv")
async def export_estimates_csv(
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Export all estimates for the current company as a downloadable CSV.
    Includes: report_short_id, status, customer_name, address, total, created_at, approved_at.
    SOW Task 1.11: Required for GDPR/privacy compliance during beta.
    """
    result = await db.execute(
        select(Estimate, Property)
        .outerjoin(Property, Estimate.property_id == Property.id)
        .where(Estimate.company_id == auth.company_id)
        .order_by(Estimate.created_at.desc())
    )
    rows = result.all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow([
        "Report ID",
        "Status",
        "Customer Name",
        "Address",
        "City",
        "State",
        "Total ($)",
        "Selected Tier",
        "Created",
        "Approved",
    ])

    for estimate, prop in rows:
        total = estimate.options[0]["total"] if estimate.options else ""
        selected = estimate.selected_option or ""

        # Get total from selected option if available
        if estimate.options and estimate.selected_option:
            for opt in estimate.options:
                if opt.get("tier") == estimate.selected_option:
                    total = opt.get("total", "")
                    break

        writer.writerow([
            estimate.report_short_id or "",
            estimate.status or "",
            (prop.customer_name or "") if prop else "",
            (prop.address_line1 or "") if prop else "",
            (prop.city or "") if prop else "",
            (prop.state or "") if prop else "",
            total,
            selected,
            estimate.created_at.strftime("%Y-%m-%d %H:%M") if estimate.created_at else "",
            estimate.approved_at.strftime("%Y-%m-%d %H:%M") if estimate.approved_at else "",
        ])

    output.seek(0)
    filename = f"scopesnap_export_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
