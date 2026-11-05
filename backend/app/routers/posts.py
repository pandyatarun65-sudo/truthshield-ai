from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, get_optional_user
from ..models import Comment, Like, Post, User
from ..schemas import CATEGORIES, CommentIn, PostUpdate
from ..security import post_limiter
from ..services.activity import log
from ..services.media_service import save_upload
from ..services.post_service import PUBLIC_STATUSES, apply_analysis, create_post, post_out

router = APIRouter(tags=["Posts"])


def _visible(post: Post | None, viewer: User | None) -> Post:
    if not post or post.status == "REMOVED" and not (viewer and viewer.role in ("admin", "moderator")):
        raise HTTPException(404, "Post not found.")
    if post.status in PUBLIC_STATUSES:
        return post
    if viewer and (viewer.id == post.user_id or viewer.role in ("admin", "moderator")):
        return post
    raise HTTPException(404, "Post not found.")


def _public_post(db: Session, post_id: int) -> Post:
    post = db.get(Post, post_id)
    if not post or post.status not in PUBLIC_STATUSES:
        raise HTTPException(404, "Post not found.")
    return post


@router.post("/posts", status_code=201, dependencies=[Depends(post_limiter)],
             summary="Create a post. The post is analysed by TruthShield AI before it becomes visible.")
async def create(text: str = Form(...), category: str = Form("General"), file: UploadFile | None = File(None),
                 user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    text = text.strip()
    if not text or len(text) > 5000:
        raise HTTPException(422, "Post text must be between 1 and 5000 characters.")
    if category not in CATEGORIES:
        category = "General"
    media_name = media_type = ocr = None
    if file is not None and file.filename:
        media_name, media_type, ocr = await save_upload(file)
    post, _ = create_post(db, user, text, category, media_name, media_type, ocr)
    return post_out(db, post, user)


@router.get("/posts", summary="List / search posts")
def list_posts(q: str | None = None, category: str | None = None, mine: bool = False,
               skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=50),
               user: User | None = Depends(get_optional_user), db: Session = Depends(get_db)):
    query = db.query(Post)
    if mine:
        if not user:
            raise HTTPException(401, "Not authenticated. Please log in.")
        query = query.filter(Post.user_id == user.id, Post.status != "REMOVED")
    else:
        query = query.filter(Post.status.in_(PUBLIC_STATUSES))
    if q:
        query = query.filter(Post.text.ilike(f"%{q}%"))
    if category:
        query = query.filter(Post.category == category)
    posts = query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    return [post_out(db, p, user, with_analysis=False) for p in posts]


@router.get("/posts/{post_id}", summary="Post details including the AI analysis")
def get_post(post_id: int, user: User | None = Depends(get_optional_user), db: Session = Depends(get_db)):
    return post_out(db, _visible(db.get(Post, post_id), user), user)


@router.put("/posts/{post_id}", summary="Edit own post (it is re-analysed)")
def update_post(post_id: int, data: PostUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post or post.status == "REMOVED":
        raise HTTPException(404, "Post not found.")
    if post.user_id != user.id:
        raise HTTPException(403, "You can only edit your own posts.")
    post.text = data.text.strip()
    if data.category in CATEGORIES:
        post.category = data.category
    apply_analysis(db, post, post.text, post.analysis.ocr_text if post.analysis else None)
    log(db, "POST_EDITED", user.id, f"post={post.id}")
    db.commit()
    return post_out(db, post, user)


@router.delete("/posts/{post_id}", summary="Delete a post (soft delete)")
def delete_post(post_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post or post.status == "REMOVED":
        raise HTTPException(404, "Post not found.")
    if post.user_id != user.id and user.role not in ("admin", "moderator"):
        raise HTTPException(403, "You can only delete your own posts.")
    post.status = "REMOVED"  # soft delete keeps the audit trail
    log(db, "POST_DELETED", user.id, f"post={post.id}")
    db.commit()
    return {"message": "Post deleted."}


@router.post("/posts/{post_id}/like", summary="Toggle like")
def toggle_like(post_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _public_post(db, post_id)
    existing = db.query(Like).filter_by(post_id=post_id, user_id=user.id).first()
    if existing:
        db.delete(existing)
    else:
        db.add(Like(post_id=post_id, user_id=user.id))
    db.commit()
    return {"liked": not existing, "likes_count": db.query(Like).filter_by(post_id=post_id).count()}


@router.get("/posts/{post_id}/comments", summary="List comments")
def list_comments(post_id: int, user: User | None = Depends(get_optional_user), db: Session = Depends(get_db)):
    _visible(db.get(Post, post_id), user)
    rows = db.query(Comment).filter_by(post_id=post_id).order_by(Comment.created_at).all()
    return [{"id": c.id, "text": c.text, "username": c.author.username, "created_at": c.created_at.isoformat()} for c in rows]


@router.post("/posts/{post_id}/comments", status_code=201, summary="Add a comment")
def add_comment(post_id: int, data: CommentIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _public_post(db, post_id)
    c = Comment(post_id=post_id, user_id=user.id, text=data.text.strip())
    db.add(c)
    db.commit()
    return {"id": c.id, "text": c.text, "username": user.username, "created_at": c.created_at.isoformat()}


@router.post("/posts/{post_id}/share", summary="Share (simulation: increments a counter)")
def share(post_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = _public_post(db, post_id)
    post.shares_count += 1
    db.commit()
    return {"shares_count": post.shares_count}
