"use client";
import ComingSoonPage from "@/components/ComingSoonPage";
export default function LeaderboardPage() {
  return (
    <ComingSoonPage
      icon="🏆"
      title="Tech Leaderboard"
      description="Gamify performance and motivate your team — ranked by estimates sent, close rate, and revenue generated."
      features={[
        "Weekly and monthly leaderboard rankings",
        "Close rate tracking per technician",
        "Revenue attribution by tech",
        "Bonus goal tracking and milestone badges",
        "Exportable performance reports",
      ]}
      backHref="/dashboard"
    />
  );
}
