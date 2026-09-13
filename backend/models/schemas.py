"""Pydantic response schemas for the ProcureLens API."""
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class VendorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    category: str
    location: str


class TenderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    department: str
    category: str
    location: str
    estimated_value: float
    date: str


class BidOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tender_id: str
    vendor_id: str
    amount: float
    rank: int


class AwardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tender_id: str
    vendor_id: str
    amount: float
    award_date: str


class RiskSignalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    signal_type: str
    severity: str
    score: float
    explanation: str
    tender_ids: list[str]
    vendor_ids: list[str]
    evidence: list[dict[str, Any]]


class CaseSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    priority: str
    score: float
    status: str
    vendor_ids: list[str]
    tender_ids: list[str]
    signal_ids: list[str]
    signal_types: list[str]
    vendor_names: list[str]
    explanation: str


class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # "vendor" | "tender"
    detail: Optional[dict[str, Any]] = None


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str  # "bid" | "award"
    detail: Optional[dict[str, Any]] = None


class GraphData(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class CaseDetailOut(BaseModel):
    id: str
    priority: str
    score: float
    status: str
    vendors: list[VendorOut]
    tenders: list[TenderOut]
    signals: list[RiskSignalOut]
    explanation: str
    evidence: list[dict[str, Any]]
    recommended_investigation: str
    graph: GraphData


class VendorDetailOut(BaseModel):
    vendor: VendorOut
    bids: list[BidOut]
    awards: list[AwardOut]
    cases: list[CaseSummaryOut]


class PriorityDistribution(BaseModel):
    HIGH: int
    MEDIUM: int
    LOW: int


class OverviewOut(BaseModel):
    total_tenders: int
    total_vendors: int
    total_bids: int
    total_awards: int
    total_signals: int
    total_cases: int
    priority_distribution: PriorityDistribution
    last_analysis_run: Optional[str] = None


class AnalyzeResultOut(BaseModel):
    signals_detected: int
    cases_created: int
    priority_distribution: PriorityDistribution
    duration_seconds: float
