import csv
import io
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_admin, require_staff
from ..models import (ActivityLog, AIAnalysis, DecisionLog, FactVerification, FeedbackSample, KnowledgeBase, Post, Report, User)
from ..schemas import KnowledgeIn, PostAction, ReportUpdate, UserStatusIn
from ..services.activity import log
from ..services.moderation import apply_post_action
from ..services.post_service import post_out, user_out
from .reports import apply_report_update, report_out

router = APIRouter(prefix="/admin", tags=["Admin / Moderator"])


def _count(db, model, *filters):
    return db.query(func.count()).select_from(model).filter(*filters).scalar()


@router.get("/dashboard", summary="Dashboard counters")
def dashboard(staff: User = Depends(require_staff), db: Session = Depends(get_db)):
    live = Post.status != "REMOVED"
    return {
        "total_users": _count(db, User),
        "total_posts": _count(db, Post, live),
        "safe_posts": _count(db, Post, Post.status == "PUBLISHED"),
        "warning_posts": _count(db, Post, Post.status == "WARNING"),
        "blocked_posts": _count(db, Post, Post.status == "BLOCKED"),
        "posts_under_review": _count(db, Post, Post.status == "UNDER_REVIEW"),
        "pending_reports": _count(db, Report, Report.status == "PENDING"),
        "total_reports": _count(db, Report),
        "fake_news_detected": _count(db, Post, live, Post.risk_score > 60),
    }


@router.get("/users", summary="List / search users")
def users(q: str | None = None, staff: User = Depends(require_staff), db: Session = Depends(get_db)):
    query = db.query(User)
    if q:
        query = query.filter(User.username.ilike(f"%{q}%") | User.email.ilike(f"%{q}%"))
    return [user_out(db, u) for u in query.order_by(User.id).limit(200).all()]


