import type { ReactNode } from "react";
import { cn } from "@/lib/cn";
import { Footer } from "@/components/layout/Footer";
import { Navbar } from "@/components/layout/Navbar";

interface AppShellProps {
  children: ReactNode;
  mainClassName?: string;
  contentClassName?: string;
  showNav?: boolean;
}

export function AppShell({ children, mainClassName, contentClassName, showNav = true }: AppShellProps) {
  return (
    <div className={cn("app-shell min-h-screen", mainClassName)}>
      <div className="pointer-events-none fixed inset-0 -z-20 bg-app-gradient" aria-hidden="true" />
      <div className="pointer-events-none fixed inset-0 -z-10 bg-tech-grid opacity-70" aria-hidden="true" />
      <div className="pointer-events-none fixed inset-0 -z-10 bg-noise-mask" aria-hidden="true" />

      {showNav ? <Navbar /> : null}
      <main className={cn("mx-auto w-full max-w-7xl px-4 pt-28 sm:px-6 sm:pt-32", contentClassName)}>{children}</main>
      <Footer />
    </div>
  );
}
