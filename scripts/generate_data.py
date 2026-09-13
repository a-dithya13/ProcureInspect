"""Generates a synthetic procurement dataset for ProcureLens and loads it into
the configured PostgreSQL database (see backend/.env -> DATABASE_URL).

Produces ~200 vendors, ~500 tenders and ~2000 bids. Most of the data is
ordinary procurement with normal price/competition variance. A handful of
scenarios are deliberately planted so the detection pipeline has known
patterns to find:

  1. Winner concentration  -- one vendor wins most of a comparable tender group
  2. Repeated participation -- two vendors keep co-bidding on the same tenders
  3. Bid similarity         -- those two vendors' bids sit unusually close together
  4. Price deviation        -- a tender's winning price is far above its peer group
  5. Convergence            -- scenarios 1-4 all happen around the SAME two
                               vendors/tenders, so they should merge into one
                               high-priority investigation case

A ground-truth record of what was planted is written to
scripts/ground_truth.json for evaluating detector recall -- it is never read
by the application itself.

Usage:
    cd backend && venv/Scripts/python.exe ../scripts/generate_data.py
"""
import json
import os
import random
import sys
from datetime import date, timedelta

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from sqlalchemy import inspect, text  # noqa: E402

from database.db import engine  # noqa: E402
from models import orm  # noqa: E402,F401

random.seed(42)

CATEGORIES = [
    "Construction", "IT Services", "Medical Supplies", "Office Equipment",
    "Road Maintenance", "Consulting", "Security Services", "Catering",
    "Cleaning Services", "Electrical Works",
]
LOCATIONS = [
    "Springfield", "Rivertown", "Oakville", "Lakeside", "Hillcrest",
    "Fairview", "Greenfield", "Brookside", "Sunnyvale", "Maple Ridge",
]
DEPARTMENTS = [
    "Public Works", "Health", "Education", "Transport", "IT",
    "Defense", "Administration", "Housing", "Environment", "Finance",
]
CATEGORY_VALUE_RANGE = {
    "Construction": (400_000, 2_000_000),
    "IT Services": (50_000, 500_000),
    "Medical Supplies": (30_000, 400_000),
    "Office Equipment": (10_000, 150_000),
    "Road Maintenance": (200_000, 1_200_000),
    "Consulting": (20_000, 300_000),
    "Security Services": (40_000, 350_000),
    "Catering": (15_000, 200_000),
    "Cleaning Services": (10_000, 180_000),
    "Electrical Works": (60_000, 600_000),
}

PREFIXES = [
    "Alpha", "Beta", "Summit", "Horizon", "Pioneer", "National", "Metro",
    "Capital", "United", "Premier", "Apex", "Vertex", "Sterling", "Crown",
    "Atlas", "Meridian", "Vanguard", "Cascade", "Granite", "Beacon",
]
SUFFIXES = [
    "Constructors", "Technologies", "Supplies", "Services", "Solutions",
    "Enterprises", "Group", "Industries", "Partners", "Corp", "Systems",
    "Holdings", "Ventures", "Associates", "Works",
]

START_DATE = date.today() - timedelta(days=730)


def random_date(days_span=700):
    return (START_DATE + timedelta(days=random.randint(0, days_span))).isoformat()


def make_vendor_names(n):
    names = set()
    while len(names) < n:
        name = f"{random.choice(PREFIXES)} {random.choice(SUFFIXES)}"
        names.add(name)
    return list(names)


