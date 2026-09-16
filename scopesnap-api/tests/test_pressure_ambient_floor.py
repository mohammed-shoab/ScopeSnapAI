"""Regression tests for the ambient-floor fix (audit 2026-09-16, finding F8)
and the boundary assertions the audit verified but nothing guarded.

F8: when ambient_c is BELOW the lowest configured operating_targets row for a
market+refrigerant, the lookup matched nothing and fell through to the
hot-weather _FALLBACK_* dict. That biases toward a false "low" classification,
which routes to a false refrigerant-leak diagnosis. The fix selects the COLDEST
configured band instead.

Exercised against a stubbed DB, so no live Postgres is required.
"""
import asyncio

from api.diagnostic import _evaluate_pressure_for_market


class _Row:
    def __init__(self, s_min, s_max, d_min, d_max):
        self.suction_min_psi = s_min
        self.suction_max_psi = s_max
        self.discharge_min_psi = d_min
        self.discharge_max_psi = d_max


class _Result:
    def __init__(self, row):
        self._row = row

    def fetchone(self):
        return self._row


class _StubDB:
    """Mimics the two-step lookup: floor-match first, coldest-row fallback second.

    `rows` maps ambient_c -> _Row. A query carrying an `amb` bind floors to the
    nearest row at or below it; a query without `amb` returns the coldest row.
    """

    def __init__(self, rows):
        self.rows = rows
        self.queries = []

    async def execute(self, stmt, params=None):
        params = params or {}
        self.queries.append(params)
        if not self.rows:
            return _Result(None)
        if "amb" in params:
            eligible = [a for a in self.rows if a <= params["amb"]]
            if not eligible:
                return _Result(None)
            return _Result(self.rows[max(eligible)])
        # no ambient bind -> coldest configured row (the F8 path)
        return _Result(self.rows[min(self.rows)])


def _run(db, value, subtype, refrigerant, ambient_c, market):
    return asyncio.run(
        _evaluate_pressure_for_market(
            db, value, subtype, refrigerant, ambient_c, market=market
        )
    )


# --- F8: PK R-22 below its lowest row -------------------------------------
# Real staging data: PK R-22 has rows ONLY at 35C (65-72) and 45C (78-88).

PK_R22 = {35: _Row(65, 72, 250, 275), 45: _Row(78, 88, 310, 345)}


def test_pk_r22_below_lowest_row_uses_coldest_band_not_hot_fallback():
    """68 PSI at 30C is normal for the coldest (35C) band. The old hot-band
    fallback (78-88) would have called it "low" -> false refrigerant leak."""
    db = _StubDB(PK_R22)
    assert _run(db, 68, "suction", "R-22", 30, "PK") == "ok"


def test_pk_r22_below_lowest_row_still_detects_genuine_low():
    db = _StubDB(PK_R22)
    assert _run(db, 40, "suction", "R-22", 30, "PK") == "low"


def test_second_query_fires_only_when_floor_lookup_missed():
    db = _StubDB(PK_R22)
    _run(db, 68, "suction", "R-22", 30, "PK")
    assert len(db.queries) == 2, "expected floor lookup then coldest-row lookup"

    db2 = _StubDB(PK_R22)
    _run(db2, 68, "suction", "R-22", 40, "PK")
    assert len(db2.queries) == 1, "floor matched; must not issue a second query"


def test_no_rows_at_all_still_uses_static_fallback():
    """US R-32 is static 110-145 BY DESIGN (PROJECT_BRAIN L84). With zero rows
    the fallback dict must still apply - F8 must not change this."""
    db = _StubDB({})
    assert _run(db, 130, "suction", "R-32", 35, "US") == "ok"
    assert _run(db, 100, "suction", "R-32", 35, "US") == "low"
    assert _run(db, 200, "suction", "R-32", 35, "US") == "high"


# --- Boundary assertions the audit checked but nothing guarded -------------

US_R410A = {
    25: _Row(95, 120, 200, 250),
    30: _Row(105, 130, 215, 265),
    35: _Row(115, 140, 225, 275),
    40: _Row(125, 150, 240, 290),
}


def test_r410a_130psi_is_normal_not_high():
    """Canonical assertion: R-410A 130 PSI must classify NORMAL, not route to
    Dirty Coil. Holds only because the comparison is EXCLUSIVE (value > hi);
    flipping to >= would silently regress it."""
    db = _StubDB(US_R410A)
    assert _run(db, 130, "suction", "R-410A", 30, "US") == "ok"
    assert _run(db, 131, "suction", "R-410A", 30, "US") == "high"


def test_pk_r22_high_min_is_88():
    db = _StubDB(PK_R22)
    assert _run(db, 88, "suction", "R-22", 45, "PK") == "ok"
    assert _run(db, 89, "suction", "R-22", 45, "PK") == "high"


PK_R32 = {30: _Row(100, 120, 280, 320), 40: _Row(120, 140, 365, 410)}


def test_pk_r32_high_min_is_140():
    db = _StubDB(PK_R32)
    assert _run(db, 140, "suction", "R-32", 40, "PK") == "ok"
    assert _run(db, 141, "suction", "R-32", 40, "PK") == "high"


def test_not_sure_refrigerant_defaults_to_r410a():
    db = _StubDB(US_R410A)
    assert _run(db, 130, "suction", "not_sure", 30, "US") == "ok"
