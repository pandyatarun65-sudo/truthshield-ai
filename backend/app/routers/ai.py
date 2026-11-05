from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ai.fact_check import verify_claim

from ..config import settings
from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..schemas import AnalyzeIn, VerifyIn
from ..services.ai_service import kb_items, run_analysis

router = APIRouter(tags=["AI & Fact Verification"])


@router.post("/ai/analyze", summary="Preview the AI analysis of a text (nothing is stored)")
def analyze_text(data: AnalyzeIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return run_analysis(db, data.text)


@router.post("/verification/check", summary="Check a claim against the knowledge base")
def check_claim(data: VerifyIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return verify_claim(data.claim, kb_items(db), settings.FACT_MATCH_THRESHOLD, settings.external_api_key)
