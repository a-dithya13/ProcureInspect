const TAG_CLASS = {
  "HIGH SIGNAL": "tag-high-signal",
  ELEVATED: "tag-elevated",
  "LOW SIGNAL": "tag-low-signal",
  NEUTRAL: "tag-neutral",
};

/**
 * Displays a tender owner's (department's) detected-pattern-density tag.
 * Deliberately styled differently from case PRIORITY badges (red/amber/slate)
 * so an aggregate "signal density around this entity" reading is never
 * confused with a specific case's investigation priority.
 */
export default function OwnerSignalBadge({ signal, compact = false }) {
  if (!signal) return null;
  const cls = TAG_CLASS[signal.tag] || "tag-neutral";

  return (
    <div className={`owner-signal ${cls}`}>
      <div className="owner-signal-tag">{signal.tag}</div>
      {!compact && (
        <div className="owner-signal-meta">
          {signal.case_count} investigation case{signal.case_count === 1 ? "" : "s"} &middot;{" "}
          {signal.signal_count} detected signal{signal.signal_count === 1 ? "" : "s"}
        </div>
      )}
    </div>
  );
}
