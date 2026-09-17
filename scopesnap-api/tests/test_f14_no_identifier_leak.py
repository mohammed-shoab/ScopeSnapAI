"""Regression tests for F14 (audit 2026-09-17).

Found in Chrome on a real Refrigerant Leak diagnosis. The reading receipt showed
the technician this:

    Compared against   reference targets
                       (superheat_subcool_targets.target_superheat_min_f,
                        target_superheat_max_f)
    WHY THIS CARD      SH above target_superheat_max_f AND SC below
                       target_subcool_min_f

Database schema on screen, and the actual target numbers never shown. Nothing
automated caught it: the page rendered without error.

Policy under test: fail CLOSED. If a string still looks like an identifier after
translation, drop it rather than render it. A missing line beats leaking
internals to someone quoting a customer.
"""
import pytest

from api.diagnostic import (
    _humanize_receipt_source,
    _humanize_receipt_why,
    _looks_like_identifier,
)


# --- the exact strings seen on screen ----------------------------------

SEEN_SOURCE = "superheat_subcool_targets.target_superheat_min_f,target_superheat_max_f"
SEEN_WHY = "SH above target_superheat_max_f AND SC below target_subcool_min_f"


def test_the_exact_source_seen_on_screen_is_suppressed():
    assert _humanize_receipt_source(SEEN_SOURCE) is None, (
        "the table.column pointer must never reach the UI (F14)"
    )


def test_the_exact_why_line_seen_on_screen_is_humanised():
    out = _humanize_receipt_why(SEEN_WHY)
    assert out is not None, "this one is translatable, it should not be dropped"
    assert "target_superheat_max_f" not in out
    assert "target_subcool_min_f" not in out
    assert "_" not in out, "no snake_case should survive: %r" % out
    assert "superheat" in out.lower() and "subcool" in out.lower()
    assert " AND " not in out, "rule syntax should read as prose"
    assert out[0].isupper(), "should read as a sentence: %r" % out


# --- identifier detection ----------------------------------------------

@pytest.mark.parametrize(
    "s",
    [
        "superheat_subcool_targets.target_superheat_min_f",
        "operating_targets.suction_max_psi",
        "target_superheat_max_f",
        "some_table.col_a,col_b",
        "reading_inputs.value_numeric",
    ],
)
def test_identifiers_are_detected(s):
    assert _looks_like_identifier(s) is True


@pytest.mark.parametrize(
    "s",
    [
        "manufacturer spec",
        "the target superheat maximum",
        "Superheat above the target superheat maximum",
        "ACCA Manual S",
    ],
)
def test_human_text_is_not_flagged(s):
    assert _looks_like_identifier(s) is False


# --- source sanitiser ---------------------------------------------------

@pytest.mark.parametrize(
    "raw,expected",
    [
        (SEEN_SOURCE, None),
        ("operating_targets.suction_max_psi", None),
        ("manufacturer spec", "manufacturer spec"),
        ("ACCA Manual S", "ACCA Manual S"),
        ("", None),
        (None, None),
        (123, None),
    ],
)
def test_source_sanitiser(raw, expected):
    assert _humanize_receipt_source(raw) == expected


# --- why-line sanitiser -------------------------------------------------

def test_untranslatable_rule_is_dropped_not_leaked():
    """A rule referencing columns we have no prose for must be suppressed."""
    out = _humanize_receipt_why("delta_t_target_min_f exceeded on coil_entering_wb_f")
    assert out is None, "unknown identifiers must be dropped, not rendered: %r" % out


def test_already_human_why_is_preserved():
    src = "Suction pressure well below the expected range for this ambient"
    assert _humanize_receipt_why(src) == src


@pytest.mark.parametrize("raw", ["", "   ", None, 42])
def test_why_handles_empty_and_non_strings(raw):
    assert _humanize_receipt_why(raw) is None


def test_psi_tokens_also_translate():
    out = _humanize_receipt_why("reading above suction_max_psi")
    assert out is not None
    assert "suction_max_psi" not in out
    assert "suction" in out.lower()
