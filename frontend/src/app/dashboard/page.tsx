"use client";

import { useAuthStore } from "@/store/authStore";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Star, Download, Package, Wallet } from "lucide-react";

export default function DashboardPage() {
  const { user, token } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!token) router.push("/");
  }, [token, router]);

  if (!user) {
    return (
      <div className="space-y-4">
        <div className="skeleton h-10 w-48 rounded-xl" />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {[1, 2, 3].map((i) => <div key={i} className="skeleton h-28 rounded-2xl" />)}
        </div>
      </div>
    );
  }

  const displayName =
    user.username ??
    `${user.wallet_address.slice(0, 6)}…${user.wallet_address.slice(-4)}`;

  const STATS = [
    { icon: Star,     label: "Reputation",  value: user.reputation_score, color: "hsl(var(--accent-skill))" },
    { icon: Download, label: "Total Installs", value: "—",               color: "hsl(var(--accent-mcp))" },
    { icon: Package,  label: "Listings",    value: "—",                  color: "hsl(var(--accent-pack))" },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="space-y-8"
    >
      {/* Profile header */}
      <div className="flex items-center gap-4">
        <div
          className="flex h-14 w-14 items-center justify-center rounded-2xl font-bold text-xl"
          style={{
            background: "hsl(var(--primary) / 0.1)",
            color: "hsl(var(--primary))",
            border: "1px solid hsl(var(--primary) / 0.2)",
          }}
        >
          {displayName.charAt(0).toUpperCase()}
        </div>
        <div>
          <h1 className="text-2xl font-bold">{displayName}</h1>
          <p className="mt-0.5 flex items-center gap-1.5 font-mono text-xs text-muted-foreground">
            <Wallet className="h-3 w-3" />
            {user.wallet_address}
          </p>
        </div>
        {user.is_verified && (
          <span
            className="ml-auto rounded-full px-3 py-1 text-xs font-medium"
            style={{ background: "hsl(var(--primary) / 0.1)", color: "hsl(var(--primary))" }}
          >
            Verified
          </span>
        )}
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {STATS.map(({ icon: Icon, label, value, color }, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08, duration: 0.35 }}
            className="rounded-2xl border border-border bg-card p-5"
          >
            <div
              className="mb-3 flex h-8 w-8 items-center justify-center rounded-lg"
              style={{ background: `color-mix(in srgb, ${color} 15%, transparent)` }}
            >
              <Icon className="h-4 w-4" style={{ color }} />
            </div>
            <div className="font-mono text-2xl font-bold">{value}</div>
            <div className="mt-0.5 text-xs uppercase tracking-wider text-muted-foreground">
              {label}
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
