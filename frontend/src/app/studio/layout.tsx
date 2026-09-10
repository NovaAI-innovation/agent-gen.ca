import type { ReactNode } from "react";
import { AppShell } from "@/components/templates/AppShell";
import { StudioSidebar } from "./StudioSidebar";

export const metadata = { title: "Creator Studio - agent-gen.ca" };

interface StudioLayoutProps {
  children: ReactNode;
}

export default function StudioLayout({ children }: StudioLayoutProps) {
  return (
    <AppShell contentClassName="mx-auto w-full max-w-7xl px-4 pb-16 pt-28 sm:px-6 sm:pt-32">
      <div className="grid gap-5 lg:grid-cols-[260px_minmax(0,1fr)]">
        <StudioSidebar />
        <section className="min-w-0">{children}</section>
      </div>
    </AppShell>
  );
}