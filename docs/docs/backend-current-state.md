# Backend Current State (Inventory)

```yaml
snapshot:
  source_root: backend/app
  captured_on: 2026-04-03
  stack:
    framework: FastAPI
    orm: SQLAlchemy Async
    auth: "JWT access + JWT refresh cookie + wallet signature verification"
    database: PostgreSQL
```

## Application Composition

```yaml
entrypoint:
  file: app/main.py
  app_name: "agent-gen.ca API"
  version: "1.0.0"
  registered_routers:
    - auth
    - users
    - listings
    - reviews
    - marketplace
    - purchases
  middleware:
    cors:
      allow_credentials: true
      origins_from_env: ALLOWED_ORIGINS
  startup_behavior:
    - "Runs SQLAlchemy Base.metadata.create_all on startup lifespan."
```

## Router Inventory

```yaml
auth_router:
  prefix: /auth
  endpoints:
    - GET /challenge
    - POST /verify
    - POST /refresh
    - POST /logout
    - POST /logout-all

users_router:
  prefix: /users
  endpoints:
    - GET /me
    - PATCH /me
    - GET /{wallet}
    - GET /{wallet}/listings
    - POST /{wallet}/follow
    - DELETE /{wallet}/follow

listings_router:
  prefix: /listings
  endpoints:
    - GET /
    - POST /
    - GET /{slug}
    - PATCH /{slug}
    - DELETE /{slug}
    - GET /{slug}/versions
    - POST /{slug}/versions
    - POST /{slug}/save
    - DELETE /{slug}/save

reviews_router:
  prefix: /
  endpoints:
    - GET /listings/{slug}/reviews
    - POST /listings/{slug}/reviews
    - DELETE /reviews/{review_id}
    - POST /reviews/{review_id}/helpful

marketplace_router:
  prefix: /marketplace
  endpoints:
    - GET /featured
    - GET /trending
    - GET /categories
    - GET /search

purchases_router:
  prefix: /
  endpoints:
    - POST /purchases
    - POST /purchases/{purchase_id}/confirm
    - POST /tips
```

## Schema and Model Inventory

```yaml
schemas:
  listing:
    - ListingOut
    - ListingCreate
    - ListingUpdate
    - ListingVersionOut
    - ListingVersionCreate
    - TagOut
    - CategoryOut
  user:
    - Token
    - UserPublic
    - UserUpdate
  review:
    - ReviewOut
    - ReviewCreate
  purchase:
    - PurchaseOut
    - PurchaseCreate
    - PurchaseConfirm
    - TipCreate

orm_models:
  - User
  - Listing
  - ListingVersion
  - Category
  - Tag
  - Review
  - Purchase
  - Tip
  - AuthNonce
  - AuthSession
  - AuthAuditEvent
```

## Business/Data Layer

```yaml
crud_modules:
  listing:
    capabilities:
      - get_listings with filters (type/category/tag/q/sort/page/page_size)
      - get_listing_by_slug
      - create_listing
      - update_listing
      - create_listing_version
      - get_listing_versions
    noteworthy_behavior:
      - "list queries include only is_published=true"
      - "search uses PostgreSQL %% operator in title/description clause"
  user:
    capabilities:
      - get_user_by_wallet
      - get_user_by_id
      - upsert_user
      - update_user
```

## Auth and Session Mechanics

```yaml
wallet_auth_flow:
  - "GET /auth/challenge creates nonce + sign-in message."
  - "POST /auth/verify verifies ed25519 signature, issues access + refresh JWTs."
  - "Refresh token stored as HttpOnly cookie."
  - "Session persisted in auth_sessions with revocation and expiry."

token_claims:
  access: [sub, uid, sid, typ=access, iss, exp, iat]
  refresh: [sub, uid, sid, typ=refresh, iss, exp, iat, jti]

limits_and_controls:
  max_active_sessions_per_user: 3
  nonce_expiry_minutes: 5
  refresh_expiry_days: 30
```

## Operational Notes

```yaml
risks:
  - "README is stale and documents old auth/tasks endpoints not present in current code."
  - "Some router SQL statements depend on non-ORM tables (e.g., user_saves/user_follows) created only via migrations, not create_all."
```

