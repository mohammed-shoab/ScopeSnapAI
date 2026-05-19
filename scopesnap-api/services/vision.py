"""
SnapAI — Gemini Vision AI Service
Handles all calls to Gemini 2.5 Flash for equipment photo analysis.
Includes retry logic, timeout handling, and graceful error recovery.

FREE TIER: 1,000 requests/day, 15 requests/minute — sufficient for development.
Get your API key at: https://ai.google.dev → Get API Key
"""

import json
import asyncio
import time
from typing import Optional
from pathlib import Path

from config import get_settings

settings = get_settings()

# ── Constants ─────────────────────────────────────────────────────────────────
MAX_RETRIES = 2
TIMEOUT_SECONDS = 30
LOW_CONFIDENCE_THRESHOLD = 50


class VisionAnalysisError(Exception):
    """Raised when Gemini analysis fails after all retries."""
    pass


class GeminiVisionService:
    """
    Wrapper around Gemini 2.5 Flash for HVAC equipment analysis.

    Usage:
        vision = GeminiVisionService()
        result = await vision.analyze_equipment_photos(
            image_bytes_list=[photo1_bytes, photo2_bytes],
            prompt=EQUIPMENT_ANALYSIS_PROMPT
        )
    """

    def __init__(self):
        if not settings.gemini_api_key:
            print("[VisionService] WARNING: GEMINI_API_KEY not set.")
            if settings.is_development:
                print("[VisionService] DEV MODE: Using mock AI responses for testing.")
                print("[VisionService] Get a free key at: https://ai.google.dev")
                self._initialized = False
                self._mock_mode = True
            else:
                print("[VisionService] GEMINI_API_KEY is required in production!")
                self._initialized = False
                self._mock_mode = False
            return
        self._mock_mode = False

        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
            self._initialized = True
            print("[VisionService] Gemini 2.5 Flash initialized successfully.")
        except ImportError:
            raise RuntimeError(
                "google-generativeai package required: pip install google-generativeai"
            )

    async def analyze_equipment_photos(
        self,
        image_bytes_list: list[bytes],
        prompt: str,
        image_content_types: Optional[list[str]] = None,
    ) -> dict:
        """
        Sends 1-5 equipment photos to Gemini 2.5 Flash with the structured prompt.
        Returns parsed JSON response from AI.

        Args:
            image_bytes_list: List of raw image bytes (1-5 images)
            prompt: The EQUIPMENT_ANALYSIS_PROMPT from prompts/equipment_analysis.py
            image_content_types: MIME types for each image (defaults to image/jpeg)

        Returns:
            Parsed JSON dict matching the EQUIPMENT_ANALYSIS_PROMPT schema

        Raises:
            VisionAnalysisError: If all retries fail or response is not valid JSON
        """
        if not self._initialized:
            if getattr(self, '_mock_mode', False) and settings.is_development:
                print("[VisionService] Returning MOCK analysis (no GEMINI_API_KEY set)")
                return self._mock_analysis_response()
            raise VisionAnalysisError(
                "Gemini API key not configured. Set GEMINI_API_KEY in .env"
            )

        if not image_bytes_list:
            raise VisionAnalysisError("No images provided for analysis.")

        if len(image_bytes_list) > 5:
            raise VisionAnalysisError("Maximum 5 images per assessment.")

        content_types = image_content_types or ["image/jpeg"] * len(image_bytes_list)

        last_error = None
        for attempt in range(MAX_RETRIES + 1):
            if attempt > 0:
                print(f"[VisionService] Retry attempt {attempt}/{MAX_RETRIES}...")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

            try:
                result = await self._call_gemini(image_bytes_list, content_types, prompt)
                return result

            except asyncio.TimeoutError:
                last_error = f"Gemini API timed out after {TIMEOUT_SECONDS}s"
                print(f"[VisionService] Timeout on attempt {attempt + 1}")

            except Exception as e:
                last_error = str(e)
                print(f"[VisionService] Error on attempt {attempt + 1}: {e}")

        raise VisionAnalysisError(
            f"Gemini analysis failed after {MAX_RETRIES + 1} attempts. Last error: {last_error}"
        )

    async def _call_gemini(
        self, image_bytes_list: list[bytes], content_types: list[str], prompt: str
    ) -> dict:
        """
        Makes the actual API call to Gemini. Runs in executor to avoid blocking.
        """
        loop = asyncio.get_event_loop()

        def _sync_call():
            import google.generativeai as genai

            # Build content parts: images first, then the prompt
            parts = []
            for img_bytes, mime_type in zip(image_bytes_list, content_types):
                parts.append({"mime_type": mime_type, "data": img_bytes})
            parts.append(prompt)

            response = self.model.generate_content(parts)
            return response.text

        # Run with timeout
        raw_text = await asyncio.wait_for(
            loop.run_in_executor(None, _sync_call),
            timeout=TIMEOUT_SECONDS
        )

        # Parse JSON response
        parsed = self._parse_json_response(raw_text)

        # Flag low confidence results (don't fail — return with flag)
        confidence = parsed.get("equipment_id", {}).get("confidence", 0)
        if confidence < LOW_CONFIDENCE_THRESHOLD:
            parsed["_low_confidence"] = True
            parsed["_confidence_warning"] = (
                f"AI confidence is {confidence}% (below {LOW_CONFIDENCE_THRESHOLD}% threshold). "
                "Consider requesting additional photos or manual review."
            )
            print(f"[VisionService] Low confidence result: {confidence}%")

        return parsed

    def _mock_analysis_response(self) -> dict:
        """
        Returns a realistic mock AI response for development testing (no API key needed).
        Based on a typical Carrier AC unit assessment.
        """
        return {
            "brand": "Carrier",
            "model_number": "24ACC636A003",
            "serial_number": "3516E12345",
            "equipment_type": "ac_unit",
            "confidence": 87,
            "confidence_reasoning": "Mock response - data plate clearly visible in photo",
            "overall_condition": "fair",
            "estimated_age_years": 9,
            "components": [
                {
                    "name": "evaporator_coil",
                    "condition": "moderate_issue",
                    "description_technical": "Moderate evaporator coil corrosion with oxidation deposits",
                    "description_plain": "Green corrosion buildup on the indoor cooling coil. This reduces efficiency and can cause leaks.",
                    "urgency": "soon"
                },
                {
                    "name": "condenser_fins",
                    "condition": "minor_issue",
                    "description_technical": "Minor condenser fin bending, approximately 15% fin damage",
                    "description_plain": "Some bent fins on the outdoor unit. Slightly reduces airflow but not urgent.",
                    "urgency": "monitor"
                },
                {
                    "name": "compressor",
                    "condition": "normal",
                    "description_technical": "Compressor appears normal with no visible oil stains or damage",
                    "description_plain": "The main pump looks healthy — no visible issues.",
                    "urgency": "none"
                },
                {
                    "name": "refrigerant_lines",
                    "condition": "normal",
                    "description_technical": "Insulation intact, no frost patterns indicating proper charge",
                    "description_plain": "The coolant pipes look good — properly insulated and no unusual frost.",
                    "urgency": "none"
                }
            ],
            "photo_annotations": [
                {
                    "photo_index": 0,
                    "annotations": [
                        {
                            "type": "circle",
                            "x_pct": 35,
                            "y_pct": 45,
                            "r_pct": 8,
                            "color": "orange",
                            "label": "COIL CORROSION",
                            "description": "Green corrosion buildup on cooling coil"
                        },
                        {
                            "type": "rectangle",
                            "x_pct": 60,
                            "y_pct": 20,
                            "w_pct": 20,
                            "h_pct": 15,
                            "color": "green",
                            "label": "DATA PLATE",
                            "description": "Model: 24ACC636A003, Serial: 3516E12345"
                        }
                    ]
                }
            ],
            "_mock": True
        }

    def _parse_json_response(self, raw_text: str) -> dict:
        """
        Extracts and parses JSON from Gemini's text response.
        Gemini sometimes wraps JSON in ```json ... ``` markdown blocks.
        """
        text = raw_text.strip()

        # Remove markdown code blocks if present
        if text.startswith("```"):
            lines = text.split('\n')
            # Remove first and last lines (```json and ```)
            text = '\n'.join(lines[1:-1]) if len(lines) > 2 else text

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"[VisionService] JSON parse failed. Raw response:\n{raw_text[:500]}")
            raise VisionAnalysisError(
                f"Gemini returned non-JSON response. Parse error: {e}\n"
                f"Raw text (first 200 chars): {raw_text[:200]}"
            )


# ── Module-level instance (singleton pattern) ─────────────────────────────────
_vision_service: Optional[GeminiVisionService] = None


def get_vision_service() -> GeminiVisionService:
    """
    Returns a cached GeminiVisionService instance.
    Use as FastAPI dependency or call directly.
    """
    global _vision_service
    if _vision_service is None:
        _vision_service = GeminiVisionService()
    return _vision_service
