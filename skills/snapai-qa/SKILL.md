---
name: snapai-qa
description: >
  End-to-end QA skill for the SnapAI HVAC diagnostic app. ALWAYS trigger
  this skill when the user asks to run QA, test the app, check if something
  is working, verify a fix is live, or do a post-deployment check on either
  the Houston market (snapai.mainnov.tech) or the PK market
  (pk.snapai.mainnov.tech) or both. Also trigger for phrases like "test
  this", "check if it works", "is it live yet", "verify the fix", "run
  through the flows", "QA this", "check the app". Runs a full cycle: UI
  click-through testing, backend health checks, bug fixing, deployment
  monitoring (waits until Vercel and Railway are confirmed live), live
  verification in the app, QA sign-off, retrospective, and PROJECT_BRAIN
  file updates. Does NOT stop until every step is confirmed complete.
---

# SnapAI QA Skill

You are running a full end-to-end QA cycle for the SnapAI HVAC diagnostic app. This is a **blocking workflow** — do not stop, summarise, or declare QA complete until every phase below has passed. If you find bugs, fix them, deploy, and re-verify before moving on.

---

## Phase 0 — Read the Project State

Before touching the app, ground yourself in the current reality.

1. Read PROJECT_BRAIN.md from the ProjectBrain folder. Extract:
   - Live URLs for Houston and PK markets
   - Railway project IDs and health endpoint
   - Vercel project details
   - Current Alembic migration version
   - Any known issues or in-progress tasks

2. Read ACTIVE_TASKS.md to see what was last worked on.

3. Read DECISIONS.md — note deployment constraints (DEC-005 emoji files, DEC-006 dual-market routing).

---

## Phase 1 — UI Click-Through Testing

Use browser tools to navigate the live app. Test **both markets** unless the user specifies only one.

### URLs
- Houston: https://snapai.mainnov.tech
- PK: https://pk.snapai.mainnov.tech

### Flow 1 — Not Cooling (core diagnostic)
1. Open app, confirm landing loads without errors
2. Log in or confirm already authenticated
3. Select brand + series (York LX for Houston, Gree Pular for PK)
4. Select tonnage — verify ALL spec fields auto-fill: Tonnage, Refrigerant, RLA, LRA, CAP uF, MCA, MOCP
5. Auto-filled fields must appear dimmed/grey with "DB" badge. Blank fields must be white with active cursor.
6. Select complaint: Not Cooling
7. Enter suction PSI:
   - Houston R-410A: 128 PSI must route to NORMAL (not high)
   - PK R-410A: 130 PSI must route to NORMAL and NOT go to Dirty Coil Card 13
8. Enter discharge PSI if prompted
9. Confirm fault card returned with correct currency (USD Houston / PKR Pakistan)

### Flow 2 — Service / Tune-Up
1. New assessment, any brand/series/tonnage
2. Complaint: Service/Tune-Up
3. Flow must complete without 503 error
4. Estimate must be generated

### Flow 3 — Water Dripping
1. New assessment, complaint: Water Dripping
2. Enter PSI values when prompted
3. Flow must complete without 404 or crash
4. Fault card must be returned

### Flow 4 — Not Turning On (voltage / contactor)
1. New assessment, complaint: Not Turning On
2. Enter normal voltage:
   - Houston: 230V must proceed normally
   - PK: 220V must proceed normally
3. Fault card must be returned

### Flow 5 — PK-Specific (PK only)
1. WhatsApp button: Send tab on any assessment must read "Send via WhatsApp" NOT "Send via Email"
2. Placeholder name: customer name field must show "Ahmed Khan" NOT "Sarah Johnson"
3. 2.5T warning: select any brand then 2.5T tonnage — commercial warning banner must appear
4. Urdu toggle: button must be present and tappable
5. Inverter badge: select Gree Fairy Inverter — inverter badge must appear

### Flow 6 — Nameplate Screen Editing
1. Select brand/series with DB data
2. Tap any auto-filled field — cursor must activate inline (no modal)
3. Change a value — badge must change from "DB" to pencil+Edited
4. Confirm no bulk-clear button exists

### Record for each flow:
- PASS or FAIL
- If FAIL: URL, what was clicked, what was seen, what was expected

---

## Phase 2 — Backend Health Checks

### 2a — Railway health
GET /health on the Railway backend URL
Expected: {"status": "ok"} HTTP 200
If non-200: check Railway dashboard build logs immediately

### 2b — Market routing
GET /api/brands with X-Market: US header — expect Houston brands
GET /api/brands with X-Market: PK header — expect Pakistan brands (Gree, Dawlance, Orient, etc.)

### 2c — Supabase connectivity
GET /api/series?brand=york (X-Market: US) — must return data
GET /api/series?brand=gree (X-Market: PK) — must return data

### 2d — PK PSI threshold validation
Confirm pak_diagnostic_questions thresholds are correct:
- R-410A high_min: 145 (not 125)
- R-22 high_min: 88
- R-32 high_min: 140
If wrong, apply the SQL patch from PK SOW Addendum Section A-2 now.

---

## Phase 3 — Bug Fixing

Fix every failure from Phase 1 and 2 before proceeding. Do not skip to deployment with known failures.

