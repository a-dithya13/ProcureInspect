from collections import Counter

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from database.db import get_db
from graph.procurement_graph import build_case_graph
from models.orm import Award, Bid, InvestigationCase, RiskSignal, Tender, Vendor
from models.schemas import (
    CaseDetailOut,
    CaseSummaryOut,
    RiskSignalOut,
    TenderWithOwnerOut,
    VendorOut,
)
from services.entity_signals import aggregate_entity_signals

router = APIRouter(prefix="/api", tags=["cases"])

CASE_EAGER_LOAD = (
    selectinload(InvestigationCase.vendors),
    selectinload(InvestigationCase.tenders),
    selectinload(InvestigationCase.signals).selectinload(RiskSignal.tenders),
    selectinload(InvestigationCase.signals).selectinload(RiskSignal.vendors),
)


def build_signal_out(signal: RiskSignal) -> RiskSignalOut:
    return RiskSignalOut(
        id=signal.id,
        signal_type=signal.signal_type,
        severity=signal.severity,
        score=signal.score,
        explanation=signal.explanation,
        tender_ids=[t.id for t in signal.tenders],
        vendor_ids=[v.id for v in signal.vendors],
        evidence=signal.evidence,
        metrics=signal.metrics or {},
    )


def _primary_entity(case: InvestigationCase):
    """Picks the vendor/tender that appears in the most contributing
    signals -- a simple, deterministic stand-in for "who/what this case is
    mainly about" used in the case list so an investigator can scan it fast.
    """
    vendor_freq, tender_freq = Counter(), Counter()
    for s in case.signals:
        for v in s.vendors:
            vendor_freq[v.id] += 1
        for t in s.tenders:
            tender_freq[t.id] += 1

    primary_vendor = None
    if case.vendors:
        primary_vendor = max(case.vendors, key=lambda v: (vendor_freq.get(v.id, 0), v.name))
    primary_tender = None
    if case.tenders:
        primary_tender = max(case.tenders, key=lambda t: (tender_freq.get(t.id, 0), t.id))

    return primary_vendor, primary_tender


def build_case_summary(case: InvestigationCase) -> CaseSummaryOut:
    primary_vendor, primary_tender = _primary_entity(case)
    return CaseSummaryOut(
        id=case.id,
        priority=case.priority,
        score=case.score,
        status=case.status,
        created_at=case.created_at.isoformat(),
        vendor_ids=[v.id for v in case.vendors],
        tender_ids=[t.id for t in case.tenders],
        signal_ids=[s.id for s in case.signals],
        signal_types=sorted({s.signal_type for s in case.signals}),
        vendor_names=[v.name for v in case.vendors],
        primary_entity=primary_vendor.name if primary_vendor else None,
        primary_tender=primary_tender.id if primary_tender else None,
        explanation=case.explanation,
    )


@router.get("/cases", response_model=list[CaseSummaryOut])
def list_cases(db: Session = Depends(get_db)):
    cases = (
        db.query(InvestigationCase)
        .options(*CASE_EAGER_LOAD)
        .order_by(InvestigationCase.score.desc())
        .all()
    )
    return [build_case_summary(c) for c in cases]


@router.get("/cases/{case_id}", response_model=CaseDetailOut)
def get_case(case_id: str, db: Session = Depends(get_db)):
    case = (
        db.query(InvestigationCase)
        .options(*CASE_EAGER_LOAD)
        .filter(InvestigationCase.id == case_id)
        .first()
    )
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    vendor_ids = [v.id for v in case.vendors]
    tender_ids = [t.id for t in case.tenders]

    owner_signals = aggregate_entity_signals(db)

    all_vendors = db.query(Vendor).all()
    all_tenders = db.query(Tender).all()
    all_bids = db.query(Bid).all()
    all_awards = db.query(Award).all()

    graph = build_case_graph(
        vendor_ids,
        tender_ids,
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

    tenders_out = []
    for t in case.tenders:
        rollup = owner_signals.get(t.department)
        tenders_out.append(TenderWithOwnerOut(
            id=t.id, title=t.title, department=t.department, category=t.category,
            location=t.location, estimated_value=t.estimated_value, date=t.date,
            owner_signal=rollup and {
                "name": t.department,
                "tag": rollup["tag"],
                "case_count": rollup["case_count"],
                "signal_count": rollup["signal_count"],
                "high_signal_count": rollup["high_signal_count"],
            },
        ))

    return CaseDetailOut(
        id=case.id,
        priority=case.priority,
        score=case.score,
        status=case.status,
        created_at=case.created_at.isoformat(),
        vendors=[VendorOut.model_validate(v) for v in case.vendors],
        tenders=tenders_out,
        signals=[build_signal_out(s) for s in case.signals],
        explanation=case.explanation,
        evidence=case.evidence,
        recommended_investigation=case.recommended_investigation,
        graph=graph,
    )
