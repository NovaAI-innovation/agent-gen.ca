import { Navbar } from "@/components/layout/Navbar";
import { ListingGrid } from "@/components/marketplace/ListingGrid";
import { MarketplaceHeader } from "@/components/marketplace/MarketplaceHeader";
import { LayoutGrid } from "lucide-react";

export const metadata = { title: "Marketplace - agent-gen.ca" };

export default function MarketplacePage() {
  return (
    <div className="flex min-h-screen flex-col tech-grid">
      <Navbar />
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 pb-16 pt-32 sm:px-6 sm:pt-36">
        <MarketplaceHeader
          icon={LayoutGrid}
          title="Marketplace"
          subtitle="Discover MCP servers, agent skills, custom agents, and packs."
          accent="hsl(var(--primary))"
          eyebrow="Community"
        />
        <ListingGrid />
      </main>
    </div>
  );
}
