"use client";

import { useQuery } from "@tanstack/react-query";
import { Bot, LayoutGrid, Package, Search, Server, SlidersHorizontal, Zap } from "lucide-react";
import { api } from "@/lib/api";

export interface Filters {
  type: string;
  category: string;
  tag: string;
  q: string;
  sort: string;
  page: number;
}

interface Props {
  filters: Filters;
  onChange: (f: Filters) => void;
}

const TYPES = [
  { value: "", label: "All", icon: LayoutGrid, color: "hsl(var(--muted-foreground))" },
  { value: "mcp_server", label: "MCP Servers", icon: Server, color: "hsl(var(--accent-mcp))" },
  { value: "agent_skill", label: "Skills", icon: Zap, color: "hsl(var(--accent-skill))" },
  { value: "custom_agent", label: "Agents", icon: Bot, color: "hsl(var(--accent-agent))" },
  { value: "pack", label: "Packs", icon: Package, color: "hsl(var(--accent-pack))" },
];

const SORT_OPTIONS = [
  { value: "created_at", label: "Newest" },
  { value: "downloads", label: "Most Downloaded" },
  { value: "rating", label: "Top Rated" },
  { value: "price_asc", label: "Price (Low to High)" },
  { value: "price_desc", label: "Price (High to Low)" },
];

export function ListingFilters({ filters, onChange }: Props) {
  const { data: categories } = useQuery({
    queryKey: ["categories"],
    queryFn: async () =>
      (await api.get("/marketplace/categories")).data as { id: number; name: string; slug: string }[],
    staleTime: Infinity,
  });

  const set = (key: keyof Filters, value: string) => onChange({ ...filters, [key]: value, page: 1 });

  return (
    <div className="space-y-4">
      <div className="relative">
        <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="search"
          placeholder="Search listings..."
          value={filters.q}
          onChange={(e) => set("q", e.target.value)}
          className="h-11 w-full rounded-xl border border-border bg-muted/70 pl-10 pr-4 text-sm placeholder:text-muted-foreground outline-none transition-colors focus:border-primary/50 focus:bg-muted"
        />
      </div>

      <div className="flex flex-wrap gap-2">
        {TYPES.map(({ value, label, icon: Icon, color }) => {
          const active = filters.type === value;
          return (
            <button
              key={value}
              onClick={() => set("type", value)}
              className="flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-all duration-200"
              style={
                active
                  ? {
                      background: `color-mix(in srgb, ${color} 14%, transparent)`,
                      borderColor: `color-mix(in srgb, ${color} 45%, transparent)`,
                      color,
                    }
                  : {
                      background: "hsl(var(--muted) / 0.8)",
                      borderColor: "hsl(var(--border))",
                      color: "hsl(var(--muted-foreground))",
                    }
              }
            >
              <Icon className="h-3.5 w-3.5" />
              {label}
            </button>
          );
        })}
      </div>

      <div className="grid gap-2 sm:grid-cols-2">
        {categories && categories.length > 0 && (
          <select
            value={filters.category}
            onChange={(e) => set("category", e.target.value)}
            className="h-10 rounded-lg border border-border bg-muted/70 px-3 text-xs text-muted-foreground outline-none transition-colors focus:border-primary/50"
          >
            <option value="">All Categories</option>
            {categories.map((c) => (
              <option key={c.id} value={c.slug}>
                {c.name}
              </option>
            ))}
          </select>
        )}

        <div className="relative">
          <SlidersHorizontal className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <select
            value={filters.sort}
            onChange={(e) => set("sort", e.target.value)}
            className="h-10 w-full rounded-lg border border-border bg-muted/70 pl-8 pr-3 text-xs text-muted-foreground outline-none transition-colors focus:border-primary/50"
          >
            {SORT_OPTIONS.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
