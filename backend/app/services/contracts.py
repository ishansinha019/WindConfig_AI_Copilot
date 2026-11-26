from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.configuration import AlarmCategory
from app.models.contract import Contract
from app.models.turbine import Turbine
from app.models.wind_farm import WindFarm
from app.schemas.contract import ContractDetail, ContractSummary


def list_contracts(db: Session) -> list[ContractSummary]:
    statement = select(Contract).order_by(Contract.start_date, Contract.name)
    return [ContractSummary.model_validate(contract) for contract in db.scalars(statement)]


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
        )
    )
    contract = db.scalar(statement)
    if contract is None:
        return None

    return ContractDetail.model_validate(contract)
