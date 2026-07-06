/**
 * SnapAI -- Public Methodology page. Defines confidence bands numerically.
 * TODO (Will / Alfred): supply numeric thresholds for High / Medium / Low bands.
 */
export default function MethodologyPage() {
  return (
    <main className="min-h-screen bg-surface-bg text-text-primary">
      <div className="max-w-2xl mx-auto px-6 py-12">
        <div className="mb-8">
          <a href="/tech" className="text-brand-green text-sm font-semibold hover:underline">← Back to SnapAI</a>
          <h1 className="text-3xl font-bold mt-4 mb-2">Our Methodology</h1>
          <p className="text-text-secondary text-sm">Last updated: TODO</p>
        </div>
        <div className="prose prose-sm max-w-none space-y-6 text-text-primary">
          <section>
            <h2 className="text-lg font-bold mb-2">Confidence bands</h2>
            <p className="text-sm text-text-secondary leading-relaxed">Each finding is labeled with a confidence band, defined numerically:</p>
            <ul className="text-sm text-text-secondary leading-relaxed space-y-2 mt-2">
              <li><strong className="text-text-primary">High confidence:</strong> TODO (Will/Alfred) numeric threshold.</li>
              <li><strong className="text-text-primary">Medium confidence:</strong> TODO (Will/Alfred) numeric range.</li>
              <li><strong className="text-text-primary">Low confidence:</strong> TODO (Will/Alfred) numeric threshold.</li>
            </ul>
          </section>
          <section>
            <h2 className="text-lg font-bold mb-2">Limitations</h2>
            <p className="text-sm text-text-secondary leading-relaxed">SnapAI is a decision-support tool for licensed HVAC professionals; findings require on-site verification by a qualified technician. TODO: align with disclaimer copy.</p>
          </section>
        </div>
      </div>
    </main>
  );
}
