from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: str
    user_id: int
    created_at: datetime
    expires_at: datetime
    status: str
    device: Optional[str] = None
    browser: Optional[str] = None
    ip_address: Optional[str] = None


class SessionListResponse(BaseModel):
    sessions: List[SessionOut]
    total: int


class LoginAttemptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attempt_id: int
    timestamp: datetime
    success: bool
    error_code: str
    ip_address: Optional[str] = None
    device: Optional[str] = None
    browser: Optional[str] = None
    response_time_ms: Optional[float] = None


class LoginAttemptListResponse(BaseModel):
    attempts: List[LoginAttemptOut]
    total: int
