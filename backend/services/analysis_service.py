"""Orchestrates the detection pipeline: load data -> run detectors -> group
signals into cases -> persist everything.

This is the only place that ties the individually-testable detectors
together, so the pipeline as a whole stays easy to follow.
"""
import time
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy.orm import Session

from cases.case_engine import build_cases
from detection import bid_similarity, competition, participation, price, winner
from models.orm import AnalysisRun, Award, Bid, InvestigationCase, RiskSignal, Tender, Vendor


def _load_dataframes(db: Session):
    vendors_df = pd.read_sql(db.query(Vendor).statement, db.bind)
    tenders_df = pd.read_sql(db.query(Tender).statement, db.bind)
    bids_df = pd.read_sql(db.query(Bid).statement, db.bind)
    awards_df = pd.read_sql(db.query(Award).statement, db.bind)
    return vendors_df, tenders_df, bids_df, awards_df


def run_analysis(db: Session) -> dict:
    start = time.monotonic()

    vendors_df, tenders_df, bids_df, awards_df = _load_dataframes(db)

    raw_signals = []
    raw_signals += price.detect(tenders_df, awards_df)
    raw_signals += winner.detect(tenders_df, bids_df, awards_df)
    raw_signals += participation.detect(tenders_df, bids_df)
    raw_signals += bid_similarity.detect(tenders_df, bids_df)
    raw_signals += competition.detect(tenders_df, bids_df)

    for i, signal in enumerate(raw_signals, start=1):
        signal["id"] = f"S{i:04d}"

    raw_cases = build_cases(raw_signals)
    for i, case in enumerate(raw_cases, start=1):
        case["id"] = f"C{i:04d}"

    # Fresh analysis run: replace prior signals/cases so results stay consistent.
    db.query(InvestigationCase).delete()
    db.query(RiskSignal).delete()

    db.bulk_insert_mappings(RiskSignal, [
        {
            "id": s["id"],
            "signal_type": s["signal_type"],
            "severity": s["severity"],
            "score": s["score"],
            "explanation": s["explanation"],
            "tender_ids": s["tender_ids"],
            "vendor_ids": s["vendor_ids"],
            "evidence": s["evidence"],
        }
        for s in raw_signals
    ])

    db.bulk_insert_mappings(InvestigationCase, [
        {
            "id": c["id"],
            "priority": c["priority"],
            "score": c["score"],
            "status": c["status"],
            "vendor_ids": c["vendor_ids"],
            "tender_ids": c["tender_ids"],
            "signal_ids": c["signal_ids"],
            "explanation": c["explanation"],
            "evidence": c["evidence"],
            "recommended_investigation": c["recommended_investigation"],
        }
        for c in raw_cases
    ])

    duration = time.monotonic() - start

    priority_distribution = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for c in raw_cases:
        priority_distribution[c["priority"]] += 1

    db.add(AnalysisRun(
        run_at=datetime.now(timezone.utc),
        signals_detected=len(raw_signals),
        cases_created=len(raw_cases),
        duration_seconds=duration,
    ))

    db.commit()

    return {
        "signals_detected": len(raw_signals),
        "cases_created": len(raw_cases),
        "priority_distribution": priority_distribution,
        "duration_seconds": round(duration, 3),
    }
