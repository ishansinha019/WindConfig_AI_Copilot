from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.configuration import AlarmCategory, AvailabilityConfiguration
from app.models.contract import Contract
from app.models.turbine import Turbine
from app.models.wind_farm import WindFarm
from app.schemas.contract import ContractDetail, ContractSummary
from app.services.availability_configurations import build_av_config_summary


def _to_contract_summary(contract: Contract, today: date) -> ContractSummary:
    turbine_count = sum(len(wf.turbines) for wf in contract.wind_farms)
    av_configs = sorted(
        contract.availability_configurations,
        key=lambda c: c.updated_at,
        reverse=True,
    )
    return ContractSummary(
        id=contract.id,
        name=contract.name,
        customer_name=contract.customer_name,
        customer_names=contract.customer_names,
        order_reason=contract.order_reason,
        sales_document_number=contract.sales_document_number,
        wind_farm_name=contract.wind_farm_name,
        region=contract.region,
        status=contract.status,
        start_date=contract.start_date,
        end_date=contract.end_date,
        target_availability=float(contract.target_availability),
        is_live=contract.start_date <= today <= contract.end_date,
        turbine_count=turbine_count,
        availability_configurations=[build_av_config_summary(c) for c in av_configs],
    )


def list_contracts(db: Session) -> list[ContractSummary]:
    statement = (
        select(Contract)
        .options(
            selectinload(Contract.wind_farms).selectinload(WindFarm.turbines),
            selectinload(Contract.availability_configurations).selectinload(
                AvailabilityConfiguration.versions
            ),
        )
        .order_by(Contract.start_date, Contract.name)
    )
    today = date.today()
    return [_to_contract_summary(contract, today) for contract in db.scalars(statement)]


def get_contract(db: Session, contract_id: UUID) -> ContractDetail | None:
    statement = (
        select(Contract)
        .where(Contract.id == contract_id)
        .options(
            selectinload(Contract.wind_farms)
            .selectinload(WindFarm.turbines)
            .selectinload(Turbine.turbine_group),
            selectinload(Contract.production_periods),
            selectinload(Contract.alarm_categories).selectinload(AlarmCategory.alarms),
            selectinload(Contract.availability_configurations).selectinload(
                AvailabilityConfiguration.versions
            ),
        )
    )
    contract = db.scalar(statement)
    if contract is None:
        return None

    today = date.today()
    summary = _to_contract_summary(contract, today)
    return ContractDetail(
        **summary.model_dump(),
        wind_farms=contract.wind_farms,
        production_periods=contract.production_periods,
        alarm_categories=contract.alarm_categories,
    )
