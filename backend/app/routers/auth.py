from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas import LoginIn, RegisterIn, TokenOut, UserOut
from ..security import auth_limiter, create_token, hash_password, verify_password
from ..services.activity import log
from ..services.post_service import user_out

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenOut, status_code=201, dependencies=[Depends(auth_limiter)],
             summary="Create a new user account")
def register(data: RegisterIn, request: Request, db: Session = Depends(get_db)):
    if db.query(User).filter((User.email == data.email.lower()) | (User.username == data.username)).first():
        raise HTTPException(409, "Username or email is already registered.")
    user = User(username=data.username, email=data.email.lower(), password_hash=hash_password(data.password))
    db.add(user)
    db.flush()
    log(db, "REGISTER", user.id, user.username, request.client.host if request.client else None)
    db.commit()
    return {"access_token": create_token(user), "token_type": "bearer", "user": user_out(db, user)}


@router.post("/login", response_model=TokenOut, dependencies=[Depends(auth_limiter)], summary="Log in and receive a JWT")
def login(data: LoginIn, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else None
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        log(db, "LOGIN_FAILED", user.id if user else None, data.email[:100], ip)
        db.commit()
        raise HTTPException(401, "Invalid email or password.")
    if not user.is_active:
        raise HTTPException(403, "This account has been suspended.")
    log(db, "LOGIN", user.id, user.username, ip)
    db.commit()
    return {"access_token": create_token(user), "token_type": "bearer", "user": user_out(db, user)}


@router.get("/me", response_model=UserOut, summary="Current user")
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_out(db, user)
