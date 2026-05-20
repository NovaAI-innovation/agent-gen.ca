"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight, Search } from "lucide-react";
import { api } from "@/lib/api";
import { ListingCard, type Listing } from "./ListingCard";
import { ListingFilters, type Filters } from "./ListingFilters";
import { Panel } from "@/components/ui/Panel";
import { EmptyState } from "@/components/ui/EmptyState";
import { Button } from "@/components/ui/Button";

function SkeletonCard() {
  return <div className="skeleton h-56 rounded-2xl" />;
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
    <div className="space-y-5">
      <Panel padding="md">
        <ListingFilters filters={filters} onChange={setFilters} />
      </Panel>

      <div className="flex items-center gap-2">
        <span className="font-mono text-xs uppercase tracking-[0.16em] text-text-muted">
          {isLoading ? "Querying listings" : `${data?.total ?? 0} results`}
        </span>
        {filters.q ? <span className="text-xs text-text-secondary">for &ldquo;{filters.q}&rdquo;</span> : null}
      </div>

      <AnimatePresence mode="wait">
        {isLoading ? (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
          >
            {Array.from({ length: 8 }).map((_, index) => (
              <SkeletonCard key={index} />
            ))}
          </motion.div>
        ) : data?.items.length === 0 ? (
          <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <EmptyState
              icon={Search}
              title="No listings found"
              description="No assets match your current filter state. Try changing type, category, or sort order."
            />
          </motion.div>
        ) : (
          <motion.div
            key="results"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
          >
            {(data?.items ?? []).map((listing, index) => (
              <motion.div
                key={listing.id}
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.28, delay: index * 0.03 }}
              >
                <ListingCard listing={listing} />
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {data && totalPages > 1 ? (
        <div className="flex items-center justify-center gap-2 pt-2">
          <Button
            variant="secondary"
            size="icon"
            disabled={filters.page === 1}
            onClick={() => setFilters((prev) => ({ ...prev, page: prev.page - 1 }))}
            type="button"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="min-w-20 text-center font-mono text-xs text-text-secondary">
            {filters.page} / {totalPages}
          </span>
          <Button
            variant="secondary"
            size="icon"
            disabled={filters.page >= totalPages}
            onClick={() => setFilters((prev) => ({ ...prev, page: prev.page + 1 }))}
            type="button"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      ) : null}
    </div>
  );
}
