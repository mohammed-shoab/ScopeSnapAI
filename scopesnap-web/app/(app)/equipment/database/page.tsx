"use client";
import ComingSoonPage from "@/components/ComingSoonPage";
export default function EquipmentDatabasePage() {
  return (
    <ComingSoonPage
      icon="⚙️"
      title="Equipment Database"
      description="Browse and search the full SnapAI equipment database — 50,000+ HVAC models with specs, recall history, and failure rates."
      features={[
        "Search by brand, model, SEER rating, and age",
        "View failure probability curves by model",
        "Active recall tracking and alerts",
        "Compare replacement options side-by-side",
        "Import from serial number photo scan",
      ]}
      backHref="/dashboard"
    />
  );
}
