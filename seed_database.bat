@echo off
echo ============================================================
echo  ScopeSnap — Database Setup
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/2] Applying database migrations...
docker compose exec api alembic upgrade head
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Migration failed. Make sure Docker is running:
    echo   docker compose up -d
    pause
    exit /b 1
)

echo.
echo [2/2] Seeding equipment models and pricing data...
docker compose exec api python -m db.seeds.run_all_seeds
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Seed failed. Check the output above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Done! Your database is ready.
echo ============================================================
echo.
pause
