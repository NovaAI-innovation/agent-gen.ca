"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight, Search } from "lucide-react";
import { api } from "@/lib/api";
import { ListingCard, type Listing } from "./ListingCard";
import { ListingFilters, type Filters } from "./ListingFilters";

function SkeletonCard() {
  return <div className="skeleton h-52 rounded-2xl" />;
}

export function ListingGrid({ defaultType }: { defaultType?: string }) {
  const [filters, setFilters] = useState<Filters>({
    type: defaultType ?? "",
    category: "",
    tag: "",
    q: "",
    sort: "created_at",
    page: 1,
  });

  const { data, isLoading } = useQuery({
    queryKey: ["listings", filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.type) params.set("type", filters.type);
      if (filters.category) params.set("category", filters.category);
      if (filters.tag) params.set("tag", filters.tag);
      if (filters.q) params.set("q", filters.q);
      params.set("sort", filters.sort);
      params.set("page", String(filters.page));
      const res = await api.get(`/listings?${params}`);
      return res.data as { items: Listing[]; total: number; page: number; page_size: number };
    },
  });

  const totalPages = data ? Math.ceil(data.total / data.page_size) : 1;

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-white/10 bg-card/55 p-4 backdrop-blur-sm sm:p-5">
        <ListingFilters filters={filters} onChange={setFilters} />
      </div>

      <div className="flex min-h-6 items-center gap-2">
        <span className="font-mono text-xs text-muted-foreground">
          {isLoading ? "Loading results..." : `${data?.total ?? 0} results`}
        </span>
        {filters.q && (
          <span className="font-mono text-xs" style={{ color: "hsl(var(--primary))" }}>
            for &ldquo;{filters.q}&rdquo;
          </span>
        )}
      </div>

      <AnimatePresence mode="wait">
        {isLoading ? (
          <motion.div
            key="skeleton"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
          >
            {Array.from({ length: 8 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </motion.div>
        ) : data?.items.length === 0 ? (
          <motion.div
            key="empty"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center rounded-2xl border border-white/10 bg-card/35 py-24 text-center"
          >
            <div className="mb-4 rounded-full border border-border bg-muted p-5 text-primary">
              <Search className="h-7 w-7" />
            </div>
            <h3 className="text-lg font-semibold">No listings found</h3>
            <p className="mt-1 text-sm text-muted-foreground">Try adjusting your filters or search query.</p>
          </motion.div>
        ) : (
          <motion.div
            key="results"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
          >
            {data?.items.map((listing, i) => (
              <motion.div
                key={listing.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.35, delay: i * 0.04, ease: [0.34, 1.56, 0.64, 1] }}
              >
                <ListingCard listing={listing} />
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {data && totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-4">
          <button
            disabled={filters.page === 1}
            onClick={() => setFilters((f) => ({ ...f, page: f.page - 1 }))}
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-muted text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground disabled:opacity-30"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>

          <span className="font-mono text-xs text-muted-foreground">
            {filters.page} / {totalPages}
          </span>

          <button
            disabled={filters.page >= totalPages}
            onClick={() => setFilters((f) => ({ ...f, page: f.page + 1 }))}
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-muted text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground disabled:opacity-30"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
}
