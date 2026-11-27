from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc, select, update
from sqlalchemy.orm import Session, selectinload

from app.domain.catalog import (
    CALCULATION_TYPE_CODES,
    FORMULA_BY_CODE,
    HIGH_WIND_CODES,
    LOW_WIND_CODES,
)
from app.models.configuration import (
    AlarmCategory,
    AvailabilityConfiguration,
    ConfigurationStatus,
    ConfigurationVersion,
)
from app.models.contract import Contract, ContractStatus
from app.models.wind_farm import WindFarm
from app.schemas.availability_configuration import (
    AvailabilityConfigDetail,
    AvailabilityConfigSummary,
    AvailabilitySnapshotDraft,
    AvConfigVersionResponse,
    AvDiffResponse,
    AvValidationReadinessResponse,
    ReadinessIssue,
)


def _parse_optional_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value:
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def build_av_config_summary(av_config: AvailabilityConfiguration) -> AvailabilityConfigSummary:
    versions = sorted(av_config.versions, key=lambda v: v.version_number, reverse=True)
    latest = versions[0] if versions else None
    published = next((v for v in versions if v.status == ConfigurationStatus.PUBLISHED), None)

    derived_status = "published" if published is not None else "draft"
    has_unpublished_draft = bool(
        published is not None and latest is not None and latest.version_number > published.version_number
    )

    calc_type: str | None = None
    start_dt: date | None = None
    end_dt: date | None = None
    if latest is not None:
        snap = latest.snapshot_data or {}
        if snap.get("schema_version") == 2:
            basic = snap.get("basic_details") or {}
            calc_type = basic.get("calculation_type")
            start_dt = _parse_optional_date(basic.get("start_date"))
            end_dt = _parse_optional_date(basic.get("end_date"))
        else:
            calc_type = snap.get("formula_type")

    return AvailabilityConfigSummary(
        id=av_config.id,
        contract_id=av_config.contract_id,
        name=av_config.name,
        status=derived_status,
        has_unpublished_draft=has_unpublished_draft,
        calculation_type=calc_type,
        start_date=start_dt,
        end_date=end_dt,
        latest_version_number=latest.version_number if latest else 0,
        created_by=av_config.created_by,
        updated_by=av_config.updated_by,
        created_at=av_config.created_at,
        updated_at=av_config.updated_at,
    )


def _build_av_config_detail(av_config: AvailabilityConfiguration) -> AvailabilityConfigDetail:
    versions = sorted(av_config.versions, key=lambda v: v.version_number, reverse=True)
    latest = versions[0]
    published = next((v for v in versions if v.status == ConfigurationStatus.PUBLISHED), None)
    summary = build_av_config_summary(av_config)
    return AvailabilityConfigDetail(
        **summary.model_dump(),
        latest_version=AvConfigVersionResponse.model_validate(latest),
        published_version=AvConfigVersionResponse.model_validate(published) if published else None,
    )


def _load_contract_with_assets(db: Session, contract_id: UUID) -> Contract:
    statement = (
        select(Contract)
        .where(Contract.id == contract_id)
        .options(
            selectinload(Contract.wind_farms).selectinload(WindFarm.turbines),
            selectinload(Contract.alarm_categories).selectinload(AlarmCategory.alarms),
            selectinload(Contract.availability_configurations).selectinload(
                AvailabilityConfiguration.versions
            ),
        )
    )
    contract = db.scalar(statement)
    if contract is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found.")
    return contract


def _load_av_config(
    db: Session, contract_id: UUID, acid: UUID
) -> AvailabilityConfiguration:
    statement = (
        select(AvailabilityConfiguration)
        .where(
            AvailabilityConfiguration.id == acid,
            AvailabilityConfiguration.contract_id == contract_id,
        )
        .options(selectinload(AvailabilityConfiguration.versions))
    )
    av_config = db.scalar(statement)
    if av_config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Availability configuration not found.",
        )
    return av_config


