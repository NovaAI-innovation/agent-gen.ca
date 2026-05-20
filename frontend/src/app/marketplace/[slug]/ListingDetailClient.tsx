"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useConnection, useWallet } from "@solana/wallet-adapter-react";
import { Download, Star } from "lucide-react";
import { motion } from "framer-motion";
import { TYPE_META, type Listing } from "@/components/marketplace/ListingCard";
import { Panel } from "@/components/ui/Panel";
import { Button } from "@/components/ui/Button";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import { sendSolPayment } from "@/lib/solana/sendPayment";

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

interface PurchaseOut {
  id: string;
  status: string;
  seller_wallet_address: string | null;
  amount_lamports: number | null;
}

type PurchaseState = "idle" | "initiating" | "sending" | "confirming" | "done" | "error";

export function ListingDetailClient({ slug }: { slug: string }) {
  const { connection } = useConnection();
  const wallet = useWallet();
  const { token } = useAuthStore();

  const [purchaseState, setPurchaseState] = useState<PurchaseState>("idle");
  const [purchaseError, setPurchaseError] = useState<string | null>(null);

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

  const handleAction = async () => {
    if (!listing) return;
    setPurchaseError(null);

    if (!token) {
      setPurchaseError("Connect your wallet to continue.");
      return;
    }

    const isFree = parseFloat(listing.price_sol) === 0;

    try {
      // Step 1: Initiate purchase on backend.
      setPurchaseState("initiating");
      const { data: purchase } = await api.post<PurchaseOut>(
        `/listings/${listing.slug}/purchase`
      );

      if (isFree || purchase.status === "confirmed") {
        // Free listing — backend confirmed it immediately.
        setPurchaseState("done");
        return;
      }

      // Step 2: Send SOL on-chain.
      const sellerWallet = purchase.seller_wallet_address;
      const lamports = purchase.amount_lamports;

      if (!sellerWallet || !lamports) {
        throw new Error("Missing payment details from server");
      }

      if (!wallet.connected || !wallet.publicKey) {
        throw new Error("Wallet disconnected before payment");
      }

      setPurchaseState("sending");
      const txSignature = await sendSolPayment(connection, wallet, sellerWallet, lamports);

      // Step 3: Submit signature to backend for on-chain verification.
      setPurchaseState("confirming");
      await api.post(`/purchases/${purchase.id}/confirm`, { tx_signature: txSignature });

      setPurchaseState("done");
    } catch (err: unknown) {
      setPurchaseState("error");
      if (err instanceof Error) {
        setPurchaseError(err.message);
      } else {
        setPurchaseError("Something went wrong. Please try again.");
      }
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="skeleton h-24 rounded-2xl" />
        <div className="skeleton h-56 rounded-2xl" />
        <div className="skeleton h-44 rounded-2xl" />
      </div>
    );
  }

  if (!listing) {
    return <p className="py-10 text-sm text-text-secondary">Listing not found.</p>;
  }

  const meta = TYPE_META[listing.type];
  const latest = versions?.find((version) => version.is_latest);
  const isFree = parseFloat(listing.price_sol) === 0;

  const actionLabel = (() => {
    if (purchaseState === "initiating") return "Preparing…";
    if (purchaseState === "sending") return "Approve in wallet…";
    if (purchaseState === "confirming") return "Confirming…";
    if (purchaseState === "done") return isFree ? "Installed" : "Purchased";
    return isFree ? "Install" : "Purchase";
  })();

  const isActionDisabled =
    purchaseState === "initiating" ||
    purchaseState === "sending" ||
    purchaseState === "confirming" ||
    purchaseState === "done";

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.28 }} className="space-y-6">
      <Panel padding="lg">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
          <div className="min-w-0">
            <div className="mb-3 inline-flex items-center gap-2 rounded-lg border border-border-subtle bg-surface-muted px-3 py-1.5 text-xs">
              <meta.icon className={`h-3.5 w-3.5 ${meta.colorClass}`} />
              <span className="text-text-secondary">{meta.label}</span>
            </div>

            <h1 className="font-display text-4xl font-bold tracking-tight text-text-primary">{listing.title}</h1>
            <p className="mt-3 max-w-2xl text-text-secondary">{listing.description ?? "No short description provided."}</p>

            <div className="mt-4 flex flex-wrap items-center gap-4 text-sm text-text-secondary">
              <span className="inline-flex items-center gap-1.5">
                <Download className="h-4 w-4" />
                {listing.download_count.toLocaleString()} installs
              </span>
              {listing.avg_rating ? (
                <span className="inline-flex items-center gap-1.5">
                  <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
                  {parseFloat(listing.avg_rating).toFixed(1)} rating
                </span>
              ) : null}
              {latest ? <span className="font-mono text-xs text-text-muted">v{latest.version}</span> : null}
            </div>
          </div>

          <Panel tone="muted" padding="md" className="min-w-56">
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">Price</p>
            <p className={`mt-1 font-mono text-2xl font-semibold ${meta.colorClass}`}>
              {isFree ? "Free" : `SOL ${parseFloat(listing.price_sol).toFixed(3)}`}
            </p>
            <Button
              className="mt-4 w-full"
              onClick={handleAction}
              disabled={isActionDisabled}
            >
              {actionLabel}
            </Button>
            {purchaseError ? (
              <p className="mt-2 text-xs text-red-400">{purchaseError}</p>
            ) : null}
            {purchaseState === "done" ? (
              <p className="mt-2 text-xs text-green-400">
                {isFree ? "Successfully installed!" : "Payment confirmed on-chain."}
              </p>
            ) : null}
          </Panel>
        </div>

        {listing.tags.length > 0 ? (
          <div className="mt-6 flex flex-wrap gap-2">
            {listing.tags.map((tag) => (
              <span key={tag.id} className="rounded-lg border border-border-subtle bg-surface-muted px-2.5 py-1 text-xs text-text-secondary">
                #{tag.name}
              </span>
            ))}
          </div>
        ) : null}
      </Panel>

      {latest?.install_instructions ? (
        <Panel padding="lg">
          <h2 className="font-display text-2xl font-bold text-text-primary">Installation</h2>
          <pre className="mt-4 overflow-x-auto rounded-xl border border-border-subtle bg-surface-muted p-5 font-mono text-xs leading-relaxed text-text-secondary whitespace-pre-wrap">
            {latest.install_instructions}
          </pre>
        </Panel>
      ) : null}

      {versions && versions.length > 0 ? (
        <Panel padding="lg">
          <h2 className="font-display text-2xl font-bold text-text-primary">Version timeline</h2>
          <div className="mt-4 space-y-2.5">
            {versions.map((version) => (
              <div key={version.id} className="flex items-start justify-between gap-4 rounded-xl border border-border-subtle bg-surface-muted px-4 py-3">
                <div>
                  <p className="font-mono text-sm text-text-primary">v{version.version}</p>
                  <p className="mt-1 text-xs text-text-secondary">{version.changelog ?? "No changelog message."}</p>
                </div>
                <div className="text-right">
                  {version.is_latest ? (
                    <span className="rounded-md border border-action-primary/30 bg-action-primary/10 px-2 py-0.5 font-mono text-[10px] uppercase tracking-[0.14em] text-action-primary">
                      latest
                    </span>
                  ) : null}
                  <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.14em] text-text-muted">
                    {new Date(version.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Panel>
      ) : null}

      <Panel padding="lg">
        <h2 className="font-display text-2xl font-bold text-text-primary">Reviews ({reviews?.length ?? 0})</h2>

        {reviews && reviews.length > 0 ? (
          <div className="mt-4 space-y-3">
            {reviews.map((review) => (
              <article key={review.id} className="rounded-xl border border-border-subtle bg-surface-muted px-4 py-3">
                <div className="flex items-center justify-between">
                  <div className="flex gap-0.5">
                    {Array.from({ length: 5 }).map((_, index) => (
                      <Star
                        key={index}
                        className={`h-3.5 w-3.5 ${index < review.rating ? "fill-amber-400 text-amber-400" : "text-text-muted"}`}
                      />
                    ))}
                  </div>
                  <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-text-muted">
                    {new Date(review.created_at).toLocaleDateString()}
                  </span>
                </div>
                {review.title ? <p className="mt-2 text-sm font-semibold text-text-primary">{review.title}</p> : null}
                {review.body ? <p className="mt-1 text-sm text-text-secondary">{review.body}</p> : null}
              </article>
            ))}
          </div>
        ) : (
          <p className="mt-4 rounded-xl border border-border-subtle bg-surface-muted px-4 py-8 text-center text-sm text-text-secondary">
            No reviews yet. Be the first to leave one.
          </p>
        )}
      </Panel>
    </motion.div>
  );
}
