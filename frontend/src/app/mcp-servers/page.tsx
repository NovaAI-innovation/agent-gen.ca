import { ListingGrid } from "@/components/marketplace/ListingGrid";
import { MARKETPLACE_SURFACES, toHeaderConfig } from "@/components/marketplace/marketplaceConfig";
import { MarketplaceTemplate } from "@/components/templates/MarketplaceTemplate";

export const metadata = { title: "MCP Servers - agent-gen.ca" };

export default function McpServersPage() {
  const surface = MARKETPLACE_SURFACES.mcp;

  return (
    <MarketplaceTemplate header={toHeaderConfig(surface)}>
      <ListingGrid defaultType={surface.defaultType} />
    </MarketplaceTemplate>
  );
}
