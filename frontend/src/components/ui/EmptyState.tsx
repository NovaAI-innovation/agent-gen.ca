import type { ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import { Panel } from "@/components/ui/Panel";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: ReactNode;
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <Panel className="text-center" tone="muted" padding="lg">
      <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl border border-border-subtle bg-surface-muted">
        <Icon className="h-5 w-5 text-text-muted" />
      </div>
      <h3 className="text-lg font-semibold text-text-primary">{title}</h3>
      <p className="mx-auto mt-1 max-w-lg text-sm text-text-secondary">{description}</p>
      {action ? <div className="mt-5 flex items-center justify-center">{action}</div> : null}
    </Panel>
  );
}
