"""Auth router — login endpoint."""
import hashlib
import secrets
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.api.deps import get_auth_service
from src.services import AuthService

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    user: str
    role: str
    token: str


def _hash_password(password: str) -> str:
    """SHA-256 hash matching the desktop app's PasswordManager."""
    return hashlib.sha256(password.encode()).hexdigest()


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    auth_svc: AuthService = Depends(get_auth_service),
):
    """Authenticate a user and return a session token."""
    password_hash = _hash_password(payload.password)
    ok = auth_svc.authenticate(payload.username, payload.password)
    if not ok:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    role = auth_svc.get_user_role(payload.username)
    # Generate a simple bearer token (stateless — swap for JWT in production)
    token = secrets.token_hex(32)
    return LoginResponse(user=payload.username, role=role or "user", token=token)
