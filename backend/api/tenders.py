from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db import get_db
from models.orm import Tender
from models.schemas import TenderOut

router = APIRouter(prefix="/api", tags=["tenders"])


@router.get("/tenders", response_model=list[TenderOut])
def list_tenders(db: Session = Depends(get_db)):
    return db.query(Tender).order_by(Tender.date.desc()).all()
