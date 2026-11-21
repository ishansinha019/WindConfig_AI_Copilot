from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.configuration import (
    ActiveConfigurationResponse,
    ConfigurationVersionResponse,
    DiffResponse,
    SaveDraftRequest,
    TransitionRequest,
    ValidationReadinessResponse,
)
from app.services.configurations import (
    _load_contract_with_relations,
    compute_diff,
    get_active_configuration,
    get_version,
    publish_version,
    save_draft,
    transition_version,
    validate_configuration_readiness,
)

router = APIRouter(prefix="/contracts/{contract_id}/configuration", tags=["configurations"])


@router.post(
    "/drafts",
    response_model=ConfigurationVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_draft_endpoint(
    contract_id: UUID,
    payload: SaveDraftRequest,
    db: Session = Depends(get_db),
) -> ConfigurationVersionResponse:
    version = save_draft(
        db=db,
        contract_id=contract_id,
        base_version=payload.base_version,
        snapshot_data=payload.snapshot_data,
    )
    return ConfigurationVersionResponse.model_validate(version)


@router.get("", response_model=ActiveConfigurationResponse)
def get_active_configuration_endpoint(
    contract_id: UUID,
    db: Session = Depends(get_db),
) -> ActiveConfigurationResponse:
    return get_active_configuration(db=db, contract_id=contract_id)


@router.get("/versions/{version_id}", response_model=ConfigurationVersionResponse)
def get_version_endpoint(
    contract_id: UUID,
    version_id: UUID,
    db: Session = Depends(get_db),
) -> ConfigurationVersionResponse:
    version = get_version(db=db, contract_id=contract_id, version_id=version_id)
    return ConfigurationVersionResponse.model_validate(version)


@router.get("/versions/{version_id}/readiness", response_model=ValidationReadinessResponse)
def get_version_readiness_endpoint(
    contract_id: UUID,
    version_id: UUID,
    db: Session = Depends(get_db),
) -> ValidationReadinessResponse:
    contract = _load_contract_with_relations(db, contract_id)
    if contract is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Contract not found.")

    version = get_version(db=db, contract_id=contract_id, version_id=version_id)
    return validate_configuration_readiness(contract, version.snapshot_data)


@router.post("/versions/{version_id}/publish", response_model=ConfigurationVersionResponse)
def publish_version_endpoint(
    contract_id: UUID,
    version_id: UUID,
    db: Session = Depends(get_db),
) -> ConfigurationVersionResponse:
    version = publish_version(db=db, contract_id=contract_id, version_id=version_id)
    return ConfigurationVersionResponse.model_validate(version)


@router.post("/versions/{version_id}/transition", response_model=ConfigurationVersionResponse)
def transition_version_endpoint(
    contract_id: UUID,
    version_id: UUID,
    payload: TransitionRequest,
    db: Session = Depends(get_db),
) -> ConfigurationVersionResponse:
    version = transition_version(
        db=db,
        contract_id=contract_id,
        version_id=version_id,
        target_status=payload.target_status,
    )
    return ConfigurationVersionResponse.model_validate(version)


@router.get("/diff", response_model=DiffResponse)
def get_diff_endpoint(
    contract_id: UUID,
    v_from: UUID = Query(...),
    v_to: UUID = Query(...),
    db: Session = Depends(get_db),
) -> DiffResponse:
    version_from = get_version(db=db, contract_id=contract_id, version_id=v_from)
    version_to = get_version(db=db, contract_id=contract_id, version_id=v_to)
    return compute_diff(version_from, version_to)
