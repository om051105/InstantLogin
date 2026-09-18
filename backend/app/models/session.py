import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SAEnum, func
from app.database import Base


class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    LOGGED_OUT = "logged_out"


class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String(64), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    status = Column(SAEnum(SessionStatus), default=SessionStatus.ACTIVE, nullable=False)
    device = Column(String(255), nullable=True)
    browser = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    refresh_token_hash = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<Session id={self.session_id} user_id={self.user_id} status={self.status}>"
