import time
from fastapi import APIRouter, Depends, HTTPException, Request, status, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session as DBSession
from typing import Optional

from app.database import get_db
from app.schemas import (
    RegisterRequest, LoginRequest, RefreshRequest,
    TokenResponse, UserOut, MessageResponse,
)
from app.services.auth_service import (
    register_user, authenticate_user, logout_user, refresh_tokens, decode_token,
)
from app.services.rate_limiter import rate_limiter
from app.dependencies import get_current_user, get_token_jti, get_client_ip
from app.models import User
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


def _parse_user_agent(user_agent: str) -> tuple[str, str]:
    """Very basic UA parsing — returns (browser, device)."""
    ua = user_agent.lower()
    browser = "Unknown"
    device = "Desktop"

    if "chrome" in ua and "edg" not in ua:
        browser = "Chrome"
    elif "firefox" in ua:
        browser = "Firefox"
    elif "safari" in ua and "chrome" not in ua:
        browser = "Safari"
    elif "edg" in ua:
        browser = "Edge"
    elif "opera" in ua or "opr" in ua:
        browser = "Opera"

    if "mobile" in ua or "android" in ua or "iphone" in ua:
        device = "Mobile"
    elif "tablet" in ua or "ipad" in ua:
        device = "Tablet"

    return browser, device


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: DBSession = Depends(get_db)):
    """Register a new user account."""
    try:
        user = register_user(db, name=body.name, email=body.email, password=body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    db: DBSession = Depends(get_db),
    user_agent: Optional[str] = Header(default="Unknown"),
):
    """Authenticate and receive JWT tokens."""
    ip = get_client_ip(request)
    browser, device = _parse_user_agent(user_agent or "")

    # Rate limit by IP
    allowed_ip, remaining_ip, retry_after = rate_limiter.is_allowed(f"ip:{ip}")
    if not allowed_ip:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "RATE_LIMITED",
                "message": f"Too many login attempts. Please try again in {retry_after} seconds.",
                "retry_after": retry_after,
            },
            headers={"Retry-After": str(retry_after)},
        )

    # Rate limit by email
    allowed_email, remaining_email, retry_after_email = rate_limiter.is_allowed(f"email:{body.email}")
    if not allowed_email:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "RATE_LIMITED",
                "message": f"Too many attempts for this account. Please try again in {retry_after_email} seconds.",
                "retry_after": retry_after_email,
            },
            headers={"Retry-After": str(retry_after_email)},
        )

    try:
        user, session, access_token, refresh_token = authenticate_user(
            db,
            email=body.email,
            password=body.password,
            ip_address=ip,
            device=device,
            browser=browser,
        )
    except ValueError as e:
        error_code = str(e)
        error_messages = {
            "INVALID_USERNAME": "No account found with that email address.",
            "INVALID_PASSWORD": "Incorrect password. Please try again.",
            "ACCOUNT_LOCKED": "Your account has been locked due to too many failed attempts. Please contact support.",
        }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": error_code,
                "message": error_messages.get(error_code, "Authentication failed."),
            },
        )

    # Reset rate limit on success
    rate_limiter.reset(f"ip:{ip}")
    rate_limiter.reset(f"email:{body.email}")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserOut.model_validate(user),
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Invalidate the current session and blacklist the access token."""
    payload = decode_token(credentials.credentials)
    jti = payload.get("jti", "") if payload else ""
    session_id = request.headers.get("X-Session-Id", "")
    logout_user(db, session_id=session_id, access_jti=jti, user_id=current_user.user_id)
    return MessageResponse(message="Successfully logged out")


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: DBSession = Depends(get_db)):
    """Exchange a valid refresh token for new access and refresh tokens."""
    try:
        new_access, new_refresh = refresh_tokens(db, refresh_token=body.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    payload = decode_token(new_access)
    user_id = int(payload["sub"])
    from app.models import User
    user = db.query(User).filter(User.user_id == user_id).first()

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's profile."""
    return current_user
