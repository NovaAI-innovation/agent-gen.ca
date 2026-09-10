"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Bot, Download, Package, Server, Star, Zap } from "lucide-react";
import { cn } from "@/lib/cn";

export const TYPE_META = {
  mcp_server: {
    icon: Server,
    label: "MCP Server",
    colorClass: "text-cyan-300",
    chipClass: "border-cyan-400/30 bg-cyan-400/10 text-cyan-200",
  },
  agent_skill: {
    icon: Zap,
    label: "Agent Skill",
    colorClass: "text-amber-300",
    chipClass: "border-amber-400/30 bg-amber-400/10 text-amber-200",
  },
  custom_agent: {
    icon: Bot,
    label: "Custom Agent",
    colorClass: "text-lime-300",
    chipClass: "border-lime-400/30 bg-lime-400/10 text-lime-200",
  },
  pack: {
    icon: Package,
    label: "Pack",
    colorClass: "text-violet-300",
    chipClass: "border-violet-400/30 bg-violet-400/10 text-violet-200",
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
  state: string;
  tags: { id: number; name: string }[];
}

export interface ListingMetaViewModel {
  displayPrice: string;
  installCount: string;
  rating?: string;
}

function getListingViewModel(listing: Listing): ListingMetaViewModel {
  const isFree = parseFloat(listing.price_sol) === 0;

  return {
    displayPrice: isFree ? "Free" : `SOL ${parseFloat(listing.price_sol).toFixed(3)}`,
    installCount: listing.download_count.toLocaleString(),
    rating: listing.avg_rating ? parseFloat(listing.avg_rating).toFixed(1) : undefined,
  };
}

export function ListingCard({ listing }: { listing: Listing }) {
  const meta = TYPE_META[listing.type];
  const Icon = meta.icon;
  const model = getListingViewModel(listing);

  return (
    <motion.div whileHover={{ y: -4 }} transition={{ duration: 0.18 }}>
      <Link
        href={`/marketplace/${listing.slug}`}
        className="group flex h-full flex-col rounded-2xl border border-border-subtle bg-surface-elevated/85 p-5 transition-all duration-200 hover:border-border-focus hover:bg-surface-hover"
      >
        <div className="flex items-center justify-between gap-3">
          <span className={cn("inline-flex items-center gap-1 rounded-lg border px-2 py-1 text-xs font-medium", meta.chipClass)}>
            <Icon className="h-3.5 w-3.5" />
            {meta.label}
          </span>
          <span className={cn("font-mono text-sm font-semibold", meta.colorClass)}>{model.displayPrice}</span>
        </div>

        <div className="mt-3">
          <h3 className="line-clamp-1 text-lg font-semibold text-text-primary">{listing.title}</h3>
          <p className="mt-1 line-clamp-2 text-sm text-text-secondary">{listing.description ?? "No description provided yet."}</p>
        </div>

        <div className="mt-5 flex items-center justify-between text-xs text-text-muted">
          <span className="flex items-center gap-1.5">
            <Download className="h-3.5 w-3.5" />
            {model.installCount}
          </span>
          {model.rating ? (
            <span className="flex items-center gap-1.5">
              <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
              {model.rating}
            </span>
          ) : null}
        </div>

        <div className="mt-3 flex flex-wrap gap-1.5">
          {listing.tags.slice(0, 3).map((tag) => (
            <span key={tag.id} className="rounded-md border border-border-subtle bg-surface-muted px-2 py-0.5 text-[11px] text-text-muted">
              #{tag.name}
            </span>
          ))}
        </div>
      </Link>
    </motion.div>
  );
}
