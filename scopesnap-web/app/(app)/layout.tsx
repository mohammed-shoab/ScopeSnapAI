/**
 * Authenticated App Layout — RW-01 updated, RW-06 offline banner added
 * Adds BottomNav for mobile. Sidebar stays for desktop.
 * pb-24 on mobile so content clears the 64px bottom nav.
 */

import SidebarNav from "@/components/SidebarNav";
import BottomNav from "@/components/BottomNav";
import OfflineBanner from "@/components/OfflineBanner";

const IS_DEV = process.env.NEXT_PUBLIC_ENV === "development" ||
  process.env.NODE_ENV === "development";

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  if (!IS_DEV) {
    try {
      const { auth } = await import("@clerk/nextjs/server");
      const { redirect } = await import("next/navigation");
      const { userId } = await auth();
      if (!userId) {
        redirect("/sign-in");
      }
    } catch {
      // Clerk not configured — continue in dev mode
    }
  }

  return (
    <div className="min-h-screen bg-surface-bg" suppressHydrationWarning>
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
    </div>
  );
}
