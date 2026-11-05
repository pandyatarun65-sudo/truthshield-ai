"""Idempotent demo seed. Runs only when the users table is empty."""
from .models import Comment, KnowledgeBase, Like, Post, Report, User
from .security import hash_password
from .seed_data import KNOWLEDGE, POSTS, USERS
from .services.activity import notify
from .services.post_service import create_post


def seed(db):
    if db.query(User).count():
        return False
    for u, e, p, r in USERS:
        db.add(User(username=u, email=e, password_hash=hash_password(p), role=r))
    for claim, fact, src, cat, status in KNOWLEDGE:
        db.add(KnowledgeBase(claim=claim, verified_fact=fact, source=src, category=cat, verification_status=status))
    db.commit()
    users = {u.username: u for u in db.query(User).all()}
    posts = []
    for author, cat, text in POSTS:
        post, _ = create_post(db, users[author], text, cat)
        posts.append(post)
    public = [p for p in posts if p.status in ("PUBLISHED", "WARNING")]
    for i, p in enumerate(public):  # a few likes / comments
        for name in ("alice", "bob", "carol")[: (i % 3) + 1]:
            if users[name].id != p.user_id:
                db.add(Like(post_id=p.id, user_id=users[name].id))
    if public:
        db.add(Comment(post_id=public[0].id, user_id=users["bob"].id, text="Thanks for sharing this update."))
        db.add(Comment(post_id=public[-1].id, user_id=users["carol"].id, text="Interesting, where can I read the paper?"))
    flagged = [p for p in posts if p.status in ("WARNING", "UNDER_REVIEW", "BLOCKED")]
    reasons = ["Fake News", "Misleading Information", "Fake News"]
    reporters = ["bob", "alice", "carol"]
    for i, p in enumerate(flagged[:3]):
        r = Report(post_id=p.id, user_id=users[reporters[i]].id, reason=reasons[i],
                   description="Demo report: this claim looks incorrect.")
        if i == 2:
            r.status, r.reviewed_by, r.resolution_note = "RESOLVED", users["moderator"].id, "Checked against the knowledge base."
            notify(db, r.user_id, "REPORT_RESOLVED", "Your report was resolved by a moderator.", p.id)
        db.add(r)
    db.commit()
    return True
