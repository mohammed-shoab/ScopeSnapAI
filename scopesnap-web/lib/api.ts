/**
 * SnapAI — API Client
 * Typed fetch wrapper for all SnapAI API calls.
 * Handles auth headers, error parsing, and dev mode shortcuts.
 */

import { detectMarket } from "./market";

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Dev mode: bypass Clerk auth with test user
const IS_DEV =
  process.env.NEXT_PUBLIC_ENV === "development" ||
  process.env.NODE_ENV === "development";
const DEV_USER_ID = "test_user_mike";

// ── Types ──────────────────────────────────────────────────────────────────────

export interface Assessment {
  id: string;
  company_id: string;
  user_id: string;
  property_id: string | null;
  photo_urls: string[];
  ai_analysis: Record<string, unknown> | null;
  ai_equipment_id: {
    brand: string;
    model: string;
    confidence: number;
    serial?: string;
    install_year?: number;
  } | null;
  ai_condition: {
    overall: string;
    components: Array<{
      name: string;
      condition: string;
      description_plain: string;
      urgency: string;
    }>;
  } | null;
  ai_issues: Array<{
    component: string;
    issue: string;
    severity: string;
    description: string;
  }> | null;
  tech_overrides: Record<string, unknown>;
  status: "pending" | "analyzed" | "estimated" | "sent" | "approved" | "completed";
  created_at: string;
}

export interface EstimateOption {
  tier: "good" | "better" | "best";
  name: string;
  description: string;
  total: number;
  five_year_total: number;
  energy_savings_annual: number;
  line_items: Array<{
    category: string;
    description: string;
    quantity: number;
    unit_cost: number;
    total: number;
  }>;
}

export interface Estimate {
  id: string;
  assessment_id: string;
  report_token: string;
  report_short_id: string;
  options: EstimateOption[];
  selected_option: string | null;
  total_amount: number | null;
  markup_percent: number;
  status: string;
  homeowner_report_url: string | null;
  contractor_pdf_url: string | null;
  created_at: string;
}

// ── Typed Error Classes ────────────────────────────────────────────────────────

/** Network not reachable at all (navigator.onLine === false or fetch throw TypeError) */
export class OfflineError extends Error {
  constructor(message = "No internet connection. Check your signal and try again.") {
    super(message);
    this.name = "OfflineError";
  }
}

/** API returned an HTTP error (4xx / 5xx) */
export class APIError extends Error {
  constructor(
    public status: number,
    public detail: string,
    public data?: unknown
  ) {
    super(detail);
    this.name = "APIError";
  }
}

/** API returned 5xx (server-side error, not user fault) */
export class ServerError extends APIError {
  constructor(status: number, detail = "Server error. Try again in a moment.") {
    super(status, detail);
    this.name = "ServerError";
  }
}

/** Friendly message for any API error type */
export function friendlyError(err: unknown): string {
  if (err instanceof OfflineError) return err.message;
  if (err instanceof ServerError) return "Server error — please try again in a moment.";
  if (err instanceof APIError) return err.detail;
  if (err instanceof Error) return err.message;
  return "Something went wrong. Please try again.";
}

// ── Core Fetch Wrapper ────────────────────────────────────────────────────────

async function apiFetch<T>(
  path: string,
  options: RequestInit & { token?: string } = {}
): Promise<T> {
  const { token, ...fetchOptions } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-Market": detectMarket(),
    ...(fetchOptions.headers as Record<string, string>),
  };

  if (IS_DEV) {
    // Dev bypass: API accepts X-Dev-Clerk-User-Id instead of Clerk JWT
    headers["X-Dev-Clerk-User-Id"] = DEV_USER_ID;
  } else if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Offline guard — fail fast with clear message
  if (typeof navigator !== "undefined" && !navigator.onLine) {
    throw new OfflineError();
  }

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...fetchOptions,
      headers,
    });
  } catch {
    // fetch throws TypeError when network is unreachable
    throw new OfflineError();
  }

  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const errorData = await response.json();
      detail = errorData.detail || detail;
    } catch {
      // ignore parse error
    }
    if (response.status >= 500) {
      throw new ServerError(response.status, detail);
    }
    throw new APIError(response.status, detail);
  }

  return response.json() as Promise<T>;
}

