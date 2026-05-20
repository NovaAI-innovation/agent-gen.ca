import { DollarSign } from "lucide-react";
import { EmptyState } from "@/components/ui/EmptyState";
import { PageHeader } from "@/components/system/PageHeader";

export default function EarningsPage() {
  return (
    <div className="space-y-5">
      <PageHeader
        icon={DollarSign}
        eyebrow="Creator"
        title="Earnings"
        subtitle="Track payouts, conversion, and revenue performance as purchasing flows come online."
        accentClassName="text-emerald-300"
      />
      <EmptyState
        icon={DollarSign}
        title="Earnings view is warming up"
        description="No payout data yet. Revenue analytics and settlement history will populate once paid installs are live."
      />
    </div>
  );
}
