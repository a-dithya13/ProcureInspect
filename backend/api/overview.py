from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.db import get_db
from models.orm import AnalysisRun, Award, Bid, InvestigationCase, RiskSignal, Tender, Vendor
from models.schemas import OverviewOut, PriorityDistribution

router = APIRouter(prefix="/api", tags=["overview"])


@router.get("/overview", response_model=OverviewOut)
def get_overview(db: Session = Depends(get_db)):
    priority_counts = dict(
        db.query(InvestigationCase.priority, func.count(InvestigationCase.id))
        .group_by(InvestigationCase.priority)
        .all()
    )

    last_run = db.query(AnalysisRun).order_by(AnalysisRun.run_at.desc()).first()

    return OverviewOut(
        total_tenders=db.query(func.count(Tender.id)).scalar() or 0,
        total_vendors=db.query(func.count(Vendor.id)).scalar() or 0,
        total_bids=db.query(func.count(Bid.id)).scalar() or 0,
        total_awards=db.query(func.count(Award.id)).scalar() or 0,
        total_signals=db.query(func.count(RiskSignal.id)).scalar() or 0,
        total_cases=db.query(func.count(InvestigationCase.id)).scalar() or 0,
        priority_distribution=PriorityDistribution(
            HIGH=priority_counts.get("HIGH", 0),
            MEDIUM=priority_counts.get("MEDIUM", 0),
            LOW=priority_counts.get("LOW", 0),
        ),
        last_analysis_run=last_run.run_at.isoformat() if last_run else None,
    )
