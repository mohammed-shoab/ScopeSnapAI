/**
 * ScopeSnap — Landing Page (placeholder)
 * This is a minimal placeholder. The full marketing landing page
 * is NOT in scope for MVP (per SOW). Build after first paying customer.
 */
import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-surface-bg flex flex-col items-center justify-center p-8">
      <div className="max-w-lg w-full text-center">
        {/* Logo */}
        <div className="mb-8">
          <div className="inline-flex items-center gap-3">
            <div className="w-10 h-10 bg-brand-green rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">S</span>
            </div>
            <span className="text-2xl font-bold tracking-tight">ScopeSnap</span>
          </div>
        </div>

        {/* Tagline */}
        <h1 className="text-3xl font-extrabold tracking-tight mb-3 text-text-primary">
          AI-Powered HVAC Estimation
        </h1>
        <p className="text-text-secondary mb-8 leading-relaxed">
          Photograph any HVAC unit. Get an instant AI assessment with
          Good/Better/Best estimates. Send the homeowner a beautiful report
          in 90 seconds.
        </p>

        {/* CTA */}
        <div className="flex flex-col gap-3">
          <Link
            href="/dashboard"
            className="w-full bg-brand-green text-white font-semibold py-3 px-6 rounded-xl hover:bg-green-700 transition-colors text-center"
          >
            Go to Dashboard →
          </Link>
          <p className="text-xs text-text-secondary">
            Local development mode — landing page in scope for marketing phase.
          </p>
        </div>

        {/* Status */}
        <div className="mt-12 p-4 bg-surface-card border border-surface-border rounded-xl text-left">
          <p className="text-xs font-mono font-semibold text-text-secondary mb-2">BUILD STATUS</p>
          <div className="space-y-1.5 text-sm">
            <div className="flex items-center gap-2">
              <span className="text-brand-green">✅</span>
              <span>WP-01: Project Scaffolding</span>
              <span className="ml-auto text-xs text-brand-green font-mono">DONE</span>
            </div>
            <div className="flex items-center gap-2 text-text-secondary">
              <span>⏳</span>
              <span>WP-02: Photo Upload + Vision AI</span>
              <span className="ml-auto text-xs font-mono">NEXT</span>
            </div>
            <div className="flex items-center gap-2 text-text-secondary">
              <span>⏳</span>
              <span>WP-03: Equipment Database</span>
              <span className="ml-auto text-xs font-mono">PENDING</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
