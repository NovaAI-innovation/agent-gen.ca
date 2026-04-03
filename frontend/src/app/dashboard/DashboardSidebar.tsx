"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, List, DollarSign, Bookmark, History } from "lucide-react";

const LINKS = [
  { href: "/dashboard",          icon: LayoutDashboard, label: "Overview" },
  { href: "/dashboard/listings", icon: List,            label: "My Listings" },
  { href: "/dashboard/earnings", icon: DollarSign,      label: "Earnings" },
  { href: "/dashboard/saves",    icon: Bookmark,        label: "Saved" },
  { href: "/dashboard/installs", icon: History,         label: "Installs" },
];

export function DashboardSidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-48 flex-shrink-0 md:block">
      <nav className="space-y-0.5">
        {LINKS.map(({ href, icon: Icon, label }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-150"
              style={
                active
                  ? {
                      background: "hsl(var(--primary) / 0.1)",
                      color: "hsl(var(--primary))",
                    }
                  : {
                      color: "hsl(var(--muted-foreground))",
                    }
              }
            >
              <Icon className="h-4 w-4 flex-shrink-0" />
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
