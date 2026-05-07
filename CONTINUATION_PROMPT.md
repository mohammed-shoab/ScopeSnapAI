# SnapAI — Continuation Prompt

Last updated: 2026-05-07 (Phase 3 QA Complete)

## Production Environment

- **App URL**: https://snapai.mainnov.tech
- **Frontend**: Next.js 14 deployed on Vercel (project: scope-snap-ai)
- **Backend API**: FastAPI + PostgreSQL (Railway)
- **Auth**: Clerk (production keys, live)
- **Analytics**: PostHog (project 369878, host https://us.i.posthog.com, token phc_A5spSAWCWKeQw9cVgVfxnmNd2f2dQjvtdwsb9PpjMbZJ)
- **Monitoring**: UptimeRobot
- **Repo**: mohammed-shoab/ScopeSnapAI (monorepo)
  - scopesnap-web/ — Next.js frontend
  - scopesnap-api/ — FastAPI backend

## Current Phase: EARLY ACCESS

App is live in production. Phase 3 QA fully complete as of 2026-05-07.

---

## Phase 3 QA — Completed

### Bugs Fixed

**BUG-004** — not_heating auto Q1 crashes on null OCR data
- File: scopesnap-api (not_heating branch logic)
- Fix: Null-safe checks for OCR data before auto-populating Q1

**BUG-005** — error_code branch crashes on null OCR brand
- File: scopesnap-api (error_code branch handler)
- Fix: Fallback for null brand in error_code_lookup call

**BUG-006** — DiagnosticFlow.handleMulti missing visual_select support
- File: scopesnap-web/components/diagnostic/DiagnosticFlow.tsx
- Symptom: visual_select questions (YES/NO big buttons) did not render
- Fix: Added visual_select case to handleMulti

**BUG-014** — Intermittent Shutdown card broken emoji
- File: scopesnap-web/app/(app)/assess/page.tsx
- Symptom: Lightning bolt rendered as replacement character on Windows/NTFS (null-byte padding)
- Fix: Replaced with clean UTF-8 U+26A1, stripped null-byte padding

### UI Improvements

**EARLY ACCESS badge** — Replaced all BETA text with EARLY ACCESS across:
- app/(app)/layout.tsx (sidebar)
- app/page.tsx (landing page header + hero)
- components/ui/sidebar.tsx

**Landing page copy** — Updated to 90-second messaging:
- Headline: HVAC estimates in 90 seconds. No guessing. No spreadsheets.
- CTA: Start Your First Assessment and See How It Works

**Video embed placeholder** — iframe added in page.tsx under See it in action
- src: https://www.youtube.com/embed/SNAPAI_VIDEO_ID?autoplay=1
- Replace SNAPAI_VIDEO_ID with real YouTube ID when demo video is recorded

### PostHog Tracking Added (Task 12)

Three custom events via posthog.capture():

1. diagnostic_started (assess/page.tsx) — props: complaint_type
2. estimate_generated (assess/page.tsx) — props: estimate_id, amount
3. diagnostic_step_answered (DiagnosticFlow.tsx) — props: question (hint_text), answer, complaint_type

Import: import posthog from 'posthog-js'
PostHog initialized via PostHogProvider in providers/posthog-provider.tsx.
NOTE: Browser ad blockers block outgoing requests to us.i.posthog.com — use incognito to verify in Live Events.

### Key Commits (Phase 3)

- c8e38fb — feat: add PostHog tracking to assess/page.tsx
- 8317f9f — fix(tracking): use hint_text as question identifier in diagnostic_step_answered
- 6fb1298 — fix(BUG-018): strip null-byte padding from app/page.tsx

---

## Known Minor Issues (Non-blocking)

- Beta Feedback floating button — bottom-right widget still says Beta Feedback. Low priority cosmetic.
- Video embed — shows broken icon because SNAPAI_VIDEO_ID is a placeholder. Replace when demo is recorded.
- PostHog Live Events — only visible with ad blocker disabled. Code is correct.

---

## Architecture Notes

### Frontend Key Files

- assess/page.tsx — Assessment flow, complaint picker, Step Zero nameplate
- components/diagnostic/DiagnosticFlow.tsx — Diagnostic UI, all question types
- app/page.tsx — Public landing page
- app/(app)/layout.tsx — App shell with EARLY ACCESS sidebar
- lib/tracking.ts — Internal event tracking (posts to /api/events only, NOT PostHog)
- providers/posthog-provider.tsx — PostHogProvider wrapper

### PostHog Integration

- posthog-js React integration via PostHogProvider
- Does NOT set window.posthog (unlike snippet method)
- Call posthog.capture() directly, not window.posthog.capture()
- NEXT_PUBLIC_POSTHOG_KEY and NEXT_PUBLIC_POSTHOG_HOST set in Vercel env vars

### Diagnostic Question Types (DiagnosticFlow.tsx)

- multiple_choice — dark pill option buttons
- visual_select — large YES (green) / NO (red) buttons
- photo — camera/upload slot with AI evaluation
- number — numeric input with unit label
- multi_input — multiple fields (photo + readings) on same step

### QuestionOut TypeScript Interface

Fields: hint_text, options, icon — NO id field.
Use hint_text as question identifier in PostHog events.

---

## Corrosion v4 Model Training

YOLOv8m binary corrosion detector for HVAC inspection feature.
- Colab: https://colab.research.google.com/drive/1qHGI-IhCKF2rMP8XAq1vx4ro1uH6J69g?authuser=1
- authuser=1 = ds.shoab@gmail.com (ALWAYS — authuser=0 is wrong account)
- Checkpoints: G:\My Drive\SnapAIAI\last_corrosion_v4.pt and best_corrosion_v4.pt

Cell run order after crash:
1. Cell 1 — pip install + mount Drive
2. Cell 2 — create dirs
3. Cell 3 — download datasets
4. Cell B — build binary dataset (must print VERIFIED)
5. Cell C — train from checkpoint (load last_corrosion_v4.pt, NOT yolov8m.pt)

---

## Prototypes

- ScopeSnapAI/prototypes/SnapAI_Prototype_Demo.html
- ScopeSnapAI/prototypes/SnapAI_Owner_Dashboard.html
- ScopeSnapAI/prototypes/SnapAI_Homeowner_Report.html
