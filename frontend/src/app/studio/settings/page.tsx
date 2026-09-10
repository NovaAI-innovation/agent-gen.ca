"use client";

import { Settings } from "lucide-react";
import { PageHeader } from "@/components/system/PageHeader";
import { Panel } from "@/components/ui/Panel";

export default function StudioSettingsPage() {
  return (
    <div className="space-y-5">
      <PageHeader
        icon={Settings}
        eyebrow="Creator Studio"
        title="Settings"
        subtitle="Manage your creator profile, payout address, and studio preferences."
        accentClassName="text-text-secondary"
      />
      <Panel padding="lg">
        <p className="text-sm text-text-secondary">
          Creator settings will include profile editing, payout wallet configuration, terms acceptance status, and studio-level notification preferences. Coming with IDN-005 (creator onboarding).
        </p>
      </Panel>
    </div>
  );
}