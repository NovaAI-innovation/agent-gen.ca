"use client";

import { useAuthStore } from "@/store/authStore";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { FileText, Plus } from "lucide-react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/system/PageHeader";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import type { Listing } from "@/components/marketplace/ListingCard";

export default function StudioDraftsPage() {
  const { user, token } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!token) router.push("/");
  }, [token, router]);

  const { data: listings, isLoading } = useQuery({
    queryKey: ["studio-drafts", user?.id],
    queryFn: async () => {
      const res = await api.get(`/users/${user!.wallet_address}/listings`, {
        params: { include_drafts: true },
      });
      return (res.data as Listing[]).filter((l) => l.state !== "published");
    },
    enabled: !!user,
  });

  return (
    <div className="space-y-5">
      <PageHeader
        icon={FileText}
        eyebrow="Creator Studio"
        title="Drafts"
        subtitle="Manage listings still in progress before submitting for review."
        accentClassName="text-amber-300"
        actions={
          <Button asChild>
            <Link href="/studio/listings/new">
              <Plus className="h-4 w-4" />
              New listing
            </Link>
          </Button>
        }
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
              <StatusBadge status={listing.state === "pending_review" ? "pending" : "draft"} />
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={FileText}
          title="No drafts"
          description="Create a new listing to start drafting."
          action={
            <Button asChild>
              <Link href="/studio/listings/new">Create listing</Link>
            </Button>
          }
        />
      )}
    </div>
  );
}