@router.put("/users/{user_id}", summary="Suspend / activate a user (admin only)")
def set_user_status(user_id: int, data: UserStatusIn, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(404, "User not found.")
    if target.id == admin.id or target.role == "admin":
        raise HTTPException(400, "Admin accounts cannot be suspended.")
    target.is_active = data.is_active
    log(db, "USER_ACTIVATED" if data.is_active else "USER_SUSPENDED", admin.id, f"user={target.id}")
    db.commit()
    return user_out(db, target)


@router.get("/posts", summary="All posts with their moderation state")
def posts(status: str | None = None, q: str | None = None, staff: User = Depends(require_staff), db: Session = Depends(get_db)):
    query = db.query(Post)
    if status:
        query = query.filter(Post.status == status)
    if q:
        query = query.filter(Post.text.ilike(f"%{q}%"))
    return [post_out(db, p, staff) for p in query.order_by(Post.created_at.desc()).limit(200).all()]


@router.put("/posts/{post_id}", summary="Approve / block / restore / remove a post")
def post_action(post_id: int, data: PostAction, staff: User = Depends(require_staff), db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(404, "Post not found.")
    apply_post_action(db, post, staff, data.action, data.note)
    db.commit()
    return post_out(db, post, staff)


@router.get("/reports", summary="All reports")
def reports(status: str | None = None, staff: User = Depends(require_staff), db: Session = Depends(get_db)):
    q = db.query(Report)
    if status:
        q = q.filter(Report.status == status)
    return [report_out(r, db) for r in q.order_by(Report.created_at.desc()).limit(200).all()]


@router.put("/reports/{report_id}", summary="Review / resolve / reject a report")
def update_report(report_id: int, data: ReportUpdate, staff: User = Depends(require_staff), db: Session = Depends(get_db)):
    r = db.get(Report, report_id)
    if not r:
        raise HTTPException(404, "Report not found.")
    apply_report_update(db, r, staff, data)
    db.commit()
    return report_out(r, db)


def _kb_out(k: KnowledgeBase):
    return {"knowledge_id": k.knowledge_id, "claim": k.claim, "verified_fact": k.verified_fact, "source": k.source,
            "category": k.category, "verification_status": k.verification_status,
            "created_at": k.created_at.isoformat(), "updated_at": k.updated_at.isoformat()}


@router.get("/knowledge-base", summary="Search / filter the knowledge base")
def kb_list(q: str | None = None, category: str | None = None, status: str | None = None,
            staff: User = Depends(require_staff), db: Session = Depends(get_db)):
    query = db.query(KnowledgeBase)
    if q:
        query = query.filter(KnowledgeBase.claim.ilike(f"%{q}%") | KnowledgeBase.verified_fact.ilike(f"%{q}%"))
    if category:
        query = query.filter(KnowledgeBase.category == category)
    if status:
        query = query.filter(KnowledgeBase.verification_status == status)
    return [_kb_out(k) for k in query.order_by(KnowledgeBase.knowledge_id).all()]


@router.post("/knowledge-base", status_code=201, summary="Add knowledge")
def kb_add(data: KnowledgeIn, staff: User = Depends(require_staff), db: Session = Depends(get_db)):
    k = KnowledgeBase(**data.model_dump())
    db.add(k)
    log(db, "KB_ADDED", staff.id, data.claim[:100])
    db.commit()
    return _kb_out(k)


@router.put("/knowledge-base/{kid}", summary="Edit knowledge")
def kb_edit(kid: int, data: KnowledgeIn, staff: User = Depends(require_staff), db: Session = Depends(get_db)):
    k = db.get(KnowledgeBase, kid)
    if not k:
        raise HTTPException(404, "Knowledge record not found.")
    for field, value in data.model_dump().items():
        setattr(k, field, value)
    log(db, "KB_EDITED", staff.id, f"id={kid}")
    db.commit()
    return _kb_out(k)


@router.delete("/knowledge-base/{kid}", summary="Delete knowledge")
def kb_delete(kid: int, staff: User = Depends(require_staff), db: Session = Depends(get_db)):
    k = db.get(KnowledgeBase, kid)
    if not k:
        raise HTTPException(404, "Knowledge record not found.")
    db.query(FactVerification).filter(FactVerification.knowledge_id == kid).update({"knowledge_id": None})
    db.delete(k)
    log(db, "KB_DELETED", staff.id, f"id={kid}")
    db.commit()
    return {"message": "Knowledge record deleted."}


@router.get("/analytics", summary="Charts data")
def analytics(staff: User = Depends(require_staff), db: Session = Depends(get_db)):
    risk = Counter(l for (l,) in db.query(Post.risk_level).filter(Post.status != "REMOVED").all())
    reasons = Counter(r for (r,) in db.query(Report.reason).all())
    decisions = Counter(f"{s}:{d}" for s, d in db.query(DecisionLog.source, DecisionLog.decision).all())
    today = datetime.now(timezone.utc).date()
    days = [(today - timedelta(days=i)) for i in range(13, -1, -1)]
    count, total = defaultdict(int), defaultdict(int)
    for created, score in db.query(AIAnalysis.created_at, AIAnalysis.risk_score).all():
        count[created.date()] += 1
        total[created.date()] += score
    return {
        "risk_distribution": [{"label": k, "value": risk.get(k, 0)} for k in ("SAFE", "WARNING", "REVIEW", "HIGH_RISK")],
        "reports_by_category": [{"label": k, "value": v} for k, v in reasons.items()],
        "daily_analysis": [{"label": d.strftime("%d %b"), "value": count[d]} for d in days],
        "fake_news_trend": [{"label": d.strftime("%d %b"), "value": round(total[d] / count[d]) if count[d] else 0} for d in days],
        "decision_stats": [{"label": k, "value": v} for k, v in decisions.items()],
    }


@router.get("/logs", summary="System / audit logs")
def logs(action: str | None = None, staff: User = Depends(require_staff), db: Session = Depends(get_db)):
    q = db.query(ActivityLog)
    if action:
        q = q.filter(ActivityLog.action == action)
    rows = q.order_by(ActivityLog.id.desc()).limit(300).all()
    names = {u.id: u.username for u in db.query(User).all()}
    return [{"id": r.id, "action": r.action, "user": names.get(r.user_id), "detail": r.detail, "ip": r.ip,
             "created_at": r.created_at.isoformat()} for r in rows]


@router.get("/feedback-dataset", summary="AI prediction vs final human decision (CSV with ?format=csv)")
def feedback(format: str = "json", staff: User = Depends(require_staff), db: Session = Depends(get_db)):
    rows = db.query(FeedbackSample).order_by(FeedbackSample.id).all()
    data = [{"post_id": r.post_id, "text": r.text, "ai_label": r.ai_label, "ai_risk_score": r.ai_risk_score,
             "human_decision": r.human_decision, "moderator_id": r.moderator_id} for r in rows]
    if format == "csv":
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=["post_id", "text", "ai_label", "ai_risk_score", "human_decision", "moderator_id"])
        w.writeheader()
        w.writerows(data)
        return Response(buf.getvalue(), media_type="text/csv")
    return data
