"""BID_SIMILARITY detector.

For vendor pairs that co-participate in several tenders (see
REPEATED_PARTICIPATION), checks whether their bid amounts sit unusually close
together, tender after tender, once normalized by tender size. A small and
consistent gap across multiple tenders is the pattern of interest -- a single
close bid is normal competition.
"""
import numpy as np
import pandas as pd

from detection.common import (
    build_pair_shared_tenders,
    clamp,
    overlap_ratio,
    severity_from_score,
    vendor_participation_counts,
)

MIN_SHARED_TENDERS = 3
MIN_OVERLAP_RATIO = 0.5
MAX_NORMALIZED_DIFF = 0.04  # bids within 4% of estimated value, on average


def detect(tenders_df: pd.DataFrame, bids_df: pd.DataFrame) -> list[dict]:
    if bids_df.empty:
        return []

    pair_tenders = build_pair_shared_tenders(bids_df)
    participation_counts = vendor_participation_counts(bids_df)
    tender_value = dict(zip(tenders_df["id"], tenders_df["estimated_value"]))
    bid_amount = {
        (row["tender_id"], row["vendor_id"]): row["amount"] for _, row in bids_df.iterrows()
    }

    signals = []
    for (v1, v2), shared in pair_tenders.items():
        if len(shared) < MIN_SHARED_TENDERS:
            continue
        if overlap_ratio(len(shared), v1, v2, participation_counts) < MIN_OVERLAP_RATIO:
            continue

        normalized_diffs = []
        per_tender_evidence = []
        for t in shared:
            value = tender_value.get(t)
            a1 = bid_amount.get((t, v1))
            a2 = bid_amount.get((t, v2))
            if not value or value <= 0 or a1 is None or a2 is None:
                continue
            diff = abs(a1 - a2) / value
            normalized_diffs.append(diff)
            per_tender_evidence.append({
                "tender_id": t,
                "vendor_a_bid": round(float(a1), 2),
                "vendor_b_bid": round(float(a2), 2),
                "normalized_diff": round(float(diff), 4),
            })

        if len(normalized_diffs) < MIN_SHARED_TENDERS:
            continue

        mean_diff = float(np.mean(normalized_diffs))
        if mean_diff > MAX_NORMALIZED_DIFF:
            continue

        score = clamp(1 - (mean_diff / MAX_NORMALIZED_DIFF), 0.3, 1.0)

        signals.append({
            "signal_type": "BID_SIMILARITY",
            "severity": severity_from_score(score),
            "score": round(score, 3),
            "explanation": (
                f"Vendors {v1} and {v2} submitted bids within {mean_diff * 100:.1f}% of each "
                f"other's value (normalized by tender size) on average, across "
                f"{len(normalized_diffs)} shared tenders -- consistently closer than the "
                f"{MAX_NORMALIZED_DIFF * 100:.0f}% threshold used for this check."
            ),
            "tender_ids": [e["tender_id"] for e in per_tender_evidence],
            "vendor_ids": [v1, v2],
            "evidence": per_tender_evidence,
            "metrics": {
                "shared_tenders": len(normalized_diffs),
                "avg_difference_percent": round(mean_diff * 100, 2),
                "threshold_percent": round(MAX_NORMALIZED_DIFF * 100, 1),
            },
        })

    return signals
