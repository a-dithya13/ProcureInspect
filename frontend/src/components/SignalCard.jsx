import PriorityBadge from "./PriorityBadge";

const SIGNAL_LABELS = {
  PRICE_DEVIATION: "Price Deviation",
  WINNER_CONCENTRATION: "Winner Concentration",
  REPEATED_PARTICIPATION: "Repeated Participation",
  BID_SIMILARITY: "Bid Similarity",
  COMPETITION_ANOMALY: "Competition Anomaly",
};

const SIGNAL_DESCRIPTIONS = {
  PRICE_DEVIATION: "Compares the winning price against a peer baseline of comparable tenders (same category/location), normalized by estimated value.",
  WINNER_CONCENTRATION: "Flags a vendor winning an unusually high share of the comparable tenders it bid on.",
  REPEATED_PARTICIPATION: "Flags vendor pairs that co-bid on the same tenders far more than typical, relative to their overall bidding activity.",
  BID_SIMILARITY: "Flags vendor pairs whose bid amounts sit unusually close together across several shared tenders.",
  COMPETITION_ANOMALY: "Flags tenders that drew far fewer bidders than comparable tenders.",
};

function EvidenceRecordTable({ records }) {
  if (!records || records.length === 0) return null;
  const columns = Array.from(
    records.reduce((set, r) => {
      Object.keys(r).forEach((k) => set.add(k));
      return set;
    }, new Set())
  );

  return (
    <div className="evidence-table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c}>{c.replaceAll("_", " ")}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {records.map((r, i) => (
            <tr key={i}>
              {columns.map((c) => (
                <td key={c} className={typeof r[c] === "string" && /^[A-Z]\d+$/.test(r[c]) ? "mono" : undefined}>
                  {r[c] === null || r[c] === undefined ? <span className="muted">—</span> : String(r[c])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function SignalCard({ signal }) {
  return (
    <div className="signal-card">
      <div className="signal-card-header">
        <div className="signal-card-title">{SIGNAL_LABELS[signal.signal_type] || signal.signal_type}</div>
        <div className="chip-row" style={{ alignItems: "center" }}>
          <PriorityBadge priority={signal.severity} />
          <span className="badge badge-type">evidence strength {signal.score.toFixed(2)}</span>
        </div>
      </div>
      <div className="muted" style={{ fontSize: 12.5, marginBottom: 8 }}>
        {SIGNAL_DESCRIPTIONS[signal.signal_type]}
      </div>
      <div className="signal-explanation">{signal.explanation}</div>

      <div style={{ display: "flex", gap: 24, flexWrap: "wrap", marginBottom: 10 }}>
        <div>
          <div className="stat-label" style={{ marginBottom: 4 }}>Supporting tenders</div>
          <div className="chip-row">
            {signal.tender_ids.length ? (
              signal.tender_ids.map((t) => (
                <span key={t} className="mono badge badge-low">{t}</span>
              ))
            ) : (
              <span className="muted">none</span>
            )}
          </div>
        </div>
        <div>
          <div className="stat-label" style={{ marginBottom: 4 }}>Supporting vendors</div>
          <div className="chip-row">
            {signal.vendor_ids.length ? (
              signal.vendor_ids.map((v) => (
                <span key={v} className="mono badge badge-low">{v}</span>
              ))
            ) : (
              <span className="muted">none</span>
            )}
          </div>
        </div>
      </div>

      <EvidenceRecordTable records={signal.evidence} />
    </div>
  );
}
