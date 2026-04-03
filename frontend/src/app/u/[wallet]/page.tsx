import { Navbar } from "@/components/layout/Navbar";
import { UserProfileClient } from "./UserProfileClient";

export default async function UserProfilePage({
  params,
}: {
  params: Promise<{ wallet: string }>;
}) {
  const { wallet } = await params;
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10 sm:px-6">
        <UserProfileClient wallet={wallet} />
      </main>
    </div>
  );
}
