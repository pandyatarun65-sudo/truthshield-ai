"""AI module tests. Run from the repo root:  python -m pytest tests/test_ai.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai.analyzer import analyze  # noqa: E402
from ai.fact_check import verify_claim  # noqa: E402
from ai.predict import predict  # noqa: E402
from ai.preprocessing import clean_text, heuristic_score  # noqa: E402

KB = [
    {"knowledge_id": 1, "claim": "Vaccines cause autism in children", "verified_fact": "No link found.", "source": "WHO", "verification_status": "FALSE"},
    {"knowledge_id": 2, "claim": "Regular handwashing reduces the spread of infectious diseases", "verified_fact": "Proven.", "source": "WHO", "verification_status": "TRUE"},
]


def test_clean_text():
    assert clean_text("Visit https://x.com NOW!!") == "visit now!!"


def test_predict_shape():
    p = predict("SHOCKING miracle cure doctors hate, share before it's deleted!!!")
    assert set(["label", "fake_probability", "real_probability", "confidence"]) <= set(p)
    assert abs(p["fake_probability"] + p["real_probability"] - 1) < 1e-6
    assert p["fake_probability"] > predict("The city council approved the budget on Tuesday, according to minutes.")["fake_probability"]


def test_heuristics_explain():
    score, reasons = heuristic_score("URGENT!!! SHOCKING secret exposed, forward this to everyone!!!")
    assert score > 0.4 and reasons


def test_fact_verification_statuses():
    assert verify_claim("Vaccines cause autism in children", KB)["status"] == "FALSE"
    assert verify_claim("Handwashing reduces spread of infectious diseases", KB)["status"] == "TRUE"
    unknown = verify_claim("My neighbour bought a red bicycle", KB)
    assert unknown["status"] == "UNVERIFIED"  # never auto-FALSE


def test_negated_claim_goes_to_human():
    assert verify_claim("Vaccines do not cause autism in children", KB)["status"] == "UNVERIFIED"


def test_analyzer_risk_ordering():
    safe = analyze("The education board released the exam timetable, according to an official statement.", KB)
    bad = analyze("SHOCKING EXPOSED: Vaccines cause autism in children, wake up and share before it's deleted!!!", KB)
    assert bad["risk_score"] > safe["risk_score"] and bad["reasons"] and safe["risk_score"] <= 40
