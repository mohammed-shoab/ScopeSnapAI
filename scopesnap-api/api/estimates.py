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

from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from sqlalchemy.orm.attributes import flag_modified

from db.database import get_db
from db.models import Assessment, Company, Estimate, EstimateLineItem, FollowUp, Property
from api.auth import get_current_user, AuthContext
from api.dependencies import get_tables, MarketTables
from api.fault_estimate import finalize_replacement_copy
from config import get_settings

router = APIRouter(prefix="/api/estimates", tags=["estimates"])


def verify_cron_secret(x_cron_secret: str | None = Header(default=None)):
    """WP-09 cron auth for /process-followups. If CRON_SECRET is configured, a
    matching X-Cron-Secret header is required. If it is NOT configured, the call
    is allowed but a warning is logged — so the existing scheduler keeps working
    until the secret is set and the caller is updated (then it fails closed)."""
    expected = (get_settings().cron_secret or "").strip()
    if not expected:
        import logging
        logging.getLogger(__name__).warning(
            "process-followups is UNAUTHENTICATED: set CRON_SECRET to require X-Cron-Secret."
        )
        return
    if not x_cron_secret or x_cron_secret != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing cron secret",
        )


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



async def _enrich_tco_from_db(data: dict, estimate, db, tables: "MarketTables") -> dict:
    """G.4 Track G: overwrite options[].five_year_comparison with TCO table data."""
    try:
        ds_result = await db.execute(
            text(
                "SELECT resolved_card_id FROM diagnostic_sessions "
                "WHERE assessment_id = :aid AND resolved_card_id IS NOT NULL "
                "ORDER BY created_at DESC LIMIT 1"
            ),
            {"aid": str(estimate.assessment_id)},
        )
        card_id = ds_result.scalar_one_or_none()
        if card_id is None:
            return data

        if tables.market == "PK":
            tco_table = "pak_card_tco_data"
            cost_col = "avg_repair_cost_pkr_if_event"
            sav_col = "energy_savings_5yr_pkr"
        else:
            tco_table = "card_tco_data"
            cost_col = "avg_repair_cost_usd_if_event"
            sav_col = "energy_savings_5yr_usd"

        tco_rows = await db.execute(
            text(
                f"SELECT tier, prob_major_repair_5yr_pct, prob_range, "
                f"{cost_col}, {sav_col} "
                f"FROM {tco_table} WHERE card_id = :cid"
            ),
            {"cid": int(card_id)},
        )
        tco_by_tier = {
            row[0]: {
                "probability_pct": row[1],
                "probability_range": row[2],
                "expected_repair_cost": row[3],
                "energy_savings_5yr": row[4],
            }
            for row in tco_rows.fetchall()
        }

        if not tco_by_tier:
            return data

        options = data.get("options") or []
        for opt in options:
            tier = opt.get("tier")  # "A", "B", or "C"
            opt["five_year_comparison"] = tco_by_tier.get(tier)
        data["options"] = options
    except Exception:
        pass  # Never break estimates for TCO enrichment failure
    return data


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



# ── GET /api/estimates/process-followups (WP-09 cron) — MUST BE BEFORE /{id} ─

