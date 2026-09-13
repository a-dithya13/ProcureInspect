import { Link } from "react-router-dom";

// Matches, in order of priority: entity IDs (T0006, V0201, S0012, C0003),
// percentages (18.7%, +69.3%, -60%), and comma-grouped/decimal amounts
// (1,065,815.07). Plain small integers (e.g. "n=15 peers") are left alone
// so highlighting stays restrained to the evidence that actually matters.
const TOKEN_RE = /\b([TVSC]\d{4})\b|([+-]?\d+(?:\.\d+)?%)|(\d{1,3}(?:,\d{3})+(?:\.\d+)?)/g;

function idHref(id) {
  if (id.startsWith("T")) return `/tenders/${id}`;
  if (id.startsWith("V")) return `/vendors/${id}`;
  return null;
}

/**
 * Renders backend-generated evidence sentences with entities, tender/vendor
 * IDs, percentages and monetary amounts picked out -- using structured regex
 * over OUR OWN generated text format (fixed ID shapes, fixed number
 * formatting), not free-text guessing.
 */
export default function EvidenceText({ text }) {
  if (!text) return null;

  const parts = [];
  let lastIndex = 0;
  let match;
  let key = 0;
  TOKEN_RE.lastIndex = 0;

  while ((match = TOKEN_RE.exec(text)) !== null) {
    if (match.index > lastIndex) parts.push(text.slice(lastIndex, match.index));
    const [, id, percent, number] = match;

    if (id) {
      const href = idHref(id);
      parts.push(
        href ? (
          <Link key={key++} to={href} className="evidence-id">{id}</Link>
        ) : (
          <span key={key++} className="evidence-id">{id}</span>
        )
      );
    } else if (percent) {
      parts.push(<strong key={key++} className="evidence-percent">{percent}</strong>);
    } else if (number) {
      parts.push(<strong key={key++} className="evidence-number">{number}</strong>);
    }
    lastIndex = TOKEN_RE.lastIndex;
  }
  if (lastIndex < text.length) parts.push(text.slice(lastIndex));

  return <>{parts}</>;
}
