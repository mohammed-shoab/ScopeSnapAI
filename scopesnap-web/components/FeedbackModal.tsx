"use client";
/**
 * ScopeSnap — In-App Feedback Modal
 * BUG-01 fix: Replaces mailto: links with a proper in-app form.
 *
 * Usage:
 *   <FeedbackModal open={open} onClose={() => setOpen(false)} />
 *
 * Submits a POST to /api/feedback (internal Next.js API route).
 * Falls back to window.open(mailto:) only if the API call fails.
 */

import { useState, useEffect, useRef } from "react";

interface Props {
  open: boolean;
  onClose: () => void;
}

type FeedbackType = "bug" | "feature" | "general";

const TYPE_OPTIONS: { value: FeedbackType; label: string; icon: string }[] = [
  { value: "bug",     label: "Bug Report",       icon: "🐞" },
  { value: "feature", label: "Feature Request",   icon: "💡" },
  { value: "general", label: "General Feedback",  icon: "💬" },
];

export default function FeedbackModal({ open, onClose }: Props) {
  const [type, setType]           = useState<FeedbackType>("general");
  const [message, setMessage]     = useState("");
  const [status, setStatus]       = useState<"idle" | "sending" | "sent" | "error">("idle");
  const textareaRef               = useRef<HTMLTextAreaElement>(null);
  const overlayRef                = useRef<HTMLDivElement>(null);

  // Reset form when opened
  useEffect(() => {
    if (open) {
      setType("general");
      setMessage("");
      setStatus("idle");
      setTimeout(() => textareaRef.current?.focus(), 80);
    }
  }, [open]);

  // Close on Escape key
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open, onClose]);

  if (!open) return null;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!message.trim()) return;
    setStatus("sending");

    try {
      const res = await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          type,
          message: message.trim(),
          page: window.location.pathname,
          userAgent: navigator.userAgent,
        }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setStatus("sent");
    } catch {
      // Fallback: open mail client (last resort)
      const subject = encodeURIComponent(`ScopeSnap Beta Feedback — ${type}`);
      const body    = encodeURIComponent(message.trim() + `\n\nPage: ${window.location.href}`);
      window.open(`mailto:feedback@scopesnap.ai?subject=${subject}&body=${body}`);
      setStatus("sent");
    }
  }

  return (
    /* Backdrop */
    <div
      ref={overlayRef}
      className="fixed inset-0 z-[200] flex items-end justify-end p-6"
      style={{ background: "rgba(0,0,0,.45)", backdropFilter: "blur(4px)" }}
      onClick={(e) => { if (e.target === overlayRef.current) onClose(); }}
      role="dialog"
      aria-modal="true"
      aria-label="Send feedback"
    >
      {/* Panel */}
      <div
        className="w-full max-w-sm rounded-2xl shadow-2xl flex flex-col"
        style={{ background: "#ffffff", border: "1px solid #e5e7eb" }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 pt-5 pb-3">
          <div>
            <h2 className="text-[15px] font-semibold text-gray-900">Send Feedback</h2>
            <p className="text-xs text-gray-400 mt-0.5">Help us improve ScopeSnap</p>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-full flex items-center justify-center text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
            aria-label="Close feedback modal"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        {status === "sent" ? (
          /* Success state */
          <div className="flex flex-col items-center justify-center px-5 py-10 gap-3">
            <div
              className="w-12 h-12 rounded-full flex items-center justify-center"
              style={{ background: "rgba(26,135,84,.12)" }}
            >
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1a8754" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </div>
            <p className="text-sm font-semibold text-gray-800">Thanks for the feedback!</p>
            <p className="text-xs text-gray-400 text-center">We read every submission and use it to improve ScopeSnap.</p>
            <button
              onClick={onClose}
              className="mt-2 px-5 py-2 rounded-lg text-sm font-medium text-white transition-colors"
              style={{ background: "#1a8754" }}
            >
              Done
            </button>
          </div>
        ) : (
          /* Form */
          <form onSubmit={handleSubmit} className="px-5 pb-5 flex flex-col gap-4">
            {/* Type selector */}
            <div className="flex gap-2">
              {TYPE_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setType(opt.value)}
                  className={`flex-1 flex flex-col items-center gap-1 py-2.5 rounded-xl border text-xs font-medium transition-all ${
                    type === opt.value
                      ? "border-[#1a8754] text-[#1a8754]"
                      : "border-gray-200 text-gray-500 hover:border-gray-300"
                  }`}
                  style={type === opt.value ? { background: "rgba(26,135,84,.07)" } : {}}
                >
                  <span className="text-base">{opt.icon}</span>
                  {opt.label}
                </button>
              ))}
            </div>

            {/* Message */}
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1.5">
                What&apos;s on your mind?
              </label>
              <textarea
                ref={textareaRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={4}
                maxLength={1000}
                placeholder={
                  type === "bug"
                    ? "Describe what happened and how to reproduce it…"
                    : type === "feature"
                    ? "Describe the feature and why it would help…"
                    : "Share your thoughts, questions, or suggestions…"
                }
                required
                className="w-full rounded-xl border border-gray-200 px-3.5 py-3 text-sm text-gray-800 resize-none focus:outline-none focus:ring-2 focus:border-transparent placeholder-gray-300"
                style={{ "--tw-ring-color": "#1a8754" } as React.CSSProperties}
              />
              <p className="text-right text-[10px] text-gray-300 mt-1">{message.length}/1000</p>
            </div>

            <button
              type="submit"
              disabled={status === "sending" || !message.trim()}
              className="w-full py-2.5 rounded-xl text-sm font-semibold text-white transition-all disabled:opacity-50"
              style={{ background: "#1a8754" }}
            >
              {status === "sending" ? "Sending…" : "Send Feedback"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
