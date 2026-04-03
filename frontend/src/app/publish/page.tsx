import { Navbar } from "@/components/layout/Navbar";
import { PublishWizard } from "./PublishWizard";

export const metadata = { title: "Publish — agent-gen.ca" };

export default function PublishPage() {
  return (
    <div className="flex min-h-screen flex-col tech-grid">
      <Navbar />
      <main className="mx-auto w-full max-w-xl flex-1 px-4 pt-28 pb-16 sm:px-6">
        <div className="mb-8">
          <p className="mb-1 font-mono text-xs uppercase tracking-widest text-muted-foreground">
            Contribute
          </p>
          <h1 className="text-3xl font-bold">Publish a listing</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Share your work with the community. Earn SOL when others use it.
          </p>
        </div>
        <PublishWizard />
      </main>
    </div>
  );
}
