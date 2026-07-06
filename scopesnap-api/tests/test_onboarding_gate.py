"""Contractor onboarding GATE (C3) -- real-handler tests for PATCH /api/auth/me/company.

The gate lives in ``api/clerk_webhook.py::update_company`` (route
``PATCH /api/auth/me/company``, mounted from ``me_router``). It exists so a
homeowner can't sign up with a Gmail, clear the license number, and reach the
authenticated app. The contract this suite pins:

  * A blank/whitespace-only ``license_number`` is REJECTED with HTTP **422** and
    detail ``"A valid contractor license number is required."`` -- a homeowner
    must never be able to clear it.
  * Omitting ``license_number`` entirely is a legal partial update (e.g. phone
    only): it returns 200 and leaves the existing license untouched, but does
    NOT stamp the attestation, so the company stays un-gated and the frontend
    guard keeps redirecting to /onboarding.
  * A valid ``license_number`` + ``attestation_accepted: true`` +
    ``terms_ack_version`` returns **200**, persists a non-null
    ``attestation_accepted_at`` and the given ``terms_ack_version`` -- the two
    columns the frontend guard reads to stop redirecting.

Unlike the other suites in this directory (which are deliberately DB-free
pure-function tests), the gate is an async DB-bound FastAPI handler, so this
suite spins up an in-memory SQLite engine and mounts ONLY ``me_router`` behind a
``get_db`` override. Auth uses the same dev bypass the app ships with
(``ENVIRONMENT=development`` + the ``X-Dev-Clerk-User-Id`` header), seeding the
canonical dev owner ``test_user_mike`` -- matching the dev-header convention the
codebase documents in ``api/auth.py``.

If the async/DB/FastAPI stack cannot be imported in the running environment the
whole module is skipped with a clear reason (see the import guard below), rather
than failing collection.
"""
from __future__ import annotations

import os
import sys

# -- Environment must be set BEFORE importing app modules ---------------------
# db/types.py picks JSONB-vs-JSON at import time off DATABASE_URL, and the auth
# dev-bypass only fires when ENVIRONMENT=development. Both have to be in place
# before the first `import db.models` / `import api.auth`.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ["ENVIRONMENT"] = "development"

_API_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

import pytest

# Skip the whole module (rather than erroring at collection) if the async web
# stack isn't installed in this environment.
try:
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from db.database import Base, get_db
    from db.models import Company, User
    from api.clerk_webhook import me_router
except Exception as exc:  # pragma: no cover - environment guard
    pytest.skip(
        f"onboarding-gate tests need the fastapi/sqlalchemy/aiosqlite stack: {exc!r}",
        allow_module_level=True,
    )


DEV_USER = "test_user_mike"
DEV_HEADERS = {"X-Dev-Clerk-User-Id": DEV_USER}
COMPANY_ID = "11111111-1111-1111-1111-111111111111"
USER_ID = "22222222-2222-2222-2222-222222222222"


# -- Fixtures -----------------------------------------------------------------
@pytest.fixture()
def engine():
    """A fresh in-memory SQLite engine per test (StaticPool so the single
    :memory: connection is shared across the app's sessions)."""
    from sqlalchemy.pool import StaticPool

    eng = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield eng


@pytest.fixture()
def session_factory(engine):
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture()
def seed(engine, session_factory):
    """Create the two tables under test and seed the dev OWNER + company.

    The owner starts with a valid license so the "omit license" and "attestation"
    paths have a realistic base row; the blank-license tests overwrite it in the
    request body.
    """
    import asyncio

    async def _prepare():
        async with engine.begin() as conn:
            # Only the tables this handler touches -- keeps SQLite happy without
            # the full schema / Postgres-only types elsewhere in the models.
            await conn.run_sync(
                lambda c: Base.metadata.create_all(
                    c, tables=[Company.__table__, User.__table__]
                )
            )
        async with session_factory() as s:
            s.add(
                Company(
                    id=COMPANY_ID,
                    name="Mike's HVAC",
                    slug="mikes-hvac",
                    license_number="TACLA000123C",
                    plan="free",
                    monthly_estimate_count=0,
                    settings={},
                    market="US",
                )
            )
            s.add(
                User(
                    id=USER_ID,
                    company_id=COMPANY_ID,
                    clerk_user_id=DEV_USER,
                    name="Mike Owner",
                    email="mike@example.com",
                    role="owner",  # gate handler requires auth.is_owner
                    total_estimates=0,
                )
            )
            await s.commit()

    asyncio.get_event_loop().run_until_complete(_prepare())
    return True


