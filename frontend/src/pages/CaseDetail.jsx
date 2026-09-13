import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import RelationshipGraph from "../components/RelationshipGraph";
import SignalCard from "../components/SignalCard";
import api from "../services/api";

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

  return (
    <div>
      <Link to="/" className="back-link">&larr; Back to dashboard</Link>

      <div className={`priority-banner ${c.priority}`}>
        <div>
          <div className="priority-banner-id mono">CASE #{c.id}</div>
          <div className="priority-banner-title">Investigation Priority: {c.priority}</div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div className="stat-label">Priority score</div>
          <div className="stat-value">{c.score.toFixed(1)}</div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Entities Involved</h2>
        </div>
        <div className="card-body">
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
              <div key={t.id} className="entity-chip">
                <div><strong className="mono">{t.id}</strong> {t.title}</div>
                <div className="entity-chip-sub">
                  {t.department} · {t.category} · {t.location} · est. {t.estimated_value.toLocaleString()}
                </div>
              </div>
            ))}
          </div>
          <p style={{ fontSize: 13.5, color: "#475569", marginTop: 14 }}>{c.explanation}</p>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Signals ({c.signals.length})</h2>
        </div>
        <div className="card-body">
          {c.signals.map((s, i) => (
            <div key={s.id}>
              <div className="stat-label" style={{ marginBottom: 6 }}>Signal {i + 1} of {c.signals.length}</div>
              <SignalCard signal={s} />
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Evidence</h2>
        </div>
        <div className="card-body">
          <p className="muted" style={{ fontSize: 13, marginTop: 0 }}>
            Underlying records used to generate each signal in this case.
          </p>
          {c.evidence.map((bundle) => (
            <div key={bundle.signal_id} style={{ marginBottom: 18 }}>
              <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 6 }}>
                <span className="mono">{bundle.signal_id}</span> · {bundle.signal_type.replaceAll("_", " ")}
              </div>
              <div className="evidence-table-wrap">
                <table>
                  <thead>
                    <tr>
                      {bundle.records[0] &&
                        Object.keys(bundle.records[0]).map((k) => <th key={k}>{k.replaceAll("_", " ")}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {bundle.records.map((r, i) => (
                      <tr key={i}>
                        {Object.entries(r).map(([k, v]) => (
                          <td key={k}>{v === null || v === undefined ? <span className="muted">—</span> : String(v)}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Vendor / Tender Relationship Graph</h2>
        </div>
        <div className="card-body">
          <RelationshipGraph graph={c.graph} />
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Recommended Investigation Focus</h2>
        </div>
        <div className="card-body">
          <div className="recommendation-box">{c.recommended_investigation}</div>
        </div>
      </div>

      <div className="disclaimer">
        This case reflects statistical and pattern-based investigation signals only. It is not a finding of
        fraud or corruption. All recommendations require independent human verification before any action is
        taken.
      </div>
    </div>
  );
}
