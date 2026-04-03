from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.db.database as db

app = FastAPI(title="agent-gen.ca API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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
    return {"message": "agent-gen.ca Marketplace API v1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


from app.routers import auth, marketplace, listings, reviews, purchases, users

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(listings.router)
app.include_router(reviews.router)
app.include_router(marketplace.router)
app.include_router(purchases.router)
