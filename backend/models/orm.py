"""SQLAlchemy ORM models for ProcureLens.

Core procurement entities (Vendor, Tender, Bid, Award) are loaded by
scripts/generate_data.py. RiskSignal and InvestigationCase are produced and
persisted by the detection pipeline (services/analysis_service.py) every time
POST /api/analyze runs.
"""
from sqlalchemy import Column, DateTime, Float, Integer, JSON, String

from database.db import Base

# Note: these tables intentionally have no SQLAlchemy relationship()/ForeignKey
# wiring. The API queries each table directly and filters by id (e.g.
# `Bid.vendor_id == vendor_id`), so ORM-level relationship traversal is never
# needed and would just add mapper complexity for no benefit.


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    location = Column(String, nullable=False)


class Tender(Base):
    __tablename__ = "tenders"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    department = Column(String, nullable=False)
    category = Column(String, nullable=False)
    location = Column(String, nullable=False)
    estimated_value = Column(Float, nullable=False)
    date = Column(String, nullable=False)  # ISO date string


class Bid(Base):
    __tablename__ = "bids"

    id = Column(String, primary_key=True)
    tender_id = Column(String, nullable=False)
    vendor_id = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)


class Award(Base):
    __tablename__ = "awards"

    id = Column(String, primary_key=True)
    tender_id = Column(String, nullable=False)
    vendor_id = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    award_date = Column(String, nullable=False)


class RiskSignal(Base):
    __tablename__ = "risk_signals"

    id = Column(String, primary_key=True)
    signal_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)  # LOW / MEDIUM / HIGH
    score = Column(Float, nullable=False)  # 0.0 - 1.0, evidence strength
    explanation = Column(String, nullable=False)
    tender_ids = Column(JSON, nullable=False, default=list)
    vendor_ids = Column(JSON, nullable=False, default=list)
    evidence = Column(JSON, nullable=False, default=list)


class InvestigationCase(Base):
    __tablename__ = "investigation_cases"

    id = Column(String, primary_key=True)
    priority = Column(String, nullable=False)  # LOW / MEDIUM / HIGH
    score = Column(Float, nullable=False)  # 0-100 investigation priority score
    status = Column(String, nullable=False, default="OPEN")
    vendor_ids = Column(JSON, nullable=False, default=list)
    tender_ids = Column(JSON, nullable=False, default=list)
    signal_ids = Column(JSON, nullable=False, default=list)
    explanation = Column(String, nullable=False)
    evidence = Column(JSON, nullable=False, default=list)
    recommended_investigation = Column(String, nullable=False)


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_at = Column(DateTime, nullable=False)
    signals_detected = Column(Integer, nullable=False)
    cases_created = Column(Integer, nullable=False)
    duration_seconds = Column(Float, nullable=False)
