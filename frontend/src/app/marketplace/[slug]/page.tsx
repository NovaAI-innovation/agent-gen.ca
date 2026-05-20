import { AppShell } from "@/components/templates/AppShell";
import { ListingDetailClient } from "./ListingDetailClient";

export default async function ListingDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;

  return (
    <AppShell contentClassName="mx-auto w-full max-w-5xl px-4 pb-16 pt-28 sm:px-6 sm:pt-32">
      <ListingDetailClient slug={slug} />
    </AppShell>
  );
}
