import cytoscape from "cytoscape";
import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

const STYLE = [
  {
    selector: "node",
    style: {
      label: "data(label)",
      "font-size": 10,
      color: "#1e293b",
      "text-wrap": "ellipsis",
      "text-max-width": "90px",
      "text-valign": "bottom",
      "text-margin-y": 6,
      "background-color": "#94a3b8",
      width: 26,
      height: 26,
      "border-width": 2,
      "border-color": "#ffffff",
    },
  },
  {
    selector: 'node[type = "vendor"]',
    style: { "background-color": "#2563eb", shape: "ellipse" },
  },
  {
    selector: 'node[type = "tender"]',
    style: { "background-color": "#0f766e", shape: "round-rectangle" },
  },
  {
    selector: "node[?is_case_entity]",
    style: {
      "border-width": 3,
      "border-color": "#dc2626",
      width: 34,
      height: 34,
      "font-weight": 700,
    },
  },
  {
    selector: "edge",
    style: {
      width: 1.5,
      "line-color": "#cbd5e1",
      "curve-style": "bezier",
      "target-arrow-shape": "none",
      opacity: 0.85,
    },
  },
  {
    selector: 'edge[type = "award"]',
    style: { "line-color": "#dc2626", width: 3, opacity: 1 },
  },
];

export default function RelationshipGraph({ graph }) {
  const containerRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!containerRef.current || !graph) return;

    const elements = [
      ...graph.nodes.map((n) => ({
        data: { id: n.id, label: n.label, type: n.type, is_case_entity: n.detail?.is_case_entity ?? false },
      })),
      ...graph.edges.map((e) => ({
        data: { id: e.id, source: e.source, target: e.target, type: e.type },
      })),
    ];

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: STYLE,
      layout: { name: "cose", animate: false, padding: 30, nodeRepulsion: 9000 },
      minZoom: 0.3,
      maxZoom: 2.5,
    });

    cy.on("tap", "node[type = \"vendor\"]", (evt) => {
      navigate(`/vendors/${evt.target.id()}`);
    });

    return () => cy.destroy();
  }, [graph, navigate]);

  return (
    <div>
      <div ref={containerRef} className="graph-canvas" />
      <div className="legend">
        <span className="legend-item">
          <span className="legend-swatch" style={{ background: "#2563eb" }} />
          Vendor
        </span>
        <span className="legend-item">
          <span className="legend-swatch" style={{ background: "#0f766e", borderRadius: 3 }} />
          Tender
        </span>
        <span className="legend-item">
          <span className="legend-swatch" style={{ border: "2px solid #dc2626", background: "white" }} />
          Case entity
        </span>
        <span className="legend-item">
          <span className="legend-swatch" style={{ background: "#dc2626", height: 3, width: 16, borderRadius: 0 }} />
          Award
        </span>
        <span className="legend-item">
          <span className="legend-swatch" style={{ background: "#cbd5e1", height: 2, width: 16, borderRadius: 0 }} />
          Bid
        </span>
      </div>
      <div className="muted" style={{ fontSize: 12, marginTop: 6 }}>
        Click a vendor node to open its profile.
      </div>
    </div>
  );
}
