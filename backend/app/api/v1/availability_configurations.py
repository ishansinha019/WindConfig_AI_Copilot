from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.configuration import DEMO_ACTOR
from app.schemas.availability_configuration import (
    AvailabilityConfigDetail,
    AvailabilityConfigListResponse,
    AvConfigVersionResponse,
    AvDiffResponse,
    AvValidationReadinessResponse,
    CreateAvailabilityConfigRequest,
    SaveAvDraftRequest,
)
from app.services.availability_configurations import (
    _load_av_config,
    _load_contract_with_assets,
    compute_av_diff,
    create_availability_configuration,
    delete_availability_configuration,
    get_availability_configuration,
    get_av_version,
    list_availability_configurations,
    list_av_versions,
    publish_av_version,
    save_av_draft,
    validate_av_readiness,
)

router = APIRouter(
    prefix="/contracts/{contract_id}/availability-configurations",
    tags=["availability-configurations"],
)


def get_acting_user(
    x_user_name: str | None = Header(default=None, alias="X-User-Name"),
) -> str:
    if x_user_name and x_user_name.strip():
        return x_user_name.strip()
    return DEMO_ACTOR


@router.get("", response_model=AvailabilityConfigListResponse)
def list_av_configs_endpoint(
    contract_id: UUID,
    db: Session = Depends(get_db),
) -> AvailabilityConfigListResponse:
    items = list_availability_configurations(db=db, contract_id=contract_id)
    return AvailabilityConfigListResponse(availability_configurations=items)


@router.post(
    "",
    response_model=AvailabilityConfigDetail,
    status_code=status.HTTP_201_CREATED,
)
def create_av_config_endpoint(
    contract_id: UUID,
    payload: CreateAvailabilityConfigRequest,
    actor: str = Depends(get_acting_user),
    db: Session = Depends(get_db),
) -> AvailabilityConfigDetail:
    return create_availability_configuration(
        db=db,
        contract_id=contract_id,
        snapshot=payload.snapshot_data,
        actor=actor,
    )


@router.get("/{acid}", response_model=AvailabilityConfigDetail)
def get_av_config_endpoint(
    contract_id: UUID,
    acid: UUID,
    db: Session = Depends(get_db),
) -> AvailabilityConfigDetail:
    return get_availability_configuration(db=db, contract_id=contract_id, acid=acid)


@router.post(
    "/{acid}/drafts",
    response_model=AvConfigVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_av_draft_endpoint(
    contract_id: UUID,
    acid: UUID,
    payload: SaveAvDraftRequest,
    actor: str = Depends(get_acting_user),
    db: Session = Depends(get_db),
) -> AvConfigVersionResponse:
    version = save_av_draft(
        db=db,
        contract_id=contract_id,
        acid=acid,
        base_version=payload.base_version,
        snapshot=payload.snapshot_data,
        actor=actor,
    )
    return AvConfigVersionResponse.model_validate(version)


@router.get("/{acid}/versions", response_model=list[AvConfigVersionResponse])
def list_av_versions_endpoint(
    contract_id: UUID,
    acid: UUID,
    db: Session = Depends(get_db),
) -> list[AvConfigVersionResponse]:
    versions = list_av_versions(db=db, contract_id=contract_id, acid=acid)
    return [AvConfigVersionResponse.model_validate(v) for v in versions]


@router.get("/{acid}/versions/{vid}", response_model=AvConfigVersionResponse)
def get_av_version_endpoint(
    contract_id: UUID,
    acid: UUID,
    vid: UUID,
    db: Session = Depends(get_db),
) -> AvConfigVersionResponse:
    version = get_av_version(db=db, contract_id=contract_id, acid=acid, vid=vid)
    return AvConfigVersionResponse.model_validate(version)


@router.get("/{acid}/versions/{vid}/readiness", response_model=AvValidationReadinessResponse)
def get_av_readiness_endpoint(
    contract_id: UUID,
    acid: UUID,
    vid: UUID,
    db: Session = Depends(get_db),
) -> AvValidationReadinessResponse:
    contract = _load_contract_with_assets(db, contract_id)
    av_config = _load_av_config(db, contract_id, acid)
    version = get_av_version(db, contract_id, acid, vid)
    return validate_av_readiness(contract=contract, av_config=av_config, version=version)


@router.post("/{acid}/versions/{vid}/publish", response_model=AvConfigVersionResponse)
def publish_av_version_endpoint(
    contract_id: UUID,
    acid: UUID,
    vid: UUID,
    actor: str = Depends(get_acting_user),
    db: Session = Depends(get_db),
) -> AvConfigVersionResponse:
    version = publish_av_version(
        db=db,
        contract_id=contract_id,
        acid=acid,
        vid=vid,
        actor=actor,
    )
    return AvConfigVersionResponse.model_validate(version)


@router.get("/{acid}/diff", response_model=AvDiffResponse)
def get_av_diff_endpoint(
    contract_id: UUID,
    acid: UUID,
    v_from: UUID = Query(...),
    v_to: UUID = Query(...),
    db: Session = Depends(get_db),
) -> AvDiffResponse:
    version_from = get_av_version(db=db, contract_id=contract_id, acid=acid, vid=v_from)
    version_to = get_av_version(db=db, contract_id=contract_id, acid=acid, vid=v_to)
    return compute_av_diff(version_from, version_to)


@router.delete("/{acid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_av_config_endpoint(
    contract_id: UUID,
    acid: UUID,
    db: Session = Depends(get_db),
) -> Response:
    delete_availability_configuration(db=db, contract_id=contract_id, acid=acid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
