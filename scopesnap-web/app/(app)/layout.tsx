/**
 * Authenticated App Layout — RW-01 updated, RW-06 offline banner added
 * Adds BottomNav for mobile. Sidebar stays for desktop.
 * pb-24 on mobile so content clears the 64px bottom nav.
 */

import SidebarNav from "@/components/SidebarNav";
import BottomNav from "@/components/BottomNav";
import OfflineBanner from "@/components/OfflineBanner";
import FeedbackButton from "@/components/FeedbackButton";
import InstallPrompt from "@/components/InstallPrompt";
import PostHogUserSync from "@/components/PostHogUserSync";
import { LanguageProvider } from "@/lib/language-context";

const IS_DEV = process.env.NEXT_PUBLIC_ENV === "development" ||
  process.env.NODE_ENV === "development";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://scopesnap-api-production.up.railway.app";

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  if (!IS_DEV) {
    try {
      const { auth } = await import("@clerk/nextjs/server");
      const { redirect } = await import("next/navigation");
      // Clerk v5: auth() returns a promise — must await
      const { userId, getToken } = await auth();
      if (!userId) {
        redirect("/sign-in");
      }

      // Check backend has a user record — new OAuth users may not have completed registration.
      // Section 7A: "Wow moment first" — if no backend record, send to /assess so the tech
      // can immediately experience the app. Profile setup is accessible from Settings.
      // Skip this check when already on /onboarding or /assess to avoid redirect loops.
      const { headers } = await import("next/headers");
      const pathname = headers().get("x-pathname") ?? "";
      const skipPaths = ["/onboarding", "/assess", "/settings"];
      if (!skipPaths.some((p) => pathname.startsWith(p))) {
        const token = await getToken();
        if (token) {
          const meRes = await fetch(`${API_URL}/api/auth/me`, {
            headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
            // Cache for 30s per user to avoid hitting the backend on every page render.
            next: { revalidate: 30 },
          });
          if (meRes.status === 404) {
            // User authenticated with Clerk but no backend record yet
            // (webhook may be delayed) — send to /assess for the wow moment.
            // The Clerk webhook will create their record in the background.
            redirect("/assess");
          }
        }
      }
    } catch (e) {
      // Re-throw Next.js redirect/notFound signals (they have a `digest` property)
      if (e && typeof e === "object" && "digest" in e) throw e;
      // Clerk not configured — continue in dev mode
    }
  }

  return (
    // LanguageProvider is a client component — no-op for US (always en),
    // activates RTL + Urdu translations for PK market users.
    <LanguageProvider>
    <div className="min-h-screen bg-surface-bg" suppressHydrationWarning>
      {/* Identify logged-in Clerk user in PostHog for event attribution */}
      <PostHogUserSync />
      <OfflineBanner />
      <SidebarNav />

      {/* Main Content — pb-24 on mobile clears the 64px bottom nav */}
      <main className="md:ml-60 transition-all duration-300">
        <div className="pt-16 md:pt-0 px-4 md:px-8 py-6 pb-24 md:pb-6">
          {IS_DEV && (
            <div className="mb-4 inline-block">
              <span
                className="text-xs font-mono font-medium px-3 py-1 rounded-full border"
                style={{
                  background: "#fef3e8",
                  color: "#c4600a",
                  borderColor: "rgba(196,96,10,.3)",
                }}
              >
                dev mode
              </span>
            </div>
          )}
          {children}
        </div>
      </main>

      {/* Mobile bottom nav — hidden on md+ */}
      <BottomNav />

      {/* PWA install 