// ── Health ────────────────────────────────────────────────────────────────────

export async function checkHealth(): Promise<{
  status: string;
  db: string;
  environment: string;
}> {
  return apiFetch("/health");
}

// ── Assessments ───────────────────────────────────────────────────────────────

export async function uploadAssessment(
  photos: File[],
  token: string,
  propertyId?: string
): Promise<Assessment> {
  const formData = new FormData();
  photos.forEach((photo) => formData.append("photos", photo));
  if (propertyId) formData.append("property_id", propertyId);

  const authHeaders: Record<string, string> = {
    "X-Market": detectMarket(),
    ...(IS_DEV
      ? { "X-Dev-Clerk-User-Id": DEV_USER_ID }
      : { Authorization: `Bearer ${token}` }),
  };

  const response = await fetch(`${API_URL}/api/assessments/`, {
    method: "POST",
    headers: authHeaders,
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new APIError(response.status, error.detail);
  }

  return response.json();
}

export async function analyzeAssessment(
  assessmentId: string,
  token: string
): Promise<Assessment> {
  return apiFetch(`/api/assessments/${assessmentId}/analyze`, {
    method: "POST",
    token,
  });
}

export async function getAssessment(
  assessmentId: string,
  token: string
): Promise<Assessment> {
  return apiFetch(`/api/assessments/${assessmentId}`, { token });
}

export async function updateAssessment(
  assessmentId: string,
  overrides: Record<string, unknown>,
  token: string
): Promise<Assessment> {
  return apiFetch(`/api/assessments/${assessmentId}`, {
    method: "PATCH",
    token,
    body: JSON.stringify(overrides),
  });
}

// ── Estimates ─────────────────────────────────────────────────────────────────

export async function generateEstimate(
  assessmentId: string,
  token: string,
  adjustments?: Record<string, unknown>
): Promise<Estimate> {
  return apiFetch("/api/estimates/generate", {
    method: "POST",
    token,
    body: JSON.stringify({ assessment_id: assessmentId, ...adjustments }),
  });
}

export async function getEstimate(estimateId: string, token: string): Promise<Estimate> {
  return apiFetch(`/api/estimates/${estimateId}`, { token });
}

export async function updateEstimate(
  estimateId: string,
  updates: Record<string, unknown>,
  token: string
): Promise<Estimate> {
  return apiFetch(`/api/estimates/${estimateId}`, {
    method: "PATCH",
    token,
    body: JSON.stringify(updates),
  });
}

export async function generateDocuments(
  estimateId: string,
  token: string
): Promise<{ contractor_pdf_url: string; homeowner_report_url: string }> {
  return apiFetch(`/api/estimates/${estimateId}/documents`, {
    method: "POST",
    token,
  });
}

export async function sendEstimate(
  estimateId: string,
  token: string,
  options: { email?: string; phone?: string }
): Promise<{ sent: boolean }> {
  return apiFetch(`/api/estimates/${estimateId}/send`, {
    method: "POST",
    token,
    body: JSON.stringify(options),
  });
}

// ── Properties ────────────────────────────────────────────────────────────────

export interface Property {
  id: string;
  address_line1?: string;
  city?: string;
  state?: string;
  zip?: string;
  customer_name?: string;
  customer_phone?: string;
  customer_email?: string;
  visit_count?: number;
  returning_customer?: boolean;
  last_visit_at?: string;
}

export async function searchProperties(q: string, token: string): Promise<Property[]> {
  return apiFetch(`/api/properties/search?q=${encodeURIComponent(q)}`, { token });
}

export async function listEstimates(token: string, limit = 20): Promise<{ items: Estimate[] }> {
  return apiFetch(`/api/estimates/?limit=${limit}`, { token });
}

// ── Public Report (no auth) ───────────────────────────────────────────────────

export async function getPublicReport(
  reportToken: string
): Promise<Record<string, unknown>> {
  return apiFetch(`/api/reports/${reportToken}`);
}
