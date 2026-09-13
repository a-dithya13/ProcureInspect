"""Vendor <-> Tender relationship graph construction.

Builds a NetworkX bipartite graph (vendors and tenders as nodes, bids/awards
as edges) around a case's core entities, then serializes it into a simple
nodes/edges shape the frontend renders with Cytoscape.js.

The seed vendors/tenders (the ones actually named by the case's signals) are
expanded by one hop -- e.g. other vendors that bid on the same tenders -- so
the graph shows the "Vendor A -- Tender -- Vendor B" pattern investigators
care about, not just an isolated set of dots.
"""
import pandas as pd

MAX_NODES = 40


def build_case_graph(
    vendor_ids: list[str],
    tender_ids: list[str],
    vendors_df: pd.DataFrame,
    tenders_df: pd.DataFrame,
    bids_df: pd.DataFrame,
    awards_df: pd.DataFrame,
) -> dict:
    seed_vendors = set(vendor_ids)
    seed_tenders = set(tender_ids)

    extra_vendors = set(bids_df[bids_df["tender_id"].isin(seed_tenders)]["vendor_id"])
    extra_tenders = set(bids_df[bids_df["vendor_id"].isin(seed_vendors)]["tender_id"])

    all_vendors = seed_vendors | extra_vendors
    all_tenders = seed_tenders | extra_tenders

    if len(all_vendors) + len(all_tenders) > MAX_NODES:
        # Keep every seed entity; trim the one-hop extras to fit.
        extra_v_budget = max(0, (MAX_NODES - len(seed_vendors) - len(seed_tenders)) // 2)
        extra_t_budget = max(0, MAX_NODES - len(seed_vendors) - len(seed_tenders) - extra_v_budget)
        all_vendors = seed_vendors | set(list(extra_vendors)[:extra_v_budget])
        all_tenders = seed_tenders | set(list(extra_tenders)[:extra_t_budget])

    vendor_lookup = vendors_df.set_index("id").to_dict("index")
    tender_lookup = tenders_df.set_index("id").to_dict("index")
    award_vendor_by_tender = dict(zip(awards_df["tender_id"], awards_df["vendor_id"]))

    nodes = []
    for vid in all_vendors:
        info = vendor_lookup.get(vid, {})
        nodes.append({
            "id": vid,
            "label": info.get("name", vid),
            "type": "vendor",
            "detail": {
                "is_case_entity": vid in seed_vendors,
                "category": info.get("category"),
                "location": info.get("location"),
            },
        })
    for tid in all_tenders:
        info = tender_lookup.get(tid, {})
        nodes.append({
            "id": tid,
            "label": info.get("title", tid),
            "type": "tender",
            "detail": {
                "is_case_entity": tid in seed_tenders,
                "category": info.get("category"),
                "location": info.get("location"),
                "estimated_value": info.get("estimated_value"),
            },
        })

    relevant_bids = bids_df[
        bids_df["vendor_id"].isin(all_vendors) & bids_df["tender_id"].isin(all_tenders)
    ]

    edges = []
    for _, bid in relevant_bids.iterrows():
        is_award = award_vendor_by_tender.get(bid["tender_id"]) == bid["vendor_id"]
        edges.append({
            "id": f"e-{bid['tender_id']}-{bid['vendor_id']}",
            "source": bid["vendor_id"],
            "target": bid["tender_id"],
            "type": "award" if is_award else "bid",
            "detail": {"amount": round(float(bid["amount"]), 2), "rank": int(bid["rank"])},
        })

    return {"nodes": nodes, "edges": edges}
