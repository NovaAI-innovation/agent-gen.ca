"use client";

import { useQuery } from "@tanstack/react-query";
import { Bot, LayoutGrid, Package, Search, Server, SlidersHorizontal, Zap } from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/cn";

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
  { value: "", label: "All", icon: LayoutGrid, accentClass: "text-text-secondary" },
  { value: "mcp_server", label: "MCP", icon: Server, accentClass: "text-cyan-300" },
  { value: "agent_skill", label: "Skills", icon: Zap, accentClass: "text-amber-300" },
  { value: "custom_agent", label: "Agents", icon: Bot, accentClass: "text-lime-300" },
  { value: "pack", label: "Packs", icon: Package, accentClass: "text-violet-300" },
];

const SORT_OPTIONS = [
  { value: "created_at", label: "Newest" },
  { value: "downloads", label: "Most Downloaded" },
  { value: "rating", label: "Top Rated" },
  { value: "price_asc", label: "Price Low -> High" },
  { value: "price_desc", label: "Price High -> Low" },
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
        <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
        <input
          type="search"
          placeholder="Search listings, tags, and creators"
          value={filters.q}
          onChange={(e) => set("q", e.target.value)}
          className="h-11 w-full rounded-xl border border-border-subtle bg-surface-muted pl-10 pr-4 text-sm text-text-primary placeholder:text-text-muted outline-none transition-colors focus:border-border-focus"
        />
      </div>

      <div className="flex flex-wrap gap-2">
        {TYPES.map(({ value, label, icon: Icon, accentClass }) => {
          const active = filters.type === value;
          return (
            <button
              key={value}
              onClick={() => set("type", value)}
              className={cn(
                "inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-all duration-200",
                active
                  ? "border-border-focus bg-surface-hover text-text-primary"
                  : "border-border-subtle bg-surface-muted text-text-secondary hover:border-border-strong hover:text-text-primary"
              )}
              type="button"
            >
              <Icon className={cn("h-3.5 w-3.5", accentClass)} />
              {label}
            </button>
          );
        })}
      </div>

      <div className="grid gap-2 sm:grid-cols-2">
        {categories && categories.length > 0 ? (
          <select
            value={filters.category}
            onChange={(e) => set("category", e.target.value)}
            className="h-10 rounded-lg border border-border-subtle bg-surface-muted px-3 text-xs text-text-secondary outline-none transition-colors focus:border-border-focus"
            suppressHydrationWarning
          >
            <option value="">All Categories</option>
            {categories.map((category) => (
              <option key={category.id} value={category.slug}>
                {category.name}
              </option>
            ))}
          </select>
        ) : null}

        <div className="relative">
          <SlidersHorizontal className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-text-muted" />
          <select
            value={filters.sort}
            onChange={(e) => set("sort", e.target.value)}
            className="h-10 w-full rounded-lg border border-border-subtle bg-surface-muted pl-8 pr-3 text-xs text-text-secondary outline-none transition-colors focus:border-border-focus"
            suppressHydrationWarning
          >
            {SORT_OPTIONS.map((sort) => (
              <option key={sort.value} value={sort.value}>
                {sort.label}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
