/**
 * SnapAI — Beta Landing Page
 * SOW Task 1.5: Replace dev placeholder with proper beta landing page.
 *
 * Sections:
 *  1. Hero — headline, sub-copy, CTA button, BETA badge
 *  2. How it works — 3 steps (Photo → AI → Send)
 *  3. Video placeholder — 16:9 embed slot
 *  4. Early-access signup — email capture → POST /api/waitlist
 *  5. Footer — minimal, no external links
 *
 * Design tokens match tailwind.config.ts (brand-green, surface-bg, etc.)
 */

"use client";

import { useState } from "react";
import Link from "next/link";
import InstallPrompt from "@/components/InstallPrompt";

export default function LandingPage() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  async function handleSignup(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim()) return;
    setSubmitting(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/api/waitlist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim() }),
      });
      if (res.ok) {
        setSubmitted(true);
      } else {
        const data = await res.json().catch(() => ({}));
        setError(data?.detail || "Something went wrong. Please try again.");
      }
    } catch {
      setError("Could not connect. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      {/* ── Meta / SEO ────────────────────────────────────────────────────── */}
      {/* Note: use Next.js Metadata API in layout.tsx for full meta control */}

      {/* PWA install prompt — shows on iOS/Android when not yet installed */}
      <InstallPrompt />

      <main className="min-h-screen bg-surface-bg text-text-primary">

        {/* ── Navigation ──────────────────────────────────────────────────── */}
        <nav className="max-w-5xl mx-auto px-6 py-5 flex items-center justify-between">
          <div className="inline-flex items-center gap-2.5">
            <div className="w-8 h-8 bg-brand-green rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">S</span>
            </div>
            <span className="font-bold text-lg tracking-tight">SnapAI</span>
            <span className="text-[10px] font-bold tracking-widest uppercase bg-brand-green/10 text-brand-green border border-brand-green/20 rounded px-1.5 py-0.5 ml-1">
              BETA
            </span>
          </div>
          <Link
            href="/dashboard"
            className="text-sm font-semibold text-brand-green hover:underline"
          >
            Sign In →
          </Link>
        </nav>

        {/* ── Hero ────────────────────────────────────────────────────────── */}
        <section className="max-w-3xl mx-auto px-6 pt-16 pb-20 text-center">
          <div className="inline-block bg-brand-green/10 text-brand-green text-xs font-semibold tracking-wider uppercase rounded-full px-4 py-1.5 mb-6 border border-brand-green/20">
            Early Access — Limited Beta
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight leading-tight mb-5">
            HVAC estimates in{" "}
            <span className="text-brand-green">90 seconds.</span>
            <br />
            No guessing. No spreadsheets.
          </h1>
          <p className="text-lg text-text-secondary leading-relaxed mb-10 max-w-xl mx-auto">
            Photograph any HVAC unit. SnapAI identifies the equipment,
            generates a Good / Better / Best estimate, and sends the homeowner a
            beautiful report — all before you leave the driveway.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link
              href="/dashboard"
              className="bg-brand-green text-white font-semibold py-3.5 px-8 rounded-xl hover:bg-green-700 transition-colors text-center text-base"
            >
              Start Your First Assessment →
            </Link>
            <a
              href="#how-it-works"
              className="border border-surface-border text-text-secondary font-medium py-3.5 px-8 rounded-xl hover:bg-surface-card transition-colors text-center text-base"
            >
              See How It Works
            </a>
          </div>
        </section>

        {/* ── How It Works ────────────────────────────────────────────────── */}
        <section id="how-it-works" className="bg-surface-card border-y border-surface-border py-20">
          <div className="max-w-4xl mx-auto px-6">
            <h2 className="text-2xl font-bold text-center mb-12">
              Three taps. Professional estimate.
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
              {[
                {
                  step: "01",
                  title: "Photograph the equipment",
                  desc: "Open the app, tap Assess, and take 1–5 photos of the HVAC unit. Works indoors and outdoors.",
                },
                {
                  step: "02",
                  title: "AI identifies everything",
                  desc: "Gemini Vision reads make, model, age, and condition. Generates Good / Better / Best pricing in seconds.",
                },
                {
                  step: "03",
                  title: "Send the homeowner a report",
                  desc: "One tap delivers a branded PDF report to the homeowner's inbox. No login required on their end.",
                },
              ].map(({ step, title, desc }) => (
                <div key={step} className="text-center">
                  <div className="w-12 h-12 bg-brand-green/10 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-brand-green/20">
                    <span className="text-brand-green font-mono font-bold text-sm">{step}</span>
                  </div>
                  <h3 className="font-semibold text-base mb-2">{title}</h3>
                  <p className="text-text-secondary text-sm leading-relaxed">{desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── App Preview ─────────────────────────────────────────────────── */}
        <section className="max-w-4xl mx-auto px-6 py-20">
          <h2 className="text-2xl font-bold text-center mb-3">See it in action</h2>
          <p className="text-center text-text-secondary text-sm mb-10">
            From the driveway to a signed estimate in under 90 seconds.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              {
                step: "01",
                color: "#1a8754", bg: "rgba(26,135,84,.08)",
                title: "Snap the nameplate",
                desc: "AI reads make, model, serial, and age automatically. No manual entry.",
              },
              {
                step: "02",
                color: "#6a1b9a", bg: "rgba(106,27,154,.08)",
                title: "Gemini builds the estimate",
                desc: "Good / Better / Best pricing with your markup applied. Parts, labor, R-22 surcharges included.",
              },
              {
                step: "03",
                color: "#c4600a", bg: "rgba(196,96,10,.08)",
                title: "Homeowner gets the report",
                desc: "A branded PDF lands in their inbox before you leave the driveway.",
              },
            ].map(({ step, title, desc, color, bg }) => (
              <div key={step} className="bg-surface-card border border-surface-border rounded-2xl p-5">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 text-sm font-mono font-bold"
                       style={{ background: bg, color }}>
                    {step}
                  </div>
                </div>
                <h3 className="font-bold text-base mb-2 text-text-primary">{title}</h3>
                <p className="text-text-secondary text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>

          {/* VIDEO PLACEHOLDER — swap this div for <iframe> when video is ready */}
          <div className="mt-12 relative w-full rounded-2xl overflow-hidden"
               style={{ paddingBottom: "56.25%", background: "#111210" }}>
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-4">
              <div className="w-20 h-20 rounded-full flex items-center justify-center"
                style={{
                  background: "rgba(26,135,84,.15)",
                  border: "2px solid rgba(26,135,84,.5)",
                  boxShadow: "0 0 40px rgba(26,135,84,.2)",
                }}>
                <svg className="w-8 h-8 ml-1" fill="#1a8754" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z"/>
                </svg>
              </div>
              <div className="text-center">
                <p className="text-white font-bold text-base">Watch the 90-second demo</p>
                <p className="text-white/40 text-xs mt-1">Video in production</p>
              </div>
              <span className="absolute top-4 right-4 text-[10px] font-bold uppercase tracking-widest px-2.5 py-1 rounded-full"
                style={{ background: "rgba(26,135,84,.2)", color: "#1a8754", border: "1px solid rgba(26,135,84,.3)" }}>
                Coming Soon
              </span>
            </div>
          </div>
          <p className="text-center text-xs text-text-secondary mt-4">
            Can&apos;t wait? <Link href="/dashboard" className="text-brand-green font-semibold hover:underline">Try it live</Link>
          </p>
        </section>

        {/* ── Early Access Signup ─────────────────────────────────────────── */}
        <section className="bg-surface-card border-y border-surface-border py-20">
          <div className="max-w-lg mx-auto px-6 text-center">
            <h2 className="text-2xl font-bold mb-3">Get early access</h2>
            <p className="text-text-secondary mb-8 text-sm leading-relaxed">
              We're onboarding HVAC contractors in small batches.
              Drop your email and we'll reach out within 48 hours.
            </p>
            {submitted ? (
              <div className="bg-brand-green/10 border border-brand-green/20 rounded-xl p-6">
                <p className="text-brand-green font-semibold text-lg mb-1">You're on the list!</p>
                <p className="text-text-secondary text-sm">
                  We'll be in touch within 48 hours with your access details.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSignup} className="flex flex-col sm:flex-row gap-3">
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  className="flex-1 border border-surface-border rounded-xl px-4 py-3 text-sm bg-surface-bg focus:outline-none focus:ring-2 focus:ring-brand-green placeholder:text-text-secondary"
                />
                <button
                  type="submit"
                  disabled={submitting}
                  className="bg-brand-green text-white font-semibold py-3 px-6 rounded-xl hover:bg-green-700 transition-colors text-sm disabled:opacity-60 whitespace-nowrap"
                >
                  {submitting ? "Sending…" : "Request Access"}
                </button>
              </form>
            )}
            {error && (
              <p className="mt-3 text-red-500 text-xs">{error}</p>
            )}
            <p className="mt-4 text-xs text-text-secondary">
              No spam. Unsubscribe any time.
            </p>
          </div>
        </section>

        {/* ── Footer ──────────────────────────────────────────────────────── */}
        <footer className="max-w-5xl mx-auto px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-text-secondary">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 bg-brand-green rounded flex items-center justify-center">
              <span className="text-white font-bold text-[10px]">S</span>
            </div>
            <span>SnapAI — Professional HVAC assessments for contractors</span>
          </div>
          <div className="flex gap-4">
            <Link href="/privacy" className="hover:text-text-primary transition-colors">Privacy</Link>
            <Link href="/dashboard" className="hover:text-text-primary transition-colors">Sign In</Link>
          </div>
        </footer>

      </main>
    </>
  );
}
