from datetime import datetime
from fastapi import HTTPException, status
from backend.app.database.excel_manager import user_db
from backend.app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token, validate_role, normalize_role
from backend.app.utils.helpers import logger


def register_user(username: str, password: str, email: str, role: str = "EMPLOYEE"):
    existing = user_db.find_by_id(username, id_column="Username")
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    valid_role = validate_role(role)
    hashed_pw = hash_password(password)
    now = datetime.now().isoformat()
    df = user_db.read_all()
    next_id = str(len(df) + 1)
    user_record = {
        "User ID": next_id,
        "Username": username,
        "Password Hash": hashed_pw,
        "Email": email,
        "Role": valid_role,
        "Is Active": "True",
        "Created At": now,
        "Updated At": now,
    }
    user_db.insert(user_record)
    logger.info(f"User registered: {username}")
    return {"message": "User registered successfully", "username": username, "user_id": next_id}


def authenticate_user(username: str, password: str):
    user = user_db.find_by_id(username, id_column="Username")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    if not verify_password(password, user["Password Hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    if user.get("Is Active", "True") != "True":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
    raw_uid = user.get("User ID", "")
    if not raw_uid or str(raw_uid).strip() == "":
        df = user_db.read_all()
        mask = df["Username"].astype(str).str.strip() == username.strip()
        user_id = str(mask.idxmax() + 1) if mask.any() else "0"
    else:
        user_id = str(raw_uid)
    role = normalize_role(user.get("Role", "EMPLOYEE"))
    company_id = user.get("company_id", "COMPANY_1")
    token_data = {
        "sub": user["Username"],
        "role": role,
        "user_id": user_id,
        "company_id": company_id,
    }
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data={"sub": user["Username"]})
    logger.info(f"User logged in: {username}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user["Username"],
        "role": role,
        "refresh_token": refresh_token,
    }


def find_user(username: str):
    user = user_db.find_by_id(username, id_column="Username")
    if not user:
        return None
    return user


def get_all_users():
    df = user_db.read_all()
    users = []
    for idx, (_, row) in enumerate(df.iterrows()):
        users.append({
            "user_id": row.get("User ID", str(idx + 1)),
            "username": row.get("Username", ""),
            "email": row.get("Email", ""),
            "role": row.get("Role", ""),
            "is_active": row.get("Is Active", ""),
            "created_at": row.get("Created At", ""),
        })
    return users


def update_user_role(username: str, new_role: str):
    user = user_db.find_by_id(username, id_column="Username")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_db.update(username, {"Role": new_role}, id_column="Username")
    logger.info(f"User role updated: {username} -> {new_role}")
    return {"message": "User role updated"}


def deactivate_user(username: str):
    user = user_db.find_by_id(username, id_column="Username")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_db.update(username, {"Is Active": "False"}, id_column="Username")
    logger.info(f"User deactivated: {username}")
    return {"message": "User deactivated"}
