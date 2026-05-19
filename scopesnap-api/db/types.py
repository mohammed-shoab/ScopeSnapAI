"""
Database-agnostic type helpers.
In production (PostgreSQL): uses JSONB, ARRAY, UUID for best performance.
In testing (SQLite): uses JSON, Text, String as fallbacks.
"""
import os
from sqlalchemy import JSON, Text, String
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB, ARRAY as PG_ARRAY, UUID as PG_UUID

DATABASE_URL = os.getenv("DATABASE_URL", "")
IS_POSTGRES = "postgresql" in DATABASE_URL or "asyncpg" in DATABASE_URL

# Use PostgreSQL-native types in production, generic types for SQLite testing
SmartJSON = PG_JSONB if IS_POSTGRES else JSON
SmartUUID = PG_UUID(as_uuid=False) if IS_POSTGRES else String(36)

def SmartArray(item_type=Text):
    return PG_ARRAY(item_type) if IS_POSTGRES else JSON
