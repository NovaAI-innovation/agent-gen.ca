"use client";

import { Eye } from "lucide-react";
import { PageHeader } from "@/components/system/PageHeader";
import { Panel } from "@/components/ui/Panel";

export default function StudioReleasesPage() {
  return (
    <div className="space-y-5">
      <PageHeader
        icon={Eye}
        eyebrow="Creator Studio"
        title="Releases"
        subtitle="Track artifact versions, scan status, and release history across your listings."
        accentClassName="text-violet-300"
      />
      <Panel padding="lg">
        <p className="text-sm text-text-secondary">
          Release management coming in ART-003. This page will show scan state, version history, and allow rolling back to previous releases.
        </p>
      </Panel>
    </div>
  );
}