import { Navbar } from "@/components/layout/Navbar";
import { ListingDetailClient } from "./ListingDetailClient";

export default async function ListingDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10 sm:px-6">
        <ListingDetailClient slug={slug} />
      </main>
    </div>
  );
}
