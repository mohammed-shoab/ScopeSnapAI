# SnapAI AI — Continuation Prompt

I'm working on a Next.js 14 / FastAPI / PostgreSQL app called SnapAI (AI-powered HVAC estimation tool) running via Docker Compose on Windows. The workspace is at `C:\Users\Shoab\Documents\Claude\Projects\SnapAIAI`. The app runs at `localhost:3000` (web), `localhost:8000` (API), `localhost:5432` (Postgres). Dev auth uses header `X-Dev-Clerk-User-Id: test_user_mike`.

## Current state after this session

### Bugs fixed
- ✅ **`$[object Object]` savings bug** — `energy_savings` is a dict `{annual_savings, five_year_savings, ...}`, not a number. Fixed in `/app/(app)/estimate/[id]/page.tsx` — added `EnergySavings` interface and safe extraction of `annual_savings`.
- ✅ **Markup PATCH infinite loop** — `updated_options.append(option)` inside `for option in updated_options` caused the list to grow forever. Removed the errant append in `/scopesnap-api/api/estimates.py`.
- ✅ **PDF "Failed to fetch"** — WeasyPrint import failure was crashing the ASGI connection without returning any HTTP response. Fixed with:
  1. Lazy import in try/except so a failed WeasyPrint import returns a proper HTTP 200 with `pdf_warning` field
  2. PDF errors no longer block the homeowner_report_url from being set, so the Send flow still works
- ✅ **Analytics 404** — Was "User not found" (404) because `test_user_mike` wasn't provisioned. The analytics error card now only shows "Owner/admin required" text when it's actually a 403.

### New pages built (all previously 404)
- ✅ `/intelligence/leaks` — **Profit Leaks** page: live analysis of pending estimates, stalled drafts, upsell gaps, low-margin jobs, slow send time. Fetches from `GET /api/estimates/`.
- ✅ `/intelligence/benchmark` — **BenchmarkIQ** stub with Phoenix Metro pricing comparison (preview data, live Q2 2026)
- ✅ `/intelligence/history` — **Property History** page, fetches from `GET /api/properties/`
- ✅ `/equipment/database` — Coming soon stub
- ✅ `/equipment/alerts` — Coming soon stub
- ✅ `/team/technicians` — Coming soon stub
- ✅ `/team/leaderboard` — Coming soon stub
- ✅ `/settings/pricing` — Coming soon stub
- ✅ `/settings/integrations` — Coming soon stub

### Seed data script
- Created `/scopesnap-api/scripts/seed_dev_data.py`
- Run with: `docker compose exec api python scripts/seed_dev_data.py`
- Seeds 8 recent properties + estimates at various funnel stages (deposit_paid, approved, viewed, sent, estimated) + 8 historical entries for 30-90 day trend charts
- Idempotent: skips if 5+ properties already exist

## Current state: APPROVED FOR BETA ✅

All 6 founder personas signed off. The comprehensive UX/UI audit is complete.
Sign-off document: `SnapAI_Beta_Readiness_SignOff.docx`

### To run seed data
```
docker compose exec api python scripts/seed_dev_data.py
```
Then refresh dashboard and analytics.

### Fixes applied (this session — post-gap-4 audit)
- ✅ **HealthGauge condition-responsive** — border/bg/text all dynamic from CONDITION_COLORS/CONDITION_BG. Was hardcoded tri-color.
- ✅ **Stripe text removed from approve button** — replaced with "Your contractor will contact you to confirm scheduling and payment details."
- ✅ **SidebarNav emoji icons → SVG** — 14 purpose-built inline SVG icons replace all emoji (Dashboard, Assessments, Analytics, etc.)
- ✅ **SidebarNav "Beta Plan" → "Free Trial"** — accurate label for beta users
- ✅ **Onboarding step counter fixed** — totalSteps=2, dot active on `step-1`, consistent with "Step 1 of 2" / "Step 2 of 2" labels

### Still to build (Phase 2 — not blocking beta)
- `/equipment/database` — Real equipment lookup from DB (needs equipment_models table populated)
- `/equipment/alerts` — Real aging alert logic (query equipment with install_year < now-12yr)
- `/team/technicians` — CRUD for team members (`GET/POST /api/teams/technicians`)
- `/team/leaderboard` — Stats per tech from estimates table
- `/settings/pricing` — Pricing rules editor (API: `GET/POST /api/pricing-rules/`)
- `/settings/integrations` — Webhooks/OAuth placeholder
- Stripe Checkout for homeowner deposit payment

### Known remaining items
1. WeasyPrint may still fail silently in Docker — run `docker compose exec api pip install weasyprint` and verify libpango/libcairo are present if PDF is needed
2. Dashboard KPIs will show 0 until seed script is run

