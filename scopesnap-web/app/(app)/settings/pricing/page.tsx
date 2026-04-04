/**
 * Settings — Pricing Rules Editor
 * Live CRUD table for company labor rates, parts costs, and markup overrides.
 * Fetches from GET /api/pricing-rules/, supports inline editing + add/delete.
 */
"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useAuth } from "@clerk/nextjs";
import { API_URL } from "@/lib/api";

const IS_DEV = process.env.NEXT_PUBLIC_ENV === "development";
const DEV_HEADER = { "X-Dev-Clerk-User-Id": "test_user_mike" };
const DEV_CT = { ...DEV_HEADER, "Content-Type": "application/json" };

const EQUIPMENT_TYPES = [
  "ac_unit",
  "furnace",
  "heat_pump",
  "air_handler",
  "mini_split",
  "package_unit",
  "boiler",
];

const JOB_TYPES = [
  "full_system",
  "coil_replacement",
  "compressor_replacement",
  "refrigerant_recharge",
  "maintenance",
  "repair",
  "installation",
];

interface PricingRule {
  id: string;
  company_id: string | null;
  equipment_type: string;
  job_type: string;
  region: string;
  labor_rate: number | null;
  permit_cost: number | null;
  refrigerant_cost_per_lb: number | null;
  parts_cost: { min?: number; max?: number; avg?: number } | null;
  labor_hours: { min?: number; max?: number; avg?: number } | null;
  additional_costs: Record<string, number> | null;
}

const EQUIP_LABELS: Record<string, string> = {
  ac_unit: "AC Unit",
  heat_pump: "Heat Pump",
  furnace: "Furnace",
  boiler: "Boiler",
  air_handler: "Air Handler",
  mini_split: "Mini-Split",
  package_unit: "Package Unit",
};

