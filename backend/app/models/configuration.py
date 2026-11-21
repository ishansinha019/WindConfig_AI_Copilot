from __future__ import annotations

import enum
import hashlib
import json
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.contract import Contract


class ConfigurationStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ProductionPeriod(TimestampMixin, Base):
    __tablename__ = "production_periods"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    contract_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    contract: Mapped[Contract] = relationship(back_populates="production_periods")

    __table_args__ = (
        UniqueConstraint("contract_id", "name", name="uq_production_period_contract_name"),
    )


class AlarmCategory(TimestampMixin, Base):
    __tablename__ = "alarm_categories"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    contract_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    contract: Mapped[Contract] = relationship(back_populates="alarm_categories")

    __table_args__ = (UniqueConstraint("contract_id", "code", name="uq_alarm_category_contract_code"),)


class ConfigurationVersion(TimestampMixin, Base):
    __tablename__ = "configuration_versions"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    contract_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[ConfigurationStatus] = mapped_column(
        Enum(
            ConfigurationStatus,
            name="configuration_status",
            values_callable=lambda statuses: [status.value for status in statuses],
        ),
        nullable=False,
        default=ConfigurationStatus.DRAFT,
    )
    snapshot_data: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    contract: Mapped[Contract] = relationship(back_populates="configuration_versions")

    __table_args__ = (
        UniqueConstraint("contract_id", "version_number", name="uq_config_version_contract_number"),
    )

    @staticmethod
    def calculate_checksum(data: dict[str, Any]) -> str:
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
