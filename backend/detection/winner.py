"""WINNER_CONCENTRATION detector.

Within a comparable-tender group (same category + location), flags a vendor
that wins an unusually high proportion of the tenders it participates in.
"""
import pandas as pd

from detection.common import clamp, severity_from_score

MIN_GROUP_SIZE = 4
MIN_PARTICIPATED = 4
WIN_PCT_THRESHOLD = 0.6


def detect(tenders_df: pd.DataFrame, bids_df: pd.DataFrame, awards_df: pd.DataFrame) -> list[dict]:
    if bids_df.empty or awards_df.empty:
        return []

    bids_merged = bids_df.merge(tenders_df, left_on="tender_id", right_on="id", suffixes=("", "_tender"))
    awards_by_tender = dict(zip(awards_df["tender_id"], awards_df["vendor_id"]))
    award_amount_by_tender = dict(zip(awards_df["tender_id"], awards_df["amount"]))

    signals = []

    for (category, location), group in bids_merged.groupby(["category", "location"]):
        distinct_tenders = group["tender_id"].unique()
        if len(distinct_tenders) < MIN_GROUP_SIZE:
            continue

        for vendor_id, vendor_bids in group.groupby("vendor_id"):
            participated = vendor_bids["tender_id"].unique().tolist()
            if len(participated) < MIN_PARTICIPATED:
                continue

            wins = [t for t in participated if awards_by_tender.get(t) == vendor_id]
            win_pct = len(wins) / len(participated)

            if win_pct < WIN_PCT_THRESHOLD or not wins:
                continue

            score = clamp(win_pct)
            evidence = [
                {
                    "tender_id": t,
                    "category": category,
                    "location": location,
                    "award_amount": round(float(award_amount_by_tender.get(t, 0)), 2),
                }
                for t in wins
            ]

            signals.append({
                "signal_type": "WINNER_CONCENTRATION",
                "severity": severity_from_score(score),
                "score": round(score, 3),
                "explanation": (
                    f"Vendor {vendor_id} won {len(wins)} of {len(participated)} comparable "
                    f"'{category}' tenders in {location} it bid on ({win_pct * 100:.0f}% win rate), "
                    f"well above the {WIN_PCT_THRESHOLD * 100:.0f}% baseline used for this check."
                ),
                "tender_ids": wins,
                "vendor_ids": [vendor_id],
                "evidence": evidence,
                "metrics": {
                    "tenders_won": len(wins),
                    "tenders_participated": len(participated),
                    "win_rate_percent": round(win_pct * 100, 1),
                    "threshold_percent": round(WIN_PCT_THRESHOLD * 100, 1),
                },
            })

    return signals
