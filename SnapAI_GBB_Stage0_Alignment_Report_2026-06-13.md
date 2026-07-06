# G/B/B → Stage 0 Alignment — Implementation Report
**Date:** 2026-06-13 · **Per:** Joe verification 2026-06-10 + joint @board/@nav consensus
**Dispatch:** SnapAI_Landing_Page_GBB_Fix_Dispatch_Prompt v1
**Decisions taken:** Commit to staging → verify → approve prod · Fix all 6 internal copy spots now · Ticket the deeper FE+BE refactor

---

## DONE — 9 files edited & verified (clean minimal diffs, LF/blob-exact)

### Customer-facing landing pages (PRIORITY 1)
| File | Lines | Change |
|---|---|---|
| `app/tech/page.tsx` | 58, 103 | Step-3 title + hero subhead → context-aware wedge |
| `app/page.tsx` | 127, 214 | Hero copy + feature card → "three context-aware options … no upsell pressure" |
| `app/homeowner/page.tsx` | 62,145,158,166,175,180,+caption | Path A: copy de-branded; sample cards retagged to one coherent mid-life (10-yr) example (Quick Fix / Smart Repair / Replace System) + clarifying caption |

### Internal app copy (PRIORITY 2 — copy only)
| File | Line | Change |
|---|---|---|
| `app/layout.tsx` | 9 | **Public SEO/OG meta description** de-branded (this one is genuinely public) |
| `app/(app)/dashboard/page.tsx` | 301, 324 | Empty-state copy + tagline de-branded |
| `lib/urdu-strings.ts` | 178 | Matching PK Urdu key+value updated so the tagline translation still resolves |
| `app/(app)/settings/pricing/page.tsx` | 591 | Owner help text de-branded |
| `app/(app)/settings/privacy/page.tsx` | 39 | Data-retention disclosure de-branded |
| `app/(app)/assess/page.tsx` | 765 | Estimate-building loading text → "Calculating your three options" |

### Verification (all pass)
- Display "Good/Better/Best" remaining in the 9 files: **0**
- Stage 0 anchor phrases across the 9 files: **17**
- "junior/senior tech" status code: **0**
- Structure (brace/paren/quote balance vs HEAD): **intact**
- Each file rebuilt from its exact HEAD blob + the single text swap → diff is purely the intended content change (2–16 lines/file).
- `tsc`/`pnpm dev`: NOT runnable in-sandbox (mount `node_modules` are Windows binaries). Edits are pure string/text content; Vercel build is the authoritative typecheck.

### Tooling notes (matter for the commit)
1. **File-tool Edit corrupts these Drive files** (truncation/EOL-mangle gotcha). All edits were applied via the sandbox using byte-exact, blob-derived replacements written in place (`cat … > file`).
2. **Sandbox git cannot commit here.** The Drive mount denies file unlink, so a stale 0-byte `.git/index.lock` (left by a failed `git checkout`) can't be removed and `git add`/`commit` fail. **The commit must be run from your Windows side.**
3. In sandbox git, ~30 untouched files show spurious whole-file diffs — pure CRLF-vs-LF artifacts of the Windows checkout meeting Linux git, NOT real changes. Only the 9 files above have real content changes. **Stage only the 9 listed files.**

---

## NOT DONE — deeper in-app G/B/B drift (ticket this separately, FE+BE)

Branded G/B/B is still live in the actual product flow:
- `components/FaultResolutionScreen.tsx:90,461,537` — tech-facing repair-plan cards hardcode "Good/Better/Best" (also flows into the homeowner PDF). **Highest impact.**
- `lib/api.ts:54` — `EstimateOption.tier: "good"|"better"|"best"` API contract (internal enum keys).
- `lib/urdu-strings.ts:74-76,196` — PK display translations of Good/Better/Best (still referenced by the live component — intentionally kept until the refactor).
- `lib/tracking.ts:17` + `FaultResolutionScreen.tsx:7` — code comments documenting the current internal model.
- `components/PresentMode.tsx:296`, `lib/tracking.ts:221` — internal id/analytics keys (not user-visible).

**Proposed ticket:** "Stage 0 context-aware tier labels in the live estimate flow." Backend emits context-aware `name` per tier by unit-age category (young/midlife/eol — label sets locked in `MBrain/SnapAI_Internal_Strategy_v1.2_Stage0_Aligned.md`); delete the hardcoded G/B/B fallback in FaultResolutionScreen; add PK label translations. The dispatch's `getTierLabels(unitAgeCategory)` helper is the right primitive. Until this ships, the product flow stays G/B/B-branded despite aligned marketing surfaces.

### Borderline, untouched
`app/tech/page.tsx:54` — "your best senior tech" (ordinary adjectives, not the retired status code; GATE 3 passes). Flag only.

---

## COMMIT HANDOFF — run from Windows (PowerShell, in the ScopeSnapAI repo)

```powershell
# you're on branch 'staging' — confirm:
git status -sb

# remove the stale lock left by the sandbox (Windows allows this):
del .git\index.lock   # if it exists

# stage ONLY the 9 edited files (avoids the CRLF EOL noise on other files):
git add `
  scopesnap-web/app/tech/page.tsx `
  scopesnap-web/app/page.tsx `
  scopesnap-web/app/homeowner/page.tsx `
  scopesnap-web/app/layout.tsx `
  "scopesnap-web/app/(app)/dashboard/page.tsx" `
  "scopesnap-web/app/(app)/settings/pricing/page.tsx" `
  "scopesnap-web/app/(app)/settings/privacy/page.tsx" `
  "scopesnap-web/app/(app)/assess/page.tsx" `
  scopesnap-web/lib/urdu-strings.ts

git status   # confirm exactly 9 files staged, nothing else
git commit -F commit_msg_gbb.txt   # message below
git push origin staging
```

Then verify on `staging.snapai.mainnov.tech` (/, /tech, /homeowner, dashboard) →
once Vercel staging is green and the copy reads right, promote to prod via the
Appendix-G promote script. Do NOT promote until you've eyeballed staging.

### Commit message (save as `commit_msg_gbb.txt`)
```
strategy: align landing + app copy with Stage 0 Q4 Tier 1 wedge (no G/B/B)

Replaces "Good / Better / Best" branded tier labels across all customer-facing
and in-app COPY with the locked Stage 0 Q4 Tier 1 framing ("three context-aware
options, one honest recommendation, no upsell pressure").

Per Joe verification 2026-06-10 + joint @board + @nav consensus.

Landing pages:
- app/tech/page.tsx (58, 103)
- app/page.tsx (127, 214)
- app/homeowner/page.tsx (62, 145, 158-180, sample-card caption; Path A)

Internal copy + SEO + PK string:
- app/layout.tsx (9, OG/meta)
- app/(app)/dashboard/page.tsx (301, 324)
- app/(app)/settings/pricing/page.tsx (591)
- app/(app)/settings/privacy/page.tsx (39)
- app/(app)/assess/page.tsx (765)
- lib/urdu-strings.ts (178)

Deferred to a separate FE+BE ticket (branded G/B/B still live in the estimate
flow): components/FaultResolutionScreen.tsx, lib/api.ts tier contract,
lib/urdu-strings.ts:74-76 display labels.

Refs: marketing/MBrain/SnapAI_Stage0_Output_v1.md
Refs: marketing/MBrain/SnapAI_Internal_Strategy_v1.2_Stage0_Aligned.md
```
