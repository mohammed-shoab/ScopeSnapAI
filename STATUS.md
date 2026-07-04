# SnapAI — Current Live State

**As of:** 2026-07-06
**Live prod:** https://snapai.mainnov.tech (US) · https://pk.snapai.mainnov.tech (PK, dormant per DEC-123)
**Alembic head:** 034 (verify via live Supabase per DEC-129)
**Latest DEC:** DEC-129
**Boards:** @board + @nav standing on (all SnapAI chats)

---

## Current focus (4 active workstreams)

1. **Legal cover + wordings update** — remediating v2 deep audit findings (LLM prompt rewrites `cascade_prompts.py` + `homeowner_narrative.py`, ToS deployment at `/tos`, homeowner-page rewrite for DTPA §17.42 compliance, PDF template disclaimer block, in-app Output disclaimer). Owner: Shoab + Alfred (legal chat).
2. **Adding new complaint cards** — Tier A per Bryan's proposal (Cards #20 Under-Airflow, #22 Latent Deficit, #23 Thermostat, #24 Oversizing + Airflow Assessment sub-flow + Comfort Complaint tab J + superheat/subcool discrimination on Card #8). Owner: Shoab + Bryan (product chat).
3. **Brain files cleanup + future system** — active this session, per `SnapAI_Brain_Files_Management_Plan_2026-07-05.md`. Owner: Shoab + Karpathy/Rob.
4. **TikTok video marketing** — upcoming, not yet scoped. Owner: Shoab + Azhan.

## Open blockers

1. Texas SaaS attorney engagement pending (Baker Botts / Winstead / Jackson Walker — not yet contacted).
2. Tech E&O insurance broker quotes pending (Hiscox / Founder Shield / Vouch — not yet contacted).
3. Tier A start date not yet formally committed (waiting on legal chat's Layer 1-4 landing first).
4. TikTok workstream not yet scoped (owner, tools, budget TBD).
5. Card #21 Heat Exchanger = Tier D indefinite hold (6 gates must clear — legal chat).

## Recent milestones (last 7 days)

- **2026-07-06 (later):** Brain files Phase 2 + Phase 3 executed — router updated, pre-commit hook, weekly audit scheduled, session log pattern adopted. Full deep narrative: `session_logs/SESSION_LOG_2026-07-06_brain_files_cleanup.md`.
- **2026-07-06:** Brain files Commits 1-3 executed (DECISIONS.md em-dash sweep 54 headers, WORKFLOW.md Section 1 rewrite, MARKET_GUIDE.md DEC-123 banner).
- **2026-07-05:** v7 branching diagnostic tree HTML built (`SnapAI_Decision_Tree_v7_full_diagram.html`).
- **2026-07-05:** Deep legal audit v2 completed — 12 Critical + 11 High findings across LLM prompts, DB schema, PDF template, homeowner emails.
- **2026-07-05:** Legal + product chat handoffs prepared (verbatim transcripts + continuation prompts saved to `ScopeSnapAI/`).
- **2026-07-05:** Brain files audit + management plan drafted (`SnapAI_Brain_and_Tree_Audit_2026-07-05.md`, `SnapAI_Brain_Files_Management_Plan_2026-07-05.md`).
- **2026-07-05:** Brain files backup created at `_brain_backup_2026-07-06/` (12 files, SHA-256 verified).

## Key files (pointers, not content — see PROJECT_BRAIN.md for architecture facts)

- CRITICAL RULES table: PROJECT_BRAIN.md first 20 lines
- Legal continuation: `SnapAI_Legal_Discussion_Continuation_Prompt.md`
- Product continuation: `SnapAI_Product_Discussion_Continuation_Prompt.md`
- Brain files plan: `SnapAI_Brain_Files_Management_Plan_2026-07-05.md`

## Auto-updated

Last modified: 2026-07-06 by Cowork session (brain files cleanup Phase 1)
