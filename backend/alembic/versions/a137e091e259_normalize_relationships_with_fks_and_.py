"""normalize relationships with fks and junction tables

Adds real foreign keys on bids/awards (tender_id -> tenders.id, vendor_id ->
vendors.id), and replaces the JSON id-array columns on risk_signals and
investigation_cases with proper many-to-many junction tables:

    risk_signal_tenders(signal_id, tender_id)
    risk_signal_vendors(signal_id, vendor_id)
    case_vendors(case_id, vendor_id)
    case_tenders(case_id, tender_id)
    case_signals(case_id, signal_id)

risk_signals and investigation_cases are analysis output regenerated in full
by every POST /api/analyze run (see services/analysis_service.py), so they
are safe to drop and recreate here -- vendors/tenders/bids/awards (the real
procurement data) are only ALTERed, never dropped.

Revision ID: a137e091e259
Revises: 013304532461
Create Date: 2026-09-13 22:14:12.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a137e091e259'
down_revision: Union[str, None] = '013304532461'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- bids / awards: add real foreign keys (data already validated, no orphans) ---
    op.create_foreign_key(
        "fk_bids_tender_id", "bids", "tenders", ["tender_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        "fk_bids_vendor_id", "bids", "vendors", ["vendor_id"], ["id"], ondelete="CASCADE"
    )
    op.create_index("ix_bids_tender_id", "bids", ["tender_id"])
    op.create_index("ix_bids_vendor_id", "bids", ["vendor_id"])

    op.create_foreign_key(
        "fk_awards_tender_id", "awards", "tenders", ["tender_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        "fk_awards_vendor_id", "awards", "vendors", ["vendor_id"], ["id"], ondelete="CASCADE"
    )
    op.create_index("ix_awards_tender_id", "awards", ["tender_id"])
    op.create_index("ix_awards_vendor_id", "awards", ["vendor_id"])

    # --- risk_signals / investigation_cases: drop and recreate without JSON id arrays ---
    # (analysis output only -- regenerated in full by the next POST /api/analyze)
    op.drop_table("risk_signals")
    op.drop_table("investigation_cases")

    op.create_table(
        "risk_signals",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("signal_type", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("explanation", sa.String(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
    )

    op.create_table(
        "investigation_cases",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("priority", sa.String(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("explanation", sa.String(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("recommended_investigation", sa.String(), nullable=False),
    )

    op.create_table(
        "risk_signal_tenders",
        sa.Column("signal_id", sa.String(), sa.ForeignKey("risk_signals.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tender_id", sa.String(), sa.ForeignKey("tenders.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_table(
        "risk_signal_vendors",
        sa.Column("signal_id", sa.String(), sa.ForeignKey("risk_signals.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("vendor_id", sa.String(), sa.ForeignKey("vendors.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_table(
        "case_vendors",
        sa.Column("case_id", sa.String(), sa.ForeignKey("investigation_cases.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("vendor_id", sa.String(), sa.ForeignKey("vendors.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_table(
        "case_tenders",
        sa.Column("case_id", sa.String(), sa.ForeignKey("investigation_cases.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tender_id", sa.String(), sa.ForeignKey("tenders.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_table(
        "case_signals",
        sa.Column("case_id", sa.String(), sa.ForeignKey("investigation_cases.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("signal_id", sa.String(), sa.ForeignKey("risk_signals.id", ondelete="CASCADE"), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("case_signals")
    op.drop_table("case_tenders")
    op.drop_table("case_vendors")
    op.drop_table("risk_signal_vendors")
    op.drop_table("risk_signal_tenders")

    op.drop_table("investigation_cases")
    op.drop_table("risk_signals")

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

    op.drop_index("ix_awards_vendor_id", table_name="awards")
    op.drop_index("ix_awards_tender_id", table_name="awards")
    op.drop_constraint("fk_awards_vendor_id", "awards", type_="foreignkey")
    op.drop_constraint("fk_awards_tender_id", "awards", type_="foreignkey")

    op.drop_index("ix_bids_vendor_id", table_name="bids")
    op.drop_index("ix_bids_tender_id", table_name="bids")
    op.drop_constraint("fk_bids_vendor_id", "bids", type_="foreignkey")
    op.drop_constraint("fk_bids_tender_id", "bids", type_="foreignkey")
