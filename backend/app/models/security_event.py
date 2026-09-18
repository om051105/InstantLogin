import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SAEnum, Text, func
from app.database import Base


class EventType(str, enum.Enum):
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILURE = "LOGIN_FAILURE"
    LOGOUT = "LOGOUT"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    ACCOUNT_UNLOCKED = "ACCOUNT_UNLOCKED"
    RATE_LIMITED = "RATE_LIMITED"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    PASSWORD_CHANGED = "PASSWORD_CHANGED"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    REGISTRATION = "REGISTRATION"


class Severity(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SecurityEvent(Base):
    __tablename__ = "security_events"

    event_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(SAEnum(EventType), nullable=False)
    severity = Column(SAEnum(Severity), default=Severity.INFO, nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)

    def __repr__(self):
        return f"<SecurityEvent id={self.event_id} type={self.event_type} severity={self.severity}>"
