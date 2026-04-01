# agent-gen.ca C4 Architecture Diagrams

## 🏢 Level 1: System Context

```mermaid
C4Context
    title System Context diagram for agent-gen.ca AI Agent Marketplace

    Person(user, "User", "Creates, buys, sells AI agents")
    Person(admin, "Admin", "Moderates marketplace")
    
    System(agentGen, "agent-gen.ca", "AI Agent Marketplace Platform")
    System(stripe, "Stripe", "Payment Processing")
    System(wallet, "Web3 Wallet", "SIWE Authentication")
    
    Rel(user, agentGen, "Browses\nBuys\nSells agents", "HTTPS")
    Rel(admin, agentGen, "Moderates", "HTTPS")
    Rel(user, wallet, "Signs messages", "SIWE")
    Rel(user, stripe, "Pays", "Stripe Checkout")
    Rel(agentGen, stripe, "Processes payments", "API")
```

## 🗂️ Level 2: Containers

```mermaid
C4Container
    title Container diagram for agent-gen.ca

    Person(user, "User", "End user")
    Person_Ext(wallet, "Web3 Wallet", "SIWE auth provider")
    System_Ext(stripe, "Stripe", "Payments")
    
    System_Boundary(c1, "agent-gen.ca") {
        Container(browser, "Browser", "Web browser", "Chrome/Edge/Firefox")
        Container(frontend, "Next.js Frontend", "React SPA", "Next.js 15 + Tailwind + Shadcn")
        Container(backend, "FastAPI Backend", "REST API", "FastAPI + SQLAlchemy")
        ContainerDb(db, "PostgreSQL", "Relational DB", "PostgreSQL 16")
        Container(sse, "SSE Server", "Real-time updates", "FastAPI SSE endpoints")
    }
    
    Rel(user, browser, "Uses")
    Rel(browser, frontend, "Loads SPA", "HTTPS")
    Rel(browser, wallet, "SIWE signature", "WalletConnect")
    Rel(frontend, backend, "API calls", "HTTPS + JWT")
    Rel(backend, db, "CRUD", "JDBC")
    Rel(backend, sse, "Real-time", "SSE")
    Rel(browser, sse, "Market updates", "SSE")
    Rel(frontend, stripe, "Checkout", "Stripe.js")
    Rel(backend, stripe, "Webhooks", "HTTPS")
```

## 🧩 Level 3: Components (Frontend)

```mermaid
C4Component
    title Frontend Components

    Container(browser, "Browser")
    Container(frontend, "Next.js App") {
        Component(authStore, "Auth Store", "Zustand", "SIWE/JWT state")
        Component(userStore, "User Store", "Zustand", "Profile/cart")
        Component(marketStore, "Market Store", "Zustand", "Products/listings")
        Component(pages, "Pages", "Next.js RSC", "Dashboard/Marketplace/Profile")
        Component(ui, "Shadcn UI", "React", "Cyber neon theme")
        Component(api, "API Client", "Axios", "Backend calls")
    }
    
    Rel(browser, pages, "Renders")
    Rel(pages, ui, "Uses components")
    Rel(pages, authStore, "Auth context")
    Rel(pages, userStore, "User data")
    Rel(pages, marketStore, "Market data")
    Rel(pages, api, "API calls")
```

## 🧩 Level 3: Components (Backend)

```mermaid
C4Component
    title Backend Components

    Container(backend, "FastAPI Backend") {
        Component(auth, "Auth Router", "FastAPI", "SIWE verification")
        Component(market, "Market Router", "FastAPI", "Products/Guides")
        Component(user, "User Router", "FastAPI", "Profile management")
        Component(dbSession, "DB Session", "SQLAlchemy", "Async sessions")
        Component(jwt, "JWT Handler", "python-jose", "Token ops")
        Component(crud, "CRUD", "SQLAlchemy", "Repo pattern")
    }
    
    Rel(auth, jwt, "Uses")
    Rel(market, dbSession, "Queries")
    Rel(user, dbSession, "Queries")
    Rel(market, crud, "Uses")
    Rel(user, crud, "Uses")
```

## 🗄️ Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    USERS ||--o{ PRODUCTS : creates
    USERS ||--o{ GUIDES : creates
    USERS ||--o{ ORDERS : places
    PRODUCTS ||--o{ REVIEWS : reviewed_by
    
    USERS {
        int id PK
        varchar wallet_address UK
        varchar username
        text avatar_url
        timestamp created_at
    }
    
    PRODUCTS {
        int id PK
        int user_id FK
        varchar name
        text description
        jsonb config_json
        decimal price
        text image_url
        timestamp created_at
    }
    
    GUIDES {
        int id PK
        int user_id FK
        varchar title
        text content
        timestamp created_at
    }
```

## 🔄 SIWE Authentication Flow (Detailed)

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant W as Wallet
    participant FE as Next.js Frontend
    participant BE as FastAPI Backend
    participant DB as PostgreSQL
    
    U->>B: Connect Wallet
    B->>FE: useAuthStore.connect()
    FE->>W: siwe.prepareMessage({nonce, domain})
    W->>FE: signature
    FE->>BE: POST /auth/siwe {message, signature}
    BE->>BE: verifySignature(message, signature, wallet)
    alt Valid
        BE->>DB: UPSERT users SET wallet_address, username
        DB-->>BE: user_id
        BE->>BE: createJWT(user_id)
        BE-->>FE: {token, user}
        FE->>localStorage: store token
        FE->>authStore: setUser(user)
    else Invalid
        BE-->>FE: 401 Unauthorized
    end
```

## 🛒 Marketplace Purchase Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant BE as Backend
    participant Stripe
    participant DB as Database
    
    U->>FE: Click Buy
    FE->>BE: POST /products/{id}/purchase
    BE->>DB: Check product ownership
    BE->>Stripe: Create Checkout Session
    Stripe-->>BE: session_url
    BE-->>FE: {url}
    FE->>Stripe: Redirect to checkout
    Stripe-->>U: Payment success → webhook
    Stripe->>BE: Webhook payment_intent.succeeded
    BE->>DB: Create order + transfer ownership
    BE-->>Stripe: 200 OK
    BE->>SSE: Notify seller/buyer
```

## 📈 Deployment Architecture

```mermaid
flowchart TD
    GitHub[GitHub] --> CI[GitHub Actions]
    CI --> Docker[Build Docker]
    Docker --> Registry[Docker Hub]
    
    Registry --> Vercel[Vercel Frontend]
    Registry --> Railway[Railway Backend/DB]
    
    User[Users] --> CDN[Cloudflare CDN]
    CDN --> Vercel
    
    Vercel -.->|API Calls| Railway
    Railway --> Postgres[Postgres]
```

**Legend:**
- **Green**: Production containers
- **Blue**: External services
- **Yellow**: Infrastructure/CDN

**Files saved:** ARCHITECTURE.md + DIAGRAMS.md

**Status:** ✅ Planning complete, ready for delegation