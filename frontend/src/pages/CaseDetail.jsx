import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import OwnerSignalBadge from "../components/OwnerSignalBadge";
import RelationshipGraph from "../components/RelationshipGraph";
import SignalCard from "../components/SignalCard";
import api from "../services/api";

const SIGNAL_LABELS = {
  PRICE_DEVIATION: "Price Deviation",
  WINNER_CONCENTRATION: "Winner Concentration",
  REPEATED_PARTICIPATION: "Repeated Participation",
  BID_SIMILARITY: "Bid Similarity",
  COMPETITION_ANOMALY: "Competition Anomaly",
};

export default function CaseDetail() {
  const { caseId } = useParams();
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api
      .get(`/cases/${caseId}`)
      .then((res) => setCaseData(res.data))
      .catch(() => setError(`Case ${caseId} could not be loaded.`))
      .finally(() => setLoading(false));
  }, [caseId]);

  if (loading) return <div className="loading-spinner">Loading case…</div>;
  if (error) {
    return (
      <div>
        <div className="error-banner">{error}</div>
        <button className="btn-secondary btn" onClick={() => navigate("/")}>Back to dashboard</button>
      </div>
    );
  }

  const c = caseData;
  const signalTypes = [...new Set(c.signals.map((s) => s.signal_type))];

  return (
    <div>
      <Link to="/" className="back-link">&larr; Back to dashboard</Link>

      <div className={`priority-banner ${c.priority}`}>
        <div>
          <div className="priority-banner-id mono">CASE #{c.id}</div>
          <div className="priority-banner-title">Investigation Priority: {c.priority}</div>
          <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>
            Generated {new Date(c.created_at).toLocaleString()}
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div className="stat-label">Investigation Score</div>
          <div className="stat-value">{c.score.toFixed(1)}</div>
        </div>
      </div>

      <div className="case-panel">
        <section className="case-section">
          <h2 className="section-title">Entities Involved</h2>
          <div className="entity-chip-list" style={{ marginBottom: 14 }}>
            {c.vendors.map((v) => (
              <Link key={v.id} to={`/vendors/${v.id}`} className="entity-chip">
                <div><strong>{v.name}</strong></div>
                <div className="entity-chip-sub">{v.id} · {v.category} · {v.location}</div>
              </Link>
            ))}
          </div>
          <div className="entity-chip-list">
            {c.tenders.map((t) => (
              <div key={t.id} className="entity-chip entity-chip-tender">
                <Link to={`/tenders/${t.id}`}>
                  <strong className="mono">{t.id}</strong> {t.title}
                </Link>
                <div className="entity-chip-sub">
                  {t.department} · {t.category} · {t.location} · est. {t.estimated_value.toLocaleString()}
                </div>
                {t.owner_signal && (
                  <div style={{ marginTop: 6 }}>
                    <OwnerSignalBadge signal={t.owner_signal} compact />
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        <section className="case-section">
          <h2 className="section-title">Why This Case Was Flagged</h2>
          <div className="case-section-flagged">
            <p className="flagged-explanation">{c.explanation}</p>
            <div className="chip-row">
              {signalTypes.map((t) => (
                <span key={t} className="badge badge-type badge-type-lg">{SIGNAL_LABELS[t] || t}</span>
              ))}
            </div>
          </div>
        </section>

        <section className="case-section">
          <h2 className="section-title">Key Findings ({c.signals.length})</h2>
          {c.signals.length === 0 ? (
            <div className="empty-state">No investigation signals detected.</div>
          ) : (
            c.signals.map((s, i) => (
              <div key={s.id}>
                <div className="stat-label" style={{ marginBottom: 6 }}>Finding {i + 1} of {c.signals.length}</div>
                <SignalCard signal={s} />
              </div>
            ))
          )}
        </section>

        <section className="case-section">
          <h2 className="section-title">Related Entities</h2>
          {c.graph.nodes.length === 0 ? (
            <div className="empty-state">No related entities found.</div>
          ) : (
            <RelationshipGraph graph={c.graph} />
          )}
        </section>

        <section className="case-section">
          <h2 className="section-title">Activity Timeline</h2>
          <ol className="timeline">
            {[...c.tenders]
              .sort((a, b) => new Date(a.date) - new Date(b.date))
              .map((t) => (
                <li key={t.id}>
                  <div className="timeline-date">{t.date}</div>
                  <div>
                    Tender <Link to={`/tenders/${t.id}`} className="evidence-id">{t.id}</Link> published
                    <div className="muted" style={{ fontSize: 12 }}>{t.title}</div>
                  </div>
                </li>
              ))}
            <li>
              <div className="timeline-date">{new Date(c.created_at).toLocaleDateString()}</div>
              <div>Case <span className="mono">{c.id}</span> created from {c.signals.length} converging signal(s)</div>
            </li>
          </ol>
        </section>

        <section className="case-section">
          <h2 className="section-title">Recommended Investigation Focus</h2>
          <div className="case-section-focus">
            <p className="muted" style={{ fontSize: 12.5, marginTop: 0, marginBottom: 12 }}>
              This is not an autonomous conclusion. It tells the investigator what to verify next.
            </p>
            {c.recommended_investigation.length === 0 ? (
              <div className="empty-state">No specific investigation focus generated for this case.</div>
            ) : (
              <ol className="focus-list">
                {c.recommended_investigation.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ol>
            )}
          </div>
        </section>
      </div>

      <div className="disclaimer">
        This case reflects statistical and pattern-based investigation signals only. It is not a finding of
        fraud or corruption. All recommendations require independent human verification before any action is
        taken.
      </div>
    </div>
  );
}
