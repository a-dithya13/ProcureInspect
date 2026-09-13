import { useNavigate } from "react-router-dom";
import PriorityBadge from "./PriorityBadge";

export default function CasesTable({ cases }) {
  const navigate = useNavigate();

  if (!cases || cases.length === 0) {
    return (
      <div className="empty-state">
        No investigation cases yet. Click "Analyze Procurement" to run the detection pipeline.
      </div>
    );
  }

  return (
    <div className="evidence-table-wrap">
      <table>
        <thead>
          <tr>
            <th>Case ID</th>
            <th>Priority</th>
            <th>Score</th>
            <th>Signals</th>
            <th>Entities</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {cases.map((c) => (
            <tr key={c.id} className="clickable" onClick={() => navigate(`/cases/${c.id}`)}>
              <td className="mono">{c.id}</td>
              <td>
                <PriorityBadge priority={c.priority} />
              </td>
              <td>{c.score.toFixed(1)}</td>
              <td>
                <div className="chip-row">
                  {c.signal_types.map((t) => (
                    <span key={t} className="badge badge-type">
                      {t.replaceAll("_", " ")}
                    </span>
                  ))}
                </div>
              </td>
              <td>{c.vendor_names.join(", ") || <span className="muted">—</span>}</td>
              <td>
                <span className="badge badge-status">{c.status}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
