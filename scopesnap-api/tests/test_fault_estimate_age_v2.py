"""Stage 2 — backend age-handling reconciliation (pure-function tests, no DB).

Loads only the target functions out of api/fault_estimate.py so the suite runs
without a database or FastAPI app context.
"""
from __future__ import annotations

import os
import re
import sys
import types

_API_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _load_fault_estimate_funcs():
    """Exec only the leading, dependency-light portion of fault_estimate.py
    (constants + pure helpers) into a throwaway module, stopping before the
    first FastAPI route/DB code."""
    path = os.path.join(_API_DIR, "api", "fault_estimate.py")
    src = open(path, encoding="utf-8").read()
    cut = src.index("# -- Request / Response models")
    head = src[:cut]
    mod = types.ModuleType("fe_head")
    mod.__dict__["Optional"] = __import__("typing").Optional
    mod.__dict__["math"] = __import__("math")
    mod.__dict__["datetime"] = __import__("datetime").datetime
    mod.__dict__["timezone"] = __import__("datetime").timezone
    mod.__dict__["logging"] = __import__("logging")
    mod.__dict__["re"] = __import__("re")
    # Strip any leftover top-level imports in head to keep exec self-contained.
    head = "\n".join(
        ln for ln in head.splitlines()
        if not re.match(r"\s*(from|import)\s", ln)
        and not re.match(r"router\s*=", ln)
        and not ln.startswith("@router")
    )
    exec(compile(head, path, "exec"), mod.__dict__)
    return mod


fe = _load_fault_estimate_funcs()


# ── DEFAULT_UNKNOWN_AGE + no silent default ──────────────────────────────────
def test_default_unknown_age_is_none():
    assert fe.DEFAULT_UNKNOWN_AGE is None


def test_age_bucket_unknown_for_none():
    assert fe._get_age_bucket(None) == "unknown"


def test_age_bucket_boundaries_reconciled_to_15():
    assert fe._get_age_bucket(7) == "young"
    assert fe._get_age_bucket(8) == "mid_life"
    assert fe._get_age_bucket(14) == "mid_life"
    assert fe._get_age_bucket(15) == "end_of_life"   # trigger age 15, not 8
    assert fe._get_age_bucket(20) == "end_of_life"


def test_replacement_trigger_age_is_15_not_8():
    assert fe._REPLACEMENT_TRIGGER_AGE == 15


def test_unknown_age_never_recommends_replacement():
    # major fault, but unknown age -> must NOT be tier C
    tier, reason, bucket, sev = fe._compute_recommended_tier(
        None, "hard", 2000, 1800, 5000)
    assert bucket == "unknown"
    assert tier in ("A", "B")
    assert tier != "C"


def test_labels_unknown_age_uses_neutral_set():
    labels = fe._get_labels(None)
    assert labels is fe._UNKNOWN_AGE_LABELS
    # neutral wording: must not scream "Replace Immediately"
    assert "Replace" not in labels["best"]


# ── _has_reliable_age: the 6 source classifications ──────────────────────────
def test_reliable_age_none_age():
    assert fe._has_reliable_age("serial_decode_high", "high", None) is False


def test_reliable_age_serial_high_medium_true_low_false():
    assert fe._has_reliable_age("serial_decode_high", "high", 12) is True
    assert fe._has_reliable_age("serial_decoder", "medium", 12) is True
    assert fe._has_reliable_age("serial_decode_low", "low", 12) is False


def test_reliable_age_plate_date_true():
    assert fe._has_reliable_age("plate_date", None, 12) is True


def test_reliable_age_homeowner_approximate_true_unknown_false():
    assert fe._has_reliable_age("homeowner_approximate", "approximate", 12) is True
    assert fe._has_reliable_age("homeowner_sure", "sure", 12) is True
    assert fe._has_reliable_age("homeowner_input", "unknown", 12) is False


def test_reliable_age_legacy_floor_true():
    assert fe._has_reliable_age("legacy_brand_age_floor", "low", 30) is True


def test_reliable_age_explicit_unknown_false():
    assert fe._has_reliable_age("unknown", "unknown", 12) is False
    assert fe._has_reliable_age(None, None, 12) is False


# ── replace_recommendation_gate ──────────────────────────────────────────────
def test_replace_gate_fires_unreliable_replacement():
    assert fe.replace_recommendation_gate(True, False) is True


def test_replace_gate_silent_when_reliable():
    assert fe.replace_recommendation_gate(True, True) is False


def test_replace_gate_silent_when_not_replacement():
    assert fe.replace_recommendation_gate(False, False) is False
