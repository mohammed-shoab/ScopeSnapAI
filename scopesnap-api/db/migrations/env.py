"""
Alembic Environment Configuration for ScopeSnap.
Reads DATABASE_URL from .env file (via config.py).
Supports both sync and async database URLs.
"""

import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import get_settings
from db.database import Base

# Import ALL models so Alembic can detect them for autogenerate
from db.models import (
    Company, User, Property, EquipmentModel, EquipmentInstance,
    Assessment, AssessmentPhoto, Estimate, EstimateLineItem,
    EstimateDocument, PricingRule, FollowUp
)

settings = get_settings()

# Alembic Config
config = context.config

# Inject our DATABASE_URL from settings (overrides alembic.ini placeholder)
# Convert async URL to sync for Alembic (asyncpg → psycopg2)
sync_url = settings.database_url.replace(
    "postgresql+asyncpg://", "postgresql://"
).replace(
    "postgresql+aiosqlite://", "sqlite:///"
)
config.set_main_option("sqlalchemy.url", sync_url)

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    Generates SQL scripts without connecting to the database.
    Useful for reviewing what will be executed.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    Connects to the database and runs migrations directly.
    This is the mode used when running: alembic upgrade head
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
