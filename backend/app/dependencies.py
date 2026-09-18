from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.services.auth_service import decode_token
from app.services.cache_service import cache_service
from app.models import User, AccountStatus

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: DBSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency that validates a Bearer JWT and returns the current user.
    Checks the token blacklist via Redis.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check blacklist
    jti = payload.get("jti")
    if jti and cache_service.is_token_blacklisted(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(payload["sub"])

    # Try cache first
    cached = cache_service.get_user(user_id)
    if cached:
        user = db.query(User).filter(User.user_id == user_id).first()
    else:
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            cache_service.set_user(user_id, {"user_id": user.user_id, "email": user.email})

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    if user.account_status != AccountStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.account_status.value}",
        )

    return user


def get_token_jti(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract the JTI from the token (for logout)."""
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload.get("jti", "")


def get_client_ip(request: Request) -> str:
    """Extract client IP from request headers (handles proxies)."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
