"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { ListChecks, Plus } from "lucide-react";
import { api } from "@/lib/api";
import { ListingCard, type Listing } from "@/components/marketplace/ListingCard";
import { PageHeader } from "@/components/system/PageHeader";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";

export default function MyListingsPage() {
  const { data: me } = useQuery({
    queryKey: ["me"],
    queryFn: async () => (await api.get("/users/me")).data,
  });

  const { data: listings, isLoading } = useQuery({
    queryKey: ["my-listings", me?.wallet_address],
    queryFn: async () => (await api.get(`/users/${me.wallet_address}/listings`)).data as Listing[],
    enabled: !!me,
  });

  return (
    <div className="space-y-5">
      <PageHeader
        icon={ListChecks}
        eyebrow="Creator"
        title="My listings"
        subtitle="Manage your public assets and monitor listing quality before buyers install."
        accentClassName="text-violet-300"
        actions={
          <Button asChild>
            <Link href="/publish">
              <Plus className="h-4 w-4" />
              New listing
            </Link>
          </Button>
        }
      />

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="skeleton h-52 rounded-2xl" />
          ))}
        </div>
      ) : listings && listings.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {listings.map((listing) => (
            <ListingCard key={listing.id} listing={listing} />
          ))}
        </div>
      ) : (
        <EmptyState
          icon={ListChecks}
          title="No listings published yet"
          description="Create your first listing to start building creator reputation and install momentum."
          action={
            <Button asChild>
              <Link href="/publish">Create listing</Link>
            </Button>
          }
        />
      )}
    </div>
  );
}
