/**
 * ScopeSnap — Public Privacy Policy Page
 * SOW Task 1.11: Required for beta launch — linked from landing page footer.
 * Plain language, mobile-friendly. No cookies banner required (first-party only).
 */

export default function PrivacyPage() {
  return (
    <main className="min-h-screen bg-surface-bg text-text-primary">
      <div className="max-w-2xl mx-auto px-6 py-12">

        {/* Header */}
        <div className="mb-8">
          <a href="/" className="text-brand-green text-sm font-semibold hover:underline">
            ← Back to ScopeSnap
          </a>
          <h1 className="text-3xl font-bold mt-4 mb-2">Privacy Policy</h1>
          <p className="text-text-secondary text-sm">Last updated: March 23, 2026</p>
        </div>

        <div className="prose prose-sm max-w-none space-y-6 text-text-primary">
          <section>
            <h2 className="text-lg font-bold mb-2">What we collect</h2>
            <p className="text-sm text-text-secondary leading-relaxed">
              ScopeSnap collects only the information necessary to provide the HVAC assessment service:
              contractor account details (name, company, email), HVAC equipment photos you upload,
              and the homeowner information you enter into each job (name, address, phone). We also
              collect anonymized usage data (pages visited, features used) to improve the product.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-2">How we use it</h2>
            <p className="text-sm text-text-secondary leading-relaxed">
              Photos are sent to Google Gemini Vision AI for equipment identification and then stored
              in Cloudflare R2. Homeowner contact information is used only to send the assessment report
              email you request. We do not sell data to third parties. We do not use your data for
              advertising.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-2">Data storage</h2>
            <p className="text-sm text-text-secondary leading-relaxed">
              Data is stored on Railway (PostgreSQL database, USA) and Cloudflare R2 (photos, USA edge
              network). Authentication is handled by Clerk. Payments are processed by Stripe. None of
              these providers have access to your assessment content beyond what is required to operate
              their services.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-2">Your rights</h2>
            <p className="text-sm text-text-secondary leading-relaxed">
              You can export all your data as a CSV from Settings → Privacy at any time. You can request
              account deletion by emailing{" "}
              <a href="mailto:support@scopesnap.ai" className="text-brand-green font-semibold hover:underline">
                support@scopesnap.ai
              </a>
              . We will process deletion requests within 5 business days.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-2">Cookies</h2>
            <p className="text-sm text-text-secondary leading-relaxed">
              ScopeSnap uses first-party session cookies only (for authentication). We do not use
              third-party tracking cookies or advertising cookies.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold mb-2">Contact</h2>
            <p className="text-sm text-text-secondary leading-relaxed">
              Privacy questions:{" "}
              <a href="mailto:privacy@scopesnap.ai" className="text-brand-green font-semibold hover:underline">
                privacy@scopesnap.ai
              </a>
            </p>
          </section>
        </div>

      </div>
    </main>
  );
}
