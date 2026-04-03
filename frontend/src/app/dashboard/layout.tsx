import { Navbar } from "@/components/layout/Navbar";
import { DashboardSidebar } from "./DashboardSidebar";

export const metadata = { title: "Dashboard — agent-gen.ca" };

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col tech-grid">
      <Navbar />
      <div className="mx-auto flex w-full max-w-6xl flex-1 gap-8 px-4 pt-28 pb-16 sm:px-6">
        <DashboardSidebar />
        <main className="min-w-0 flex-1">{children}</main>
      </div>
    </div>
  );
}
