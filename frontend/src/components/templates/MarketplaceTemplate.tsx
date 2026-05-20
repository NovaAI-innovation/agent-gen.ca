import type { ReactNode } from "react";
import { AppShell } from "@/components/templates/AppShell";
import { PageHeader, type PageHeaderConfig } from "@/components/system/PageHeader";

interface MarketplaceTemplateProps {
  header: PageHeaderConfig;
  children: ReactNode;
}

export function MarketplaceTemplate({ header, children }: MarketplaceTemplateProps) {
  return (
    <AppShell>
      <PageHeader {...header} className="mb-8" />
      {children}
    </AppShell>
  );
}
