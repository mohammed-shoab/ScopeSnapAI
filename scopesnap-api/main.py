import os
"""
SnapAI API — FastAPI Application Entry Point

Run locally: uvicorn main:app --reload --port 8000
API docs:    http://localhost:8000/docs
Health:      http://localhost:8000/health
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from config import get_settings
from db.database import check_db_connection
from api import assessments, estimates, reports, properties
from api.payments import router as payments_router, webhook_router as stripe_webhook_router
from api.clerk_webhook import router as clerk_webhook_router, me_router as auth_router
from api.analytics import router as analytics_router
from api.billing import router as billing_router, webhook_router as billing_webhook_router
from api.pricing_rules import router as pricing_rules_router
from api.events import router as events_router
from api.admin import router as admin_router
from api.sensor_diagnosis import router as sensor_diagnosis_router
from api.repo import router as repo_router  # WS-A: GET /api/repo/version
from api.ocr import router as ocr_router   # WS-B: POST /api/ocr/nameplate
from api.fault_estimate import router as fault_estimate_router
from api.diagnostic import router as diagnostic_router         # WS-A3: Phase 3 diagnostic flow
from api.error_code import router as error_code_router         # WS-D
from api.thermal import router as thermal_router               # WS-E
from api.card_feedback import router as feedback_router        # WS-F
from api.recommend import router as recommend_router           # WS-H
from api.followup import router as followup_router             # WS-I
from api.uploads import router as uploads_router   # Diagnostic photo upload
from api.models import router as models_router     # Section 5A: model lookup


# ── Sentry Error Tracking ─────────────────────────────────────────────────────
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

_sentry_dsn = os.environ.get("SENTRY_DSN", "")
if _sentry_dsn:
    sentry_sdk.init(
        dsn=_sentry_dsn,
        integrations=[FastApiIntegration(), SqlalchemyIntegration()],
        traces_sample_rate=0.1,
        environment=os.environ.get("ENVIRONMENT", "development"),
        release="snapai-api@1.0.0",
    )

settings = get_settings()

# ── Rate Limiter ──────────────────────────────────────────────────────────────
# The limiter is defined in rate_limit.py so individual API modules can
# import it without circular-importing main.py. Imported here to wire it
# into FastAPI state / middleware below.
from rate_limit import limiter

# ── App Setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="SnapAI API",
    description="AI-powered HVAC estimation platform for contractors",
    version="0.1.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    redirect_slashes=False,
)

# ── Rate Limit Middleware + Handler ──────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "https://snapai.mainnov.tech",
        "https://pk.snapai.mainnov.tech",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Local File Serving ─────────────────────────────────────────────────────────
# Serve /files from local disk when R2 is not configured (dev or staging).
# When R2 credentials are set, the frontend will reference R2 URLs directly and
# this mount is a harmless no-op fallback.
uploads_dir = Path(settings.upload_dir)
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/files", StaticFiles(directory=str(uploads_dir)), name="uploads")

# ── API Routers ───────────────────────────────────────────────────────────────
app.include_router(assessments.router)
app.include_router(recommend_router)        # WS-H: registered FIRST to prevent /{estimate_id} catch-all conflict
app.include_router(estimates.router)
app.include_router(reports.router)
app.include_router(properties.router)
app.include_router(payments_router)
app.include_router(stripe_webhook_router)
app.include_router(clerk_webhook_router)
app.include_router(auth_router)
app.include_router(analytics_router)
app.include_router(billing_router)
app.include_router(billing_webhook_router)
app.include_router(pricing_rules_router)
app.include_router(events_router)  # POST /api/events + POST /api/waitlist
app.include_router(admin_router)   # POST /admin/seed, GET /admin/status (protected)
app.include_router(sensor_diagnosis_router)  # POST /api/sensor-diagnosis (XGBoost Track A)
app.include_router(repo_router)             # GET /api/repo/version (WS-A data foundation)
app.include_router(ocr_router)              # POST /api/ocr/nameplate (WS-B Step Zero OCR)
app.include_router(fault_estimate_router)
app.include_router(diagnostic_router)          # GET+POST /api/diagnostic/* (WS-A3)
app.include_router(error_code_router)       # WS-D brand DB lookup
app.include_router(thermal_router)          # WS-E thermal camera
app.include_router(feedback_router)         # WS-F training feedback
app.include_router(followup_router)         # WS-I follow-up emails
app.include_router(uploads_router)           # POST /api/uploads (diagnostic photo upload)
app.include_router(models_router)            # GET /api/models/* (Section 5A model lookup)


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["system"])
async def health_check():
    """
    Health check endpoint.
    Returns DB connection status — used by WP-01 acceptance criteria.

    Expected response: {"status": "ok", "db": "connected"}
    """
    db_ok = await check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "db": "connected" if db_ok else "disconnected",
        "environment": settings.environment,
        "version": "0.1.0",
    }


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", tags=["system"])
async def root():
    return {
        "name": "SnapAI API",
        "version": "0.1.0",
        "docs": "http://localhost:8000/docs",
        "health": "http://localhost:8000/health",
    }


# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    print(f"\n{'='*50}")
    print(f"  SnapAI API starting up")
    print(f"  Environment: {settings.environment}")
    print(f"  Database: {settings.database_url[:50]}...")
    if settings.is_development:
        print(f"  Storage: LocalStorage → {settings.upload_dir}")
        print(f"  Email: ConsoleSender (emails printed to terminal)")
        print(f"  API Docs: http://localhost:8000/docs")
    print(f"{'='*50}\n")

    # Verify DB connection on startup
    db_ok = await check_db_connection()
    if db_ok:
        print("✅ Database connection: OK")
    else:
        print("❌ Database connection: FAILED")
        print("   Make sure PostgreSQL is running and DATABASE_URL is correct.")
        print("   For Windows, run: docker start scopesnap-db")

    import sys as _sys
    _sys.path.insert(0, "/app")

    # Auto-seed pricing rules if the table is empty
    try:
        from db.database import AsyncSessionLocal
        from db.models import PricingRule
        from sqlalchemy import select, func as sql_func
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(sql_func.count()).select_from(PricingRule))
            rule_count = result.scalar_one()
        if rule_count == 0:
            print("📋 Pricing rules table is empty — seeding national defaults...")
            from scripts.seed_pricing import seed_pricing
            await seed_pricing()
            print("✅ Pricing rules seeded successfully")
        else:
            print(f"✅ Pricing rules: {rule_count} rules loaded")
    except Exception as _seed_err:
        print(f"⚠️  Pricing rules seed failed (non-fatal): {_seed_err}")

    # Auto-seed equipment models if the table is empty
    try:
        from db.models import EquipmentModel
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(sql_func.count()).select_from(EquipmentModel))
            model_count = result.scalar_one()
        if model_count == 0:
            print("🔧 Equipment models table is empty — seeding 50 HVAC models...")
            from scripts.seed_equipment_db import seed_equipment_db
            await seed_equipment_db()
            print("✅ Equipment models seeded successfully")
        else:
            print(f"✅ Equipment models: {model_count} models loaded")
    except Exception as _equip_err:
        print(f"⚠️  Equipment models seed failed (non-fatal): {_equip_err}")
