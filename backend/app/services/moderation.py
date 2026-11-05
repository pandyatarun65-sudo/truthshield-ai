"""Human moderation actions (approve / block / restore / remove) + feedback dataset."""
from sqlalchemy.orm import Session

from ..models import DecisionLog, FeedbackSample, Post, User
from .activity import log, notify
from .post_service import adjust_trust

ACTIONS = {
    "approve": ("PUBLISHED", "APPROVED", +2, "A moderator reviewed and approved your post."),
    "restore": ("PUBLISHED", "APPROVED", +2, "A moderator restored your post."),
    "block": ("BLOCKED", "BLOCKED", -10, "A moderator blocked your post for violating misinformation guidelines."),
    "remove": ("REMOVED", "REMOVED", -10, "A moderator removed your post."),
}


def apply_post_action(db: Session, post: Post, staff: User, action: str, note: str | None):
    status, human, trust_delta, msg = ACTIONS[action]
    post.status = status
    post.decision = f"HUMAN_{action.upper()}"
    db.add(DecisionLog(post_id=post.id, decided_by=staff.id, source="HUMAN", decision=action.upper(),
                       risk_score=post.risk_score, note=note))
    if post.analysis:  # feedback dataset: AI prediction vs final human decision (manual retraining later)
        db.add(FeedbackSample(post_id=post.id, text=post.text, ai_label=post.analysis.ml_label,
                              ai_risk_score=post.risk_score, human_decision=human, moderator_id=staff.id))
    adjust_trust(post.author, trust_delta)
    notify(db, post.user_id, "ADMIN_DECISION", msg + (f" Note: {note}" if note else ""), post.id)
    log(db, "ADMIN_POST_ACTION", staff.id, f"post={post.id} action={action}")
