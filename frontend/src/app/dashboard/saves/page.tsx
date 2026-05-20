import { Bookmark } from "lucide-react";
import { EmptyState } from "@/components/ui/EmptyState";
import { PageHeader } from "@/components/system/PageHeader";

export default function SavesPage() {
  return (
    <div className="space-y-5">
      <PageHeader
        icon={Bookmark}
        eyebrow="Creator"
        title="Saved listings"
        subtitle="Pin high-signal listings for benchmarking, inspiration, and quick revisit."
        accentClassName="text-amber-300"
      />
      <EmptyState
        icon={Bookmark}
        title="No saved listings"
        description="Bookmark listings from the marketplace and they will appear here for fast access."
      />
    </div>
  );
}
