import { Navbar } from "@/components/layout/Navbar";
import { ListingGrid } from "@/components/marketplace/ListingGrid";
import { MarketplaceHeader } from "@/components/marketplace/MarketplaceHeader";
import { Package } from "lucide-react";

export const metadata = { title: "Packs - agent-gen.ca" };

export default function PacksPage() {
  return (
    <div className="flex min-h-screen flex-col tech-grid">
      <Navbar />
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 pb-16 pt-32 sm:px-6 sm:pt-36">
        <MarketplaceHeader
          icon={Package}
          title="Packs"
          subtitle="Curated bundles of marketplace items built for fast deployment."
          accent="hsl(var(--accent-pack))"
          eyebrow="Category"
        />
        <ListingGrid defaultType="pack" />
      </main>
    </div>
  );
}
