import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import CasesTable from "../components/CasesTable";
import api from "../services/api";

export default function VendorDetail() {
  const { vendorId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api
      .get(`/vendors/${vendorId}`)
      .then((res) => setData(res.data))
      .catch(() => setError(`Vendor ${vendorId} could not be loaded.`))
      .finally(() => setLoading(false));
  }, [vendorId]);

  if (loading) return <div className="loading-spinner">Loading vendor…</div>;
  if (error) return <div className="error-banner">{error}</div>;

  const { vendor, bids, awards, cases } = data;
  const awardedTenderIds = new Set(awards.map((a) => a.tender_id));

  return (
    <div>
      <Link to="/" className="back-link">&larr; Back to dashboard</Link>

      <div className="page-header">
        <div>
          <h1 className="page-title">{vendor.name}</h1>
          <p className="page-subtitle mono">{vendor.id} · {vendor.category} · {vendor.location}</p>
        </div>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Bids Submitted</div>
          <div className="stat-value">{bids.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Tenders Won</div>
          <div className="stat-value">{awards.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Win Rate</div>
          <div className="stat-value">{bids.length ? `${((awards.length / bids.length) * 100).toFixed(0)}%` : "—"}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Investigation Cases</div>
          <div className="stat-value">{cases.length}</div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Investigation Cases Involving This Vendor</h2>
        </div>
        <CasesTable cases={cases} />
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Bid History ({bids.length})</h2>
        </div>
        <div className="evidence-table-wrap">
          <table>
            <thead>
              <tr>
                <th>Tender</th>
                <th>Bid Amount</th>
                <th>Rank</th>
                <th>Outcome</th>
              </tr>
            </thead>
            <tbody>
              {bids.map((b) => (
                <tr key={b.id}>
                  <td className="mono">{b.tender_id}</td>
                  <td>{b.amount.toLocaleString()}</td>
                  <td>{b.rank}</td>
                  <td>
                    {awardedTenderIds.has(b.tender_id) && awards.find((a) => a.tender_id === b.tender_id)?.vendor_id === vendor.id ? (
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
      </div>
    </div>
  );
}