def _enforce_contract_scoping(contract: Contract, snapshot: AvailabilitySnapshotDraft) -> None:
    """Reject any turbine or alarm UUID that does not belong to this contract (422)."""
    contract_turbine_ids = {
        t.id for wf in contract.wind_farms for t in wf.turbines
    }
    foreign_turbines = [
        str(tid) for tid in snapshot.turbine_ids if tid not in contract_turbine_ids
    ]
    if foreign_turbines:
        raise HTTPException(
            status_code=422,
            detail=f"Turbine UUID(s) do not belong to this contract: {', '.join(foreign_turbines)}",
        )

    contract_alarm_ids = {
        alarm.id for cat in contract.alarm_categories for alarm in cat.alarms
    }
    for assignment in snapshot.alarm_assignments:
        if assignment.alarm_id not in contract_alarm_ids:
            raise HTTPException(
                status_code=422,
                detail=f"Alarm UUID {assignment.alarm_id} does not belong to this contract.",
            )
        foreign_assigned = [
            str(tid) for tid in assignment.turbine_ids if tid not in contract_turbine_ids
        ]
        if foreign_assigned:
            raise HTTPException(
                status_code=422,
                detail=f"Assigned turbine UUID(s) do not belong to this contract: {', '.join(foreign_assigned)}",
            )


def list_availability_configurations(
    db: Session, contract_id: UUID
) -> list[AvailabilityConfigSummary]:
    contract = db.get(Contract, contract_id)
    if contract is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found.")

    statement = (
        select(AvailabilityConfiguration)
        .where(AvailabilityConfiguration.contract_id == contract_id)
        .options(selectinload(AvailabilityConfiguration.versions))
        .order_by(desc(AvailabilityConfiguration.updated_at))
    )
    configs = list(db.scalars(statement))
    return [build_av_config_summary(c) for c in configs]


def create_availability_configuration(
    db: Session,
    contract_id: UUID,
    snapshot: AvailabilitySnapshotDraft,
    actor: str,
) -> AvailabilityConfigDetail:
    contract = _load_contract_with_assets(db, contract_id)
    _enforce_contract_scoping(contract, snapshot)

    name = snapshot.basic_details.name
    existing_same_name = next(
        (c for c in contract.availability_configurations if c.name.lower() == name.lower()),
        None,
    )
    if existing_same_name is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An availability configuration named '{name}' already exists for this contract.",
        )

    serialized = snapshot.model_dump(mode="json")
    checksum = ConfigurationVersion.calculate_checksum(serialized)

    av_config = AvailabilityConfiguration(
        contract_id=contract_id,
        name=name,
        created_by=actor,
        updated_by=actor,
        versions=[
            ConfigurationVersion(
                version_number=1,
                status=ConfigurationStatus.DRAFT,
                snapshot_data=serialized,
                checksum=checksum,
                created_by=actor,
            )
        ],
    )
    db.add(av_config)
    db.commit()
    db.refresh(av_config)
    return _build_av_config_detail(_load_av_config(db, contract_id, av_config.id))


def get_availability_configuration(
    db: Session, contract_id: UUID, acid: UUID
) -> AvailabilityConfigDetail:
    av_config = _load_av_config(db, contract_id, acid)
    return _build_av_config_detail(av_config)


def save_av_draft(
    db: Session,
    contract_id: UUID,
    acid: UUID,
    base_version: int | None,
    snapshot: AvailabilitySnapshotDraft,
    actor: str,
) -> ConfigurationVersion:
    contract = _load_contract_with_assets(db, contract_id)
    av_config = _load_av_config(db, contract_id, acid)
    _enforce_contract_scoping(contract, snapshot)

    versions = sorted(av_config.versions, key=lambda v: v.version_number, reverse=True)
    current_version_number = versions[0].version_number if versions else 0

    if base_version is not None and base_version != current_version_number:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Conflict: Draft has been modified concurrently. "
                f"Your base version was {base_version}, but database is currently at version {current_version_number}."
            ),
        )

    new_name = snapshot.basic_details.name
    duplicate = next(
        (
            c
            for c in contract.availability_configurations
            if c.id != acid and c.name.lower() == new_name.lower()
        ),
        None,
    )
    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Another availability configuration named '{new_name}' already exists for this contract.",
        )

    serialized = snapshot.model_dump(mode="json")
    new_version = ConfigurationVersion(
        availability_configuration_id=acid,
        version_number=current_version_number + 1,
        status=ConfigurationStatus.DRAFT,
        snapshot_data=serialized,
        checksum=ConfigurationVersion.calculate_checksum(serialized),
        created_by=actor,
    )
    av_config.name = new_name
    av_config.updated_by = actor
    av_config.updated_at = datetime.now(timezone.utc)
    db.add(new_version)
    db.commit()
    db.refresh(new_version)
    return new_version


