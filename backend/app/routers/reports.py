from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_staff
from ..models import Post, Report, User
from ..schemas import ReportIn, ReportUpdate
from ..services.activity import log, notify

router = APIRouter(tags=["Reports"])


def report_out(r: Report, db: Session):
    post = db.get(Post, r.post_id)
    reporter = db.get(User, r.user_id)
    return {"report_id": r.report_id, "post_id": r.post_id, "post_text": (post.text[:140] if post else ""),
            "post_status": post.status if post else None, "user_id": r.user_id,
            "reporter": reporter.username if reporter else None, "reason": r.reason, "description": r.description,
            "status": r.status, "reviewed_by": r.reviewed_by, "resolution_note": r.resolution_note,
            "created_at": r.created_at.isoformat()}


def apply_report_update(db: Session, report: Report, staff: User, data: ReportUpdate):
    report.status, report.reviewed_by, report.resolution_note = data.status, staff.id, data.resolution_note
    if data.status in ("RESOLVED", "REJECTED"):
        word = "resolved" if data.status == "RESOLVED" else "reviewed and rejected"
        notify(db, report.user_id, "REPORT_RESOLVED", f"Your report #{report.report_id} was {word} by a moderator.", report.post_id)
    log(db, "REPORT_ACTION", staff.id, f"report={report.report_id} -> {data.status}")


@router.post("/reports", status_code=201, summary="Report a post")
def create_report(data: ReportIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = db.get(Post, data.post_id)
    if not post or post.status == "REMOVED":
        raise HTTPException(404, "Post not found.")
    if db.query(Report).filter_by(post_id=data.post_id, user_id=user.id, status="PENDING").first():
        raise HTTPException(409, "You have already reported this post.")
    r = Report(post_id=data.post_id, user_id=user.id, reason=data.reason, description=data.description)
    db.add(r)
    log(db, "REPORT_CREATED", user.id, f"post={data.post_id} reason={data.reason}")
    db.commit()
    return report_out(r, db)


@router.get("/reports", summary="Own report history (staff see all)")
def list_reports(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    q = db.query(Report)
    if user.role == "user":
        q = q.filter(Report.user_id == user.id)
    return [report_out(r, db) for r in q.order_by(Report.created_at.desc()).limit(200).all()]


@router.put("/reports/{report_id}", summary="Update a report status (moderator/admin)")
def update_report(report_id: int, data: ReportUpdate, staff: User = Depends(require_staff), db: Session = Depends(get_db)):
    r = db.get(Report, report_id)
    if not r:
        raise HTTPException(404, "Report not found.")
    apply_report_update(db, r, staff, data)
    db.commit()
    return report_out(r, db)
