from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db import get_db
from models.schemas import AnalyzeResultOut, PriorityDistribution
from services.analysis_service import run_analysis

router = APIRouter(prefix="/api", tags=["analyze"])


@router.post("/analyze", response_model=AnalyzeResultOut)
def analyze(db: Session = Depends(get_db)):
    result = run_analysis(db)
    return AnalyzeResultOut(
        signals_detected=result["signals_detected"],
        cases_created=result["cases_created"],
        priority_distribution=PriorityDistribution(**result["priority_distribution"]),
        duration_seconds=result["duration_seconds"],
    )
