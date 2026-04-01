from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

import app.db.database as db

app = FastAPI(title="Agent-Gen.ca API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with db.engine.begin() as conn:
        await conn.run_sync(db.Base.metadata.create_all)

@app.get("/")
def read_root():
    return {"message": "Agent-Gen.ca Marketplace API v1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

from app.routers import auth, agents, marketplace
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(agents.router, prefix="/agents", tags=["agents"])
app.include_router(marketplace.router, prefix="/marketplace", tags=["marketplace"])
