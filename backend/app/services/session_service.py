from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session as DBSession

from app.models import Session, SessionStatus, User


def get_user_sessions(db: DBSession, user_id: int) -> List[Session]:
    """Return all non-expired sessions for a user."""
    return (
        db.query(Session)
        .filter(Session.user_id == user_id)
        .order_by(Session.created_at.desc())
        .all()
    )


def get_active_sessions(db: DBSession, user_id: int) -> List[Session]:
    """Return only currently active sessions."""
    now = datetime.now(timezone.utc)
    sessions = (
        db.query(Session)
        .filter(
            Session.user_id == user_id,
            Session.status == SessionStatus.ACTIVE,
        )
        .all()
    )
    # Expire any sessions that have passed their expires_at
    updated = []
    for s in sessions:
        exp = s.expires_at
        if exp.tzinfo is None:
            from datetime import timezone as _tz
            exp = exp.replace(tzinfo=_tz.utc)
        if exp < now:
            s.status = SessionStatus.EXPIRED
        else:
            updated.append(s)
    db.commit()
    return updated


def revoke_session(db: DBSession, session_id: str, user_id: int) -> bool:
    """Revoke a specific session. Returns True if found and revoked."""
    session = db.query(Session).filter(
        Session.session_id == session_id,
        Session.user_id == user_id,
    ).first()
    if not session:
        return False
    session.status = SessionStatus.LOGGED_OUT
    db.commit()
    return True


def revoke_all_sessions(db: DBSession, user_id: int, except_session_id: Optional[str] = None) -> int:
    """Revoke all sessions for a user (except the current one). Returns count revoked."""
    query = db.query(Session).filter(
        Session.user_id == user_id,
        Session.status == SessionStatus.ACTIVE,
    )
    if except_session_id:
        query = query.filter(Session.session_id != except_session_id)
    sessions = query.all()
    for s in sessions:
        s.status = SessionStatus.LOGGED_OUT
    db.commit()
    return len(sessions)
