import { Navbar } from "@/components/layout/Navbar";
import { ListingGrid } from "@/components/marketplace/ListingGrid";
import { MarketplaceHeader } from "@/components/marketplace/MarketplaceHeader";
import { Zap } from "lucide-react";

export const metadata = { title: "Agent Skills - agent-gen.ca" };

export default function AgentSkillsPage() {
  return (
    <div className="flex min-h-screen flex-col tech-grid">
      <Navbar />
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 pb-16 pt-32 sm:px-6 sm:pt-36">
        <MarketplaceHeader
          icon={Zap}
          title="Agent Skills"
          subtitle="Reusable tools and skills designed for AI agents."
          accent="hsl(var(--accent-skill))"
          eyebrow="Category"
        />
        <ListingGrid defaultType="agent_skill" />
      </main>
    </div>
  );
}
