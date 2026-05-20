"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { DollarSign, History, LayoutDashboard, List, Bookmark, Sparkles } from "lucide-react";
import { cn } from "@/lib/cn";

const LINKS = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Overview" },
  { href: "/dashboard/listings", icon: List, label: "Listings" },
  { href: "/dashboard/earnings", icon: DollarSign, label: "Earnings" },
  { href: "/dashboard/saves", icon: Bookmark, label: "Saved" },
  { href: "/dashboard/installs", icon: History, label: "Installs" },
];

export function DashboardSidebar() {
  const pathname = usePathname();

  return (
    <aside className="space-y-3">
      <div className="rounded-2xl border border-border-subtle bg-surface-elevated/80 p-4">
        <div className="mb-3 flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-action-primary" />
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-text-muted">Creator Console</p>
        </div>

        <nav className="grid gap-1.5 sm:grid-cols-2 lg:grid-cols-1">
          {LINKS.map(({ href, icon: Icon, label }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-2 rounded-xl border px-3 py-2 text-sm transition-all duration-200",
                  active
                    ? "border-action-primary/45 bg-action-primary/12 text-action-primary"
                    : "border-border-subtle bg-surface-muted/45 text-text-secondary hover:border-border-strong hover:bg-surface-muted hover:text-text-primary"
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
