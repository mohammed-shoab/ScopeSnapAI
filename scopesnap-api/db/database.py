"""
SnapAI — Database Connection & Session Management
AsyncSession with SQLAlchemy 2.0 async engine.
Supports both PostgreSQL (production) and SQLite (local testing).
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text, event
from config import get_settings

settings = get_settings()

# ── Fix URL for async drivers ─────────────────────────────────────────────────
def get_async_url(url: str) -> str:
    """Ensure URL uses an async driver.

    asyncpg does not accept the libpq/psycopg2 'sslmode' query parameter.
    It uses 'ssl' instead. We normalise both here so either form of the
    connection string works without manual intervention.
    """
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("sqlite://"):
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)

    # Convert psycopg2-style sslmode → asyncpg-style ssl
    url = url.replace("sslmode=require", "ssl=require")
    url = url.replace("sslmode=verify-full", "ssl=require")
    url = url.replace("sslmode=verify-ca", "ssl=require")
    url = url.replace("sslmode=prefer", "ssl=prefer")
    url = url.replace("sslmode=disable", "ssl=disable")
    url = url.replace("sslmode=allow", "ssl=prefer")

    return url

async_url = get_async_url(settings.database_url)
is_sqlite = "sqlite" in async_url

# ── Engine ────────────────────────────────────────────────────────────────────
engine_kwargs = dict(echo=settings.is_development)
if not is_sqlite:
    # Supabase free-tier PgBouncer runs in session mode with a 15-connection
    # cap. Keep pool_size + max_overflow well under that limit to avoid
    # EMAXCONNSESSION errors when multiple Railway replicas are running.
    engine_kwargs.update(pool_size=3, max_overflow=7, pool_pre_ping=True)

engine = create_async_engine(async_url, **engine_kwargs)

# ── Session Factory ───────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# ── Base Class ────────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass

# ── Dependency ────────────────────────────────────────────────────────────────
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# ── Health Check ──────────────────────────────────────────────────────────────
async def check_db_connection() -> bool:
    try:
   