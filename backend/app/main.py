from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, dashboard, sync, gamification
from app.core.database import AsyncSessionLocal
from app.services.badge_engine import seed_badges

app = FastAPI(title="DevPulse API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(sync.router, prefix="/api/v1/sync", tags=["sync"])
app.include_router(gamification.router, prefix="/api/v1/gamification", tags=["gamification"])

@app.on_event("startup")
async def startup_event():
    async with AsyncSessionLocal() as db:
        await seed_badges(db)

@app.get("/health")
async def health():
    return {"status": "ok"}