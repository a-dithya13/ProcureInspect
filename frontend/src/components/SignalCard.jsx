import { useState } from "react";
import { Link } from "react-router-dom";
import EvidenceText from "./EvidenceText";
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

const WHY_IT_MATTERS = {
  PRICE_DEVIATION: "The winning price differs materially from comparable procurement activity.",
  WINNER_CONCENTRATION: "One vendor is winning a disproportionate share of comparable tenders.",
  REPEATED_PARTICIPATION: "The same vendors keep appearing together across tenders, far more than a typical pair.",
  BID_SIMILARITY: "Bid amounts from these vendors are unusually close, tender after tender.",
  COMPETITION_ANOMALY: "This tender drew far fewer competing bids than comparable procurements.",
};

const METRIC_DEFS = {
  PRICE_DEVIATION: [
    { key: "observed_amount", label: "Observed Bid", format: "amount" },
    { key: "peer_median_amount", label: "Peer Median", format: "amount" },
    { key: "deviation_percent", label: "Deviation", format: "signed-percent" },
  ],
  WINNER_CONCENTRATION: [
    { key: "tenders_won", label: "Tenders Won", format: "int" },
    { key: "tenders_participated", label: "Tenders Participated", format: "int" },
    { key: "win_rate_percent", label: "Win Rate", format: "percent" },
  ],
  REPEATED_PARTICIPATION: [
    { key: "shared_tenders", label: "Shared Tenders", format: "int" },
    { key: "overlap_ratio_percent", label: "Overlap Ratio", format: "percent" },
    { key: "dataset_average_shared_tenders", label: "Dataset Average", format: "amount" },
  ],
  BID_SIMILARITY: [
    { key: "shared_tenders", label: "Shared Tenders", format: "int" },
    { key: "avg_difference_percent", label: "Avg Bid Difference", format: "percent" },
    { key: "threshold_percent", label: "Threshold Used", format: "percent" },
  ],
  COMPETITION_ANOMALY: [
    { key: "observed_bids", label: "Observed Bids", format: "int" },
    { key: "peer_median_bids", label: "Peer Median Bids", format: "amount" },
    { key: "difference_percent", label: "Difference", format: "signed-percent" },
  ],
};

function formatMetric(value, format) {
  if (value === null || value === undefined) return "—";
  if (format === "percent") return `${value}%`;
  if (format === "signed-percent") return `${value > 0 ? "+" : ""}${value}%`;
  if (format === "amount") return typeof value === "number" ? value.toLocaleString(undefined, { maximumFractionDigits: 2 }) : value;
  return value;
}

function EvidenceRecordTable({ records }) {
  if (!records || records.length === 0) {
    return <div className="empty-state" style={{ padding: "16px 0" }}>No additional evidence available.</div>;
  }
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
  const [showEvidence, setShowEvidence] = useState(false);
  const metricDefs = METRIC_DEFS[signal.signal_type] || [];

  return (
    <div className="signal-card">
      <div className="signal-card-header">
        <div className="signal-card-title">{SIGNAL_LABELS[signal.signal_type] || signal.signal_type}</div>
        <div className="chip-row" style={{ alignItems: "center" }}>
          <PriorityBadge priority={signal.severity} />
          <span className="badge badge-type">evidence strength {signal.score.toFixed(2)}</span>
        </div>
      </div>
      <div className="muted" style={{ fontSize: 12.5, marginBottom: 10 }}>
        {SIGNAL_DESCRIPTIONS[signal.signal_type]}
      </div>

      {metricDefs.length > 0 && (
        <div className="metric-row">
          {metricDefs.map((m) => (
            <div key={m.key} className="metric-stat">
              <div className="metric-stat-label">{m.label}</div>
              <div className="metric-stat-value">{formatMetric(signal.metrics?.[m.key], m.format)}</div>
            </div>
          ))}
        </div>
      )}

      <p className="signal-explanation">
        <EvidenceText text={signal.explanation} />
      </p>

      <div className="why-it-matters">
        <strong>Why it matters: </strong>
        {WHY_IT_MATTERS[signal.signal_type] || "This pattern differs from comparable procurement activity."}
      </div>

      <div className="signal-card-footer">
        <div className="chip-row">
          {signal.tender_ids.length > 0 && (
            <span className="muted" style={{ fontSize: 12 }}>
              Evidence source:{" "}
              {signal.tender_ids.map((t, i) => (
                <span key={t}>
                  {i > 0 && ", "}
                  <Link to={`/tenders/${t}`} className="evidence-id">{t}</Link>
                </span>
              ))}
            </span>
          )}
        </div>
        <button type="button" className="btn-link" onClick={() => setShowEvidence((v) => !v)}>
          {showEvidence ? "Hide evidence" : "View evidence"}
        </button>
      </div>

      {showEvidence && (
        <div style={{ marginTop: 10 }}>
          <EvidenceRecordTable records={signal.evidence} />
        </div>
      )}
    </div>
  );
}
