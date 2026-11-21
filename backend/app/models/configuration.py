from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.contract import Contract


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
