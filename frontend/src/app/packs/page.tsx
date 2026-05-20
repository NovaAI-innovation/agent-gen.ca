import { ListingGrid } from "@/components/marketplace/ListingGrid";
import { MARKETPLACE_SURFACES, toHeaderConfig } from "@/components/marketplace/marketplaceConfig";
import { MarketplaceTemplate } from "@/components/templates/MarketplaceTemplate";

export const metadata = { title: "Packs - agent-gen.ca" };

export default function PacksPage() {
  const surface = MARKETPLACE_SURFACES.packs;

  return (
    <MarketplaceTemplate header={toHeaderConfig(surface)}>
      <ListingGrid defaultType={surface.defaultType} />
    </MarketplaceTemplate>
  );
}
