"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import { Bot, Package, Server, Sparkles, Zap } from "lucide-react";
import { TYPE_META } from "@/components/marketplace/ListingCard";
import { EmptyState } from "@/components/ui/EmptyState";
import { Button } from "@/components/ui/Button";
import { Panel } from "@/components/ui/Panel";
import { cn } from "@/lib/cn";

const TYPES = [
  { value: "mcp_server", icon: Server, label: "MCP Server", description: "Installable protocol package" },
  { value: "agent_skill", icon: Zap, label: "Agent Skill", description: "Reusable tool capability" },
  { value: "custom_agent", icon: Bot, label: "Custom Agent", description: "Full system personality" },
  { value: "pack", icon: Package, label: "Pack", description: "Curated listing bundle" },
] as const;

type ListingTypeValue = (typeof TYPES)[number]["value"];

export function PublishWizard() {
  const router = useRouter();
  const { token } = useAuthStore();

  const [step, setStep] = useState<1 | 2>(1);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const [form, setForm] = useState({
    type: "mcp_server" as ListingTypeValue,
    title: "",
    description: "",
    long_description: "",
    price_sol: "0",
  });

  const set = (key: keyof typeof form, value: string) => setForm((prev) => ({ ...prev, [key]: value }));

  if (!token) {
    return (
      <EmptyState
        icon={Sparkles}
        title="Connect wallet to publish"
        description="Wallet connection is required to verify ownership and create listings."
      />
    );
  }

  const handleSubmit = async () => {
    setError(null);
    setSubmitting(true);

    try {
      const res = await api.post("/listings", {
        type: form.type,
        title: form.title,
        description: form.description || null,
        long_description: form.long_description || null,
        price_sol: parseFloat(form.price_sol) || 0,
      });
      router.push(`/marketplace/${res.data.slug}`);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Failed to publish listing";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  const selectedMeta = TYPE_META[form.type];

  return (
    <div className="space-y-5">
      <Panel padding="sm" className="grid grid-cols-2 gap-2">
        {[1, 2].map((current) => {
          const active = current <= step;
          return (
            <div
              key={current}
              className={cn(
                "rounded-lg border px-3 py-2 text-center font-mono text-xs uppercase tracking-[0.16em]",
                active
                  ? "border-action-primary/40 bg-action-primary/10 text-action-primary"
                  : "border-border-subtle bg-surface-muted text-text-muted"
              )}
            >
              Step {current}
            </div>
          );
        })}
      </Panel>

      <AnimatePresence mode="wait">
        {step === 1 ? (
          <motion.div key="step-1" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}>
            <Panel padding="lg">
              <h2 className="font-display text-2xl font-bold text-text-primary">Choose listing type</h2>
              <p className="mt-1 text-sm text-text-secondary">Pick the container that matches what you are publishing.</p>

              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                {TYPES.map(({ value, icon: Icon, label, description }) => {
                  const active = form.type === value;
                  const meta = TYPE_META[value];

                  return (
                    <button
                      key={value}
                      type="button"
                      onClick={() => set("type", value)}
                      className={cn(
                        "rounded-xl border p-4 text-left transition-all duration-200",
                        active
                          ? "border-border-focus bg-surface-hover"
                          : "border-border-subtle bg-surface-muted/70 hover:border-border-strong"
                      )}
                    >
                      <div className="mb-2 flex h-9 w-9 items-center justify-center rounded-lg border border-border-subtle bg-surface-elevated">
                        <Icon className={cn("h-4 w-4", meta.colorClass)} />
                      </div>
                      <p className="font-semibold text-text-primary">{label}</p>
                      <p className="mt-1 text-sm text-text-secondary">{description}</p>
                    </button>
                  );
                })}
              </div>

              <div className="mt-5 flex justify-end">
                <Button onClick={() => setStep(2)}>
                  Continue
                </Button>
              </div>
            </Panel>
          </motion.div>
        ) : (
          <motion.div key="step-2" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}>
            <Panel padding="lg">
              <div className="mb-4 flex items-center gap-2">
                <selectedMeta.icon className={cn("h-5 w-5", selectedMeta.colorClass)} />
                <h2 className="font-display text-2xl font-bold text-text-primary">Listing details</h2>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="mb-1.5 block text-sm font-medium text-text-primary">
                    Title <span className="text-feedback-danger">*</span>
                  </label>
                  <input
                    value={form.title}
                    onChange={(event) => set("title", event.target.value)}
                    placeholder="e.g. secure-filesystem-mcp"
                    className="h-11 w-full rounded-xl border border-border-subtle bg-surface-muted px-4 text-sm text-text-primary outline-none transition-colors focus:border-border-focus"
                  />
                </div>

                <div>
                  <label className="mb-1.5 block text-sm font-medium text-text-secondary">Short description</label>
                  <input
                    value={form.description}
                    onChange={(event) => set("description", event.target.value)}
                    placeholder="One sentence used in cards and search results"
                    className="h-11 w-full rounded-xl border border-border-subtle bg-surface-muted px-4 text-sm text-text-primary outline-none transition-colors focus:border-border-focus"
                  />
                </div>

                <div>
                  <label className="mb-1.5 block text-sm font-medium text-text-secondary">Full description</label>
                  <textarea
                    value={form.long_description}
                    onChange={(event) => set("long_description", event.target.value)}
                    rows={6}
                    placeholder="Use this space for docs, usage, and integration notes"
                    className="w-full rounded-xl border border-border-subtle bg-surface-muted px-4 py-3 text-sm text-text-primary outline-none transition-colors focus:border-border-focus"
                  />
                </div>

                <div>
                  <label className="mb-1.5 block text-sm font-medium text-text-secondary">Price (SOL)</label>
                  <input
                    type="number"
                    min="0"
                    step="0.001"
                    value={form.price_sol}
                    onChange={(event) => set("price_sol", event.target.value)}
                    className="h-11 w-full rounded-xl border border-border-subtle bg-surface-muted px-4 font-mono text-sm text-text-primary outline-none transition-colors focus:border-border-focus"
                  />
                </div>
              </div>

              {error ? (
                <p className="mt-4 rounded-lg border border-feedback-danger/35 bg-feedback-danger/10 px-4 py-2 text-sm text-red-200">{error}</p>
              ) : null}

              <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
                <Button variant="secondary" onClick={() => setStep(1)}>
                  Back
                </Button>
                <Button onClick={handleSubmit} disabled={!form.title.trim() || submitting}>
                  {submitting ? "Publishing..." : "Publish listing"}
                </Button>
              </div>
            </Panel>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
