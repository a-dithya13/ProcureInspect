"""COMPETITION_ANOMALY detector.

Flags tenders that attracted an unusually low number of bidders compared
with comparable tenders (same category + location). Low competition on an
otherwise-typical tender is worth a second look -- it can reflect restrictive
specifications, short notice periods, or limited outreach.
"""
import numpy as np
import pandas as pd

from detection.common import clamp, severity_from_score

MIN_PEER_GROUP = 5
MIN_GAP = 2
MAX_EVIDENCE_PEERS = 8


def detect(tenders_df: pd.DataFrame, bids_df: pd.DataFrame) -> list[dict]:
    if bids_df.empty:
        return []

    bidder_counts = bids_df.groupby("tender_id")["vendor_id"].nunique()
    tenders = tenders_df.copy()
    tenders["bidder_count"] = tenders["id"].map(bidder_counts).fillna(0).astype(int)

    signals = []

    for (category, location), group in tenders.groupby(["category", "location"]):
        if len(group) < MIN_PEER_GROUP + 1:
            continue

        for _, row in group.iterrows():
            peers = group[group["id"] != row["id"]]
            peer_median = float(np.median(peers["bidder_count"]))
            current = int(row["bidder_count"])

            gap = peer_median - current
            if gap < MIN_GAP:
                continue

            score = clamp(gap / max(peer_median, 1.0), 0.35, 1.0)

            evidence = [
                {
                    "tender_id": p["id"],
                    "category": p["category"],
                    "location": p["location"],
                    "bidder_count": int(p["bidder_count"]),
                }
                for _, p in peers.sort_values("bidder_count", ascending=False).head(MAX_EVIDENCE_PEERS).iterrows()
            ]

            signals.append({
                "signal_type": "COMPETITION_ANOMALY",
                "severity": severity_from_score(score),
                "score": round(score, 3),
                "explanation": (
                    f"Tender {row['id']} received {current} bid(s), well below the peer "
                    f"median of {peer_median:.1f} for comparable '{category}' tenders in "
                    f"{location} (n={len(peers)} peers)."
                ),
                "tender_ids": [row["id"]],
                "vendor_ids": [],
                "evidence": evidence,
            })

    return signals