## Key files
- `scopesnap-web/app/(app)/estimate/[id]/page.tsx` — Estimate Builder (energy_savings fix)
- `scopesnap-web/app/(app)/analytics/page.tsx` — Analytics (error message fix)
- `scopesnap-web/app/(app)/intelligence/leaks/page.tsx` — NEW: Profit Leaks page
- `scopesnap-web/app/(app)/intelligence/benchmark/page.tsx` — NEW: BenchmarkIQ stub
- `scopesnap-web/app/(app)/intelligence/history/page.tsx` — NEW: Property History
- `scopesnap-web/components/ComingSoonPage.tsx` — NEW: Reusable coming soon component
- `scopesnap-api/api/estimates.py` — Markup PATCH fix + PDF resilience
- `scopesnap-api/scripts/seed_dev_data.py` — NEW: Dev data seeder

---

## 🤖 Corrosion v4 AI Model Training (ACTIVE — April 2026)

### What is being trained
YOLOv8m binary corrosion detector (`corrosion_v4`) for SnapAI's HVAC inspection feature.
- **Model**: YOLOv8m, nc=1 (corrosion only), 640px, batch=16
- **Dataset**: 17,198 train images / 1,844 val images (Roboflow corrosion dataset, polygon→bbox fixed)
- **Training**: 112 epochs remaining (resumed from epoch 38 checkpoint after T4 crash on April 2 at ~2:24 AM PKT)
- **Total target**: 150 epochs (38 already completed in previous run)

### Colab notebook
- URL: `https://colab.research.google.com/drive/1qHGI-IhCKF2rMP8XAq1vx4ro1uH6J69g?authuser=1`
- **authuser=1 = ds.shoab@gmail.com** (ALWAYS use authuser=1, NOT authuser=0)
- authuser=0 = shoab@omnisecurityinc.com (WRONG account)

### Cell order (after a crash, re-run in this exact order)
1. **Cell 1** — pip install ultralytics roboflow + mount Drive → `/content/drive/MyDrive/SnapAIAI`
2. **Cell 2** — create directories in `/content/scopesnap_yolo`
3. **Cell 3** — download 3 Roboflow datasets (Rust 10.1k, Corrosion 9.2k, Mould 6.2k) to `/content/raw_*`
4. **Cell B** — build corrosion binary dataset with polygon→bbox fix → must print **"VERIFIED: Labels look good. Safe to run Cell C."**
5. **Cell C** — training cell (load checkpoint, train 112 epochs)

### Cell C — resume from checkpoint (ALWAYS use this after a crash)
```python
# Load from Drive checkpoint, NOT yolov8m.pt
CKPT_PATH = Path('/content/drive/MyDrive/SnapAIAI/last_corrosion_v4.pt')
model = YOLO(str(CKPT_PATH))
# Then train with remaining epochs (112 if crashed at epoch 38, adjust if crashed later)
results = model.train(epochs=112, ...)
```

### Drive checkpoints (ds.shoab@gmail.com Drive)
- `My Drive/SnapAIAI/last_corrosion_v4.pt` — saved after every epoch (~155 MB)
- `My Drive/SnapAIAI/best_corrosion_v4.pt` — best mAP checkpoint
- Check: `https://drive.google.com/drive/u/1/search?q=corrosion_v4`

### Automated monitoring (scheduled task)
- Task ID: `corrosion-v4-monitor`
- Runs every **10 minutes**
- **IMPORTANT**: Uses bash/Python FIRST (checks Drive for Desktop sync folder), browser only as fallback
- Root cause of previous failure: old monitor used browser as first step → hung when computer asleep → no checks ran for 7+ hours after 1:38 AM crash
- **Google Drive File Stream** installed at `C:\Program Files\Google\Drive File Stream\` — mounts as a VIRTUAL DRIVE LETTER (G:, H:, etc.), NOT a local folder. Files are streamed, not cached locally.
- Google Drive mounted as **G:** → checkpoint path is `G:\My Drive\SnapAIAI\last_corrosion_v4.pt`

### Key fixes from previous failures
- **v3 0% mAP bug**: Cell B was rejecting all polygon annotations (89–175 fields). Fixed with `poly_to_bbox()` conversion
- **Early stopping bug (v3)**: Used `patience=50`, stopped at epoch 36. Fixed with `patience=0`
- **Wrong lr (v3)**: Used `lr0=0.001`. Fixed to `lr0=0.01`
- **OOM bug**: Fixed with `cache='disk'` instead of RAM

### Training metrics (reference)
- Epoch 1/112 (= epoch 39 overall): box_loss~0.82, cls_loss~0.73, mAP50 expected ~0.78+
- Each epoch: ~11 minutes on T4 GPU
- Estimated completion: ~20 hours from start of Cell C

## Prototype files (for reference)
- `SnapAIAI/prototypes/SnapAI_Prototype_Demo.html`
- `SnapAI_Owner_Dashboard.html`
- `SnapAI_Homeowner_Report.html`
- Review report: `SnapAIAI/scopesnap-review-report.html`
