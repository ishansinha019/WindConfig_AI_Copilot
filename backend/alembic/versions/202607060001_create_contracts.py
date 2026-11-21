"""create contracts table

Revision ID: 202607060001
Revises:
Create Date: 2026-07-06 01:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202607060001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    contract_status = sa.Enum("draft", "needs_review", "published", name="contract_status")
    contract_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "contracts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("customer_name", sa.String(length=160), nullable=False),
        sa.Column("wind_farm_name", sa.String(length=160), nullable=False),
        sa.Column("region", sa.String(length=80), nullable=False),
        sa.Column("status", contract_status, nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("target_availability", sa.Numeric(5, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("contracts")
    sa.Enum(name="contract_status").drop(op.get_bind(), checkfirst=True)
