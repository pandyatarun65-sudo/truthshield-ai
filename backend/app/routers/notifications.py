from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Notification, User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def _out(n: Notification):
    return {"id": n.id, "type": n.type, "message": n.message, "post_id": n.post_id,
            "is_read": n.is_read, "created_at": n.created_at.isoformat()}


@router.get("", summary="My notifications")
def list_notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Notification).filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(100).all()
    return {"unread": sum(1 for n in rows if not n.is_read), "items": [_out(n) for n in rows]}


@router.put("/read-all", summary="Mark all as read")
def read_all(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter_by(user_id=user.id, is_read=False).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read."}


@router.put("/{notification_id}/read", summary="Mark one as read")
def mark_read(notification_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    n = db.get(Notification, notification_id)
    if not n or n.user_id != user.id:
        raise HTTPException(404, "Notification not found.")
    n.is_read = True
    db.commit()
    return _out(n)
