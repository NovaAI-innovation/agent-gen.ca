"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import { Server, Zap, Bot, Package, ArrowRight, ArrowLeft } from "lucide-react";
import { TYPE_META } from "@/components/marketplace/ListingCard";

const TYPES = [
  { value: "mcp_server",  icon: Server,  label: "MCP Server",    desc: "Installable Model Context Protocol package" },
  { value: "agent_skill", icon: Zap,     label: "Agent Skill",   desc: "Reusable tool or skill for AI agents" },
  { value: "custom_agent",icon: Bot,     label: "Custom Agent",  desc: "Full agent config, prompts & tool chain" },
  { value: "pack",        icon: Package, label: "Pack",          desc: "Curated bundle of marketplace items" },
] as const;

type ListingTypeValue = (typeof TYPES)[number]["value"];

export function PublishWizard() {
  const router = useRouter();
  const { token } = useAuthStore();
  const [step, setStep] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const [form, setForm] = useState({
    type: "mcp_server" as ListingTypeValue,
    title: "",
    description: "",
    long_description: "",
    price_sol: "0",
  });

  const set = (key: keyof typeof form, value: string) =>
    setForm((f) => ({ ...f, [key]: value }));

  if (!token) {
    return (
      <div className="rounded-2xl border border-border bg-muted/30 p-12 text-center">
        <div
          className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full"
          style={{ background: "hsl(var(--primary) / 0.1)" }}
        >
          <span className="font-mono text-xl" style={{ color: "hsl(var(--primary))" }}>◎</span>
        </div>
        <h3 className="text-lg font-semibold">Connect your wallet first</h3>
        <p className="mt-1 text-sm text-muted-foreground">
          Connect your Phantom wallet to publish a listing on agent-gen.ca
        </p>
      </div>
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
    } catch (e: unknown) {
      const msg =
        (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Failed to create listing";
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const selectedMeta = TYPE_META[form.type];

  return (
    <div className="space-y-8">
      {/* Progress bar */}
      <div className="flex gap-2">
        {[1, 2].map((s) => (
          <motion.div
            key={s}
            className="h-1 flex-1 rounded-full"
            style={{
              background: s <= step ? "hsl(var(--primary))" : "hsl(var(--border))",
            }}
            animate={{ background: s <= step ? "hsl(var(--primary))" : "hsl(var(--border))" }}
          />
        ))}
      </div>

      <AnimatePresence mode="wait">
        {step === 1 && (
          <motion.div
            key="step1"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.25 }}
            className="space-y-6"
          >
            <div>
              <h2 className="text-xl font-semibold">Choose a listing type</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                What are you publishing to the marketplace?
              </p>
            </div>

            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {TYPES.map(({ value, icon: Icon, label, desc }) => {
                const meta = TYPE_META[value];
                const active = form.type === value;
                return (
                  <button
                    key={value}
                    onClick={() => set("type", value)}
                    className="flex items-start gap-4 rounded-2xl border p-5 text-left transition-all duration-200"
                    style={{
                      background: active ? meta.bg : "transparent",
                      borderColor: active ? meta.border : "hsl(var(--border))",
                    }}
                  >
                    <div
                      className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl"
                      style={{ background: meta.bg }}
                    >
                      <Icon className="h-4 w-4" style={{ color: meta.color }} />
                    </div>
                    <div>
                      <p className="font-medium" style={{ color: active ? meta.color : undefined }}>
                        {label}
                      </p>
                      <p className="mt-0.5 text-xs text-muted-foreground">{desc}</p>
                    </div>
                  </button>
                );
              })}
            </div>

            <button
              onClick={() => setStep(2)}
              className="flex w-full items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold transition-all duration-200 hover:opacity-90"
              style={{
                background: "hsl(var(--primary))",
                color: "hsl(var(--primary-foreground))",
                boxShadow: "0 0 20px hsl(var(--primary) / 0.3)",
              }}
            >
              Continue <ArrowRight className="h-4 w-4" />
            </button>
          </motion.div>
        )}

        {step === 2 && (
          <motion.div
            key="step2"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.25 }}
            className="space-y-5"
          >
            <div className="flex items-center gap-3">
              <div
                className="flex h-8 w-8 items-center justify-center rounded-lg"
                style={{ background: selectedMeta.bg }}
              >
                <selectedMeta.icon className="h-4 w-4" style={{ color: selectedMeta.color }} />
              </div>
              <h2 className="text-xl font-semibold">Listing details</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="mb-1.5 block text-sm font-medium">
                  Title <span className="text-destructive">*</span>
                </label>
                <input
                  value={form.title}
                  onChange={(e) => set("title", e.target.value)}
                  placeholder="e.g. Filesystem MCP Server"
                  className="h-11 w-full rounded-xl border border-border bg-muted px-4 text-sm outline-none transition-colors focus:border-primary/50"
                />
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-medium text-muted-foreground">
                  Short description
                </label>
                <input
                  value={form.description}
                  onChange={(e) => set("description", e.target.value)}
                  placeholder="One sentence shown in listing cards"
                  className="h-11 w-full rounded-xl border border-border bg-muted px-4 text-sm outline-none transition-colors focus:border-primary/50"
                />
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-medium text-muted-foreground">
                  Full description
                </label>
                <textarea
                  value={form.long_description}
                  onChange={(e) => set("long_description", e.target.value)}
                  rows={5}
                  placeholder="Detailed description, usage guide, examples..."
                  className="w-full rounded-xl border border-border bg-muted px-4 py-3 text-sm outline-none transition-colors focus:border-primary/50 resize-none"
                />
              </div>

              <div>
                <label className="mb-1.5 block text-sm font-medium text-muted-foreground">
                  Price (SOL) — set to 0 for free
                </label>
                <div className="relative">
                  <span
                    className="absolute left-4 top-1/2 -translate-y-1/2 font-mono text-sm"
                    style={{ color: "hsl(var(--primary))" }}
                  >
                    ◎
                  </span>
                  <input
                    type="number"
                    min="0"
                    step="0.001"
                    value={form.price_sol}
                    onChange={(e) => set("price_sol", e.target.value)}
                    className="h-11 w-full rounded-xl border border-border bg-muted pl-9 pr-4 font-mono text-sm outline-none transition-colors focus:border-primary/50"
                  />
                </div>
              </div>
            </div>

            {error && (
              <p className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-2 text-sm text-destructive">
                {error}
              </p>
            )}

            <div className="flex gap-3">
              <button
                onClick={() => setStep(1)}
                className="flex items-center gap-1.5 rounded-xl border border-border bg-muted px-5 py-3 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              >
                <ArrowLeft className="h-4 w-4" /> Back
              </button>
              <button
                onClick={handleSubmit}
                disabled={!form.title || submitting}
                className="flex flex-1 items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold transition-all duration-200 hover:opacity-90 disabled:opacity-40"
                style={{
                  background: "hsl(var(--primary))",
                  color: "hsl(var(--primary-foreground))",
                  boxShadow: "0 0 20px hsl(var(--primary) / 0.3)",
                }}
              >
                {submitting ? "Publishing…" : "Publish Listing"}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
