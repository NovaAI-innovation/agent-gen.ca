"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import { Bot, Package, Server, Sparkles, Zap, Save, Send, X } from "lucide-react";
import { TYPE_META } from "@/components/marketplace/ListingCard";
import { EmptyState } from "@/components/ui/EmptyState";
import { Button } from "@/components/ui/Button";
import { Panel } from "@/components/ui/Panel";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { cn } from "@/lib/cn";

const TYPES = [
  { value: "mcp_server", icon: Server, label: "MCP Server", description: "Installable protocol package" },
  { value: "agent_skill", icon: Zap, label: "Agent Skill", description: "Reusable tool capability" },
  { value: "custom_agent", icon: Bot, label: "Custom Agent", description: "Full system personality" },
  { value: "pack", icon: Package, label: "Pack", description: "Curated listing bundle" },
] as const;

type ListingTypeValue = (typeof TYPES)[number]["value"];

interface ListingDraft {
  id: string;
  type: ListingTypeValue;
  title: string;
  description: string;
  long_description: string;
  price_sol: string;
  state: string;
  slug: string;
}

export default function NewStudioListingPage() {
  const router = useRouter();
  const { token } = useAuthStore();

  if (!token) {
    return (
      <EmptyState
        icon={Sparkles}
        title="Connect wallet to publish"
        description="Wallet connection is required to create listings."
      />
    );
  }

  // ---- wizard state ----
  const [step, setStep] = useState<1 | 2>(1);
  const [saving, setSaving] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | { code: string; field: string | null; message: string }[] | null>(null);
  const [draft, setDraft] = useState<ListingDraft | null>(null); // after initial save

  const [form, setForm] = useState({
    type: "mcp_server" as ListingTypeValue,
    title: "",
    description: "",
    long_description: "",
    price_sol: "0",
  });

  const set = (key: keyof typeof form, value: string) => setForm((prev) => ({ ...prev, [key]: value }));

  const selectedMeta = TYPE_META[form.type];

  // ---- save draft (step 2) ----
  const handleSaveDraft = async () => {
    setError(null);
    setSaving(true);
    try {
      if (draft) {
        // PATCH existing draft
        const res = await api.patch(`/studio/listings/${draft.id}`, {
          title: form.title,
          description: form.description || null,
          long_description: form.long_description || null,
          price_sol: parseFloat(form.price_sol) || 0,
        });
        setDraft({ ...draft, ...res.data });
      } else {
        // POST new draft
        const res = await api.post("/studio/listings", {
          type: form.type,
          title: form.title,
          description: form.description || null,
          long_description: form.long_description || null,
          price_sol: parseFloat(form.price_sol) || 0,
        });
        setDraft(res.data);
      }
    } catch (err: unknown) {
      const respData = (err as { response?: { data?: { detail?: string | unknown[] } } })?.response?.data?.detail;
      setError(typeof respData === "string" ? respData : (respData as any) ?? "Failed to save draft");
    } finally {
      setSaving(false);
    }
  };

  // ---- submit for review ----
  const handleSubmitForReview = async () => {
    if (!draft) return;
    // Save first, then submit
    setError(null);
    setSubmitting(true);
    try {
      if (form.title || form.description) {
        await api.patch(`/studio/listings/${draft.id}`, {
          title: form.title,
          description: form.description || null,
          long_description: form.long_description || null,
          price_sol: parseFloat(form.price_sol) || 0,
        });
      }
      await api.post(`/studio/listings/${draft.id}/submit`);
      router.push(`/studio/drafts?submitted=1`);
    } catch (err: unknown) {
      const respData = (err as { response?: { data?: { detail?: string | unknown[] } } })?.response?.data?.detail;
      setError(typeof respData === "string" ? respData : (respData as any) ?? "Failed to submit");
    } finally {
      setSubmitting(false);
    }
  };

  // ---- error display ----
  const renderErrors = () => {
    if (!error) return null;
    if (typeof error === "string") {
      return (
        <div className="rounded-lg border border-feedback-danger/35 bg-feedback-danger/10 px-4 py-2 text-sm text-red-200">
          {error}
        </div>
      );
    }
    return (
      <div className="space-y-1">
        {error.map((e, i) => (
          <div key={i} className="rounded-lg border border-feedback-danger/35 bg-feedback-danger/10 px-4 py-2 text-sm text-red-200">
            <span className="font-mono text-[11px] text-red-300">[{e.code}]</span> {e.message}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-5">
      {/* Step indicator */}
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
              {current === 1 ? "Type" : "Details"}
            </div>
          );
        })}
      </Panel>

      {/* Draft state badge */}
      {draft && (
        <Panel padding="sm" className="flex items-center gap-3">
          <StatusBadge status={draft.state === "pending_review" ? "pending" : "draft"} />
          <span className="font-mono text-xs text-text-muted">
            Draft saved · {draft.title}
          </span>
        </Panel>
      )}

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
                  <label className="mb-1.5 flex items-baseline justify-between text-sm font-medium text-text-primary">
                    Title <span className="text-feedback-danger">*</span>
                    <span className="text-xs text-text-muted">3–200 chars</span>
                  </label>
                  <input
                    value={form.title}
                    onChange={(event) => set("title", event.target.value)}
                    placeholder="e.g. secure-filesystem-mcp"
                    maxLength={200}
                    className="h-11 w-full rounded-xl border border-border-subtle bg-surface-muted px-4 text-sm text-text-primary outline-none transition-colors focus:border-border-focus"
                  />
                </div>

                <div>
                  <label className="mb-1.5 block text-sm font-medium text-text-secondary">
                    Short description <span className="text-xs text-text-muted">— max 2,000 chars, used in search</span>
                  </label>
                  <input
                    value={form.description}
                    onChange={(event) => set("description", event.target.value)}
                    placeholder="One sentence used in cards and search results"
                    maxLength={2000}
                    className="h-11 w-full rounded-xl border border-border-subtle bg-surface-muted px-4 text-sm text-text-primary outline-none transition-colors focus:border-border-focus"
                  />
                </div>

                <div>
                  <label className="mb-1.5 block text-sm font-medium text-text-secondary">
                    Full description <span className="text-xs text-text-muted">— max 50,000 chars, markdown supported</span>
                  </label>
                  <textarea
                    value={form.long_description}
                    onChange={(event) => set("long_description", event.target.value)}
                    rows={8}
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

              {renderErrors()}

              <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
                <div className="flex gap-2">
                  <Button variant="secondary" onClick={() => setStep(1)}>
                    Back
                  </Button>
                  {draft && (
                    <Button
                      variant="secondary"
                      onClick={async () => {
                        await handleSaveDraft();
                        router.push("/studio/drafts");
                      }}
                      disabled={saving || !form.title.trim()}
                    >
                      <Save className="h-4 w-4" />
                      Save &amp; close
                    </Button>
                  )}
                </div>

                <div className="flex gap-2">
                  <Button
                    variant="secondary"
                    onClick={handleSaveDraft}
                    disabled={saving || !form.title.trim()}
                  >
                    <Save className="h-4 w-4" />
                    {draft ? "Save draft" : "Create draft"}
                  </Button>
                  <Button
                    onClick={handleSubmitForReview}
                    disabled={submitting || !draft || !form.title.trim()}
                  >
                    <Send className="h-4 w-4" />
                    {submitting ? "Submitting…" : "Submit for review"}
                  </Button>
                </div>
              </div>
            </Panel>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}