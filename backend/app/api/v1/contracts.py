from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.contract import ContractDetail, ContractListResponse
from app.services.contracts import get_contract, list_contracts

router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.get("", response_model=ContractListResponse)
def get_contracts(db: Session = Depends(get_db)) -> ContractListResponse:
    return ContractListResponse(contracts=list_contracts(db))


@router.get("/{contract_id}", response_model=ContractDetail)
def get_contract_by_id(contract_id: UUID, db: Session = Depends(get_db)) -> ContractDetail:
    contract = get_contract(db, contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found.",
        )

    return contract
