import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import CasesTable from "../components/CasesTable";
import OwnerSignalBadge from "../components/OwnerSignalBadge";
import api from "../services/api";

export default function TenderDetail() {
  const { tenderId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api
      .get(`/tenders/${tenderId}`)
      .then((res) => setData(res.data))
      .catch(() => setError(`Tender ${tenderId} could not be loaded.`))
      .finally(() => setLoading(false));
  }, [tenderId]);

  if (loading) return <div className="loading-spinner">Loading tender…</div>;
  if (error) return <div className="error-banner">{error}</div>;

  const { tender, bids, award, cases } = data;

  return (
    <div>
      <Link to="/" className="back-link">&larr; Back to dashboard</Link>

      <div className="page-header">
        <div>
          <h1 className="page-title">{tender.title}</h1>
          <p className="page-subtitle mono">
            {tender.id} &middot; {tender.department} &middot; {tender.category} &middot; {tender.location}
          </p>
        </div>
        {tender.owner_signal && <OwnerSignalBadge signal={tender.owner_signal} />}
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Estimated Value</div>
          <div className="stat-value">{tender.estimated_value.toLocaleString()}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Bids Received</div>
          <div className="stat-value">{bids.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Awarded To</div>
          <div className="stat-value" style={{ fontSize: 16 }}>
            {award ? <Link to={`/vendors/${award.vendor_id}`} className="mono">{award.vendor_id}</Link> : <span className="muted">Not awarded</span>}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Investigation Cases</div>
          <div className="stat-value">{cases.length}</div>
        </div>
      </div>

      {tender.owner_signal && (
        <p className="muted" style={{ fontSize: 12.5, marginTop: -8, marginBottom: 20 }}>
          Signal levels represent detected procurement patterns across all of this department's tenders and
          are not findings of misconduct.
        </p>
      )}

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Investigation Cases Involving This Tender</h2>
        </div>
        <CasesTable cases={cases} />
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Bids ({bids.length})</h2>
        </div>
        {bids.length === 0 ? (
          <div className="empty-state">No bids recorded for this tender.</div>
        ) : (
          <div className="evidence-table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Vendor</th>
                  <th>Bid Amount</th>
                  <th>Rank</th>
                  <th>Outcome</th>
                </tr>
              </thead>
              <tbody>
                {bids.map((b) => (
                  <tr key={b.id}>
                    <td>
                      <Link to={`/vendors/${b.vendor_id}`} className="mono">{b.vendor_id}</Link>
                    </td>
                    <td>{b.amount.toLocaleString()}</td>
                    <td>{b.rank}</td>
                    <td>
                      {award?.vendor_id === b.vendor_id ? (
                        <span className="badge badge-status">Won</span>
                      ) : (
                        <span className="muted">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
