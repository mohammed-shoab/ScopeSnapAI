/**
 * SnapAI -- Public Methodology page. Defines confidence bands numerically.
 * Bands are code-derived: report score from components/DataConfidenceLabel.tsx;
 * in-app fault badge from components/FaultResolutionScreen.tsx.
 */
export default function MethodologyPage() {
  return (
    <main className="min-h-screen bg-surface-bg text-text-primary">
      <div className="max-w-2xl mx-auto px-6 py-12">
        <div className="mb-8">
          <a href="/tech" className="text-brand-green text-sm font-semibold hover:underline">← Back to SnapAI</a>
          <h1 className="text-3xl font-bold mt-4 mb-2">Our Methodology</h1>
          <p className="text-text-secondary text-sm">Last updated: July 6, 2026</p>
          <p className="text-text-secondary text-sm italic mt-1">Draft pending final legal review (Alfred, US HVAC counsel). Not yet effective.</p>
        </div>
        <div className="prose prose-sm max-w-none space-y-6 text-text-primary">
          <section>
            <h2 className="text-lg font-bold mb-2">Confidence bands</h2>
            <p className="text-sm text-text-secondary leading-relaxed">
              Every finding in a homeowner report carries a confidence label derived from an AI-confidence score on a 0–100 scale. The score maps to four bands:
            </p>
            <ul className="text-sm text-text-secondary leading-relaxed space-y-2 mt-2">
              <li><strong className="text-text-primary">High Confidence:</strong> score of 90 or above.</li>
              <li><strong className="text-text-primary">Good Confidence:</strong> score of 75 to 89.</li>
              <li><strong className="text-text-primary">Fair Confidence:</strong> score of 60 to 74.</li>
              <li><strong className="text-text-primary">Low Confidence:</strong> score below 60.</li>
            </ul>
            <p className="text-sm text-text-secondary leading-relaxed mt-3">
              The in-app fault card badge summarizes these into three qualitative tiers — High, Medium, and Low. These tiers come from our cascade pipeline: the sensor track treats a confidence of 85% or above as high-confidence, and the visual OCR track flags results below 50% as low-confidence.
            </p>
            <p className="text-sm text-text-secondary leading-relaxed mt-3">
              Confidence reflects model agreement across our sensor and visual checks; it is not a guarantee of accuracy, and every finding requires on-site verification by your licensed contractor.
            </p>
          </section>
          <section>
            <h2 className="text-lg font-bold mb-2">Limitations</h2>
            <p className="text-sm text-text-secondary leading-relaxed">
              SnapAI is a decision-support tool for licensed HVAC professionals. Findings are preliminary and require independent verification by a qualified, licensed technician. SnapAI does not perform combustion, heat exchanger, or carbon monoxide safety diagnostics.
            </p>
          </section>
          <section>
            <p className="text-sm text-text-secondary leading-relaxed">
              See our full{" "}
              <a href="/tos" className="text-brand-green font-semibold hover:underline">Terms of Service</a>.
            </p>
          </section>
        </div>
      </div>
    </main>
  );
}
