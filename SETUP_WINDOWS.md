# SnapAI — Windows Setup Guide (WP-01)

Run these commands in **Windows PowerShell** or **Command Prompt**.
Everything installs locally — no cloud accounts, no credit card needed yet.

---

## Step 1: Install PostgreSQL

**Option A — Docker Desktop (Recommended)**

1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
2. Install and start Docker Desktop
3. Open PowerShell and run:

```powershell
docker run -d --name scopesnap-db `
  -e POSTGRES_DB=scopesnap_dev `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_PASSWORD=devpass `
  -p 5432:5432 `
  postgres:16

# Verify it's running:
docker ps
```

**Option B — PostgreSQL Installer**

1. Download from https://www.postgresql.org/download/windows/
2. Install with default settings, password: `devpass`
3. Open pgAdmin or psql and create database:
```sql
CREATE DATABASE scopesnap_dev;
```

---

## Step 2: Set Up Python Backend

```powershell
# Navigate to the backend folder
cd path\to\SnapAIAI\scopesnap-api

# Create virtual environment
python -m venv venv

# Activate it (PowerShell)
venv\Scripts\Activate.ps1

# If you get a permissions error, run first:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env

# Edit .env — the defaults work for local dev (no changes needed yet)
# If using Docker Option A: DATABASE_URL=postgresql+asyncpg://postgres:devpass@localhost:5432/scopesnap_dev
# If using installer Option B: adjust password if you set a different one
notepad .env
```

---

## Step 3: Run Database Migrations

```powershell
# Make sure your venv is activated (you'll see (venv) in the prompt)
# Make sure PostgreSQL/Docker is running

# Run Alembic migration — creates all 12 tables
alembic upgrade head

# Verify tables were created:
# If using Docker:
docker exec -it scopesnap-db psql -U postgres -d scopesnap_dev -c "\dt"

# You should see: companies, users, properties, equipment_models,
# equipment_instances, assessments, assessment_photos, estimates,
# estimate_line_items, estimate_documents, pricing_rules, follow_ups
```

---

## Step 4: Start the Backend API

```powershell
# From scopesnap-api/ with venv activated:
uvicorn main:app --reload --port 8000

# You should see:
# ==================================================
#   SnapAI API starting up
#   Environment: development
#   Storage: LocalStorage → ./uploads
#   Email: ConsoleSender (emails printed to terminal)
#   API Docs: http://localhost:8000/docs
# ==================================================
# ✅ Database connection: OK
```

**Verify it works:**
- Open browser: http://localhost:8000/health
- You should see: `{"status": "ok", "db": "connected", ...}`
- API Docs: http://localhost:8000/docs

---

## Step 5: Set Up Next.js Frontend

```powershell
# Open a NEW PowerShell window (keep backend running)
cd path\to\SnapAIAI\scopesnap-web

# Install dependencies (first time takes 1-2 minutes)
npm install

# Copy environment file
copy .env.local.example .env.local

# Start the frontend dev server
npm run dev
```

**Verify it works:**
- Open browser: http://localhost:3000
- You should see the SnapAI landing page

---

## Step 6: Get Your Gemini API Key (Free)

1. Go to https://ai.google.dev
2. Click "Get API Key" → "Create API key in new project"
3. Copy the key (no credit card needed — 1,000 requests/day free)
4. Add it to `scopesnap-api\.env`:
   ```
   GEMINI_API_KEY=AIza...your_key_here
   ```
5. Restart the backend: `uvicorn main:app --reload --port 8000`

You'll need this for **WP-02** (photo analysis). WP-01 works without it.

---

## WP-01 Acceptance Checklist

Run through these to confirm WP-01 is complete:

- [ ] `uvicorn main:app --reload` starts without errors on localhost:8000
- [ ] `npm run dev` starts without errors on localhost:3000
- [ ] `GET http://localhost:8000/health` returns `{"status": "ok", "db": "connected"}`
- [ ] All 12 database tables exist (verify with `\dt` in psql or Docker exec above)
- [ ] `alembic upgrade head` ran cleanly
- [ ] `.env` has all required variables documented
- [ ] LocalStorage saves files to `./uploads/` folder

**Once all checkboxes pass → ready for WP-02!**

---

## Daily Workflow (After Setup)

```powershell
# Terminal 1: Start database (if using Docker)
docker start scopesnap-db

# Terminal 2: Start backend
cd path\to\SnapAIAI\scopesnap-api
venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000

# Terminal 3: Start frontend
cd path\to\SnapAIAI\scopesnap-web
npm run dev
```

---

## Troubleshooting

**"Cannot connect to database"**
- Check Docker is running: `docker ps` (should show scopesnap-db)
- Or start it: `docker start scopesnap-db`
- Check DATABASE_URL in `.env` matches your setup

**"Module not found" errors**
- Make sure venv is activated: `venv\Scripts\Activate.ps1`
- Try: `pip install -r requirements.txt` again

**"Port 8000 already in use"**
- Find what's using it: `netstat -ano | findstr :8000`
- Or run on a different port: `uvicorn main:app --reload --port 8001`
- Update `NEXT_PUBLIC_API_URL` in `scopesnap-web\.env.local` accordingly

**PowerShell execution policy error**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
