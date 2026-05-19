"""
SnapAI — Admin Endpoints
Protected utility endpoints for production database management.
All routes require X-Admin-Secret header matching ADMIN_SECRET env var.

Usage (Railway):
  Set ADMIN_SECRET=<random-string> in Railway environment variables.
  Then call:
    curl -X POST https://scopesnap-api-production.up.railway.app/admin/seed \
         -H "X-Admin-Secret: <your-secret>"
"""

import os
from fastapi import APIRouter, Header, HTTPException
from sqlalchemy import select, func as sql_func

router = APIRouter(prefix="/admin", tags=["admin"])

ADMIN_SECRET = os.getenv("ADMIN_SECRET", "")


def _require_admin(x_admin_secret: str = Header(default="")):
    """Dependency: validates admin secret header."""
    if not ADMIN_SECRET:
        raise HTTPException(
            status_code=503,
            detail="Admin endpoints are disabled. Set ADMIN_SECRET in Railway env vars to enable."
        )
    if x_admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Invalid admin secret.")


@router.post("/seed", summary="Seed pricing rules and equipment models")
async def run_seeds(x_admin_secret: str = Header(default="")):
    """
    Runs all database seeds (pricing rules + equipment models).
    Safe to run multiple times — uses upsert/ignore-duplicates logic.
    Requires X-Admin-Secret header.
    """
    _require_admin(x_admin_secret)

    import sys
    sys.path.insert(0, "/app")

    results = {}

    # Seed pricing rules
    try:
        from db.database import AsyncSessionLocal
        from db.models import PricingRule
        from scripts.seed_pricing import seed_pricing

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(sql_func.count()).select_from(PricingRule))
            before = result.scalar_one()

        await seed_pricing()

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(sql_func.count()).select_from(PricingRule))
            after = result.scalar_one()

        results["pricing_rules"] = {
            "status": "ok",
            "before": before,
            "after": after,
            "inserted": after - before,
        }
    except Exception as e:
        results["pricing_rules"] = {"status": "error", "detail": str(e)}

    # Seed equipment models
    try:
        from db.models import EquipmentModel
        from scripts.seed_equipment_db import seed_equipment_db

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(sql_func.count()).select_from(EquipmentModel))
            before = result.scalar_one()

        await seed_equipment_db()

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(sql_func.count()).select_from(EquipmentModel))
            after = result.scalar_one()

        results["equipment_models"] = {
            "status": "ok",
            "before": before,
            "after": after,
            "inserted": after - before,
        }
    except Exception as e:
        results["equipment_models"] = {"status": "error", "detail": str(e)}

    return {
        "message": "Seed run complete",
        "results": results,
    }


@router.get("/status", summary="Check seed status (row counts)")
async def seed_status(x_admin_secret: str = Header(default="")):
    """
    Returns row counts for key seed tables.
    Useful for verifying the production DB is seeded correctly.
    """
    _require_admin(x_admin_secret)

    from db.database import AsyncSessionLocal
    from db.models import PricingRule, EquipmentModel

    counts = {}
    async with AsyncSessionLocal() as db:
        for model, name in [(PricingRule, "pricing_rules"), (EquipmentModel, "equipment_models")]:
            try:
                result = await db.execute(select(sql_func.count()).select_from(model))
                counts[name] = result.scalar_one()
            except Exception as e:
                counts[name] = f"error: {e}"

    return {"table_counts": counts}


# ── GET /admin/dashboard — operator metrics overview ─────────────────────────

@router.get("/dashboard")
async def admin_dashboard(x_admin_secret: str = Header(default="")):
    """
    Operator dashboard — key metrics across all companies and users.
    Returns: total assessments, emails sent, label edit rate, active companies.
    Protected by ADMIN_SECRET header.
    """
    _require_admin(x_admin_secret)

    from db.models import Assessment, Estimate, Company, User
    from sqlalchemy import func as sql_func, case

    async with AsyncSessionLocal() as db:
        # Total assessments
        total_assessments = (await db.execute(
            select(sql_func.count()).select_from(Assessment)
        )).scalar_one()

        # Assessments by status
        status_counts_rows = (await db.execute(
            select(Assessment.status, sql_func.count())
            .group_by(Assessment.status)
        )).all()
        assessments_by_status = {row[0]: row[1] for row in status_counts_rows}

        # Assessments with label edits (AI accuracy indicator)
        label_edited_count = (await db.execute(
            select(sql_func.count()).select_from(Assessment)
            .where(Assessment.label_edited == True)  # noqa: E712
        )).scalar_one()

        # Estimates sent (emails delivered to homeowners)
        sent_estimates = (await db.execute(
            select(sql_func.count()).select_from(Estimate)
            .where(Estimate.status.in_(["sent", "viewed", "approved", "deposit_paid"]))
        )).scalar_one()

        # Estimates with payments (deposit collected)
        paid_estimates = (await db.execute(
            select(sql_func.count()).select_from(Estimate)
            .where(Estimate.status == "deposit_paid")
        )).scalar_one()

        # Active companies (at least 1 assessment)
        active_companies = (await db.execute(
            select(sql_func.count(sql_func.distinct(Assessment.company_id)))
            .select_from(Assessment)
        )).scalar_one()

        # Total users
        total_users = (await db.execute(
            select(sql_func.count()).select_from(User)
        )).scalar_one()

        # Assessments last 7 days
        from datetime import datetime, timezone, timedelta
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_assessments = (await db.execute(
            select(sql_func.count()).select_from(Assessment)
            .where(Assessment.created_at >= seven_days_ago)
        )).scalar_one()

    label_edit_rate = round(label_edited_count / total_assessments * 100, 1) if total_assessments > 0 else 0
    email_conversion = round(sent_estimates / total_assessments * 100, 1) if total_assessments > 0 else 0
    deposit_rate = round(paid_estimates / sent_estimates * 100, 1) if sent_estimates > 0 else 0

    return {
        "summary": {
            "total_assessments": total_assessments,
            "assessments_last_7_days": recent_assessments,
            "active_companies": active_companies,
            "total_users": total_users,
        },
        "pipeline": {
            "assessments_by_status": assessments_by_status,
            "emails_sent": sent_estimates,
            "deposits_collected": paid_estimates,
            "email_conversion_pct": email_conversion,
            "deposit_rate_pct": deposit_rate,
        },
        "ai_accuracy": {
            "label_edits_total": label_edited_count,
            "label_edit_rate_pct": label_edit_rate,
            "note": "Lower edit rate = AI is more accurate. Target < 20%.",
        },
    }


# ── POST /admin/load-repo — reload ac_data_repo.json into DB ─────────────────

@router.post("/load-repo", summary="Reload ac_data_repo.json into brand/parts/fault_cards tables")
async def run_load_repo(x_admin_secret: str = Header(default="")):
    """
    Runs scripts/load_repo.py → truncates and re-seeds brands, parts_catalog,
    fault_cards, error_codes, pricing_tiers, labor_rates, legacy_model_prefixes,
    lifecycle_rules, data_defaults, replacement_cost_estimates.

    Run after any update to ac_data_repo.json.
    Requires X-Admin-Secret header.
    """
    _require_admin(x_admin_secret)

    import sys as _sys
    _sys.path.insert(0, "/app")

    try:
        from scripts.load_repo import main as load_repo_main
        await load_repo_main(dry_run=False)
        return {"message": "load_repo completed successfully"}
    except BaseException as exc:
        raise HTTPException(status_code=500, detail=f"load_repo failed: {type(exc).__name__}: {exc}")
