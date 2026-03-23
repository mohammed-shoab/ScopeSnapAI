"""
ScopeSnap — Admin Endpoints
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