### Rules:
- PK-only bugs: gate behind detectMarket() === "PK". Never change Houston behaviour.
- Universal bugs (same on both markets): fix without a gate.
- DB fixes: apply SQL via Supabase SQL editor. Log exact SQL run.
- Emoji files: NEVER read from NTFS mount during git ops. Use git cat-file blob <sha> method (DEC-005).
- Alembic: current version 011. If migration needed, it must be 012.

### Log each fix:
  FIX: [component] — [description]
  File: [path]
  Change: [what and why]
  Market: [Houston / PK / Both]

---

## Phase 4 — Deploy and Wait

### Push
```
git add -A
git commit -m "fix: [description]"
git push origin main
```

### Wait for Railway (poll every 30 seconds, max 10 minutes)
Keep hitting GET /health until you get {"status": "ok"} on the NEW deployment.
Confirm it is new by checking the deployment ID in response headers or Railway dashboard.
DO NOT proceed until Railway is confirmed live on the new build.
If Railway build fails: check logs, fix the error, push again, restart the wait.

### Wait for Vercel (poll every 30 seconds, max 8 minutes)
Poll both https://snapai.mainnov.tech and https://pk.snapai.mainnov.tech.
Compare X-Vercel-Deployment-Id header before and after push to confirm new code is serving.
DO NOT proceed until both URLs show the new deployment.
If Vercel build fails: check Vercel dashboard build logs, fix, push again.

---

## Phase 5 — Live Verification

After Railway and Vercel confirm the new deployment:
1. Re-run every flow that failed in Phase 1
2. Spot-check at least one flow that was already passing — confirm no regressions
3. If a fix is still broken: hard-refresh (or incognito), verify deployment ID changed, return to Phase 3 if needed

---

## Phase 6 — QA Sign-Off

Only announce "QA COMPLETE" when ALL of the following are true:
- All Phase 1 flows PASS on all markets tested
- All Phase 2 backend checks PASS
- All bugs found are fixed and confirmed live
- Railway returns health OK on the new deployment
- Both Vercel URLs serve the new deployment
- Phase 5 live verification confirms fixes work in the real app

Produce this summary:
```
QA Summary — [date]
Markets tested: [Houston / PK / Both]

Flows:
  Flow 1 Not Cooling: PASS/FAIL
  Flow 2 Service/Tune-Up: PASS/FAIL
  Flow 3 Water Dripping: PASS/FAIL
  Flow 4 Not Turning On: PASS/FAIL
  Flow 5 PK-Specific: PASS/FAIL (PK only)
  Flow 6 Nameplate editing: PASS/FAIL

Bugs found: [list each: component, symptom, root cause]

Fixes applied: [list each: file, change, market]

Deployment:
  Git commit: [hash]
  Railway: [confirmed live]
  Vercel Houston: [confirmed live]
  Vercel PK: [confirmed live]

Status: QA COMPLETE
```

---

## Phase 7 — Retrospective

Ask the user:

"QA is done and everything is live. Before I update the project files, a few quick questions:

1. What worked well in this QA run?
2. What surprised you or didn't work as expected?
3. How did we find the root cause of any bugs — what clues led us there?
4. Anything to change about how we run QA next time?

I'll use your answers to update PROJECT_BRAIN.md, DECISIONS.md, and ACTIVE_TASKS.md."

Wait for the user's answers. Do not update brain files before receiving them.

---

## Phase 8 — Update Project Brain Files

Use the QA summary and retrospective answers to update all three files.

### ACTIVE_TASKS.md
- Mark tasks verified live as [completed]
- Add newly discovered bugs as [in_progress] or [backlog]
- Add or update "Last QA run" line: date, markets tested, outcome, bugs fixed count

### DECISIONS.md
- If a new workaround or architectural decision was made, add a DEC-### entry:
  DEC-###: [date] — [title]
  Problem: [what was wrong]
  Solution: [what was done]
  Rationale: [why this approach]

### PROJECT_BRAIN.md
- Remove fixed issues from "Current known issues"
- Update deployment details if anything changed
- Add to QA History section (create it if missing):
    [date]: [markets] — [outcome] — [bugs fixed]
- If tech stack changed (new env var, new table, schema change), update that section

After all updates, confirm:
"Project Brain files updated. Changes: [brief summary of what was added or modified in each file]."

---

## SnapAI Architecture Reference

- Single codebase, dual market: one git push deploys Houston AND PK at once
- Market detection: detectMarket() reads hostname → X-Market header → backend get_tables() routes to pak_* tables
- Database: Supabase (NOT Railway). PK tables prefixed pak_. SQL patches via Supabase SQL editor.
- Backend: Railway (FastAPI). Health endpoint: GET /health returns {"status":"ok"}
- Frontend: Vercel (Next.js). Two domains, one deployment.
- PK tables: pak_brands, pak_fault_cards, pak_diagnostic_questions, pak_operating_targets, pak_data_defaults, pak_assessments, pak_estimates
- Emoji files: NEVER read from NTFS mount in git operations. Use git cat-file blob <sha> (DEC-005).
- Alembic: current 011. Next migration must be 012.
- Currency: Houston = USD, PK = PKR
- PK voltage: 220-240V / 50Hz single phase (not Houston 208/240V)
- R-410A normal suction at 40C ambient: 125-145 PSI
- R-22 normal suction at 40C ambient: 65-88 PSI
- R-32 normal suction at 40C ambient: 120-140 PSI
