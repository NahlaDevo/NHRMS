from datetime import datetime, timedelta, timezone
from typing import Optional, List, Callable
from jose import JWTError, jwt
import bcrypt as _bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from backend.app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ── Role Constants ────────────────────────────────────────────────

ROLE_ADMIN = "ADMIN"
ROLE_RECRUITER = "RECRUITER"
ROLE_HR = "HR"
ROLE_PAYROLL_MANAGER = "PAYROLL_MANAGER"
ROLE_EMPLOYEE = "EMPLOYEE"
VALID_ROLES = [ROLE_ADMIN, ROLE_RECRUITER, ROLE_HR, ROLE_PAYROLL_MANAGER, ROLE_EMPLOYEE]

ROLE_HIERARCHY = {
    ROLE_ADMIN: 100,
    ROLE_RECRUITER: 60,
    ROLE_HR: 50,
    ROLE_PAYROLL_MANAGER: 40,
    ROLE_EMPLOYEE: 10,
}

# ── Permission Matrix ─────────────────────────────────────────────
PERMISSIONS = {
    # Employee records
    "employee.create": [ROLE_ADMIN, ROLE_HR, ROLE_RECRUITER],
    "employee.read": [ROLE_ADMIN, ROLE_HR, ROLE_RECRUITER, ROLE_PAYROLL_MANAGER, ROLE_EMPLOYEE],
    "employee.update": [ROLE_ADMIN, ROLE_HR, ROLE_RECRUITER],
    "employee.delete": [ROLE_ADMIN],
    "employee.import": [ROLE_ADMIN, ROLE_HR],
    "employee.export": [ROLE_ADMIN, ROLE_HR],
    "employee.upload_doc": [ROLE_ADMIN, ROLE_HR],

    # Attendance
    "attendance.checkin": [ROLE_ADMIN, ROLE_HR, ROLE_EMPLOYEE],
    "attendance.checkout": [ROLE_ADMIN, ROLE_HR, ROLE_EMPLOYEE],
    "attendance.read": [ROLE_ADMIN, ROLE_HR, ROLE_RECRUITER, ROLE_PAYROLL_MANAGER, ROLE_EMPLOYEE],
    "attendance.auto_close": [ROLE_ADMIN, ROLE_HR],

    # Payroll
    "payroll.generate": [ROLE_ADMIN, ROLE_PAYROLL_MANAGER],
    "payroll.read": [ROLE_ADMIN, ROLE_PAYROLL_MANAGER, ROLE_EMPLOYEE],
    "payroll.export": [ROLE_ADMIN, ROLE_PAYROLL_MANAGER],

    # Analytics
    "analytics.read": [ROLE_ADMIN, ROLE_RECRUITER, ROLE_HR, ROLE_PAYROLL_MANAGER],

    # ATS
    "ats.job.create": [ROLE_ADMIN, ROLE_HR, ROLE_RECRUITER],
    "ats.job.update": [ROLE_ADMIN, ROLE_HR, ROLE_RECRUITER],
    "ats.job.delete": [ROLE_ADMIN, ROLE_HR],
    "ats.job.read": [ROLE_ADMIN, ROLE_HR, ROLE_RECRUITER],
    "ats.candidate.upload": [ROLE_ADMIN, ROLE_HR, ROLE_RECRUITER],
    "ats.candidate.read": [ROLE_ADMIN, ROLE_HR, ROLE_RECRUITER],
    "ats.candidate.update": [ROLE_ADMIN, ROLE_HR, ROLE_RECRUITER],
    "ats.dashboard": [ROLE_ADMIN, ROLE_HR, ROLE_RECRUITER],

    # Interviews
    "interview.create": [ROLE_ADMIN, ROLE_HR, ROLE_RECRUITER],
    "interview.update": [ROLE_ADMIN, ROLE_HR, ROLE_RECRUITER],
    "interview.read": [ROLE_ADMIN, ROLE_HR, ROLE_RECRUITER],
    "interview.delete": [ROLE_ADMIN, ROLE_HR],

    # Admin
    "admin.users.read": [ROLE_ADMIN],
    "admin.users.manage": [ROLE_ADMIN],
    "admin.audit.read": [ROLE_ADMIN],
    "admin.attendance.stats": [ROLE_ADMIN, ROLE_HR, ROLE_RECRUITER],
    "admin.payroll.stats": [ROLE_ADMIN, ROLE_PAYROLL_MANAGER],
}

REFRESH_TOKEN_EXPIRE_DAYS = 30


# ── Password Helpers ──────────────────────────────────────────────

def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def normalize_role(role: str) -> str:
    r = role.strip().upper()
    return r if r in VALID_ROLES else ROLE_EMPLOYEE


def validate_role(role: str) -> str:
    r = normalize_role(role)
    if r not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{role}'. Must be one of: {VALID_ROLES}",
        )
    return r

# ── JWT Helpers ───────────────────────────────────────────────────


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = decode_access_token(token)
    if payload.get("type") == "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not allowed for this endpoint",
        )
    username: str = payload.get("sub")
    role: str = normalize_role(payload.get("role", ROLE_EMPLOYEE))
    user_id: str = payload.get("user_id", "")
    company_id: str = payload.get("company_id", "")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return {"username": username, "role": role, "user_id": user_id, "company_id": company_id}


def verify_refresh_token(token: str) -> dict:
    payload = decode_access_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    return payload


# ── Role-Based Access Control ─────────────────────────────────────


def require_roles(roles: List[str]) -> Callable:
    normalized = [normalize_role(r) for r in roles]

    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in normalized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {roles}",
            )
        return current_user

    return role_checker


def require_permission(permission: str) -> Callable:
    def permission_checker(current_user: dict = Depends(get_current_user)) -> dict:
        allowed = PERMISSIONS.get(permission, [])
        if current_user["role"] not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Missing permission: {permission}",
            )
        return current_user

    return permission_checker


def has_role(current_user: dict, role: str) -> bool:
    return current_user.get("role") == normalize_role(role)


def has_any_role(current_user: dict, roles: List[str]) -> bool:
    return current_user.get("role") in [normalize_role(r) for r in roles]


def role_at_least(current_user: dict, minimum_role: str) -> bool:
    user_level = ROLE_HIERARCHY.get(current_user.get("role"), 0)
    min_level = ROLE_HIERARCHY.get(normalize_role(minimum_role), 0)
    return user_level >= min_level


# ── Backward-Compatible Aliases ───────────────────────────────────

require_admin = require_roles([ROLE_ADMIN])
