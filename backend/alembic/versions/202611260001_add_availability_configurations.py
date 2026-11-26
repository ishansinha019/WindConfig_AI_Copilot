"""Add per-contract availability configurations and nested alarms.

Revision ID: 202611260001
Revises: 202611220002
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "202611260001"
down_revision = "202611220002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("contracts", sa.Column("order_reason", sa.String(120)))
    op.add_column("contracts", sa.Column("sales_document_number", sa.String(20)))
    op.add_column("contracts", sa.Column("customer_names", postgresql.JSONB()))
    op.execute(
        """
        WITH numbered AS (
            SELECT id, row_number() OVER (ORDER BY id) AS n
            FROM contracts
        )
        UPDATE contracts AS c
        SET order_reason = 'Legacy contract',
            sales_document_number = 'L' || numbered.n::text,
            customer_names = jsonb_build_array(c.customer_name)
        FROM numbered
        WHERE c.id = numbered.id
        """
    )
    op.alter_column("contracts", "order_reason", nullable=False)
    op.alter_column("contracts", "sales_document_number", nullable=False)
    op.alter_column("contracts", "customer_names", nullable=False)
    op.create_unique_constraint(
        "uq_contract_sales_document_number", "contracts", ["sales_document_number"]
    )
    op.drop_column("contracts", "customer_name")

    op.create_table(
        "availability_configurations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "contract_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("contracts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("created_by", sa.String(120), nullable=False),
        sa.Column("updated_by", sa.String(120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("contract_id", "name", name="uq_av_config_contract_name"),
    )
    op.create_table(
        "alarms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "alarm_category_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("alarm_categories.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code", sa.String(40), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("alarm_category_id", "code", name="uq_alarm_category_code"),
    )
    op.add_column(
        "configuration_versions",
        sa.Column("availability_configuration_id", postgresql.UUID(as_uuid=True)),
    )
    op.add_column("configuration_versions", sa.Column("created_by", sa.String(120)))
    op.execute(
        """
        INSERT INTO availability_configurations
            (id, contract_id, name, created_by, updated_by, created_at, updated_at)
        SELECT gen_random_uuid(), contract_id, 'Default configuration',
               'Demo User', 'Demo User', min(created_at), max(updated_at)
        FROM configuration_versions
        GROUP BY contract_id
        """
    )
    op.execute(
        """
        UPDATE configuration_versions AS v
        SET availability_configuration_id = c.id, created_by = 'Demo User'
        FROM availability_configurations AS c
        WHERE v.contract_id = c.contract_id
        """
    )
    op.alter_column("configuration_versions", "availability_configuration_id", nullable=False)
    op.alter_column("configuration_versions", "created_by", nullable=False)
    op.create_foreign_key(
        "fk_config_version_av_config",
        "configuration_versions",
        "availability_configurations",
        ["availability_configuration_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_index("uq_published_contract_config", table_name="configuration_versions")
    op.drop_constraint(
        "uq_config_version_contract_number", "configuration_versions", type_="unique"
    )
    op.drop_column("configuration_versions", "contract_id")
    op.create_unique_constraint(
        "uq_config_version_av_number",
        "configuration_versions",
        ["availability_configuration_id", "version_number"],
    )
    op.create_index(
        "uq_published_av_config",
        "configuration_versions",
        ["availability_configuration_id"],
        unique=True,
        postgresql_where=sa.text("status = 'published'"),
    )


def downgrade() -> None:
    # Do not silently unpublish configurations that the old schema cannot represent.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM configuration_versions AS v
                JOIN availability_configurations AS c ON c.id = v.availability_configuration_id
                WHERE v.status = 'published'
                GROUP BY c.contract_id
                HAVING count(*) > 1
            ) THEN
                RAISE EXCEPTION 'Cannot downgrade: a contract has multiple published configurations';
            END IF;
        END;
        $$
        """
    )
    op.add_column(
        "configuration_versions", sa.Column("contract_id", postgresql.UUID(as_uuid=True))
    )
    op.execute(
        """
        UPDATE configuration_versions AS v
        SET contract_id = c.contract_id
        FROM availability_configurations AS c
        WHERE c.id = v.availability_configuration_id
        """
    )
    op.alter_column("configuration_versions", "contract_id", nullable=False)
    op.create_foreign_key(
        "configuration_versions_contract_id_fkey",
        "configuration_versions",
        "contracts",
        ["contract_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_index("uq_published_av_config", table_name="configuration_versions")
    op.drop_constraint("uq_config_version_av_number", "configuration_versions", type_="unique")
    # Keep the original default's version numbers, moving only colliding versions.
    op.execute(
        """
        WITH ranked AS (
            SELECT v.id, v.contract_id,
                   max(v.version_number) OVER (PARTITION BY v.contract_id) AS max_number,
                   row_number() OVER (
                       PARTITION BY v.contract_id, v.version_number
                       ORDER BY (c.name <> 'Default configuration'), v.created_at, v.id
                   ) AS occurrence
            FROM configuration_versions AS v
            JOIN availability_configurations AS c ON c.id = v.availability_configuration_id
        ), reassigned AS (
            SELECT id, max_number + row_number() OVER (
                PARTITION BY contract_id ORDER BY id
            ) AS new_number
            FROM ranked
            WHERE occurrence > 1
        )
        UPDATE configuration_versions AS v
        SET version_number = reassigned.new_number
        FROM reassigned
        WHERE v.id = reassigned.id
        """
    )
    op.create_unique_constraint(
        "uq_config_version_contract_number",
        "configuration_versions",
        ["contract_id", "version_number"],
    )
    op.create_index(
        "uq_published_contract_config",
        "configuration_versions",
        ["contract_id"],
        unique=True,
        postgresql_where=sa.text("status = 'published'"),
    )
    op.drop_column("configuration_versions", "availability_configuration_id")
    op.drop_column("configuration_versions", "created_by")
    op.drop_table("availability_configurations")
    op.drop_table("alarms")

    op.add_column("contracts", sa.Column("customer_name", sa.String(160)))
    op.execute("UPDATE contracts SET customer_name = left(customer_names ->> 0, 160)")
    op.alter_column("contracts", "customer_name", nullable=False)
    op.drop_column("contracts", "customer_names")
    op.drop_column("contracts", "sales_document_number")
    op.drop_column("contracts", "order_reason")
