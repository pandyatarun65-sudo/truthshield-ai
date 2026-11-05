"""Text preprocessing and simple rule-based (heuristic) signals."""
import re

URL_RE = re.compile(r"https?://\S+|www\.\S+")
CLICKBAIT = [
    "you won't believe", "doctors hate", "shocking", "what they don't want you to know",
    "share before", "before it's deleted", "before it is deleted", "miracle cure",
    "100% guaranteed", "100% proven", "wake up", "they are hiding", "they're hiding",
    "going viral", "forward this", "share this with everyone", "exposed", "secret cure",
    "doctors don't want", "urgent:", "breaking:",
]
VAGUE_SOURCES = ["my cousin", "a friend who works", "insiders say", "people are saying",
                 "sources say", "i heard that", "everyone knows", "a whatsapp message"]
CONSPIRACY = ["hoax", "cover-up", "cover up", "mainstream media won't", "big pharma",
              "deep state", "new world order", "microchip", "crisis actor"]
CREDIBLE = ["according to", "published in", "peer-reviewed", "official statement",
            "ministry of", "reuters", "world health organization", "press conference"]
NEGATIONS = {"not", "no", "never", "cannot", "without", "none"}


def clean_text(text: str) -> str:
    """Lower-case, strip URLs, keep letters/digits/basic punctuation."""
    text = URL_RE.sub(" ", (text or "").lower())
    text = re.sub(r"[^a-z0-9!?'\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def has_negation(text: str) -> bool:
    words = re.findall(r"[a-z']+", (text or "").lower())
    return any(w in NEGATIONS or w.endswith("n't") for w in words)


def heuristic_score(text: str):
    """Return (score 0..1, reasons[]) from transparent rules (explainability)."""
    raw = text or ""
    low = raw.lower()
    score, reasons = 0.0, []
    letters = [c for c in raw if c.isalpha()]
    if len(letters) > 20 and sum(c.isupper() for c in letters) / len(letters) > 0.3:
        score += 0.25
        reasons.append("Excessive capital letters (sensational style)")
    if raw.count("!") >= 3:
        score += 0.2
        reasons.append("Excessive exclamation marks")
    hits = [p for p in CLICKBAIT if p in low]
    if hits:
        score += min(0.5, 0.2 * len(hits))
        reasons.append("Clickbait / urgency language detected: " + ", ".join(hits[:3]))
    if any(p in low for p in VAGUE_SOURCES):
        score += 0.15
        reasons.append("Vague or unverifiable attribution (no named source)")
    if any(p in low for p in CONSPIRACY):
        score += 0.2
        reasons.append("Conspiracy-style wording detected")
    if any(p in low for p in CREDIBLE):
        score = max(0.0, score - 0.2)
    return min(1.0, score), reasons
