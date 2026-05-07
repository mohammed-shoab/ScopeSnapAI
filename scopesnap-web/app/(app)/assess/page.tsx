/**
 * Assess Page Ã¢ÂÂ Phase 3 Diagnostic Flow
 *
 * Flow: step-zero (nameplate OCR) Ã¢ÂÂ complaint selection Ã¢ÂÂ diagnostic (question tree)
 *       Ã¢ÂÂ evidence (photos) Ã¢ÂÂ estimating Ã¢ÂÂ /assessment/{id}
 *
 * Confirm mode (?confirm=1&assessment_id=X): post-job feedback via JobConfirmationCard.
 */
"use client";

import { useState, useCallback, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import { API_URL } from "@/lib/api";
import { processOfflineQueue, getOfflineQueueCount } from "@/lib/offlineQueue";
import { track } from "@/lib/tracking";
import StepZeroPanel from "@/components/StepZeroPanel";
import DiagnosticFlow, { GateContinuation, AnswerRecord } from "@/components/diagnostic/DiagnosticFlow";
import FaultCardResult from "@/components/diagnostic/FaultCardResult";
import JobConfirmationCard, { FaultCardOption } from "@/components/diagnostic/JobConfirmationCard";
import ServiceChecklist, { ServiceEstimateResult } from "@/components/diagnostic/ServiceChecklist";
import { PhotoSlotSpec, PhotoResult } from "@/components/diagnostic/PhotoSlot";
import posthog from 'posthog-js';

const IS_DEV = process.env.NEXT_PUBLIC_ENV === "development";
const DEV_HEADER = { "X-Dev-Clerk-User-Id": "test_user_mike" };

type Phase =
  | "step-zero"
  | "complaint"
  | "diagnostic"
  | "service-checklist"
  | "service-complete"
  | "phase2-gate"
  | "evidence"
  | "estimating"
  | "confirm";

// Ã¢ÂÂÃ¢ÂÂ Complaint options (Tab S first Ã¢ÂÂ service is default) Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
const COMPLAINT_OPTIONS = [
  { id: "service",               icon: "\u{1F527}", label: "Service / Tune-Up",      sub: "Routine maintenance visit" },
  { id: "not_cooling",           icon: "\u{1F975}", label: "Not Cooling",            sub: "Weak or no cooling" },
  { id: "not_heating",           icon: "\u{1F525}", label: "Not Heating",            sub: "No heat / cold air" },
  { id: "intermittent_shutdown", icon: "â¡",    label: "Intermittent Shutdown",  sub: "Short cycling / random shutoffs" },
  { id: "water_dripping",        icon: "\u{1F4A7}", label: "Water Dripping",         sub: "Dripping or pooling" },
  { id: "not_turning_on",        icon: "\u{1F50C}", label: "Not Turning On",         sub: "No response at all" },
  { id: "making_noise",          icon: "\u{1F50A}", label: "Making Noise",           sub: "Banging, squealing, humming" },
  { id: "high_electric_bill",    icon: "\u{1F4B8}", label: "High Electric Bill",     sub: "Unusually high usage" },
  { id: "error_code",            icon: "\u{1F6A8}", label: "Error Code",             sub: "Display or thermostat error" },
] as const;
type ComplaintId = typeof COMPLAINT_OPTIONS[number]["id"];

interface PropertySuggestion {
  id: string;
  address_line1?: string;
  city?: string;
  state?: string;
  customer_name?: string;
  returning_customer?: boolean;
}

interface PriorEstimate {
  id: string;
  report_short_id: string;
  status: string;
  total_amount?: number;
  created_at?: string;
}

const DRAFT_KEY = "snapai_draft_assessment";

// Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
// Inner component (requires useSearchParams Ã¢ÂÂ must be inside Suspense)
// Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
function AssessPageInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { getToken } = useAuth();

  const getAuthHeaders = useCallback(async (): Promise<Record<string, string>> => {
    if (IS_DEV) return DEV_HEADER;
    const token = await getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }, [getToken]);

  // Ã¢ÂÂÃ¢ÂÂ Core state Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  const [phase, setPhase] = useState<Phase>("step-zero");
  const [ocrResult, setOcrResult] = useState<Record<string, unknown> | null>(null);
  const [complaintType, setComplaintType] = useState<ComplaintId | null>(null);
  const [assessmentId, setAssessmentId] = useState<string | null>(null);
  const [resolvedHeaders, setResolvedHeaders] = useState<Record<string, string>>(
    IS_DEV ? DEV_HEADER : {}
  );
  const [creatingAssessment, setCreatingAssessment] = useState(false);

  // Ã¢ÂÂÃ¢ÂÂ Diagnostic resolution Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  const [resolvedCardId, setResolvedCardId] = useState<number | null>(null);
  const [resolvedCardName, setResolvedCardName] = useState<string>("");
  const [resolvedPhotoSlots, setResolvedPhotoSlots] = useState<PhotoSlotSpec[]>([]);
  const [resolvedHistory, setResolvedHistory] = useState<AnswerRecord[]>([]);
  const [diagnosedSessionId, setDiagnosedSessionId] = useState<string | null>(null);

  // Ã¢ÂÂÃ¢ÂÂ Job info Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  const [address, setAddress] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [customerPhone, setCustomerPhone] = useState("");

  // Ã¢ÂÂÃ¢ÂÂ Property search Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  const [suggestions, setSuggestions] = useState<PropertySuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedProperty, setSelectedProperty] = useState<PropertySuggestion | null>(null);
  const [priorEstimates, setPriorEstimates] = useState<PriorEstimate[]>([]);

  // Ã¢ÂÂÃ¢ÂÂ UI helpers Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  const [draftRecovery, setDraftRecovery] = useState<{
    address: string;
    customerName: string;
    timestamp: number;
  } | null>(null);
  const [pendingCount, setPendingCount] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [faultCards, setFaultCards] = useState<FaultCardOption[]>([]);
  const [serviceResult, setServiceResult] = useState<ServiceEstimateResult | null>(null);

  // Ã¢ÂÂÃ¢ÂÂ Confirm mode: URL ?confirm=1&assessment_id=X Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  useEffect(() => {
    const isConfirm = searchParams.get("confirm") === "1";
    const urlAssessmentId = searchParams.get("assessment_id");
    if (isConfirm && urlAssessmentId) {
      setAssessmentId(urlAssessmentId);
      setPhase("confirm");
      getAuthHeaders().then(h => {
        setResolvedHeaders(h);
        return fetch(`${API_URL}/api/fault-cards`, { headers: h });
      }).then(r => r && r.ok ? r.json() : [])
        .then(data => { if (Array.isArray(data)) setFaultCards(data); })
        .catch(() => {});
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Ã¢ÂÂÃ¢ÂÂ Draft recovery + offline queue Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  useEffect(() => {
    track.assessmentStarted();
    posthog.capture('diagnostic_session_started', { complaint_type: complaintType });
    try {
      const raw = localStorage.getItem(DRAFT_KEY);
      if (raw) {
        const draft = JSON.parse(raw);
        const ageHrs = (Date.now() - draft.timestamp) / 3600000;
        if (ageHrs < 4 && draft.address) setDraftRecovery(draft);
      }
    } catch { /* ignore */ }
    getOfflineQueueCount().then(count => { if (count > 0) setPendingCount(count); }).catch(() => {});
    const handleOnline = () => {
      getAuthHeaders().then(headers =>
        processOfflineQueue(API_URL, headers).then(({ uploaded }) => {
          if (uploaded > 0) setPendingCount(0);
        })
      ).catch(() => {});
    };
    window.addEventListener("online", handleOnline);
    if (typeof navigator !== "undefined" && navigator.onLine) handleOnline();
    return () => window.removeEventListener("online", handleOnline);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Ã¢ÂÂÃ¢ÂÂ Draft auto-save Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  useEffect(() => {
    if (address || customerName) {
      try {
        localStorage.setItem(DRAFT_KEY, JSON.stringify({ address, customerName, timestamp: Date.now() }));
      } catch { /* ignore */ }
    }
  }, [address, customerName]);

  // Ã¢ÂÂÃ¢ÂÂ Address autocomplete Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  useEffect(() => {
    if (address.length < 3) { setSuggestions([]); return; }
    const t = setTimeout(async () => {
      try {
        const h = await getAuthHeaders();
        const r = await fetch(`${API_URL}/api/properties/search?q=${encodeURIComponent(address)}&limit=5`, { headers: h });
        if (r.ok) { setSuggestions(await r.json()); setShowSuggestions(true); }
      } catch { /* ignore */ }
    }, 300);
    return () => clearTimeout(t);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [address]);


  // PostHog: resolved and escalated diagnostic events
  useEffect(() => {
    if (resolved) {
      posthog.capture('diagnostic_resolved', { complaint_type: complaintType ?? '' });
    }
  }, [resolved]);

  useEffect(() => {
    if (escalated) {
      posthog.capture('diagnostic_escalated', { complaint_type: complaintType ?? '' });
    }
  }, [escalated]);
  // Ã¢ÂÂÃ¢ÂÂ Create assessment + enter diagnostic Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  const handleComplaintSelected = async (complaintId: ComplaintId) => {
    setComplaintType(complaintId);
    setCreatingAssessment(true);
    setError(null);
    try {
      const headers = await getAuthHeaders();
      setResolvedHeaders(headers);
      const fd = new FormData();
      fd.append("complaint_type", complaintId);
      if (address) fd.append("property_address", address);
      if (customerName) fd.append("homeowner_name", customerName);
      if (customerPhone) fd.append("homeowner_phone", customerPhone);
      if (ocrResult) fd.append("ocr_nameplate_json", JSON.stringify(ocrResult));
      const r = await fetch(`${API_URL}/api/assessments/`, { method: "POST", headers, body: fd });
      if (!r.ok) {
        const detail = await r.json().then((d: { detail?: unknown }) => {
          if (typeof d.detail === "string") return d.detail;
          if (Array.isArray(d.detail) && d.detail[0]?.msg) return d.detail[0].msg as string;
          return "Failed to create assessment";
        }).catch(() => "Failed to create assessment");
        throw new Error(detail ?? "Failed to create assessment");
      }
      const data = await r.json();
      setAssessmentId(data.id);
      try { localStorage.removeItem(DRAFT_KEY); } catch { /* ignore */ }
      setPhase(complaintId === "service" ? "service-checklist" : "diagnostic");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to start assessment");
    } finally {
      setCreatingAssessment(false);
    }
  };

  // Ã¢ÂÂÃ¢ÂÂ Diagnostic callbacks Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  const handleDiagnosticResolved = (
    cardId: number,
    cardName: string,
    sessionId: string,
    photoSlots: PhotoSlotSpec[],
    history: AnswerRecord[],
  ) => {
    setResolvedCardId(cardId);
    setResolvedCardName(cardName);
    setResolvedPhotoSlots(photoSlots);
    setResolvedHistory(history);
    setDiagnosedSessionId(sessionId);
    setPhase("evidence");
  };

  const handlePhase2Gate = useCallback((continuation: GateContinuation) => {
    setPhase("phase2-gate");
    setError(null);
    getAuthHeaders().then(headers => {
      return fetch(`${API_URL}/api/estimates/fault-card`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({
          assessment_id: assessmentId,
          card_id: continuation.card_id,
          session_id: continuation.session_id,
          gate_continuation: continuation.gate_continuation,
        }),
      });
    }).then(r => {
      if (!r.ok) throw new Error("Estimate generation failed");
      return r.json();
    }).then(est => {
      track.estimateGenerated(est.id, est.total_amount || 0);
          posthog.capture('estimate_generated', { estimate_id: est.id, amount: est.total_amount || 0 });
      router.push(`/assessment/${est.id}`);
    }).catch(e => {
      setError(e instanceof Error ? e.message : "Error generating estimate");
      setPhase("complaint");
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [assessmentId, router]);

  // Ã¢ÂÂÃ¢ÂÂ Generate estimate from evidence Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  const handleGenerateEstimate = useCallback(async (photos: PhotoResult[]) => {
    setPhase("estimating");
    setError(null);
    try {
      const headers = await getAuthHeaders();
      const body: Record<string, unknown> = {
        assessment_id: assessmentId,
        card_id: resolvedCardId,
      };
      if (diagnosedSessionId) body.session_id = diagnosedSessionId;
      if (photos.length > 0) body.photo_urls = photos.map(p => p.photo_url);
      const r = await fetch(`${API_URL}/api/estimates/fault-card`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!r.ok) throw new Error((await r.json()).detail || "Generate failed");
      const est = await r.json();
      track.estimateGenerated(est.id, est.total_amount || 0);
          posthog.capture('estimate_generated', { estimate_id: est.id, amount: est.total_amount || 0 });
      router.push(`/assessment/${est.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error generating estimate");
      setPhase("evidence");
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [assessmentId, resolvedCardId, diagnosedSessionId, router]);

  // Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  // PHASE RENDERS
  // Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ

  // Ã¢ÂÂÃ¢ÂÂ step-zero: nameplate OCR Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  if (phase === "step-zero") {
    return (
      <StepZeroPanel
        clerkToken={null}
        onConfirm={(result) => {
          setOcrResult(result as unknown as Record<string, unknown>);
          setPhase("complaint");
        }}
        onSkip={() => setPhase("complaint")}
      />
    );
  }

  // Ã¢ÂÂÃ¢ÂÂ complaint: job info + complaint chip grid Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  if (phase === "complaint") {
    return (
      <div className="max-w-lg mx-auto space-y-5 px-4 pb-6">
        {pendingCount > 0 && (
          <div className="flex items-center gap-3 bg-yellow-50 border border-yellow-200 rounded-xl px-4 py-3 mt-2">
            <span className="text-base">&#x1F4E1;</span>
            <p className="text-xs font-bold text-yellow-900">
              {pendingCount} assessment{pendingCount !== 1 ? "s" : ""} queued Ã¢ÂÂ will upload when online
            </p>
          </div>
        )}
        {draftRecovery && (
          <div className="flex items-center gap-3 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 mt-2">
            <span className="text-base">&#x1F4CB;</span>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-bold text-text-primary">Unsaved draft found</p>
              <p className="text-xs text-text-secondary truncate">{draftRecovery.address}</p>
            </div>
            <button
              onClick={() => { setAddress(draftRecovery.address); setCustomerName(draftRecovery.customerName || ""); setDraftRecovery(null); }}
              className="text-xs font-bold text-brand-orange hover:underline flex-shrink-0"
            >Continue</button>
            <button
              onClick={() => { localStorage.removeItem(DRAFT_KEY); setDraftRecovery(null); }}
              className="text-xs text-text-secondary hover:text-text-primary flex-shrink-0"
            >Discard</button>
          </div>
        )}

        {/* Header */}
        <div className="pt-4">
          <button onClick={() => setPhase("step-zero")} className="text-sm text-gray-500 hover:text-gray-800 mb-3 block">
            &#x2190; Back
          </button>
          <h1 className="text-3xl font-extrabold tracking-tight">New Assessment</h1>
          <p className="text-text-secondary text-sm mt-1">Fill in job info, then tap the complaint.</p>
        </div>

        {/* Job info */}
        <div className="bg-white border border-gray-200 rounded-2xl p-4 space-y-3">
          <p className="text-xs font-mono text-gray-600 uppercase tracking-widest font-bold">Job Info (optional)</p>
          <div className="relative">
            <input
              type="text"
              placeholder="Property address (search existing...)"
              value={address}
              onChange={e => { setAddress(e.target.value); setShowSuggestions(true); }}
              onFocus={() => setShowSuggestions(true)}
              className="w-full border border-gray-300 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-green-600 focus:ring-1 focus:ring-green-500 transition-colors"
            />
            {showSuggestions && suggestions.length > 0 && (
              <div className="absolute z-10 w-full bg-white border border-gray-300 rounded-xl mt-1 shadow-lg">
                {suggestions.map(s => (
                  <button
                    key={s.id}
                    onMouseDown={async () => {
                      setAddress(s.address_line1 || "");
                      setCustomerName(s.customer_name || "");
                      setShowSuggestions(false);
                      setSelectedProperty(s);
                      try {
                        const h = await getAuthHeaders();
                        const r = await fetch(`${API_URL}/api/estimates/?property_id=${s.id}&limit=5`, { headers: h });
                        if (r.ok) {
                          const d = await r.json();
                          setPriorEstimates(Array.isArray(d.items) ? d.items : Array.isArray(d) ? d : []);
      posthog.capture('report_sent', { complaint_type: complaintType ?? '' });
                        }
                      } catch { /* ignore */ }
                    }}
                    className="w-full text-left px-3 py-2.5 hover:bg-gray-100 text-sm border-b border-gray-200 last:border-0 transition-colors"
                  >
                    <p className="font-semibold text-gray-900">{s.address_line1}</p>
                    <p className="text-xs text-gray-600">
                      {[s.customer_name, s.returning_customer && "Previous visit found"].filter(Boolean).join(" ÃÂ· ")}
                    </p>
                  </button>
                ))}
              </div>
            )}
          </div>
          <div className="grid grid-cols-2 gap-2">
            <input
              type="text" placeholder="Homeowner name" value={customerName}
              onChange={e => setCustomerName(e.target.value)}
              className="border border-gray-300 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-green-600"
            />
            <input
              type="tel" placeholder="Phone number" value={customerPhone}
              onChange={e => setCustomerPhone(e.target.value)}
              className="border border-gray-300 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-green-600"
            />
          </div>
        </div>

        {/* Prior estimates for returning customer */}
        {selectedProperty && priorEstimates.length > 0 && (
          <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
              <div>
                <p className="text-xs font-mono text-gray-600 uppercase tracking-widest font-bold">Returning Customer</p>
                <p className="text-sm font-bold text-gray-900">{selectedProperty.customer_name || selectedProperty.address_line1}</p>
              </div>
              <button
                onClick={() => { setSelectedProperty(null); setPriorEstimates([]); }}
                className="text-xs text-gray-500 font-semibold"
              >&#x2715;</button>
            </div>
            <div className="p-4 space-y-2">
              {priorEstimates.map(est => {
                const statusColors: Record<string, string> = {
                  approved: "bg-green-100 text-green-700",
                  deposit_paid: "bg-green-100 text-green-700",
                  sent: "bg-blue-100 text-blue-700",
                  viewed: "bg-blue-100 text-blue-700",
                  estimated: "bg-yellow-100 text-yellow-700",
                  draft: "bg-gray-100 text-gray-600",
                };
                const daysAgo = est.created_at
                  ? Math.floor((Date.now() - new Date(est.created_at).getTime()) / 86400000)
                  : null;
                return (
                  <a
                    key={est.id}
                    href={`/assessment/${est.id}`}
                    className="flex items-center justify-between gap-3 p-3 bg-gray-50 hover:bg-gray-100 rounded-xl transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-gray-900">{est.report_short_id}</span>
                      <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${statusColors[est.status] || "bg-gray-100 text-gray-600"}`}>
                        {est.status.replace(/_/g, " ")}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-gray-500">
                      {est.total_amount != null && (
                        <span className="font-mono font-bold text-gray-900">${est.total_amount.toLocaleString()}</span>
                      )}
                      {daysAgo != null && (
                        <span>{daysAgo === 0 ? "today" : daysAgo === 1 ? "yesterday" : `${daysAgo}d ago`}</span>
                      )}
                    </div>
                  </a>
                );
              })}
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-sm text-red-600 font-medium">
            &#x26A0; {error}
          </div>
        )}

        {/* Complaint grid */}
        <div>
          <p className="text-sm font-bold text-gray-700 mb-3">What&apos;s the complaint?</p>
          <div className="grid grid-cols-2 gap-3">
            {COMPLAINT_OPTIONS.map(opt => (
              <button
                key={opt.id}
                onClick={() => handleComplaintSelected(opt.id)}
                disabled={creatingAssessment}
                className="bg-white border-2 border-gray-200 hover:border-green-500 rounded-2xl p-4 text-left transition-all active:scale-95 focus:outline-none disabled:opacity-50"
              >
                <div className="text-3xl mb-2">{opt.icon}</div>
                <p className="font-bold text-gray-900 text-sm leading-tight">{opt.label}</p>
                <p className="text-xs text-gray-500 mt-0.5">{opt.sub}</p>
              </button>
            ))}
          </div>
          {creatingAssessment && (
            <div className="flex items-center justify-center gap-2 mt-4">
              <div className="w-4 h-4 border-2 border-green-600 border-t-transparent rounded-full animate-spin" />
              <span className="text-sm text-gray-500">Starting assessment...</span>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Ã¢ÂÂÃ¢ÂÂ service-checklist: Tab S regular service flow Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  if (phase === "service-checklist" && assessmentId) {
    return (
      <div className="max-w-lg mx-auto px-4 pb-6 pt-4" style={{ background: "#0f1117", minHeight: "100vh" }}>
        <div className="mb-4 flex items-center gap-3">
          <button
            onClick={() => setPhase("complaint")}
            className="text-sm font-medium"
            style={{ color: "#4a5568" }}
          >
            &#x2190; Back
          </button>
          <p className="text-xs font-bold uppercase tracking-widest" style={{ color: "#7a8299" }}>
            SERVICE / TUNE-UP
          </p>
        </div>
        <ServiceChecklist
          assessmentId={assessmentId}
          authHeaders={resolvedHeaders}
          ocrNameplate={ocrResult}
          onComplete={(result, _sid) => {
            setServiceResult(result);
            setPhase("service-complete");
          }}
          onCancel={() => setPhase("complaint")}
        />
      </div>
    );
  }

  // Ã¢ÂÂÃ¢ÂÂ service-complete: show service estimate summary Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  if (phase === "service-complete" && serviceResult) {
    const allItems = [...serviceResult.base_items, ...serviceResult.add_ons];
    return (
      <div className="max-w-lg mx-auto px-4 pb-6 pt-4" style={{ background: "#0f1117", minHeight: "100vh" }}>
        <div className="mb-6 flex items-center justify-between">
          <button
            onClick={() => router.push("/assessments")}
            className="text-sm font-medium"
            style={{ color: "#4a5568" }}
          >
            &#x2190; Dashboard
          </button>
          <p className="text-xs font-bold uppercase tracking-widest" style={{ color: "#1abc9c" }}>
            Service Complete
          </p>
        </div>

        {/* Totals */}
        <div className="rounded-2xl p-5 mb-4 flex flex-col gap-1"
          style={{ background: "#071a14", border: "1px solid #1a3a30" }}>
          <p className="text-xs font-mono font-bold uppercase tracking-widest mb-2" style={{ color: "#2a6a5a" }}>
            Service Estimate
          </p>
          <div className="flex items-end justify-between">
            <p className="text-4xl font-extrabold text-white">
              ${serviceResult.total_typical.toLocaleString()}
            </p>
            <p className="text-sm font-semibold pb-1" style={{ color: "#4a8a6a" }}>
              ${serviceResult.total_min.toLocaleString()}Ã¢ÂÂ${serviceResult.total_max.toLocaleString()}
            </p>
          </div>
          <p className="text-xs mt-1" style={{ color: "#4a8a6a" }}>
            Includes {Math.round(serviceResult.markup_pct)}% markup &bull; {serviceResult.findings_count} item{serviceResult.findings_count !== 1 ? "s" : ""} inspected
          </p>
        </div>

        {/* Line items */}
        <div className="rounded-2xl overflow-hidden mb-4" style={{ background: "#0d1f1a", border: "1px solid #1a3a30" }}>
          <p className="text-xs font-mono font-bold uppercase tracking-widest px-4 py-3" style={{ color: "#2a6a5a", borderBottom: "1px solid #1a3a30" }}>
            Services Performed
          </p>
          {allItems.map((item, i) => (
            <div key={i} className="flex items-center justify-between px-4 py-3"
              style={{ borderBottom: i < allItems.length - 1 ? "1px solid #111e19" : "none" }}>
              <span className="text-sm text-white flex-1 pr-2">{item.description}</span>
              <span className="text-sm font-semibold font-mono flex-shrink-0" style={{ color: "#1abc9c" }}>
                ${item.amount_min}Ã¢ÂÂ${item.amount_max}
              </span>
            </div>
          ))}
        </div>

        {/* Flags */}
        {serviceResult.flags.length > 0 && (
          <div className="rounded-2xl p-4 mb-4 flex flex-col gap-2"
            style={{ background: "rgba(230,126,34,0.08)", border: "1px solid rgba(230,126,34,0.3)" }}>
            <p className="text-xs font-mono font-bold uppercase tracking-widest" style={{ color: "#e67e22" }}>
              Flags / Follow-Ups
            </p>
            {serviceResult.flags.map((f, i) => (
              <div key={i} className="flex items-start gap-2">
                <span className="text-sm mt-0.5">&#x26A0;</span>
                <span className="text-sm" style={{ color: "#e67e22" }}>{f.description}</span>
              </div>
            ))}
          </div>
        )}

        <button
          onClick={() => router.push("/assessments")}
          className="w-full py-4 rounded-2xl font-bold text-sm"
          style={{ background: "#1abc9c", color: "#071a14" }}
        >
          Done Ã¢ÂÂ Back to Dashboard
        </button>
      </div>
    );
  }

  // Ã¢ÂÂÃ¢ÂÂ diagnostic: question-tree flow Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  if (phase === "diagnostic" && assessmentId && complaintType) {
    return (
      <div className="max-w-lg mx-auto px-4 pb-6 pt-4" style={{ background: "#0f1117", minHeight: "100vh" }}>
        <div className="mb-4 flex items-center gap-3">
          <button
            onClick={() => setPhase("complaint")}
            className="text-sm font-medium"
            style={{ color: "#4a5568" }}
          >
            &#x2190; Back
          </button>
          <p className="text-xs font-bold uppercase tracking-widest" style={{ color: "#7a8299" }}>
            {COMPLAINT_OPTIONS.find(o => o.id === complaintType)?.label ?? complaintType}
          </p>
        </div>
        <DiagnosticFlow
          assessmentId={assessmentId}
          complaintType={complaintType}
          authHeaders={resolvedHeaders}
          ocrNameplate={ocrResult}
          onResolved={handleDiagnosticResolved}
          onPhase2Gate={handlePhase2Gate}
          onEscalated={() => {
            setError("Diagnostic escalated Ã¢ÂÂ please inspect manually.");
            setPhase("complaint");
          }}
          onCancel={() => setPhase("complaint")}
        />
      </div>
    );
  }

  // Ã¢ÂÂÃ¢ÂÂ phase2-gate: deep analysis spinner Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  if (phase === "phase2-gate") {
    return (
      <div className="max-w-md mx-auto pt-16 text-center space-y-4 px-4" style={{ background: "#0f1117", minHeight: "100vh" }}>
        <div className="flex gap-3 justify-center">
          {[0, 1, 2].map(i => (
            <div
              key={i}
              className="w-4 h-4 rounded-full"
              style={{
                background: "#3498db",
                animation: `pulseDot 1.4s ease-in-out ${i * 0.2}s infinite`,
              }}
            />
          ))}
          <style>{`@keyframes pulseDot{0%,80%,100%{transform:scale(0.6);opacity:.4}40%{transform:scale(1.2);opacity:1}}`}</style>
        </div>
        <h2 className="text-xl font-extrabold text-white">Deep Analysis Running...</h2>
        <p className="text-sm" style={{ color: "#7a8299" }}>Building your estimate from diagnosis data</p>
        {error && <p className="text-sm font-medium mt-2" style={{ color: "#e74c3c" }}>{error}</p>}
      </div>
    );
  }

  // Ã¢ÂÂÃ¢ÂÂ evidence: fault card + photo capture Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  if (phase === "evidence" && assessmentId && resolvedCardId !== null) {
    return (
      <div className="max-w-lg mx-auto px-4 pb-6 pt-4" style={{ background: "#0f1117", minHeight: "100vh" }}>
        <FaultCardResult
          cardId={resolvedCardId}
          cardName={resolvedCardName}
          resolutionPath={resolvedHistory}
          photoSlots={resolvedPhotoSlots}
          assessmentId={assessmentId}
          authHeaders={resolvedHeaders}
          onAllPhotosCaptured={handleGenerateEstimate}
          onSkip={() => handleGenerateEstimate([])}
        />
        {error && (
          <div className="mt-4 rounded-xl px-4 py-3" style={{ background: "rgba(231,76,60,0.12)" }}>
            <p className="text-sm font-medium text-center" style={{ color: "#e74c3c" }}>{error}</p>
          </div>
        )}
      </div>
    );
  }

  // Ã¢ÂÂÃ¢ÂÂ estimating: building estimate spinner Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  if (phase === "estimating") {
    return (
      <div className="max-w-md mx-auto pt-16 text-center space-y-4" style={{ background: "#0f1117", minHeight: "100vh" }}>
        <div className="text-5xl">&#x2699;&#xFE0F;</div>
        <h2 className="text-xl font-extrabold text-white">Building Estimate...</h2>
        <p className="text-sm" style={{ color: "#7a8299" }}>Calculating Good / Better / Best pricing</p>
      </div>
    );
  }

  // Ã¢ÂÂÃ¢ÂÂ confirm: post-job feedback (from email link ?confirm=1) Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
  if (phase === "confirm") {
    if (!assessmentId) {
      return (
        <div
          className="flex flex-col items-center justify-center gap-4"
          style={{ background: "#0f1117", minHeight: "100vh" }}
        >
          <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin" />
          <p className="text-sm" style={{ color: "#7a8299" }}>Loading...</p>
        </div>
      );
    }
    return (
      <div className="max-w-lg mx-auto px-4 pb-6 pt-4" style={{ background: "#0f1117", minHeight: "100vh" }}>
        <div className="mb-4">
          <button
            onClick={() => router.push(`/assessment/${assessmentId}`)}
            className="text-sm font-medium"
            style={{ color: "#4a5568" }}
          >
            &#x2190; Back to Report
          </button>
        </div>
        <JobConfirmationCard
          assessmentId={assessmentId}
          diagnosedCardId={resolvedCardId ?? 0}
          diagnosedCardName={resolvedCardName}
          faultCards={faultCards}
          authHeaders={resolvedHeaders}
          onConfirmed={() => router.push(`/assessment/${assessmentId}`)}
          onSkip={() => router.push(`/assessment/${assessmentId}`)}
        />
      </div>
    );
  }

  return null;
}

// Ã¢ÂÂÃ¢ÂÂ Exported page: Suspense wrapper required for useSearchParams Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
export default function AssessPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-screen">
          <div className="w-8 h-8 border-2 border-green-600 border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <AssessPageInner />
    </Suspense>
  );
}
