import { useEffect, useState } from "react";
import CasesTable from "../components/CasesTable";
import PriorityChart from "../components/PriorityChart";
import StatCard from "../components/StatCard";
import api from "../services/api";

export default function Dashboard() {
  const [overview, setOverview] = useState(null);
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeResult, setAnalyzeResult] = useState(null);
  const [error, setError] = useState(null);

  const load = async () => {
    setError(null);
    try {
      const [overviewRes, casesRes] = await Promise.all([api.get("/overview"), api.get("/cases")]);
      setOverview(overviewRes.data);
      setCases(casesRes.data);
    } catch (e) {
      setError("Could not reach the ProcureLens API. Is the backend running on port 8000?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setAnalyzeResult(null);
    setError(null);
    try {
      const res = await api.post("/analyze");
      setAnalyzeResult(res.data);
      await load();
    } catch (e) {
      setError("Analysis failed. Check the backend logs.");
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return <div className="loading-spinner">Loading procurement overview…</div>;
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Investigator Dashboard</h1>
          <p className="page-subtitle">
            Procurement statistics and prioritized investigation cases. Signals surface patterns worth a
            closer look -- they are not findings of wrongdoing.
          </p>
        </div>
        <button className="btn" onClick={handleAnalyze} disabled={analyzing}>
          {analyzing ? "Analyzing…" : "Analyze Procurement"}
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {analyzeResult && (
        <div className="error-banner" style={{ background: "#f0fdf4", borderColor: "#bbf7d0", color: "#166534" }}>
          Analysis complete in {analyzeResult.duration_seconds}s -- {analyzeResult.signals_detected} investigation
          signals detected, grouped into {analyzeResult.cases_created} cases
          ({analyzeResult.priority_distribution.HIGH} high / {analyzeResult.priority_distribution.MEDIUM} medium /
          {" "}{analyzeResult.priority_distribution.LOW} low priority).
        </div>
      )}

      <div className="stat-grid">
        <StatCard label="Total Tenders" value={overview.total_tenders} />
        <StatCard label="Total Vendors" value={overview.total_vendors} />
        <StatCard label="Total Bids" value={overview.total_bids} />
        <StatCard label="Investigation Signals" value={overview.total_signals} />
        <StatCard label="Investigation Cases" value={overview.total_cases} />
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Investigation Cases</h2>
            <span className="muted" style={{ fontSize: 12.5 }}>
              {overview.last_analysis_run
                ? `Last analysis: ${new Date(overview.last_analysis_run).toLocaleString()}`
                : "No analysis run yet"}
            </span>
          </div>
          <CasesTable cases={cases} />
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Case Priority Distribution</h2>
          </div>
          <div className="card-body">
            <PriorityChart distribution={overview.priority_distribution} />
          </div>
        </div>
      </div>

      <div className="disclaimer">
        ProcureLens surfaces investigation signals and priority scores to help human investigators focus
        their review. It does not determine, and should not be read as claiming, that any vendor engaged in
        wrongdoing. All findings require independent verification.
      </div>
    </div>
  );
}
