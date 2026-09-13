# ProcureLens Frontend Client 🖥️

This directory houses the React 18 Single-Page Application (SPA) for **ProcureLens**, built using [Vite](https://vitejs.dev), [React Router](https://reactrouter.com/), [Recharts](https://recharts.org/), and [Cytoscape.js](https://js.cytoscape.org/).

---

## 🛠️ Tech Stack & Key Libraries

- **React 18 & Vite**: Fast development server and optimized production bundling.
- **Cytoscape.js**: Interactive bipartite graph visualization mapping vendors, tenders, bids, and contract awards.
- **Recharts**: Responsive chart components for priority distribution and risk metrics.
- **Axios**: HTTP client configured for the FastAPI backend (`/api/*`).
- **Lucide Icons**: Modern icons for investigation indicators and severity tags.

---

## 🚀 Setup & Development

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Development Server
```bash
npm run dev
```
The application will launch on `http://localhost:5173`.

### 3. Build for Production
```bash
npm run build
```

---

## 📂 Directory Structure

```
frontend/
├── src/
│   ├── components/            # Reusable UI widgets
│   │   ├── CasesTable.jsx     # Sortable/filterable table of investigation cases
│   │   ├── PriorityBadge.jsx  # HIGH / MEDIUM / LOW severity tags
│   │   ├── PriorityChart.jsx  # Recharts breakdown of cases by priority
│   │   ├── RelationshipGraph.jsx # Interactive Cytoscape.js bipartite graph
│   │   ├── SignalCard.jsx     # Expandable evidence card for individual signals
│   │   └── StatCard.jsx       # Metric summary cards
│   ├── pages/                 # Route views
│   │   ├── Dashboard.jsx      # Overview stats, priority distribution, analysis trigger
│   │   ├── CaseDetail.jsx     # Deep dive: converging signals, evidence audit, graph
│   │   └── VendorDetail.jsx   # Vendor profile, bid history, and associated cases
│   ├── services/
│   │   └── api.js             # Centralized Axios API service
│   ├── App.jsx                # Router configuration & main navigation layout
│   └── main.jsx               # React entrypoint
├── package.json
└── vite.config.js
```

---

## 🔗 Main Project Documentation

For full system architecture, detector documentation, and backend setup, see the root [README.md](file:///c:/Users/Atharva%20Joshi/Projects/MHash/README.md) and the [`docs/`](file:///c:/Users/Atharva%20Joshi/Projects/MHash/docs/README.md) folder.
