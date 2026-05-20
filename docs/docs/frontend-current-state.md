# Frontend Current State (Inventory)

```yaml
snapshot:
  source_root: frontend/src
  captured_on: 2026-04-03
  stack:
    framework: Next.js App Router
    language: TypeScript
    data_fetching: "@tanstack/react-query + axios"
    auth: "Solana wallet signature -> JWT access token + refresh cookie"
```

## Route Surface

```yaml
app_routes:
  - path: /
    file: src/app/page.tsx
    purpose: "Landing page with category navigation and ecosystem highlights"
  - path: /marketplace
    file: src/app/marketplace/page.tsx
    purpose: "All listings discovery"
  - path: /marketplace/[slug]
    file: src/app/marketplace/[slug]/page.tsx
    purpose: "Listing detail, versions, reviews"
  - path: /publish
    file: src/app/publish/page.tsx
    purpose: "2-step listing creation flow"
  - path: /dashboard
    file: src/app/dashboard/page.tsx
    purpose: "Creator overview"
  - path: /dashboard/listings
    file: src/app/dashboard/listings/page.tsx
    purpose: "Creator listings"
  - path: /dashboard/earnings
    file: src/app/dashboard/earnings/page.tsx
    purpose: "Placeholder earnings view"
  - path: /dashboard/installs
    file: src/app/dashboard/installs/page.tsx
    purpose: "Placeholder install-history view"
  - path: /dashboard/saves
    file: src/app/dashboard/saves/page.tsx
    purpose: "Placeholder saved-listings view"
  - path: /u/[wallet]
    file: src/app/u/[wallet]/page.tsx
    purpose: "Public creator profile + listings"
  - path: /mcp-servers
    file: src/app/mcp-servers/page.tsx
    purpose: "Marketplace filtered to type=mcp_server"
  - path: /agent-skills
    file: src/app/agent-skills/page.tsx
    purpose: "Marketplace filtered to type=agent_skill"
  - path: /agents
    file: src/app/agents/page.tsx
    purpose: "Marketplace filtered to type=custom_agent"
  - path: /packs
    file: src/app/packs/page.tsx
    purpose: "Marketplace filtered to type=pack"
```

## Component Inventory

```yaml
layout_and_shell:
  - src/components/templates/AppShell.tsx
  - src/components/layout/Navbar.tsx
  - src/components/templates/MarketplaceTemplate.tsx
  - src/components/templates/DashboardTemplate.tsx
  - src/components/templates/ContentTemplate.tsx
  - src/components/system/PageHeader.tsx

marketplace_components:
  - src/components/marketplace/ListingGrid.tsx
  - src/components/marketplace/ListingFilters.tsx
  - src/components/marketplace/ListingCard.tsx
  - src/components/marketplace/MarketplaceHeader.tsx
  - src/components/marketplace/marketplaceConfig.ts

auth_wallet_state:
  - src/components/wallet/ConnectWalletButton.tsx
  - src/app/AuthSessionBootstrap.tsx
  - src/store/authStore.ts
  - src/lib/authToken.ts
  - src/lib/wallet/WalletProvider.tsx
  - src/lib/api.ts

ui_primitives:
  - src/components/ui/Button.tsx
  - src/components/ui/Panel.tsx
  - src/components/ui/EmptyState.tsx
```

## Frontend Data Contracts (Current API Usage)

```yaml
auth:
  - method: GET
    path: /auth/challenge
    used_by: ConnectWalletButton
    request:
      query:
        wallet: string
    expects:
      challenge_id: string
      nonce: string
      message: string
  - method: POST
    path: /auth/verify
    used_by: ConnectWalletButton
    request:
      body:
        wallet: string
        challenge_id: string
        nonce: string
        signature: base64
    expects:
      access_token: string
  - method: POST
    path: /auth/refresh
    used_by: api interceptor
    request:
      body:
        wallet: string
    expects:
      access_token: string
  - method: POST
    path: /auth/logout
    used_by: authStore.logout(remote=true)

users:
  - method: GET
    path: /users/me
    used_by:
      - authStore.fetchMe
      - dashboard/listings page
  - method: GET
    path: /users/{wallet}
    used_by: user profile page
  - method: GET
    path: /users/{wallet}/listings
    used_by:
      - user profile page
      - dashboard/listings page

listings:
  - method: GET
    path: /listings
    used_by: ListingGrid
    request:
      query:
        type: optional
        category: optional
        tag: optional
        q: optional
        sort: created_at|downloads|rating|price_asc|price_desc
        page: number
    expects:
      items: Listing[]
      total: number
      page: number
      page_size: number
  - method: POST
    path: /listings
    used_by: PublishWizard
    request:
      body:
        type: mcp_server|agent_skill|custom_agent|pack
        title: string
        description: string|null
        long_description: string|null
        price_sol: number
    expects:
      slug: string
  - method: GET
    path: /listings/{slug}
    used_by: ListingDetailClient
  - method: GET
    path: /listings/{slug}/versions
    used_by: ListingDetailClient
  - method: GET
    path: /listings/{slug}/reviews
    used_by: ListingDetailClient

marketplace_support:
  - method: GET
    path: /marketplace/categories
    used_by: ListingFilters
```

## Behavioral Notes

```yaml
session_bootstrap:
  behavior:
    - "On app load, if access token exists and user profile missing, call /users/me."
    - "On 401 from non-auth endpoint, attempt /auth/refresh once."
    - "If refresh fails, clear local token and emit auth:logout."

publish_flow:
  behavior:
    - "Requires connected wallet + existing JWT token."
    - "After successful POST /listings, redirects to /marketplace/{slug}."

dashboard_state:
  behavior:
    - "/dashboard/earnings, /dashboard/installs, /dashboard/saves are UI placeholders (no API calls yet)."
```

