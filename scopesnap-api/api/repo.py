"""
WS-A — Data Repository API
===========================
GET /api/repo/version  — returns the loaded ac_data_repo version + row counts.

This endpoint is the WS-A acceptance check: it confirms the data-foundation
tables are populated and returns the version string so other workstreams can
verify they're running against the right data set.
"""

from fastapi import APIRouter
from sqlalchemy import text
from db.database import AsyncSessionLocal
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/repo", tags=["repo"])


@router.get("/version", status_code=200)
async def get_repo_version():
    """
    Return the currently-loaded ac_data_repo version and a row-count summary.

    Acceptance criterion (WS-A M1): returns {"version": "2.0"}.

    If the data_repo_versions table doesn't exist yet (migration 007 not run)
    or is empty (load_repo.py not run), returns a clear error so the caller
    knows exactly what to do next.
    """
    try:
        async with AsyncSessionLocal() as db:
            # Latest load record
            row = await db.execute(
                text("""
                    SELECT version, source_file, row_counts, loaded_at
                    FROM data_repo_versions
                    ORDER BY loaded_at DESC
                    LIMIT 1
                """)
            )
            record = row.fetchone()
            if not record:
                return {
                    "version": None,
                    "status": "not_loaded",
                    "message": (
                        "data_repo_versions table exists but is empty. "
                        "Run: python scripts/load_repo.py"
                    ),
                }

            # Live row counts from the actual tables (real-time verification)
            counts = {}
            for table in [
                "brands", "parts_catalog", "fault_cards", "error_codes",
                "pricing_tiers", "labor_rates_houston",
                "legacy_model_prefixes", "lifecycle_rules",
            ]:
                result = await db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                counts[table] = result.scalar()

            return {
                "version": record.version,
                "status": "ok",
                "source_file": record.source_file,
                "loaded_at": record.loaded_at.isoformat() if record.loaded_at else None,
                "stored_row_counts": record.row_counts,
                "live_row_counts": counts,
            }

    except Exception as e:
        err = str(e)
        if "data_repo_versions" in err and "does not exist" in err:
            return {
                "version": None,
                "status": "migration_pending",
                "message": (
                    "Migration 007 has not been run. "
                    "Run: alembic upgrade head"
                ),
            }
        logger.error(f"[repo/version] {e}")
        return {
            "version": None,
            "status": "error",
            "message": str(e),
        }
