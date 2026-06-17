"""
Stage 6 — install_year change-log + age_corrected event (pure-helper tests).

No DB / no FastAPI app: we test the factored-out pure helpers only.

services/analytics.py imports cleanly (only stdlib), so it's imported directly.
api/assessments.py pulls in FastAPI/SQLAlchemy, so we exec-extract just the
pure `build_install_year_change_entry` helper out of it (same pattern used by
tests/test_fault_estimate_age_v2.py).
"""

import os
import re
import types

from services.analytics import (
    capture,
    fire_age_corrected,
    correction_delta_years,
    classify_confident_wrong,
)

_API_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _load_build_install_year_change_entry():
    """Exec-extract just the pure builder out of api/assessments.py without
    importing FastAPI / SQLAlchemy."""
    path = os.path.join(_API_DIR, "api", "assessments.py")
    src = open(path, encoding="utf-8").read()
    start = src.index("def build_install_year_change_entry(")
    end = src.index("\nclass AssessmentResponse(BaseModel):", start)
    snippet = src[start:end]
    mod = types.ModuleType("assess_helper")
    exec(compile(snippet, path, "exec"), mod.__dict__)
    return mod.build_install_year_change_entry


build_install_year_change_entry = _load_build_install_year_change_entry()


# ── build_install_year_change_entry ──────────────────────────────────────────
def test_build_install_year_change_entry_shape():
    entry = build_install_year_change_entry(
        ai_install_year=2008,
        new_install_year=2015,
        ai_install_year_source="serial_decoder",
        tech_id="tech_123",
        timestamp="2026-06-16T00:00:00+00:00",
    )
    assert entry == {
        "field": "install_year",
        "from": 2008,
        "to": 2015,
        "from_source": "serial_decoder",
        "to_source": "tech_override",
        "tech_id": "tech_123",
        "timestamp": "2026-06-16T00:00:00+00:00",
    }


def test_build_install_year_change_entry_defaults_source():
    entry = build_install_year_change_entry(
        ai_install_year=None,
        new_install_year=2020,
        ai_install_year_source=None,
        tech_id="tech_x",
        timestamp="2026-06-16T00:00:00+00:00",
    )
    assert entry["from"] is None
    assert entry["to"] == 2020
    assert entry["from_source"] == "ai_decoder"
    assert entry["to_source"] == "tech_override"


# ── classify_confident_wrong ─────────────────────────────────────────────────
def test_classify_confident_wrong_rule():
    assert classify_confident_wrong("high", 4) is True
    assert classify_confident_wrong("medium", 5) is True
    assert classify_confident_wrong("low", 10) is False
    assert classify_confident_wrong("high", 2) is False


def test_classify_confident_wrong_edges():
    assert classify_confident_wrong("high", 3) is False    # strictly > 3
    assert classify_confident_wrong("high", -4) is True    # negative delta counts
    assert classify_confident_wrong("HIGH", 4) is True     # case-insensitive
    assert classify_confident_wrong("high", None) is False
    assert classify_confident_wrong(None, 9) is False


def test_correction_delta_years():
    assert correction_delta_years(2008, 2015) == 7
    assert correction_delta_years(2020, 2010) == -10
    assert correction_delta_years(None, 2015) is None
    assert correction_delta_years(2008, None) is None


# ── best-effort no-op (POSTHOG_API_KEY unset) ────────────────────────────────
def _reset_analytics_memo():
    import services.analytics as analytics
    analytics._posthog_init_attempted = False
    analytics._posthog_client = None


def test_capture_noops_without_key(monkeypatch):
    monkeypatch.delenv("POSTHOG_API_KEY", raising=False)
    _reset_analytics_memo()
    assert capture("age_corrected", {"x": 1}, distinct_id="d") is False


def test_fire_age_corrected_noops_without_key(monkeypatch):
    monkeypatch.delenv("POSTHOG_API_KEY", raising=False)
    _reset_analytics_memo()
    result = fire_age_corrected(
        assessment_id="a1",
        original_year=2008,
        corrected_year=2015,
        original_confidence="high",
        original_source="serial_decoder",
        corrected_by="tech",
    )
    assert result is False


def test_fire_age_corrected_handles_bad_input(monkeypatch):
    monkeypatch.delenv("POSTHOG_API_KEY", raising=False)
    _reset_analytics_memo()
    assert fire_age_corrected(
        assessment_id="a1",
        original_year=None,
        corrected_year=None,
        corrected_by="homeowner",
    ) is False
