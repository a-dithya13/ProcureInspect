# Anomaly Detectors Reference

ProcureLens implements five deterministic, statistical and network detectors in `backend/detection/`. Each detector evaluates specific anomalous procurement patterns against localized peer-group baselines.

All detector thresholds are named, visible constants at the top of each module — no opaque black-box machine learning models are used.

---

## 1. Price Deviation (`PRICE_DEVIATION`)

- **Module**: `backend/detection/price.py`
- **Objective**: Identifies winning tenders whose awarded price deviates significantly from comparable tenders awarded within the same category and location.

### Normalization & Comparability
To ensure equitable comparison across tenders of varying scope, each award is normalized as:
$$\text{Price Ratio} = \frac{\text{Award Amount}}{\text{Estimated Tender Value}}$$

### Peer Group Selection
1. Filters peer tenders in the same `category` and `location`.
2. If fewer than `MIN_PEERS_REQUIRED = 3` peers exist locally, falls back to all tenders in the same `category` across all locations.
3. If still fewer than 3 peers exist, no baseline can be established and no signal is produced.

### Detection Thresholds & Formulas
- **Large Peer Groups ($n \ge 5$)**:
  Uses z-score test against the peer distribution:
  $$z = \frac{\text{ratio} - \text{median}(\text{peer\_ratios})}{\text{std}(\text{peer\_ratios})}$$
  - **Flagged if**: $|z| \ge 2.5$ (`ZSCORE_THRESHOLD`)
  - **Score**: $\text{clamp}(|z| / 5.0, 0.4, 1.0)$

- **Small Peer Groups ($3 \le n < 5$)**:
  Uses percentage deviation from median:
  $$\text{pct\_dev} = \frac{\text{ratio} - \text{median}}{\text{median}}$$
  - **Flagged if**: $|\text{pct\_dev}| \ge 0.40$ (`PCT_DEVIATION_THRESHOLD`, 40% deviation)
  - **Score**: $\text{clamp}(|\text{pct\_dev}| / 1.0, 0.4, 1.0)$

---

## 2. Winner Concentration (`WINNER_CONCENTRATION`)

- **Module**: `backend/detection/winner.py`
- **Objective**: Flags vendors that win an abnormally high proportion of comparable tenders within a category and location.

### Baseline & Thresholds
- `MIN_GROUP_SIZE = 4`: Minimum number of distinct tenders in the peer group.
- `MIN_PARTICIPATED = 4`: Minimum tenders the specific vendor must have bid on in this group.
- `WIN_PCT_THRESHOLD = 0.60` (60% win rate).

### Formula & Scoring
$$\text{Win Rate} = \frac{\text{Number of Wins by Vendor in Peer Group}}{\text{Total Bids by Vendor in Peer Group}}$$
- **Flagged if**: $\text{Win Rate} \ge 0.60$ and $\ge 1$ win recorded.
- **Score**: $\text{clamp}(\text{Win Rate}, 0.0, 1.0)$

---

## 3. Repeated Participation (`REPEATED_PARTICIPATION`)

- **Module**: `backend/detection/participation.py`
- **Objective**: Flags pairs of vendors that repeatedly co-bid on the same tenders significantly more frequently than the dataset average.

### Noise Filtering (Overlap Ratio)
High-volume bidders naturally overlap occasionally. To avoid false positives from mere volume, the detector computes:
$$\text{Overlap Ratio}(v_1, v_2) = \frac{\text{Shared Tenders}(v_1, v_2)}{\min(\text{Total Bids}(v_1), \text{Total Bids}(v_2))}$$
A pairing is only flagged if $\text{Overlap Ratio} \ge 0.50$ (`MIN_OVERLAP_RATIO`), meaning the shared tenders represent at least 50% of the less-active vendor's lifetime bidding activity.

### Statistical Outlier Cutoff
- Computes mean $\mu$ and standard deviation $\sigma$ across all co-bidding vendor pairs in the dataset.
- $\text{Threshold} = \max(4, \mu + 3\sigma)$.
- If $\sigma > 10^{-9}$: $z = (\text{shared} - \mu) / \sigma$, $\text{score} = \text{clamp}(z / 5.0, 0.4, 1.0)$.
- Combined with overlap ratio: $\text{Score} = \text{clamp}((\text{score} + \text{ratio}) / 2, 0.4, 1.0)$.

---

## 4. Bid Similarity (`BID_SIMILARITY`)

- **Module**: `backend/detection/bid_similarity.py`
- **Objective**: Flags vendor pairs whose bid submissions are consistently clustered within a razor-thin percentage margin across multiple tenders.

### Thresholds & Evaluation
- `MIN_SHARED_TENDERS = 3`: Must co-bid across at least 3 shared tenders.
- `MIN_OVERLAP_RATIO = 0.50`: Must meet the co-participation significance filter.
- `MAX_NORMALIZED_DIFF = 0.04` (4% average difference):
  $$\text{Normalized Diff} = \frac{|\text{Bid}_A - \text{Bid}_B|}{\text{Tender Estimated Value}}$$
  $$\text{Mean Diff} = \frac{1}{|T_{\text{shared}}|} \sum_{t \in T_{\text{shared}}} \text{Normalized Diff}_t$$

### Scoring
$$\text{Score} = \text{clamp}\left(1.0 - \frac{\text{Mean Diff}}{\text{MAX\_NORMALIZED\_DIFF}}, 0.4, 1.0\right)$$
Closer bids (smaller margin) yield a higher evidence strength score.

---

## 5. Competition Anomaly (`COMPETITION_ANOMALY`)

- **Module**: `backend/detection/competition.py`
- **Objective**: Detects tenders that experienced unexpectedly low competition compared to peers in the same category and location.

### Baseline & Thresholds
- `MIN_PEER_GROUP = 5`: At least 5 peer tenders required to establish a peer baseline.
- `MIN_GAP = 2`: Tender must receive at least 2 fewer bids than the peer median.

### Formula & Scoring
$$\text{Gap} = \text{median}(\text{Peer Bidder Counts}) - \text{Current Bidder Count}$$
- **Flagged if**: $\text{Gap} \ge 2$.
- **Score**: $\text{clamp}\left(\frac{\text{Gap}}{\max(\text{Peer Median}, 1.0)}, 0.35, 1.0\right)$.

---

## Summary of Detector Constants

| Detector | Primary Threshold | Min Sample Size | Output Severity |
|---|---|---|---|
| `PRICE_DEVIATION` | $|z| \ge 2.5$ or $|\text{dev}| \ge 40\%$ | $n \ge 3$ ($n \ge 5$ for z-score) | Dynamic (from score) |
| `WINNER_CONCENTRATION` | $\text{Win Rate} \ge 60\%$ | $\ge 4$ tenders in group | Dynamic (from score) |
| `REPEATED_PARTICIPATION` | $\mu + 3\sigma$ co-bids & $\text{Overlap} \ge 50\%$ | $\ge 4$ shared tenders | Dynamic (from score) |
| `BID_SIMILARITY` | Average diff $\le 4\%$ of value | $\ge 3$ shared tenders | Dynamic (from score) |
| `COMPETITION_ANOMALY` | $\ge 2$ bidders below peer median | $\ge 5$ peer tenders | Dynamic (from score) |
