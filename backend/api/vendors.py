from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.cases import build_case_summary
from database.db import get_db
from models.orm import Award, Bid, InvestigationCase, RiskSignal, Vendor
from models.schemas import VendorDetailOut, VendorOut

router = APIRouter(prefix="/api", tags=["vendors"])


@router.get("/vendors", response_model=list[VendorOut])
def list_vendors(db: Session = Depends(get_db)):
    return db.query(Vendor).order_by(Vendor.name).all()


@router.get("/vendors/{vendor_id}", response_model=VendorDetailOut)
def get_vendor(vendor_id: str, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail=f"Vendor {vendor_id} not found")

    bids = db.query(Bid).filter(Bid.vendor_id == vendor_id).all()
    awards = db.query(Award).filter(Award.vendor_id == vendor_id).all()

    all_cases = db.query(InvestigationCase).all()
    vendors_by_id = {v.id: v for v in db.query(Vendor).all()}
    signals_by_id = {s.id: s for s in db.query(RiskSignal).all()}
    related_cases = [
        build_case_summary(c, vendors_by_id, signals_by_id)
        for c in all_cases
        if vendor_id in c.vendor_ids
    ]

    return VendorDetailOut(vendor=vendor, bids=bids, awards=awards, cases=related_cases)
