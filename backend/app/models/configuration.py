from __future__ import annotations

import enum
import hashlib
import json
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.contract import Contract


LEGACY_CONFIGURATION_NAME = "Default configuration"
DEMO_ACTOR = "Demo User"


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
    alarms: Mapped[list[Alarm]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
        order_by="Alarm.code",
    )

    __table_args__ = (UniqueConstraint("contract_id", "code", name="uq_alarm_category_contract_code"),)


class Alarm(TimestampMixin, Base):
    __tablename__ = "alarms"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    alarm_category_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("alarm_categories.id", ondelete="CASCADE"),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))

    category: Mapped[AlarmCategory] = relationship(back_populates="alarms")

    __table_args__ = (UniqueConstraint("alarm_category_id", "code", name="uq_alarm_category_code"),)


class AvailabilityConfiguration(TimestampMixin, Base):
    __tablename__ = "availability_configurations"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    contract_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(120), nullable=False)

    contract: Mapped[Contract] = relationship(back_populates="availability_configurations")
    versions: Mapped[list[ConfigurationVersion]] = relationship(
        back_populates="availability_configuration",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("contract_id", "name", name="uq_av_config_contract_name"),
    )


class ConfigurationVersion(TimestampMixin, Base):
    __tablename__ = "configuration_versions"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    availability_configuration_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey(
            "availability_configurations.id",
            name="fk_config_version_av_config",
            ondelete="CASCADE",
        ),
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
    created_by: Mapped[str] = mapped_column(String(120), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    availability_configuration: Mapped[AvailabilityConfiguration] = relationship(
        back_populates="versions",
    )

    __table_args__ = (
        UniqueConstraint(
            "availability_configuration_id", "version_number", name="uq_config_version_av_number"
        ),
        Index(
            "uq_published_av_config",
            "availability_configuration_id",
            unique=True,
            postgresql_where=text("status = 'published'"),
            sqlite_where=text("status = 'published'"),
        ),
    )

    @property
    def contract_id(self) -> UUID:
        return self.availability_configuration.contract_id

    @staticmethod
    def calculate_checksum(data: dict[str, Any]) -> str:
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
