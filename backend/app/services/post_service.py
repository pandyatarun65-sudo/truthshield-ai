"""Post pipeline: analyze -> verify -> decide -> store -> notify -> log."""
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import AIAnalysis, Comment, DecisionLog, FactVerification, Like, Post, Report, User
from .activity import log, notify
from .ai_service import run_analysis
from .decision import NOTIFY

PUBLIC_STATUSES = ("PUBLISHED", "WARNING")


def apply_analysis(db: Session, post: Post, text: str, ocr_text=None):
    combined = f"{text}\n{ocr_text}" if ocr_text else text
    r = run_analysis(db, combined)
    post.risk_score, post.risk_level, post.decision, post.status = r["risk_score"], r["risk_level"], r["decision"], r["post_status"]
    if post.analysis:
        db.delete(post.analysis)
        db.query(FactVerification).filter(FactVerification.post_id == post.id).delete()
        db.flush()
    db.add(AIAnalysis(post_id=post.id, fake_probability=r["fake_probability"], real_probability=r["real_probability"],
                      confidence=r["confidence"], credibility=r["credibility"], risk_score=r["risk_score"],
                      risk_level=r["risk_level"], ml_label=r["ml_label"], reasons=r["reasons"],
                      ocr_text=ocr_text, model_version=r["model_version"]))
    f = r["fact"]
    db.add(FactVerification(post_id=post.id, knowledge_id=f["knowledge_id"], status=f["status"],
                            similarity=f["similarity"], explanation=f["explanation"], source=f["source"]))
    db.add(DecisionLog(post_id=post.id, decided_by=None, source="AI", decision=r["decision"],
                       risk_score=r["risk_score"], note=f"fact={f['status']}"))
    return r


def create_post(db: Session, user: User, text, category="General", media_path=None, media_type=None, ocr_text=None):
    post = Post(user_id=user.id, text=text, category=category, media_path=media_path, media_type=media_type, status="PUBLISHED")
    db.add(post)
    db.flush()
    r = apply_analysis(db, post, text, ocr_text)
    ntype, msg = NOTIFY[post.status]
    notify(db, user.id, ntype, msg, post.id)
    log(db, "POST_DECISION", user.id, f"post={post.id} risk={post.risk_score} -> {post.status}")
    db.commit()
    db.refresh(post)
    return post, r


def post_out(db: Session, post: Post, viewer=None, with_analysis=True):
    likes = db.query(func.count(Like.id)).filter(Like.post_id == post.id).scalar()
    comments = db.query(func.count(Comment.id)).filter(Comment.post_id == post.id).scalar()
    liked = bool(viewer and db.query(Like).filter_by(post_id=post.id, user_id=viewer.id).first())
    fv = db.query(FactVerification).filter_by(post_id=post.id).order_by(FactVerification.id.desc()).first()
    out = {
        "id": post.id, "text": post.text, "category": post.category, "status": post.status,
        "media_type": post.media_type, "media_url": f"/api/uploads/{post.media_path}" if post.media_path else None,
        "risk_score": post.risk_score, "risk_level": post.risk_level, "decision": post.decision,
        "created_at": post.created_at.isoformat(), "fact_status": fv.status if fv else None,
        "author": {"id": post.author.id, "username": post.author.username,
                   "photo_url": post.author.photo_url, "trust_score": post.author.trust_score},
        "likes_count": likes, "comments_count": comments, "shares_count": post.shares_count, "liked_by_me": liked,
    }
    if with_analysis and post.analysis:
        a = post.analysis
        out["analysis"] = {"fake_probability": a.fake_probability, "real_probability": a.real_probability,
                           "confidence": a.confidence, "credibility": a.credibility, "risk_score": a.risk_score,
                           "risk_level": a.risk_level, "reasons": a.reasons, "ocr_text": a.ocr_text,
                           "model_version": a.model_version,
                           "fact": {"status": fv.status, "explanation": fv.explanation, "source": fv.source,
                                    "similarity": fv.similarity} if fv else None}
    return out


def user_out(db: Session, u: User):
    return {"id": u.id, "username": u.username, "email": u.email, "role": u.role, "is_active": u.is_active,
            "trust_score": u.trust_score, "photo_url": u.photo_url,
            "post_count": db.query(func.count(Post.id)).filter(Post.user_id == u.id, Post.status != "REMOVED").scalar(),
            "report_count": db.query(func.count(Report.report_id)).filter(Report.user_id == u.id).scalar()}


def adjust_trust(user: User, delta: int):
    user.trust_score = max(0, min(100, user.trust_score + delta))
