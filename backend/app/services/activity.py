from sqlalchemy.orm import Session

from ..models import ActivityLog, Notification


def log(db: Session, action: str, user_id=None, detail=None, ip=None):
    db.add(ActivityLog(user_id=user_id, action=action, detail=(detail or "")[:300], ip=ip))


def notify(db: Session, user_id: int, type_: str, message: str, post_id=None):
    db.add(Notification(user_id=user_id, post_id=post_id, type=type_, message=message[:300]))
