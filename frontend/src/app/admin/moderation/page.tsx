"use client";

import { useAuthStore } from "@/store/authStore";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Shield,
  CheckCircle2,
  XCircle,
  Ban,
  RotateCcw,
  Eye,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/system/PageHeader";
import { Panel } from "@/components/ui/Panel";
import { Button } from "@/components/ui/Button";
import { StatusBadge, type StatusBadgeProps } from "@/components/ui/StatusBadge";
import { cn } from "@/lib/cn";

type QueueItem = {
  id: string;
  title: string;
  slug: string;
  type: string;
  state: string;
  owner_wallet: string | null;
  created_at: string;
};

type AuditEntry = {
  id: string;
  from_state: string;
  to_state: string;
  reason: string | null;
  actor_id: string | null;
  created_at: string;
};

export default function ModerationPage() {
  const { user, token } = useAuthStore();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) router.push("/");
  }, [token, router]);

  const isMod = user?.is_verified;

  const { data: queue, isLoading } = useQuery({
    queryKey: ["mod-queue"],
    queryFn: async () =>
      (await api.get("/admin/moderation/queue", { params: { scope: "listings", page_size: 50 } })).data as {
        items: QueueItem[];
        total: number;
      },
    enabled: !!isMod,
  });

  const { data: audit } = useQuery({
    queryKey: ["mod-audit", expandedId],
    queryFn: async () =>
      (await api.get(`/admin/moderation/listings/${expandedId}/audit`)).data as AuditEntry[],
    enabled: !!expandedId && !!isMod,
  });

  const actionMutation = useMutation({
    mutationFn: async ({ listingId, action, reason }: { listingId: string; action: string; reason?: string }) => {
      await api.post(`/admin/moderation/listings/${listingId}/${action}`, null, {
        params: reason ? { reason } : undefined,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mod-queue"] });
      setActionError(null);
    },
    onError: (err: any) => {
      setActionError(err?.response?.data?.detail ?? "Action failed");
    },
  });

  if (!isMod) {
    return (
      <div className="space-y-5 pt-28">
        <PageHeader
          icon={Shield}
          eyebrow="Admin"
          title="Moderation"
          subtitle="You need a verified account to access moderation tools."
          accentClassName="text-feedback-danger"
        />
      </div>
    );
  }

  return (
    <div className="space-y-5 pt-28 sm:pt-32 max-w-5xl mx-auto px-4 sm:px-6 pb-16">
      <PageHeader
        icon={Shield}
        eyebrow="Admin"
        title="Moderation queue"
        subtitle="Review pending listings submitted by creators."
        accentClassName="text-violet-300"
        stats={[
          { label: "Pending", value: String(queue?.total ?? 0) },
        ]}
      />

      {actionError && (
        <div className="rounded-lg border border-feedback-danger/35 bg-feedback-danger/10 px-4 py-3 text-sm text-red-200">
          {actionError}
        </div>
      )}

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="skeleton h-20 rounded-2xl" />
          ))}
        </div>
      ) : queue && queue.items.length > 0 ? (
        <div className="space-y-3">
          {queue.items.map((item) => {
            const isExpanded = expandedId === item.id;
            const typeLabel = item.type.replace(/_/g, " ");

            return (
              <Panel key={item.id} padding="none" className="overflow-hidden">
                <button
                  type="button"
                  onClick={() => setExpandedId(isExpanded ? null : item.id)}
                  className="flex w-full items-center justify-between px-5 py-4 text-left hover:bg-surface-muted/40 transition-colors"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-3">
                      <StatusBadge status={(item.state === "pending_review" ? "pending" : item.state) as StatusBadgeProps["status"]} />
                      <p className="truncate font-medium text-text-primary">{item.title}</p>
                    </div>
                    <p className="mt-1 text-xs text-text-muted">
                      {typeLabel} · owner {item.owner_wallet?.slice(0, 6)}…{item.owner_wallet?.slice(-4)} · submitted{" "}
                      {new Date(item.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  {isExpanded ? (
                    <ChevronUp className="h-4 w-4 text-text-muted shrink-0" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-text-muted shrink-0" />
                  )}
                </button>

                {isExpanded && (
                  <div className="border-t border-border-subtle px-5 py-4 space-y-4">
                    <div className="flex flex-wrap gap-2">
                      <Button
                        size="sm"
                        onClick={() =>
                          actionMutation.mutate({ listingId: item.id, action: "approve" })
                        }
                        disabled={actionMutation.isPending}
                      >
                        <CheckCircle2 className="h-3.5 w-3.5" />
                        Approve
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => {
                          const reason = prompt("Rejection reason (required):");
                          if (reason) actionMutation.mutate({ listingId: item.id, action: "reject", reason });
                        }}
                        disabled={actionMutation.isPending}
                      >
                        <XCircle className="h-3.5 w-3.5" />
                        Reject
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => {
                          const reason = prompt("Suspension reason (required):");
                          if (reason) actionMutation.mutate({ listingId: item.id, action: "suspend", reason });
                        }}
                        disabled={actionMutation.isPending}
                      >
                        <Ban className="h-3.5 w-3.5" />
                        Suspend
                      </Button>
                    </div>

                    {/* Audit trail */}
                    <div>
                      <p className="text-xs font-mono uppercase tracking-[0.16em] text-text-muted mb-2">
                        Audit trail
                      </p>
                      {audit ? (
                        audit.length > 0 ? (
                          <div className="space-y-2">
                            {audit.map((e) => (
                              <div
                                key={e.id}
                                className="flex items-center justify-between rounded-lg border border-border-subtle bg-surface-muted/60 px-3 py-2 text-xs"
                              >
                                <div className="flex items-center gap-2 text-text-secondary">
                                  <span className="font-mono text-text-muted">{e.from_state}</span>
                                  <span className="text-action-primary">→</span>
                                  <span className="font-mono font-medium text-text-primary">{e.to_state}</span>
                                  {e.reason && (
                                    <span className="text-text-muted">— {e.reason}</span>
                                  )}
                                </div>
                                <span className="font-mono text-text-muted shrink-0">
                                  {new Date(e.created_at).toLocaleString()}
                                </span>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-xs text-text-muted">No audit events yet.</p>
                        )
                      ) : (
                        <div className="skeleton h-10 rounded-lg" />
                      )}
                    </div>
                  </div>
                )}
              </Panel>
            );
          })}
        </div>
      ) : (
        <Panel padding="lg">
          <div className="flex flex-col items-center gap-3 py-6">
            <Shield className="h-8 w-8 text-feedback-success" />
            <p className="text-sm font-medium text-text-primary">Queue is clear</p>
            <p className="text-xs text-text-muted">No listings pending review right now.</p>
          </div>
        </Panel>
      )}
    </div>
  );
}