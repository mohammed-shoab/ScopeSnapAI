/**
 * v3 — Estimate Builder
 * Screens 5+6+8 — Builder → Output → Send
 * Redesigned with:
 *   - Full labor / parts / permit cost breakdown per line item
 *   - Inline edit & delete per line item
 *   - Repair vs. Replace toggle per option
 *   - Steve Jobs principles: clean, purposeful, no clutter
 */
"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@clerk/nextjs";
import { API_URL } from "@/lib/api";
import { trackEvent } from "@/lib/tracking";
import { ph } from "@/providers/PostHogProvider";
import PresentMode from "@/components/PresentMode";

const IS_DEV = process.env.NEXT_PUBLIC_ENV === "development";
const DEV_HEADER = { "X-Dev-Clerk-User-Id": "test_user_mike" };

type Tab = "estimate" | "output" | "send" | "saved";
type JobType = "repair" | "replace";
type ItemCategory = "labor" | "parts" | "permit" | "disposal" | "other";

interface LineItem {
  category: string;
  item_type?: ItemCategory;
  description?: string;
  label?: string;
  quantity?: number;
  // Detailed breakdown
  labor_hours?: number;
  labor_rate?: number;    // $/hr
  parts_cost?: number;
  permit_cost?: number;
  disposal_cost?: number;
  // Totals
  total?: number;
  amount?: number;
}

interface EnergySavings {
  annual_savings: number;
  five_year_savings: number;
  seer_improvement_pct?: number;
  current_seer?: number;
  new_seer?: number;
}

interface Option {
  tier: string;
  name: string;
  description?: string;
  total: number;
  subtotal?: number;
  markup_percent?: number;
  five_year_total?: number;
  line_items?: LineItem[];
  energy_savings?: EnergySavings | number;
  job_type?: JobType;
}

interface EstimateData {
  id: string;
  assessment_id: string;
  report_short_id: string;
  report_token: string;
  status: string;
  options: Option[];
  markup_percent: number;
  total_amount?: number;
  contractor_pdf_url?: string;
  homeowner_report_url?: string;
  created_at?: string;
  viewed_at?: string;
  view_count?: number;
}

function fmt(n?: number) {
  return n != null ? "$" + n.toLocaleString("en-US", { maximumFractionDigits: 0 }) : "—";
}

function fmtHr(n?: number) {
  return n != null ? n.toFixed(1).replace(/\.0$/, "") + "h" : "";
}

/** Compute the raw cost of a line item (before markup) */
function itemRawCost(item: LineItem): number {
  if (item.item_type === "labor" && item.labor_hours != null && item.labor_rate != null) {
    return item.labor_hours * item.labor_rate * (item.quantity ?? 1);
  }
  if (item.parts_cost != null) return item.parts_cost;
  if (item.permit_cost != null) return item.permit_cost;
  if (item.disposal_cost != null) return item.disposal_cost;
  return item.total ?? item.amount ?? 0;
}

/** Blank item template for "Add line item" */
function blankItem(type: ItemCategory = "labor"): LineItem {
  return {
    category: type === "labor" ? "Labor" : type === "parts" ? "Parts & Equipment" : "Fees",
    item_type: type,
    description: "",
    labor_hours: type === "labor" ? 1 : undefined,
    labor_rate: type === "labor" ? 95 : undefined,
    parts_cost: type === "parts" ? 0 : undefined,
    permit_cost: type === "permit" ? 0 : undefined,
    disposal_cost: type === "disposal" ? 0 : undefined,
    total: 0,
    amount: 0,
  };
}

// ─── Category grouping helpers ────────────────────────────────────────────────
const LABOR_KEYWORDS = ["install", "labor", "work", "service", "repair", "wiring", "hook", "charge"];
const PARTS_KEYWORDS = ["unit", "coil", "refrigerant", "freon", "capacitor", "contactor", "filter",
  "compressor", "motor", "blower", "board", "sensor", "valve", "drain", "duct", "equipment"];
const FEES_KEYWORDS = ["permit", "disposal", "haul", "fee", "dump", "removal"];

function inferItemType(item: LineItem): ItemCategory {
  if (item.item_type) return item.item_type;
  const text = (item.description || item.label || item.category || "").toLowerCase();
  if (FEES_KEYWORDS.some((k) => text.includes(k))) return text.includes("disposal") || text.includes("haul") ? "disposal" : "permit";
  if (PARTS_KEYWORDS.some((k) => text.includes(k))) return "parts";
  if (LABOR_KEYWORDS.some((k) => text.includes(k))) return "labor";
  if (item.labor_hours != null) return "labor";
  if (item.parts_cost != null) return "parts";
  if (item.permit_cost != null) return "permit";
  if (item.disposal_cost != null) return "disposal";
  return "other";
}

function groupItems(items: LineItem[]): Record<string, LineItem[]> {
  const groups: Record<string, LineItem[]> = { labor: [], parts: [], fees: [], other: [] };
  items.forEach((item) => {
    const t = inferItemType(item);
    if (t === "labor") groups.labor.push(item);
    else if (t === "parts") groups.parts.push(item);
    else if (t === "permit" || t === "disposal") groups.fees.push(item);
    else groups.other.push(item);
  });
  return groups;
}

// ─── Inline Edit Form ─────────────────────────────────────────────────────────
interface EditFormProps {
  draft: LineItem;
  onChange: (d: LineItem) => void;
  onSave: () => void;
  onCancel: () => void;
  onDelete: () => void;
  isNew?: boolean;
}

