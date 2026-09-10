"use client";

import { useAuthStore } from "@/store/authStore";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Layers } from "lucide-react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/system/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { EmptyState } from "@/components/ui/EmptyState";
import { Button } from "@/components/ui/Button";
import type { Listing } from "@/components/marketplace/ListingCard";

export default function StudioPublishedPage() {
  const { user, token } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!token) router.push("/");
  }, [token, router]);

  const { data: listings, isLoading } = useQuery({
    queryKey: ["studio-published", user?.id],
    queryFn: async () => {
      const res = await api.get(`/users/${user!.wallet_address}/listings`, {
        params: { include_drafts: true },
      });
      return (res.data as Listing[]).filter((l) => l.state === "published");
    },
    enabled: !!user,
  });

  return (
    <div className="space-y-5">
      <PageHeader
        icon={Layers}
        eyebrow="Creator Studio"
        title="Published"
        subtitle="Listings currently live in the marketplace."
        accentClassName="text-cyan-300"
      />

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="skeleton h-16 rounded-2xl" />
          ))}
        </div>
      ) : listings && listings.length > 0 ? (
        <div className="space-y-2">
          {listings.map((listing) => (
            <Link
              key={listing.id}
              href={`/studio/listings/${listing.id}/edit`}
              className="flex items-center justify-between rounded-2xl border border-border-subtle bg-surface-elevated/80 px-4 py-3 transition hover:border-border-strong hover:bg-surface-muted"
            >
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-text-primary">{listing.title}</p>
                <p className="text-xs text-text-muted">{listing.type.replace(/_/g, " ")}</p>
              </div>
              <StatusBadge status="published" />
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={Layers}
          title="No published listings"
          description="Submit a draft for review to start publishing."
        />
      )}
    </div>
  );
}