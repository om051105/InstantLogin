import uuid
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session as DBSession

from app.config import get_settings
from app.models import User, AccountStatus, Session, SessionStatus, LoginAttempt, ErrorCode, SecurityEvent, EventType, Severity
from app.services.cache_service import cache_service

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─── Password Helpers ─────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ─── JWT Helpers ──────────────────────────────────────────────────────────────

def create_access_token(user_id: int, email: str) -> tuple[str, str]:
    """Returns (token, jti)."""
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "jti": jti,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, jti


def create_refresh_token(user_id: int) -> tuple[str, str]:
    """Returns (token, jti)."""
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": jti,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, jti


def decode_token(token: str) -> Optional[dict]:
    """Returns payload dict or None on failure."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


# ─── Registration ─────────────────────────────────────────────────────────────

def register_user(db: DBSession, name: str, email: str, password: str) -> User:
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise ValueError("Email already registered")

    user = User(
        name=name.strip(),
        email=email.lower().strip(),
        password_hash=hash_password(password),
        account_status=AccountStatus.ACTIVE,
    )
    db.add(user)
    db.flush()

    # Log registration event
    event = SecurityEvent(
        user_id=user.user_id,
        event_type=EventType.REGISTRATION,
        severity=Severity.INFO,
        description=f"New user registered: {email}",
    )
    db.add(event)
    db.commit()
    db.refresh(user)
    return user


# ─── Authentication ───────────────────────────────────────────────────────────

MAX_FAILED_ATTEMPTS = 5


def authenticate_user(
    db: DBSession,
    email: str,
    password: str,
    ip_address: Optional[str] = None,
    device: Optional[str] = None,
    browser: Optional[str] = None,
) -> tuple[User, Session, str, str]:
    """
    Authenticates credentials and creates a session.
    Returns (user, session, access_token, refresh_token).
    Raises ValueError with a descriptive error code string on failure.
    """
    import time as _time
    start = _time.perf_counter()

    def _record_attempt(user_id: Optional[int], success: bool, error_code: ErrorCode):
        elapsed_ms = (_time.perf_counter() - start) * 1000
        attempt = LoginAttempt(
            user_id=user_id,
            success=success,
            error_code=error_code,
            ip_address=ip_address,
            device=device,
            browser=browser,
            response_time_ms=round(elapsed_ms, 2),
        )
        db.add(attempt)

    # 1. Find user
    user: Optional[User] = db.query(User).filter(User.email == email.lower().strip()).first()

    if user is None:
        _record_attempt(None, False, ErrorCode.INVALID_USERNAME)
        _log_security_event(db, None, EventType.LOGIN_FAILURE, Severity.WARNING,
                            f"Login attempt with unknown email: {email}", ip_address)
        db.commit()
        raise ValueError(ErrorCode.INVALID_USERNAME)

    # 2. Check account status
    if user.account_status == AccountStatus.LOCKED:
        _record_attempt(user.user_id, False, ErrorCode.ACCOUNT_LOCKED)
        _log_security_event(db, user.user_id, EventType.LOGIN_FAILURE, Severity.HIGH,
                            "Login attempt on locked account", ip_address)
        db.commit()
        raise ValueError(ErrorCode.ACCOUNT_LOCKED)

    # 3. Verify password
    if not verify_password(password, user.password_hash):
        user.failed_attempts += 1
        if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
            user.account_status = AccountStatus.LOCKED
            _log_security_event(db, user.user_id, EventType.ACCOUNT_LOCKED, Severity.HIGH,
                                f"Account locked after {user.failed_attempts} failed attempts", ip_address)
        _record_attempt(user.user_id, False, ErrorCode.INVALID_PASSWORD)
        _log_security_event(db, user.user_id, EventType.LOGIN_FAILURE, Severity.WARNING,
                            "Invalid password provided", ip_address)
        db.commit()
        raise ValueError(ErrorCode.INVALID_PASSWORD)

    # 4. Successful — reset failed attempts, update last_login
    user.failed_attempts = 0
    user.last_login = datetime.now(timezone.utc)

    # 5. Create tokens
    access_token, access_jti = create_access_token(user.user_id, user.email)
    refresh_token, refresh_jti = create_refresh_token(user.user_id)

    # 6. Create session record
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    session = Session(
        session_id=session_id,
        user_id=user.user_id,
        expires_at=expires_at,
        status=SessionStatus.ACTIVE,
        device=device,
        browser=browser,
        ip_address=ip_address,
        refresh_token_hash=hash_password(refresh_token),
    )
    db.add(session)

    _record_attempt(user.user_id, True, ErrorCode.NONE)
    _log_security_event(db, user.user_id, EventType.LOGIN_SUCCESS, Severity.INFO,
                        "Successful login", ip_address)
    db.commit()
    db.refresh(user)
    db.refresh(session)

    return user, session, access_token, refresh_token


def _log_security_event(
    db: DBSession,
    user_id: Optional[int],
    event_type: EventType,
    severity: Severity,
    description: str,
    ip_address: Optional[str] = None,
) -> None:
    event = SecurityEvent(
        user_id=user_id,
        event_type=event_type,
        severity=severity,
        description=description,
        ip_address=ip_address,
    )
    db.add(event)


# ─── Logout ───────────────────────────────────────────────────────────────────

def logout_user(db: DBSession, session_id: str, access_jti: str, user_id: int) -> None:
    session = db.query(Session).filter(
        Session.session_id == session_id,
        Session.user_id == user_id,
    ).first()
    if session:
        session.status = SessionStatus.LOGGED_OUT

    # Blacklist the access token
    cache_service.blacklist_token(access_jti, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    cache_service.invalidate_user(user_id)

    _log_security_event(db, user_id, EventType.LOGOUT, Severity.INFO, "User logged out")
    db.commit()


# ─── Token Refresh ────────────────────────────────────────────────────────────

def refresh_tokens(db: DBSession, refresh_token: str) -> tuple[str, str]:
    """
    Validates a refresh token, revokes the old session, and issues new tokens.
    Returns (new_access_token, new_refresh_token).
    """
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token")

    user_id = int(payload["sub"])
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user or user.account_status != AccountStatus.ACTIVE:
        raise ValueError("User not found or inactive")

    new_access, _ = create_access_token(user.user_id, user.email)
    new_refresh, _ = create_refresh_token(user.user_id)
    return new_access, new_refresh
