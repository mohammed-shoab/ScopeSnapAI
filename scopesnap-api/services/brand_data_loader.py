"""
SnapAI -- Brand Data Loader (Master Plan v2.0, Stage 1)

Loads the v1.2 brand research data (serial-decoder formats + replace-decision
records) once at import time and exposes it to the decoder + estimate services.

Data source resolution order:
  1. env BRAND_DATA_DIR (staging/prod can override)
  2. <repo>/scopesnap-api/data/ (committed default)

Refs: SnapAI_Brand_Decoder_Implementation_Master_Plan_v2.md Section 3, Stage 1.
"""
from __future__ import annotations

import json
import logging
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

BRAND_DATA_VERSION = "1.2"

_SERIAL_FILE = "serial_decoder_data_v1.2.json"
_REPLACE_FILE = "replace_decision_data_v1.2.json"


def _data_dir() -> Path:
    override = os.environ.get("BRAND_DATA_DIR")
    if override:
        return Path(override)
    # default: <this file>/../data
    return Path(__file__).resolve().parent.parent / "data"


def _load_json(name: str) -> Dict[str, Any]:
    path = _data_dir() / name
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


@lru_cache(maxsize=1)
def _serial_data() -> Dict[str, Any]:
    return _load_json(_SERIAL_FILE)


@lru_cache(maxsize=1)
def _replace_data() -> Dict[str, Any]:
    return _load_json(_REPLACE_FILE)


@lru_cache(maxsize=1)
def _serial_brand_index() -> Dict[str, Dict[str, Any]]:
    """Lower-cased brand-name -> brand record. Keys on canonical_name AND every
    oem_sibling, so e.g. 'bryant'/'payne' resolve to the Carrier record."""
    idx: Dict[str, Dict[str, Any]] = {}
    for rec in _serial_data().get("brands", []):
        canon = (rec.get("canonical_name") or "").strip().lower()
        if canon:
            idx.setdefault(canon, rec)
        for sib in (rec.get("oem_siblings") or []):
            s = (sib or "").strip().lower()
            if s:
                idx.setdefault(s, rec)
    return idx


def get_serial_brand(brand: str) -> Optional[Dict[str, Any]]:
    if not brand:
        return None
    return _serial_brand_index().get(brand.strip().lower())


def _count_tier1_sources(rec: Dict[str, Any]) -> int:
    """Number of Tier-1 ('(T1)') sources cited in a replace record's source_links.

    Records mark each source with a tier suffix, e.g.
    'building-center.org (T2)'. Tier-1 ('(T1)') are the strongest primary
    sources (AHRI / ASHRAE / Energy Star / manufacturer bulletins).
    """
    n = 0
    for s in (rec.get("source_links") or []):
        if re.search(r"\(T1\)", str(s), re.IGNORECASE):
            n += 1
    return n


@lru_cache(maxsize=1)
def _recomputed_replace_records() -> list:
    """Constraint #2 -- load-time confidence recompute.

    For any record where cr_substituted is True AND confidence == "medium" AND
    it cites < 1 Tier-1 source, demote confidence to "low" (CR-substituted
    Tier-3 data without a primary source does not warrant "medium" confidence).

    Operates on a deep-ish copy (per-record shallow dict copies) so the raw
    cached JSON is left untouched. Logs a count of demotions once.
    """
    records = _replace_data().get("brand_tier_records", [])
    out = []
    demotions = 0
    for rec in records:
        if (
            rec.get("cr_substituted") is True
            and rec.get("confidence") == "medium"
            and _count_tier1_sources(rec) < 1
        ):
            rec = dict(rec)
            rec["confidence"] = "low"
            rec["confidence_demoted"] = True
            demotions += 1
        out.append(rec)
    logger.info(
        "BrandDataLoader: confidence recompute demoted %d cr_substituted+medium "
        "records (<1 Tier-1 source) to low", demotions,
    )
    return out


def get_replace_records() -> list:
    """Replace-decision records with the load-time confidence recompute applied."""
    return _recomputed_replace_records()


def get_raw_replace_records() -> list:
    """Replace-decision records exactly as stored in the JSON (no recompute)."""
    return _replace_data().get("brand_tier_records", [])


def get_serial_brands() -> list:
    """All brand records from the v1.2 serial-decoder data file."""
    return _serial_data().get("brands", [])


def get_serial_spec() -> Dict[str, Any]:
    return _serial_data().get("decoder_implementation_spec", {})


def get_replace_logic_spec() -> Dict[str, Any]:
    return _replace_data().get("replace_decision_logic_spec", {})


def load_all() -> Dict[str, Any]:
    """Load + log a startup summary. Call once at app startup."""
    s = _serial_data()
    r = _replace_data()
    brands = s.get("brands", [])
    records = r.get("brand_tier_records", [])
    cr_sub = sum(1 for rec in records if rec.get("cr_substituted"))
    field_cap = sum(1 for rec in brands if rec.get("serial_capture_required_from_field"))
    summary = {
        "brand_data_version": BRAND_DATA_VERSION,
        "serial_brands": len(brands),
        "replace_records": len(records),
        "cr_substituted": cr_sub,
        "serial_capture_required_from_field": field_cap,
        "data_dir": str(_data_dir()),
    }
    logger.info("BrandDataLoader: %s", summary)
    return summary
