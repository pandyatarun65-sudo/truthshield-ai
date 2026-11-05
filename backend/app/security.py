import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import HTTPException, Request

from .config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode()[:72], bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode()[:72], hashed.encode())
    except ValueError:
        return False


def create_token(user) -> str:
    payload = {"sub": str(user.id), "role": user.role,
               "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])


class RateLimiter:
    """Very small in-memory sliding-window limiter (per IP + path). Fine for a prototype."""

    def __init__(self, limit: int, window_seconds: int):
        self.limit, self.window, self.hits = limit, window_seconds, defaultdict(deque)

    def __call__(self, request: Request):
        if not settings.RATE_LIMIT_ENABLED:
            return
        key = f"{request.client.host if request.client else 'x'}:{request.url.path}"
        now, q = time.time(), self.hits[key]
        while q and now - q[0] > self.window:
            q.popleft()
        if len(q) >= self.limit:
            raise HTTPException(429, "Too many requests. Please slow down and try again shortly.")
        q.append(now)


auth_limiter = RateLimiter(20, 60)
post_limiter = RateLimiter(30, 60)
