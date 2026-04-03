import { Navbar } from "@/components/layout/Navbar";
import { ListingGrid } from "@/components/marketplace/ListingGrid";
import { MarketplaceHeader } from "@/components/marketplace/MarketplaceHeader";
import { Server } from "lucide-react";

export const metadata = { title: "MCP Servers - agent-gen.ca" };

export default function McpServersPage() {
  return (
    <div className="flex min-h-screen flex-col tech-grid">
      <Navbar />
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 pb-16 pt-32 sm:px-6 sm:pt-36">
        <MarketplaceHeader
          icon={Server}
          title="MCP Servers"
          subtitle="Model Context Protocol server packages for production agent workflows."
          accent="hsl(var(--accent-mcp))"
          eyebrow="Category"
        />
        <ListingGrid defaultType="mcp_server" />
      </main>
    </div>
  );
}
