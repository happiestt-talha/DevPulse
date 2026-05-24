from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.workers.sync_github import sync_github_for_user

router = APIRouter()

@router.post("/trigger")
async def trigger_sync(request: Request, db: AsyncSession = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401)
    token = auth_header.split(" ")[1]
    from app.core.auth import decode_token
    payload = decode_token(token)
    user_id = payload["sub"]
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one()
    sync_github_for_user.delay(str(user.id), user.github_token, user.github_username)
    return {"status": "sync queued"}

@router.get("/status")
async def sync_status(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = await get_current_user_id(request, db)  # reuse logic
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one()
    return {
        "github_last_sync": user.last_synced_at.isoformat() if user.last_synced_at else None,
        "wakatime_last_sync": None,
        "leetcode_last_sync": None,
    }