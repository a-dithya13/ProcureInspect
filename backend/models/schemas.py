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
    metrics: dict[str, Any] = {}


class CaseSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    priority: str
    score: float
    status: str
    created_at: str
    vendor_ids: list[str]
    tender_ids: list[str]
    signal_ids: list[str]
    signal_types: list[str]
    vendor_names: list[str]
    primary_entity: Optional[str] = None
    primary_tender: Optional[str] = None
    explanation: str


class TenderOwnerSignalOut(BaseModel):
    """Deterministic rollup of detected activity around a tender-owning
    department. Describes pattern density, never a finding of misconduct."""
    name: str
    tag: str  # HIGH SIGNAL | ELEVATED | LOW SIGNAL | NEUTRAL
    case_count: int
    signal_count: int
    high_signal_count: int


class TenderWithOwnerOut(TenderOut):
    owner_signal: Optional[TenderOwnerSignalOut] = None


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
    created_at: str
    vendors: list[VendorOut]
    tenders: list[TenderWithOwnerOut]
    signals: list[RiskSignalOut]
    explanation: str
    evidence: list[dict[str, Any]]
    recommended_investigation: list[str]
    graph: GraphData


class VendorDetailOut(BaseModel):
    vendor: VendorOut
    bids: list[BidOut]
    awards: list[AwardOut]
    cases: list[CaseSummaryOut]


class TenderDetailOut(BaseModel):
    tender: TenderWithOwnerOut
    bids: list[BidOut]
    award: Optional[AwardOut] = None
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
    high_priority_cases: int
    vendors_under_review: int
    priority_distribution: PriorityDistribution
    last_analysis_run: Optional[str] = None


class AnalyzeResultOut(BaseModel):
    signals_detected: int
    cases_created: int
    priority_distribution: PriorityDistribution
    duration_seconds: float
