from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.wind_farm import TurbineGroup, WindFarm


class Turbine(TimestampMixin, Base):
    __tablename__ = "turbines"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    wind_farm_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("wind_farms.id", ondelete="CASCADE"),
        nullable=False,
    )
    turbine_group_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("turbine_groups.id", ondelete="SET NULL"),
        nullable=True,
    )
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    rated_power_mw: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    wind_farm: Mapped[WindFarm] = relationship(back_populates="turbines")
    turbine_group: Mapped[TurbineGroup | None] = relationship(back_populates="turbines")

    __table_args__ = (UniqueConstraint("wind_farm_id", "code", name="uq_turbine_farm_code"),)
