import { History } from "lucide-react";
import { EmptyState } from "@/components/ui/EmptyState";
import { PageHeader } from "@/components/system/PageHeader";

export default function InstallHistoryPage() {
  return (
    <div className="space-y-5">
      <PageHeader
        icon={History}
        eyebrow="Creator"
        title="Install history"
        subtitle="Review install activity across your listings and identify high-retention assets."
        accentClassName="text-cyan-300"
      />
      <EmptyState
        icon={History}
        title="No install activity yet"
        description="Install history will appear here after your listings receive downloads and successful onboarding events."
      />
    </div>
  );
}
