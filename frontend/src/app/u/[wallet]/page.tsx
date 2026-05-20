import { AppShell } from "@/components/templates/AppShell";
import { UserProfileClient } from "./UserProfileClient";

export default async function UserProfilePage({
  params,
}: {
  params: Promise<{ wallet: string }>;
}) {
  const { wallet } = await params;

  return (
    <AppShell contentClassName="mx-auto w-full max-w-6xl px-4 pb-16 pt-28 sm:px-6 sm:pt-32">
      <UserProfileClient wallet={wallet} />
    </AppShell>
  );
}
