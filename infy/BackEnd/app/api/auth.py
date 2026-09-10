from fastapi import APIRouter, HTTPException, Header, status
from app.core.security import hash_password, verify_password, create_jwt_token, decode_jwt_token
from app.schemas.auth import SignUpRequest, LoginRequest, AuthResponse
from app.services.storage_service import storage_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse)
def signup(payload: SignUpRequest):
    """
    Registers a new developer or admin user account.
    """
    existing_user = storage_service.get_user_by_email(payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    hashed_pw = hash_password(payload.password)

    user = storage_service.create_user(
        email=payload.email,
        hashed_password=hashed_pw,
        full_name=payload.full_name,
        role="developer"
    )

    token = create_jwt_token({
        "user_id": user["user_id"],
        "email": user["email"],
        "role": user["role"],
        "full_name": user["full_name"]
    })

    return AuthResponse(
        token=token,
        user_id=user["user_id"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"],
        is_active=bool(user["is_active"])
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    """
    Authenticates a user and returns a JWT session token.
    """
    user = storage_service.get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated by an administrator."
        )

    token = create_jwt_token({
        "user_id": user["user_id"],
        "email": user["email"],
        "role": user["role"],
        "full_name": user["full_name"]
    })

    return AuthResponse(
        token=token,
        user_id=user["user_id"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"],
        is_active=bool(user["is_active"])
    )


@router.get("/me", response_model=AuthResponse)
def get_current_user(authorization: str = Header(None)):
    """
    Validates current authorization header JWT token.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header."
        )

    token = authorization.split(" ")[1]
    payload = decode_jwt_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired or invalid JWT token."
        )

    user = storage_service.get_user_by_id(payload["user_id"])
    if not user or not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer active."
        )

    return AuthResponse(
        token=token,
        user_id=user["user_id"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"],
        is_active=bool(user["is_active"])
    )
