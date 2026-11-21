from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.contract import Contract
    from app.models.turbine import Turbine


class WindFarm(TimestampMixin, Base):
    __tablename__ = "wind_farms"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    contract_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    region: Mapped[str] = mapped_column(String(80), nullable=False)

    contract: Mapped[Contract] = relationship(back_populates="wind_farms")
    turbine_groups: Mapped[list[TurbineGroup]] = relationship(
        back_populates="wind_farm",
        cascade="all, delete-orphan",
    )
    turbines: Mapped[list[Turbine]] = relationship(
        back_populates="wind_farm",
        cascade="all, delete-orphan",
    )

    __table_args__ = (UniqueConstraint("contract_id", "name", name="uq_wind_farm_contract_name"),)


class TurbineGroup(TimestampMixin, Base):
    __tablename__ = "turbine_groups"

    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)
    wind_farm_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("wind_farms.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    wind_farm: Mapped[WindFarm] = relationship(back_populates="turbine_groups")
    turbines: Mapped[list[Turbine]] = relationship(back_populates="turbine_group")

    __table_args__ = (UniqueConstraint("wind_farm_id", "name", name="uq_turbine_group_farm_name"),)
