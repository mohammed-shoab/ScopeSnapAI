"""Unit tests for finalize_replacement_copy (Brand Decoder finding #1).

The [N] age placeholder is seeded in fault_cards.better_option_estimate
(migrations 021/024). This helper resolves it at serve time:
  - reliable age  -> substitute the real number
  - unreliable    -> strip the "At [N] years old, " lead-in (never fabricate)
"""
import pytest

from api.fault_estimate import finalize_replacement_copy

US = ("At [N] years old, complete system replacement eliminates near-term "
      "repair risk and reduces electricity costs by 30-40%.")
PK = ("At [N] years old, complete system replacement shifts to R-32 or "
      "R-410A, provides new warranty, and saves 30-40% on electricity.")


def test_reliable_age_substitutes_number():
    out = finalize_replacement_copy(US, 15, True)
    assert out.startswith("At 15 years old, complete system replacement")
    assert "[N]" not in out


def test_pk_reliable_age_substitutes_number():
    out = finalize_replacement_copy(PK, 11, True)
    assert out.startswith("At 11 years old,")
    assert "[N]" not in out and "R-32" in out


def test_unreliable_strips_leadin_and_capitalises():
    out = finalize_replacement_copy(US, None, False)
    assert out.startswith("Complete system replacement")
    assert "[N]" not in out and "years old" not in out.split(",")[0]


def test_unreliable_with_age_present_still_strips():
    # reliable_age False overrides a present unit_age — never fabricate.
    out = finalize_replacement_copy(US, 12, False)
    assert out.startswith("Complete system replacement")
    assert "[N]" not in out


def test_passthrough_when_no_token():
    plain = "Replace the failed capacitor and verify cooling."
    assert finalize_replacement_copy(plain, 12, True) == plain


def test_none_and_empty_passthrough():
    assert finalize_replacement_copy(None, 12, True) is None
    assert finalize_replacement_copy("", 12, True) == ""


def test_reliable_but_age_none_does_not_print_none():
    # Guard: reliable flag True but age missing -> strip, never "At None years".
    out = finalize_replacement_copy(US, None, True)
    assert "None" not in out and "[N]" not in out


@pytest.mark.parametrize("raw", [US, PK])
def test_no_stray_token_remains_either_branch(raw):
    assert "[N]" not in (finalize_replacement_copy(raw, 9, True) or "")
    assert "[N]" not in (finalize_replacement_copy(raw, None, False) or "")
