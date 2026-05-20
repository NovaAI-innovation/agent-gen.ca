import { Bot, LayoutGrid, Package, Server, Zap, type LucideIcon } from "lucide-react";
import type { PageHeaderConfig } from "@/components/system/PageHeader";

interface RouteHeaderConfig {
  icon: LucideIcon;
  title: string;
  subtitle: string;
  eyebrow: string;
  accentClassName: string;
}

export interface ListingSurfaceConfig {
  defaultType?: "mcp_server" | "agent_skill" | "custom_agent" | "pack";
  header: RouteHeaderConfig;
}

const DEFAULT_STATS = [
  { label: "Live listings", value: "500+" },
  { label: "Weekly installs", value: "8.1k" },
  { label: "Verified creators", value: "312" },
];

export const MARKETPLACE_SURFACES: Record<string, ListingSurfaceConfig> = {
  marketplace: {
    header: {
      icon: LayoutGrid,
      title: "Marketplace",
      subtitle: "Discover, evaluate, and install production-ready assets for AI agents.",
      eyebrow: "Discover",
      accentClassName: "text-action-primary",
    },
  },
  mcp: {
    defaultType: "mcp_server",
    header: {
      icon: Server,
      title: "MCP Servers",
      subtitle: "Model Context Protocol packages built for reliable runtime integration.",
      eyebrow: "Category",
      accentClassName: "text-cyan-300",
    },
  },
  skills: {
    defaultType: "agent_skill",
    header: {
      icon: Zap,
      title: "Agent Skills",
      subtitle: "Composable tools and capabilities you can plug into any agent workflow.",
      eyebrow: "Category",
      accentClassName: "text-amber-300",
    },
  },
  agents: {
    defaultType: "custom_agent",
    header: {
      icon: Bot,
      title: "Custom Agents",
      subtitle: "Full agent personalities and system bundles tuned for specific outcomes.",
      eyebrow: "Category",
      accentClassName: "text-lime-300",
    },
  },
  packs: {
    defaultType: "pack",
    header: {
      icon: Package,
      title: "Packs",
      subtitle: "Curated bundles that combine listings into deployment-ready stacks.",
      eyebrow: "Category",
      accentClassName: "text-violet-300",
    },
  },
};

export function toHeaderConfig(surface: ListingSurfaceConfig): PageHeaderConfig {
  return {
    ...surface.header,
    stats: DEFAULT_STATS,
  };
}
