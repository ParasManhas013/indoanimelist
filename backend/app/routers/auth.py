from datetime import timedelta, timezone, datetime
from fastapi import APIRouter, HTTPException, Request, Response, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, MessageResponse
from app.services import auth_service
from app.services.email_service import send_verification_email
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    is_prod = settings.ENVIRONMENT == "production"
    # Cross-origin deployments (Vercel → Render) require SameSite=None + Secure.
    # SameSite=Lax causes browsers to silently drop cookies on cross-origin requests,
    # making every authenticated call return 401. In development we use Lax (same-origin).
    samesite: str = "none" if is_prod else "lax"
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_prod,  # SameSite=None requires Secure=True (enforced in prod)
        samesite=samesite,
        max_age=settings.JWT_EXPIRE_DAYS * 86400,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_prod,
        samesite=samesite,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # Extract client IP
    client_ip = request.headers.get("X-Forwarded-For", request.client.host).split(",")[0].strip()

    # Geofence check
    is_indian = await auth_service.check_indian_ip(client_ip)
    if not is_indian:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is restricted to users accessing from India.",
        )

    # Check duplicate email
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # Create user
    verification_token = auth_service.create_verification_token()
    user = User(
        email=payload.email,
        hashed_password=auth_service.hash_password(payload.password),
        verification_token=verification_token,
    )
    db.add(user)
    await db.commit()

    # Send verification email
    await send_verification_email(payload.email, verification_token)

    return {"message": "Account created. Please check your email to verify your account."}


@router.get("/verify", response_model=MessageResponse)
async def verify_email(token: str, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.verification_token == token))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token.")

    user.is_verified = True
    user.verification_token = None

    # Issue tokens on verification
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token()
    user.refresh_token = refresh_token

    await db.commit()
    _set_auth_cookies(response, access_token, refresh_token)

    return {"message": "Email verified successfully. You are now logged in."}


@router.post("/login", response_model=MessageResponse)
async def login(payload: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not auth_service.verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in.",
        )

    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token()
    user.refresh_token = refresh_token
    await db.commit()

    _set_auth_cookies(response, access_token, refresh_token)
    return {"message": "Logged in successfully."}


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully."}


@router.post("/refresh", response_model=MessageResponse)
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token.")

    result = await db.execute(select(User).where(User.refresh_token == token))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")

    access_token = auth_service.create_access_token(user.id)
    new_refresh = auth_service.create_refresh_token()
    user.refresh_token = new_refresh
    await db.commit()

    _set_auth_cookies(response, access_token, new_refresh)
    return {"message": "Token refreshed."}


@router.get("/me", response_model=UserResponse)
async def me(request: Request, db: AsyncSession = Depends(get_db)):
    user = await auth_service.get_current_user(db, request.cookies.get("access_token"))
    return user