function labelify(s: string) {
  return EQUIP_LABELS[s] ?? s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function fmt(n?: number | null) {
  if (n == null) return "—";
  return "$" + n.toLocaleString("en-US", { maximumFractionDigits: 0 });
}

const DEFAULT_NEW: Omit<PricingRule, "id" | "company_id"> = {
  equipment_type: "ac_unit",
  job_type: "full_system",
  region: "national",
  labor_rate: null,
  permit_cost: null,
  refrigerant_cost_per_lb: null,
  parts_cost: null,
  labor_hours: null,
  additional_costs: null,
};

export default function PricingRulesPage() {
  const { getToken } = useAuth();
  const [rules, setRules] = useState<PricingRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValues, setEditValues] = useState<Partial<PricingRule>>({});
  const [showAddForm, setShowAddForm] = useState(false);
  const [newRule, setNewRule] = useState({ ...DEFAULT_NEW });
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const getAuthHeaders = useCallback(async (): Promise<Record<string, string>> => {
    if (IS_DEV) return DEV_HEADER;
    const token = await getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }, [getToken]);

  const getAuthCT = useCallback(async (): Promise<Record<string, string>> => {
    if (IS_DEV) return DEV_CT;
    const token = await getToken();
    return token
      ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" }
      : { "Content-Type": "application/json" };
  }, [getToken]);

  useEffect(() => {
    const load = async () => {
      const headers = await getAuthHeaders();
      fetch(`${API_URL}/api/pricing-rules/`, { headers })
        .then((r) => {
          if (!r.ok) throw new Error(`API error ${r.status}`);
          return r.json();
        })
        .then((data) => {
          setRules(Array.isArray(data) ? data : []);
          setLoading(false);
        })
        .catch((e) => {
          setError(e.message || "Could not load pricing rules.");
          setLoading(false);
        });
    };
    load();
  }, [getAuthHeaders]);

  const startEdit = (rule: PricingRule) => {
    setEditingId(rule.id);
    setEditValues({
      labor_rate: rule.labor_rate,
      permit_cost: rule.permit_cost,
      refrigerant_cost_per_lb: rule.refrigerant_cost_per_lb,
    });
    setSaveError(null);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditValues({});
    setSaveError(null);
  };

  const saveEdit = async (ruleId: string) => {
    setSaving(true);
    setSaveError(null);
    try {
      const headers = await getAuthCT();
      const r = await fetch(`${API_URL}/api/pricing-rules/${ruleId}`, {
        method: "PATCH",
        headers,
        body: JSON.stringify(editValues),
      });
      if (!r.ok) {
        const body = await r.json();
        throw new Error(body.detail || "Save failed");
      }
      const updated = await r.json();
      setRules((prev) => prev.map((rule) => (rule.id === ruleId ? updated : rule)));
      setEditingId(null);
      setEditValues({});
    } catch (e: unknown) {
      setSaveError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  };

  const deleteRule = async (ruleId: string) => {
    if (!confirm("Remove this pricing override? The job will revert to national defaults.")) return;
    setDeletingId(ruleId);
    try {
      const headers = await getAuthHeaders();
      const r = await fetch(`${API_URL}/api/pricing-rules/${ruleId}`, {
        method: "DELETE",
        headers,
      });
      if (!r.ok && r.status !== 204) throw new Error("Delete failed");
      setRules((prev) => prev.filter((rule) => rule.id !== ruleId));
    } catch {
      /* ignore */
    } finally {
      setDeletingId(null);
    }
  };

  const createRule = async () => {
    setSaving(true);
    setSaveError(null);
    try {
      const headers = await getAuthCT();
      const r = await fetch(`${API_URL}/api/pricing-rules/`, {
        method: "POST",
        headers,
        body: JSON.stringify(newRule),
      });
      if (!r.ok) {
        const body = await r.json();
        throw new Error(body.detail || "Create failed");
      }
      const created = await r.json();
      setRules((prev) => [...prev, created]);
      setShowAddForm(false);
      setNewRule({ ...DEFAULT_NEW });
    } catch (e: unknown) {
      setSaveError(e instanceof Error ? e.message : "Create failed");
    } finally {
      setSaving(false);
    }
  };

  // Split company overrides from global defaults
  const companyRules = rules.filter((r) => r.company_id !== null);
  const globalRules = rules.filter((r) => r.company_id === null);

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-10">
      {/* Header */}
      <div className="pt-2">
        <div className="flex items-center gap-2 mb-1">
          <Link href="/settings" className="text-sm text-text-secondary hover:text-text-primary">
            ← Settings
          </Link>
        </div>
        <div className="flex items-start justify-between gap-4 mt-1">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-text-primary">
              💳 Pricing Rules
            </h1>
            <p className="text-text-secondary text-sm mt-1">
              Override national defaults with your actual labor rates and parts costs.
            </p>
          </div>
          <button
            onClick={() => { setShowAddForm(true); setSaveError(null); }}
            className="flex-shrink-0 bg-brand-green text-white font-bold px-4 py-2.5 rounded-xl text-sm hover:shadow-lg transition-shadow"
          >
            + Add Rule
          </button>
        </div>
      </div>

      {/* Add Rule Form */}
      {showAddForm && (
        <div className="bg-white border-2 border-brand-green rounded-2xl p-5 space-y-4">
          <p className="font-bold text-sm">New Pricing Override</p>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1">
                Equipment Type
              </label>
              <select
                value={newRule.equipment_type}
                onChange={(e) => setNewRule((p) => ({ ...p, equipment_type: e.target.value }))}
                className="w-full border border-surface-border rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-brand-green"
              >
                {EQUIPMENT_TYPES.map((t) => (
                  <option key={t} value={t}>{labelify(t)}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1">
                Job Type
              </label>
              <select
                value={newRule.job_type}
                onChange={(e) => setNewRule((p) => ({ ...p, job_type: e.target.value }))}
                className="w-full border border-surface-border rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-brand-green"
              >
                {JOB_TYPES.map((t) => (
                  <option key={t} value={t}>{labelify(t)}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1">
                Region
              </label>
              <input
                value={newRule.region}
                onChange={(e) => setNewRule((p) => ({ ...p, region: e.target.value }))}
                placeholder="national"
                className="w-full border border-surface-border rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-brand-green"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1">
                Labor Rate ($/hr)
              </label>
              <input
                type="number"
                value={newRule.labor_rate ?? ""}
                onChange={(e) => setNewRule((p) => ({ ...p, labor_rate: e.target.value ? Number(e.target.value) : null }))}
                placeholder="e.g. 95"
                className="w-full border border-surface-border rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-brand-green"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1">
                Permit Cost ($)
              </label>
              <input
                type="number"
                value={newRule.permit_cost ?? ""}
                onChange={(e) => setNewRule((p) => ({ ...p, permit_cost: e.target.value ? Number(e.target.value) : null }))}
                placeholder="e.g. 150"
                className="w-full border border-surface-border rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-brand-green"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-text-secondary mb-1">
                Refrigerant ($/lb)
              </label>
              <input
                type="number"
                value={newRule.refrigerant_cost_per_lb ?? ""}
                onChange={(e) => setNewRule((p) => ({ ...p, refrigerant_cost_per_lb: e.target.value ? Number(e.target.value) : null }))}
                placeholder="e.g. 75"
                className="w-full border border-surface-border rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-brand-green"
              />
            </div>
          </div>
          {saveError && (
            <p className="text-sm text-brand-red font-medium">⚠ {saveError}</p>
          )}
          <div className="flex gap-2 pt-1">
            <button
              onClick={createRule}
              disabled={saving}
              className="flex-1 bg-brand-green text-white font-bold py-2.5 rounded-xl text-sm disabled:opacity-50"
            >
              {saving ? "Saving..." : "Save Rule →"}
            </button>
            <button
              onClick={() => { setShowAddForm(false); setSaveError(null); }}
              className="px-5 bg-surface-secondary border border-surface-border text-text-secondary font-semibold py-2.5 rounded-xl text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center h-32">
          <div className="w-6 h-6 border-2 border-brand-green border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {error && (
        <div className="card p-6 text-center">
          <p className="text-brand-red font-medium">⚠ {error}</p>
        </div>
      )}

      {!loading && !error && (
        <>
          {/* Your Company Overrides */}
          <div className="bg-white rounded-2xl border border-surface-border overflow-hidden shadow-sm">
            <div className="px-5 py-4 border-b border-surface-border flex items-center justify-between">
              <div>
                <p className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary mb-0.5">
                  Your Overrides
                </p>
                <h2 className="text-base font-bold text-text-primary">Company Pricing Rules</h2>
              </div>
              <span className="text-xs font-mono text-text-secondary">
                {companyRules.length} rule{companyRules.length !== 1 ? "s" : ""}
              </span>
            </div>

            {companyRules.length === 0 ? (
              <div className="p-8 text-center text-text-secondary text-sm">
                No overrides yet. Add a rule to customize your pricing above national defaults.
              </div>
            ) : (
              <div className="divide-y divide-surface-border">
                {companyRules.map((rule) => {
                  const isEditing = editingId === rule.id;
                  const isDeleting = deletingId === rule.id;
                  return (
                    <div key={rule.id} className="px-5 py-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-bold text-sm text-text-primary">
                              {labelify(rule.equipment_type)}
                            </span>
                            <span className="text-text-secondary">·</span>
                            <span className="text-sm text-text-secondary">
                              {labelify(rule.job_type)}
                            </span>
                            {rule.region !== "national" && (
                              <span className="text-xs bg-blue-50 text-blue-600 font-semibold px-2 py-0.5 rounded-full">
                                {rule.region}
                              </span>
                            )}
                          </div>
                        </div>
                        {!isEditing && (
                          <div className="flex gap-2 flex-shrink-0">
                            <button
                              onClick={() => startEdit(rule)}
                              className="text-xs font-semibold text-brand-green hover:underline"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => deleteRule(rule.id)}
                              disabled={isDeleting}
                              className="text-xs font-semibold text-brand-red hover:underline disabled:opacity-50"
                            >
                              {isDeleting ? "..." : "Delete"}
                            </button>
                          </div>
                        )}
                      </div>

                      {isEditing ? (
                        <div className="mt-3 space-y-3">
                          <div className="grid grid-cols-3 gap-3">
                            <div>
                              <label className="block text-xs font-semibold text-text-secondary mb-1">
                                Labor Rate ($/hr)
                              </label>
                              <input
                                type="number"
                                value={editValues.labor_rate ?? ""}
                                onChange={(e) =>
                                  setEditValues((p) => ({
                                    ...p,
                                    labor_rate: e.target.value ? Number(e.target.value) : null,
                                  }))
                                }
                                className="w-full border border-surface-border rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-brand-green"
                              />
                            </div>
                            <div>
                              <label className="block text-xs font-semibold text-text-secondary mb-1">
                                Permit Cost ($)
                              </label>
                              <input
                                type="number"
                                value={editValues.permit_cost ?? ""}
                                onChange={(e) =>
                                  setEditValues((p) => ({
                                    ...p,
                                    permit_cost: e.target.value ? Number(e.target.value) : null,
                                  }))
                                }
                                className="w-full border border-surface-border rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-brand-green"
                              />
                            </div>
                            <div>
                              <label className="block text-xs font-semibold text-text-secondary mb-1">
                                Refrigerant ($/lb)
                              </label>
                              <input
                                type="number"
                                value={editValues.refrigerant_cost_per_lb ?? ""}
                                onChange={(e) =>
                                  setEditValues((p) => ({
                                    ...p,
                                    refrigerant_cost_per_lb: e.target.value
                                      ? Number(e.target.value)
                                      : null,
                                  }))
                                }
                                className="w-full border border-surface-border rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-brand-green"
                              />
                            </div>
                          </div>
                          {saveError && editingId === rule.id && (
                            <p className="text-sm text-brand-red">⚠ {saveError}</p>
                          )}
                          <div className="flex gap-2">
                            <button
                              onClick={() => saveEdit(rule.id)}
                              disabled={saving}
                              className="bg-brand-green text-white text-sm font-bold px-5 py-2 rounded-xl disabled:opacity-50"
                            >
                              {saving ? "Saving..." : "Save"}
                            </button>
                            <button
                              onClick={cancelEdit}
                              className="text-sm text-text-secondary font-semibold px-4 py-2 rounded-xl border border-surface-border"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="flex gap-6 mt-2 flex-wrap">
                          <div className="text-sm">
                            <span className="text-text-secondary text-xs">Labor Rate</span>
                            <p className="font-mono font-bold text-text-primary">
                              {rule.labor_rate != null ? `${fmt(rule.labor_rate)}/hr` : "—"}
                            </p>
                          </div>
                          <div className="text-sm">
                            <span className="text-text-secondary text-xs">Permit</span>
                            <p className="font-mono font-bold text-text-primary">
                              {fmt(rule.permit_cost)}
                            </p>
                          </div>
                          <div className="text-sm">
                            <span className="text-text-secondary text-xs">Refrigerant</span>
                            <p className="font-mono font-bold text-text-primary">
                              {rule.refrigerant_cost_per_lb != null
                                ? `${fmt(rule.refrigerant_cost_per_lb)}/lb`
                                : "—"}
                            </p>
                          </div>
                          {rule.parts_cost?.avg != null && (
                            <div className="text-sm">
                              <span className="text-text-secondary text-xs">Parts (avg)</span>
                              <p className="font-mono font-bold text-text-primary">
                                {fmt(rule.parts_cost.avg)}
                              </p>
                            </div>
                          )}
                          {rule.labor_hours?.avg != null && (
                            <div className="text-sm">
                              <span className="text-text-secondary text-xs">Labor Hours</span>
                              <p className="font-mono font-bold text-text-primary">
                                {rule.labor_hours.avg}h avg
                              </p>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* National Defaults (read-only) */}
          {globalRules.length > 0 && (
            <div className="bg-white rounded-2xl border border-surface-border overflow-hidden shadow-sm">
              <div className="px-5 py-4 border-b border-surface-border">
                <p className="text-[9px] font-bold uppercase tracking-widest font-mono text-text-secondary mb-0.5">
                  Read-Only
                </p>
                <h2 className="text-base font-bold text-text-primary">National Defaults</h2>
                <p className="text-xs text-text-secondary mt-0.5">
                  Add a rule above to override any of these for your company.
                </p>
              </div>
              <div className="divide-y divide-surface-border">
                {globalRules.map((rule) => (
                  <div key={rule.id} className="px-4 py-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 sm:gap-4">
                    <div className="min-w-0">
                      <span className="font-semibold text-sm text-text-primary">
                        {labelify(rule.equipment_type)}
                      </span>
                      <span className="text-text-secondary text-xs mx-2">·</span>
                      <span className="text-sm text-text-secondary">{labelify(rule.job_type)}</span>
                    </div>
                    <div className="flex flex-wrap gap-x-4 gap-y-0.5 text-xs font-mono text-text-secondary">
                      {rule.labor_rate != null && (
                        <span>{fmt(rule.labor_rate)}/hr labor</span>
                      )}
                      {rule.parts_cost?.avg != null && (
                        <span>{fmt(rule.parts_cost.avg)} parts avg</span>
                      )}
                      {rule.permit_cost != null && (
                        <span>{fmt(rule.permit_cost)} permit</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Info card */}
          <div className="card p-5 bg-blue-50 border-blue-100">
            <div className="flex items-start gap-3">
              <span className="text-xl">💡</span>
              <div>
                <p className="font-bold text-sm text-text-primary">How pricing rules work</p>
                <p className="text-xs text-text-secondary mt-1 leading-relaxed">
                  When SnapAI generates an estimate, it uses your company overrides first.
                  If no override exists for a given job type, it falls back to national market
                  averages. Set your actual labor rate and common permit costs to get the most
                  accurate Good/Better/Best pricing.
                </p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