def list_av_versions(
    db: Session, contract_id: UUID, acid: UUID
) -> list[ConfigurationVersion]:
    av_config = _load_av_config(db, contract_id, acid)
    return sorted(av_config.versions, key=lambda v: v.version_number, reverse=True)


def get_av_version(
    db: Session, contract_id: UUID, acid: UUID, vid: UUID
) -> ConfigurationVersion:
    av_config = _load_av_config(db, contract_id, acid)
    version = next((v for v in av_config.versions if v.id == vid), None)
    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration version not found.",
        )
    return version


def validate_av_readiness(
    contract: Contract,
    av_config: AvailabilityConfiguration,
    version: ConfigurationVersion,
) -> AvValidationReadinessResponse:
    blocking_errors: list[ReadinessIssue] = []
    warnings: list[ReadinessIssue] = []

    snap = version.snapshot_data or {}
    basic = snap.get("basic_details") or {}

    # Step 1: Basic details
    name = (basic.get("name") or "").strip()
    if not name:
        blocking_errors.append(
            ReadinessIssue(step=1, field="basic_details.name", message="Configuration name is required.")
        )
    else:
        name_conflict = any(
            c.id != av_config.id and c.name.lower() == name.lower()
            for c in contract.availability_configurations
        )
        if name_conflict:
            blocking_errors.append(
                ReadinessIssue(
                    step=1,
                    field="basic_details.name",
                    message=f"Configuration name '{name}' is already used in this contract.",
                )
            )

    calc_type = basic.get("calculation_type")
    if not calc_type or calc_type not in CALCULATION_TYPE_CODES:
        blocking_errors.append(
            ReadinessIssue(
                step=1,
                field="basic_details.calculation_type",
                message="Calculation type must be one of TBA, YBA, or RBA.",
            )
        )

    start_dt = _parse_optional_date(basic.get("start_date"))
    end_dt = _parse_optional_date(basic.get("end_date"))
    if start_dt is None:
        blocking_errors.append(
            ReadinessIssue(step=1, field="basic_details.start_date", message="Start date is required.")
        )
    if end_dt is None:
        blocking_errors.append(
            ReadinessIssue(step=1, field="basic_details.end_date", message="End date is required.")
        )
    if start_dt is not None and end_dt is not None and end_dt <= start_dt:
        blocking_errors.append(
            ReadinessIssue(
                step=1,
                field="basic_details.end_date",
                message="End date must be strictly after start date.",
            )
        )

    # Step 2: Turbines
    turbine_by_id = {
        str(t.id).lower(): t
        for wf in contract.wind_farms
        for t in wf.turbines
    }
    raw_turbine_ids = [str(tid).lower() for tid in (snap.get("turbine_ids") or [])]
    selected_turbine_set = set(raw_turbine_ids)

    if not raw_turbine_ids:
        blocking_errors.append(
            ReadinessIssue(step=2, field="turbine_ids", message="At least one turbine must be selected.")
        )
    else:
        foreign = [tid for tid in raw_turbine_ids if tid not in turbine_by_id]
        if foreign:
            blocking_errors.append(
                ReadinessIssue(
                    step=2,
                    field="turbine_ids",
                    message=f"Turbine(s) do not belong to this contract: {', '.join(foreign)}.",
                )
            )

    # Step 3: Formula & Alarm assignments
    formula_code = snap.get("formula_code")
    formula_item = FORMULA_BY_CODE.get(formula_code) if formula_code else None
    if formula_item is None:
        blocking_errors.append(
            ReadinessIssue(step=3, field="formula_code", message="A valid availability formula must be selected.")
        )
    elif calc_type and formula_item.calculation_type != calc_type:
        blocking_errors.append(
            ReadinessIssue(
                step=3,
                field="formula_code",
                message=f"Formula '{formula_code}' does not match calculation type '{calc_type}'.",
            )
        )

    alarm_to_cat = {
        str(alarm.id).lower(): cat
        for cat in contract.alarm_categories
        for alarm in cat.alarms
    }
    assignments = snap.get("alarm_assignments") or []
    included_cat_codes: set[str] = set()
    turbines_with_alarms: set[str] = set()

    for idx, assignment in enumerate(assignments):
        aid = str(assignment.get("alarm_id", "")).lower()
        assigned_tids = [str(tid).lower() for tid in (assignment.get("turbine_ids") or [])]
        cat = alarm_to_cat.get(aid)
        if cat is None:
            blocking_errors.append(
                ReadinessIssue(
                    step=3,
                    field=f"alarm_assignments[{idx}].alarm_id",
                    message=f"Alarm ID '{aid}' does not belong to this contract.",
                )
            )
        else:
            included_cat_codes.add(cat.code)

        if not assigned_tids:
            blocking_errors.append(
                ReadinessIssue(
                    step=3,
                    field=f"alarm_assignments[{idx}].turbine_ids",
                    message="Each selected alarm must be assigned to at least one turbine.",
                )
            )
        else:
            out_of_scope = [tid for tid in assigned_tids if tid not in selected_turbine_set]
            if out_of_scope:
                blocking_errors.append(
                    ReadinessIssue(
                        step=3,
                        field=f"alarm_assignments[{idx}].turbine_ids",
                        message="Alarm assignment references turbine(s) not selected in Step 2.",
                    )
                )
            turbines_with_alarms.update(assigned_tids)

    for cat in contract.alarm_categories:
        if cat.is_required and cat.code not in included_cat_codes:
            blocking_errors.append(
                ReadinessIssue(
                    step=3,
                    field="alarm_assignments",
                    message=f"Required alarm category '{cat.name}' ({cat.code}) must have at least one alarm included.",
                )
            )

    # Warning for selected turbines with no alarm assigned
    unassigned_in_scope = [
        turbine_by_id[tid].code
        for tid in selected_turbine_set
        if tid in turbine_by_id and tid not in turbines_with_alarms
    ]
    if unassigned_in_scope:
        warnings.append(
            ReadinessIssue(
                step=3,
                field="alarm_assignments",
                message=f"Turbine(s) in scope have no alarms assigned: {', '.join(sorted(unassigned_in_scope))}.",
            )
        )

    # Step 4: Details
    details = snap.get("details") or {}
    park_pct = details.get("park_availability_pct")
    if park_pct is None:
        blocking_errors.append(
            ReadinessIssue(
                step=4,
                field="details.park_availability_pct",
                message="Park availability (%) is required.",
            )
        )
    elif not (0.0 <= float(park_pct) <= 100.0):
        blocking_errors.append(
            ReadinessIssue(
                step=4,
                field="details.park_availability_pct",
                message=f"Park availability must be between 0 and 100, got {park_pct}.",
            )
        )

    low_wind = details.get("low_wind_variant")
    if not low_wind or low_wind not in LOW_WIND_CODES:
        blocking_errors.append(
            ReadinessIssue(
                step=4,
                field="details.low_wind_variant",
                message="A valid low wind variant is required.",
            )
        )

    high_wind = details.get("high_wind_variant")
    if not high_wind or high_wind not in HIGH_WIND_CODES:
        blocking_errors.append(
            ReadinessIssue(
                step=4,
                field="details.high_wind_variant",
                message="A valid high wind variant is required.",
            )
        )

    # Overlap check against OTHER published AV configs in the same contract
    if start_dt is not None and end_dt is not None and selected_turbine_set:
        for other in contract.availability_configurations:
            if other.id == av_config.id:
                continue
            other_pub = next(
                (v for v in other.versions if v.status == ConfigurationStatus.PUBLISHED),
                None,
            )
            if other_pub is None:
                continue
            o_snap = other_pub.snapshot_data or {}
            o_basic = o_snap.get("basic_details") or {}
            o_start = _parse_optional_date(o_basic.get("start_date"))
            o_end = _parse_optional_date(o_basic.get("end_date"))
            o_turbines = {str(tid).lower() for tid in (o_snap.get("turbine_ids") or [])}
            if o_start is None or o_end is None:
                continue

            dates_overlap = start_dt <= o_end and end_dt >= o_start
            shared_turbines = selected_turbine_set & o_turbines
            if dates_overlap and shared_turbines:
                shared_codes = sorted(
                    turbine_by_id[tid].code for tid in shared_turbines if tid in turbine_by_id
                )
                blocking_errors.append(
                    ReadinessIssue(
                        step=1,
                        field="basic_details.start_date",
                        message=(
                            f"Overlaps published configuration '{other.name}' "
                            f"({o_start} to {o_end}) on turbine(s): {', '.join(shared_codes)}."
                        ),
                    )
                )

    return AvValidationReadinessResponse(
        is_valid=len(blocking_errors) == 0,
        blocking_errors=blocking_errors,
        warnings=warnings,
    )


