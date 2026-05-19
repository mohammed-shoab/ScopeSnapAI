"""
SnapAI — File Storage Abstraction
Local dev: saves files to ./uploads/ folder and serves via FastAPI static files.
Cloud:     uploads to Cloudflare R2 (S3-compatible, zero egress fees).

DESIGN PRINCIPLE: Both classes expose the same async interface.
Switching from local → cloud is a single config change (ENVIRONMENT=production).
"""

import os
import uuid
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Optional

from config import get_settings

settings = get_settings()


# ── Abstract Base ─────────────────────────────────────────────────────────────
class BaseStorage(ABC):
    """
    Interface that both LocalStorage and R2Storage must implement.
    FastAPI routes depend on this interface — never on a concrete class.
    """

    @abstractmethod
    async def upload(self, file_bytes: bytes, path: str, content_type: str = "image/jpeg") -> str:
        """Upload file bytes to storage. Returns the public URL."""
        ...

    @abstractmethod
    async def get_url(self, path: str) -> str:
        """Returns the public URL for a stored file path."""
        ...

    @abstractmethod
    async def delete(self, path: str) -> bool:
        """Deletes a file. Returns True if successful."""
        ...

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Returns True if the file exists in storage."""
        ...

    async def get_bytes(self, path_or_url: str) -> Optional[bytes]:
        """Returns file bytes. Override in subclasses for efficiency."""
        return None


# ── Local Storage (Development) ───────────────────────────────────────────────
class LocalStorage(BaseStorage):
    """
    Saves files to a local ./uploads/ directory.
    Files are served via FastAPI's StaticFiles mount at /files/.

    Zero cost. Zero setup. Instant dev iteration.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or settings.upload_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "http://localhost:8000/files"

    async def upload(self, file_bytes: bytes, path: str, content_type: str = "image/jpeg") -> str:
        """
        Saves file to ./uploads/{path}
        Example: upload(bytes, "photos/abc-hvac/assessment-123/photo-1.jpg")
        Returns: "http://localhost:8000/files/photos/abc-hvac/assessment-123/photo-1.jpg"
        """
        full_path = self.base_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(file_bytes)
        return f"{self.base_url}/{path}"

    async def get_url(self, path: str) -> str:
        return f"{self.base_url}/{path}"

    async def delete(self, path: str) -> bool:
        full_path = self.base_dir / path
        if full_path.exists():
            full_path.unlink()
            return True
        return False

    async def exists(self, path: str) -> bool:
        return (self.base_dir / path).exists()

    async def get_bytes(self, path_or_url: str) -> Optional[bytes]:
        """Helper for vision.py — loads image bytes for Gemini API.
        Accepts either a storage path or a full URL."""
        # Strip base_url prefix if it's a full URL
        if path_or_url.startswith("http"):
            prefix = self.base_url + "/"
            if path_or_url.startswith(prefix):
                path_or_url = path_or_url[len(prefix):]
            else:
                # Unknown URL format — try to fetch it
                try:
                    import httpx
                    async with httpx.AsyncClient() as client:
                        resp = await client.get(path_or_url, timeout=10)
                        if resp.status_code == 200:
                            return resp.content
                except Exception:
                    pass
                return None

        full_path = self.base_dir / path_or_url
        if full_path.exists():
            return full_path.read_bytes()
        return None


