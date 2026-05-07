from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...db.session import get_db
from ...db.models import User, Session
from ...core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from ...core.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


def user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "xp": user.xp,
        "badges": user.badges or [],
        "avatar_color": user.avatar_color,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User).where(User.email == body.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Email already registered")
        user = User(email=body.email, hashed_password=hash_password(body.password), name=body.name)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id)
        settings = get_settings()
        session = Session(
            user_id=user.id,
            refresh_token=refresh,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
        )
        db.add(session)
        await db.commit()
        return {"access_token": access, "refresh_token": refresh, "token_type": "bearer", "user": user_to_dict(user)}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=503,
            detail=f"Database unavailable (schema may be stale). Call POST /api/admin/reset-db to fix. Error: {e}",
        )


@router.post("/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User).where(User.email == body.email))
        user = result.scalar_one_or_none()
        if not user or not verify_password(body.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        user.last_login = datetime.now(timezone.utc)
        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id)
        settings = get_settings()
        session = Session(
            user_id=user.id,
            refresh_token=refresh,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
        )
        db.add(session)
        await db.commit()
        await db.refresh(user)
        return {"access_token": access, "refresh_token": refresh, "token_type": "bearer", "user": user_to_dict(user)}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=503,
            detail=f"Database unavailable (schema may be stale). Call POST /api/admin/reset-db to fix. Error: {e}",
        )


@router.post("/refresh")
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    user_id = decode_token(body.refresh_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    result = await db.execute(select(Session).where(Session.refresh_token == body.refresh_token))
    session = result.scalar_one_or_none()
    if not session or session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")
    access = create_access_token(user_id)
    return {"access_token": access, "token_type": "bearer"}


# /api/me is implemented in main.py with proper dependency injection
