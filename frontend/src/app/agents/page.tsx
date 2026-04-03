import { Navbar } from "@/components/layout/Navbar";
import { ListingGrid } from "@/components/marketplace/ListingGrid";
import { MarketplaceHeader } from "@/components/marketplace/MarketplaceHeader";
import { Bot } from "lucide-react";

export const metadata = { title: "Custom Agents - agent-gen.ca" };

export default function AgentsPage() {
  return (
    <div className="flex min-h-screen flex-col tech-grid">
      <Navbar />
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 pb-16 pt-32 sm:px-6 sm:pt-36">
        <MarketplaceHeader
          icon={Bot}
          title="Custom Agents"
          subtitle="Full agent configurations and personalities."
          accent="hsl(var(--accent-agent))"
          eyebrow="Category"
        />
        <ListingGrid defaultType="custom_agent" />
      </main>
    </div>
  );
}
