/**
 * SnapAI — Public Homeowner Report (SSR)
 * WP-06: Full implementation.
 *
 * This page is PUBLIC — no auth required.
 * The reportId in the URL is the report_short_id (e.g. "rpt-0847").
 * The API resolves it by report_short_id OR report_token.
 */

import { notFound } from "next/navigation";
import ReportClient from "./ReportClient";

export const dynamic = "force-dynamic";

interface ReportPageProps {
  params: {
    slug: string;      // Company slug e.g. "abc-hvac"
    reportId: string;  // Report short ID e.g. "rpt-0847"
  };
}

async function fetchReport(reportId: string) {
  // Use server-side API_URL (http://api:8000) in Docker, fall back to public URL for local dev
  const apiUrl =
    process.env.API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000";
  try {
    const res = await fetch(`${apiUrl}/api/reports/${reportId}`, {
      // Revalidate once per minute — report data rarely changes after creation
      next: { revalidate: 60 },
    });
    if (res.status === 404) return null;
    if (!res.ok) {
      console.error(`Report fetch error: ${res.status} ${res.statusText}`);
      return null;
    }
    return res.json();
  } catch (err) {
    console.error("Report fetch failed:", err);
    return null;
  }
}

// Server Component — SSR for fast initial load
export default async function HomeownerReportPage({ params }: ReportPageProps) {
  const { reportId } = params;

  const report = await fetchReport(reportId);

  if (!report) {
    notFound();
  }

  return <ReportClient report={report} />;
}

// not-found page for invalid tokens
export function generateStaticParams() {
  return [];
}

// Generate metadata for SEO
export async function generateMetadata({ params }: ReportPageProps) {
  const { reportId, slug } = params;
  const report = await fetchReport(reportId);

  const companyName = report?.company?.name || slug.replace(/-/g, " ").replace(/\b\w/g, (l: string) => l.toUpperCase());
  const address = report?.property?.address_line1 || "Your Home";

  return {
    title: `HVAC Report — ${address} — ${companyName}`,
    description: `Your personalized HVAC assessment with equipment photos, condition analysis, and repair options from ${companyName}.`,
    robots: "noindex, nofollow", // Don't index individual reports
  };
}
