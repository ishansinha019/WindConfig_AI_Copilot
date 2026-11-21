from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.schemas.contract import ContractDetail, ContractSummary


def list_contracts(db: Session) -> list[ContractSummary]:
    statement = select(Contract).order_by(Contract.start_date, Contract.name)
    return [ContractSummary.model_validate(contract) for contract in db.scalars(statement)]


def get_contract(db: Session, contract_id: UUID) -> ContractDetail | None:
    contract = db.get(Contract, contract_id)
    if contract is None:
        return None

    return ContractDetail.model_validate(contract)
