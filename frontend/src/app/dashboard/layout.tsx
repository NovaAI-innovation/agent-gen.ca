import { DashboardTemplate } from "@/components/templates/DashboardTemplate";

export const metadata = { title: "Dashboard - agent-gen.ca" };

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <DashboardTemplate>{children}</DashboardTemplate>;
}
