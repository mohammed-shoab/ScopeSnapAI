"""
SnapAI Phase 3 — Diagnostic Branch Evaluator (pure Python, no DB calls)

Imported by api/diagnostic.py to evaluate reading measurements and
branch_logic_jsonb rules. All logic mirrors Section 1.3 of
SnapAI_Phase3_Cowork_Instructions.md (the universal reading comparison rules).

WS-G3/H3/I3/J3/K3 update: added temp_delta reading type for Tab H Path B
terminal IR thermometer checks.
"""

from typing import Optional


# ── Reading Evaluation ─────────────────────────────────────────────────────────

def evaluate_reading(
    reading_type: str,
    actual_value: float,
    nameplate_spec: Optional[float] = None,
    subtype: Optional[str] = None,
    tolerance_pct: int = 10,
) -> dict:
    """
    Evaluate a numeric reading against spec (or fixed thresholds).

    Returns:
        {
            classification: 'OK' | 'LOW' | 'HIGH' | 'CRITICAL',
            passed: bool,
            flag_message: str | None,
            branch_key: str   # feeds branch_logic_jsonb lookup
        }
    """
    rt = reading_type.lower()

    # ── Capacitor (uF) ─────────────────────────────────────────────────────────
    if rt == "uf":
        if nameplate_spec is None:
            return _unknown("no nameplate spec for uF", "ok")
        pct_delta = (actual_value - nameplate_spec) / nameplate_spec * 100
        if pct_delta < -tolerance_pct:
            return _result("LOW", False,
                f"uF {actual_value:.1f} is {abs(pct_delta):.0f}% below spec ({nameplate_spec:.1f})", "low")
        if pct_delta > 5:
            return _result("HIGH", False,
                f"uF {actual_value:.1f} is {pct_delta:.0f}% above spec ({nameplate_spec:.1f})", "high")
        return _result("OK", True, None, "ok")

    # ── Amp draw — compressor vs RLA ───────────────────────────────────────────
    if rt in ("amps_compressor", "amps"):
        if nameplate_spec is None:
            return _unknown("no RLA spec", "ok")
        pct_delta = (actual_value - nameplate_spec) / nameplate_spec * 100
        if pct_delta > tolerance_pct:
            return _result("HIGH", False,
                f"Compressor amps {actual_value:.1f}A is {pct_delta:.0f}% over RLA ({nameplate_spec:.1f}A)", "over_rla")
        if actual_value < nameplate_spec * 0.5:
            return _result("LOW", False,
                f"Compressor amps {actual_value:.1f}A far below RLA — compressor may not be loaded", "under")
        return _result("OK", True, None, "ok")

    # ── Amp draw — blower vs FLA ───────────────────────────────────────────────
    if rt == "amps_blower":
        if nameplate_spec is None:
            return _unknown("no FLA spec", "ok")
        pct_delta = (actual_value - nameplate_spec) / nameplate_spec * 100
        if pct_delta > tolerance_pct:
            return _result("HIGH", False,
                f"Blower amps {actual_value:.1f}A is {pct_delta:.0f}% over FLA ({nameplate_spec:.1f}A)", "over_fla")
        return _result("OK", True, None, "ok")

    # ── Voltage (line) L1 + L2 ─────────────────────────────────────────────────
    if rt == "voltage" and subtype in (None, "l1_l2", "L1_L2", "line"):
        nominal = 230.0
        pct_delta = abs(actual_value - nominal) / nominal * 100
        if actual_value < 50:
            return _result("CRITICAL", False, f"No power: {actual_value:.0f}V at L1+L2", "no_power")
        if pct_delta > 10:
            return _result("LOW", False,
                f"Line voltage {actual_value:.0f}V is {pct_delta:.0f}% from nominal 230V", "phase_loss")
        return _result("OK", True, None, "power_passes_normal")

    # ── Voltage (ignitor) ─────────────────────────────────────────────────────
    if rt == "voltage" and subtype and "ignitor" in subtype.lower():
        if actual_value < 50:
            return _result("CRITICAL", False, f"No voltage at ignitor: {actual_value:.0f}V", "no_voltage")
        return _result("OK", True, None, "ok")

    # ── Voltage drop (across terminal / wire) ─────────────────────────────────
    if rt == "voltage_drop":
        if actual_value < 0.5:
            return _result("OK", True, None, "ok")
        if actual_value < 1.0:
            return _result("LOW", False, f"Elevated voltage drop: {actual_value:.2f}V", "elevated")
        if actual_value < 3.0:
            return _result("HIGH", False, f"High voltage drop: {actual_value:.2f}V", "elevated_high")
        return _result("CRITICAL", False, f"Fault-level voltage drop: {actual_value:.2f}V", "fault")

    # ── Delta-T (supply minus return, cooling) ─────────────────────────────────
    if rt == "delta_t":
        if actual_value < 14:
            return _result("LOW", False,
                f"Delta-T {actual_value:.1f}F is below 14F — airflow or refrigerant issue", "delta_t_low")
        if actual_value <= 22:
            return _result("OK", True, None, "delta_t_ok")
        return _result("HIGH", False,
            f"Delta-T {actual_value:.1f}F above 22F — possible over-cooling / low airflow", "delta_t_high")

    # ── Temperature delta (terminal vs ambient — Tab H Path B) ───────────────
    if rt == "temp_delta":
        # Section 1.3: >10F delta on any terminal = suspect loose connection
        threshold = 10.0
        if actual_value > threshold:
            return _result("HIGH", False,
                f"Terminal delta {actual_value:.1f}F exceeds {threshold:.0f}F threshold — suspect loose terminal",
                "max_delta_over_10F")
        return _result("OK", True, None, "all_within_10F")

    # ── Ohms (ignitor / sensor) ────────────────────────────────────────────────
    if rt == "ohms":
        if actual_value > 1e6 or actual_value == 0:
            return _result("CRITICAL", False, "Reads open circuit — element cracked or broken", "open")
        if subtype and "ignitor" in subtype.lower():
            if 50 <= actual_value <= 80:
                return _result("OK", True, None, "ok")
            return _result("HIGH", False,
                f"Ignitor resistance {actual_value:.0f}ohm outside 50-80ohm healthy range", "out_of_spec")
        # Generic ohm check — sensor/component
        return _result("OK", True, None, "ok")

    # ── Micro-amps (flame sensor) ─────────────────────────────────────────────
    if rt == "micro_amps":
        if actual_value < 1.0:
            return _result("CRITICAL", False,
                f"Flame sensor {actual_value:.2f}uA — oxide coated, replace", "replace")
        if actual_value < 2.0:
            return _result("LOW", False,
                f"Flame sensor {actual_value:.2f}uA — clean and retest", "marginal")
        return _result("OK", True, None, "ok")

    # ── IR temperature (terminal, per Section 1.3) ────────────────────────────
    if rt == "temp_f" and subtype and "terminal" in subtype:
        # caller passes ambient_temp separately; we receive delta already if subtype='terminal_delta'
        # For raw terminal temp, the caller computes delta vs ambient before calling
        return _result("OK", True, None, "ok")

    # ── Default: unknown reading type ─────────────────────────────────────────
    return _unknown(f"unrecognised reading_type '{reading_type}'", "ok")


