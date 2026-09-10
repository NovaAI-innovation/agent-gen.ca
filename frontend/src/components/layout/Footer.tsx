import Link from "next/link";

const FOOTER_LINKS = [
  {
    label: "Legal",
    links: [
      { href: "/terms", label: "Terms of Service" },
      { href: "/privacy", label: "Privacy Policy" },
      { href: "/acceptable-use", label: "Acceptable Use Policy" },
      { href: "/security", label: "Security Policy" },
    ],
  },
  {
    label: "Marketplace",
    links: [
      { href: "/marketplace", label: "Browse All" },
      { href: "/marketplace?type=mcp_server", label: "MCP Servers" },
      { href: "/marketplace?type=agent_skill", label: "Agent Skills" },
      { href: "/marketplace?type=custom_agent", label: "Custom Agents" },
    ],
  },
  {
    label: "Creators",
    links: [
      { href: "/studio", label: "Creator Studio" },
      { href: "/studio/releases", label: "Release Management" },
      { href: "/studio/analytics", label: "Analytics" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="border-t border-border-subtle bg-surface-base/80 backdrop-blur-sm">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          {FOOTER_LINKS.map((group) => (
            <div key={group.label}>
              <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-text-muted">
                {group.label}
              </h3>
              <ul className="space-y-2">
                {group.links.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-sm text-text-secondary transition-colors hover:text-text-primary"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          <div>
            <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-text-muted">
              Project
            </h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="https://github.com/your-org/agent-gen"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-text-secondary transition-colors hover:text-text-primary"
                >
                  GitHub
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/your-org/agent-gen/issues"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-text-secondary transition-colors hover:text-text-primary"
                >
                  Report an Issue
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-10 flex flex-col items-center justify-between gap-4 border-t border-border-subtle pt-8 sm:flex-row">
          <p className="text-sm text-text-muted">
            &copy; {new Date().getFullYear()} agent-gen.ca &mdash; AI Agent Marketplace on Solana
          </p>
          <p className="text-xs text-text-muted">
            All transactions on Solana. Built with FastAPI &amp; Next.js.
          </p>
        </div>
      </div>
    </footer>
  );
}
