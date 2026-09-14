"""Tender-owner (department) signal aggregation.

The "tender owner" in this dataset is the issuing department (e.g. "Public
Works", "Health"). This module gives investigators a quick, transparent read
on how much detected procurement activity clusters around a given department
-- WITHOUT implying anyone in that department did anything wrong. It is a
rollup of already-computed signals/cases, not a new detector.

Departments are coarse buckets (each owns roughly 1/10th of all tenders), so
raw case/signal counts are dominated by dataset-wide background noise --
nearly every department would look "high" by a fixed absolute threshold.
Classification is therefore done RELATIVE to the dataset-wide average rate
per tender, the same peer-baseline approach used by the detectors themselves.
"""
from collections import defaultdict

from sqlalchemy.orm import Session

from models.orm import CaseTender, RiskSignal, RiskSignalTender, Tender

# Deterministic thresholds, expressed as a multiple of the dataset-wide
# average rate per tender for each metric (never a raw count) -- adjust here
# only; every caller reuses this. Rate-relative (not absolute) because a
# department is a coarse bucket that also absorbs background noise: an
# absolute count that looks alarming in isolation may just be this dataset's
# normal baseline once you account for how many tenders that department owns.
HIGH_RATE_MULTIPLIER = 1.5
ELEVATED_RATE_MULTIPLIER = 1.0


def _exceeds(rate: float, avg_rate: float, multiplier: float) -> bool:
    return avg_rate > 0 and rate >= avg_rate * multiplier


def classify_entity_signal(case_rate: float, signal_rate: float, high_severity_rate: float,
                            avg_case_rate: float, avg_signal_rate: float, avg_high_severity_rate: float,
                            signal_count: int) -> str:
    """Deterministic HIGH SIGNAL / ELEVATED / LOW SIGNAL / NEUTRAL tag.

    Describes DETECTED PATTERN DENSITY relative to the dataset average, not
    a finding of misconduct. Never surface this as "corrupt" or "guilty".
    """
    if (
        _exceeds(case_rate, avg_case_rate, HIGH_RATE_MULTIPLIER)
        or _exceeds(signal_rate, avg_signal_rate, HIGH_RATE_MULTIPLIER)
        or _exceeds(high_severity_rate, avg_high_severity_rate, HIGH_RATE_MULTIPLIER)
    ):
        return "HIGH SIGNAL"
    if (
        _exceeds(case_rate, avg_case_rate, ELEVATED_RATE_MULTIPLIER)
        or _exceeds(signal_rate, avg_signal_rate, ELEVATED_RATE_MULTIPLIER)
        or _exceeds(high_severity_rate, avg_high_severity_rate, ELEVATED_RATE_MULTIPLIER)
    ):
        return "ELEVATED"
    if signal_count >= 1:
        return "LOW SIGNAL"
    return "NEUTRAL"


def aggregate_entity_signals(db: Session) -> dict[str, dict]:
    """Rolls up case/signal activity per tender-owning department, relative
    to the dataset-wide average rate of cases/signals per tender.

    Returns {department_name: {case_count, signal_count, high_signal_count, tag}}
    for EVERY department that owns at least one tender (including those with
    zero detected activity, which come back NEUTRAL).
    """
    tender_department = {t.id: t.department for t in db.query(Tender.id, Tender.department).all()}

    dept_tender_count: dict[str, int] = defaultdict(int)
    for dept in tender_department.values():
        dept_tender_count[dept] += 1

    dept_signal_ids: dict[str, set] = defaultdict(set)
    for row in db.query(RiskSignalTender.signal_id, RiskSignalTender.tender_id).all():
        dept = tender_department.get(row.tender_id)
        if dept:
            dept_signal_ids[dept].add(row.signal_id)

    dept_case_ids: dict[str, set] = defaultdict(set)
    for row in db.query(CaseTender.case_id, CaseTender.tender_id).all():
        dept = tender_department.get(row.tender_id)
        if dept:
            dept_case_ids[dept].add(row.case_id)

    signal_severity = dict(db.query(RiskSignal.id, RiskSignal.severity).all())

    departments = sorted(dept_tender_count)
    case_rates, signal_rates, high_severity_rates = {}, {}, {}
    high_severity_counts = {}
    for dept in departments:
        n = dept_tender_count[dept]
        sig_ids = dept_signal_ids.get(dept, set())
        high_severity_counts[dept] = sum(1 for sid in sig_ids if signal_severity.get(sid) == "HIGH")
        case_rates[dept] = len(dept_case_ids.get(dept, set())) / n if n else 0.0
        signal_rates[dept] = len(sig_ids) / n if n else 0.0
        high_severity_rates[dept] = high_severity_counts[dept] / n if n else 0.0

    avg_case_rate = sum(case_rates.values()) / len(departments) if departments else 0.0
    avg_signal_rate = sum(signal_rates.values()) / len(departments) if departments else 0.0
    avg_high_severity_rate = sum(high_severity_rates.values()) / len(departments) if departments else 0.0

    result = {}
    for dept in departments:
        sig_ids = dept_signal_ids.get(dept, set())
        case_ids = dept_case_ids.get(dept, set())
        result[dept] = {
            "case_count": len(case_ids),
            "signal_count": len(sig_ids),
            "high_signal_count": high_severity_counts[dept],
            "tag": classify_entity_signal(
                case_rates[dept], signal_rates[dept], high_severity_rates[dept],
                avg_case_rate, avg_signal_rate, avg_high_severity_rate,
                len(sig_ids),
            ),
        }
    return result
