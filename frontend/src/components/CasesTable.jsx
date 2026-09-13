import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import PriorityBadge from "./PriorityBadge";

const PRIORITY_ORDER = { HIGH: 0, MEDIUM: 1, LOW: 2 };
const FILTERS = ["ALL", "HIGH", "MEDIUM", "LOW"];
const SORTS = [
  { value: "priority", label: "Highest Priority" },
  { value: "score", label: "Highest Investigation Score" },
  { value: "newest", label: "Newest" },
];

export default function CasesTable({ cases, showControls = true, limit }) {
  const navigate = useNavigate();
  const [priorityFilter, setPriorityFilter] = useState("ALL");
  const [sortBy, setSortBy] = useState("priority");

  const counts = useMemo(() => {
    const c = { ALL: cases?.length ?? 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
    for (const item of cases || []) c[item.priority] = (c[item.priority] || 0) + 1;
    return c;
  }, [cases]);

  const visible = useMemo(() => {
    let rows = cases || [];
    if (priorityFilter !== "ALL") {
      rows = rows.filter((c) => c.priority === priorityFilter);
    }
    rows = [...rows].sort((a, b) => {
      if (sortBy === "score") return b.score - a.score;
      if (sortBy === "newest") return new Date(b.created_at) - new Date(a.created_at) || b.id.localeCompare(a.id);
      const pd = PRIORITY_ORDER[a.priority] - PRIORITY_ORDER[b.priority];
      return pd !== 0 ? pd : b.score - a.score;
    });
    return limit ? rows.slice(0, limit) : rows;
  }, [cases, priorityFilter, sortBy, limit]);

  if (!cases || cases.length === 0) {
    return (
      <div className="empty-state">
        No investigation cases yet. Click "Analyze Procurement" to run the detection pipeline.
      </div>
    );
  }

  return (
    <div>
      {showControls && (
        <div className="case-controls">
          <div className="filter-bar">
            {FILTERS.map((f) => (
              <button
                key={f}
                className={`filter-btn${priorityFilter === f ? " active" : ""}`}
                onClick={() => setPriorityFilter(f)}
                type="button"
              >
                {f === "ALL" ? "All" : f.charAt(0) + f.slice(1).toLowerCase()}
                <span className="filter-count">{counts[f] ?? 0}</span>
              </button>
            ))}
          </div>
          <label className="sort-control">
            Sort
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              {SORTS.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
          </label>
        </div>
      )}

      {showControls && (
        <div className="showing-count">
          Showing {visible.length} of {cases.length} case{cases.length === 1 ? "" : "s"}
        </div>
      )}

      {visible.length === 0 ? (
        <div className="empty-state">No cases match this filter.</div>
      ) : (
        <div className="evidence-table-wrap">
          <table>
            <thead>
              <tr>
                <th>Case ID</th>
                <th>Priority</th>
                <th>Score</th>
                <th>Primary Entity</th>
                <th>Tender</th>
                <th>Signals</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((c) => (
                <tr key={c.id} className="clickable" onClick={() => navigate(`/cases/${c.id}`)}>
                  <td className="mono">{c.id}</td>
                  <td>
                    <PriorityBadge priority={c.priority} />
                  </td>
                  <td>{c.score.toFixed(1)}</td>
                  <td>{c.primary_entity || <span className="muted">—</span>}</td>
                  <td className="mono">{c.primary_tender || <span className="muted">—</span>}</td>
                  <td>
                    <div className="chip-row">
                      {c.signal_types.map((t) => (
                        <span key={t} className="badge badge-type">
                          {t.replaceAll("_", " ")}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td>
                    <span className="badge badge-status">{c.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
