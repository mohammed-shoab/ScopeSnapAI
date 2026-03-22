"use client";
import ComingSoonPage from "@/components/ComingSoonPage";
export default function TechniciansPage() {
  return (
    <ComingSoonPage
      icon="👥"
      title="Technicians"
      description="Manage your field team — add techs, set roles, track individual performance, and control what each tech can see and do."
      features={[
        "Add unlimited technicians per company",
        "Role-based access: tech / admin / owner",
        "Per-tech estimate count and close rate",
        "GPS job check-in and time tracking",
        "Invite via email — no IT required",
      ]}
      backHref="/dashboard"
    />
  );
}
