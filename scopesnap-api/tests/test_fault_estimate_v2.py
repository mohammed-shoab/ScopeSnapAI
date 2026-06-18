"""Tests for Level 2 per-tier line items + replacement breakdown (Bug 1 + Bug 5).

Covers _build_line_items:
  * replacement tier -> 4 distinct components summing exactly to tier.total
  * repair tier A -> single Option 1 line priced at tier.total
  * repair tier B -> single Option 2 line priced at tier.total
  * no markup-arithmetic leak (line item(s) always sum to the displayed total)
  * Level 2 data files load with the expected shape
"""
from types import SimpleNamespace

import pytest

from api.fault_estimate import (
    _build_line_items,
    _REPAIR_LINE_ITEMS,
    _UNIVERSAL_STRINGS,
    REPLACEMENT_BREAKDOWN_RATIOS,
)


def _tier(tier_letter, total, is_replacement=False):
    return SimpleNamespace(tier=tier_letter, total=total, is_replacement=is_replacement)


def _fc(card_id=8, card_name="Refrigerant Leak"):
    return SimpleNamespace(card_id=card_id, card_name=card_name)


def test_data_files_loaded():
    assert len(_REPAIR_LINE_ITEMS) == 19
    assert set(_UNIVERSAL_STRINGS["replacement_components"].keys()) == {
        "equipment", "refrigerant", "installation", "service"
    }
    assert abs(sum(REPLACEMENT_BREAKDOWN_RATIOS.values()) - 1.0) < 1e-9


def test_replacement_tier_four_items_sum_to_total():
    tier = _tier("C", 8400.0, is_replacement=True)
    items = _build_line_items(tier, _fc(), card_id=8)
    assert len(items) == 4
    # distinct descriptions, all from the universal component strings
    descs = [i["description"] for i in items]
    assert len(set(descs)) == 4
    assert all(i["category"] == "replacement" for i in items)
    # exact sum to the displayed total (no rounding leak)
    assert round(sum(i["amount"] for i in items), 2) == 8400.0


def test_repair_tier_a_uses_option_1_at_total():
    tier = _tier("A", 575.0, is_replacement=False)
    items = _build_line_items(tier, _fc(card_id=8), card_id=8)
    assert len(items) == 1
    assert items[0]["amount"] == 575.0
    assert items[0]["category"] == "repair"
    assert items[0]["description"] == _REPAIR_LINE_ITEMS[8]["option_1"]


def test_repair_tier_b_uses_option_2_at_total():
    tier = _tier("B", 760.0, is_replacement=False)
    items = _build_line_items(tier, _fc(card_id=8), card_id=8)
    assert len(items) == 1
    assert items[0]["amount"] == 760.0
    assert items[0]["description"] == _REPAIR_LINE_ITEMS[8]["option_2"]


def test_no_markup_leak_single_line_equals_total():
    # Bug 1: a repair line item must never be lower than the tier total.
    tier = _tier("A", 245.0, is_replacement=False)
    items = _build_line_items(tier, _fc(card_id=1), card_id=1)
    assert sum(i["amount"] for i in items) == tier.total


def test_unknown_card_falls_back_to_card_name():
    tier = _tier("A", 100.0, is_replacement=False)
    items = _build_line_items(tier, _fc(card_id=999, card_name="Mystery Fault"), card_id=999)
    assert items[0]["description"] == "Mystery Fault"


@pytest.mark.parametrize("card_id", range(1, 20))
def test_every_card_has_both_options_banned_word_free(card_id):
    card = _REPAIR_LINE_ITEMS[card_id]
    blob = (card["option_1"] + " " + card["option_2"]).lower()
    for banned in ("guarantee", "ensure", "eliminat", "risk-free", "never fails", "lasts forever"):
        assert banned not in blob
    # 'prevent' is banned EXCEPT the allowed 'preventive maintenance' framing
    assert "prevent" not in blob.replace("preventive maintenance", "")
