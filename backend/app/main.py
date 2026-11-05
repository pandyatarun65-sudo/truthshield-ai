"""TruthShield AI - FastAPI application entry point."""
import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError

from .config import settings
from .database import Base, SessionLocal, engine
from .routers import admin, ai, auth, notifications, posts, reports, users
from .seed import seed

logger = logging.getLogger("truthshield")
DESCRIPTION = """
**TruthShield AI** - academic prototype of a real-time fake-news prevention system.
Posts are analysed (ML + rules + knowledge-base fact check) *before* publication.
AI output is probabilistic; *UNVERIFIED does not mean FALSE*; moderators make the final call.
"""


def init_db(retries: int = 30):
    for attempt in range(retries):
        try:
            Base.metadata.create_all(engine)
            return
        except OperationalError:
            logger.warning("Database not ready (attempt %s/%s)...", attempt + 1, retries)
            time.sleep(2)
    raise RuntimeError("Database unavailable")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if settings.SEED_ON_STARTUP:
        with SessionLocal() as db:
            if seed(db):
                logger.info("Demo data seeded.")
    yield


app = FastAPI(title="TruthShield AI API", description=DESCRIPTION, version="1.0.0", lifespan=lifespan,
              docs_url="/docs", redoc_url="/redoc")

app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in settings.FRONTEND_URL.split(",") if o.strip()],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/api/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

for r in (auth, users, posts, ai, reports, notifications, admin):
    app.include_router(r.router, prefix="/api")


@app.get("/api/health", tags=["System"])
def health():
    return {"status": "ok", "demo_mode": settings.DEMO_MODE}


@app.exception_handler(OperationalError)
async def db_down(request: Request, exc: OperationalError):
    logger.error("Database error: %s", exc)
    return JSONResponse({"detail": "Database is temporarily unavailable. Please try again later."}, status_code=503)


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    logger.exception("Unhandled error")  # stack trace goes to the server log only
    return JSONResponse({"detail": "Something went wrong on our side. Please try again."}, status_code=500)