def publish_av_version(
    db: Session,
    contract_id: UUID,
    acid: UUID,
    vid: UUID,
    actor: str,
) -> ConfigurationVersion:
    contract = _load_contract_with_assets(db, contract_id)
    av_config = next(
        (c for c in contract.availability_configurations if c.id == acid),
        None,
    )
    if av_config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Availability configuration not found.",
        )

    version = next((v for v in av_config.versions if v.id == vid), None)
    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration version not found.",
        )

    if version.status == ConfigurationStatus.PUBLISHED:
        return version

    readiness = validate_av_readiness(contract, av_config, version)
    if not readiness.is_valid:
        messages = "; ".join(err.message for err in readiness.blocking_errors)
        raise HTTPException(
            status_code=422,
            detail=f"Cannot publish configuration with blocking errors: {messages}",
        )

    # Archive any previously published version of THIS AV config
    db.execute(
        update(ConfigurationVersion)
        .where(
            ConfigurationVersion.availability_configuration_id == acid,
            ConfigurationVersion.status == ConfigurationStatus.PUBLISHED,
        )
        .values(status=ConfigurationStatus.ARCHIVED)
    )

    now = datetime.now(timezone.utc)
    version.status = ConfigurationStatus.PUBLISHED
    version.published_at = now
    av_config.updated_by = actor
    av_config.updated_at = now
    contract.status = ContractStatus.PUBLISHED

    db.commit()
    db.refresh(version)
    return version