function EditForm({ draft, onChange, onSave, onCancel, onDelete, isNew }: EditFormProps) {
  const type = inferItemType(draft);
  return (
    <div className="mt-1 mb-2 bg-white border border-brand-green rounded-xl p-3 space-y-2.5 shadow-sm">
      {/* Type selector */}
      <div className="flex gap-1.5 flex-wrap">
        {(["labor", "parts", "permit", "disposal"] as ItemCategory[]).map((t) => (
          <button
            key={t}
            onClick={() => onChange({ ...draft, item_type: t,
              labor_hours: t === "labor" ? (draft.labor_hours ?? 1) : undefined,
              labor_rate: t === "labor" ? (draft.labor_rate ?? 95) : undefined,
              parts_cost: t === "parts" ? (draft.parts_cost ?? 0) : undefined,
              permit_cost: t === "permit" ? (draft.permit_cost ?? 0) : undefined,
              disposal_cost: t === "disposal" ? (draft.disposal_cost ?? 0) : undefined,
            })}
            className={`text-xs px-2.5 py-1 rounded-full font-semibold transition-colors ${
              type === t
                ? "bg-brand-green text-white"
                : "bg-surface-secondary text-text-secondary hover:bg-surface-border"
            }`}
          >
            {t === "labor" ? "⏱ Labor" : t === "parts" ? "🔧 Parts" : t === "permit" ? "📋 Permit" : "🗑 Disposal"}
          </button>
        ))}
      </div>

      {/* Description */}
      <input
        autoFocus
        value={draft.description || draft.label || ""}
        onChange={(e) => onChange({ ...draft, description: e.target.value })}
        placeholder={
          type === "labor" ? "e.g. AC unit installation" :
          type === "parts" ? "e.g. Carrier 2-ton AC unit" :
          type === "permit" ? "e.g. HVAC permit" :
          "e.g. Old equipment haul-away"
        }
        className="w-full border border-surface-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-green focus:ring-1 focus:ring-brand-green focus:ring-opacity-30"
      />

      {/* Labor-specific: hours × rate */}
      {type === "labor" && (
        <div className="flex gap-2">
          <div className="flex-1">
            <label className="text-[10px] text-text-secondary font-semibold uppercase tracking-wider block mb-1">Hours</label>
            <input
              type="number"
              min={0.5}
              step={0.5}
              value={draft.labor_hours ?? 1}
              onChange={(e) => onChange({ ...draft, labor_hours: parseFloat(e.target.value) || 0 })}
              className="w-full border border-surface-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-green"
            />
          </div>
          <div className="flex-1">
            <label className="text-[10px] text-text-secondary font-semibold uppercase tracking-wider block mb-1">Rate ($/hr)</label>
            <input
              type="number"
              min={0}
              step={5}
              value={draft.labor_rate ?? 95}
              onChange={(e) => onChange({ ...draft, labor_rate: parseFloat(e.target.value) || 0 })}
              className="w-full border border-surface-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-green"
            />
          </div>
          <div className="flex-shrink-0">
            <label className="text-[10px] text-text-secondary font-semibold uppercase tracking-wider block mb-1">Qty</label>
            <input
              type="number"
              min={1}
              step={1}
              value={draft.quantity ?? 1}
              onChange={(e) => onChange({ ...draft, quantity: parseInt(e.target.value) || 1 })}
              className="w-16 border border-surface-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-green"
            />
          </div>
        </div>
      )}

      {/* Parts cost */}
      {type === "parts" && (
        <div>
          <label className="text-[10px] text-text-secondary font-semibold uppercase tracking-wider block mb-1">Parts Cost ($)</label>
          <input
            type="number"
            min={0}
            step={10}
            value={draft.parts_cost ?? 0}
            onChange={(e) => onChange({ ...draft, parts_cost: parseFloat(e.target.value) || 0 })}
            className="w-full border border-surface-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-green"
          />
        </div>
      )}

      {/* Permit cost */}
      {type === "permit" && (
        <div>
          <label className="text-[10px] text-text-secondary font-semibold uppercase tracking-wider block mb-1">Permit Fee ($)</label>
          <input
            type="number"
            min={0}
            step={25}
            value={draft.permit_cost ?? 0}
            onChange={(e) => onChange({ ...draft, permit_cost: parseFloat(e.target.value) || 0 })}
            className="w-full border border-surface-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-green"
          />
        </div>
      )}

      {/* Disposal cost */}
      {type === "disposal" && (
        <div>
          <label className="text-[10px] text-text-secondary font-semibold uppercase tracking-wider block mb-1">Disposal Cost ($)</label>
          <input
            type="number"
            min={0}
            step={25}
            value={draft.disposal_cost ?? 0}
            onChange={(e) => onChange({ ...draft, disposal_cost: parseFloat(e.target.value) || 0 })}
            className="w-full border border-surface-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand-green"
          />
        </div>
      )}

      {/* Preview cost */}
      <div className="flex items-center justify-between text-xs font-mono text-brand-green font-bold pt-1">
        <span className="text-text-secondary font-sans font-normal">Line total</span>
        <span>{fmt(itemRawCost({ ...draft, item_type: type as ItemCategory }))}</span>
      </div>

      {/* Action buttons */}
      <div className="flex gap-2 pt-1">
        <button
          onClick={onSave}
          className="flex-1 bg-brand-green text-white text-xs font-bold py-2 rounded-lg hover:shadow-md transition-shadow"
        >
          {isNew ? "Add" : "Save"}
        </button>
        <button
          onClick={onCancel}
          className="flex-1 border border-surface-border text-text-secondary text-xs font-semibold py-2 rounded-lg hover:bg-surface-secondary transition-colors"
        >
          Cancel
        </button>
        {!isNew && (
          <button
            onClick={onDelete}
            className="px-3 py-2 border border-red-200 text-red-500 text-xs font-semibold rounded-lg hover:bg-red-50 transition-colors"
          >
            Delete
          </button>
        )}
      </div>
    </div>
  );
}

