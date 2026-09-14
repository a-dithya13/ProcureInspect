from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.cases import CASE_EAGER_LOAD, build_case_summary
from database.db import get_db
from models.orm import Award, Bid, CaseTender, InvestigationCase, Tender
from models.schemas import TenderDetailOut, TenderOwnerSignalOut, TenderWithOwnerOut
from services.entity_signals import aggregate_entity_signals

router = APIRouter(prefix="/api", tags=["tenders"])


def _with_owner_signal(tender: Tender, owner_signals: dict) -> TenderWithOwnerOut:
    rollup = owner_signals.get(tender.department)
    return TenderWithOwnerOut(
        id=tender.id, title=tender.title, department=tender.department, category=tender.category,
        location=tender.location, estimated_value=tender.estimated_value, date=tender.date,
        owner_signal=TenderOwnerSignalOut(
            name=tender.department,
            tag=rollup["tag"],
            case_count=rollup["case_count"],
            signal_count=rollup["signal_count"],
            high_signal_count=rollup["high_signal_count"],
        ) if rollup else None,
    )


@router.get("/tenders", response_model=list[TenderWithOwnerOut])
def list_tenders(db: Session = Depends(get_db)):
    owner_signals = aggregate_entity_signals(db)
    tenders = db.query(Tender).order_by(Tender.date.desc()).all()
    return [_with_owner_signal(t, owner_signals) for t in tenders]


@router.get("/tenders/{tender_id}", response_model=TenderDetailOut)
def get_tender(tender_id: str, db: Session = Depends(get_db)):
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail=f"Tender {tender_id} not found")

    owner_signals = aggregate_entity_signals(db)
    bids = db.query(Bid).filter(Bid.tender_id == tender_id).order_by(Bid.rank).all()
    award = db.query(Award).filter(Award.tender_id == tender_id).first()

    related_cases = (
        db.query(InvestigationCase)
        .join(CaseTender, CaseTender.case_id == InvestigationCase.id)
        .filter(CaseTender.tender_id == tender_id)
        .options(*CASE_EAGER_LOAD)
        .order_by(InvestigationCase.score.desc())
        .all()
    )

    return TenderDetailOut(
        tender=_with_owner_signal(tender, owner_signals),
        bids=bids,
        award=award,
        cases=[build_case_summary(c) for c in related_cases],
    )
