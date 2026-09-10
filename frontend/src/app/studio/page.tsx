"use client";

import { useAuthStore } from "@/store/authStore";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  FileText,
  Layers,
  Plus,
  Sparkles,
  ArrowRight,
} from "lucide-react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/system/PageHeader";
import { Panel } from "@/components/ui/Panel";
import { Button } from "@/components/ui/Button";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { Listing } from "@/components/marketplace/ListingCard";

export default function StudioPage() {
  const { user, token } = useAuthStore();
  const router = useRouter();

  // Gate: unauthenticated users see sign-in state
  useEffect(() => {
    if (!token) router.push("/");
  }, [token, router]);

  // Fetch creator's listings (including drafts)
  const { data: listings, isLoading } = useQuery({
    queryKey: ["studio-listings", user?.id],
    queryFn: async () => {
      const res = await api.get(`/users/${user!.wallet_address}/listings`, {
        params: { include_drafts: true },
      });
      return res.data as Listing[];
    },
    enabled: !!user,
  });

  // Unauthenticated / loading skeleton
  if (!user) {
    return (
      <div className="space-y-4">
        <div className="skeleton h-24 rounded-2xl" />
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="skeleton h-32 rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  // Creator-not-approved landing
  if (user.creator_state !== "approved") {
    return (
      <div className="space-y-5">
        <PageHeader
          icon={Sparkles}
          eyebrow="Creator Studio"
          title="You're almost there"
          subtitle="Your creator account is pending review. Once approved you'll be able to create, edit, and publish listings through the Studio."
          accentClassName="text-amber-300"
        />
        <Panel padding="md">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-border-subtle bg-surface-muted">
              <FileText className="h-4 w-4 text-amber-300" />
            </div>
            <div>
              <p className="text-sm font-medium text-text-primary">Account status</p>
              <p className="text-xs text-text-secondary">
                {user.creator_state === "pending_approval"
                  ? "Pending approval — an admin will review your account shortly."
                  : user.creator_state === "suspended"
                    ? "Your creator account is suspended."
                    : "Your creator account is banned."}
              </p>
            </div>
          </div>
        </Panel>
      </div>
    );
  }

  // Approved creator — main studio dashboard
  const draftCount = listings?.filter((l) => l.state !== "published").length ?? 0;
  const publishedCount = listings?.filter((l) => l.state === "published").length ?? 0;

  const displayName =
    user.username ?? `${user.wallet_address.slice(0, 6)}...${user.wallet_address.slice(-4)}`;

  return (
    <div className="space-y-5">
      <PageHeader
        icon={Sparkles}
        eyebrow="Creator Studio"
        title={displayName}
        subtitle="Manage your listings, track draft status, and publish marketplace assets."
        accentClassName="text-action-primary"
        stats={[
          { label: "Drafts", value: String(draftCount) },
          { label: "Published", value: String(publishedCount) },
        ]}
        actions={
          <Button asChild>
            <Link href="/studio/listings/new">
              <Plus className="h-4 w-4" />
              New listing
            </Link>
          </Button>
        }
      />

      {/* Quick stats */}
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Panel padding="md">
          <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg border border-border-subtle bg-surface-muted">
            <FileText className="h-4 w-4 text-amber-300" />
          </div>
          <p className="font-mono text-2xl font-semibold text-text-primary">{draftCount}</p>
          <p className="mt-1 text-xs uppercase tracking-[0.16em] text-text-muted">Drafts in progress</p>
        </Panel>

        <Panel padding="md">
          <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg border border-border-subtle bg-surface-muted">
            <Layers className="h-4 w-4 text-cyan-300" />
          </div>
          <p className="font-mono text-2xl font-semibold text-text-primary">{publishedCount}</p>
          <p className="mt-1 text-xs uppercase tracking-[0.16em] text-text-muted">Published listings</p>
        </Panel>
      </section>

      {/* Recent listings (drafts + published) */}
      <Panel padding="md">
        <div className="mb-4 flex items-center justify-between">
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-text-muted">
            Recent listings
          </p>
          <Link
            href="/studio/drafts"
            className="flex items-center gap-1 text-xs text-action-primary hover:underline"
          >
            View all <ArrowRight className="h-3 w-3" />
          </Link>
        </div>

        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="skeleton h-14 rounded-xl" />
            ))}
          </div>
        ) : listings && listings.length > 0 ? (
          <div className="space-y-2">
            {listings.slice(0, 5).map((listing) => (
              <Link
                key={listing.id}
                href={`/studio/listings/${listing.id}/edit`}
                className="flex items-center justify-between rounded-xl border border-border-subtle bg-surface-muted/45 px-4 py-3 transition hover:border-border-strong hover:bg-surface-muted"
              >
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-text-primary">{listing.title}</p>
                  <p className="text-xs text-text-muted">
                    {listing.type.replace(/_/g, " ")} · v{listing.download_count ?? 0}
                  </p>
                </div>
                <StatusBadge status={listing.state === "published" ? "published" : listing.state === "pending_review" ? "pending" : "draft"} />
              </Link>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3 py-8">
            <FileText className="h-8 w-8 text-text-muted" />
            <p className="text-sm text-text-secondary">No listings yet — create your first one!</p>
            <Button asChild size="sm">
              <Link href="/studio/listings/new">Create listing</Link>
            </Button>
          </div>
        )}
      </Panel>
    </div>
  );
}