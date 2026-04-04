# SnapAI AI

> **HVAC estimates in 90 seconds. No guessing. No spreadsheets.**

AI-powered assessment tool for HVAC contractors. Photograph any unit — SnapAI identifies the equipment, generates Good / Better / Best pricing, and sends the homeowner a beautiful report, all before you leave the driveway.

---

## 🌐 Live App

| Who | Link |
|---|---|
| **Homeowner** (report link) | `https://snapai.mainnov.tech/r/[slug]/[reportId]` — public, no login required |
| **Contractor** (sign in) | https://snapai.mainnov.tech |
| **Owner / Admin** | https://snapai.mainnov.tech/dashboard |

---

## 📋 Project Documents

| Document | Location | Description |
|---|---|---|
| **Beta Readiness Audit** | `SnapAI_Beta_Readiness_SignOff.docx` | Full 6-founder UX/UI audit with sign-offs — Phase 1 + Phase 2 findings |
| **Tech Stack** | `TECH_STACK.md` | Complete architecture, env vars, API endpoints, repo structure |

---

## ✅ Beta Status

**Phase 1 + Phase 2 audits complete. All 6 founders signed off.**

### Phase 1 Fixes (committed `95417d4`)
- HealthGauge now responds to equipment condition (good/fair/poor/critical)
- Homeowner report: Stripe text removed, replaced with accurate follow-up copy
- Sidebar navigation: 14 professional SVG icons replacing all emoji
- Onboarding: step counter fixed (Step 1 of 2 / Step 2 of 2)
- Dashboard: HVAC illustration in empty state
- Privacy & Data settings page built out
- Event tracking, offline queue, feature flags, data confidence label

### Phase 2 Fixes (committed `cce91b4`)
- Homeowner report: "Your AC:" label is now dynamic — uses actual equipment_type from AI
- Homeowner report: 📞/💬 emoji call/text buttons replaced with clean SVG icons
- Branded 404 page — replaces plain Next.js default

### Before Open Beta Signup
- [ ] Switch Clerk from Development → Production mode
- [ ] Replace dev auth header with real Clerk JWT token in API calls
- [ ] Stripe Checkout wiring

---

## 🏗 Stack

- **Frontend:** Next.js 14 (App Router) + TypeScript + Tailwind CSS → Vercel
- **Backend:** FastAPI (Python) + PostgreSQL → Railway
- **AI:** Google Gemini 2.5 Flash (vision)
- **Auth:** Clerk
- **Storage:** Cloudflare R2
- **Email:** Resend
- **Payments:** Stripe (feature-flagged for beta)

→ Full details in [`TECH_STACK.md`](./TECH_STACK.md)

---

## 🚀 Deploying Changes

```bash
# From Windows Git Bash in this folder:
git add <files>
git commit -m "your message"
git push origin main
# Vercel auto-deploys frontend in ~90 seconds
# Railway auto-deploys API from scopesnap-api/ subdirectory
```
