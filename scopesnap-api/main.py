"""
ScopeSnap API — FastAPI Application Entry Point

Run locally: uvicorn main:app --reload --port 8000
API docs:    http://localhost:8000/docs
Health:      http://localhost:8000/health
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from config import get_settings
from db.database import check_db_connection
from api import assessments, estimates, reports, properties
from api.payments import router as payments_router, webhook_router as stripe_webhook_router
from api.clerk_webhook import router as clerk_webhook_router, me_router as auth_router
from api.analytics import router as analytics_router
from api.billing import router as billing_router, webhook_router as billing_webhook_router
from api.pricing_rules import router as pricing_rules_router
from api.events import router as events_router

settings = get_settings()

# ── App Setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ScopeSnap API",
    description="AI-powered HVAC estimation platform for contractors",
    version="0.1.0",
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    redirect_slashes=False,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Local File Serving (Development Only) ─────────────────────────────────────
# In production, files are served from Cloudflare R2 (zero egress fees)
# In development, we serve them directly from FastAPI at /files/
if settings.is_development:
    uploads_dir = Path(settings.upload_dir)
    uploads_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/files", StaticFiles(directory=str(uploads_dir)), name="uploads")

# ── API Routers ───────────────────────────────────────────────────────────────
app.include_router(assessments.router)
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
        "name": "ScopeSnap API",
        "version": "0.1.0",
        "docs": "http://localhost:8000/docs",
        "health": "http://localhost:8000/health",
    }


# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    print(f"\n{'='*50}")
    print(f"  ScopeSnap API starting up")
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
            import sys
            sys.path.insert(0, "/app")
            from scripts.seed_pricing import seed_pricing
            await seed_pricing()
            print("✅ Pricing rules seeded successfully")
        else:
            print(f"✅ Pricing rules: {rule_count} rules loaded")
    except Exception as _seed_err:
        print(f"⚠️  Pricing rules seed failed (non-fatal): {_seed_err}")