def _result(classification: str, passed: bool, message: Optional[str], branch_key: str) -> dict:
    return {"classification": classification, "passed": passed,
            "flag_message": message, "branch_key": branch_key}


def _unknown(reason: str, branch_key: str) -> dict:
    return {"classification": "OK", "passed": True,
            "flag_message": f"Could not evaluate: {reason}", "branch_key": branch_key}


# ── Branch Logic Evaluator ─────────────────────────────────────────────────────

def evaluate_branch(question: dict, answer, computed_branch_key: Optional[str] = None) -> dict:
    """
    Apply branch_logic_jsonb to an answer and return the routing outcome.

    Returns one of:
        {'kind': 'next_step',    'next_step_id': str}
        {'kind': 'resolve_card', 'card_id': int, 'photo_slots': list}
        {'kind': 'phase_2_gate', 'continuation': dict}
        {'kind': 'service_step', 'finding': dict | None, 'next_step_id': str | None}
        {'kind': 'escalate',     'reason': str}
    """
    branch_logic = question.get("branch_logic_jsonb", {})
    branch_key = computed_branch_key if computed_branch_key is not None else str(answer)

    rule = branch_logic.get(branch_key)
    if rule is None:
        rule = branch_logic.get("any")  # wildcard — photo steps that always route the same way
    if rule is None:
        rule = branch_logic.get("default", {"escalate": True, "reason": "unhandled_answer"})

    if rule is None:
        return {"kind": "escalate", "reason": f"no rule for branch_key='{branch_key}'"}

    if "phase_2_gate" in rule and rule["phase_2_gate"]:
        return {"kind": "phase_2_gate", "continuation": rule.get("after", {})}

    if "resolve_card" in rule:
        return {
            "kind": "resolve_card",
            "card_id": rule["resolve_card"],
            "photo_slots": rule.get("photo_slots", []),
        }

    if "next_step_id" in rule:
        return {"kind": "next_step", "next_step_id": rule["next_step_id"]}

    if "finding" in rule:
        return {
            "kind": "service_step",
            "finding": rule.get("finding"),
            "next_step_id": rule.get("next_step_id"),
        }

    if rule.get("escalate"):
        return {"kind": "escalate", "reason": rule.get("reason", "escalated")}

    return {"kind": "escalate", "reason": f"unrecognised rule shape: {list(rule.keys())}"}


# ── Photo-answer passthrough ───────────────────────────────────────────────────

def evaluate_photo_answer(question: dict, ai_grade: Optional[str] = None) -> dict:
    """
    For photo-type questions, the branch key is the AI grade returned by Gemini.
    Falls through to 'default' if no grade (i.e. tech uploaded but AI not called yet).
    """
    return evaluate_branch(question, ai_grade or "ungraded", ai_grade)
