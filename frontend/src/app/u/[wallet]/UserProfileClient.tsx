"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { ListingCard, type Listing } from "@/components/marketplace/ListingCard";
import { Panel } from "@/components/ui/Panel";
import { BadgeCheck, Wallet } from "lucide-react";

interface User {
  id: string;
  wallet_address: string;
  username: string | null;
  bio: string | null;
  avatar_url: string | null;
  reputation_score: number;
  is_verified: boolean;
  created_at: string;
}

export function UserProfileClient({ wallet }: { wallet: string }) {
  const { data: user, isLoading } = useQuery({
    queryKey: ["user", wallet],
    queryFn: async () => (await api.get(`/users/${wallet}`)).data as User,
  });

  const { data: listings } = useQuery({
    queryKey: ["user-listings", wallet],
    queryFn: async () => (await api.get(`/users/${wallet}/listings`)).data as Listing[],
    enabled: !!user,
  });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="skeleton h-36 rounded-2xl" />
        <div className="skeleton h-72 rounded-2xl" />
      </div>
    );
  }

  if (!user) {
    return <p className="text-sm text-text-secondary">User not found.</p>;
  }

  const displayName = user.username ?? `${user.wallet_address.slice(0, 6)}...${user.wallet_address.slice(-4)}`;

  return (
    <div className="space-y-6">
      <Panel padding="lg">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-start gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl border border-border-subtle bg-surface-muted text-xl font-bold text-action-primary">
              {displayName.charAt(0).toUpperCase()}
            </div>
            <div>
              <h1 className="font-display text-3xl font-bold text-text-primary">{displayName}</h1>
              <p className="mt-1 inline-flex items-center gap-1.5 font-mono text-[11px] uppercase tracking-[0.14em] text-text-muted">
                <Wallet className="h-3.5 w-3.5" />
                {user.wallet_address}
              </p>
              {user.bio ? <p className="mt-3 max-w-2xl text-sm text-text-secondary">{user.bio}</p> : null}
            </div>
          </div>

          <div className="space-y-2">
            {user.is_verified ? (
              <span className="inline-flex items-center gap-1.5 rounded-full border border-action-primary/30 bg-action-primary/10 px-3 py-1 text-xs text-action-primary">
                <BadgeCheck className="h-3.5 w-3.5" />
                Verified
              </span>
            ) : null}
            <p className="font-mono text-xs text-text-secondary">Reputation: {user.reputation_score}</p>
          </div>
        </div>
      </Panel>

      <Panel padding="lg">
        <h2 className="font-display text-2xl font-bold text-text-primary">
          Published listings ({listings?.length ?? 0})
        </h2>

        {listings && listings.length > 0 ? (
          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {listings.map((listing) => (
              <ListingCard key={listing.id} listing={listing} />
            ))}
          </div>
        ) : (
          <p className="mt-3 text-sm text-text-secondary">No published listings yet.</p>
        )}
      </Panel>
    </div>
  );
}
