from fastapi import APIRouter, Depends, HTTPException
from backend.app.schemas.user import UserRegister, UserLogin, TokenResponse, RefreshTokenRequest
from backend.app.services import auth_service
from backend.app.utils.security import get_current_user, verify_refresh_token, create_access_token, normalize_role

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register")
def register(data: UserRegister):
    return auth_service.register_user(
        username=data.username,
        password=data.password,
        email=data.email,
        role=data.role,
    )


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin):
    return auth_service.authenticate_user(
        username=data.username,
        password=data.password,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(data: RefreshTokenRequest):
    payload = verify_refresh_token(data.refresh_token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = auth_service.find_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    access_token = create_access_token(data={
        "sub": user["username"],
        "role": normalize_role(user.get("role", "EMPLOYEE")),
        "user_id": str(user.get("id", "")),
        "company_id": user.get("company_id", ""),
    })
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": data.refresh_token,
    }


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
