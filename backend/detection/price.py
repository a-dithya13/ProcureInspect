"""PRICE_DEVIATION detector.

Compares each awarded tender's winning price against a peer baseline built
from comparable tenders (same category, preferably same location) that were
also awarded. Prices are normalized as award_amount / estimated_value so
tenders of different sizes can be compared fairly.

When the peer group is large enough (n >= 5) a z-score against the peer
distribution is used. For smaller peer groups we fall back to a simple
percentage-deviation-from-median threshold, since a z-score is unstable with
few samples.
"""
import numpy as np
import pandas as pd

from detection.common import clamp, severity_from_score

MIN_PEERS_FOR_ZSCORE = 5
MIN_PEERS_REQUIRED = 3
ZSCORE_THRESHOLD = 2.5
PCT_DEVIATION_THRESHOLD = 0.40
MAX_EVIDENCE_PEERS = 8


def detect(tenders_df: pd.DataFrame, awards_df: pd.DataFrame) -> list[dict]:
    if awards_df.empty:
        return []

    merged = awards_df.merge(
        tenders_df, left_on="tender_id", right_on="id", suffixes=("_award", "_tender")
    )
    merged = merged[merged["estimated_value"] > 0].copy()
    merged["ratio"] = merged["amount"] / merged["estimated_value"]

    signals = []

    for category, cat_group in merged.groupby("category"):
        if len(cat_group) < MIN_PEERS_REQUIRED + 1:
            continue

        for _, row in cat_group.iterrows():
            same_location = cat_group[
                (cat_group["location"] == row["location"]) & (cat_group["tender_id"] != row["tender_id"])
            ]
            other_category = cat_group[cat_group["tender_id"] != row["tender_id"]]
            peers = same_location if len(same_location) >= MIN_PEERS_REQUIRED else other_category

            if len(peers) < MIN_PEERS_REQUIRED:
                continue

            peer_ratios = peers["ratio"].to_numpy()
            median = float(np.median(peer_ratios))
            std = float(np.std(peer_ratios))
            ratio = float(row["ratio"])

            flagged = False
            score = 0.0

            if len(peers) >= MIN_PEERS_FOR_ZSCORE and std > 1e-9:
                z = (ratio - median) / std
                if abs(z) >= ZSCORE_THRESHOLD:
                    flagged = True
                    score = clamp(abs(z) / 5.0, 0.4, 1.0)
                pct_dev = (ratio - median) / median if median > 0 else 0.0
            else:
                pct_dev = (ratio - median) / median if median > 0 else 0.0
                if abs(pct_dev) >= PCT_DEVIATION_THRESHOLD:
                    flagged = True
                    score = clamp(abs(pct_dev) / 1.0, 0.4, 1.0)

            if not flagged:
                continue

            direction = "higher" if ratio > median else "lower"
            peer_median_amount = median * row["estimated_value"]

            evidence_peers = peers.sort_values("ratio", ascending=False).head(MAX_EVIDENCE_PEERS)
            evidence = [
                {
                    "tender_id": p["tender_id"],
                    "category": p["category"],
                    "location": p["location"],
                    "estimated_value": round(float(p["estimated_value"]), 2),
                    "award_amount": round(float(p["amount"]), 2),
                    "price_ratio": round(float(p["ratio"]), 3),
                }
                for _, p in evidence_peers.iterrows()
            ]

            signals.append({
                "signal_type": "PRICE_DEVIATION",
                "severity": severity_from_score(score),
                "score": round(score, 3),
                "explanation": (
                    f"Winning price for tender {row['tender_id']} is {abs(pct_dev) * 100:.1f}% "
                    f"{direction} than the peer median for comparable '{category}' tenders "
                    f"in {row['location']} (n={len(peers)} peers). "
                    f"Award amount: {row['amount']:,.2f}; peer median equivalent: "
                    f"{peer_median_amount:,.2f}."
                ),
                "tender_ids": [row["tender_id"]],
                "vendor_ids": [row["vendor_id"]],
                "evidence": evidence,
            })

    return signals
