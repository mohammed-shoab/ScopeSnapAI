# SnapAI audit harness

Isolated tooling for the `snapai-full-audit` skill. **Not part of the Next.js app build** —
it has its own `package.json` so it never affects `scopesnap-web` deps or Vercel builds.

## What's here
- `tests/audit.spec.ts` — passwordless authenticated flow via Clerk **sign-in tokens** + `@clerk/testing` Testing Tokens.
- `global.setup.ts` — fetches the Clerk Testing Token before tests.
- `playwright.config.ts` — points at staging by default (`AUDIT_BASE_URL` to override).
- `loadtest.js` — k6 load script (full mode only).

## One-time setup
```bash
cd audit
npm install --include=dev   # this machine has NODE_ENV=production, which skips devDeps without this flag
npm run install-browsers    # downloads the Chromium Playwright build (global cache)
```

## Working auth path (VERIFIED 2026-06-18)
Staging Clerk forces an email code after password, and `sign_in_tokens` 404s — so the harness
uses a **`+clerk_test` user with Clerk's magic code `424242`** (auto-selected when AUDIT_EMAIL
contains `clerk_test`). Staging is also behind Vercel Deployment Protection, so the bypass secret
is required. Verified passing command:
```bash
cd audit && npm install --include=dev
set NODE_ENV=development
set CLERK_PUBLISHABLE_KEY=pk_test_...        # staging publishable
set CLERK_SECRET_KEY=sk_test_...             # staging secret (Testing Token)
set AUDIT_EMAIL=ds.shoab+clerk_test_audit@gmail.com
set AUDIT_BASE_URL=https://staging.snapai.mainnov.tech
set VERCEL_AUTOMATION_BYPASS_SECRET=...      # staging Protection Bypass for Automation
npm test
# -> AUTH OK — Clerk user: user_...  | Gated route landed on: .../dashboard | 1 passed
```

## Run the authenticated audit flow (staging)
```bash
# from a gitignored env file (do NOT commit secrets):
#   CLERK_PUBLISHABLE_KEY=pk_test_...   (staging publishable)
#   CLERK_SECRET_KEY=sk_test_...        (staging secret — admin credential, env only)
#   AUDIT_USER_ID=user_...              (a staging audit user id from .env.test)
#   AUDIT_BASE_URL=https://staging.snapai.mainnov.tech
cd audit
npm test
```
If `clerk.signIn({ strategy: "ticket" })` is rejected by the installed Clerk version,
the spec automatically falls back to consuming the ticket via `/sign-in?__clerk_ticket=...`.

## Load test (full mode)
```bash
k6 run --vus 50 --duration 5m audit/loadtest.js
```

> ⚠️ The exact Clerk method names (`signInTokens.createSignInToken`, `clerk.signIn` ticket
> strategy) must be confirmed against the installed `@clerk/testing` / `@clerk/backend`
> versions on first run. This harness is scaffolded from the documented API and verified to
> install + compile; the live sign-in assertion still needs one real run against staging.
