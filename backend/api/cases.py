import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from graph.procurement_graph import build_case_graph
from models.orm import Award, Bid, InvestigationCase, RiskSignal, Tender, Vendor
from models.schemas import CaseDetailOut, CaseSummaryOut, RiskSignalOut, TenderOut, VendorOut

router = APIRouter(prefix="/api", tags=["cases"])


def build_case_summary(case: InvestigationCase, vendors_by_id: dict, signals_by_id: dict) -> CaseSummaryOut:
    vendor_names = [vendors_by_id[v].name for v in case.vendor_ids if v in vendors_by_id]
    signal_types = sorted({
        signals_by_id[s].signal_type for s in case.signal_ids if s in signals_by_id
    })
    return CaseSummaryOut(
        id=case.id,
        priority=case.priority,
        score=case.score,
        status=case.status,
        vendor_ids=case.vendor_ids,
        tender_ids=case.tender_ids,
        signal_ids=case.signal_ids,
        signal_types=signal_types,
        vendor_names=vendor_names,
        explanation=case.explanation,
    )


@router.get("/cases", response_model=list[CaseSummaryOut])
def list_cases(db: Session = Depends(get_db)):
    cases = db.query(InvestigationCase).order_by(InvestigationCase.score.desc()).all()
    vendors_by_id = {v.id: v for v in db.query(Vendor).all()}
    signals_by_id = {s.id: s for s in db.query(RiskSignal).all()}
    return [build_case_summary(c, vendors_by_id, signals_by_id) for c in cases]


@router.get("/cases/{case_id}", response_model=CaseDetailOut)
def get_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(InvestigationCase).filter(InvestigationCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    vendors = db.query(Vendor).filter(Vendor.id.in_(case.vendor_ids)).all()
    tenders = db.query(Tender).filter(Tender.id.in_(case.tender_ids)).all()
    signals = db.query(RiskSignal).filter(RiskSignal.id.in_(case.signal_ids)).all()

    all_vendors = db.query(Vendor).all()
    all_tenders = db.query(Tender).all()
    all_bids = db.query(Bid).all()
    all_awards = db.query(Award).all()

    graph = build_case_graph(
        case.vendor_ids,
        case.tender_ids,
        pd.DataFrame([{"id": v.id, "name": v.name, "category": v.category, "location": v.location} for v in all_vendors]),
        pd.DataFrame([
            {
                "id": t.id, "title": t.title, "department": t.department, "category": t.category,
                "location": t.location, "estimated_value": t.estimated_value, "date": t.date,
            } for t in all_tenders
        ]),
        pd.DataFrame([
            {"id": b.id, "tender_id": b.tender_id, "vendor_id": b.vendor_id, "amount": b.amount, "rank": b.rank}
            for b in all_bids
        ]),
        pd.DataFrame([
            {"id": a.id, "tender_id": a.tender_id, "vendor_id": a.vendor_id, "amount": a.amount, "award_date": a.award_date}
            for a in all_awards
        ]),
    )

    return CaseDetailOut(
        id=case.id,
        priority=case.priority,
        score=case.score,
        status=case.status,
        vendors=[VendorOut.model_validate(v) for v in vendors],
        tenders=[TenderOut.model_validate(t) for t in tenders],
        signals=[RiskSignalOut.model_validate(s) for s in signals],
        explanation=case.explanation,
        evidence=case.evidence,
        recommended_investigation=case.recommended_investigation,
        graph=graph,
    )
