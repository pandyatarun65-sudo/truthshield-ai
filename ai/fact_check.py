"""Fact verification against an internal knowledge base (+ optional external API)."""
import json
import urllib.parse
import urllib.request

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .preprocessing import clean_text, has_negation


def _unverified(msg, sim=0.0):
    return {"status": "UNVERIFIED", "explanation": msg, "similarity": round(float(sim), 3),
            "knowledge_id": None, "source": None, "verified_fact": None}


def external_lookup(text: str, api_key: str):
    """Optional Google Fact Check Tools API lookup. Returns dict or None."""
    try:
        url = ("https://factchecktools.googleapis.com/v1alpha1/claims:search?"
               + urllib.parse.urlencode({"query": text[:200], "key": api_key, "languageCode": "en"}))
        with urllib.request.urlopen(url, timeout=6) as r:
            data = json.loads(r.read().decode())
        claims = data.get("claims") or []
        if not claims:
            return None
        review = claims[0]["claimReview"][0]
        rating = review.get("textualRating", "").lower()
        if any(w in rating for w in ("false", "fake", "incorrect", "pants")):
            status = "FALSE"
        elif any(w in rating for w in ("misleading", "partly", "mixture", "half", "context")):
            status = "MISLEADING"
        elif any(w in rating for w in ("true", "correct", "accurate")):
            status = "TRUE"
        else:
            return None
        publisher = review.get("publisher", {}).get("name", "external fact-checker")
        return {"status": status, "similarity": 1.0, "knowledge_id": None, "source": publisher,
                "verified_fact": review.get("title"),
                "explanation": f"External fact-check ({publisher}) rated a similar claim: {rating}."}
    except Exception:
        return None


def verify_claim(text, kb_items, threshold=0.35, api_key=None):
    """kb_items: list of dicts (knowledge_id, claim, verified_fact, source, verification_status)."""
    if not (text or "").strip():
        return _unverified("No text to verify.")
    best = None
    if kb_items:
        try:
            vec = TfidfVectorizer(stop_words="english", preprocessor=clean_text)
            mat = vec.fit_transform([k["claim"] for k in kb_items] + [text])
            sims = cosine_similarity(mat[-1], mat[:-1])[0]
            i = int(sims.argmax())
            best = (kb_items[i], float(sims[i]))
        except ValueError:  # empty vocabulary
            best = None
    if best and best[1] >= threshold:
        kb, sim = best
        if has_negation(text) != has_negation(kb["claim"]):
            return _unverified("The post resembles a known claim but its wording seems to "
                               "contradict or negate it, so a human should review it.", sim)
        return {"status": kb["verification_status"], "similarity": round(sim, 3),
                "knowledge_id": kb["knowledge_id"], "source": kb.get("source"),
                "verified_fact": kb.get("verified_fact"),
                "explanation": f"Matches a known claim in the knowledge base "
                               f"(similarity {sim:.0%}): {kb['verified_fact']}"}
    if api_key:
        ext = external_lookup(text, api_key)
        if ext:
            return ext
    return _unverified("No reliable source found for this claim. 'Unverified' does not mean "
                       "the claim is false.", best[1] if best else 0.0)
