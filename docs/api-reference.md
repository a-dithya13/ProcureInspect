# REST API Reference

The ProcureLens backend exposes a lightweight REST API powered by FastAPI.

- **Base URL**: `http://localhost:8000/api`
- **Interactive Swagger UI**: `http://localhost:8000/docs`
- **OpenAPI Schema (JSON)**: `http://localhost:8000/openapi.json`

---

## Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/overview` | Aggregated system metrics, case counts, and priority distribution |
| `GET` | `/api/tenders` | List of all procurement tenders |
| `GET` | `/api/vendors` | List of all registered vendors |
| `GET` | `/api/vendors/{vendor_id}` | Detailed vendor profile with bids, awards, and linked investigation cases |
| `GET` | `/api/cases` | All investigation cases sorted by priority score |
| `GET` | `/api/cases/{case_id}` | Detailed case payload: signals, evidence, audit focus, and Cytoscape graph |
| `POST` | `/api/analyze` | Triggers the end-to-end detection and convergence pipeline |

---

## Endpoint Details

### 1. `GET /api/overview`
Returns high-level statistics for the dashboard header and charts.

#### Response Example (`200 OK`)
```json
{
  "total_vendors": 215,
  "total_tenders": 520,
  "total_bids": 2140,
  "total_awards": 520,
  "total_signals": 12,
  "total_cases": 5,
  "priority_distribution": {
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 2
  }
}
```

---

### 2. `POST /api/analyze`
Executes all 5 anomaly detectors across current database records, groups overlapping signals into cases using connected components, computes priority scores, and persists results.

#### Response Example (`200 OK`)
```json
{
  "signals_detected": 12,
  "cases_created": 5,
  "duration_seconds": 0.42
}
```

---

### 3. `GET /api/cases`
Returns a list of all identified investigation cases, ordered descending by `score` (0-100).

#### Response Example (`200 OK`)
```json
[
  {
    "id": "C0001",
    "priority": "HIGH",
    "score": 95.0,
    "status": "OPEN",
    "vendor_ids": ["V0201", "V0202"],
    "tender_ids": ["T0001", "T0002", "T0003", "T0004", "T0005", "T0006"],
    "signal_ids": ["S0001", "S0002", "S0003", "S0004"],
    "signal_types": [
      "BID_SIMILARITY",
      "PRICE_DEVIATION",
      "REPEATED_PARTICIPATION",
      "WINNER_CONCENTRATION"
    ],
    "vendor_names": ["Apex Roadworks Ltd", "Beacon Paving Corp"],
    "explanation": "High-priority investigation case involving 2 vendors and 6 tenders with 4 converging signals: BID_SIMILARITY, PRICE_DEVIATION, REPEATED_PARTICIPATION, WINNER_CONCENTRATION."
  }
]
```

---

### 4. `GET /api/cases/{case_id}`
Retrieves complete case audit data, including underlying signals, structured evidence items, recommendation narrative, and graph structure.

#### Response Example (`200 OK`)
```json
{
  "id": "C0001",
  "priority": "HIGH",
  "score": 95.0,
  "status": "OPEN",
  "vendor_ids": ["V0201", "V0202"],
  "tender_ids": ["T0001", "T0002", "T0003", "T0004", "T0005", "T0006"],
  "signal_ids": ["S0001", "S0002", "S0003", "S0004"],
  "explanation": "High-priority investigation case involving 2 vendors...",
  "recommended_investigation": "1. Verify the pricing justification for tender T0006...\n2. Review the award history of vendor V0201...",
  "vendors": [
    {
      "id": "V0201",
      "name": "Apex Roadworks Ltd",
      "category": "Road Maintenance",
      "location": "Springfield"
    }
  ],
  "tenders": [
    {
      "id": "T0001",
      "title": "Springfield Highway Resurfacing Phase 1",
      "department": "Department of Transportation",
      "category": "Road Maintenance",
      "location": "Springfield",
      "estimated_value": 450000.0,
      "date": "2024-01-15"
    }
  ],
  "signals": [
    {
      "id": "S0001",
      "signal_type": "PRICE_DEVIATION",
      "severity": "HIGH",
      "score": 0.88,
      "explanation": "Winning price for tender T0006 is 44.2% higher than the peer median...",
      "tender_ids": ["T0006"],
      "vendor_ids": ["V0201"],
      "evidence": [...]
    }
  ],
  "graph": {
    "nodes": [
      {
        "id": "V0201",
        "label": "Apex Roadworks Ltd",
        "type": "vendor",
        "data": { "category": "Road Maintenance", "location": "Springfield" }
      },
      {
        "id": "T0001",
        "label": "Springfield Highway Resurfacing Phase 1",
        "type": "tender",
        "data": { "estimated_value": 450000.0 }
      }
    ],
    "edges": [
      {
        "source": "V0201",
        "target": "T0001",
        "type": "AWARD",
        "data": { "amount": 448000.0, "award_date": "2024-01-20" }
      }
    ]
  }
}
```

---

### 5. `GET /api/vendors/{vendor_id}`
Returns profile details for an individual vendor along with historical bids, awards, and linked investigation cases.

#### Response Example (`200 OK`)
```json
{
  "vendor": {
    "id": "V0201",
    "name": "Apex Roadworks Ltd",
    "category": "Road Maintenance",
    "location": "Springfield"
  },
  "bids": [
    {
      "id": "B0001",
      "tender_id": "T0001",
      "vendor_id": "V0201",
      "amount": 448000.0,
      "rank": 1
    }
  ],
  "awards": [
    {
      "id": "A0001",
      "tender_id": "T0001",
      "vendor_id": "V0201",
      "amount": 448000.0,
      "award_date": "2024-01-20"
    }
  ],
  "cases": [
    {
      "id": "C0001",
      "priority": "HIGH",
      "score": 95.0,
      "status": "OPEN",
      "signal_types": ["PRICE_DEVIATION", "WINNER_CONCENTRATION", "REPEATED_PARTICIPATION", "BID_SIMILARITY"]
    }
  ]
}
```
