"use client";
/**
 * SnapAI — Bottom Navigation Bar
 * SOW Task 1.6: Simplified for beta — 4 tabs only.
 *
 * Changes from pre-beta version:
 * - Removed "Intel" tab (analytics hidden behind feature flag for beta)
 * - 4 tabs: Home | Assess (hero) | Jobs | Settings
 * - Tab order: Home, Assess (center hero), Jobs, Settings
 * - Intel tab re-enabled when NEXT_PUBLIC_SHOW_INTEL=true (via featureFlags)
 */

import Link from "next/link";
import { usePathname } from "next/navigation";
import { featureFlags } from "@/lib/featureFlags";

// ── SVG icon helpers ──────────────────────────────────────────────────────────
const HomeIcon = ({ active }: { active: boolean }) => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth={active ? 2.2 : 1.75} strokeLinecap="round" strokeLinejoin="round">
    {active
      ? <path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H5a1 1 0 01-1-1V9.5z" fill="currentColor" stroke="currentColor"/>
      : <path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H5a1 1 0 01-1-1V9.5z"/>
    }
    {!active && <polyline points="9 22 9 12 15 12 15 22"/>}
  </svg>
);

const AssessIcon = () => (
  <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="white"
    strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
    <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/>
    <circle cx="12" cy="13" r="4"/>
  </svg>
);

const JobsIcon = ({ active }: { active: boolean }) => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth={active ? 2.2 : 1.75} strokeLinecap="round" strokeLinejoin="round">
    {active ? (
      <>
        <rect x="3" y="3" width="18" height="18" rx="2" fill="currentColor" opacity="0.15"/>
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <line x1="8" y1="8" x2="16" y2="8"/>
        <line x1="8" y1="12" x2="16" y2="12"/>
        <line x1="8" y1="16" x2="12" y2="16"/>
      </>
    ) : (
      <>
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <line x1="8" y1="8" x2="16" y2="8"/>
        <line x1="8" y1="12" x2="16" y2="12"/>
        <line x1="8" y1="16" x2="12" y2="16"/>
      </>
    )}
  </svg>
);

const IntelIcon = ({ active }: { active: boolean }) => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth={active ? 2.2 : 1.75} strokeLinecap="round" strokeLinejoin="round">
    {active ? (
      <>
        <rect x="2" y="13" width="4" height="9" rx="1" fill="currentColor"/>
        <rect x="9" y="8" width="4" height="14" rx="1" fill="currentColor"/>
        <rect x="16" y="4" width="4" height="18" rx="1" fill="currentColor"/>
      </>
    ) : (
      <>
        <rect x="2" y="13" width="4" height="9" rx="1"/>
        <rect x="9" y="8" width="4" height="14" rx="1"/>
        <rect x="16" y="4" width="4" height="18" rx="1"/>
      </>
    )}
  </svg>
);

const SettingsIcon = ({ active }: { active: boolean }) => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth={active ? 2.2 : 1.75} strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="3" fill={active ? "currentColor" : "none"}/>
    <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/>
  </svg>
);

// ── Tab definition ────────────────────────────────────────────────────────────
interface Tab {
  href: string;
  label: string;
  activeOn: string[];
  hero?: boolean;
  renderIcon: (active: boolean) => React.ReactNode;
}

function buildTabs(): Tab[] {
  const tabs: Tab[] = [
    {
      href: "/dashboard",
      label: "Home",
      activeOn: ["/dashboard"],
      renderIcon: (active) => <HomeIcon active={active} />,
    },
    {
      href: "/assess",
      label: "Assess",
      activeOn: ["/assess"],
      hero: true,
      renderIcon: (_active) => <AssessIcon />,
    },
  ];

  if (featureFlags.showJobs) {
    tabs.splice(2, 0, {
      href: "/assessments",
      label: "Jobs",
      activeOn: ["/assessments", "/assessment"],
      renderIcon: (active) => <JobsIcon active={active} />,
    });
  }

  if (featureFlags.showIntel) {
    tabs.splice(featureFlags.showJobs ? 3 : 2, 0, {
      href: "/analytics",
      label: "Intel",
      activeOn: ["/analytics", "/intelligence"],
      renderIcon: (active) => <IntelIcon active={active} />,
    });
  }

  tabs.push({
    href: "/settings",
    label: "Settings",
    activeOn: ["/settings"],
    renderIcon: (active) => <SettingsIcon active={active} />,
  });

  return tabs;
}

export default function BottomNav() {
  const pathname = usePathname();

  const isActive = (tab: Tab) =>
    tab.activeOn.some((p) => pathname === p || pathname.startsWith(p + "/"));

  const tabs = buildTabs();

  return (
    <nav
      className="md:hidden fixed bottom-0 left-0 right-0 z-40 flex items-end justify-around"
      style={{
        background: "rgba(255,255,255,0.96)",
        backdropFilter: "blur(12px)",
        WebkitBackdropFilter: "blur(12px)",
        borderTop: "1px solid #e2dfd7",
        paddingBottom: "env(safe-area-inset-bottom, 0px)",
        height: "calc(64px + env(safe-area-inset-bottom, 0px))",
      }}
      aria-label="Main navigation"
    >
      {tabs.map((tab) => {
        const active = isActive(tab);

        if (tab.hero) {
          return (
            <Link
              key={tab.href}
              href={tab.href}
              aria-label="Start new assessment"
              aria-current={active ? "page" : undefined}
              className="flex flex-col items-center justify-end pb-2 gap-1 flex-1"
              style={{ textDecoration: "none" }}
            >
              <div
                className="flex items-center justify-center rounded-full"
                style={{
                  width: 52,
                  height: 52,
                  background: "linear-gradient(135deg, #1a8754 0%, #159a5e 100%)",
                  boxShadow: active
                    ? "0 6px 20px rgba(26,135,84,.6)"
                    : "0 4px 14px rgba(26,135,84,.45)",
                  transform: "translateY(-8px)",
                  transition: "box-shadow 0.2s, transform 0.2s",
                }}
              >
                {tab.renderIcon(active)}
              </div>
              <span
                className="text-[10px] font-semibold"
                style={{ color: "#1a8754", marginTop: -4 }}
              >
                {tab.label}
              </span>
            </Link>
          );
        }

        return (
          <Link
            key={tab.href}
            href={tab.href}
            aria-label={`Navigate to ${tab.label}`}
            aria-current={active ? "page" : undefined}
            className="flex flex-col items-center justify-end pb-2 gap-1 flex-1 min-h-[44px]"
            style={{
              textDecoration: "none",
              color: active ? "#1a8754" : "#7a7770",
              transition: "color 0.15s",
            }}
          >
            <div className="flex items-center justify-center w-6 h-6">
              {tab.renderIcon(active)}
            </div>
            <span
              className="text-[10px] font-semibold"
              style={{ color: active ? "#1a8754" : "#7a7770" }}
            >
              {tab.label}
            </span>
          </Link>
        );
      })}
    </nav>
  );
}
