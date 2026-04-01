# Agent-Gen.ca API Documentation

## 🏠 Base URL
```
http://localhost:8000
https://api.agent-gen.ca (production)
```

## 🔐 Authentication (SIWE + JWT)

### 1. SIWE Verify
**POST** `/auth/siwe/verify`

```bash
curl -X POST "http://localhost:8000/auth/siwe/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "agent-gen.ca wants you to sign in with your Ethereum account:\n...",
    "signature": "0x..."
  }'
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Usage
All subsequent requests use `Authorization: Bearer <access_token>`

## ✅ Health Check
**GET** `/health`
```bash
curl http://localhost:8000/health
```
**Response:** `{"status": "healthy"}`

## 🤖 Agents API

### List Agents
**GET** `/agents/`
```bash
curl -H "Authorization: Bearer eyJ..." http://localhost:8000/agents/
```

### Create Agent
**POST** `/agents/`
```bash
curl -X POST -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  http://localhost:8000/agents/ \
  -d '{"name": "MyAgent", "description": "..."}'
```

## 🛒 Marketplace API

### Browse Marketplace
**GET** `/marketplace/`
```bash
curl -H "Authorization: Bearer eyJ..." http://localhost:8000/marketplace/
```

## 📦 Postman Collection

Save as `agent-gen.ca.postman_collection.json`:

```json
{
  "info": {
    "name": "Agent-Gen.ca API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    },
    {
      "key": "access_token",
      "value": "eyJ..."
    }
  ],
  "item": [
    {
      "name": "Health",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/health",
          "host": ["{{base_url}}"],
          "path": ["health"]
        }
      }
    },
    {
      "name": "SIWE Verify",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"message\": \"agent-gen.ca wants you to sign in...\",\n  \"signature\": \"0x...\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/auth/siwe/verify",
          "host": ["{{base_url}}"],
          "path": ["auth", "siwe", "verify"]
        }
      }
    },
    {
      "name": "List Agents",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{access_token}}"
          }
        ],
        "url": {
          "raw": "{{base_url}}/agents/",
          "host": ["{{base_url}}"],
          "path": ["agents", ""]
        }
      }
    }
  ]
}
```

## 🛠 OpenAPI Spec
Available at `/docs` (Swagger UI) and `/openapi.json`

---
**Reference:** [FastAPI Docs](https://fastapi.tiangolo.com/)