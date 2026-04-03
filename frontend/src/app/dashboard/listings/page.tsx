"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { ListingCard, type Listing } from "@/components/marketplace/ListingCard";
import Link from "next/link";

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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">My Listings</h2>
        <Link
          href="/publish"
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          + New Listing
        </Link>
      </div>
      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => <div key={i} className="h-48 animate-pulse rounded-xl bg-muted" />)}
        </div>
      ) : listings && listings.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {listings.map((l) => <ListingCard key={l.id} listing={l} />)}
        </div>
      ) : (
        <p className="text-muted-foreground">You haven't published any listings yet.</p>
      )}
    </div>
  );
}
