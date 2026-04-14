"""
SnapAI — Application Configuration
Reads all settings from environment variables / .env file.
Uses pydantic-settings for type-safe config with validation.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Database ──────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:devpass@localhost:5432/scopesnap_dev"

    # ── Environment ───────────────────────────────────────────
    # "development" → LocalStorage + ConsoleSender (everything local, $0)
    # "production"  → R2Storage + ResendSender (cloud)
    environment: str = "development"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    # ── Gemini Vision AI ──────────────────────────────────────
    gemini_api_key: str = ""

    # ── File Storage (Local Dev) ──────────────────────────────
    upload_dir: str = "./uploads"

    # ── File Storage (Cloud — Cloudflare R2) ─────────────────
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "scopesnap-photos"
    r2_public_url: str = ""

    # ── Auth (Clerk) ──────────────────────────────────────────
    clerk_secret_key: str = ""
    clerk_publishable_key: str = ""
    clerk_webhook_secret: str = ""  # svix webhook signing secret from Clerk dashboard

    # ── Payments (Stripe) ─────────────────────────────────────
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    # ── Email (Resend) ────────────────────────────────────────
    resend_api_key: str = ""
    from_email: str = "estimates@mainnov.tech"

    # ── URLs ──────────────────────────────────────────────────
    frontend_url: str = "http://localhost:3000"
    report_base_url: str = "http://localhost:3000/r"


@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached settings instance.
    Use as FastAPI dependency: settings: Settings = Depends(get_settings)
    Or import directly: from config import get_settings; settings = get_settings()
    """
    return Settings()
