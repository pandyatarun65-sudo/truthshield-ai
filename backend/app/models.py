"""SQLAlchemy models (PostgreSQL). Admin/moderator accounts are users with role admin/moderator."""
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user")  # user | moderator | admin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    trust_score: Mapped[int] = mapped_column(Integer, default=80)
    photo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    text: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50), default="General")
    media_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    media_type: Mapped[str | None] = mapped_column(String(10), nullable=True)
    status: Mapped[str] = mapped_column(String(20), index=True)  # PUBLISHED|WARNING|UNDER_REVIEW|BLOCKED|REMOVED
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    risk_level: Mapped[str] = mapped_column(String(20), default="SAFE")
    decision: Mapped[str] = mapped_column(String(30), default="PUBLISH")
    shares_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    author = relationship("User")
    analysis = relationship("AIAnalysis", uselist=False, back_populates="post")


class AIAnalysis(Base):
    __tablename__ = "ai_analysis"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), unique=True)
    fake_probability: Mapped[float] = mapped_column(Float)
    real_probability: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    credibility: Mapped[float] = mapped_column(Float)
    risk_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(20))
    ml_label: Mapped[str] = mapped_column(String(10))
    reasons: Mapped[list] = mapped_column(JSON)
    ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_version: Mapped[str] = mapped_column(String(60))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    post = relationship("Post", back_populates="analysis")


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    knowledge_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim: Mapped[str] = mapped_column(Text)
    verified_fact: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(50), index=True)
    verification_status: Mapped[str] = mapped_column(String(15))  # TRUE | FALSE | MISLEADING
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class FactVerification(Base):
    __tablename__ = "fact_verifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    knowledge_id: Mapped[int | None] = mapped_column(ForeignKey("knowledge_base.knowledge_id"), nullable=True)
    status: Mapped[str] = mapped_column(String(15))  # TRUE|FALSE|MISLEADING|UNVERIFIED
    similarity: Mapped[float] = mapped_column(Float, default=0.0)
    explanation: Mapped[str] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Report(Base):
    __tablename__ = "reports"
    report_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    reason: Mapped[str] = mapped_column(String(40))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(15), default="PENDING")  # PENDING|UNDER_REVIEW|RESOLVED|REJECTED
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    post_id: Mapped[int | None] = mapped_column(ForeignKey("posts.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(30))
    message: Mapped[str] = mapped_column(String(300))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class DecisionLog(Base):
    __tablename__ = "decision_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    decided_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)  # null = AI
    source: Mapped[str] = mapped_column(String(10))  # AI | HUMAN
    decision: Mapped[str] = mapped_column(String(30))
    risk_score: Mapped[int] = mapped_column(Integer)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    author = relationship("User")


class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_like"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(40), index=True)
    detail: Mapped[str | None] = mapped_column(String(300), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class FeedbackSample(Base):
    """Feedback dataset: AI prediction vs final human decision (for controlled, manual retraining)."""
    __tablename__ = "feedback_dataset"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    text: Mapped[str] = mapped_column(Text)
    ai_label: Mapped[str] = mapped_column(String(10))
    ai_risk_score: Mapped[int] = mapped_column(Integer)
    human_decision: Mapped[str] = mapped_column(String(20))
    moderator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
