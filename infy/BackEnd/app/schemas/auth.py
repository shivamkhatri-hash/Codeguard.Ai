from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: Optional[str] = "developer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    token: str
    user_id: str
    email: str
    full_name: str
    role: str
    is_active: bool


class UserItem(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: str


class AdminStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_analyses: int
    total_findings: int
    severity_breakdown: Dict[str, int]
    threat_distribution: Dict[str, int]
    average_health_score: float
    recent_audit_logs: List[Dict[str, Any]]