# ── R2 Storage (Production — Cloudflare) ──────────────────────────────────────
class R2Storage(BaseStorage):
    """
    Uploads files to Cloudflare R2 (S3-compatible).
    Zero egress fees — critical for image-heavy app.

    Requires: R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY,
              R2_BUCKET_NAME, R2_PUBLIC_URL in .env

    NOT used during local development. Swapped in when ENVIRONMENT=production.
    """

    def __init__(self):
        # Import boto3 only when needed (not required for local dev)
        try:
            import boto3
            self.client = boto3.client(
                "s3",
                endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=settings.r2_access_key_id,
                aws_secret_access_key=settings.r2_secret_access_key,
                region_name="auto",
            )
            self.bucket = settings.r2_bucket_name
            self.public_url = settings.r2_public_url.rstrip("/")
        except ImportError:
            raise RuntimeError(
                "boto3 is required for R2Storage. Install with: pip install boto3"
            )

    async def upload(self, file_bytes: bytes, path: str, content_type: str = "image/jpeg") -> str:
        import asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.client.put_object(
                Bucket=self.bucket,
                Key=path,
                Body=file_bytes,
                ContentType=content_type,
            )
        )
        return f"{self.public_url}/{path}"

    async def get_url(self, path: str) -> str:
        return f"{self.public_url}/{path}"

    async def delete(self, path: str) -> bool:
        import asyncio
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: self.client.delete_object(Bucket=self.bucket, Key=path)
            )
            return True
        except Exception:
            return False

    async def exists(self, path: str) -> bool:
        import asyncio
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: self.client.head_object(Bucket=self.bucket, Key=path)
            )
            return True
        except Exception:
            return False

    async def get_bytes(self, path_or_url: str) -> Optional[bytes]:
        """Fetches file bytes from R2 for vision.py Gemini API usage."""
        import asyncio
        # Strip public URL prefix if full URL provided
        if path_or_url.startswith("http"):
            prefix = self.public_url + "/"
            if path_or_url.startswith(prefix):
                path_or_url = path_or_url[len(prefix):]
            else:
                # Unknown URL — try HTTP fetch as fallback
                try:
                    import httpx
                    async with httpx.AsyncClient() as client:
                        resp = await client.get(path_or_url, timeout=10)
                        if resp.status_code == 200:
                            return resp.content
                except Exception:
                    pass
                return None
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None,
                lambda: self.client.get_object(Bucket=self.bucket, Key=path_or_url)
            )
            return response["Body"].read()
        except Exception:
            return None


# ── Factory ───────────────────────────────────────────────────────────────────
def get_storage() -> BaseStorage:
    """
    Returns the correct storage implementation based on ENVIRONMENT and credentials.

    Decision tree:
      1. ENVIRONMENT=development → LocalStorage (always, no credentials needed)
      2. ENVIRONMENT=production + R2 credentials set → R2Storage (photos survive redeploys)
      3. ENVIRONMENT=production + R2 credentials MISSING → LocalStorage + loud warning
         Photos will be lost on redeploy. Set R2_ACCOUNT_ID / R2_ACCESS_KEY_ID /
         R2_SECRET_ACCESS_KEY / R2_BUCKET_NAME / R2_PUBLIC_URL in Railway to fix.

    Railway env vars required for R2:
      R2_ACCOUNT_ID       — Cloudflare account ID (dash.cloudflare.com → right sidebar)
      R2_ACCESS_KEY_ID    — R2 API token Access Key ID
      R2_SECRET_ACCESS_KEY — R2 API token Secret
      R2_BUCKET_NAME      — bucket name (e.g. "scopesnap-photos")
      R2_PUBLIC_URL       — public bucket domain (e.g. "https://pub-xxx.r2.dev")
    """
    if settings.is_development:
        return LocalStorage()

    # Production: use R2 if credentials are present
    r2_creds_set = all([
        settings.r2_account_id,
        settings.r2_access_key_id,
        settings.r2_secret_access_key,
        settings.r2_bucket_name,
        settings.r2_public_url,
    ])

    if not r2_creds_set:
        print("\n" + "⚠️ " * 20)
        print("  WARNING: ENVIRONMENT=production but R2 credentials are not set.")
        print("  Photos are being stored locally and WILL BE LOST on next redeploy.")
        print("  Fix: set R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY,")
        print("       R2_BUCKET_NAME, R2_PUBLIC_URL in Railway environment variables.")
        print("⚠️ " * 20 + "\n")
        return LocalStorage()

    return R2Storage()


# ── Utilities ─────────────────────────────────────────────────────────────────
def generate_storage_path(company_slug: str, assessment_id: str, filename: str) -> str:
    """
    Generates a consistent storage path for assessment photos.
    Example: "photos/abc-hvac/assessment-550e8400.../photo-1.jpg"
    """
    return f"photos/{company_slug}/assessment-{assessment_id}/{filename}"


def generate_document_path(company_slug: str, estimate_id: str, doc_type: str) -> str:
    """
    Generates a consistent storage path for generated documents.
    Example: "documents/abc-hvac/estimate-550e8400.../contractor_report.pdf"
    """
    return f"documents/{company_slug}/estimate-{estimate_id}/{doc_type}"
