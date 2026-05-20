import { ListingGrid } from "@/components/marketplace/ListingGrid";
import { MARKETPLACE_SURFACES, toHeaderConfig } from "@/components/marketplace/marketplaceConfig";
import { MarketplaceTemplate } from "@/components/templates/MarketplaceTemplate";

export const metadata = { title: "Custom Agents - agent-gen.ca" };

export default function AgentsPage() {
  const surface = MARKETPLACE_SURFACES.agents;

  return (
    <MarketplaceTemplate header={toHeaderConfig(surface)}>
      <ListingGrid defaultType={surface.defaultType} />
    </MarketplaceTemplate>
  );
}
