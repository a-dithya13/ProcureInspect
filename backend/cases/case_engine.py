"""Signal convergence + investigation priority scoring.

A single signal rarely tells the whole story. This module groups signals
that share a vendor or a tender into one InvestigationCase, so an
investigator sees the full picture (price deviation + winner concentration +
repeated participation + bid similarity, say) as ONE case instead of four
disconnected alerts.

Priority score is a transparent, deterministic function of the contributing
signals' severities and the amount of convergence between them. It is an
"Investigation Priority" -- how much this warrants a human look -- and it is
explicitly NOT a probability of wrongdoing.
"""
import networkx as nx

SEVERITY_WEIGHT = {"LOW": 1.0, "MEDIUM": 2.0, "HIGH": 3.0}
CONVERGENCE_BONUS = 0.5  # extra weight per additional converging signal
NORMALIZATION_DIVISOR = 6.0  # tuned so 2+ converging HIGH signals reach ~100


def _priority_label(score_100: float, signal_count: int) -> str:
    if score_100 >= 70 or signal_count >= 3:
        return "HIGH"
    if score_100 >= 40 or signal_count == 2:
        return "MEDIUM"
    return "LOW"


def _recommendation_for_signal(signal: dict) -> str:
    t = signal["signal_type"]
    tender_ids = ", ".join(signal["tender_ids"]) if signal["tender_ids"] else "the flagged tender(s)"
    vendor_ids = signal["vendor_ids"]

    if t == "PRICE_DEVIATION":
        return (
            f"Verify the pricing justification for tender {tender_ids} against "
            f"comparable procurements in the same category and location."
        )
    if t == "WINNER_CONCENTRATION":
        v = vendor_ids[0] if vendor_ids else "the vendor"
        return (
            f"Review the award history of vendor {v}, which won an unusually high "
            f"share of comparable tenders ({tender_ids})."
        )
    if t == "REPEATED_PARTICIPATION":
        v1, v2 = (vendor_ids + ["", ""])[:2]
        return (
            f"Review the repeated participation pattern between {v1} and {v2} "
            f"across tenders {tender_ids}."
        )
    if t == "BID_SIMILARITY":
        v1, v2 = (vendor_ids + ["", ""])[:2]
        return (
            f"Examine the bid submission process between {v1} and {v2} for tenders "
            f"{tender_ids}, where bid amounts were unusually close."
        )
    if t == "COMPETITION_ANOMALY":
        return (
            f"Confirm outreach and eligibility criteria for tender {tender_ids}, "
            f"which drew fewer bidders than comparable tenders."
        )
    return f"Review the {t} signal for tender(s) {tender_ids}."


def build_cases(signals: list[dict]) -> list[dict]:
    """Group signals into cases by shared vendor/tender, score, and explain.

    `signals` must already have a stable "id" field assigned to each dict.
    Returns a list of case dicts (without an "id" -- assigned by the caller).
    """
    if not signals:
        return []

    graph = nx.Graph()
    for signal in signals:
        graph.add_node(signal["id"])

    for i, s1 in enumerate(signals):
        s1_entities = set(s1["vendor_ids"]) | set(s1["tender_ids"])
        for s2 in signals[i + 1:]:
            s2_entities = set(s2["vendor_ids"]) | set(s2["tender_ids"])
            if s1_entities & s2_entities:
                graph.add_edge(s1["id"], s2["id"])

    signals_by_id = {s["id"]: s for s in signals}
    cases = []

    for component in nx.connected_components(graph):
        group = [signals_by_id[sid] for sid in component]
        group.sort(key=lambda s: s["id"])

        vendor_ids = sorted({v for s in group for v in s["vendor_ids"]})
        tender_ids = sorted({t for s in group for t in s["tender_ids"]})
        signal_ids = [s["id"] for s in group]
        signal_types = sorted({s["signal_type"] for s in group})

        raw = sum(SEVERITY_WEIGHT[s["severity"]] * s["score"] for s in group)
        raw += CONVERGENCE_BONUS * (len(group) - 1)
        score_100 = round(min(1.0, raw / NORMALIZATION_DIVISOR) * 100, 1)
        priority = _priority_label(score_100, len(group))

        explanation = (
            f"{len(group)} converging investigation signal(s) "
            f"({', '.join(signal_types)}) involving vendor(s) "
            f"{', '.join(vendor_ids) if vendor_ids else 'n/a'} and tender(s) "
            f"{', '.join(tender_ids) if tender_ids else 'n/a'}."
        )

        evidence = [
            {
                "signal_id": s["id"],
                "signal_type": s["signal_type"],
                "records": s["evidence"],
            }
            for s in group
        ]

        recommended_investigation = " ".join(_recommendation_for_signal(s) for s in group)

        cases.append({
            "priority": priority,
            "score": score_100,
            "status": "OPEN",
            "vendor_ids": vendor_ids,
            "tender_ids": tender_ids,
            "signal_ids": signal_ids,
            "explanation": explanation,
            "evidence": evidence,
            "recommended_investigation": recommended_investigation,
        })

    cases.sort(key=lambda c: c["score"], reverse=True)
    return cases
