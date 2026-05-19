"""
SnapAI — Diagnostic Photo Upload Endpoint
POST /api/uploads  — accepts a single photo for a diagnostic step, stores it,
and optionally runs a lightweight AI grade via the vision service.

Used by: PhotoSlot.tsx (diagnostic multi / photo steps)
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import get_current_user, AuthContext
from db.database import get_db
from services.storage import get_storage

router = APIRouter()


@router.post("/api/uploads")
async def upload_diagnostic_photo(
    file: UploadFile = File(..., description="Photo file (image/*)"),
    assessment_id: str = Form(..., description="Assessment UUID this photo belongs to"),
    slot_name: str = Form(..., description="Logical slot name (e.g. 'ignitor_photo')"),
    photo_type: str = Form("diagnostic", description="'diagnostic' or 'evidence'"),
    ai_prompt: Optional[str] = Form(None, description="If provided, Gemini grades the photo"),
    _auth: AuthContext = Depends(get_current_user),
    _db: AsyncSession = Depends(get_db),
):
    """
    Accepts a multipart photo upload, stores it using the configured storage
    backend (LocalStorage in dev, R2 in production), and returns the public URL.

    Optionally runs Gemini vision grading if ai_prompt is supplied.
    """
    # ── Validate content type ─────────────────────────────────────────────────
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are accepted.")

    # ── Read bytes ────────────────────────────────────────────────────────────
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # ── Build storage path ────────────────────────────────────────────────────
    ext = (file.filename or "photo.jpg").rsplit(".", 1)[-1].lower()
    if ext not in {"jpg", "jpeg", "png", "heic", "heif", "webp"}:
        ext = "jpg"
    unique_id = uuid.uuid4().hex[:10]
    storage_path = f"photos/diagnostic/{assessment_id}/{slot_name}-{unique_id}.{ext}"

    # ── Upload ────────────────────────────────────────────────────────────────
    storage = get_storage()
    content_type = file.content_type or "image/jpeg"
    url = await storage.upload(file_bytes, storage_path, content_type)

    # ── Optional AI grading ───────────────────────────────────────────────────
    ai_grade: Optional[str] = None
    if ai_prompt:
        try:
            from services.vision import get_vision_service
            vision = get_vision_service()
            image_bytes = await storage.get_bytes(storage_path)
            if image_bytes:
                result = await vision.analyze(
                    images=[image_bytes],
                    prompt=ai_prompt,
                )
                # Return first line of response as a short grade label
                ai_grade = (result or "").strip().split("\n")[0][:120]
        except Exception:
            # Never fail the upload because of AI grading errors
            ai_grade = None

    return {
        "url": url,
        "photo_url": url,   # alias — PhotoSlot reads either key
        "slot_name": slot_name,
        "photo_type": photo_type,
        "ai_grade": ai_grade,
    }
