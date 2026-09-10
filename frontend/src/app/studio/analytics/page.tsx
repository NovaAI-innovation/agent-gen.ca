"use client";

import { BarChart3 } from "lucide-react";
import { PageHeader } from "@/components/system/PageHeader";
import { Panel } from "@/components/ui/Panel";

export default function StudioAnalyticsPage() {
  return (
    <div className="space-y-5">
      <PageHeader
        icon={BarChart3}
        eyebrow="Creator Studio"
        title="Analytics"
        subtitle="Track installs, review scores, and marketplace performance across your catalog."
        accentClassName="text-cyan-300"
      />
      <Panel padding="lg">
        <p className="text-sm text-text-secondary">
          The analytics dashboard will populate once your listings begin receiving installs. Metrics will include installed-by-day charts, review scores, and revenue tracking (Release B).
        </p>
      </Panel>
    </div>
  );
}