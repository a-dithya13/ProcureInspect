"""REPEATED_PARTICIPATION detector.

Flags pairs of vendors that repeatedly bid on the same tenders far more often
than the typical vendor pair in the dataset. This is reported as a
"repeated participation" pattern -- it is evidence to review, not a claim of
collusion.

Raw shared-tender counts alone are misleading: a vendor that simply bids a
lot will rack up a few coincidental overlaps with many different competitors
just by chance. To separate a genuine recurring pairing from that noise, we
also require that a large share of the LESS active vendor's total bidding
activity is specifically with this one partner (`overlap_ratio`).
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

MIN_SHARED_TENDERS = 4
MIN_OVERLAP_RATIO = 0.5


def detect(tenders_df: pd.DataFrame, bids_df: pd.DataFrame) -> list[dict]:
    if bids_df.empty:
        return []

    tender_info = tenders_df.set_index("id").to_dict("index")
    pair_tenders = build_pair_shared_tenders(bids_df)
    participation_counts = vendor_participation_counts(bids_df)

    if not pair_tenders:
        return []

    counts = np.array([len(v) for v in pair_tenders.values()])
    mean = float(np.mean(counts))
    std = float(np.std(counts))
    stat_threshold = max(MIN_SHARED_TENDERS, mean + 3 * std)

    signals = []
    for (v1, v2), shared in pair_tenders.items():
        if len(shared) < stat_threshold:
            continue

        ratio = overlap_ratio(len(shared), v1, v2, participation_counts)
        if ratio < MIN_OVERLAP_RATIO:
            continue

        if std > 1e-9:
            z = (len(shared) - mean) / std
            score = clamp(z / 5.0, 0.4, 1.0)
        else:
            score = clamp(len(shared) / 6.0, 0.4, 1.0)
        score = clamp((score + ratio) / 2, 0.4, 1.0)

        evidence = [
            {
                "tender_id": t,
                "category": tender_info.get(t, {}).get("category"),
                "location": tender_info.get(t, {}).get("location"),
                "date": tender_info.get(t, {}).get("date"),
            }
            for t in shared
        ]

        signals.append({
            "signal_type": "REPEATED_PARTICIPATION",
            "severity": severity_from_score(score),
            "score": round(score, 3),
            "explanation": (
                f"Vendors {v1} and {v2} both submitted bids on {len(shared)} of the same "
                f"tenders -- {ratio * 100:.0f}% of the less-active vendor's total bidding "
                f"activity -- compared with an average of {mean:.1f} shared tenders across "
                f"all vendor pairs in this dataset."
            ),
            "tender_ids": shared,
            "vendor_ids": [v1, v2],
            "evidence": evidence,
            "metrics": {
                "shared_tenders": len(shared),
                "overlap_ratio_percent": round(ratio * 100, 1),
                "dataset_average_shared_tenders": round(mean, 1),
            },
        })

    return signals
