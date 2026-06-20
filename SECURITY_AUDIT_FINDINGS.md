# SnapAI Security Audit — Findings & Status

> Source: `snapai-full-audit` skill, **scoped + safe** runs. Date: 2026-06-20.
> Result: **0 Critical / 0 High.** Everything below is Medium/Low hardening or hygiene.
> Auth on staging is gated by Vercel Deployment Protection; audit reaches it via a
> Protection-Bypass-for-Automation secret (in `.env.test`, gitignored).

---

## A. FIXED — committed (staging; several rode to prod via the full promote `5b092eb`)

| Finding | Fix | Where |
|---|---|---|
| Leaked dev keys in committed files (Clerk `sk_test`, Gemini `AIza…`, Roboflow) | Redacted in-file + `.gitleaks.toml` allowlist for public keys/caches | `CODE_AUDIT_REPORT.md`, notebook, `.gitleaks.toml` |
| **SSRF** in PDF image fetch (only `startswith("http")`) | `_is_safe_remote_url()` blocks private/loopback/link-local/metadata hosts | `scopesnap-api/services/pdf_generator.py` |
| **ReDoS** via unescaped dynamic regex | `escapeRegExp()` on the label | `scopesnap-web/lib/tesseractOcr.ts` |
| Dockerfile run-as-root (semgrep) | Prod stage already non-root (`USER nextjs`); dev stage documented `nosemgrep` | `scopesnap-web/Dockerfile` |
| SAST noise: raw SQL in Alembic migrations | `.semgrepignore` for `db/migrations/` (static DDL, not request-driven) | `.semgrepignore` |
| `X-Powered-By` framework leak (ZAP Low) | `poweredByHeader: false` | `scopesnap-web/next.config.js` |
| CSP "no fallback" directives missing (ZAP Medium) | Added `object-src 'none'`, `base-uri 'self'`, `frame-ancestors 'none'`, `form-action 'self'` | `scopesnap-web/next.config.js` |

## B. ACCEPTED RISK — researched, intentional (do NOT "fix")

| Item | Why it stays |
|---|---|
| CSP `script-src 'unsafe-eval'` | **Google Maps JS API requires it** (Google CSP docs, 2026). Removing needs Maps in a sandboxed iframe — feature refactor, not a header. |
| CSP `style-src 'unsafe-inline'` | Clerk + Google Maps + Tailwind inject inline `style=""` attributes; a nonce doesn't cover attribute styles. Lowest-severity item. |
| ZAP "Cross-Domain Misconfiguration" (Medium) | **False positive.** Vercel serves `ACAO:*` on public `/_next/static/` immutable assets (no creds, no sensitive data). Backend API CORS is already correctly scoped. |
| ZAP "Cross-Domain JS Source File Inclusion" (Low) | Expected first-party SDKs (Clerk/PostHog/Sentry/Maps). SRI impractical on auto-updating vendor loaders. |

## C. OPEN — action needed (exact steps)

1. **Rotate the 3 leaked keys** (redaction doesn't purge git history): Clerk `sk_test` for instance `glowing-cowbird-89`, the Gemini API key, the Roboflow private key. Revoke + reissue in each provider's dashboard.
2. **Env-var drift (staging ≠ prod):** add to **staging** Vercel (`scopesnap-web-staging`): `NEXT_PUBLIC_SUPABASE_URL` + `NEXT_PUBLIC_SUPABASE_ANON_KEY` (use the **staging** `snapai-staging-use1` project's values — anon key is public/safe) and `NEXT_TELEMETRY_DISABLED`. These power the dashboard **Supabase Realtime approval-notification** feature, which is silently OFF + untestable on staging without them (`lib/supabaseClient.ts` returns `null`). Also resolve prod `CLERK_SECRET_KEY` "Needs Attention" flag in Vercel.
3. **SRI for first-party bundles** — apply during a *watched* staging build (experimental flag on the new Next 16 stack):
   ```js
   // next.config.js, top-level in nextConfig
   experimental: { sri: { algorithm: "sha384" } },
   ```
   Verify the staging Vercel build succeeds + chunks load; one-line revert if not. (Only covers first-party scripts; vendor SDKs can't get SRI.)
4. **Remove `script-src 'unsafe-inline'`** (real XSS hardening, separate project): migrate to Clerk strict-CSP nonce — `clerkMiddleware({ contentSecurityPolicy: { strict: true } })` + `'strict-dynamic'` + `<ClerkProvider dynamic>`. Needs full auth/maps/analytics testing on staging. Refs: clerk.com/docs/security/clerk-csp, nextjs.org/docs/app/guides/content-security-policy.
5. **CORS localhost tidiness (optional, negligible risk):** gate the `localhost`/`127.0.0.1` origins behind `settings.environment` so they're absent in production.
   ```python
   cors_origins = [settings.frontend_url, "https://snapai.mainnov.tech",
                   "https://pk.snapai.mainnov.tech", "https://staging.snapai.mainnov.tech",
                   "https://pk-staging.snapai.mainnov.tech"]
   if settings.environment != "production":
       cors_origins += ["http://localhost:3000", "http://127.0.0.1:3000"]
   ```
6. **2 API test files fail collection** — `tests/test_fault_estimate_age_v2.py` + `tests/test_stage4_5.py` raise `NameError: os` / `__file__` from their own `exec()`-based module loader (pre-existing, not from audit changes). Fix the loader to pass proper globals, or exclude with `--ignore` until then. (Other 122 API tests pass on Python 3.12.)

## D. Gate / verification results (safe mode)

- **Schema parity:** staging `alembic_version` **041** = prod **041** — PASS.
- **ZAP passive DAST (real app, 80 URLs):** 0 High · 6 Medium · 2 Low — see A/B above; no critical/exploitable.
- **Both markets reachable** (US + PK staging) — PASS.
- **Env-var key parity:** drift (item C-2) — the one item keeping the promote gate at NO-GO until staging mirrors prod.
- **Railway backend:** `scopesnap-api` Online, latest deploy successful, healthy metrics.

## E. Environment notes for re-runs
- Python API tests need a **Python 3.12 venv** (psycopg2-binary has no 3.14 wheel).
- semgrep runs via `python -m semgrep`; `semgrep.exe` is intermittently blocked by Device Guard.
- ZAP needs the Vercel bypass **header** injected via a ZAP automation-plan replacer (cookie/query-param don't persist through the spider). Plan at `C:\tmp\zapwork\plan.yaml`.
