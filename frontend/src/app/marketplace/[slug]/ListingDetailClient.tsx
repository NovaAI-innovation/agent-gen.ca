"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Download, Star, ChevronDown } from "lucide-react";
import { motion } from "framer-motion";
import { TYPE_META, type Listing } from "@/components/marketplace/ListingCard";

interface Version {
  id: string;
  version: string;
  changelog: string | null;
  install_instructions: string | null;
  config_json: unknown;
  is_latest: boolean;
  created_at: string;
}

interface Review {
  id: string;
  reviewer_id: string;
  rating: number;
  title: string | null;
  body: string | null;
  helpful_count: number;
  created_at: string;
}

export function ListingDetailClient({ slug }: { slug: string }) {
  const { data: listing, isLoading } = useQuery({
    queryKey: ["listing", slug],
    queryFn: async () => (await api.get(`/listings/${slug}`)).data as Listing,
  });

  const { data: versions } = useQuery({
    queryKey: ["listing-versions", slug],
    queryFn: async () => (await api.get(`/listings/${slug}/versions`)).data as Version[],
    enabled: !!listing,
  });

  const { data: reviews } = useQuery({
    queryKey: ["listing-reviews", slug],
    queryFn: async () => (await api.get(`/listings/${slug}/reviews`)).data as Review[],
    enabled: !!listing,
  });

  if (isLoading) {
    return (
      <div className="space-y-4 pt-4">
        <div className="skeleton h-12 w-2/3 rounded-xl" />
        <div className="skeleton h-6 w-full rounded-lg" />
        <div className="skeleton h-48 rounded-2xl" />
      </div>
    );
  }
  if (!listing) return <p className="pt-8 text-muted-foreground">Listing not found.</p>;

  const meta = TYPE_META[listing.type];
  const Icon = meta.icon;
  const latest = versions?.find((v) => v.is_latest);
  const isFree = parseFloat(listing.price_sol) === 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
      className="space-y-8"
    >
      {/* Header */}
      <div className="flex flex-col gap-6 sm:flex-row sm:items-start">
        <div
          className="flex h-16 w-16 flex-shrink-0 items-center justify-center rounded-2xl"
          style={{ background: meta.bg, border: `1px solid ${meta.border}` }}
        >
          <Icon className="h-8 w-8" style={{ color: meta.color }} />
        </div>

        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span
              className="rounded-md px-2 py-0.5 text-xs font-medium"
              style={{ background: meta.bg, color: meta.color }}
            >
              {meta.label}
            </span>
            {listing.avg_rating && (
              <span className="flex items-center gap-1 text-xs text-muted-foreground">
                <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
                {parseFloat(listing.avg_rating).toFixed(1)}
              </span>
            )}
          </div>
          <h1 className="mt-2 text-3xl font-bold tracking-tight">{listing.title}</h1>
          {listing.description && (
            <p className="mt-2 text-muted-foreground">{listing.description}</p>
          )}
          <div className="mt-3 flex items-center gap-4 text-sm text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <Download className="h-4 w-4" />
              {listing.download_count.toLocaleString()} installs
            </span>
            {latest && (
              <span className="font-mono text-xs">v{latest.version}</span>
            )}
          </div>
        </div>

        {/* CTA */}
        <div className="flex-shrink-0 text-right">
          <div
            className="mb-3 font-mono text-2xl font-bold"
            style={{ color: isFree ? "hsl(var(--muted-foreground))" : meta.color }}
          >
            {isFree ? "Free" : `◎ ${parseFloat(listing.price_sol).toFixed(3)}`}
          </div>
          <button
            className="w-full rounded-xl px-6 py-2.5 text-sm font-semibold transition-all duration-200 hover:opacity-90"
            style={{
              background: meta.color,
              color: "hsl(var(--background))",
              boxShadow: `0 0 20px color-mix(in srgb, ${meta.color} 40%, transparent)`,
            }}
          >
            {isFree ? "Install" : "Purchase"}
          </button>
        </div>
      </div>

      {/* Tags */}
      {listing.tags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {listing.tags.map((tag) => (
            <span
              key={tag.id}
              className="rounded-lg border border-border bg-muted px-2.5 py-1 text-xs text-muted-foreground"
            >
              #{tag.name}
            </span>
          ))}
        </div>
      )}

      {/* Install instructions */}
      {latest?.install_instructions && (
        <section>
          <h2 className="mb-3 text-lg font-semibold">Installation</h2>
          <pre className="overflow-x-auto rounded-xl border border-border bg-muted p-5 font-mono text-xs leading-relaxed text-foreground/90 whitespace-pre-wrap">
            {latest.install_instructions}
          </pre>
        </section>
      )}

      {/* Versions */}
      {versions && versions.length > 0 && (
        <section>
          <h2 className="mb-3 text-lg font-semibold">Version History</h2>
          <div className="space-y-2">
            {versions.map((v) => (
              <div
                key={v.id}
                className="flex items-center justify-between rounded-xl border border-border bg-muted/40 px-4 py-3"
              >
                <div className="flex items-center gap-3">
                  <span className="font-mono text-sm font-semibold">v{v.version}</span>
                  {v.is_latest && (
                    <span
                      className="rounded-md px-1.5 py-0.5 text-[10px] font-medium"
                      style={{ background: meta.bg, color: meta.color }}
                    >
                      latest
                    </span>
                  )}
                  {v.changelog && (
                    <p className="text-xs text-muted-foreground line-clamp-1">{v.changelog}</p>
                  )}
                </div>
                <span className="font-mono text-xs text-muted-foreground">
                  {new Date(v.created_at).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Reviews */}
      <section>
        <h2 className="mb-4 text-lg font-semibold">
          Reviews{" "}
          <span className="font-mono text-sm text-muted-foreground">({reviews?.length ?? 0})</span>
        </h2>
        {reviews && reviews.length > 0 ? (
          <div className="space-y-3">
            {reviews.map((r) => (
              <div
                key={r.id}
                className="rounded-xl border border-border bg-card p-4"
              >
                <div className="flex items-center justify-between">
                  <div className="flex gap-0.5">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star
                        key={i}
                        className={`h-3.5 w-3.5 ${i < r.rating ? "fill-amber-400 text-amber-400" : "text-muted"}`}
                      />
                    ))}
                  </div>
                  <span className="font-mono text-xs text-muted-foreground">
                    {new Date(r.created_at).toLocaleDateString()}
                  </span>
                </div>
                {r.title && <p className="mt-2 text-sm font-medium">{r.title}</p>}
                {r.body && <p className="mt-1 text-sm text-muted-foreground">{r.body}</p>}
              </div>
            ))}
          </div>
        ) : (
          <div className="rounded-xl border border-border bg-muted/30 py-12 text-center">
            <p className="text-sm text-muted-foreground">No reviews yet — be the first to review.</p>
          </div>
        )}
      </section>
    </motion.div>
  );
}
