/**
 * Reusable "Coming Soon" stub page component.
 */
"use client";

import Link from "next/link";

interface Props {
  icon: string;
  title: string;
  description: string;
  eta?: string;
  features?: string[];
  backHref?: string;
  backLabel?: string;
}

export default function ComingSoonPage({
  icon,
  title,
  description,
  eta = "Q2 2026",
  features = [],
  backHref = "/dashboard",
  backLabel = "← Back to Dashboard",
}: Props) {
  return (
    <div className="max-w-lg mx-auto space-y-6 pt-8 pb-12">
      <div className="text-center space-y-3">
        <div className="text-6xl">{icon}</div>
        <h1 className="text-2xl font-extrabold text-text-primary">{title}</h1>
        <p className="text-text-secondary text-sm">{description}</p>
        <span className="inline-block text-xs font-bold bg-blue-100 text-blue-700 px-3 py-1.5 rounded-full">
          🚧 Coming {eta}
        </span>
      </div>

      {features.length > 0 && (
        <div className="card p-5 space-y-3">
          <p className="text-xs font-bold uppercase tracking-widest text-text-secondary font-mono">
            What's Planned
          </p>
          {features.map((f) => (
            <div key={f} className="flex items-start gap-2.5">
              <span className="text-brand-green font-bold mt-0.5">✓</span>
              <p className="text-sm text-text-primary">{f}</p>
            </div>
          ))}
        </div>
      )}

      <Link
        href={backHref}
        className="block w-full text-center py-3 border border-surface-border rounded-xl text-sm font-semibold text-text-secondary hover:border-brand-green hover:text-brand-green transition-colors"
      >
        {backLabel}
      </Link>
    </div>
  );
}
