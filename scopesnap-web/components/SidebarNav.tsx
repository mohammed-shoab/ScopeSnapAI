"use client";
/**
 * SnapAI â Sidebar Navigation
 * SOW Task 1.6: Simplified for beta â 4 core items + feature-flagged extras.
 *
 * Changes from pre-beta version:
 * - Removed all hardcoded numeric badges (47 estimates, $70K, 43 alerts)
 * - Added BETA badge in logo area
 * - Non-essential sections hidden via featureFlags
 * - Core items always visible: Dashboard, Assessments, Settings
 * - Feature-flagged (hidden by default): Analytics, Intelligence, Equipment, Team, Integrations
 * - Feedback button at bottom (links to feedback form / mailto)
 */

import Link from "next/link";
import { useState, useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useClerk, useUser } from "@clerk/nextjs";
import { featureFlags } from "@/lib/featureFlags";
import FeedbackModal from "@/components/FeedbackModal";

// ââ SVG icon definitions (no emojis â clean, professional, accessible) ââââââââ
const NavIcons: Record<string, React.ReactNode> = {
  dashboard: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>
      <rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>
    </svg>
  ),
  assessments: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/>
      <line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="15" y2="17"/>
    </svg>
  ),
  analytics: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
    </svg>
  ),
  leaks: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
    </svg>
  ),
  benchmark: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
    </svg>
  ),
  history: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
      <polyline points="9 22 9 12 15 12 15 22"/>
    </svg>
  ),
  equipment: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/>
    </svg>
  ),
  alerts: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/>
    </svg>
  ),
  team: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/>
      <path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/>
    </svg>
  ),
  leaderboard: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M8 6l4-4 4 4"/><path d="M12 2v10.3"/><path d="M20 21H4M4 21v-4a2 2 0 012-2h12a2 2 0 012 2v4"/>
    </svg>
  ),
  pricing: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>
    </svg>
  ),
  integrations: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/>
      <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
    </svg>
  ),
  settings: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3"/>
      <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/>
    </svg>
  ),
  feedback: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
    </svg>
  ),
};

// ââ Nav item type âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
interface NavItem {
  label: string;
  href: string;
  iconKey: string;
}

interface NavSection {
  section: string;
  items: NavItem[];
}

// ââ Build nav sections based on feature flags âââââââââââââââââââââââââââââââââ
function buildNavSections(): NavSection[] {
  const sections: NavSection[] = [];

  // ââ OVERVIEW (always visible) âââââââââââââââââââââââââââââââââââââââââââââ
  const overviewItems: NavItem[] = [
    { label: "Dashboard",    href: "/dashboard",  iconKey: "dashboard" },
    { label: "Assessments",  href: "/assessments",  iconKey: "assessments" },
  ];
  if (featureFlags.showAnalytics) {
    overviewItems.push({ label: "Accuracy Tracker", href: "/analytics", iconKey: "analytics" });
  }
  sections.push({ section: "OVERVIEW", items: overviewItems });

  // ââ INTELLIGENCE (feature-flagged) ââââââââââââââââââââââââââââââââââââââââ
  const intelItems: NavItem[] = [];
  if (featureFlags.showProfitLeaks)      intelItems.push({ label: "Profit Leaks",     href: "/intelligence/leaks",     iconKey: "leaks" });
  if (featureFlags.showBenchmark)        intelItems.push({ label: "BenchmarkIQ",      href: "/intelligence/benchmark", iconKey: "benchmark" });
  if (featureFlags.showPropertyHistory)  intelItems.push({ label: "Property History", href: "/intelligence/history",   iconKey: "history" });
  if (intelItems.length > 0) {
    sections.push({ section: "INTELLIGENCE", items: intelItems });
  }

  // ââ EQUIPMENT (feature-flagged) âââââââââââââââââââââââââââââââââââââââââââ
  if (featureFlags.showEquipment) {
    sections.push({
      section: "EQUIPMENT",
      items: [
        { label: "Equipment Database", href: "/equipment/database", iconKey: "equipment" },
        { label: "Aging Alerts",       href: "/equipment/alerts",   iconKey: "alerts" },
      ],
    });
  }

  // ââ TEAM (feature-flagged) ââââââââââââââââââââââââââââââââââââââââââââââââ
  if (featureFlags.showTeam) {
    sections.push({
      section: "TEAM",
      items: [
        { label: "Technicians", href: "/team/technicians", iconKey: "team" },
        { label: "Leaderboard", href: "/team/leaderboard", iconKey: "leaderboard" },
      ],
    });
  }

  // ââ SETTINGS (always visible) âââââââââââââââââââââââââââââââââââââââââââââ
  const settingsItems: NavItem[] = [
    { label: "Pricing Database", href: "/settings/pricing", iconKey: "pricing" },
  ];
  if (featureFlags.showIntegrations) {
    settingsItems.push({ label: "Integrations", href: "/settings/integrations", iconKey: "integrations" });
  }
  settingsItems.push({ label: "Settings", href: "/settings", iconKey: "settings" });
  sections.push({ section: "SETTINGS", items: settingsItems });

  return sections;
}

