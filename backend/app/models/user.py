import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum, Boolean, func
from app.database import Base


class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    LOCKED = "locked"
    SUSPENDED = "suspended"
    UNVERIFIED = "unverified"


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    account_status = Column(SAEnum(AccountStatus), default=AccountStatus.ACTIVE, nullable=False)
    failed_attempts = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User id={self.user_id} email={self.email} status={self.account_status}>"
