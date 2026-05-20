import { ListingGrid } from "@/components/marketplace/ListingGrid";
import { MARKETPLACE_SURFACES, toHeaderConfig } from "@/components/marketplace/marketplaceConfig";
import { MarketplaceTemplate } from "@/components/templates/MarketplaceTemplate";

export const metadata = { title: "Marketplace - agent-gen.ca" };

export default function MarketplacePage() {
  const surface = MARKETPLACE_SURFACES.marketplace;

  return (
    <MarketplaceTemplate header={toHeaderConfig(surface)}>
      <ListingGrid defaultType={surface.defaultType} />
    </MarketplaceTemplate>
  );
}
