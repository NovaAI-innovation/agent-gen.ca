import type { ReactNode } from "react";
import { AppShell } from "@/components/templates/AppShell";
import { DashboardSidebar } from "@/app/dashboard/DashboardSidebar";

interface DashboardTemplateProps {
  children: ReactNode;
}

export function DashboardTemplate({ children }: DashboardTemplateProps) {
  return (
    <AppShell contentClassName="mx-auto w-full max-w-7xl px-4 pb-16 pt-28 sm:px-6 sm:pt-32">
      <div className="grid gap-5 lg:grid-cols-[260px_minmax(0,1fr)]">
        <DashboardSidebar />
        <section className="min-w-0">{children}</section>
      </div>
    </AppShell>
  );
}
