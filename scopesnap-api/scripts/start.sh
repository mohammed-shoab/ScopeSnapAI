#!/bin/bash
# SnapAI API - Docker Startup Script
# Runs migrations then starts the server.
# Called by Dockerfile CMD.
# Environment variable ENVIRONMENT controls dev vs prod behaviour.

set -e

echo "=================================================="
echo "  SnapAI API - Starting up"
echo "  ENVIRONMENT=${ENVIRONMENT:-development}"
echo "  PORT=${PORT:-8000}"
echo "=================================================="

echo ""
echo "Initializing AI models (downloading from GitHub Releases if needed)..."
python /app/scripts/download_models.py
echo "AI models ready"

echo ""
echo "Running database migrations..."
alembic upgrade head
echo "Migrations complete"

echo ""
echo "Loading data repository (ac_data_repo.json v2.0)..."
PYTHONUNBUFFERED=1 python -u /app/scripts/load_repo.py || echo "Data repo load skipped (non-fatal - run manually if needed)"
echo "Data repo step complete"

echo ""
echo "Seeding equipment models (all 15 brands — skips existing rows)..."
PYTHONUNBUFFERED=1 python -u /app/scripts/seed_equipment_db.py || echo "Equipment seed skipped (non-fatal)"
PYTHONUNBUFFERED=1 python -u /app/scripts/seed_missing_brands.py || echo "Missing-brand seed skipped (non-fatal)"
echo "Equipment model seed complete"

echo ""
echo "Starting uvicorn..."

# Calculate workers: 2 x CPU cores + 1 (standard formula for async workers)
CPU_CORES=$(nproc --all 2>/dev/null || echo "1")
WORKERS=${UVICORN_WORKERS:-$((CPU_CORES * 2 + 1))}
PORT=${PORT:-8000}

if [ "${ENVIRONMENT}" = "production" ]; then
    echo "  Mode: PRODUCTION (${WORKERS} workers, no reload)"
    exec uv