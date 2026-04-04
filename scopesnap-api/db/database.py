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
    """Ensure URL uses an async driver."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("sqlite://"):
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return url

async_url = get_async_url(settings.database_url)
is_sqlite = "sqlite" in async_url

# ── Engine ────────────────────────────────────────────────────────────────────
engine_kwargs = dict(echo=settings.is_development)
if not is_sqlite:
    engine_kwargs.update(pool_size=10, max_overflow=20, pool_pre_ping=True)

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
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"[DB] Connection check failed: {e}")
        return False
