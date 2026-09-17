"""Regression tests for F9 (audit 2026-09-17).

Sentry SNAPAI-API-1A: GET /api/estimates/new raised

    asyncpg DataError: invalid input for query argument $1: 'new'
    (invalid UUID 'new': length must be between 32..36 characters, got 3)

because the {estimate_id} path params were typed `str` and handed straight to
`WHERE estimates.id = $1::UUID`. The result was an unhandled 500, a Sentry
event, and the full SQL in the logs - reachable by anyone typing a bad URL.

Typing the param as UUID makes FastAPI reject it at the edge with 422, before
the DB is touched at all.
"""
import inspect
import re
from uuid import UUID

import pytest

from api import estimates, payments
import main as main_module


ROUTE_FUNCS = [
    (estimates, "get_estimate"),
    (estimates, "refresh_draft_estimate"),
    (estimates, "update_estimate"),
    (estimates, "generate_documents"),
    (estimates, "send_estimate"),
    (payments, "create_checkout"),
    (payments, "get_payment_status"),
]


@pytest.mark.parametrize("mod,fname", ROUTE_FUNCS)
def test_estimate_id_path_param_is_uuid_typed(mod, fname):
    """Every {estimate_id} route must validate at the edge, not at the driver."""
    fn = getattr(mod, fname, None)
    assert fn is not None, "%s.%s not found" % (mod.__name__, fname)

    sig = inspect.signature(fn)
    assert "estimate_id" in sig.parameters, "%s has no estimate_id param" % fname

    ann = sig.parameters["estimate_id"].annotation
    assert ann is UUID, (
        "%s.%s: estimate_id is annotated %r, expected UUID. A str annotation "
        "lets a non-UUID reach Postgres and raise an unhandled DataError (500) "
        "instead of a clean 422 - this is exactly F9." % (mod.__name__, fname, ann)
    )


def test_no_estimate_id_str_annotations_remain():
    """Guard against a regression reintroducing `estimate_id: str`."""
    for mod in (estimates, payments):
        src = inspect.getsource(mod)
        bad = re.findall(r"^\s+estimate_id:\s*str\b", src, re.M)
        assert not bad, (
            "%s still has %d `estimate_id: str` annotation(s); they must be "
            "UUID (F9)." % (mod.__name__, len(bad))
        )


def test_uuid_is_imported_in_both_modules():
    for mod in (estimates, payments):
        assert "from uuid import UUID" in inspect.getsource(mod), (
            "%s must import UUID" % mod.__name__
        )


# --- defence-in-depth handler ------------------------------------------------

def test_dbapi_data_error_handler_is_registered():
    """Routes still typed str (assessment_id, session_id) must degrade to 400,
    not 500, until they are typed too."""
    src = inspect.getsource(main_module)
    assert "_dbapi_data_error_handler" in src, "F9 DBAPIError handler is missing"
    assert "DBAPIError" in src, "DBAPIError must be imported and handled"


def test_handler_only_catches_malformed_input_not_real_db_failures():
    """The handler must be narrow. A connection failure has to stay a 500 so it
    still pages us - swallowing it as a 400 would hide a real outage."""
    src = inspect.getsource(main_module._dbapi_data_error_handler)
    assert "raise exc" in src, (
        "handler must re-raise anything that is not a data/format error"
    )
    for token in ("DataError", "invalid input", "InvalidTextRepresentation"):
        assert token in src, "handler should key off %r" % token


@pytest.mark.parametrize(
    "bad_id",
    ["new", "undefined", "null", "0", "abc", "../../etc/passwd", "1 OR 1=1"],
)
def test_known_bad_path_segments_are_not_valid_uuids(bad_id):
    """Characterises the inputs that used to 500. 'new' is the one that actually
    fired in staging traffic (Sentry SNAPAI-API-1A)."""
    with pytest.raises(ValueError):
        UUID(bad_id)
