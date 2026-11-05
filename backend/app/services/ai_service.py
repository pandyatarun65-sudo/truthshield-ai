"""Glue between the database and the ai/ package."""
from sqlalchemy.orm import Session

from ai.analyzer import analyze

from ..config import settings
from ..models import KnowledgeBase
from .decision import decide


def kb_items(db: Session):
    return [dict(knowledge_id=k.knowledge_id, claim=k.claim, verified_fact=k.verified_fact,
                 source=k.source, verification_status=k.verification_status)
            for k in db.query(KnowledgeBase).all()]


def run_analysis(db: Session, text: str):
    """Returns the analysis dict plus risk_level/decision/status from the decision engine."""
    result = analyze(text, kb_items(db), settings.FACT_MATCH_THRESHOLD, settings.external_api_key)
    level, decision, status = decide(result["risk_score"])
    result.update(risk_level=level, decision=decision, post_status=status)
    return result
