"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Bot, Download, Package, Server, Star, Zap } from "lucide-react";

export const TYPE_META = {
  mcp_server: {
    icon: Server,
    label: "MCP Server",
    color: "hsl(var(--accent-mcp))",
    glow: "glow-mcp",
    bg: "hsl(183 100% 50% / 0.07)",
    border: "hsl(183 100% 50% / 0.18)",
  },
  agent_skill: {
    icon: Zap,
    label: "Agent Skill",
    color: "hsl(var(--accent-skill))",
    glow: "glow-skill",
    bg: "hsl(38 95% 55% / 0.07)",
    border: "hsl(38 95% 55% / 0.18)",
  },
  custom_agent: {
    icon: Bot,
    label: "Custom Agent",
    color: "hsl(var(--accent-agent))",
    glow: "glow-agent",
    bg: "hsl(142 75% 50% / 0.07)",
    border: "hsl(142 75% 50% / 0.18)",
  },
  pack: {
    icon: Package,
    label: "Pack",
    color: "hsl(var(--accent-pack))",
    glow: "glow-pack",
    bg: "hsl(270 85% 65% / 0.07)",
    border: "hsl(270 85% 65% / 0.18)",
  },
} as const;

export interface Listing {
  id: string;
  type: keyof typeof TYPE_META;
  title: string;
  slug: string;
  description: string | null;
  price_sol: string;
  download_count: number;
  avg_rating: string | null;
  owner_id: string;
  tags: { id: number; name: string }[];
}

export function ListingCard({ listing }: { listing: Listing }) {
  const meta = TYPE_META[listing.type];
  const Icon = meta.icon;
  const isFree = parseFloat(listing.price_sol) === 0;

  return (
    <motion.div whileHover={{ y: -3, scale: 1.01 }} transition={{ type: "spring", stiffness: 400, damping: 25 }}>
      <Link
        href={`/marketplace/${listing.slug}`}
        className={`group relative flex flex-col gap-3 rounded-2xl border p-5 transition-shadow duration-300 hover:${meta.glow}`}
        style={{ background: "hsl(var(--card))", borderColor: "hsl(var(--border))" }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLElement).style.borderColor = meta.border;
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLElement).style.borderColor = "hsl(var(--border))";
        }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 rounded-lg px-2 py-1 text-xs font-medium" style={{ background: meta.bg, color: meta.color }}>
            <Icon className="h-3 w-3" />
            {meta.label}
          </div>
          <span className="font-mono text-sm font-bold" style={{ color: isFree ? "hsl(var(--muted-foreground))" : meta.color }}>
            {isFree ? "Free" : `SOL ${parseFloat(listing.price_sol).toFixed(3)}`}
          </span>
        </div>

        <div>
          <h3 className="line-clamp-1 font-semibold leading-snug transition-colors duration-200" style={{ color: "hsl(var(--foreground))" }}>
            {listing.title}
          </h3>
          {listing.description && <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">{listing.description}</p>}
        </div>

        <div className="mt-auto flex items-center justify-between text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <Download className="h-3 w-3" />
            {listing.download_count.toLocaleString()}
          </span>
          {listing.avg_rating && (
            <span className="flex items-center gap-1">
              <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
              {parseFloat(listing.avg_rating).toFixed(1)}
            </span>
          )}
        </div>

        {listing.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {listing.tags.slice(0, 3).map((tag) => (
              <span key={tag.id} className="rounded-md bg-white/5 px-2 py-0.5 text-[11px] text-muted-foreground">
                {tag.name}
              </span>
            ))}
          </div>
        )}

        <div
          className="absolute right-3.5 top-3.5 h-1.5 w-1.5 rounded-full opacity-0 transition-opacity duration-200 group-hover:opacity-100"
          style={{ background: meta.color }}
        />
      </Link>
    </motion.div>
  );
}
