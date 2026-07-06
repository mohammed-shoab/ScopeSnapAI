/**
 * SnapAI -- Public Terms of Service page. Linked from the public footer.
 * CONTENT SOURCE: ScopeSnapAI/SnapAI_Legal_Framework_ToS_and_Disclaimers_v1_DRAFT.md
 * TODO: paste approved ToS (incl. Sec 2A-2C definitional clause + Sec 7 indemnification).
 *       Do NOT edit legal wording without Alfred (US HVAC counsel) sign-off.
 */
export default function TermsPage() {
  return (
    <main className="min-h-screen bg-surface-bg text-text-primary">
      <div className="max-w-2xl mx-auto px-6 py-12">
        <div className="mb-8">
          <a href="/tech" className="text-brand-green text-sm font-semibold hover:underline">← Back to SnapAI</a>
          <h1 className="text-3xl font-bold mt-4 mb-2">Terms of Service</h1>
          <p className="text-text-secondary text-sm">Last updated: TODO</p>
        </div>
        <div className="prose prose-sm max-w-none space-y-6 text-text-primary">
          <section>
            <h2 className="text-lg font-bold mb-2">Terms of Service</h2>
            <p className="text-sm text-text-secondary leading-relaxed">
              The full Terms of Service and disclaimers are being finalized. Questions:{" "}
              <a href="mailto:hello@mainnov.tech" className="text-brand-green font-semibold hover:underline">hello@mainnov.tech</a>.
            </p>
          </section>
        </div>
      </div>
    </main>
  );
}
