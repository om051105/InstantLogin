import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum as SAEnum, Float, func
from app.database import Base


class ErrorCode(str, enum.Enum):
    NONE = "NONE"
    INVALID_PASSWORD = "INVALID_PASSWORD"
    INVALID_USERNAME = "INVALID_USERNAME"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    MFA_FAILURE = "MFA_FAILURE"
    NETWORK_ERROR = "NETWORK_ERROR"
    SERVER_ERROR = "SERVER_ERROR"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    RATE_LIMITED = "RATE_LIMITED"


class LoginAttempt(Base):
    __tablename__ = "login_attempts"

    attempt_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True, index=True)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    success = Column(Boolean, default=False, nullable=False)
    error_code = Column(SAEnum(ErrorCode), default=ErrorCode.NONE, nullable=False)
    ip_address = Column(String(45), nullable=True)
    device = Column(String(255), nullable=True)
    browser = Column(String(255), nullable=True)
    response_time_ms = Column(Float, nullable=True)

    def __repr__(self):
        return f"<LoginAttempt id={self.attempt_id} user_id={self.user_id} success={self.success}>"
