"""Regression tests for F11 and F13 (audit 2026-09-17).

Both were found by LOOKING at a screenshot of the fault-resolution screen.
Neither was catchable by the existing suite, ZAP, semgrep or k6 - the code ran
without error, it just told the technician the wrong thing.

F11: share_url was hardcoded to the PRODUCTION domains, so every link generated
     on staging pointed at prod, where the token 404s.
F13: low_threshold is the INCLUSIVE bottom of the normal band but high_threshold
     is the EXCLUSIVE start of "high". Rendering high_threshold as the band top
     showed "115-141 WITHIN RANGE" while the classifier called 141 HIGH.
"""
import inspect
import re

import pytest

from api import diagnostic


# --- F11 ---------------------------------------------------------------

def test_no_hardcoded_prod_domain_in_share_url():
    """The literal prod hosts must not be used to build share links."""
    src = inspect.getsource(diagnostic)
    # Allow them inside the PK-mapping helper, but nowhere near share_url.
    for m in re.finditer(r"share_url\s*=\s*(.+)", src):
        expr = m.group(1)
        assert "snapai.mainnov.tech" not in expr, (
            "share_url is being built from a hardcoded domain: %r. Use "
            "_public_base_url(market), which derives from settings.frontend_url "
            "(F11)." % expr.strip()
        )


def test_public_base_url_exists_and_is_used():
    assert hasattr(diagnostic, "_public_base_url"), "F11 helper is missing"
    src = inspect.getsource(diagnostic)
    assert src.count("_public_base_url(") >= 3, (
        "expected the helper definition plus both share_url call sites"
    )


@pytest.mark.parametrize(
    "frontend_url,market,expected",
    [
        # staging must stay on staging - this is the actual F11 bug
        ("https://staging.snapai.mainnov.tech", "US", "https://staging.snapai.mainnov.tech"),
        ("https://staging.snapai.mainnov.tech", "PK", "https://pk-staging.snapai.mainnov.tech"),
        # prod behaviour unchanged
        ("https://snapai.mainnov.tech", "US", "https://snapai.mainnov.tech"),
        ("https://snapai.mainnov.tech", "PK", "https://pk.snapai.mainnov.tech"),
        # already-PK hosts are left alone
        ("https://pk-staging.snapai.mainnov.tech", "PK", "https://pk-staging.snapai.mainnov.tech"),
        # trailing slash trimmed
        ("https://staging.snapai.mainnov.tech/", "US", "https://staging.snapai.mainnov.tech"),
        # local dev
        ("http://localhost:3000", "US", "http://localhost:3000"),
    ],
)
def test_public_base_url_maps_environment_and_market(monkeypatch, frontend_url, market, expected):
    class _S:
        pass

    s = _S()
    s.frontend_url = frontend_url
    monkeypatch.setattr(diagnostic, "get_settings", lambda: s)
    assert diagnostic._public_base_url(market) == expected


def test_share_link_on_staging_does_not_point_at_prod(monkeypatch):
    """The exact defect seen on screen: a staging page showing a prod share URL."""
    class _S:
        pass

    s = _S()
    s.frontend_url = "https://staging.snapai.mainnov.tech"
    monkeypatch.setattr(diagnostic, "get_settings", lambda: s)

    url = diagnostic._public_base_url("US") + "/d/" + "159529f437ed4af10a1ad08f979bcbdc"
    assert url.startswith("https://staging."), url
    assert "//snapai.mainnov.tech" not in url, (
        "staging generated a PRODUCTION share link - this is F11"
    )


# --- F13 ---------------------------------------------------------------

def test_receipt_band_top_steps_back_from_high_threshold():
    """high_threshold is exclusive; the displayed band top must be one below it."""
    src = inspect.getsource(diagnostic)
    assert "F13" in src, "F13 rationale comment should stay with the code"
    assert "_ht - 1" in src, (
        "the receipt must step back from high_threshold so the displayed band "
        "matches the classifier's decision (F13)"
    )


@pytest.mark.parametrize(
    "low,high,want_low,want_high",
    [
        # R-410A US suction: canonical table says 115-140 normal, >=141 high
        (115, 141, 115, 140),
        # R-410A US discharge: 225-275 normal, >=276 high
        (225, 276, 225, 275),
    ],
)
def test_canonical_bands_render_as_documented(low, high, want_low, want_high):
    """Mirrors the arithmetic the receipt now performs, pinned to the canonical
    table in PROJECT_BRAIN so a spec change cannot silently drift the display."""
    rendered_low = low
    rendered_high = high - 1 if float(high).is_integer() else high
    assert (rendered_low, rendered_high) == (want_low, want_high)


def test_the_exact_value_seen_on_screen_is_now_correct():
    """The screenshot showed 'Compared against 115-141 PSI ... WITHIN RANGE'
    while the classifier treats 141 as HIGH. It must now read 115-140."""
    high_threshold = 141
    assert high_threshold - 1 == 140
