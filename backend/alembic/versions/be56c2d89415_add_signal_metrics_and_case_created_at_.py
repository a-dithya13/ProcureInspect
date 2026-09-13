"""add signal metrics and case created_at and recommendation list

Adds:
- risk_signals.metrics (JSON) -- structured headline numbers per signal
  (observed_amount, peer_median_amount, deviation_percent, etc.) so the
  frontend can render signal cards without parsing the explanation string.
- investigation_cases.created_at (DateTime) -- when the case was produced.
- investigation_cases.recommended_investigation changes from a single
  String paragraph to a JSON list of checklist items (one per contributing
  signal), rendered as a numbered "Recommended Investigation Focus".

investigation_cases is analysis output regenerated in full by every
POST /api/analyze run, so altering its column shape here is safe.

Revision ID: be56c2d89415
Revises: a137e091e259
Create Date: 2026-09-20 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'be56c2d89415'
down_revision: Union[str, None] = 'a137e091e259'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "risk_signals",
        sa.Column("metrics", sa.JSON(), nullable=False, server_default="{}"),
    )

    op.add_column(
        "investigation_cases",
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.execute("UPDATE investigation_cases SET created_at = now() WHERE created_at IS NULL")
    op.alter_column("investigation_cases", "created_at", nullable=False)

    op.drop_column("investigation_cases", "recommended_investigation")
    op.add_column(
        "investigation_cases",
        sa.Column("recommended_investigation", sa.JSON(), nullable=False, server_default="[]"),
    )


def downgrade() -> None:
    op.drop_column("investigation_cases", "recommended_investigation")
    op.add_column(
        "investigation_cases",
        sa.Column("recommended_investigation", sa.String(), nullable=False, server_default=""),
    )
    op.drop_column("investigation_cases", "created_at")
    op.drop_column("risk_signals", "metrics")