// ─── Category Section Header ──────────────────────────────────────────────────
function CategoryHeader({ label, icon }: { label: string; icon: string }) {
  return (
    <div className="flex items-center gap-2 mt-4 mb-1 first:mt-0">
      <span className="text-xs">{icon}</span>
      <span className="text-[10px] font-bold uppercase tracking-widest font-mono text-text-secondary">
        {label}
      </span>
      <div className="flex-1 h-px bg-surface-border" />
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────
export default function EstimatePage() {
  const { id } = useParams<{ id: string }>();
  const { getToken } = useAuth();

  const getAuthHeaders = useCallback(async (): Promise<Record<string, string>> => {
    if (IS_DEV) return DEV_HEADER;
    const token = await getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }, [getToken]);
  const [estimate, setEstimate] = useState<EstimateData | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<Tab>("estimate");

  // Markup — collapsed by default (Steve Jobs: hide complexity)
  const [markup, setMarkup] = useState(35);
  const [markupOpen, setMarkupOpen] = useState(false);
  const [markupUpdating, setMarkupUpdating] = useState(false);

  const [selectedTier, setSelectedTier] = useState("better");

  // Repair / Replace toggle per option tier
  const [jobTypes, setJobTypes] = useState<Record<string, JobType>>({});

  // Local line items state (editable, not persisted to API yet)
  const [localItems, setLocalItems] = useState<Record<string, LineItem[]>>({});

  // Editing state: { tier, idx } or null; idx === -1 means "adding new"
  const [editingItem, setEditingItem] = useState<{ tier: string; idx: number } | null>(null);
  const [editDraft, setEditDraft] = useState<LineItem | null>(null);

  // Present Mode
  const [presenting, setPresenting] = useState(false);

  // Output/Send state
  const [docsLoading, setDocsLoading] = useState(false);
  const [docsDone, setDocsDone] = useState(false);
  const [sendEmail, setSendEmail] = useState("");
  const [sendPhone, setSendPhone] = useState("");
  const [homeownerName, setHomeownerName] = useState("");
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Feedback loop — "Did you send as-is or adjust?" (Musk/Zuckerberg req: AI training signal)
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [feedbackStep, setFeedbackStep] = useState<"ask" | "amount">("ask");
  const [correctionAmount, setCorrectionAmount] = useState("");

  useEffect(() => {
    (async () => {
      const headers = await getAuthHeaders();
      fetch(`${API_URL}/api/estimates/${id}`, { headers })
        .then((r) => r.json())
        .then((data: EstimateData) => {
          setEstimate(data);
          setMarkup(data.markup_percent || 35);
          setLoading(false);
          if (data.contractor_pdf_url) setDocsDone(true);
          ph.estimateGenerated(String(id), data.card_name);
          // Pre-fill send fields from property data returned by estimate endpoint
          const d = data as EstimateData & { customer_email?: string; customer_phone?: string; customer_name?: string };
          if (d.customer_email) setSendEmail(d.customer_email);
          if (d.customer_phone) setSendPhone(d.customer_phone);
          if (d.customer_name) setHomeownerName(d.customer_name);
          // Init local items & job types from API data
          const items: Record<string, LineItem[]> = {};
          const jt: Record<string, JobType> = {};
          (data.options || []).forEach((opt) => {
            items[opt.tier] = [...(opt.line_items || [])];
            jt[opt.tier] = opt.job_type || "replace";
          });
          setLocalItems(items);
          setJobTypes(jt);
        })
        .catch(() => setLoading(false));
    })();
  }, [id, getAuthHeaders]);

  // Recompute option totals from local items + markup
  function computeTotal(tier: string): number {
    const items = localItems[tier] || [];
    const subtotal = items.reduce((s, item) => s + itemRawCost(item), 0);
    return Math.round(subtotal * (1 + markup / 100));
  }

  const updateMarkup = async (val: number) => {
    if (!estimate) return;
    setMarkupUpdating(true);
    try {
      const authHeaders = await getAuthHeaders();
      const r = await fetch(`${API_URL}/api/estimates/${id}`, {
        method: "PATCH",
        headers: { ...authHeaders, "Content-Type": "application/json" },
        body: JSON.stringify({ markup_percent: val }),
      });
      if (r.ok) {
        const updated: EstimateData = await r.json();
        setEstimate(updated);
      }
    } catch {
      /* ignore */
    } finally {
      setMarkupUpdating(false);
    }
  };

  const generateDocuments = async () => {
    setDocsLoading(true);
    setError(null);
    try {
      const authHeaders = await getAuthHeaders();
      const r = await fetch(`${API_URL}/api/estimates/${id}/documents`, {
        method: "POST",
        headers: authHeaders,
      });
      if (!r.ok) throw new Error((await r.json()).detail);
      const data = await r.json();
      setEstimate((prev) =>
        prev
          ? { ...prev, contractor_pdf_url: data.contractor_pdf_url, homeowner_report_url: data.homeowner_report_url }
          : prev
      );
      setDocsDone(true);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed");
    } finally {
      setDocsLoading(false);
    }
  };

  const sendEstimate = async () => {
    if (!sendEmail && !sendPhone) { setError("Enter email or phone to send the estimate."); return; }
    setSending(true);
    setError(null);
    try {
      const authHeaders = await getAuthHeaders();
      const r = await fetch(`${API_URL}/api/estimates/${id}/send`, {
        method: "POST",
        headers: { ...authHeaders, "Content-Type": "application/json" },
        body: JSON.stringify({ homeowner_name: homeownerName, homeowner_email: sendEmail, homeowner_phone: sendPhone }),
      });
      if (!r.ok) {
        const body = await r.json().catch(() => ({}));
        throw new Error(body.detail || `Send failed (${r.status})`);
      }
      // SOW Task 1.10 — track successful email send
      trackEvent("email_sent", { estimate_id: id, homeowner_name: homeownerName });
      setSent(true);
    } catch (e: unknown) {
      trackEvent("email_failed", { estimate_id: id });
      setError(e instanceof Error ? e.message : "Send failed. Check connection and try again.");
    } finally {
      setSending(false);
    }
  };

  const saveToHistory = async () => {
    try {
      const authHeaders = await getAuthHeaders();
      await fetch(`${API_URL}/api/assessments/${estimate?.assessment_id}/complete`, {
        method: "POST",
        headers: authHeaders,
      });
    } catch { /* ignore */ }
    setTab("saved");
  };

  // ── Helpers for line item editing ──────────────────────────────────────────
  function startEdit(tier: string, idx: number) {
    const items = localItems[tier] || [];
    setEditingItem({ tier, idx });
    setEditDraft({ ...items[idx] });
  }

  function startAdd(tier: string, type: ItemCategory = "labor") {
    setEditingItem({ tier, idx: -1 });
    setEditDraft(blankItem(type));
  }

  function saveEdit() {
    if (!editingItem || !editDraft) return;
    const { tier, idx } = editingItem;
    const cost = itemRawCost(editDraft);
    const updatedDraft = { ...editDraft, total: cost, amount: cost };
    setLocalItems((prev) => {
      const items = [...(prev[tier] || [])];
      if (idx === -1) {
        items.push(updatedDraft);
      } else {
        items[idx] = updatedDraft;
      }
      return { ...prev, [tier]: items };
    });
    setEditingItem(null);
    setEditDraft(null);
  }

  function deleteItem(tier: string, idx: number) {
    setLocalItems((prev) => {
      const items = [...(prev[tier] || [])];
      items.splice(idx, 1);
      return { ...prev, [tier]: items };
    });
    setEditingItem(null);
    setEditDraft(null);
  }

  function cancelEdit() {
    setEditingItem(null);
    setEditDraft(null);
  }

  // ── Loading / Not found ────────────────────────────────────────────────────
  if (loading)
    return (
      <div className="pt-20 text-center text-text-secondary">
        <div className="spinner w-8 h-8 border-2 border-brand-green border-t-transparent rounded-full mx-auto mb-3" />
        Loading estimate...
      </div>
    );
  if (!estimate)
    return (
      <div className="pt-20 text-center">
        <p className="text-brand-red font-medium">Estimate not found.</p>
        <Link href="/dashboard" className="text-sm text-brand-green mt-2 block">← Back to Dashboard</Link>
      </div>
    );

  const options = estimate.options || [];
  const selectedOption = options.find((o) => o.tier === selectedTier) || options[0];

  // ── Saved Screen ──────────────────────────────────────────────────────────
  if (tab === "saved")
    return (
      <div className="max-w-md mx-auto pt-16 text-center space-y-6">
        <div className="text-6xl">✅</div>
        <h2 className="text-2xl font-extrabold">Job Saved!</h2>
        <p className="text-text-secondary">The assessment has been saved to property history.</p>
        <div className="card p-4 text-left space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-text-secondary">Report ID</span>
            <span className="font-mono font-bold">{estimate.report_short_id}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-text-secondary">Status</span>
            <span className="font-semibold text-brand-green">Sent</span>
          </div>
          {estimate.homeowner_report_url && (
            <div className="flex justify-between text-sm">
              <span className="text-text-secondary">Report URL</span>
              <span className="font-mono text-xs text-brand-green truncate">{estimate.homeowner_report_url}</span>
            </div>
          )}
        </div>
        <Link href="/dashboard" className="block w-full bg-brand-green text-white font-bold py-4 rounded-xl text-center">
          Back to Dashboard →
        </Link>
      </div>
    );

  // ── Main Layout ────────────────────────────────────────────────────────────
  return (
    <div className="max-w-2xl mx-auto space-y-4 pb-8">
      {/* Present Mode overlay */}
      {presenting && (
        <PresentMode
          estimate={estimate}
          selectedTier={selectedTier}
          onClose={() => setPresenting(false)}
          onSelectTier={(tier) => { setSelectedTier(tier); setPresenting(false); }}
        />
      )}
      {/* Header */}
      <div className="flex items-center gap-3 pt-4">
        <Link href="/dashboard" className="text-sm text-text-secondary hover:text-text-primary">← Back</Link>
        <h1 className="text-xl font-extrabold flex-1">Estimate Builder</h1>
        <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
          estimate.status === "approved" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
        }`}>
          {estimate.report_short_id}
        </span>
      </div>

      {/* Tab Bar */}
      <div className="flex gap-1 bg-surface-secondary rounded-xl p-1">
        {(["estimate", "output", "send"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 py-2.5 text-sm font-semibold rounded-lg transition-colors ${
              tab === t ? "bg-white shadow-sm text-text-primary" : "text-text-secondary"
            }`}
          >
            {t === "estimate" ? (
              <span className="flex items-center justify-center gap-1.5">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
                Builder
              </span>
            ) : t === "output" ? (
              <span className="flex items-center justify-center gap-1.5">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                Output
              </span>
            ) : (
              <span className="flex items-center justify-center gap-1.5">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                Send
              </span>
            )}
          </button>
        ))}
      </div>

      {/* ══ BUILDER TAB ══════════════════════════════════════════════════════ */}
      {tab === "estimate" && (
        <>
          {/* Markup — collapsed disclosure */}
          <div className="card overflow-hidden">
            <button
              onClick={() => setMarkupOpen((o) => !o)}
              className="w-full flex items-center justify-between px-4 py-3 hover:bg-surface-secondary transition-colors"
            >
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-text-primary">⚙ Company Markup</span>
                <span className="text-xs text-text-secondary font-mono bg-surface-secondary px-2 py-0.5 rounded-full">
                  {markup}% applied
                </span>
                {markupUpdating && (
                  <span className="text-xs text-brand-green animate-pulse">saving…</span>
                )}
              </div>
              <span className="text-text-secondary text-xs">{markupOpen ? "▲" : "▼"}</span>
            </button>
            {markupOpen && (
              <div className="px-4 pb-4 border-t border-surface-border">
                <div className="flex justify-between items-center mt-3 mb-2">
                  <span className="text-xs text-text-secondary">Drag to adjust</span>
                  <span className="text-xl font-mono font-bold text-brand-green">{markup}%</span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={markup}
                  onChange={(e) => setMarkup(Number(e.target.value))}
                  onMouseUp={() => updateMarkup(markup)}
                  onTouchEnd={() => updateMarkup(markup)}
                  className="w-full accent-brand-green cursor-pointer"
                />
                <div className="flex justify-between text-xs text-text-secondary mt-1">
                  <span>0%</span><span>50%</span><span>100%</span>
                </div>
              </div>
            )}
          </div>

          {/* Option Cards */}
          <div className="space-y-4">
            {options.map((opt) => {
              const isSelected = selectedTier === opt.tier;
              const isRec = opt.tier === "better";
              const jobType = jobTypes[opt.tier] || "replace";
              const items = localItems[opt.tier] || [];
              const groups = groupItems(items);

              // Compute totals from local items
              const subtotal = items.reduce((s, item) => s + itemRawCost(item), 0);
              const markupAmt = Math.round(subtotal * markup / 100);
              const displayTotal = subtotal > 0 ? subtotal + markupAmt : opt.total;
              const displaySubtotal = subtotal > 0 ? subtotal : (opt.subtotal || Math.round(opt.total / (1 + markup / 100)));

              // Card styling per tier
              let borderColor = "border-surface-border";
              let headerBg = "bg-gray-50";
              let badgeBg = "bg-gray-200 text-gray-700";
              let priceColor = "text-text-primary";
              let ringClass = "";
              if (opt.tier === "better") {
                headerBg = "bg-brand-green-light";
                badgeBg = "bg-brand-green text-white";
                priceColor = "text-brand-green";
              } else if (opt.tier === "best") {
                headerBg = "bg-blue-50";
                badgeBg = "bg-brand-blue text-white";
                priceColor = "text-brand-blue";
              }
              if (isSelected) {
                borderColor = "border-brand-green";
                ringClass = "ring-2 ring-brand-green ring-opacity-40";
              }

              const isEditingThis = (idx: number) =>
                editingItem?.tier === opt.tier && editingItem?.idx === idx;
              const isAddingThis = editingItem?.tier === opt.tier && editingItem?.idx === -1;

              return (
                <div
                  key={opt.tier}
                  onClick={() => setSelectedTier(opt.tier)}
                  className={`card cursor-pointer transition-all border-2 ${borderColor} ${ringClass}`}
                >
                  {/* ── Card Header ── */}
                  <div className={`px-4 py-3 ${headerBg}`}>
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        {/* Badge + Repair/Replace toggle */}
                        <div className="flex items-center gap-2 mb-2 flex-wrap">
                          <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${badgeBg}`}>
                            Option {opt.tier === "good" ? "A" : opt.tier === "better" ? "B" : "C"}
                            {isRec && " — ★ REC"}
                          </span>
                          {/* Repair / Replace segmented control */}
                          <div
                            className="flex bg-white rounded-full border border-surface-border p-0.5 shadow-sm"
                            onClick={(e) => e.stopPropagation()}
                          >
                            {(["repair", "replace"] as JobType[]).map((jt) => (
                              <button
                                key={jt}
                                onClick={() => setJobTypes((prev) => ({ ...prev, [opt.tier]: jt }))}
                                className={`text-xs font-semibold px-3 py-1 rounded-full transition-all ${
                                  jobType === jt
                                    ? "bg-brand-green text-white shadow-sm"
                                    : "text-text-secondary hover:text-text-primary"
                                }`}
                              >
                                {jt === "repair" ? "🔧 Repair" : "🔄 Replace"}
                              </button>
                            ))}
                          </div>
                        </div>
                        <h3 className="font-bold text-base text-text-primary leading-tight">{opt.name}</h3>
                        {opt.description && (
                          <p className="text-xs text-text-secondary mt-0.5 leading-snug">{opt.description}</p>
                        )}
                      </div>
                      <div className="text-right flex-shrink-0">
                        <p className={`text-2xl font-mono font-bold ${priceColor}`}>{fmt(displayTotal)}</p>
                        {opt.five_year_total && (
                          <p className="text-xs text-text-secondary mt-0.5">{fmt(opt.five_year_total)} / 5yr</p>
                        )}
                        {opt.energy_savings && (() => {
                          const ann = typeof opt.energy_savings === "object"
                            ? (opt.energy_savings as EnergySavings).annual_savings
                            : (opt.energy_savings as number);
                          return ann > 0 ? (
                            <p className="text-xs text-brand-green font-semibold mt-0.5">
                              Saves ${ann.toLocaleString()}/yr
                            </p>
                          ) : null;
                        })()}
                      </div>
                    </div>
                  </div>

                  {/* ── Line Items ── */}
                  <div
                    className="px-4 pt-2 pb-3 bg-white space-y-0"
                    onClick={(e) => e.stopPropagation()}
                  >
                    {/* Labor section */}
                    {(groups.labor.length > 0 || groups.other.length > 0) && (
                      <>
                        <CategoryHeader label="Labor" icon="⏱" />
                        {[...groups.labor, ...groups.other].map((item) => {
                          const globalIdx = items.indexOf(item);
                          const type = inferItemType(item);
                          const cost = itemRawCost(item);
                          const isEditing = isEditingThis(globalIdx);
                          return (
                            <div key={globalIdx}>
                              {isEditing && editDraft ? (
                                <EditForm
                                  draft={editDraft}
                                  onChange={setEditDraft}
                                  onSave={saveEdit}
                                  onCancel={cancelEdit}
                                  onDelete={() => deleteItem(opt.tier, globalIdx)}
                                />
                              ) : (
                                <div className="flex items-center gap-2 py-1.5 group">
                                  <div className="flex-1 min-w-0">
                                    <span className="text-sm text-text-primary">
                                      {item.description || item.label || "Labor item"}
                                    </span>
                                    {type === "labor" && item.labor_hours != null && item.labor_rate != null && (
                                      <span className="text-xs text-text-secondary ml-2 font-mono">
                                        {fmtHr(item.labor_hours)} × ${item.labor_rate}/hr
                                        {(item.quantity || 1) > 1 && ` × ${item.quantity}`}
                                      </span>
                                    )}
                                  </div>
                                  <span className="font-mono text-sm font-semibold text-text-primary whitespace-nowrap">
                                    {fmt(cost)}
                                  </span>
                                  <button
                                    onClick={() => startEdit(opt.tier, globalIdx)}
                                    className="text-text-secondary hover:text-brand-green transition-colors opacity-0 group-hover:opacity-100 text-xs px-1.5 py-1 rounded hover:bg-surface-secondary"
                                    title="Edit"
                                  >
                                    ✏
                                  </button>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </>
                    )}

                    {/* Parts & Equipment section */}
                    {groups.parts.length > 0 && (
                      <>
                        <CategoryHeader label="Parts & Equipment" icon="🔧" />
                        {groups.parts.map((item) => {
                          const globalIdx = items.indexOf(item);
                          const cost = itemRawCost(item);
                          const isEditing = isEditingThis(globalIdx);
                          return (
                            <div key={globalIdx}>
                              {isEditing && editDraft ? (
                                <EditForm
                                  draft={editDraft}
                                  onChange={setEditDraft}
                                  onSave={saveEdit}
                                  onCancel={cancelEdit}
                                  onDelete={() => deleteItem(opt.tier, globalIdx)}
                                />
                              ) : (
                                <div className="flex items-center gap-2 py-1.5 group">
                                  <div className="flex-1 min-w-0">
                                    <span className="text-sm text-text-primary">
                                      {item.description || item.label || "Part"}
                                    </span>
                                    {(item.quantity || 1) > 1 && (
                                      <span className="text-xs text-text-secondary ml-2 font-mono">
                                        × {item.quantity}
                                      </span>
                                    )}
                                  </div>
                                  <span className="font-mono text-sm font-semibold text-text-primary whitespace-nowrap">
                                    {fmt(cost)}
                                  </span>
                                  <button
                                    onClick={() => startEdit(opt.tier, globalIdx)}
                                    className="text-text-secondary hover:text-brand-green transition-colors opacity-0 group-hover:opacity-100 text-xs px-1.5 py-1 rounded hover:bg-surface-secondary"
                                    title="Edit"
                                  >
                                    ✏
                                  </button>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </>
                    )}

                    {/* Fees section */}
                    {groups.fees.length > 0 && (
                      <>
                        <CategoryHeader label="Fees" icon="📋" />
                        {groups.fees.map((item) => {
                          const globalIdx = items.indexOf(item);
                          const cost = itemRawCost(item);
                          const isEditing = isEditingThis(globalIdx);
                          return (
                            <div key={globalIdx}>
                              {isEditing && editDraft ? (
                                <EditForm
                                  draft={editDraft}
                                  onChange={setEditDraft}
                                  onSave={saveEdit}
                                  onCancel={cancelEdit}
                                  onDelete={() => deleteItem(opt.tier, globalIdx)}
                                />
                              ) : (
                                <div className="flex items-center gap-2 py-1.5 group">
                                  <div className="flex-1 min-w-0">
                                    <span className="text-sm text-text-primary">
                                      {item.description || item.label || "Fee"}
                                    </span>
                                  </div>
                                  <span className="font-mono text-sm font-semibold text-text-primary whitespace-nowrap">
                                    {fmt(cost)}
                                  </span>
                                  <button
                                    onClick={() => startEdit(opt.tier, globalIdx)}
                                    className="text-text-secondary hover:text-brand-green transition-colors opacity-0 group-hover:opacity-100 text-xs px-1.5 py-1 rounded hover:bg-surface-secondary"
                                    title="Edit"
                                  >
                                    ✏
                                  </button>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </>
                    )}

                    {/* New item add form (inline) */}
                    {isAddingThis && editDraft && (
                      <EditForm
                        draft={editDraft}
                        onChange={setEditDraft}
                        onSave={saveEdit}
                        onCancel={cancelEdit}
                        onDelete={cancelEdit}
                        isNew
                      />
                    )}

                    {/* Add line item — one tap, opens inline form defaulting to Labor */}
                    {!isAddingThis && (
                      <div className="mt-3">
                        <button
                          onClick={() => startAdd(opt.tier, "labor")}
                          className="text-xs font-semibold text-brand-green hover:underline flex items-center gap-1"
                        >
                          <span className="text-base leading-none">＋</span> Add line item
                        </button>
                      </div>
                    )}

                    {/* Subtotal / Markup / Total summary */}
                    {(items.length > 0 || subtotal > 0) && (
                      <div className="mt-3 pt-3 border-t border-surface-border space-y-1">
                        <div className="flex justify-between text-xs text-text-secondary">
                          <span>Subtotal (cost)</span>
                          <span className="font-mono">{fmt(displaySubtotal)}</span>
                        </div>
                        <div className="flex justify-between text-xs text-text-secondary">
                          <span>Markup ({markup}%)</span>
                          <span className="font-mono">
                            +{fmt(subtotal > 0 ? markupAmt : opt.total - (opt.subtotal || Math.round(opt.total / (1 + markup / 100))))}
                          </span>
                        </div>
                        <div className={`flex justify-between text-sm font-bold pt-1 ${priceColor}`}>
                          <span>Total</span>
                          <span className="font-mono">{fmt(displayTotal)}</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* 5-Year Cost Comparison Table */}
          {options.length > 1 && options.some((o) => o.five_year_total) && (
            <div className="bg-white rounded-xl border border-surface-border overflow-hidden shadow-sm">
              <div className="px-4 py-3 border-b border-surface-border">
                <p className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary mb-0.5">
                  5-Year Total Cost
                </p>
                <p className="text-sm font-bold text-text-primary">Side-by-Side Comparison</p>
              </div>
              <div>
                <table className="w-full text-sm">
                  <thead className="bg-surface-bg border-b border-surface-border">
                    <tr>
                      <th className="px-3 py-2.5 text-left text-xs font-bold uppercase tracking-widest font-mono text-text-secondary">Option</th>
                      <th className="px-2 py-2.5 text-right text-xs font-bold uppercase tracking-widest font-mono text-text-secondary">Install</th>
                      <th className="px-2 py-2.5 text-right text-xs font-bold uppercase tracking-widest font-mono text-text-secondary">5-Yr Total</th>
                      <th className="px-2 py-2.5 text-right text-xs font-bold uppercase tracking-widest font-mono text-text-secondary">Savings</th>
                    </tr>
                  </thead>
                  <tbody>
                    {options.map((opt) => {
                      const isSelected = selectedTier === opt.tier;
                      const annualSavings = opt.energy_savings
                        ? typeof opt.energy_savings === "object"
                          ? (opt.energy_savings as EnergySavings).annual_savings
                          : (opt.energy_savings as number)
                        : null;
                      const tierColors: Record<string, string> = {
                        good: "text-text-primary", better: "text-brand-green", best: "text-brand-blue",
                      };
                      return (
                        <tr
                          key={opt.tier}
                          onClick={() => setSelectedTier(opt.tier)}
                          className={`border-b border-surface-border cursor-pointer transition-colors ${
                            isSelected ? "bg-brand-green-light" : "hover:bg-surface-bg"
                          }`}
                        >
                          <td className="px-3 py-3">
                            <div className="flex items-center gap-1.5">
                              {isSelected && <span className="w-2 h-2 rounded-full bg-brand-green flex-shrink-0" />}
                              <span className={`font-semibold text-xs md:text-sm ${tierColors[opt.tier] || "text-text-primary"}`}>
                                {opt.name}
                              </span>
                            </div>
                          </td>
                          <td className={`px-2 py-3 text-right font-mono font-bold text-xs md:text-sm ${tierColors[opt.tier] || ""}`}>
                            {fmt(opt.total)}
                          </td>
                          <td className="px-2 py-3 text-right font-mono text-text-secondary text-xs md:text-sm">
                            {opt.five_year_total ? fmt(opt.five_year_total) : "—"}
                          </td>
                          <td className="px-2 py-3 text-right">
                            {annualSavings && annualSavings > 0 ? (
                              <span className="text-xs font-semibold text-brand-green">${annualSavings.toLocaleString()}/yr</span>
                            ) : (
                              <span className="text-xs text-text-secondary">—</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              <div className="px-4 py-2.5 bg-surface-bg border-t border-surface-border">
                <p className="text-xs text-text-secondary">
                  5-year total = install cost + estimated operating costs − energy savings. Lower is better value.
                </p>
              </div>
            </div>
          )}

          {/* CTA to Output */}
          <button
            onClick={() => setTab("output")}
            className="w-full bg-brand-green text-white font-bold py-4 rounded-xl text-base shadow-lg shadow-green-200 hover:shadow-xl transition-shadow"
          >
            {selectedOption
              ? `Continue with ${selectedOption.name} (${fmt(selectedOption.total)}) →`
              : "Continue →"}
          </button>
        </>
      )}

      {/* ══ OUTPUT TAB ═══════════════════════════════════════════════════════ */}
      {tab === "output" && (
        <>
          <div className="card p-4 space-y-4">
            <div>
              <p className="font-semibold text-sm">Generate Documents</p>
              <p className="text-xs text-text-secondary mt-1">
                Creates the contractor PDF estimate and homeowner report link.
              </p>
            </div>
            {!docsDone ? (
              <button
                onClick={generateDocuments}
                disabled={docsLoading}
                className="w-full bg-brand-green text-white font-bold py-3 rounded-xl disabled:opacity-50 hover:shadow-lg transition-shadow"
              >
                {docsLoading ? "Generating..." : "Generate Documents →"}
              </button>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm text-brand-green font-semibold">
                  <span className="text-lg">✓</span> Documents ready
                </div>
                {/* View count — Zuckerberg req: show contractor when homeowner views */}
                {estimate.view_count !== undefined && (
                  <div className="flex items-center gap-2 text-xs rounded-lg px-3 py-2 bg-surface-secondary">
                    <span className="text-base">{estimate.view_count > 0 ? "👀" : "⏳"}</span>
                    <span className="text-text-secondary">
                      {estimate.view_count > 0
                        ? <><strong className="text-text-primary">Homeowner</strong>{" viewed the report "}<strong className="text-brand-green">{estimate.view_count}x</strong></>
                        : "Not yet viewed by homeowner"}
                    </span>
                  </div>
                )}
                {estimate.contractor_pdf_url && (
                  <a
                    href={estimate.contractor_pdf_url?.startsWith('http') ? estimate.contractor_pdf_url : `${API_URL}${estimate.contractor_pdf_url}`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-3 p-3 bg-surface-secondary rounded-xl text-sm font-medium hover:bg-surface-border transition-colors group"
                  >
                    <span className="text-xl">📄</span>
                    <div className="flex-1">
                      <p className="font-semibold text-text-primary">Contractor Estimate</p>
                      <p className="text-xs text-text-secondary">{estimate.report_short_id}.pdf</p>
                    </div>
                    <span className="text-text-secondary group-hover:translate-x-1 transition-transform">↗</span>
                  </a>
                )}
                {estimate.homeowner_report_url && (
                  <div className="p-3 bg-surface-secondary rounded-xl">
                    <p className="text-xs text-text-secondary font-semibold mb-2">Report URL</p>
                    <div className="flex items-center gap-2">
                      <code className="flex-1 text-xs font-mono text-brand-green break-all truncate">
                        {estimate.homeowner_report_url}
                      </code>
                      <button
                        onClick={() => navigator.clipboard.writeText(estimate.homeowner_report_url || "")}
                        className="text-xs font-semibold text-brand-green hover:underline whitespace-nowrap ml-2"
                      >
                        Copy
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
            {error && <p className="text-sm text-brand-red">⚠ {error}</p>}
          </div>

          <div className="card p-4">
            <p className="font-semibold text-sm mb-1">Present Mode</p>
            <p className="text-xs text-text-secondary mb-3">Full-screen slideshow to show the homeowner on-site.</p>
            <button
              onClick={() => setPresenting(true)}
              className="w-full py-3 rounded-xl text-sm font-bold text-white transition-shadow hover:shadow-lg"
              style={{ background: "linear-gradient(135deg,#1a1a18 0%,#2a2a28 100%)" }}
            >
              🖥 Present to Homeowner →
            </button>
          </div>

          {docsDone && (
            <button
              onClick={() => setTab("send")}
              className="w-full bg-brand-green text-white font-bold py-4 rounded-xl text-base shadow-lg shadow-green-200 hover:shadow-xl transition-shadow"
            >
              Send to Homeowner →
            </button>
          )}
        </>
      )}

      {/* ══ SEND TAB ═════════════════════════════════════════════════════════ */}
      {tab === "send" && (
        <>
          {sent ? (
            /* ── Success State ── */
            <div className="card p-6 text-center space-y-4">
              <div
                className="mx-auto flex items-center justify-center rounded-full"
                style={{ width: 72, height: 72, background: "linear-gradient(135deg,#1a8754,#159a5e)" }}
              >
                <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-extrabold text-brand-green">Estimate Sent!</h2>
                {homeownerName && (
                  <p className="text-sm text-text-secondary mt-1">{homeownerName} will receive their report shortly.</p>
                )}
              </div>

              {/* ── Estimate Correction Feedback Loop ── */}
              {/* Musk req: capture actual vs AI price as training data */}
              {/* Zuckerberg req: estimate quality signal for product analytics */}
              {!feedbackSubmitted ? (
                <div className="bg-surface-secondary rounded-xl p-4 text-left space-y-3">
                  {feedbackStep === "ask" ? (
                    <>
                      <p className="text-sm font-semibold text-text-primary">Did you adjust the estimate before sending?</p>
                      <p className="text-xs text-text-secondary">Helps us improve AI accuracy for your next job.</p>
                      <div className="flex gap-2">
                        <button
                          onClick={() => {
                            const aiTotal = estimate?.options?.reduce((s, o) => s + (o.total ?? 0), 0) ?? 0;
                            trackEvent("estimate_feedback", { estimate_id: id, adjusted: false, decision: "sent_as_is", ai_total: aiTotal });
                            ph.estimateCorrection(String(id), false, aiTotal, aiTotal);
                            setFeedbackSubmitted(true);
                          }}
                          className="flex-1 py-2.5 text-sm font-semibold rounded-xl border border-surface-border bg-white hover:bg-surface-secondary transition-colors"
                        >
                          ✓ Sent as-is
                        </button>
                        <button
                          onClick={() => setFeedbackStep("amount")}
                          className="flex-1 py-2.5 text-sm font-semibold rounded-xl border border-brand-green text-brand-green bg-white hover:bg-green-50 transition-colors"
                        >
                          ✏ Yes, I adjusted
                        </button>
                      </div>
                    </>
                  ) : (
                    <>
                      <p className="text-sm font-semibold text-text-primary">What was the final total you sent?</p>
                      <p className="text-xs text-text-secondary">
                        AI suggested {estimate?.options ? fmt(estimate.options.reduce((s, o) => Math.max(s, o.total ?? 0), 0)) : "—"} — what did you actually charge?
                      </p>
                      <div className="flex gap-2 items-center">
                        <span className="text-text-secondary font-bold text-sm">$</span>
                        <input
                          type="number"
                          inputMode="numeric"
                          placeholder="e.g. 8500"
                          value={correctionAmount}
                          onChange={(e) => setCorrectionAmount(e.target.value)}
                          className="flex-1 border border-surface-border rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-brand-green bg-white"
                          autoFocus
                        />
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => setFeedbackStep("ask")}
                          className="py-2 px-3 text-xs text-text-secondary rounded-xl border border-surface-border bg-white hover:bg-surface-secondary transition-colors"
                        >
                          ← Back
                        </button>
                        <button
                          onClick={() => {
                            const aiMax = estimate?.options ? estimate.options.reduce((s, o) => Math.max(s, o.total ?? 0), 0) : 0;
                            const actual = correctionAmount ? parseFloat(correctionAmount) : undefined;
                            trackEvent("estimate_feedback", {
                              estimate_id: id,
                              adjusted: true,
                              decision: "adjusted",
                              ai_total: aiMax,
                              actual_total: actual,
                              delta: actual != null ? actual - aiMax : undefined,
                            });
                            ph.estimateCorrection(String(id), true, aiMax, actual);
                            setFeedbackSubmitted(true);
                          }}
                          className="flex-1 py-2.5 text-sm font-semibold rounded-xl bg-brand-green text-white hover:opacity-90 transition-opacity"
                        >
                          Submit →
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ) : (
                <p className="text-xs text-text-secondary bg-surface-secondary rounded-xl py-2.5 px-4">
                  Thanks — that helps us make the AI smarter for your next job.
                </p>
              )}

              <p className="text-xs text-text-secondary">
                Auto follow-ups: 24h if not viewed &middot; 48h if viewed &middot; 7 days final check-in.
              </p>
              {estimate.homeowner_report_url && (
                <>
                  <div className="bg-surface-secondary rounded-xl p-3 font-mono text-xs text-brand-green break-all text-left">
                    {estimate.homeowner_report_url}
                  </div>
                  <button
                    onClick={() => navigator.clipboard.writeText(estimate.homeowner_report_url!)}
                    className="w-full border border-brand-green text-brand-green font-bold py-3 rounded-xl text-sm hover:bg-green-50 transition-colors"
                  >
                    Copy Report Link
                  </button>
                </>
              )}
              <button
                onClick={saveToHistory}
                className="w-full bg-brand-green text-white font-bold py-3 rounded-xl hover:shadow-lg transition-shadow"
              >
                Save to History →
              </button>
            </div>
          ) : (
            /* ── Send Form ── */
            <div className="space-y-4">
              {/* Header */}
              <div className="card p-4 space-y-1">
                <h2 className="font-extrabold text-base">
                  {homeownerName ? `Send to ${homeownerName}` : "Send to Homeowner"}
                </h2>
                <p className="text-xs text-text-secondary">
                  They'll get a personalized report with all options, pricing, and energy savings.
                </p>
              </div>

              <div className="card p-4 space-y-4">
                {/* Homeowner name */}
                <div>
                  <label className="text-xs text-text-secondary block mb-2 font-semibold">Homeowner Name</label>
                  <input
                    type="text"
                    placeholder="Sarah Johnson"
                    value={homeownerName}
                    onChange={(e) => setHomeownerName(e.target.value)}
                    className="w-full border border-surface-border rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-brand-green focus:ring-2 focus:ring-brand-green focus:ring-opacity-20"
                  />
                </div>
                <div>
                  <label className="text-xs text-text-secondary block mb-2 font-semibold">Email Address</label>
                  <input
                    type="email"
                    placeholder="homeowner@email.com"
                    value={sendEmail}
                    onChange={(e) => setSendEmail(e.target.value)}
                    className="w-full border border-surface-border rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-brand-green focus:ring-2 focus:ring-brand-green focus:ring-opacity-20"
                  />
                </div>
                <div>
                  <label className="text-xs text-text-secondary block mb-2 font-semibold">Phone (SMS)</label>
                  <input
                    type="tel"
                    placeholder="(555) 555-5555"
                    value={sendPhone}
                    onChange={(e) => setSendPhone(e.target.value)}
                    className="w-full border border-surface-border rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-brand-green focus:ring-2 focus:ring-brand-green focus:ring-opacity-20"
                  />
                </div>
                <p className="text-xs text-text-secondary">
                  Auto follow-ups: 24h if not viewed &middot; 48h if viewed &middot; 7 days final check-in.
                </p>
              </div>

              {/* Report link preview */}
              {estimate.homeowner_report_url && (
                <div className="card p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-semibold">Report Link</p>
                    <button
                      onClick={() => navigator.clipboard.writeText(estimate.homeowner_report_url!)}
                      className="text-xs text-brand-green font-semibold hover:underline"
                    >
                      Copy
                    </button>
                  </div>
                  <div className="bg-surface-secondary rounded-lg p-3 font-mono text-xs text-brand-green break-all">
                    {estimate.homeowner_report_url}
                  </div>
                </div>
              )}

              {error && (
                <p className="text-sm text-brand-red bg-brand-red-light p-3 rounded-xl">⚠ {error}</p>
              )}

              <button
                onClick={sendEstimate}
                disabled={sending || (!sendEmail && !sendPhone)}
                className="w-full bg-brand-green text-white font-bold py-4 rounded-xl text-base shadow-lg shadow-green-200 hover:shadow-xl disabled:opacity-40 transition-shadow"
              >
                {sending ? "Sending..." : `Send${homeownerName ? ` to ${homeownerName}` : ""} →`}
              </button>
           