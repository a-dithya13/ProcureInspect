export default function PriorityBadge({ priority }) {
  const cls = { HIGH: "badge-high", MEDIUM: "badge-medium", LOW: "badge-low" }[priority] || "badge-low";
  return <span className={`badge ${cls}`}>{priority}</span>;
}
