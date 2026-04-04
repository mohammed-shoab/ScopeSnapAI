# SCOPESNAP — BUILD CONTEXT FOR COWORK

## What Is SnapAI
An AI-powered HVAC equipment assessment and estimation tool. Technicians photograph equipment → AI identifies brand/model/condition → generates professional estimates (Good/Better/Best) → produces a visual homeowner report with annotated photos that closes deals. Built by Mainnov Tech (founder: Shoab, 12+ years data science, Pakistan-based, bootstrapped).

## Your Role
You are the developer building SnapAI. Follow the SOW work packages in sequence. Write production-quality code. Match the prototypes visually. Do not make product decisions — the Product Bible has those. Do not change the tech stack — the Technical Spec has that. Your job is to execute, not strategize.

## Document Hierarchy (Read in This Order)
1. **SnapAI_Build_SOW.html** — THE TASK LIST. 16 sequential work packages. Each has: what to build, acceptance criteria, dependencies, referenced docs. **START HERE for every coding session.**
2. **SnapAI_Product_Bible.html** — Product strategy, competitive intelligence, pricing, positioning. Read when you need WHY something is designed a certain way. Don't change product decisions.
3. **SnapAI_MVP_Technical_Spec.html** — Database schema (§02), API endpoints (§03), AI prompts (§04), estimate pipeline (§05), report architecture (§06), equipment DB (§07), file storage (§08), auth (§09), Stripe (§10), email (§11), build plan (§12). Section numbers are referenced in the SOW. **This is your implementation reference.**
4. **prototypes/** — HTML files showing what each screen looks like. Open in a browser. These are DESIGN TARGETS — match them as closely as possible.
   - `SnapAI_Prototype_Demo.html` — 9-screen mobile app for the HVAC technician
   - `SnapAI_Owner_Dashboard.html` — Laptop dashboard for the HVAC business owner
   - `SnapAI_Homeowner_Report.html` — The report homeowners receive (mobile + desktop + email/text notifications)

## How to Execute Work Packages
- Work on ONE work package at a time
- Read the full WP entry in the SOW before writing any code
- Read the referenced Tech Spec sections (e.g., "Tech Spec §04" means section 4 of 02_Technical_Spec.html)
- If the WP references a prototype, open it to see the visual target
- After completing a WP, verify ALL acceptance criteria before moving on
- If an acceptance criterion fails, fix it before starting the next WP
- Do NOT skip ahead to future WPs

## Tech Stack (Do Not Change)
- **Backend:** Python 3.12 + FastAPI (run locally with `uvicorn main:app --reload --port 8000`)
- **Frontend:** Next.js 14 + TypeScript + Tailwind CSS (run locally with `npm run dev`)
- **Database:** PostgreSQL 16 (local install or Docker, see Tech Spec §00)
- **ORM:** SQLAlchemy (async) + Alembic for migrations
- **AI Vision:** Google Gemini 2.5 Flash via `google-generativeai` Python SDK
- **File Storage:** Local folder `./uploads/` during development (swaps to Cloudflare R2 in production)
- **Auth:** Clerk (use development mode during local dev)
- **Payments:** Stripe (use test mode with card 4242424242424242)
- **Email:** Print to console during development (swaps to Resend in production)
- **PDF:** WeasyPrint (Python library — HTML template → PDF)

## Five Critical Rules

### Rule 1: Deterministic Over AI
Only use AI (Gemini API) for TWO things:
1. Equipment photo analysis (vision) — Tech Spec §04
2. 2-3 sentence homeowner explanation — Tech Spec §04

Everything else is math, SQL queries, and templates. NEVER call an LLM to calculate pricing, generate line items, fill templates, or do anything a formula can do. If you're importing `google.generativeai` anywhere outside of `services/vision.py`, you're doing it wrong.

### Rule 2: Service Abstractions from Day 1
Every external service must have two implementations behind one interface:

```python
# Storage
class LocalStorage:    # Development — saves to ./uploads/
class R2Storage:       # Production — saves to Cloudflare R2
storage = LocalStorage() if ENV == "development" else R2Storage()

# Email  
class ConsoleSender:   # Development — prints to terminal
class ResendSender:    # Production — sends via Resend API
sender = ConsoleSender() if ENV == "development" else ResendSender()
```

Switching from local to cloud must be a config change (.env), not a code rewrite.

### Rule 3: Database Schema Is Law
Use the EXACT schema from Tech Spec §02. Every column, every type, every constraint, every index. Do not:
- Simplify JSONB fields (they're designed for future features)
- Skip nullable columns (they'll be populated later)
- Change column names (the API layer depends on them)
- Omit indexes (they're there for query performance)

### Rule 4: The Homeowner Report Is the Product
The visual report homeowners receive (WP-06) is the #1 differentiator. It must:
- Match the prototype (`prototypes/Homeowner_Report.html`) as closely as possible
- Work perfectly on mobile (375px) AND desktop (1200px)
- Load in under 2 seconds (server-side rendered, minimal JS)
- Show the annotated equipment photo with animated SVG callouts
- Have selectable option cards that update the approve button dynamically
- Include 5-year cost comparison bars
- Work WITHOUT JavaScript (content visible, just options not selectable)

### Rule 5: Multi-Tenancy from Day 1
Every database query must be scoped to `company_id`. Use PostgreSQL Row Level Security (Tech Spec §02, indexes section). The middleware sets `app.current_company_id` on every request (Tech Spec §09). Never write a query without company scoping. The `equipment_models` table is the only exception — it's global (read-only for all companies).

## File Naming Convention
- Python files: `snake_case.py`
- TypeScript files: `camelCase.tsx` for components, `camelCase.ts` for utilities
- API routes: `/api/resource_name` (snake_case in URLs)
- Database tables: `snake_case` (plural: `estimates`, `assessments`, `companies`)

## When You're Stuck
- Check the Tech Spec section referenced in the SOW work package
- Check the prototype HTML file for visual clarity
- If a product question (pricing, features, positioning): check Product Bible
- If an architecture question (which table, which endpoint, which service): check Tech Spec
- If unclear, ask the user — don't guess on product decisions

## Lessons Learned (Add Mistakes Here)
When Cowork makes a mistake, add the fix here so it never happens again. Format: what went wrong → what to do instead.

<!-- Examples (replace with real mistakes as they happen):
- Wrong: Used LLM to calculate estimate totals → Fix: All pricing is math, never AI. Use SQL + arithmetic.
- Wrong: Forgot company_id in query, returned other company's data → Fix: Every query MUST filter by company_id. No exceptions.
- Wrong: Stored photos as base64 in database → Fix: Always store in filesystem/R2, save URL in database.
-->