@router.get("/process-followups")
async def process_followups_early(
    db: AsyncSession = Depends(get_db),
    _cron: None = Depends(verify_cron_secret),
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

        # WS-M3: tech_confirm_24h fires AFTER approval — skip the standard cancel check
        is_tech_confirm = fu.template == "tech_confirm_24h"
        if not is_tech_confirm and estimate.status in ("approved", "completed"):
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

        # ── WS-M3: Tech confirmation email (goes to technician, not homeowner) ──
        if is_tech_confirm:
            tech_email = (company.email if company else None) or to_email
            assessment_id_str = str(estimate.assessment_id) if estimate.assessment_id else ""
            confirm_url = f"{base_url}/assess?confirm=1&assessment_id={assessment_id_str}"
            customer_addr = (property_record.address_line1 if property_record else None) or "the job site"
            tier = (estimate.selected_option or "approved").title()
            html_body = f"""
<div style="font-family:sans-serif;max-width:560px;margin:auto;padding:24px">
  <h2 style="color:#1a1a2e">Job Complete — Quick Confirm?</h2>
  <p>Hi,</p>
  <p>Your customer at <strong>{customer_addr}</strong> just approved the
     <strong>{tier}</strong> option on estimate
     <strong>{estimate.report_short_id}</strong>. Nice work!</p>
  <p>It takes <strong>30 seconds</strong> to confirm what you actually
     fixed — this data trains the AI to give better diagnoses next time.</p>
  <p style="margin:28px 0">
    <a href="{confirm_url}"
       style="background:#3498db;color:#fff;padding:14px 28px;border-radius:8px;
              text-decoration:none;font-weight:bold;display:inline-block">
      Confirm Job Outcome &rarr;
    </a>
  </p>
  <p style="color:#7a8299;font-size:13px">
    If you already filled this in, ignore this email.<br>
    &mdash; {company_name} &times; SnapAI
  </p>
</div>"""
            try:
                from services.email import EmailMessage
                await sender.send(EmailMessage(
                    to=tech_email,
                    subject=f"[SnapAI] Confirm job outcome — {estimate.report_short_id}",
                    html_body=html_body,
                    text_body=(
                        f"Job complete! Confirm what you fixed at {customer_addr}.\n"
                        f"Takes 30 seconds: {confirm_url}"
                    ),
                ))
                fu.sent_at = now
                sent_count += 1
            except Exception as e:
                errors.append({"follow_up_id": str(fu.id), "error": str(e)})
            continue  # skip the standard send_follow_up below

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
    tables: MarketTables = Depends(get_tables),
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

    # G.4 Track G: enrich with TCO probability data
    data = await _enrich_tco_from_db(data, estimate, db, tables)

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

    # Bug 3: surface the assessment's first photo + overall condition so the
    # Estimate Builder Present Mode (Slide 1) shows the real unit + a health badge.
    data["assessment_photo_url"] = None
    data["assessment_condition"] = None
    try:
        if estimate.assessment_id:
            asmt_res = await db.execute(
                select(Assessment).where(Assessment.id == estimate.assessment_id)
            )
            asmt = asmt_res.scalar_one_or_none()
            if asmt:
                photos = asmt.photo_urls or []
                data["assessment_photo_url"] = photos[0] if photos else None
                cond = asmt.ai_condition if isinstance(asmt.ai_condition, dict) else {}
                data["assessment_condition"] = cond.get("overall")
    except Exception:
        pass

    return data


# ── POST /api/estimates/{id}/refresh (Q.7) ──────────────────────────────────────

@router.post("/{estimate_id}/refresh")
async def refresh_draft_estimate(
    estimate_id: str,
    auth: AuthContext = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Q.7 — Re-stamp description/why_recommended from the latest
    fault_cards.better_option_estimate onto a draft estimate's stored options.
    Called by the Estimate Builder on load so descriptions added after estimate
    creation (e.g. migration 021) appear without requiring a new estimate.
    Idempotent: safe to call repeatedly; no-op if estimate is not 'draft'.
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

    if estimate.status != "draft":
        return _estimate_to_dict(estimate)

    # Resolve card_id via diagnostic_sessions
    ds_row = await db.execute(
        text(
            "SELECT resolved_card_id FROM diagnostic_sessions "
            "WHERE assessment_id = :aid AND resolved_card_id IS NOT NULL LIMIT 1"
        ),
        {"aid": str(estimate.assessment_id)},
    )
    card_id = ds_row.scalar_one_or_none()
    if card_id is None:
        return _estimate_to_dict(estimate)

    # Fetch better_option_estimate JSONB for this fault card
    fc_row = await db.execute(
        text("SELECT better_option_estimate FROM fault_cards WHERE card_id = :cid"),
        {"cid": int(card_id)},
    )
    better_data = fc_row.scalar_one_or_none() or {}

    # Brand Decoder finding #1: resolve the [N] age token when re-stamping the
    # replacement-tier copy. Age provenance was stashed on the recommended option
    # as recommendation_meta at generation time (fault_estimate.py), so no extra
    # query is needed.
    _rec_meta = next(
        (o.get("recommendation_meta") for o in (estimate.options or [])
         if isinstance(o, dict) and o.get("recommendation_meta")),
        {},
    ) or {}
    _unit_age = _rec_meta.get("unit_age_years")
    _reliable_age = bool(_rec_meta.get("reliable_age"))

    # Patch description/why_recommended per tier without touching amounts or line_items
    updated_options = []
    for opt in (estimate.options or []):
        opt = dict(opt)
        tier = opt.get("tier")
        if tier == "good":
            desc = better_data.get("description_good")
            why  = better_data.get("why_recommended_good")
        elif tier == "better":
            desc = better_data.get("description")
            why  = better_data.get("why_recommended")
        elif tier == "best":
            if opt.get("is_replacement"):
                desc = finalize_replacement_copy(
                    better_data.get("description_best_replacement"),
                    _unit_age, _reliable_age,
                )
                why  = better_data.get("why_recommended_best_replacement")
            else:
                desc = better_data.get("description_best_comprehensive")
                why  = better_data.get("why_recommended_best_comprehensive")
        else:
            desc = why = None
        if desc:
            opt["description"] = desc
        if why:
            opt["why_recommended"] = why
        updated_options.append(opt)

    estimate.options = updated_options
    flag_modified(estimate, "options")
    await db.commit()
    await db.refresh(estimate)
    return _estimate_to_dict(estimate)


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
        "overall_condition": (
            assessment.ai_condition.get("overall", "fair")
            if assessment and isinstance(assessment.ai_condition, dict)
            else "fair"
        ),
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
    # Q.6: use 32-char report_token for security. Legacy short_id URLs remain
    # valid for 12 months via the OR clause in reports.py (see reports.py line ~60).
    # REMOVE 2027-05-19: legacy short-ID lookup, per DEC-016.
    homeowner_url = f"/r/{company.slug if company else 'hvac'}/{estimate.report_token}"

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
    _cron: None = Depends(verify_cron_secret),
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
# SOW Task 1.11: Data export for privacy