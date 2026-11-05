"""Central configuration, read from environment variables (never hard-code secrets)."""
import os
from pathlib import Path

try:  # optional: load variables from the repo-level .env file (real env vars always win)
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass


def _bool(name, default):
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


class Settings:
    def __init__(self):
        url = os.getenv("DATABASE_URL") or "postgresql+psycopg2://truthshield:truthshield@localhost:5432/truthshield"
        # Render / Neon / Heroku give postgres:// or postgresql:// URLs; SQLAlchemy needs the driver name.
        for prefix in ("postgres://", "postgresql://"):
            if url.startswith(prefix):
                url = "postgresql+psycopg2://" + url[len(prefix):]
        self.DATABASE_URL = url
        self.JWT_SECRET = os.getenv("JWT_SECRET") or "change-me-in-production"  # set a real one in .env!
        self.JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "120"))
        self.FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
        self.DEMO_MODE = _bool("DEMO_MODE", True)
        self.SEED_ON_STARTUP = _bool("SEED_ON_STARTUP", True)
        self.FACT_CHECK_API_KEY = os.getenv("FACT_CHECK_API_KEY", "")
        self.FACT_MATCH_THRESHOLD = float(os.getenv("FACT_MATCH_THRESHOLD", "0.35"))
        # Decision thresholds (upper bounds, inclusive) - configurable
        self.SAFE_MAX = int(os.getenv("SAFE_MAX", "30"))
        self.WARNING_MAX = int(os.getenv("WARNING_MAX", "60"))
        self.REVIEW_MAX = int(os.getenv("REVIEW_MAX", "80"))
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
        self.MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
        self.RATE_LIMIT_ENABLED = _bool("RATE_LIMIT_ENABLED", True)

    @property
    def external_api_key(self):
        """External fact-check API is used only when NOT in demo mode and a key exists."""
        return None if self.DEMO_MODE or not self.FACT_CHECK_API_KEY else self.FACT_CHECK_API_KEY


settings = Settings()
