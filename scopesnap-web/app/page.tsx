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
            From the driveway to a signed estimate — in under 90 seconds.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              {
                step: "01",
                icon: (
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
                    <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/>
                    <circle cx="12" cy="13" r="4"/>
                  </svg>
                ),
                title: "Snap the nameplate",
                desc: "AI reads make, model, serial, and age automatically — no manual entry.",
                color: "#1a8754",
                bg: "rgba(26,135,84,.08)",
              },
              {
                step: "02",
                icon: (
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
                    <path d="M9.5 2A2.5 2.5 0 0112 4.5v15a2.5 2.5 0 01-5 0v-15A2.5 2.5 0 019.5 2z"/>
                    <path d="M14.5 8A2.5 2.5 0 0117 10.5v9a2.5 2.5 0 01-5 0v-9A2.5 2.5 0 0114.5 8z"/>
                    <path d="M4.5 13A2.5 2.5 0 017 15.5v4a2.5 2.5 0 01-5 0v-4A2.5 2.5 0 014.5 13z"/>
                  </svg>
                ),
                title: "Gemini builds the estimate",
                desc: "Good / Better / Best pricing generated with your markup — parts, labor, and R-22 surcharges included.",
                color: "#6a1b9a",
                bg: "rgba(106,27,154,.08)",
              },
              {
                step: "03",
                icon: (
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
                    <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 9.81a19.79 19.79 0 01-3.07-8.67A2 2 0 012 1h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L6.91 8.91a16 16 0 006.18 6.18l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/>
                  </svg>
                ),
                title: "Homeowner gets the report",
                desc: "A branded PDF lands in their inbox before you leave the driveway. No login needed on their end.",
                color: "#c4600a",
                bg: "rgba(196,96,10,.08)",
              },
            ].map(({ step, icon, title, desc, color, bg }) => (
              <div key={step} className="bg-surface-card border border-surface-border rounded-2xl p-5">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                       style={{ background: bg, color }}>
                    {icon}
                  </div>
                  <span className="text-xs font-mono font-bold" style={{ color }}>Step {step}</span>
                </div>
                <h3 className="font-bold text-base mb-2 text-text-primary">{title}</h3>
                <p className="text-text-secondary text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
          {/* ── Video embed slot — swap this div for <iframe> when video is ready ── */}
          <div className="mt-12 relative w-full rounded-2xl overflow-hidden"
               style={{ paddingBottom: "56.25%", background: "#111210" }}>
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-4">
              {/* Subtle grid lines for depth */}
              <svg className="absolute inset-0 w-full h-full opacity-5" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" strokeWidth="0.5"/>
                  </pattern>
                </defs>
                <