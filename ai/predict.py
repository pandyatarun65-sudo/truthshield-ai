"""Prediction wrapper. Returns label, fake_probability, real_probability, confidence."""
import joblib
from pathlib import Path

from .preprocessing import clean_text  # noqa: F401  (needed to unpickle the pipeline)

MODEL_PATH = Path(__file__).resolve().parent / "model" / "model.joblib"
_cache = {}
DISCLAIMER = "Academic prototype: probabilistic prediction, not a verified fact-check."


def load_model():
    if "m" not in _cache:
        if not MODEL_PATH.exists():
            from .train import train
            train(verbose=False)
        _cache["m"] = joblib.load(MODEL_PATH)
    return _cache["m"]


def predict(text: str) -> dict:
    try:
        m = load_model()
        fake = float(m["pipeline"].predict_proba([text or ""])[0][1])
        return {"label": "fake" if fake >= 0.5 else "real", "fake_probability": round(fake, 4),
                "real_probability": round(1 - fake, 4), "confidence": round(max(fake, 1 - fake), 4),
                "model_available": True, "model_version": m["version"], "disclaimer": DISCLAIMER}
    except Exception:  # AI model unavailable -> neutral result, never crash the API
        return {"label": "unknown", "fake_probability": 0.5, "real_probability": 0.5,
                "confidence": 0.0, "model_available": False, "model_version": "unavailable",
                "disclaimer": DISCLAIMER}
