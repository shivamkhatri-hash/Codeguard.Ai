from typing import List
from fastapi import APIRouter, HTTPException, Header, status

from app.core.security import decode_jwt_token
from app.schemas.auth import UserItem, AdminStatsResponse
from app.services.storage_service import storage_service

router = APIRouter(prefix="/admin", tags=["admin"])


def _verify_admin(authorization: str):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header."
        )

    token = authorization.split(" ")[1]
    payload = decode_jwt_token(token)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to access this resource."
        )

    return payload


@router.get("/users", response_model=List[UserItem])
def list_users(authorization: str = Header(None)):
    """
    Returns list of registered users (Admin only).
    """
    _verify_admin(authorization)
    users = storage_service.list_users()
    return [
        UserItem(
            user_id=u["user_id"],
            email=u["email"],
            full_name=u["full_name"],
            role=u["role"],
            is_active=bool(u["is_active"]),
            created_at=u["created_at"]
        )
        for u in users
    ]


@router.post("/users/{user_id}/status")
def toggle_user_status(user_id: str, authorization: str = Header(None)):
    """
    Toggles active/blocked status for a user (Admin only).
    """
    _verify_admin(authorization)
    if not storage_service.toggle_user_status(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found."
        )

    user = storage_service.get_user_by_id(user_id)
    return {
        "success": True,
        "user_id": user_id,
        "is_active": bool(user["is_active"]),
        "message": f"User status updated to {'Active' if user['is_active'] else 'Blocked'}."
    }


@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(authorization: str = Header(None)):
    """
    Returns platform-wide security analytics (Admin only).
    """
    _verify_admin(authorization)
    stats = storage_service.get_admin_stats()
    return AdminStatsResponse(
        total_users=stats["total_users"],
        active_users=stats["active_users"],
        total_analyses=stats["total_analyses"],
        total_findings=stats["total_findings"],
        severity_breakdown=stats["severity_breakdown"],
        threat_distribution=stats["threat_distribution"],
        average_health_score=stats["average_health_score"],
        recent_audit_logs=stats["recent_audit_logs"]
    )