def main():
    vendors, tenders, bids, awards = [], [], [], []
    ground_truth = {"scenarios": []}

    v_counter = 1
    t_counter = 1
    b_counter = 1
    a_counter = 1

    def next_vendor_id():
        nonlocal v_counter
        vid = f"V{v_counter:04d}"
        v_counter += 1
        return vid

    def next_tender_id():
        nonlocal t_counter
        tid = f"T{t_counter:04d}"
        t_counter += 1
        return tid

    def next_bid_id():
        nonlocal b_counter
        bid_id = f"B{b_counter:05d}"
        b_counter += 1
        return bid_id

    def next_award_id():
        nonlocal a_counter
        aid = f"A{a_counter:04d}"
        a_counter += 1
        return aid

    def add_vendor(name, category, location):
        vid = next_vendor_id()
        vendors.append({"id": vid, "name": name, "category": category, "location": location})
        return vid

    def add_tender(title, department, category, location, estimated_value, tender_date):
        tid = next_tender_id()
        tenders.append({
            "id": tid, "title": title, "department": department, "category": category,
            "location": location, "estimated_value": round(estimated_value, 2), "date": tender_date,
        })
        return tid

    def add_bid(tender_id, vendor_id, amount, rank):
        bid_id = next_bid_id()
        bids.append({
            "id": bid_id, "tender_id": tender_id, "vendor_id": vendor_id,
            "amount": round(amount, 2), "rank": rank,
        })
        return bid_id

    def add_award(tender_id, vendor_id, amount, award_date):
        aid = next_award_id()
        awards.append({
            "id": aid, "tender_id": tender_id, "vendor_id": vendor_id,
            "amount": round(amount, 2), "award_date": award_date,
        })
        return aid

    def run_normal_tender(category, location, department=None, bidder_pool=None,
                           bidder_count=None, value_range=None, tender_date=None,
                           lowest_wins_prob=0.85):
        """Generates one ordinary tender with realistic-but-unremarkable bids."""
        department = department or random.choice(DEPARTMENTS)
        lo, hi = value_range or CATEGORY_VALUE_RANGE[category]
        estimated_value = random.uniform(lo, hi)
        tender_date = tender_date or random_date()
        title = f"{category} tender - {department} ({location})"
        tid = add_tender(title, department, category, location, estimated_value, tender_date)

        pool = bidder_pool if bidder_pool is not None else vendor_ids
        n_bidders = bidder_count if bidder_count is not None else max(1, min(9, round(random.gauss(4.3, 1.6))))
        n_bidders = min(n_bidders, len(pool))
        bidders = random.sample(pool, n_bidders)

        bid_amounts = []
        for vid in bidders:
            amount = estimated_value * random.uniform(0.80, 1.10)
            bid_amounts.append((vid, amount))

        bid_amounts.sort(key=lambda x: x[1])
        for rank, (vid, amount) in enumerate(bid_amounts, start=1):
            add_bid(tid, vid, amount, rank)

        if bid_amounts:
            if random.random() < lowest_wins_prob:
                winner_vid, winner_amount = bid_amounts[0]
            else:
                winner_vid, winner_amount = random.choice(bid_amounts)
            award_date = (date.fromisoformat(tender_date) + timedelta(days=random.randint(5, 25))).isoformat()
            add_award(tid, winner_vid, winner_amount, award_date)

        return tid, estimated_value

    # ------------------------------------------------------------------
    # 1. Base vendor pool (mostly random, ordinary companies)
    # ------------------------------------------------------------------
    TOTAL_VENDORS = 200
    names = make_vendor_names(TOTAL_VENDORS)
    vendor_ids = []
    for name in names:
        category = random.choice(CATEGORIES)
        location = random.choice(LOCATIONS)
        vendor_ids.append(add_vendor(name, category, location))

    # ------------------------------------------------------------------
    # 2. Planted scenario: convergence cluster (vendors A & B)
    #    winner concentration + repeated participation + bid similarity
    #    + price deviation, all around the same two vendors/tenders.
    # ------------------------------------------------------------------
    plant_a = add_vendor("Crown Road Contractors", "Road Maintenance", "Springfield")
    plant_b = add_vendor("Apex Infrastructure Group", "Road Maintenance", "Springfield")
    filler_vendors = [add_vendor(f"{random.choice(PREFIXES)} {random.choice(SUFFIXES)} Rd", "Road Maintenance", "Springfield") for _ in range(3)]

    cluster_tender_ids = []
    for i in range(6):
        estimated_value = random.uniform(500_000, 800_000)
        tender_date = random_date()
        title = f"Road Maintenance tender - Public Works (Springfield) #{i + 1}"
        tid = add_tender(title, "Public Works", "Road Maintenance", "Springfield", estimated_value, tender_date)
        cluster_tender_ids.append(tid)

        base = estimated_value * random.uniform(0.90, 0.97)
        a_amount = base
        b_amount = base * random.uniform(0.99, 1.02)  # bid_similarity: within ~2%

        third_vendor = random.choice(filler_vendors)
        third_amount = estimated_value * random.uniform(1.05, 1.15)

        entries = [(plant_a, a_amount), (plant_b, b_amount), (third_vendor, third_amount)]
        entries.sort(key=lambda x: x[1])
        for rank, (vid, amount) in enumerate(entries, start=1):
            add_bid(tid, vid, amount, rank)

        award_date = (date.fromisoformat(tender_date) + timedelta(days=random.randint(5, 20))).isoformat()
        if i < 5:
            # vendor A wins 5 of 6 -> winner concentration
            winner_vid, winner_amount = plant_a, a_amount
        else:
            winner_vid, winner_amount = plant_b, b_amount

        if i == 5:
            # inflate the final win far above the peer baseline -> price deviation
            winner_amount = estimated_value * 1.55
        add_award(tid, winner_vid, winner_amount, award_date)

    # A handful of ordinary Road Maintenance/Springfield peers so the price
    # deviation baseline has a realistic comparison group.
    for _ in range(5):
        run_normal_tender("Road Maintenance", "Springfield", value_range=(500_000, 800_000))

    ground_truth["scenarios"].append({
        "name": "convergence_cluster",
        "description": "Vendors A & B: winner concentration + repeated participation + bid similarity + price deviation on the final award",
        "vendor_ids": [plant_a, plant_b],
        "tender_ids": cluster_tender_ids,
    })

    # ------------------------------------------------------------------
    # 3. Planted scenario: standalone price deviation
    # ------------------------------------------------------------------
    price_dev_peers = []
    for _ in range(5):
        tid, _ = run_normal_tender("IT Services", "Oakville", value_range=(150_000, 250_000))
        price_dev_peers.append(tid)

    price_dev_vendor = add_vendor("Sterling Systems Ltd", "IT Services", "Oakville")
    ev = random.uniform(150_000, 250_000)
    tender_date = random_date()
    tid = add_tender("IT Services tender - IT (Oakville) - special", "IT", "IT Services", "Oakville", ev, tender_date)
    filler = random.sample(vendor_ids, 2)
    overpriced_amount = ev * 1.9
    add_bid(tid, price_dev_vendor, overpriced_amount, 1)
    other_amounts = []
    for vid in filler:
        amt = ev * random.uniform(0.85, 1.05)
        other_amounts.append((vid, amt))
    for rank, (vid, amt) in enumerate(sorted(other_amounts, key=lambda x: x[1]), start=2):
        add_bid(tid, vid, amt, rank)
    award_date = (date.fromisoformat(tender_date) + timedelta(days=10)).isoformat()
    add_award(tid, price_dev_vendor, overpriced_amount, award_date)

    ground_truth["scenarios"].append({
        "name": "standalone_price_deviation",
        "description": "Single tender awarded far above the IT Services/Oakville peer baseline",
        "vendor_ids": [price_dev_vendor],
        "tender_ids": [tid],
    })

    # ------------------------------------------------------------------
    # 4. Planted scenario: standalone competition anomaly
    # ------------------------------------------------------------------
    for _ in range(6):
        run_normal_tender("Security Services", "Lakeside", bidder_count=random.choice([5, 6]),
                           value_range=(100_000, 300_000))

    low_comp_vendor = random.choice(vendor_ids)
    ev = random.uniform(100_000, 300_000)
    tender_date = random_date()
    tid = add_tender("Security Services tender - Defense (Lakeside) - urgent", "Defense", "Security Services",
                      "Lakeside", ev, tender_date)
    amount = ev * random.uniform(0.9, 1.0)
    add_bid(tid, low_comp_vendor, amount, 1)
    award_date = (date.fromisoformat(tender_date) + timedelta(days=8)).isoformat()
    add_award(tid, low_comp_vendor, amount, award_date)

    ground_truth["scenarios"].append({
        "name": "standalone_competition_anomaly",
        "description": "Tender with a single bidder against a peer group averaging 5-6 bidders",
        "vendor_ids": [low_comp_vendor],
        "tender_ids": [tid],
    })

    # ------------------------------------------------------------------
    # 5. Planted scenario: standalone winner concentration
    # ------------------------------------------------------------------
    winner_vendor = add_vendor("Meridian Medical Supply Co", "Medical Supplies", "Fairview")
    wc_filler = [add_vendor(f"{random.choice(PREFIXES)} {random.choice(SUFFIXES)} Med", "Medical Supplies", "Fairview") for _ in range(3)]
    wc_tenders = []
    for i in range(7):
        ev = random.uniform(80_000, 300_000)
        tender_date = random_date()
        tid = add_tender(f"Medical Supplies tender - Health (Fairview) #{i + 1}", "Health", "Medical Supplies",
                          "Fairview", ev, tender_date)
        wc_tenders.append(tid)
        winner_amount = ev * random.uniform(0.85, 0.95)
        entries = [(winner_vendor, winner_amount)]
        others = random.sample(wc_filler, 2)
        for vid in others:
            entries.append((vid, ev * random.uniform(0.96, 1.15)))
        entries.sort(key=lambda x: x[1])
        for rank, (vid, amount) in enumerate(entries, start=1):
            add_bid(tid, vid, amount, rank)
        award_date = (date.fromisoformat(tender_date) + timedelta(days=12)).isoformat()
        if i < 6:
            add_award(tid, winner_vendor, winner_amount, award_date)
        else:
            other_vid, other_amount = entries[1]
            add_award(tid, other_vid, other_amount, award_date)

    ground_truth["scenarios"].append({
        "name": "standalone_winner_concentration",
        "description": "One vendor wins 6 of 7 comparable Medical Supplies/Fairview tenders",
        "vendor_ids": [winner_vendor],
        "tender_ids": wc_tenders,
    })

    # ------------------------------------------------------------------
    # 6. Planted scenario: standalone repeated participation + bid similarity
    #    (no winner concentration -- wins are split, so only these two
    #    signals should converge here)
    # ------------------------------------------------------------------
    part_a = add_vendor("Beacon Consulting Partners", "Consulting", "Hillcrest")
    part_b = add_vendor("Vanguard Advisory Group", "Consulting", "Hillcrest")
    part_third = add_vendor("Granite Strategy Associates", "Consulting", "Hillcrest")
    part_tenders = []
    for i in range(5):
        ev = random.uniform(60_000, 220_000)
        tender_date = random_date()
        tid = add_tender(f"Consulting tender - Administration (Hillcrest) #{i + 1}", "Administration",
                          "Consulting", "Hillcrest", ev, tender_date)
        part_tenders.append(tid)
        base = ev * random.uniform(0.88, 0.98)
        a_amount = base
        b_amount = base * random.uniform(0.98, 1.03)
        c_amount = ev * random.uniform(1.05, 1.2)
        entries = sorted([(part_a, a_amount), (part_b, b_amount), (part_third, c_amount)], key=lambda x: x[1])
        for rank, (vid, amount) in enumerate(entries, start=1):
            add_bid(tid, vid, amount, rank)
        award_date = (date.fromisoformat(tender_date) + timedelta(days=9)).isoformat()
        # alternate the winner so no single vendor concentrates wins
        winner_vid, winner_amount = (part_a, a_amount) if i % 2 == 0 else (part_b, b_amount)
        add_award(tid, winner_vid, winner_amount, award_date)

    ground_truth["scenarios"].append({
        "name": "standalone_participation_and_similarity",
        "description": "Two vendors repeatedly co-bid with closely-matched amounts, but wins are split (no winner concentration)",
        "vendor_ids": [part_a, part_b],
        "tender_ids": part_tenders,
    })

    # ------------------------------------------------------------------
    # 7. Fill remaining tenders with ordinary, random procurement
    # ------------------------------------------------------------------
    TOTAL_TENDERS = 500
    remaining = TOTAL_TENDERS - len(tenders)
    for _ in range(remaining):
        category = random.choice(CATEGORIES)
        location = random.choice(LOCATIONS)
        run_normal_tender(category, location)

    # ------------------------------------------------------------------
    # 8. Load into the database
    # ------------------------------------------------------------------
    vendors_df = pd.DataFrame(vendors)
    tenders_df = pd.DataFrame(tenders)
    bids_df = pd.DataFrame(bids)
    awards_df = pd.DataFrame(awards)

    print(f"Generated {len(vendors_df)} vendors, {len(tenders_df)} tenders, "
          f"{len(bids_df)} bids, {len(awards_df)} awards.")

    inspector = inspect(engine)
    if not inspector.has_table("vendors"):
        raise RuntimeError(
            "Database schema not found. Run migrations first:\n"
            "    cd backend && venv\\Scripts\\python.exe -m alembic upgrade head"
        )

    print("Clearing existing data (schema is managed by Alembic, not recreated here)...")
    with engine.begin() as conn:
        # Deletes cascade to bids/awards/risk_signal_*/case_* via FK ON DELETE CASCADE.
        conn.execute(text("DELETE FROM investigation_cases"))
        conn.execute(text("DELETE FROM risk_signals"))
        conn.execute(text("DELETE FROM analysis_runs"))
        conn.execute(text("DELETE FROM tenders"))
        conn.execute(text("DELETE FROM vendors"))

    print("Loading data into PostgreSQL (this may take a little while)...")
    vendors_df.to_sql("vendors", engine, if_exists="append", index=False, method="multi", chunksize=500)
    tenders_df.to_sql("tenders", engine, if_exists="append", index=False, method="multi", chunksize=500)
    bids_df.to_sql("bids", engine, if_exists="append", index=False, method="multi", chunksize=500)
    awards_df.to_sql("awards", engine, if_exists="append", index=False, method="multi", chunksize=500)

    ground_truth_path = os.path.join(os.path.dirname(__file__), "ground_truth.json")
    with open(ground_truth_path, "w") as f:
        json.dump(ground_truth, f, indent=2)

    print(f"Ground truth written to {ground_truth_path}")
    print("Done. Run POST /api/analyze (or click 'Analyze Procurement' in the UI) to detect signals.")


if __name__ == "__main__":
    main()