export default function SidebarNav() {
  const pathname = usePathname();
  const [isMobileOpen, setIsMobileOpen]   = useState(false);
  const [mounted, setMounted]             = useState(false);
  const [feedbackOpen, setFeedbackOpen]   = useState(false);
  const { signOut } = useClerk();
  const { user } = useUser();
  const router = useRouter();

  const handleSignOut = async () => {
    await signOut();
    router.push("/");
  };

  useEffect(() => { setMounted(true); }, []);

  // Defer active-state comparison until client is mounted to prevent hydration mismatch
  const isActive = (href: string) =>
    mounted && (pathname === href || pathname.startsWith(href + "/"));

  const navSections = buildNavSections();

  return (
    <>
      {/* Mobile hamburger */}
      <button
        onClick={() => setIsMobileOpen(!isMobileOpen)}
        className="md:hidden fixed top-4 left-4 z-40 p-2 hover:bg-gray-700 rounded-lg transition-colors"
        style={{ background: "#2a2a28" }}
        aria-label="Toggle navigation menu"
      >
        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d={isMobileOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} />
        </svg>
      </button>

      {/* Mobile overlay backdrop */}
      {mounted && isMobileOpen && (
        <div
          className="md:hidden fixed inset-0 z-20 bg-black/50"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        suppressHydrationWarning
        className={`fixed top-0 left-0 h-[100dvh] w-60 overflow-hidden transition-transform duration-300 ease-in-out z-30 md:z-10 ${
          isMobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
        style={{ background: "#1a1a18" }}
      >
        <div className="flex flex-col h-full">

          {/* ââ Logo Area with BETA badge ââââââââââââââââââââââââââââââââââ */}
          <div className="px-5 py-5 border-b" style={{ borderColor: "rgba(255,255,255,.08)" }}>
            <Link href="/dashboard" className="flex items-center gap-2.5" onClick={() => setIsMobileOpen(false)}>
              <div
                className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ background: "#1a8754" }}
              >
                <span className="text-white font-extrabold text-base">S</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div>
                  <span className="text-white/90 font-extrabold text-[17px] tracking-tight">Snap</span>
                  <span style={{ color: "#1a8754" }} className="font-extrabold text-[17px] tracking-tight">AI</span>
                </div>
                <span
                  className="text-[8px] font-bold tracking-widest uppercase px-1.5 py-0.5 rounded"
                  style={{
                    background: "rgba(26,135,84,.25)",
                    color: "#1a8754",
                    border: "1px solid rgba(26,135,84,.35)",
                    letterSpacing: "0.1em",
                  }}
                >
                  EARLY ACCESS
                </span>
              </div>
            </Link>
          </div>

          {/* ââ New Assessment CTA âââââââââââââââââââââââââââââââââââââââââ */}
          <div className="px-3 pt-4 pb-2" suppressHydrationWarning>
            <Link
              href="/assess"
              onClick={() => setIsMobileOpen(false)}
              className="flex items-center justify-center gap-2 w-full py-3 rounded-xl text-white font-bold text-[14px] transition-all hover:brightness-110 active:scale-95"
              style={{
                background: "linear-gradient(135deg, #1a8754 0%, #159a5e 100%)",
                boxShadow: "0 4px 14px rgba(26,135,84,.45)",
                letterSpacing: "-0.2px",
              }}
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="8" r="7.25" stroke="white" strokeWidth="1.5" strokeOpacity="0.6"/>
                <path d="M8 5v6M5 8h6" stroke="white" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              New Assessment
            </Link>
          </div>

          {/* ââ Nav Sections âââââââââââââââââââââââââââââââââââââââââââââââ */}
          <nav className="flex-1 px-2.5 py-3 overflow-y-auto">
            {navSections.map((section) => (
              <div key={section.section}>
                <div
                  className="px-3 pt-4 pb-1.5 text-[9px] font-bold uppercase tracking-widest"
                  style={{ color: "rgba(255,255,255,.25)", letterSpacing: "1.2px" }}
                >
                  {section.section}
                </div>
                <div className="space-y-0.5">
                  {section.items.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setIsMobileOpen(false)}
                      className={`flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-[13px] transition-all ${
                        isActive(item.href)
                          ? "text-white font-semibold"
                          : "font-medium hover:text-white/85"
                      }`}
                      style={{
                        background: isActive(item.href) ? "rgba(26,135,84,.2)" : "transparent",
                        color: isActive(item.href) ? "white" : "rgba(255,255,255,.55)",
                      }}
                    >
                      <span className="w-5 flex-shrink-0 flex items-center justify-center opacity-70">
                        {NavIcons[item.iconKey] ?? null}
                      </span>
                      <span className="flex-1">{item.label}</span>
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </nav>

          {/* ââ Feedback Button ââââââââââââââââââââââââââââââââââââââââââââ */}
          <div className="px-3 pb-2">
            <button
              onClick={() => { setFeedbackOpen(true); setIsMobileOpen(false); }}
              className="flex items-center gap-2 w-full px-3 py-2.5 rounded-lg text-[13px] font-medium transition-all hover:bg-white/5"
              style={{ color: "rgba(255,255,255,.4)" }}
            >
              <span className="w-5 flex-shrink-0 flex items-center justify-center opacity-70">
                {NavIcons.feedback}
              </span>
              <span>Send Feedback</span>
            </button>
          </div>

          {/* ââ Footer / User Area âââââââââââââââââââââââââââââââââââââââââ */}
          {/* ── Footer / User Area ───────────────────────────────────────────────────────────────────────────────── */}
          <div className="px-3 py-3 border-t flex-shrink-0" style={{ borderColor: "rgba(255,255,255,.08)" }}>
            <div className="flex items-center gap-2">
              {/* Avatar + name/email — links to settings */}
              <Link
                href="/settings"
                onClick={() => setIsMobileOpen(false)}
                className="flex items-center gap-2 flex-1 min-w-0 hover:opacity-80 transition-opacity"
              >
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
                  style={{ background: "#1a8754" }}
                >
                  {user?.firstName
                    ? user.firstName[0].toUpperCase()
                    : <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                  }
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-xs font-semibold truncate" style={{ color: "rgba(255,255,255,.85)" }}>
                    {user?.firstName
                      ? `${user.firstName}${user.lastName ? " " + user.lastName : ""}`
                      : user?.emailAddresses?.[0]?.emailAddress ?? "Account"}
                  </div>
                  <div className="text-[10px] truncate" style={{ color: "rgba(255,255,255,.4)" }}>
                    {user?.firstName && user?.emailAddresses?.[0]?.emailAddress
                      ? user.emailAddresses[0].emailAddress
                      : "Free Trial"}
                  </div>
                </div>
              </Link>
              {/* Log Out — always-visible icon, never cut off */}
              <button
                onClick={handleSignOut}
                title="Log Out"
                className="flex-shrink-0 p-2 rounded-lg transition-all hover:bg-white/10 active:bg-white/20"
                style={{ color: "rgba(255,255,255,.5)" }}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
                </svg>
              </button>
            </div>
          </div>

        </div>
      </aside>

      {/* In-app feedback modal (BUG-01 fix) */}
      <FeedbackModal open={feedbackOpen} onClose={() => setFeedbackOpen(false)} />
    </>
  );
}
