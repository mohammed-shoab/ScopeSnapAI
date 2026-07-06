"""
SnapAI — Homeowner Narrative Prompt (V1)
Sent to Gemini 2.5 Flash-Lite AFTER equipment analysis.
Generates 2-3 sentences of plain-English explanation for homeowner report.

This is the ONLY non-vision LLM call in the entire pipeline.
Cost: ~$0.10/1M tokens with Flash-Lite. Negligible.

The narrative must be warm, clear, jargon-free, and under 40 words.
"""

# Template string — fill with .format() before sending to Gemini
HOMEOWNER_NARRATIVE_PROMPT = """
You are writing a plain-language summary for a homeowner. This summary supports the
licensed HVAC contractor's professional recommendations -- it does not replace them.

Never present findings as a diagnosis. Never use medical analogies. Never make specific
efficiency, cost, or lifespan claims. Attribute all recommendations to the licensed contractor.

Equipment: {brand} {model}, installed {install_year} ({age} years old).
Preliminary contractor assessment: {overall_condition}.
Items your contractor flagged for review: {issues_plain_english}

Write exactly 2 sentences:
1. What the equipment is and what your contractor observed (describe what was observed for
   review; do not state a definitive condition).
2. What your contractor recommends you discuss with them next.

Under 40 words total. Use "your". Attribute recommendations to "your contractor". Never state
that SnapAI diagnosed or determined anything.

RESPOND WITH ONLY the 2 sentences -- no JSON, no extra text.
"""


def build_narrative_prompt(
    brand: str,
    model: str,
    install_year: int | None,
    overall_condition: str,
    issues_plain_english: list[str],
) -> str:
    """
    Fills in the HOMEOWNER_NARRATIVE_PROMPT template with assessment data.

    Args:
        brand: Equipment brand (e.g., "Carrier")
        model: Model number (e.g., "24ACC636A003")
        install_year: Year installed (from serial decode or tech estimate)
        overall_condition: One of: excellent, good, fair, poor, critical
        issues_plain_english: List of plain-English issue descriptions

    Returns:
        Formatted prompt string ready to send to Gemini Flash-Lite
    """
    from datetime import datetime
    current_year = datetime.now().year
    age = f"{current_year - install_year}" if install_year else "unknown"
    install_year_str = str(install_year) if install_year else "unknown year"

    if not issues_plain_english:
        issues_str = "No significant issues found — equipment looks healthy."
    elif len(issues_plain_english) == 1:
        issues_str = issues_plain_english[0]
    else:
        issues_str = "; ".join(issues_plain_english[:3])  # Max 3 issues in prompt
        if len(issues_plain_english) > 3:
            issues_str += f" (and {len(issues_plain_english) - 3} more)"

    return HOMEOWNER_NARRATIVE_PROMPT.format(
        brand=brand or "HVAC unit",
        model=model or "unknown model",
        install_year=install_year_str,
        age=age,
        overall_condition=overall_condition,
        issues_plain_english=issues_str,
    )


# ── Prompt Metadata ───────────────────────────────────────────────────────────
NARRATIVE_PROMPT_VERSION = "1.1.0"  # 2026-07-06 decision-support rewrite (legal-safe wordings v1)
NARRATIVE_MODEL = "gemini-2.5-flash"  # Use flash-lite for cost savings in production
