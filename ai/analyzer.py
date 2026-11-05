"""Combines ML + heuristics + fact verification into one explainable risk result."""
from .fact_check import verify_claim
from .predict import predict
from .preprocessing import heuristic_score

FACT_RISK = {"TRUE": 0.0, "UNVERIFIED": 0.3, "MISLEADING": 0.7, "FALSE": 1.0}


def analyze(text, kb_items, fact_threshold=0.35, api_key=None):
    ml = predict(text)
    heur, heur_reasons = heuristic_score(text)
    fact = verify_claim(text, kb_items, fact_threshold, api_key)
    fact_risk = FACT_RISK[fact["status"]]
    ml_part = ml["fake_probability"] if ml["model_available"] else 0.5
    risk = round(100 * (0.45 * ml_part + 0.35 * fact_risk + 0.20 * heur))
    if fact["status"] == "FALSE" and fact["similarity"] >= fact_threshold:
        risk = max(risk, 65)  # a known-false claim always needs at least moderator review
    if fact["status"] == "TRUE":
        risk = min(risk, 40)
    risk = max(0, min(100, risk))

    reasons = []
    if ml["model_available"]:
        if ml["fake_probability"] >= 0.5:
            reasons.append(f"ML model: language resembles known misinformation ({ml['fake_probability']:.0%} fake probability)")
        else:
            reasons.append(f"ML model: language resembles normal reporting ({ml['real_probability']:.0%} real probability)")
    else:
        reasons.append("AI model unavailable: score uses fact-check and rule signals only")
    if fact["status"] in ("FALSE", "MISLEADING"):
        reasons.append(f"Fact check: {fact['status']}. {fact['explanation']}")
    elif fact["status"] == "TRUE":
        reasons.append(f"Fact check: TRUE. {fact['explanation']}")
    else:
        reasons.append("Fact check: UNVERIFIED. " + fact["explanation"])
    reasons += heur_reasons
    return {
        "fake_probability": round(ml_part * 100, 1), "real_probability": round((1 - ml_part) * 100, 1),
        "confidence": round(ml["confidence"] * 100, 1), "credibility": float(100 - risk),
        "risk_score": risk, "ml_label": ml["label"], "reasons": reasons, "fact": fact,
        "model_version": ml["model_version"], "disclaimer": ml["disclaimer"],
    }