@pytest.fixture()
def client(engine, session_factory, seed):
    """A TestClient over a minimal app mounting ONLY the auth/me router, with
    get_db overridden to the in-memory session."""
    app = FastAPI()
    app.include_router(me_router)

    async def _override_get_db():
        async with session_factory() as s:
            yield s

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c


def _read_company(session_factory) -> Company:
    """Re-read the seeded company from a fresh session to assert persistence."""
    import asyncio
    from sqlalchemy import select

    async def _get():
        async with session_factory() as s:
            res = await s.execute(select(Company).where(Company.id == COMPANY_ID))
            return res.scalar_one()

    return asyncio.get_event_loop().run_until_complete(_get())


# -- Tests: blank / missing license is rejected (the gate) --------------------
def test_blank_license_number_rejected_422(client):
    """A blank license number must never pass the gate."""
    resp = client.patch(
        "/api/auth/me/company",
        json={"license_number": ""},
        headers=DEV_HEADERS,
    )
    assert resp.status_code == 422, resp.text
    assert "license number is required" in resp.json()["detail"].lower()


def test_whitespace_only_license_number_rejected_422(client):
    """Whitespace-only is treated as blank (handler .strip()s before checking)."""
    resp = client.patch(
        "/api/auth/me/company",
        json={"license_number": "   "},
        headers=DEV_HEADERS,
    )
    assert resp.status_code == 422, resp.text
    assert resp.json()["detail"] == "A valid contractor license number is required."


def test_null_license_number_rejected_422(client):
    """An explicit null license number is rejected the same as blank."""
    resp = client.patch(
        "/api/auth/me/company",
        json={"license_number": None},
        headers=DEV_HEADERS,
    )
    assert resp.status_code == 422, resp.text


def test_omitted_license_number_does_not_gate_or_error(client, session_factory):
    """Omitting license_number is a legal partial update (e.g. changing phone
    only): it returns 200 and leaves the existing license untouched, but does
    NOT stamp the attestation -- so the company stays un-gated (guard keeps
    redirecting to /onboarding)."""
    resp = client.patch(
        "/api/auth/me/company",
        json={"phone": "713-555-0100"},
        headers=DEV_HEADERS,
    )
    assert resp.status_code == 200, resp.text
    company = _read_company(session_factory)
    assert company.license_number == "TACLA000123C"  # unchanged
    assert company.phone == "713-555-0100"
    assert company.attestation_accepted_at is None  # still un-gated


# -- Tests: valid license + attestation passes the gate & persists ------------
def test_valid_license_and_attestation_persists_gate(client, session_factory):
    """The happy path: valid license + attestation accepted + terms version ->
    200, and both gate columns are persisted (attestation non-null, version set)."""
    resp = client.patch(
        "/api/auth/me/company",
        json={
            "license_number": "  TACLA000456C  ",  # surrounding space is stripped
            "attestation_accepted": True,
            "terms_ack_version": "v1",
        },
        headers=DEV_HEADERS,
    )
    assert resp.status_code == 200, resp.text

    payload = resp.json()
    assert payload["success"] is True
    assert payload["company"]["license_number"] == "TACLA000456C"
    assert payload["company"]["attestation_accepted_at"] is not None
    assert payload["company"]["terms_ack_version"] == "v1"

    # And it's actually persisted (re-read from a fresh session).
    company = _read_company(session_factory)
    assert company.license_number == "TACLA000456C"
    assert company.attestation_accepted_at is not None
    assert company.terms_ack_version == "v1"


def test_attestation_false_clears_gate(client, session_factory):
    """Un-ticking the attestation (attestation_accepted: false) nulls the stamp,
    so a company that later fails re-attestation is pushed back through the gate."""
    # First pass the gate.
    client.patch(
        "/api/auth/me/company",
        json={
            "license_number": "TACLA000456C",
            "attestation_accepted": True,
            "terms_ack_version": "v1",
        },
        headers=DEV_HEADERS,
    )
    # Then un-tick.
    resp = client.patch(
        "/api/auth/me/company",
        json={"attestation_accepted": False},
        headers=DEV_HEADERS,
    )
    assert resp.status_code == 200, resp.text
    company = _read_company(session_factory)
    assert company.attestation_accepted_at is None
