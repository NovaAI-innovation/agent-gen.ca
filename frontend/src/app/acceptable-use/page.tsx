import type { Metadata } from "next";
import { AppShell } from "@/components/templates/AppShell";

export const metadata: Metadata = {
  title: "Acceptable Use Policy — agent-gen.ca",
  description: "Rules and prohibited activities on agent-gen.ca.",
};

export default function AcceptableUsePage() {
  return (
    <AppShell contentClassName="max-w-3xl">
      <article className="prose prose-invert prose-cyan max-w-none">
        <h1>Acceptable Use Policy</h1>
        <p className="lead text-text-secondary">
          Last updated: September 2026. This policy defines what you may and may not do on agent-gen.ca.
        </p>

        <h2>1. Purpose</h2>
        <p>
          agent-gen.ca is a marketplace for AI agents, agent skills, MCP servers, and related digital goods. This
          Acceptable Use Policy (&ldquo;AUP&rdquo;) exists to keep the platform safe, lawful, and useful for everyone.
        </p>

        <h2>2. Prohibited Content and Activities</h2>
        <p>The following are strictly prohibited on agent-gen.ca:</p>

        <h3>2.1 Illegal Content</h3>
        <p>
          Listings or activity that facilitates, promotes, or constitutes illegal activity under applicable law,
          including but not limited to: copyright infringement, fraud, money laundering, or the sale of illegal goods
          or services.
        </p>

        <h3>2.2 Malware and Harmful Software</h3>
        <p>
          Listings that contain viruses, trojans, ransomware, spyware, cryptominers, or any software designed to harm,
          exploit, or gain unauthorized access to systems or data.
        </p>

        <h3>2.3 Phishing and Social Engineering</h3>
        <p>
          Listings that impersonate legitimate services, harvest credentials, or deceive users into revealing
          sensitive information.
        </p>

        <h3>2.4 Intellectual Property Infringement</h3>
        <p>
          Listings that distribute content you do not have the right to sell or redistribute, including pirated
          software, leaked datasets, or stolen code.
        </p>

        <h3>2.5 Deceptive Listings</h3>
        <p>
          Listings with materially misleading descriptions, fake screenshots, inflated download or rating counts,
          or which do not deliver what they advertise.
        </p>

        <h3>2.6 Discrimination and Harassment</h3>
        <p>
          Content that promotes discrimination, harassment, or violence against individuals or groups based on
          protected characteristics.
        </p>

        <h3>2.7 Spam and Manipulation</h3>
        <p>
          Using the platform to distribute spam, artificially inflate ratings, submit fake reviews, or
          manipulate marketplace rankings.
        </p>

        <h3>2.8 NSFW Content</h3>
        <p>
          Listings containing sexually explicit, gratuitously violent, or otherwise adult-only content without
          appropriate age-gating or clear labeling.
        </p>

        <h2>3. Enforcement</h2>
        <p>
          Violations may result in removal of listings, suspension of creator accounts, and referral to law
          enforcement where required. We reserve the right to make enforcement decisions at our discretion.
        </p>

        <h2>4. Reporting Violations</h2>
        <p>
          If you encounter prohibited content or activity, use the Report button on the relevant listing or contact
          us through the GitHub repository. We review all reports promptly.
        </p>

        <h2>5. Changes</h2>
        <p>
          We may update this AUP at any time. The date at the top of this page indicates the last revision.
        </p>
      </article>
    </AppShell>
  );
}
