from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas import UserOut, UserUpdate
from ..services.media_service import save_upload
from ..services.post_service import user_out

router = APIRouter(prefix="/users", tags=["Users"])


def _own_or_admin(target_id: int, user: User):
    if user.id != target_id and user.role != "admin":
        raise HTTPException(403, "You can only modify your own profile.")


@router.get("/{user_id}", response_model=UserOut, summary="View a user profile")
def get_user(user_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(404, "User not found.")
    out = user_out(db, target)
    if user.id != target.id and user.role == "user":
        out["email"] = ""  # hide e-mail from other normal users
    return out


@router.put("/{user_id}", response_model=UserOut, summary="Update own profile")
def update_user(user_id: int, data: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _own_or_admin(user_id, user)
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(404, "User not found.")
    if data.username and data.username != target.username:
        if db.query(User).filter(User.username == data.username).first():
            raise HTTPException(409, "Username is already taken.")
        target.username = data.username
    db.commit()
    return user_out(db, target)


@router.post("/{user_id}/photo", response_model=UserOut, summary="Upload profile photo")
async def upload_photo(user_id: int, file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _own_or_admin(user_id, user)
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(404, "User not found.")
    name, _, _ = await save_upload(file, only="image")
    target.photo_url = f"/api/uploads/{name}"
    db.commit()
    return user_out(db, target)
