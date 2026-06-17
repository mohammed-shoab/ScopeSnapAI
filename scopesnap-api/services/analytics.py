"""
SnapAI — Backend analytics (PostHog) helper.

Stage 6: install_year change-log tracking + `age_corrected` event.

This module is intentionally dependency-light and *best-effort*:
  - If POSTHOG_API_KEY is unset (or the posthog SDK is not installed) every
    call becomes a silent no-op.
  - capture() NEVER raises. All errors are swallowed so that analytics can
    never break a request path (e.g. the PATCH /api/assessments/{id} handler).

Both the tech-correction path (backend) and the homeowner-correction path
(frontend Stage 3B, served by a later endpoint) fire the SAME `age_corrected`
event via fire_age_corrected(), differing only in corrected_by.
"""

from __future__ import annotations

import os
from typing import Any, Optional


# -- PostHog client (lazy, optional) -----------------------------------------
_posthog_client = None
_posthog_init_attempted = False


def _get_client():
    """Lazily build a PostHog client. Returns None when unavailable.

    No-ops (returns None) when POSTHOG_API_KEY is unset or the SDK is missing.
    Never raises.
    """
    global _posthog_client, _posthog_init_attempted
    if _posthog_init_attempted:
        return _posthog_client

    _posthog_init_attempted = True
    api_key = os.environ.get("POSTHOG_API_KEY")
    if not api_key:
        return None
    try:
        from posthog import Posthog  # type: ignore

        host = os.environ.get("POSTHOG_HOST", "https://us.i.posthog.com")
        _posthog_client = Posthog(project_api_key=api_key, host=host)
    except Exception:
        # SDK not installed or failed to init -- stay a no-op.
        _posthog_client = None
    return _posthog_client


def capture(
    event: str,
    properties: Optional[dict] = None,
    distinct_id: Optional[str] = None,
) -> bool:
    """Best-effort PostHog event capture.

    Returns True if an event was actually sent, False if it no-op'd.
    NEVER raises -- all errors are swallowed.
    """
    try:
        client = _get_client()
        if client is None:
            return False
        props = dict(properties or {})
        # Tag every backend event with its environment (production/staging) so
        # one PostHog project cleanly separates the two (free-tier pattern).
        props.setdefault("environment", os.environ.get("ENVIRONMENT", "development"))
        client.capture(
            distinct_id=distinct_id or "backend",
            event=event,
            properties=props,
        )
        return True
    except Exception:
        # Best-effort: analytics must never break the caller.
        return False


def capture_event(
    event: str,
    properties: Optional[dict] = None,
    distinct_id: Optional[str] = None,
) -> bool:
    """Alias for capture() — kept for Stage 4 shadow-eval call sites."""
    return capture(event, properties=properties,
                   distinct_id=distinct_id or "snapai-backend")


def is_enabled() -> bool:
    """True only when a PostHog key is configured."""
    return bool(os.environ.get("POSTHOG_API_KEY", "").strip())


# -- age_corrected event -----------------------------------------------------
def fire_age_corrected(
    *,
    assessment_id: str,
    original_year: Optional[int],
    corrected_year: Optional[int],
    original_confidence: Any = None,
    original_source: Optional[str] = None,
    corrected_by: str,
    distinct_id: Optional[str] = None,
) -> bool:
    """Fire the `age_corrected` PostHog event (best-effort).

    Shared by both correction paths:
      - tech path      -> corrected_by="tech"      (PATCH /api/assessments/{id})
      - homeowner path -> corrected_by="homeowner" (frontend Stage 3B endpoint)

    correction_delta_years is computed here so both callers agree on the rule.
    Returns True if an event was sent, False otherwise. NEVER raises.
    """
    try:
        delta = correction_delta_years(original_year, corrected_year)
        properties = {
            "assessment_id": assessment_id,
            "original_year": original_year,
            "corrected_year": corrected_year,
            "original_confidence": original_confidence,
            "original_source": original_source,
            "corrected_by": corrected_by,
            "correction_delta_years": delta,
        }
        return capture(
            "age_corrected",
            properties=properties,
            distinct_id=distinct_id or assessment_id,
        )
    except Exception:
        return False


def correction_delta_years(
    original_year: Optional[int], corrected_year: Optional[int]
) -> Optional[int]:
    """Signed correction delta (corrected - original). None if either missing."""
    if original_year is None or corrected_year is None:
        return None
    try:
        return int(corrected_year) - int(original_year)
    except (TypeError, ValueError):
        return None


# -- "% confident-wrong" classification rule ---------------------------------
def classify_confident_wrong(
    original_confidence: Any, correction_delta_years: Optional[int]
) -> bool:
    """Was this a *confident-but-wrong* age call?

    Returns True when the AI was confident (confidence "high" or "medium")
    AND the human correction moved the install year by more than 3 years
    in either direction (abs(delta) > 3).

    This documents + unit-tests the Bezos "% confident-wrong" metric rule.
    The actual daily-rate aggregation runs in PostHog.
    """
    if correction_delta_years is None:
        return False

    conf = original_confidence
    if isinstance(conf, str):
        conf = conf.strip().lower()
    confident = conf in ("high", "medium")

    try:
        return confident and abs(int(correction_delta_years)) > 3
    except (TypeError, ValueError):
        return False
