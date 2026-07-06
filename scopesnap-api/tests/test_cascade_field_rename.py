"""
D7 guard — cascade JSON field rename (legal-safe-wordings v1).

Protects against the silent-fallback trap: if the prompt asks Gemini to return
one key but the reader `.get()`s a different key, the reader silently returns
its fallback forever and the rename looks done but isn't. These tests assert the
prompt key and the reader key are the SAME, and that no old key survives.
"""
import re
from pathlib import Path

API = Path(__file__).resolve().parents[1]
PROMPTS = (API / "prompts" / "cascade_prompts.py").read_text(encoding="utf-8")
CASCADE = (API / "services" / "ai_cascade.py").read_text(encoding="utf-8")

OLD = ("confirmed_fault", "sensor_diagnosis_correct", "visual_findings_correct")
NEW_PRIMARY = "suggested_finding_for_review"
NEW_PROMPT_ONLY = ("sensor_reading_appears_consistent", "visual_scan_supports_finding")


def test_no_old_keys_anywhere():
    for tok in OLD:
        assert tok not in PROMPTS, f"old key {tok!r} still in cascade_prompts.py"
        assert tok not in CASCADE, f"old key {tok!r} still in ai_cascade.py"


def test_prompt_declares_new_keys():
    assert PROMPTS.count(NEW_PRIMARY) >= 2, "both Track A & B prompts must ask for the renamed primary key"
    for tok in NEW_PROMPT_ONLY:
        assert tok in PROMPTS, f"prompt-only field {tok!r} missing from prompt schema"


def test_reader_key_matches_prompt_key():
    # every gemini_result.get("...fault...") in the reader must use the NEW key,
    # so the extracted value can never silently fall back to the default.
    gets = re.findall(r'gemini_result\.get\(\s*"([^"]+)"', CASCADE)
    finding_gets = [k for k in gets if "fault" in k or "finding" in k]
    assert finding_gets, "expected at least one reader extraction of the finding key"
    for k in finding_gets:
        assert k == NEW_PRIMARY, f"reader extracts {k!r} but prompt returns {NEW_PRIMARY!r} (silent-fallback trap)"


def test_fallback_dict_uses_new_key():
    assert f'"{NEW_PRIMARY}": "unknown"' in CASCADE, "Gemini-failure fallback dict must use the renamed key"
