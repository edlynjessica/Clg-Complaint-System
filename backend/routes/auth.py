from fastapi import APIRouter, HTTPException, Depends
from pymongo.errors import DuplicateKeyError

from database import users_collection
from models.user import User
from schemas.auth import SignupRequest, LoginRequest
from utils.auth import create_access_token, get_current_user, require_role
from utils.security import hash_password, verify_password

ALLOWED_ROLES = {
    "Faculty / Staff",
    "Service Incharge",
    "Technician",
    "Admin",
}

ALLOWED_SERVICES = {
    "Electrical",
    "Plumbing",
}


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup")
def signup(data: SignupRequest):
    if data.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")

    if data.role in {"Service Incharge", "Technician"}:
        if data.service not in ALLOWED_SERVICES:
            raise HTTPException(
                status_code=400,
                detail="Service must be Electrical or Plumbing",
            )
    else:
        if data.service is not None:
            raise HTTPException(
                status_code=400,
                detail="Service is only applicable to Service Incharge or Technician",
            )
    existing_user = users_collection.find_one({"email": data.email})
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
        service=data.service,
    )

    try:
        result = users_collection.insert_one(user.model_dump())
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already registered")

    return {
        "message": "User registered successfully",
        "user_id": str(result.inserted_id),
    }


@router.post("/login")
def login(data: LoginRequest):
    user = users_collection.find_one({"email": data.email})

    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(
        {
            "user_id": str(user["_id"]),
            "role": user["role"],
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

@router.get("/admin-test")
def admin_test(current_user: dict = Depends(get_current_user)):
    require_role(current_user, ["Admin"])
    return {"message": "Admin access granted"}