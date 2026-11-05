import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .security import decode_token

bearer = HTTPBearer(auto_error=False)


def get_current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not creds:
        raise HTTPException(401, "Not authenticated. Please log in.")
    try:
        data = decode_token(creds.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Your session has expired. Please log in again.")
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid authentication token.")
    user = db.get(User, int(data["sub"]))
    if not user:
        raise HTTPException(401, "User no longer exists.")
    if not user.is_active:
        raise HTTPException(403, "This account has been suspended.")
    return user


def get_optional_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)):
    if not creds:
        return None
    try:
        return get_current_user(creds, db)
    except HTTPException:
        return None


def require_staff(user: User = Depends(get_current_user)) -> User:
    if user.role not in ("admin", "moderator"):
        raise HTTPException(403, "Moderator or admin access required.")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(403, "Admin access required.")
    return user
