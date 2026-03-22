"use client";
import ComingSoonPage from "@/components/ComingSoonPage";
export default function IntegrationsPage() {
  return (
    <ComingSoonPage
      icon="🔗"
      title="Integrations"
      description="Connect ScopeSnap to your existing tools — CRMs, accounting software, and field service platforms."
      features={[
        "ServiceTitan two-way sync",
        "QuickBooks Online invoice export",
        "Google Calendar job scheduling",
        "Stripe payment collection",
        "Zapier webhook for any CRM",
      ]}
      backHref="/settings"
      backLabel="← Back to Settings"
    />
  );
}
