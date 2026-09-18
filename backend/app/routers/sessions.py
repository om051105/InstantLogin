from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.schemas.session import SessionListResponse, SessionOut, LoginAttemptListResponse, LoginAttemptOut
from app.schemas.auth import MessageResponse
from app.services.session_service import get_active_sessions, get_user_sessions, revoke_session, revoke_all_sessions
from app.dependencies import get_current_user
from app.models import User, LoginAttempt

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("/me", response_model=SessionListResponse)
async def list_my_sessions(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    """List all active sessions for the current user."""
    sessions = get_active_sessions(db, current_user.user_id)
    return SessionListResponse(
        sessions=[SessionOut.model_validate(s) for s in sessions],
        total=len(sessions),
    )


@router.delete("/{session_id}", response_model=MessageResponse)
async def revoke_session_endpoint(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    """Revoke a specific session."""
    success = revoke_session(db, session_id=session_id, user_id=current_user.user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return MessageResponse(message="Session revoked successfully")


@router.delete("/", response_model=MessageResponse)
async def revoke_all_sessions_endpoint(
    current_session_id: str = "",
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    """Revoke all sessions for the current user."""
    count = revoke_all_sessions(db, user_id=current_user.user_id)
    return MessageResponse(message=f"Revoked {count} sessions")


@router.get("/attempts", response_model=LoginAttemptListResponse)
async def list_login_attempts(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
):
    """Get recent login attempts for the current user."""
    attempts = (
        db.query(LoginAttempt)
        .filter(LoginAttempt.user_id == current_user.user_id)
        .order_by(LoginAttempt.timestamp.desc())
        .limit(min(limit, 100))
        .all()
    )
    return LoginAttemptListResponse(
        attempts=[LoginAttemptOut.model_validate(a) for a in attempts],
        total=len(attempts),
    )
