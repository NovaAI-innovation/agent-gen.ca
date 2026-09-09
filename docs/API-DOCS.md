# API Docs

> This document covers the v2 API surface. Release B endpoints are marked accordingly and are not available until the Release B gate passes.

## Base URLs

- Local backend: `http://localhost:8000`
- Production API: `https://api.agent-gen.ca`

## Health

- `GET /health` — liveness check

## Authentication (Identity context)

### Get challenge

`GET /auth/challenge?wallet=<base58_pubkey>`

Response includes:
- `challenge_id`
- `nonce`
- `domain`
- `uri`
- `chain_id`
- `issued_at`
- `expires_at`
- `message`

### Verify signature

`POST /auth/verify`

```json
{
  "wallet": "<base58_pubkey>",
  "challenge_id": "<uuid>",
  "nonce": "<nonce>",
  "signature": "<base64_signature>"
}
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "wallet_address": "<base58_pubkey>",
  "session_id": "<uuid>",
  "expires_at": "2026-04-03T00:00:00Z"
}
```

### Refresh

`POST /auth/refresh` — requires refresh cookie.

### Session management

- `POST /auth/logout` — revoke current session
- `POST /auth/logout-all` — revoke all sessions
- `GET /auth/sessions` — list active sessions

## Creator onboarding (Identity context)

- `POST /creators/apply` — submit creator profile (handle, display name, bio, support link, terms, payout address)
- `GET /creators/me` — get own creator profile
- `PATCH /creators/me` — update creator profile

> Only approved creators can create drafts.

## Catalog (Catalog context)

- `GET /listings` — search and filter public listings
- `GET /listings/{slug}` — get listing detail with trust signals
- `GET /listings/{slug}/versions` — list release versions
- `GET /listings/{slug}/reviews` — list verified reviews

## Publishing (Publishing context)

Requires approved creator status.

- `POST /studio/listings` — create a new draft
- `PATCH /studio/listings/{id}` — update draft (autosave)
- `POST /studio/listings/{id}/preview` — generate preview
- `POST /studio/listings/{id}/submit` — submit for moderation review
- `DELETE /studio/listings/{id}` — delete draft

## Studio (Catalog + Publishing context)

- `GET /studio/overview` — creator dashboard summary
- `GET /studio/listings` — list creator's drafts and published listings
- `GET /studio/listings/{id}` — get draft detail
- `GET /studio/analytics` — install and revenue analytics

## Artifacts (Artifacts context)

- `POST /artifacts/upload-url` — request a short-lived signed upload URL
- `POST /artifacts` — register uploaded artifact with manifest
- `GET /artifacts/{id}/status` — check scan status

## Releases (Artifacts context)

- `POST /studio/listings/{id}/releases` — create a new release
- `GET /studio/listings/{id}/releases` — list releases for a listing
- `GET /releases/{id}` — get release detail with scan result

## Downloads and library (Entitlements context)

- `POST /acquire/{listing_slug}` — acquire a free listing
- `GET /library` — list acquired entitlements
- `GET /library/{listing_id}` — get entitlement detail with download URL
- `POST /library/{listing_id}/download` — request a short-lived download URL
- `POST /library/{listing_id}/install-event` — record an install event

## Reviews (Entitlements context)

- `POST /listings/{slug}/reviews` — submit a verified review (requires entitlement)
- `PATCH /reviews/{id}` — update own review
- `DELETE /reviews/{id}` — delete own review

## Reports (Reports context)

- `POST /reports` — submit an abuse report
- `GET /reports/{id}` — check report status

## Moderation (Moderation context)

Requires operator role.

- `GET /admin/moderation/queue` — list pending moderation items
- `POST /admin/moderation/{id}/approve` — approve with reason
- `POST /admin/moderation/{id}/reject` — reject with reason
- `POST /admin/moderation/{id}/suspend` — suspend with reason
- `POST /admin/moderation/{id}/restore` — restore from suspension
- `GET /admin/moderation/audit` — list moderation audit events

## Payments (Release B — Payments context)

- `POST /payments/intents` — create a payment intent
- `GET /payments/intents/{id}` — get intent status
- `POST /payments/intents/{id}/submit` — submit transaction signature
- `GET /payments/receipts/{id}` — get payment receipt

## Operations (Operations context)

Requires operator role.

- `GET /health/ready` — readiness check (database, Redis, workers)
- `GET /admin/health` — dependency health detail
- `GET /admin/metrics` — operational metrics
- `GET /admin/audit-log` — system audit log

## Public metrics

- `GET /metrics/public` — time-bounded public metrics (approved creators, published listings, successful installs)