def delete_availability_configuration(db: Session, contract_id: UUID, acid: UUID) -> None:
    av_config = _load_av_config(db, contract_id, acid)
    has_published = any(v.status == ConfigurationStatus.PUBLISHED for v in av_config.versions)
    if has_published:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete an availability configuration that has a published version.",
        )

    db.delete(av_config)
    db.commit()


def compute_av_diff(
    v_from: ConfigurationVersion,
    v_to: ConfigurationVersion,
) -> AvDiffResponse:
    from_snap = v_from.snapshot_data or {}
    to_snap = v_to.snapshot_data or {}

    from_basic = from_snap.get("basic_details") or {}
    to_basic = to_snap.get("basic_details") or {}
    basic_changes = {
        k: {"from": from_basic.get(k), "to": to_basic.get(k)}
        for k in sorted(set(from_basic.keys()) | set(to_basic.keys()))
        if from_basic.get(k) != to_basic.get(k)
    }

    from_turbines = {str(t) for t in (from_snap.get("turbine_ids") or [])}
    to_turbines = {str(t) for t in (to_snap.get("turbine_ids") or [])}

    from_formula = from_snap.get("formula_code")
    to_formula = to_snap.get("formula_code")
    formula_change = (
        {"from": from_formula, "to": to_formula} if from_formula != to_formula else None
    )

    from_alarms = {
        str(a["alarm_id"]): sorted(str(t) for t in a.get("turbine_ids", []))
        for a in (from_snap.get("alarm_assignments") or [])
    }
    to_alarms = {
        str(a["alarm_id"]): sorted(str(t) for t in a.get("turbine_ids", []))
        for a in (to_snap.get("alarm_assignments") or [])
    }

    added_alarms = sorted(set(to_alarms.keys()) - set(from_alarms.keys()))
    removed_alarms = sorted(set(from_alarms.keys()) - set(to_alarms.keys()))
    assignment_changes = [
        {"alarm_id": aid, "from": from_alarms[aid], "to": to_alarms[aid]}
        for aid in sorted(set(from_alarms.keys()) & set(to_alarms.keys()))
        if from_alarms[aid] != to_alarms[aid]
    ]

    from_details = from_snap.get("details") or {}
    to_details = to_snap.get("details") or {}
    details_changes = {
        k: {"from": from_details.get(k), "to": to_details.get(k)}
        for k in sorted(set(from_details.keys()) | set(to_details.keys()))
        if from_details.get(k) != to_details.get(k)
    }

    return AvDiffResponse(
        v_from_number=v_from.version_number,
        v_to_number=v_to.version_number,
        basic_details_changes=basic_changes,
        added_turbines=sorted(to_turbines - from_turbines),
        removed_turbines=sorted(from_turbines - to_turbines),
        formula_change=formula_change,
        added_alarms=added_alarms,
        removed_alarms=removed_alarms,
        alarm_assignment_changes=assignment_changes,
        details_changes=details_changes,
    )
