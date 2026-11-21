"""create configuration versions table

Revision ID: 202611220002
Revises: 202611220001
Create Date: 2026-11-22 01:30:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202611220002"
down_revision: str | None = "202611220001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    configuration_status = postgresql.ENUM(
        "draft",
        "in_review",
        "published",
        "archived",
        name="configuration_status",
        create_type=False,
    )
    configuration_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "configuration_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            configuration_status,
            nullable=False,
            server_default="draft",
        ),
        sa.Column("snapshot_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("contract_id", "version_number", name="uq_config_version_contract_number"),
    )

    # Partial unique index to enforce at most ONE published configuration per contract
    op.create_index(
        "uq_published_contract_config",
        "configuration_versions",
        ["contract_id"],
        unique=True,
        postgresql_where=sa.text("status = 'published'"),
    )


def downgrade() -> None:
    op.drop_index("uq_published_contract_config", table_name="configuration_versions")
    op.drop_table("configuration_versions")
    configuration_status = postgresql.ENUM(name="configuration_status")
    configuration_status.drop(op.get_bind(), checkfirst=True)
