"""SQLAlchemy ORM models for ProcureLens.

Core procurement entities (Vendor, Tender, Bid, Award) are loaded by
scripts/generate_data.py. RiskSignal and InvestigationCase are produced and
persisted by the detection pipeline (services/analysis_service.py) every time
POST /api/analyze runs.

Schema is managed by Alembic (see backend/alembic/) -- this file is the
source of truth for the ORM/target schema, but changes to it must be paired
with a migration under alembic/versions/. Do not rely on
Base.metadata.create_all() against a real environment; use
`alembic upgrade head`.

Relational shape:
    Vendor 1--* Bid *--1 Tender          (who bid on what)
    Vendor 1--* Award *--1 Tender        (who won what)
    RiskSignal *--* Tender, Vendor       (via risk_signal_tenders / risk_signal_vendors)
    InvestigationCase *--* Vendor, Tender, RiskSignal
        (via case_vendors / case_tenders / case_signals)

The many-to-many links above used to be plain JSON arrays of ids on
RiskSignal/InvestigationCase. They are now real foreign-key-backed junction
tables so the relationships are enforceable and visible in tools like the
Supabase schema visualizer. `evidence` stays as JSON: it's a denormalized
snapshot of the numbers that produced a signal/case (ratios, medians, z-scores)
at analysis time, not a reference to other rows.
"""
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from database.db import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    location = Column(String, nullable=False)

    bids = relationship("Bid", back_populates="vendor")
    awards = relationship("Award", back_populates="vendor")


class Tender(Base):
    __tablename__ = "tenders"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    department = Column(String, nullable=False)
    category = Column(String, nullable=False)
    location = Column(String, nullable=False)
    estimated_value = Column(Float, nullable=False)
    date = Column(String, nullable=False)  # ISO date string

    bids = relationship("Bid", back_populates="tender")
    awards = relationship("Award", back_populates="tender")


class Bid(Base):
    __tablename__ = "bids"

    id = Column(String, primary_key=True)
    tender_id = Column(String, ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False, index=True)
    vendor_id = Column(String, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)

    tender = relationship("Tender", back_populates="bids")
    vendor = relationship("Vendor", back_populates="bids")


class Award(Base):
    __tablename__ = "awards"

    id = Column(String, primary_key=True)
    tender_id = Column(String, ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False, index=True)
    vendor_id = Column(String, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    award_date = Column(String, nullable=False)

    tender = relationship("Tender", back_populates="awards")
    vendor = relationship("Vendor", back_populates="awards")


class RiskSignal(Base):
    __tablename__ = "risk_signals"

    id = Column(String, primary_key=True)
    signal_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)  # LOW / MEDIUM / HIGH
    score = Column(Float, nullable=False)  # 0.0 - 1.0, evidence strength
    explanation = Column(String, nullable=False)
    evidence = Column(JSON, nullable=False, default=list)
    # Structured headline numbers for this signal (e.g. observed_amount,
    # peer_median_amount, deviation_percent) -- what the signal card's stat
    # row renders. Kept separate from `evidence` (a list of supporting
    # records) so the frontend never has to parse the explanation string.
    metrics = Column(JSON, nullable=False, default=dict)

    tenders = relationship("Tender", secondary="risk_signal_tenders", order_by="Tender.id")
    vendors = relationship("Vendor", secondary="risk_signal_vendors", order_by="Vendor.id")


class InvestigationCase(Base):
    __tablename__ = "investigation_cases"

    id = Column(String, primary_key=True)
    priority = Column(String, nullable=False)  # LOW / MEDIUM / HIGH
    score = Column(Float, nullable=False)  # 0-100 investigation priority score
    status = Column(String, nullable=False, default="OPEN")
    created_at = Column(DateTime, nullable=False)
    explanation = Column(String, nullable=False)
    evidence = Column(JSON, nullable=False, default=list)
    # Ordered checklist of what to verify next (one entry per contributing
    # signal) -- a list, not a single paragraph, so the UI can render it as
    # a numbered "Recommended Investigation Focus".
    recommended_investigation = Column(JSON, nullable=False, default=list)

    vendors = relationship("Vendor", secondary="case_vendors", order_by="Vendor.id")
    tenders = relationship("Tender", secondary="case_tenders", order_by="Tender.id")
    signals = relationship("RiskSignal", secondary="case_signals", order_by="RiskSignal.id")


class RiskSignalTender(Base):
    __tablename__ = "risk_signal_tenders"

    signal_id = Column(String, ForeignKey("risk_signals.id", ondelete="CASCADE"), primary_key=True)
    tender_id = Column(String, ForeignKey("tenders.id", ondelete="CASCADE"), primary_key=True)


class RiskSignalVendor(Base):
    __tablename__ = "risk_signal_vendors"

    signal_id = Column(String, ForeignKey("risk_signals.id", ondelete="CASCADE"), primary_key=True)
    vendor_id = Column(String, ForeignKey("vendors.id", ondelete="CASCADE"), primary_key=True)


class CaseVendor(Base):
    __tablename__ = "case_vendors"

    case_id = Column(String, ForeignKey("investigation_cases.id", ondelete="CASCADE"), primary_key=True)
    vendor_id = Column(String, ForeignKey("vendors.id", ondelete="CASCADE"), primary_key=True)


class CaseTender(Base):
    __tablename__ = "case_tenders"

    case_id = Column(String, ForeignKey("investigation_cases.id", ondelete="CASCADE"), primary_key=True)
    tender_id = Column(String, ForeignKey("tenders.id", ondelete="CASCADE"), primary_key=True)


class CaseSignal(Base):
    __tablename__ = "case_signals"

    case_id = Column(String, ForeignKey("investigation_cases.id", ondelete="CASCADE"), primary_key=True)
    signal_id = Column(String, ForeignKey("risk_signals.id", ondelete="CASCADE"), primary_key=True)


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_at = Column(DateTime, nullable=False)
    signals_detected = Column(Integer, nullable=False)
    cases_created = Column(Integer, nullable=False)
    duration_seconds = Column(Float, nullable=False)
