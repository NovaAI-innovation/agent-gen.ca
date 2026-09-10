"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  FileText,
  Layers,
  LayoutDashboard,
  Settings,
  Sparkles,
  Eye,
} from "lucide-react";
import { cn } from "@/lib/cn";

const STUDIO_LINKS = [
  { href: "/studio", icon: LayoutDashboard, label: "Overview" },
  { href: "/studio/drafts", icon: FileText, label: "Drafts" },
  { href: "/studio/listings", icon: Layers, label: "Published" },
  { href: "/studio/releases", icon: Eye, label: "Releases" },
  { href: "/studio/analytics", icon: BarChart3, label: "Analytics" },
  { href: "/studio/settings", icon: Settings, label: "Settings" },
];

export function StudioSidebar() {
  const pathname = usePathname();

  return (
    <aside className="space-y-3">
      <div className="rounded-2xl border border-border-subtle bg-surface-elevated/80 p-4">
        <div className="mb-3 flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-action-primary" />
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-text-muted">
            Creator Studio
          </p>
        </div>

        <nav className="grid gap-1.5 sm:grid-cols-2 lg:grid-cols-1">
          {STUDIO_LINKS.map(({ href, icon: Icon, label }) => {
            // Only the exact studio root should be active for "/studio",
            // otherwise use prefix matching for nested routes.
            const active =
              href === "/studio"
                ? pathname === "/studio"
                : pathname.startsWith(href);

            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-2 rounded-xl border px-3 py-2 text-sm transition-all duration-200",
                  active
                    ? "border-action-primary/45 bg-action-primary/12 text-action-primary"
                    : "border-border-subtle bg-surface-muted/45 text-text-secondary hover:border-border-strong hover:bg-surface-muted hover:text-text-primary",
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