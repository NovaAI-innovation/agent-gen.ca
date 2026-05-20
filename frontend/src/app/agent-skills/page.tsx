import { ListingGrid } from "@/components/marketplace/ListingGrid";
import { MARKETPLACE_SURFACES, toHeaderConfig } from "@/components/marketplace/marketplaceConfig";
import { MarketplaceTemplate } from "@/components/templates/MarketplaceTemplate";

export const metadata = { title: "Agent Skills - agent-gen.ca" };

export default function AgentSkillsPage() {
  const surface = MARKETPLACE_SURFACES.skills;

  return (
    <MarketplaceTemplate header={toHeaderConfig(surface)}>
      <ListingGrid defaultType={surface.defaultType} />
    </MarketplaceTemplate>
  );
}
