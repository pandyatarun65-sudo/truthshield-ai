"""Pydantic request/response schemas (validation + OpenAPI docs)."""
from typing import Literal

from pydantic import BaseModel, Field

CATEGORIES = ["General", "Health", "Science", "Technology", "Politics", "Sports", "Education", "Environment", "Entertainment"]
REPORT_REASONS = ["Fake News", "Misleading Information", "Spam", "Hate Speech", "Manipulated Media", "Other"]


class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=30, pattern=r"^[A-Za-z0-9_]+$")
    email: str = Field(max_length=120, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=72)


class LoginIn(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    trust_score: int
    photo_url: str | None = None
    post_count: int = 0
    report_count: int = 0


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=30, pattern=r"^[A-Za-z0-9_]+$")


class AnalyzeIn(BaseModel):
    text: str = Field(min_length=1, max_length=5000)


class VerifyIn(BaseModel):
    claim: str = Field(min_length=3, max_length=2000)


class PostUpdate(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    category: str | None = None


class CommentIn(BaseModel):
    text: str = Field(min_length=1, max_length=500)


class ReportIn(BaseModel):
    post_id: int
    reason: Literal["Fake News", "Misleading Information", "Spam", "Hate Speech", "Manipulated Media", "Other"]
    description: str | None = Field(default=None, max_length=1000)


class ReportUpdate(BaseModel):
    status: Literal["PENDING", "UNDER_REVIEW", "RESOLVED", "REJECTED"]
    resolution_note: str | None = Field(default=None, max_length=1000)


class PostAction(BaseModel):
    action: Literal["approve", "block", "restore", "remove"]
    note: str | None = Field(default=None, max_length=1000)


class UserStatusIn(BaseModel):
    is_active: bool


class KnowledgeIn(BaseModel):
    claim: str = Field(min_length=3, max_length=1000)
    verified_fact: str = Field(min_length=3, max_length=2000)
    source: str = Field(min_length=2, max_length=200)
    category: str = Field(min_length=2, max_length=50)
    verification_status: Literal["TRUE", "FALSE", "MISLEADING"]
