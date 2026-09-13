import { useEffect, useState } from "react";
import CasesTable from "../components/CasesTable";
import api from "../services/api";

export default function CasesPage() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .get("/cases")
      .then((res) => setCases(res.data))
      .catch(() => setError("Could not reach the ProcureLens API. Is the backend running on port 8000?"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-spinner">Loading investigation cases…</div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Investigation Cases</h1>
          <p className="page-subtitle">
            Cases group converging investigation signals around the same vendors and tenders. Priority
            reflects how much a case warrants a closer look -- it is not a finding of wrongdoing.
          </p>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="card">
        <CasesTable cases={cases} />
      </div>

      <div className="disclaimer">
        ProcureLens doesn't decide who is corrupt. It helps investigators decide where to look first --
        and shows them why.
      </div>
    </div>
  );
}
