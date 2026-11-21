from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc, select, update
from sqlalchemy.orm import Session, selectinload

from app.models.configuration import ConfigurationStatus, ConfigurationVersion
from app.models.contract import Contract, ContractStatus
from app.models.turbine import Turbine
from app.models.wind_farm import WindFarm
from app.schemas.configuration import (
    ActiveConfigurationResponse,
    ConfigurationVersionResponse,
    DiffResponse,
    ValidationReadinessResponse,
)


def _load_contract_with_relations(db: Session, contract_id: UUID) -> Contract | None:
    statement = (
        select(Contract)
        .where(Contract.id == contract_id)
        .options(
            selectinload(Contract.wind_farms)
            .selectinload(WindFarm.turbines)
            .selectinload(Turbine.turbine_group),
            selectinload(Contract.production_periods),
            selectinload(Contract.alarm_categories),
            selectinload(Contract.configuration_versions),
        )
    )
    return db.scalar(statement)


def validate_configuration_readiness(
    contract: Contract,
    snapshot_data: dict[str, Any],
) -> ValidationReadinessResponse:
    blocking_errors: list[str] = []
    warnings: list[str] = []

    # 1. Alarm category validation
    included_alarms = set(snapshot_data.get("included_alarm_codes", []))
    for category in contract.alarm_categories:
        if category.is_required and category.code not in included_alarms:
            blocking_errors.append(
                f"Required alarm category '{category.name}' (code: {category.code}) is omitted from the configuration."
            )

    # 2. Turbine assignment validation
    all_turbines = [
        turbine
        for wind_farm in contract.wind_farms
        for turbine in wind_farm.turbines
    ]
    included_turbine_ids = {
        str(t_id).lower() for t_id in snapshot_data.get("turbine_ids", [])
    }
    unassigned = [
        t.code
        for t in all_turbines
        if str(t.id).lower() not in included_turbine_ids
    ]
    if unassigned:
        blocking_errors.append(
            f"Unassigned turbines detected: {', '.join(sorted(unassigned))} must be included in the fleet configuration."
        )

    # 3. Target availability validation
    target_avail = snapshot_data.get("target_availability")
    if target_avail is None:
        blocking_errors.append("Target availability percentage is required.")
    elif not (0.0 <= float(target_avail) <= 100.0):
        blocking_errors.append(f"Target availability must be between 0% and 100%, got {target_avail}%.")

    # 4. Production period check
    if contract.production_periods:
        included_period_ids = {
            str(p_id).lower() for p_id in snapshot_data.get("production_period_ids", [])
        }
        if not included_period_ids:
            warnings.append("No seasonal production periods selected for this configuration.")

    return ValidationReadinessResponse(
        is_valid=len(blocking_errors) == 0,
        blocking_errors=blocking_errors,
        warnings=warnings,
    )


def save_draft(
    db: Session,
    contract_id: UUID,
    base_version: int | None,
    snapshot_data: dict[str, Any],
) -> ConfigurationVersion:
    contract = db.get(Contract, contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found.",
        )

    # Fetch latest version for OCC check
    statement = (
        select(ConfigurationVersion)
        .where(ConfigurationVersion.contract_id == contract_id)
        .order_by(desc(ConfigurationVersion.version_number))
    )
    existing_versions = list(db.scalars(statement))
    current_version_number = existing_versions[0].version_number if existing_versions else 0

    if base_version is not None and base_version != current_version_number:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Conflict: Draft has been modified concurrently. "
                f"Your base version was {base_version}, but database is currently at version {current_version_number}."
            ),
        )

    next_version_number = current_version_number + 1
    checksum = ConfigurationVersion.calculate_checksum(snapshot_data)

    new_version = ConfigurationVersion(
        contract_id=contract_id,
        version_number=next_version_number,
        status=ConfigurationStatus.DRAFT,
        snapshot_data=snapshot_data,
        checksum=checksum,
    )
    db.add(new_version)
    db.commit()
    db.refresh(new_version)
    return new_version


