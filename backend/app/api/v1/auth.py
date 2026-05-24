from fastapi import APIRouter, HTTPException, Request, Response, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.config import settings
from app.core.auth import create_access_token, create_refresh_token
from app.core.encryption import encrypt_token
from app.models.user import User
from app.integrations.leetcode_client import LeetCodeClient
from app.workers.sync_wakatime import sync_wakatime_for_user
from app.workers.sync_leetcode import sync_leetcode_for_user
from app.api.v1.dashboard import get_current_user_id

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

@router.get("/github")
async def github_login():
    return {
        "authorization_url": f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&redirect_uri={settings.GITHUB_REDIRECT_URI}&scope=read:user,repo,read:org"
    }

from fastapi.responses import RedirectResponse

@router.get("/github/callback")
async def github_callback(code: str, response: Response, db: AsyncSession = Depends(get_db)):
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GITHUB_REDIRECT_URI,
            },
        )
        token_data = token_resp.json()
        if "error" in token_data:
            raise HTTPException(status_code=400, detail=token_data["error_description"])
        access_token = token_data["access_token"]

    # Fetch GitHub user info
    async with httpx.AsyncClient() as client:
        user_resp = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        gh_user = user_resp.json()

    # Check existing user
    stmt = select(User).where(User.github_id == gh_user["id"])
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            github_id=gh_user["id"],
            github_username=gh_user["login"],
            github_token=encrypt_token(access_token),
            email=gh_user.get("email"),
            avatar_url=gh_user.get("avatar_url"),
            display_name=gh_user.get("name"),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        user.github_token = encrypt_token(access_token)
        user.github_username = gh_user["login"]
        user.email = gh_user.get("email") or user.email
        user.avatar_url = gh_user.get("avatar_url") or user.avatar_url
        user.display_name = gh_user.get("name") or user.display_name
        await db.commit()

    # Issue JWT
    access_jwt = create_access_token(str(user.id))
    refresh_jwt = create_refresh_token(str(user.id))

    # Trigger initial GitHub sync
    from app.workers.sync_github import sync_github_for_user
    sync_github_for_user.delay(str(user.id), user.github_token, user.github_username)

    # Redirect to frontend callback page with the JWT
    frontend_url = f"http://localhost:3000/auth/callback?access_token={access_jwt}"
    redirect_response = RedirectResponse(url=frontend_url, status_code=302)
    redirect_response.set_cookie(
        key="refresh_token",
        value=refresh_jwt,
        httponly=True,
        secure=False,   # set True in production with HTTPS
        samesite="lax",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )
    return redirect_response

@router.get("/wakatime/authorize")
async def wakatime_authorize():
    """Return the WakaTime OAuth authorization URL."""
    return {
        "authorization_url": f"https://wakatime.com/oauth/authorize?client_id={settings.WAKATIME_CLIENT_ID}&redirect_uri={settings.WAKATIME_REDIRECT_URI}&response_type=code&scope=email,read_stats,read_logged_time"
    }

@router.get("/wakatime/callback")
async def wakatime_callback(code: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Handle WakaTime OAuth callback — exchange code for token and redirect to frontend."""
    # For this callback to work, the user must already be logged in (JWT in cookie or we need
    # to pass state). For simplicity, we'll redirect to the frontend with the code so it can
    # call the /wakatime/connect endpoint with auth.
    frontend_url = f"http://localhost:3000/auth/wakatime-callback?code={code}"
    return RedirectResponse(url=frontend_url, status_code=302)

@router.post("/wakatime/connect")
async def connect_wakatime(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user_id = await get_current_user_id(request, db)
    # WakaTime OAuth is a two‑step; we'll get the code from request body
    body = await request.json()
    code = body.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    # Exchange code for token (WakaTime uses same OAuth2 pattern)
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://wakatime.com/oauth/token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.WAKATIME_CLIENT_ID,
                "client_secret": settings.WAKATIME_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.WAKATIME_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"WakaTime token exchange failed (HTTP {resp.status_code}): {resp.text[:200]}"
            )
        try:
            token_data = resp.json()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail=f"WakaTime returned non-JSON response: {resp.text[:200]}"
            )
        if "error" in token_data:
            raise HTTPException(status_code=400, detail=token_data.get("error_description", "OAuth failed"))
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="WakaTime did not return an access token")
        refresh_token = token_data.get("refresh_token")

    # Store encrypted
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one()
    user.wakatime_token = encrypt_token(access_token)
    if refresh_token:
        user.wakatime_refresh = encrypt_token(refresh_token)
    await db.commit()

    # Trigger initial sync
    sync_wakatime_for_user.delay(str(user.id), user.wakatime_token)

    return {"status": "connected"}


@router.post("/leetcode/connect")
async def connect_leetcode(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user_id = await get_current_user_id(request, db)
    body = await request.json()
    username = body.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="Missing username")

    # Verify profile exists
    profile = await LeetCodeClient.get_user_profile(username)
    if not profile:
        raise HTTPException(status_code=404, detail="LeetCode user not found")

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one()
    user.leetcode_username = username
    await db.commit()

    # Trigger initial sync
    sync_leetcode_for_user.delay(str(user.id), username)

    return {"status": "connected", "username": username}

@router.post("/wakatime/disconnect")
async def disconnect_wakatime(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = await get_current_user_id(request, db)
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one()
    user.wakatime_token = None
    user.wakatime_refresh = None
    await db.commit()
    return {"status": "disconnected"}

@router.post("/leetcode/disconnect")
async def disconnect_leetcode(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = await get_current_user_id(request, db)
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one()
    user.leetcode_username = None
    await db.commit()
    return {"status": "disconnected"}

@router.get("/me")
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing access token")
    token = auth_header.split(" ")[1]
    try:
        from app.core.auth import decode_token
        payload = decode_token(token)
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": str(user.id),
        "github_username": user.github_username,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "email": user.email,
        "level": user.level,
        "total_xp": user.total_xp,
        "streak_current": user.streak_current,
        "streak_longest": user.streak_longest,
        "developer_score": user.developer_score,
        "wakatime_connected": user.wakatime_token is not None,
        "leetcode_connected": user.leetcode_username is not None,
        "leetcode_username": user.leetcode_username,
    }