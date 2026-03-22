"use client";
import ComingSoonPage from "@/components/ComingSoonPage";
export default function EquipmentAlertsPage() {
  return (
    <ComingSoonPage
      icon="⚠️"
      title="Aging Alerts"
      description="Proactive alerts when equipment in your customer base reaches critical age thresholds or matches known recall patterns."
      features={[
        "Automatic alerts when units hit 12, 15, and 18 years",
        "Push notifications to tech app on service day",
        "Recall match alerts from CPSC database",
        "Pre-written customer outreach templates",
        "Batch schedule follow-up assessments",
      ]}
      backHref="/dashboard"
    />
  );
}
