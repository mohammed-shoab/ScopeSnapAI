"use client";
// v2
import Link from "next/link";
import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";

const NAV_SECTIONS = [
  {
    section: "OVERVIEW",
    items: [
      { label: "Dashboard",        href: "/dashboard",              icon: "📊" },
      { label: "Estimates",        href: "/estimates",              icon: "📋", badge: "47" },
      { label: "Accuracy Tracker", href: "/analytics",              icon: "🎯" },
    ],
  },
  {
    section: "INTELLIGENCE",
    items: [
      { label: "Profit Leaks",     href: "/intelligence/leaks",     icon: "🔍", badge: "$70K", badgeColor: "#c4600a" },
      { label: "BenchmarkIQ",      href: "/intelligence/benchmark", icon: "📈" },
      { label: "Property History", href: "/intelligence/history",   icon: "🏠" },
    ],
  },
  {
    section: "EQUIPMENT",
    items: [
      { label: "Equipment Database", href: "/equipment/database",   icon: "❄️" },
      { label: "Aging Alerts",       href: "/equipment/alerts",     icon: "⚠️", badge: "43", badgeColor: "#c62828" },
    ],
  },
  {
    section: "TEAM",
    items: [
      { label: "Technicians", href: "/team/technicians", icon: "👥" },
      { label: "Leaderboard", href: "/team/leaderboard", icon: "🏆" },
    ],
  },
  {
    section: "SETTINGS",
    items: [
      { label: "Pricing Database", href: "/settings/pricing",       icon: "💰" },
      { label: "Integrations",     href: "/settings/integrations",  icon: "🔗" },
      { label: "Settings",         href: "/settings",               icon: "⚙️" },
    ],
  },
];

export default function SidebarNav() {
  const pathname = usePathname();
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  // Defer active-state comparison until client is mounted to prevent hydration mismatch
  const isActive = (href: string) =>
    mounted && (pathname === href || pathname.startsWith(href + "/"));

  return (
    <>
      {/* Mobile hamburger */}
      <button
        onClick={() => setIsMobileOpen(!isMobileOpen)}
        className="md:hidden fixed top-4 left-4 z-40 p-2 hover:bg-gray-700 rounded-lg transition-colors"
        style={{ background: "#2a2a28" }}
      >
        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={isMobileOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} />
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
        className={`fixed top-0 left-0 h-screen w-60 overflow-y-auto transition-transform duration-300 ease-in-out z-30 md:z-10 ${
          isMobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
        style={{ background: "#1a1a18" }}
      >
        <div className="flex flex-col h-full">
          {/* Logo Area */}
          <div className="px-5 py-5 border-b" style={{ borderColor: "rgba(255,255,255,.08)" }}>
            <Link href="/dashboard" className="flex items-center gap-2.5" onClick={() => setIsMobileOpen(false)}>
              <div
                className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ background: "#1a8754" }}
              >
                <span className="text-white font-extrabold text-base">S</span>
              </div>
              <div>
                <span className="text-white/90 font-extrabold text-[17px] tracking-tight">Scope</span>
                <span style={{ color: "#1a8754" }} className="font-extrabold text-[17px] tracking-tight">Snap</span>
              </div>
            </Link>
          </div>

          {/* New Assessment CTA — the ONE button a tech needs */}
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

          {/* Nav Sections */}
          <nav className="flex-1 px-2.5 py-3 overflow-y-auto">
            {NAV_SECTIONS.map((section) => (
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
                      <span className="text-base w-6 text-center flex-shrink-0">{item.icon}</span>
                      <span className="flex-1">{item.label}</span>
                      {"badge" in item && item.badge && (
                        <span
                          className="text-[9px] font-bold px-1.5 py-0.5 rounded-full flex-shrink-0"
                          style={{
                            background: ("badgeColor" in item && item.badgeColor) ? item.badgeColor : "rgba(255,255,255,.18)",
                            color: "white",
                          }}
                        >
                          {item.badge}
                        </span>
                      )}
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </nav>

          {/* Footer with User Avatar */}
          <div className="px-3.5 py-4 border-t" style={{ borderColor: "rgba(255,255,255,.08)" }}>
            <div className="flex items-center gap-2.5">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
                style={{ background: "#1a8754" }}
              >
                DM
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-xs font-semibold truncate" style={{ color: "rgba(255,255,255,.85)" }}>
                  Dave Martinez
                </div>
                <div className="text-[10px] truncate" style={{ color: "rgba(255,255,255,.4)" }}>
                  ABC HVAC Services · Team Plan
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
