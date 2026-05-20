"use client";

import { useAuthStore } from "@/store/authStore";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Download, Package, Sparkles, Star, Wallet } from "lucide-react";
import { PageHeader } from "@/components/system/PageHeader";
import { Panel } from "@/components/ui/Panel";

export default function DashboardPage() {
  const { user, token } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!token) router.push("/");
  }, [token, router]);

  if (!user) {
    return (
      <div className="space-y-4">
        <div className="skeleton h-24 rounded-2xl" />
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="skeleton h-32 rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  const displayName = user.username ?? `${user.wallet_address.slice(0, 6)}...${user.wallet_address.slice(-4)}`;

  const metrics = [
    { label: "Reputation", value: String(user.reputation_score), icon: Star, accent: "text-amber-300" },
    { label: "Total installs", value: "-", icon: Download, accent: "text-cyan-300" },
    { label: "Listings", value: "-", icon: Package, accent: "text-violet-300" },
  ];

  return (
    <div className="space-y-5">
      <PageHeader
        icon={Sparkles}
        eyebrow="Creator"
        title={`${displayName} dashboard`}
        subtitle="Monitor listing performance, manage catalog health, and track trust signals in one place."
        accentClassName="text-action-primary"
        stats={[
          { label: "Wallet", value: `${user.wallet_address.slice(0, 6)}...${user.wallet_address.slice(-4)}` },
          { label: "Verified", value: user.is_verified ? "Yes" : "No" },
        ]}
      />

      <Panel padding="md" className="flex items-center gap-2 text-sm text-text-secondary">
        <Wallet className="h-4 w-4 text-action-primary" />
        Connected wallet: <span className="font-mono text-text-primary">{user.wallet_address}</span>
      </Panel>

      <section className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {metrics.map(({ label, value, icon: Icon, accent }) => (
          <Panel key={label} padding="md">
            <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-lg border border-border-subtle bg-surface-muted">
              <Icon className={`h-4 w-4 ${accent}`} />
            </div>
            <p className="font-mono text-2xl font-semibold text-text-primary">{value}</p>
            <p className="mt-1 text-xs uppercase tracking-[0.16em] text-text-muted">{label}</p>
          </Panel>
        ))}
      </section>
    </div>
  );
}
