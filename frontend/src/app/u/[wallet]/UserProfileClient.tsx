"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { ListingCard, type Listing } from "@/components/marketplace/ListingCard";

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

  if (isLoading) return <div className="animate-pulse h-32 rounded-xl bg-muted" />;
  if (!user) return <p className="text-muted-foreground">User not found.</p>;

  const displayName = user.username ?? `${user.wallet_address.slice(0, 6)}…${user.wallet_address.slice(-4)}`;

  return (
    <div className="space-y-8">
      <div className="flex items-start gap-6">
        <div className="flex h-20 w-20 flex-shrink-0 items-center justify-center rounded-full bg-primary/10 text-2xl font-bold text-primary">
          {displayName.charAt(0).toUpperCase()}
        </div>
        <div>
          <h1 className="text-3xl font-bold">{displayName}</h1>
          {user.is_verified && (
            <span className="mt-1 inline-block rounded-full bg-primary/10 px-2 py-0.5 text-xs text-primary">Verified</span>
          )}
          {user.bio && <p className="mt-2 text-muted-foreground">{user.bio}</p>}
          <p className="mt-2 text-sm text-muted-foreground">Reputation: {user.reputation_score}</p>
          <p className="text-xs text-muted-foreground font-mono mt-1">{user.wallet_address}</p>
        </div>
      </div>

      <section>
        <h2 className="mb-4 text-xl font-semibold">Published Listings ({listings?.length ?? 0})</h2>
        {listings && listings.length > 0 ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {listings.map((l) => <ListingCard key={l.id} listing={l} />)}
          </div>
        ) : (
          <p className="text-muted-foreground">No published listings yet.</p>
        )}
      </section>
    </div>
  );
}
