from __future__ import annotations

import enum
from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Date, Enum, JSON, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.configuration import AlarmCategory, AvailabilityConfiguration, ProductionPeriod
    from app.models.wind_farm import WindFarm


class ContractStatus(str, enum.Enum):
    DRAFT = "draft"
    NEEDS_REVIEW = "needs_review"
    PUBLISHED = "published"


class Contract(TimestampMixin, Base):
    __tablename__ = "contracts"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    customer_names: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False
    )
    order_reason: Mapped[str] = mapped_column(String(120), nullable=False)
    sales_document_number: Mapped[str] = mapped_column(String(20), nullable=False)
    wind_farm_name: Mapped[str] = mapped_column(String(160), nullable=False)
    region: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[ContractStatus] = mapped_column(
        Enum(
            ContractStatus,
            name="contract_status",
            values_callable=lambda statuses: [status.value for status in statuses],
        ),
        nullable=False,
        default=ContractStatus.DRAFT,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_availability: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    wind_farms: Mapped[list[WindFarm]] = relationship(
        back_populates="contract",
        cascade="all, delete-orphan",
    )
    production_periods: Mapped[list[ProductionPeriod]] = relationship(
        back_populates="contract",
        cascade="all, delete-orphan",
    )
    alarm_categories: Mapped[list[AlarmCategory]] = relationship(
        back_populates="contract",
        cascade="all, delete-orphan",
    )
    availability_configurations: Mapped[list[AvailabilityConfiguration]] = relationship(
        back_populates="contract",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("sales_document_number", name="uq_contract_sales_document_number"),
    )

    @property
    def customer_name(self) -> str:
        # Compatibility field for the existing home and detail pages.
        return " | ".join(self.customer_names)
