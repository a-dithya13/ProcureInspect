# ProcureLens 🔍

**Automated Public-Procurement Investigation Support & Anomaly Convergence Engine**

ProcureLens is an open-source investigative intelligence prototype designed for public procurement auditors, oversight agencies, and fraud analysts. It ingests procurement data (vendors, tenders, bids, awards), runs five transparent statistical and network anomaly detectors, converges overlapping signals into unified **Investigation Cases**, and delivers a prioritized worklist with full audit evidence and interactive relationship graphs.

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![Vite](https://img.shields.io/badge/Bundler-Vite-646CFF?style=flat-square&logo=vite)](https://vitejs.dev)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-4169E1?style=flat-square&logo=postgresql)](https://www.postgresql.org)
[![NetworkX](https://img.shields.io/badge/Graph_Analytics-NetworkX-blue?style=flat-square)](https://networkx.org)

---

## 📖 Table of Contents

- [The Basic Idea](#-the-basic-idea)
- [Core Product Principle](#️-core-product-principle)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start & Installation](#-quick-start--installation)
  - [Prerequisites](#prerequisites)
  - [1. Clone Repository](#1-clone-repository)
  - [2. Backend Setup](#2-backend-setup)
  - [3. Environment Configuration](#3-environment-configuration)
  - [4. Run Database Migrations](#4-run-database-migrations)
  - [5. Generate Synthetic Dataset](#5-generate-synthetic-dataset)
  - [6. Launch Backend Server](#6-launch-backend-server)
  - [7. Launch Frontend Client](#7-launch-frontend-client)
  - [8. Run Procurement Analysis](#8-run-procurement-analysis)
- [The 5 Anomaly Detectors](#-the-5-anomaly-detectors)
- [Interactive Demo Walkthrough](#-interactive-demo-walkthrough)
- [API Overview](#-api-overview)
- [In-Depth Documentation](#-in-depth-documentation)
- [Limitations & Future Roadmap](#-limitations--future-roadmap)

---

## 💡 The Basic Idea

Public procurement represents trillions in public spending annually. Manual oversight across thousands of tenders and bids is slow and error-prone. Isolated statistical anomalies (e.g. a high win rate or a slightly close bid) happen frequently by coincidence, but when multiple independent signals overlap on the same suppliers and tenders, the case warrants investigator review.

ProcureLens solves this by:
1. **Evaluating localized peer baselines** for pricing, winner concentration, and competition levels.
2. **Identifying network anomalies** like recurring co-bidding pairs and razor-thin bid margins.
3. **Clustering intersecting anomalies** into actionable **Investigation Cases** using graph connected components.
4. **Ranking cases with an Investigation Priority Score (0–100)** to focus limited investigator resources where evidence is strongest.
5. **Providing visual audit trails** and interactive entity relationship graphs for immediate context.

---

## ⚖️ Core Product Principle

> **ProcureLens never asserts fraud or corruption.**

ProcureLens is strictly a **decision-support tool** for human investigators:
- It highlights statistical anomalies, evidence strength, and investigation priority.
- All UI labels, API payloads, and generated summaries adhere to non-accusatory language (e.g., *"Investigation Priority: HIGH"* or *"Review repeated participation pattern"*).
- Every threshold and calculation is transparent, deterministic, and auditable.

---

## 🛠️ Tech Stack

| Tier | Technologies |
|---|---|
| **Frontend** | React 18, Vite, React Router 6, Axios, Recharts, Cytoscape.js |
| **Backend** | Python 3.12+, FastAPI, Pydantic v2, Uvicorn |
| **Data & Graph Analytics** | Pandas, NumPy, NetworkX |
| **Database** | PostgreSQL (hosted on Supabase or local instance) via SQLAlchemy 2 & Psycopg 3, schema managed by **Alembic** |

---

## 📂 Project Structure

```
MHash/
├── README.md                      # Primary project overview & setup guide
├── docs/                          # In-depth technical documentation folder
│   ├── README.md                  # Documentation hub and architecture overview
│   ├── architecture.md            # System architecture, pipeline flow, and scoring math
│   ├── detectors.md               # Detailed formulas and thresholds for all 5 detectors
│   ├── data-models.md             # Database models, ER diagrams, and schema definitions
│   ├── api-reference.md           # Complete REST API documentation
│   └── synthetic-data.md          # Synthetic data generator & planted scenario guide
├── backend/
│   ├── main.py                    # FastAPI entrypoint, CORS setup, router registration
│   ├── database/
│   │   └── db.py                  # SQLAlchemy engine & session factory
│   ├── alembic/
│   │   ├── env.py                 # Loads DATABASE_URL from .env, targets models/orm.py metadata
│   │   └── versions/              # 0001 baseline schema -> 0002 FKs + junction tables
│   ├── models/
│   │   ├── orm.py                 # PostgreSQL ORM models (FK-linked Vendor/Tender/Bid/Award, junction tables)
│   │   └── schemas.py             # Pydantic request/response schemas
│   ├── detection/                 # The 5 Anomaly Detectors
│   │   ├── common.py              # Shared statistical utilities & severity clampers
│   │   ├── price.py               # PRICE_DEVIATION detector
│   │   ├── winner.py              # WINNER_CONCENTRATION detector
│   │   ├── participation.py       # REPEATED_PARTICIPATION detector
│   │   ├── bid_similarity.py      # BID_SIMILARITY detector
│   │   └── competition.py         # COMPETITION_ANOMALY detector
│   ├── cases/
│   │   └── case_engine.py         # Signal convergence, priority scoring & recommendations
│   ├── graph/
│   │   └── procurement_graph.py   # Cytoscape bipartite graph builder
│   ├── services/
│   │   └── analysis_service.py    # Pipeline orchestrator (Ingest -> Detect -> Cluster -> Persist)
│   ├── api/                       # REST API Route Handlers
│   │   ├── overview.py            # /api/overview stats
│   │   ├── tenders.py             # /api/tenders
│   │   ├── vendors.py             # /api/vendors
│   │   ├── cases.py               # /api/cases
│   │   └── analyze.py             # /api/analyze
│   └── requirements.txt           # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── pages/                 # Dashboard, CaseDetail, VendorDetail
│   │   ├── components/            # StatCard, PriorityBadge, RelationshipGraph, CasesTable
│   │   ├── services/api.js        # Axios API client
│   │   └── App.jsx                # Router & main layout
│   └── package.json               # Frontend dependencies & scripts
└── scripts/
    ├── generate_data.py           # Synthetic dataset generator with 6 planted scenarios
    └── ground_truth.json          # Verification record of planted ground truth scenarios
```

---

## 🚀 Quick Start & Installation

Follow these steps once you clone the repository to get the full stack running locally.

### Prerequisites
- **Python 3.12+** ([python.org](https://www.python.org/downloads/))
- **Node.js 18+ & npm** ([nodejs.org](https://nodejs.org/))
- **PostgreSQL Database** (a free [Supabase](https://supabase.com) Postgres database or local PostgreSQL instance)

---

### 1. Clone Repository

```bash
git clone https://github.com/your-username/MHash.git
cd MHash
```

---

### 2. Backend Setup

Create and activate a Python virtual environment, then install backend dependencies:

**Windows (PowerShell / Command Prompt):**
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**macOS / Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 3. Environment Configuration

Ensure a `.env` file exists in the `backend/` directory with your PostgreSQL connection URL:

`backend/.env`:
```env
DATABASE_URL=postgresql+psycopg://username:password@hostname:5432/postgres
```
*(Note: If using Supabase, obtain the direct or pooled transaction URL from your project database settings).*

---

### 4. Run Database Migrations

Schema is managed by Alembic, not by the app itself. Run this once (and again after pulling any future schema change):

```bash
# From the backend directory with venv activated:
python -m alembic upgrade head
```

This creates `vendors`, `tenders`, `bids`/`awards` (with foreign keys to them), `risk_signals`/`investigation_cases`, and their junction tables (`risk_signal_tenders`, `risk_signal_vendors`, `case_vendors`, `case_tenders`, `case_signals`). See [docs/data-models.md](file:///c:/Users/Atharva%20Joshi/Projects/MHash/docs/data-models.md) for the full schema and migration history.

---

### 5. Generate Synthetic Dataset

Run the generator script to seed ~200 vendors, ~500 tenders, and ~2,000 bids with planted test scenarios. It assumes the schema from step 4 already exists -- it only clears and reloads data, it never creates or drops tables.

**Windows:**
```powershell
# From the backend directory with venv activated:
python ..\scripts\generate_data.py
```

**macOS / Linux:**
```bash
# From the backend directory with venv activated:
python ../scripts/generate_data.py
```

---

### 6. Launch Backend Server

Start the FastAPI application with Uvicorn:

```bash
uvicorn main:app --reload --port 8000
```
- **Backend API**: `http://localhost:8000`
- **Swagger Documentation**: `http://localhost:8000/docs`

---

### 7. Launch Frontend Client

Open a new terminal window, navigate to the `frontend/` directory, install packages, and launch Vite:

```bash
cd frontend
npm install
npm run dev
```
- **Web Application**: `http://localhost:5173`

---

### 8. Run Procurement Analysis

1. Open `http://localhost:5173` in your browser.
2. Click the **"Analyze Procurement"** button on the top right of the dashboard.
3. *Alternatively*, trigger the analysis via cURL in your terminal:
   ```bash
   curl -X POST http://localhost:8000/api/analyze
   ```
4. The dashboard will populate with statistical metrics, priority charts, and clustered investigation cases.

---

## 🔬 The 5 Anomaly Detectors

Each detector analyzes specific patterns against peer-group baselines (same category & region):

1. **PRICE_DEVIATION** (`backend/detection/price.py`):
   Compares winning price to peer baselines ($n \ge 5$ z-score $\ge 2.5$ or $\ge 40\%$ deviation from peer median).
2. **WINNER_CONCENTRATION** (`backend/detection/winner.py`):
   Flags vendors winning $\ge 60\%$ of comparable tenders they bid on ($\ge 4$ tenders).
3. **REPEATED_PARTICIPATION** (`backend/detection/participation.py`):
   Flags vendor pairs with unusually high co-bidding ($\mu + 3\sigma$ threshold and $\ge 50\%$ overlap ratio).
4. **BID_SIMILARITY** (`backend/detection/bid_similarity.py`):
   Flags co-participating vendor pairs whose bids sit within $\le 4\%$ of tender estimated value across $\ge 3$ tenders.
5. **COMPETITION_ANOMALY** (`backend/detection/competition.py`):
   Flags tenders receiving $\ge 2$ fewer bids than the peer median for comparable procurements.

For mathematical formulas and baseline calculations, see [docs/detectors.md](file:///c:/Users/Atharva%20Joshi/Projects/MHash/docs/detectors.md).

---

## 🖥️ Interactive Demo Walkthrough

1. **Dashboard Overview**: Inspect total vendors, tenders, bids, and the case priority distribution.
2. **Run Analysis**: Click **"Analyze Procurement"** to run the detector suite in $<1$ second.
3. **Inspect Top High-Priority Case**: Open the top case (planted convergence scenario with vendors `V0201` and `V0202`).
4. **Review Evidence**: Examine the underlying peer prices, co-bid tenders, and razor-thin bid differentials.
5. **Explore Relationship Graph**: Interact with the Cytoscape graph showing vendors, tenders, bids, and winning award edges.
6. **Actionable Focus**: Review the auto-generated, non-accusatory recommended investigation checklist.

---

## 🌐 API Overview

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/overview` | Summary counts and priority distribution |
| `GET` | `/api/tenders` | List of all tenders |
| `GET` | `/api/vendors` | List of all vendors |
| `GET` | `/api/vendors/{id}` | Vendor profile, bid history, awards, and associated cases |
| `GET` | `/api/cases` | All cases sorted by priority score |
| `GET` | `/api/cases/{id}` | Detailed case audit view with signals, evidence, and Cytoscape graph |
| `POST` | `/api/analyze` | Executes detection pipeline and updates database |

For request/response schemas and examples, see [docs/api-reference.md](file:///c:/Users/Atharva%20Joshi/Projects/MHash/docs/api-reference.md).

---

## 📚 In-Depth Documentation

Detailed guides and technical references are located in the [`docs/`](file:///c:/Users/Atharva%20Joshi/Projects/MHash/docs/README.md) folder:

- 🏗️ [Architecture & Priority Math](file:///c:/Users/Atharva%20Joshi/Projects/MHash/docs/architecture.md)
- 🔬 [Detectors & Statistical Thresholds](file:///c:/Users/Atharva%20Joshi/Projects/MHash/docs/detectors.md)
- 🗄️ [Data Models & Schema Reference](file:///c:/Users/Atharva%20Joshi/Projects/MHash/docs/data-models.md)
- 🔌 [REST API Reference](file:///c:/Users/Atharva%20Joshi/Projects/MHash/docs/api-reference.md)
- 🧪 [Synthetic Data & Ground Truth Scenarios](file:///c:/Users/Atharva%20Joshi/Projects/MHash/docs/synthetic-data.md)

---

## ⚠️ Limitations & Future Roadmap

- **Synthetic Data**: Seeded dataset for prototyping and evaluation.
- **Stateless Re-runs**: `/api/analyze` performs a clean evaluation on each run.
- **Planned Enhancements**:
  - Investigator case status workflows (Open $\rightarrow$ Under Review $\rightarrow$ Cleared $\rightarrow$ Escalated).
  - Configurable detector threshold controls directly from the UI.
  - Multi-factor peer group weighting (inflation adjustments, contract specification similarity).
