# SAAS Task Manager Backend (FastAPI)

## Quick Start

```bash
# Clone & cd
cd backend

# Install deps
pip install -e .

# Start postgres (docker-compose up db)
docker-compose up db

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Docs
http://localhost:8000/docs

## Test Auth
```bash
# Register
curl -X POST "http://localhost:8000/auth/register" -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"testpass123"}'

# Login
curl -X POST "http://localhost:8000/auth/login" -H "Content-Type: application/x-www-form-urlencoded" -d "username=test@example.com&password=testpass123"
```

## Test Tasks
```bash
curl -X POST "http://localhost:8000/tasks/" -H "Content-Type: application/json" -d '{"title":"Test Task","description":"Test desc"}'

curl "http://localhost:8000/tasks/?status=todo"
```
