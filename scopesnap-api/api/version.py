"""
SnapAI -- Version endpoint (Brand Decoder Stage 5).

GET /api/version  -- PUBLIC (no auth). Returns the brand-decoder + replace-logic
data versions the running backend is serving, so the frontend / QA can confirm
which data set is live.

    {
      "decoder_version": "1.2",
      "replace_logic_version": "1.2",
      "brand_data_version": "1.2"
    }

decoder_version + brand_data_version come from brand_data_loader.BRAND_DATA_VERSION.
replace_logic_version comes from the replace_decision_logic_spec.version (falls
back to BRAND_DATA_VERSION when the spec omits a version key).
"""
from __future__ import annotations

import logging

from fastapi import APIRouter

from services.brand_data_loader import BRAND_DATA_VERSION, get_replace_logic_spec
from services.analytics import is_enabled as _analytics_enabled

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["version"])


def _resolve_replace_logic_version() -> str:
    """replace_decision_logic_spec.version, else fall back to BRAND_DATA_VERSION."""
    try:
        spec = get_replace_logic_spec() or {}
        return str(spec.get("version") or BRAND_DATA_VERSION)
    except Exception:  # pragma: no cover - loader should not fail, but stay safe
        logger.debug("version: replace-logic spec lookup failed", exc_info=True)
        return BRAND_DATA_VERSION


def get_version_payload() -> dict:
    """Pure helper (unit-testable without the HTTP layer)."""
    return {
        "decoder_version": BRAND_DATA_VERSION,
        "replace_logic_version": _resolve_replace_logic_version(),
        "brand_data_version": BRAND_DATA_VERSION,
        "analytics_enabled": bool(_analytics_enabled()),
    }


@router.get("/version", status_code=200)
async def get_version():
    """Public version stamp for the brand-decoder data set."""
    return get_version_payload()
