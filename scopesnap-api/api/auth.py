"""
SnapAI — Clerk JWT Authentication Middleware
Verifies Clerk session tokens and extracts company + user context.

In local dev mode (ENVIRONMENT=development), you can bypass auth for testing
by passing X-Dev-Company-Id and X-Dev-User-Id headers.
"""

from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import time
import httpx
from jose import jwt as jose_jwt, JWTError

from db.database import get_db
from db.models import User, Company
from config import get_settings

settings = get_settings()
security = HTTPBearer(auto_error=False)

# ── JWKS Cache (avoid fetching on every request) ───────────────────────────────
_jwks_cache: Optional[dict] = None
_jwks_cache_time: float = 0.0
_JWKS_CACHE_TTL: float = 3600.0  # 1 hour


async def _get_clerk_jwks() -> dict:
    """Fetches and caches Clerk's JWKS public keys."""
    global _jwks_cache, _jwks_cache_time
    if _jwks_cache and (time.time() - _jwks_cache_time) < _JWKS_CACHE_TTL:
        return _jwks_cache
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.clerk.com/v1/jwks",
            headers={"Authorization": f"Bearer {settings.clerk_secret_key}"},
            timeout=10.0,
        )
    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not fetch Clerk JWKS — check CLERK_SECRET_KEY",
        )
    _jwks_cache = resp.json()
    _jwks_cache_time = time.time()
    return _jwks_cache


# ── Auth Context Data Classes ──────────────────────────────────────────────────
class AuthContext:
    """
    Holds the verified identity of the current API request.
    Injected into route handlers via FastAPI dependency injection.
    """
    def __init__(self, user: User, company: Company):
        self.user = user
        self.company = company
        self.user_id = user.id
        self.company_id = company.id
        self.role = user.role
        self.is_owner = user.role == "owner"
        self.is_admin = user.role in ("owner", "admin")


# ── Token Verification ────────────────────────────────────────────────────────
async def verify_clerk_token(token: str) -> dict:
    """
    Verifies a Clerk JWT using JWKS public-key verification.
    Replaces the broken /sessions/me approach — JWTs must be verified via JWKS.
    """
    if not settings.clerk_secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clerk secret key not configured on server",
        )

    # Get unverified header to find the key ID
    try:
        header = jose_jwt.get_unverified_header(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
        )

    kid = header.get("kid")

    # Fetch JWKS (cached)
    jwks = await _get_clerk_jwks()
    keys = jwks.get("keys", [])

    # Find the matching public key by kid
    key_data = next((k for k in keys if k.get("kid") == kid), None)
    if not key_data and keys:
        key_data = keys[0]  # Fallback: use first key if no kid match
    if not key_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signing key not found in Clerk JWKS",
        )

    # Verify and decode the JWT
    try:
        claims = jose_jwt.decode(
            token,
            key_data,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        return claims
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
        )


# ── Main Auth Dependency ───────────────────────────────────────────────────────
async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> AuthContext:
    """
    FastAPI dependency that verifies the Clerk JWT and returns AuthContext.

    Development shortcut: Skip actual Clerk verification by passing:
      X-Dev-Clerk-User-Id: clerk_user_id_here
    Only works when ENVIRONMENT=development.

    Usage in routes:
        @router.get("/endpoint")
        async def my_endpoint(auth: AuthContext = Depends(get_current_user)):
            user = auth.user
            company = auth.company
    """
    # ── DEV BYPASS (local development only) ───────────────────────────────────
    if settings.is_development:
        dev_clerk_user_id = request.headers.get("X-Dev-Clerk-User-Id")
        if dev_clerk_user_id:
            return await _load_auth_context(dev_clerk_user_id, db)

    # ── PRODUCTION: Verify Clerk JWT ──────────────────────────────────────────
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    claims = await verify_clerk_token(credentials.credentials)
    clerk_user_id = claims.get("user_id") or claims.get("sub")

    if not clerk_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not extract user ID from token",
        )

    return await _load_auth_context(clerk_user_id, db)


async def _load_auth_context(clerk_user_id: str, db: AsyncSession) -> AuthContext:
    """Loads user and company from DB given a Clerk user ID."""
    # Find user by Clerk ID
    result = await db.execute(
        select(User).where(User.clerk_user_id == clerk_user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found. Please complete registration. (Clerk ID: {clerk_user_id})",
        )

    # Load company
    result = await db.execute(
        select(Company).where(Company.id == user.company_id)
    )
    company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found for this user.",
        )

    return AuthContext(user=user, company=company)


# ── Role Guards ───────────────────────────────────────────────────────────────
async def require_owner(auth: AuthContext = Depends(get_current_user)) -> AuthContext:
    """Only company owners can access this endpoint."""
    if not auth.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner access required.",
        )
    return auth


async def require_admin(auth: AuthContext = Depends(get_current_user)) -> AuthContext:
    """Company owners and admins can access this endpoint."""
    if not auth.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return auth
