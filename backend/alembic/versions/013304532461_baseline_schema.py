"""baseline schema

Represents the schema as it existed before Alembic was introduced (tables
created ad hoc via Base.metadata.create_all()): no foreign keys on
bids/awards, and RiskSignal/InvestigationCase storing related ids as raw
JSON arrays. This revision is what a brand-new environment starts from; the
live Supabase database was `alembic stamp`-ed at this revision rather than
having it re-run, since its tables already matched this shape exactly.

Revision ID: 013304532461
Revises:
Create Date: 2026-09-13 22:14:04.863723

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '013304532461'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vendors",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
    )

    op.create_table(
        "tenders",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("department", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("estimated_value", sa.Float(), nullable=False),
        sa.Column("date", sa.String(), nullable=False),
    )

    op.create_table(
        "bids",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("tender_id", sa.String(), nullable=False),
        sa.Column("vendor_id", sa.String(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
    )

    op.create_table(
        "awards",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("tender_id", sa.String(), nullable=False),
        sa.Column("vendor_id", sa.String(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("award_date", sa.String(), nullable=False),
    )

    op.create_table(
        "risk_signals",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("signal_type", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("explanation", sa.String(), nullable=False),
        sa.Column("tender_ids", sa.JSON(), nullable=False),
        sa.Column("vendor_ids", sa.JSON(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
    )

    op.create_table(
        "investigation_cases",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("priority", sa.String(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("vendor_ids", sa.JSON(), nullable=False),
        sa.Column("tender_ids", sa.JSON(), nullable=False),
        sa.Column("signal_ids", sa.JSON(), nullable=False),
        sa.Column("explanation", sa.String(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("recommended_investigation", sa.String(), nullable=False),
    )

    op.create_table(
        "analysis_runs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("run_at", sa.DateTime(), nullable=False),
        sa.Column("signals_detected", sa.Integer(), nullable=False),
        sa.Column("cases_created", sa.Integer(), nullable=False),
        sa.Column("duration_seconds", sa.Float(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("analysis_runs")
    op.drop_table("investigation_cases")
    op.drop_table("risk_signals")
    op.drop_table("awards")
    op.drop_table("bids")
    op.drop_table("tenders")
    op.drop_table("vendors")
