import type { ReactNode } from "react";
import { AppShell } from "@/components/templates/AppShell";
import { PageHeader, type PageHeaderConfig } from "@/components/system/PageHeader";

interface ContentTemplateProps {
  header?: PageHeaderConfig;
  children: ReactNode;
  maxWidthClassName?: string;
}

export function ContentTemplate({ header, children, maxWidthClassName = "max-w-5xl" }: ContentTemplateProps) {
  return (
    <AppShell contentClassName={`mx-auto w-full ${maxWidthClassName} px-4 pb-16 pt-28 sm:px-6 sm:pt-32`}>
      {header ? <PageHeader {...header} className="mb-8" /> : null}
      {children}
    </AppShell>
  );
}
