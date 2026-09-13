from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.cases import CASE_EAGER_LOAD, build_case_summary
from database.db import get_db
from models.orm import Award, Bid, CaseVendor, InvestigationCase, Vendor
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

    related_cases = (
        db.query(InvestigationCase)
        .join(CaseVendor, CaseVendor.case_id == InvestigationCase.id)
        .filter(CaseVendor.vendor_id == vendor_id)
        .options(*CASE_EAGER_LOAD)
        .order_by(InvestigationCase.score.desc())
        .all()
    )

    return VendorDetailOut(
        vendor=vendor,
        bids=bids,
        awards=awards,
        cases=[build_case_summary(c) for c in related_cases],
    )