def get_active_configuration(db: Session, contract_id: UUID) -> ActiveConfigurationResponse:
    contract = db.get(Contract, contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found.",
        )

    statement = (
        select(ConfigurationVersion)
        .where(ConfigurationVersion.contract_id == contract_id)
        .order_by(desc(ConfigurationVersion.version_number))
    )
    versions = list(db.scalars(statement))
    version_responses = [ConfigurationVersionResponse.model_validate(v) for v in versions]

    # Published takes priority as current version, otherwise latest version
    current_version = None
    for v in version_responses:
        if v.status == ConfigurationStatus.PUBLISHED:
            current_version = v
            break
    if current_version is None and version_responses:
        current_version = version_responses[0]

    return ActiveConfigurationResponse(
        contract_id=contract_id,
        current_version=current_version,
        versions=version_responses,
    )


def get_version(db: Session, contract_id: UUID, version_id: UUID) -> ConfigurationVersion:
    statement = select(ConfigurationVersion).where(
        ConfigurationVersion.id == version_id,
        ConfigurationVersion.contract_id == contract_id,
    )
    version = db.scalar(statement)
    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration version not found.",
        )
    return version


def publish_version(db: Session, contract_id: UUID, version_id: UUID) -> ConfigurationVersion:
    contract = _load_contract_with_relations(db, contract_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found.",
        )

    version = get_version(db, contract_id, version_id)
    if version.status == ConfigurationStatus.PUBLISHED:
        return version

    # Validate readiness
    readiness = validate_configuration_readiness(contract, version.snapshot_data)
    if not readiness.is_valid:
        raise HTTPException(
            status_code=422,
            detail=f"Cannot publish configuration with blocking errors: {'; '.join(readiness.blocking_errors)}",
        )

    # Archive previous published versions
    db.execute(
        update(ConfigurationVersion)
        .where(
            ConfigurationVersion.contract_id == contract_id,
            ConfigurationVersion.status == ConfigurationStatus.PUBLISHED,
        )
        .values(status=ConfigurationStatus.ARCHIVED)
    )

    version.status = ConfigurationStatus.PUBLISHED
    version.published_at = datetime.now(timezone.utc)
    contract.status = ContractStatus.PUBLISHED
    db.commit()
    db.refresh(version)
    return version


def transition_version(
    db: Session,
    contract_id: UUID,
    version_id: UUID,
    target_status: ConfigurationStatus,
) -> ConfigurationVersion:
    version = get_version(db, contract_id, version_id)

    if version.status == ConfigurationStatus.PUBLISHED and target_status == ConfigurationStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot transition from published to draft.",
        )

    if version.status == ConfigurationStatus.ARCHIVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot transition an archived configuration version.",
        )

    if target_status == ConfigurationStatus.PUBLISHED:
        return publish_version(db, contract_id, version_id)

    version.status = target_status
    db.commit()
    db.refresh(version)
    return version


def compute_diff(v_from: ConfigurationVersion, v_to: ConfigurationVersion) -> DiffResponse:
    from_data = v_from.snapshot_data or {}
    to_data = v_to.snapshot_data or {}

    from_alarms = set(from_data.get("included_alarm_codes", []))
    to_alarms = set(to_data.get("included_alarm_codes", []))

    from_turbines = set(str(t) for t in from_data.get("turbine_ids", []))
    to_turbines = set(str(t) for t in to_data.get("turbine_ids", []))

    from_vars = from_data.get("variables", {}) or {}
    to_vars = to_data.get("variables", {}) or {}
    all_var_keys = sorted(set(from_vars.keys()) | set(to_vars.keys()))

    variable_changes: dict[str, dict[str, Any]] = {}
    for key in all_var_keys:
        val_from = from_vars.get(key)
        val_to = to_vars.get(key)
        if val_from != val_to:
            variable_changes[key] = {"from": val_from, "to": val_to}

    return DiffResponse(
        v_from_number=v_from.version_number,
        v_to_number=v_to.version_number,
        added_alarms=sorted(list(to_alarms - from_alarms)),
        removed_alarms=sorted(list(from_alarms - to_alarms)),
        added_turbines=sorted(list(to_turbines - from_turbines)),
        removed_turbines=sorted(list(from_turbines - to_turbines)),
        variable_changes=variable_changes,
    )
