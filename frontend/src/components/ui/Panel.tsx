import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/cn";

const panelVariants = cva(
  "rounded-2xl border border-border-subtle bg-surface-elevated/80 backdrop-blur-md",
  {
    variants: {
      tone: {
        default: "",
        accent: "border-border-focus bg-surface-accent/40",
        muted: "bg-surface-muted/70",
      },
      padding: {
        none: "",
        sm: "p-4",
        md: "p-5 sm:p-6",
        lg: "p-6 sm:p-7",
      },
    },
    defaultVariants: {
      tone: "default",
      padding: "md",
    },
  }
);

interface PanelProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof panelVariants> {}

export function Panel({ className, tone, padding, ...props }: PanelProps) {
  return <div className={cn(panelVariants({ tone, padding, className }))} {...props} />;
}
