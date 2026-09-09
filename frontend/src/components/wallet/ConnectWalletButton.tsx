"use client";

import { useState } from "react";
import { useAuthStore } from "@/store/authStore";
import { SignInDialog } from "@/features/auth/SignInDialog";
import { SessionMenu } from "@/features/auth/SessionMenu";
import { Button } from "@/components/ui/Button";

export function ConnectWalletButton() {
  const { token } = useAuthStore();
  const [dialogOpen, setDialogOpen] = useState(false);

  const isSignedIn = !!token;

  if (isSignedIn) {
    return <SessionMenu />;
  }

  return (
    <>
      <Button
        variant="secondary"
        size="sm"
        onClick={() => setDialogOpen(true)}
        className="min-w-[130px]"
      >
        Connect Wallet
      </Button>

      <SignInDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
      />
    </>
  );
}