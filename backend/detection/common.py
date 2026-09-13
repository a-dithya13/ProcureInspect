"""Shared helpers used by every detector.

Each detector in this package returns a list of plain dicts shaped like:

    {
        "signal_type": str,
        "severity": "LOW" | "MEDIUM" | "HIGH",
        "score": float,           # 0.0-1.0 evidence strength, NOT a probability
        "explanation": str,       # human-readable, no accusations
        "tender_ids": [str, ...],
        "vendor_ids": [str, ...],
        "evidence": [dict, ...],  # underlying records that support the signal
    }

Detectors never assign an "id" -- that is done centrally when signals are
persisted (see services/analysis_service.py) so IDs stay unique and stable
across a single analysis run.
"""


def severity_from_score(score: float) -> str:
    """Map a 0-1 evidence-strength score onto a LOW/MEDIUM/HIGH label."""
    if score >= 0.75:
        return "HIGH"
    if score >= 0.45:
        return "MEDIUM"
    return "LOW"


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def build_pair_shared_tenders(bids_df) -> dict:
    """Map each (vendor_id, vendor_id) pair -> list of tender_ids both bid on.

    Shared by REPEATED_PARTICIPATION and BID_SIMILARITY so the "who
    co-participates with whom" logic is defined in exactly one place.
    """
    from collections import defaultdict
    from itertools import combinations

    pair_tenders = defaultdict(list)
    bidders_by_tender = bids_df.groupby("tender_id")["vendor_id"].apply(list)
    for tender_id, vendors in bidders_by_tender.items():
        distinct_vendors = sorted(set(vendors))
        for v1, v2 in combinations(distinct_vendors, 2):
            pair_tenders[(v1, v2)].append(tender_id)
    return pair_tenders


def vendor_participation_counts(bids_df) -> dict:
    """Map vendor_id -> number of distinct tenders that vendor bid on."""
    return bids_df.groupby("vendor_id")["tender_id"].nunique().to_dict()


def overlap_ratio(shared_count: int, v1: str, v2: str, participation_counts: dict) -> float:
    """How much of the LESS active vendor's bidding activity is with this
    specific partner. A hub vendor that bids on many tenders will coincide
    with lots of others a few times each by pure chance -- this ratio is
    what tells a real recurring pairing apart from that noise.
    """
    smaller_total = min(participation_counts.get(v1, shared_count), participation_counts.get(v2, shared_count))
    if smaller_total <= 0:
        return 0.0
    return shared_count / smaller_total
