# API Docs

## Base URLs
1. Local backend: `http://localhost:8000`
2. Production API (example): `https://api.agent-gen.ca`

## Health
1. `GET /health`

## Authentication (Solana wallet)

### Get challenge
1. `GET /auth/challenge?wallet=<base58_pubkey>`
2. Response includes:
   1. `challenge_id`
   2. `nonce`
   3. `domain`
   4. `uri`
   5. `chain_id`
   6. `issued_at`
   7. `expires_at`
   8. `message`

### Verify signature
1. `POST /auth/verify`
2. Body:
```json
{
  "wallet": "<base58_pubkey>",
  "challenge_id": "<uuid>",
  "nonce": "<nonce>",
  "signature": "<base64_signature>"
}
```
3. Response:
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
1. `POST /auth/refresh`
2. Body:
```json
{
  "wallet": "<base58_pubkey>"
}
```
3. Requires refresh cookie.

### Logout
1. `POST /auth/logout`
2. `POST /auth/logout-all`

## Marketplace and listing APIs
1. `GET /listings`
2. `POST /listings`
3. `GET /listings/{slug}`
4. `PATCH /listings/{slug}`
5. `DELETE /listings/{slug}`
6. `GET /listings/{slug}/versions`
7. `POST /listings/{slug}/versions`
8. `GET /listings/{slug}/reviews`
9. `POST /listings/{slug}/reviews`

## User APIs
1. `GET /users/me`
2. `PATCH /users/me`
3. `GET /users/{wallet}`
4. `GET /users/{wallet}/listings`
5. `POST /users/{wallet}/follow`
6. `DELETE /users/{wallet}/follow`

## Purchase APIs (current)
1. `POST /purchases`
2. `POST /purchases/{purchase_id}/confirm`
3. `POST /tips`

Note: Sprint 1 adds schema support for server-verified intents and on-chain transaction tracking. Intent-driven purchase APIs are added in Sprint 2.
