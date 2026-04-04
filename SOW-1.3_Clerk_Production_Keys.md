# SOW-1.3 — Clerk Production Key Switch Guide
*Prepared: 2026-04-03*

Before launching SnapAI to real users you must switch from Clerk **development** keys (`pk_test_` / `sk_test_`) to Clerk **production** keys (`pk_live_` / `sk_live_`). Development keys only allow sign-in from `localhost`; users on the live domain will see auth errors unless you complete this switch.

---

## Step 1 — Create a Production Instance in Clerk

1. Go to [https://dashboard.clerk.com](https://dashboard.clerk.com) and open the **SnapAI** application.
2. In the top-left dropdown that says **"Development"**, click **"Create production instance"**.
3. Clerk will walk you through:
   - Verifying your domain (`app.scopesnap.ai` or similar)
   - Adding DNS records (CNAME for `clerk.scopesnap.ai`)
   - Enabling allowed redirect URLs (e.g. `https://app.scopesnap.ai/dashboard`)
4. Once verified, Clerk will show your **Production API Keys**.

---

## Step 2 — Copy Production Keys

From the Clerk Dashboard → **API Keys** tab (make sure "Production" is selected):

| Key | Example format | Where to use |
|-----|---------------|--------------|
| Publishable Key | `pk_live_XXXXXXXXXXXXXXXX` | Vercel (frontend) + Railway (api, as `CLERK_PUBLISHABLE_KEY`) |
| Secret Key | `sk_live_XXXXXXXXXXXXXXXX` | Vercel (frontend) + Railway (api, as `CLERK_SECRET_KEY`) |

---

## Step 3 — Update Vercel (Frontend)

1. Go to [https://vercel.com](https://vercel.com) → **SnapAI** project → **Settings** → **Environment Variables**.
2. Update these two variables (set for **Production** environment):

```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY = pk_live_XXXXXXXXXXXXXXXX
CLERK_SECRET_KEY                  = sk_live_XXXXXXXXXXXXXXXX
```

3. Also set/verify:
```
NEXT_PUBLIC_ENV = production
NEXT_PUBLIC_API_URL = https://your-railway-api-url.railway.app
```

4. Click **Save**, then **Redeploy** (Deployments tab → three dots → Redeploy).

---

## Step 4 — Update Railway (API)

1. Go to [https://railway.app](https://railway.app) → **SnapAI API** service → **Variables** tab.
2. Update:

```
CLERK_SECRET_KEY      = sk_live_XXXXXXXXXXXXXXXX
CLERK_PUBLISHABLE_KEY = pk_live_XXXXXXXXXXXXXXXX
ENVIRONMENT           = production
FRONTEND_URL          = https://app.scopesnap.ai
REPORT_BASE_URL       = https://app.scopesnap.ai/r
```

3. Railway auto-deploys on variable save. Watch the **Deployments** tab to confirm success.

---

## Step 5 — Update .env.production Template (Local Reference)

Create `scopesnap-web/.env.production` (never commit this file — it's in `.gitignore`):

```bash
NEXT_PUBLIC_API_URL=https://your-api.railway.app
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_XXXXXXXXXXXXXXXX
CLERK_SECRET_KEY=sk_live_XXXXXXXXXXXXXXXX
NEXT_PUBLIC_ENV=production
```

Create `scopesnap-api/.env.production` (never commit):

```bash
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/scopesnap_prod
ENVIRONMENT=production
CLERK_SECRET_KEY=sk_live_XXXXXXXXXXXXXXXX
CLERK_PUBLISHABLE_KEY=pk_live_XXXXXXXXXXXXXXXX
GEMINI_API_KEY=your_production_gemini_key
RESEND_API_KEY=your_resend_api_key
FROM_EMAIL=noreply@scopesnap.ai
FRONTEND_URL=https://app.scopesnap.ai
REPORT_BASE_URL=https://app.scopesnap.ai/r
```

---

## Step 6 — Verify

After both services redeploy:

1. Open `https://app.scopesnap.ai` in an **incognito window**.
2. Click **Sign Up** — you should land on the Clerk-hosted sign-up page.
3. Create a test account and confirm you reach the dashboard.
4. Check Clerk Dashboard → **Users** tab — you should see the new user appear.
5. Test sign-out and sign-in again.

---

## Checklist

- [ ] Clerk production instance created and domain verified
- [ ] DNS CNAME record for `clerk.scopesnap.ai` propagated
- [ ] `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` updated in Vercel (production)
- [ ] `CLERK_SECRET_KEY` updated in Vercel (production)
- [ ] `CLERK_SECRET_KEY` + `CLERK_PUBLISHABLE_KEY` updated in Railway
- [ ] `NEXT_PUBLIC_ENV=production` set in Vercel
- [ ] Sign-up / sign-in tested in incognito on live domain
- [ ] New user appears in Clerk production dashboard

---

## Important Notes

- **Do not** reuse dev keys in production — they are rate-limited and only work on localhost.
- **Do not** commit `.env.production` files to git. Add them to `.gitignore` if not already.
- The existing `sk_test_VhO4cPofHo...` key visible in `scopesnap-api/.env` is a **dev key** — fine for local/Railway dev but must be replaced before public launch.
- Clerk's free tier supports up to **10,000 monthly active users** — plenty for beta.
