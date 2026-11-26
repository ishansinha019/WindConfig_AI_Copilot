from datetime import datetime, timezone
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.seed import (
    COASTAL_PLAINS_CONTRACT_ID,
    COASTAL_PLAINS_WIND_FARM_ID,
    NORTH_RIDGE_CONTRACT_ID,
    NORTH_RIDGE_WIND_FARM_ID,
    SYNTHETIC_TURBINES,
    seed_database,
)
from app.models.configuration import (
    LEGACY_CONFIGURATION_NAME,
    AvailabilityConfiguration,
    ConfigurationStatus,
    ConfigurationVersion,
)
from app.models.contract import Contract

NORTH_RIDGE_ID = str(NORTH_RIDGE_CONTRACT_ID)
COASTAL_PLAINS_ID = str(COASTAL_PLAINS_CONTRACT_ID)

VALID_SNAPSHOT_DATA = {
    "formula_type": "time_based_iec",
    "formula_name": "IEC 61400-26-1 Time-based Availability",
    "target_availability": 97.5,
    "included_alarm_codes": ["GRID", "MAINT", "WX"],
    "turbine_ids": [
        str(row["id"]) for row in SYNTHETIC_TURBINES if row["wind_farm_id"] == NORTH_RIDGE_WIND_FARM_ID
    ],
    "production_period_ids": [
        "3101f056-80d5-47bd-a8ee-208b913cf612",
        "3102f056-80d5-47bd-a8ee-208b913cf612",
    ],
    "variables": {
        "planned_maintenance_cap_hours": 120.0,
        "grid_outage_grace_period_hours": 4.0,
    },
}

COASTAL_VALID_SNAPSHOT = {
    "formula_type": "time_based_iec",
    "formula_name": "IEC 61400-26-1 Time-based Availability",
    "target_availability": 96.8,
    "included_alarm_codes": ["GRID", "MAINT"],
    "turbine_ids": [
        str(row["id"]) for row in SYNTHETIC_TURBINES
        if row["wind_farm_id"] == COASTAL_PLAINS_WIND_FARM_ID
    ],
    "production_period_ids": [
        "3201f056-80d5-47bd-a8ee-208b913cf612",
    ],
    "variables": {
        "grid_outage_grace_period_hours": 2.0,
    },
}


def test_create_and_fetch_draft_configuration(client: TestClient, db_session: Session) -> None:
    seed_database(db_session)

    # 1. North Ridge already has seeded v1
    active_res = client.get(f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration")
    assert active_res.status_code == 200
    assert active_res.json()["current_version"]["version_number"] == 1
    assert active_res.json()["current_version"]["status"] == "draft"

    # 2. Coastal Plains starts with 0 versions; save initial draft v1
    response = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/configuration/drafts",
        json={"base_version": None, "snapshot_data": COASTAL_VALID_SNAPSHOT},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["version_number"] == 1
    assert data["status"] == "draft"


def test_occ_conflict_on_stale_base_version(client: TestClient, db_session: Session) -> None:
    seed_database(db_session)

    # Coastal Plains starts at version 0. Save v1 (base_version=0 or None)
    v1_res = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/configuration/drafts",
        json={"base_version": None, "snapshot_data": COASTAL_VALID_SNAPSHOT},
    )
    assert v1_res.status_code == 201
    assert v1_res.json()["version_number"] == 1

    # Update with correct base_version=1 -> succeeds and produces v2
    v2_res = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/configuration/drafts",
        json={"base_version": 1, "snapshot_data": COASTAL_VALID_SNAPSHOT},
    )
    assert v2_res.status_code == 201
    assert v2_res.json()["version_number"] == 2

    # Attempt to update with stale base_version=1 while DB is at v2 -> HTTP 409 Conflict
    conflict_res = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/configuration/drafts",
        json={"base_version": 1, "snapshot_data": COASTAL_VALID_SNAPSHOT},
    )
    assert conflict_res.status_code == 409
    assert "Conflict" in conflict_res.json()["detail"]


def test_validation_blocks_publish_when_required_alarms_missing(client: TestClient, db_session: Session) -> None:
    seed_database(db_session)

    # Omit "GRID", which is is_required=True in synthetic seeds
    invalid_snapshot = dict(VALID_SNAPSHOT_DATA)
    invalid_snapshot["included_alarm_codes"] = ["MAINT", "WX"]

    draft_res = client.post(
        f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration/drafts",
        json={"base_version": 1, "snapshot_data": invalid_snapshot},
    )
    assert draft_res.status_code == 201
    version_id = draft_res.json()["id"]

    # Validate readiness
    val_res = client.get(f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration/versions/{version_id}/readiness")
    assert val_res.status_code == 200
    val_data = val_res.json()
    assert val_data["is_valid"] is False
    assert any("GRID" in err for err in val_data["blocking_errors"])

    # Attempting to publish must fail with 422
    publish_res = client.post(f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration/versions/{version_id}/publish")
    assert publish_res.status_code == 422
    assert "blocking errors" in publish_res.json()["detail"]


def test_validation_blocks_publish_when_turbines_unassigned(client: TestClient, db_session: Session) -> None:
    seed_database(db_session)

    # Include only two of the contract turbines.
    incomplete_snapshot = dict(VALID_SNAPSHOT_DATA)
    incomplete_snapshot["turbine_ids"] = [
        "1101f056-80d5-47bd-a8ee-208b913cf612",
        "1102f056-80d5-47bd-a8ee-208b913cf612",
    ]

    draft_res = client.post(
        f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration/drafts",
        json={"base_version": 1, "snapshot_data": incomplete_snapshot},
    )
    version_id = draft_res.json()["id"]

    val_res = client.get(f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration/versions/{version_id}/readiness")
    assert val_res.status_code == 200
    assert val_res.json()["is_valid"] is False
    assert any("turbines" in err.lower() for err in val_res.json()["blocking_errors"])


def test_successful_publish_and_immutability(client: TestClient, db_session: Session) -> None:
    seed_database(db_session)

    # Use seeded v1 of North Ridge (which is valid)
    active_res = client.get(f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration")
    v1_id = active_res.json()["current_version"]["id"]

    # Check readiness passes
    val_res = client.get(f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration/versions/{v1_id}/readiness")
    assert val_res.status_code == 200
    assert val_res.json()["is_valid"] is True

    # Publish v1
    pub_res = client.post(f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration/versions/{v1_id}/publish")
    assert pub_res.status_code == 200
    assert pub_res.json()["status"] == "published"
    assert pub_res.json()["published_at"] is not None

    # Attempt to modify or revert published version -> forbidden
    trans_res = client.post(
        f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration/versions/{v1_id}/transition",
        json={"target_status": "draft"},
    )
    assert trans_res.status_code == 400
    assert "Cannot transition from published to draft" in trans_res.json()["detail"]


def test_publish_second_version_archives_previous_published(client: TestClient, db_session: Session) -> None:
    seed_database(db_session)

    # Publish seeded v1
    v1_id = client.get(f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration").json()["current_version"]["id"]
    client.post(f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration/versions/{v1_id}/publish")

    # Create v2 draft (base_version=1)
    v2_id = client.post(
        f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration/drafts",
        json={"base_version": 1, "snapshot_data": VALID_SNAPSHOT_DATA},
    ).json()["id"]

    # Publish v2
    client.post(f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration/versions/{v2_id}/publish")

    # Verify v1 is now archived and v2 is published
    v1_check = client.get(f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration/versions/{v1_id}").json()
    v2_check = client.get(f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration/versions/{v2_id}").json()

    assert v1_check["status"] == "archived"
    assert v2_check["status"] == "published"


def test_configuration_diff_endpoint(client: TestClient, db_session: Session) -> None:
    seed_database(db_session)

    # Seeded v1 is at North Ridge
    v1_id = client.get(f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration").json()["current_version"]["id"]

    # Draft v2 modifies alarm codes and variables
    modified_data = dict(VALID_SNAPSHOT_DATA)
    modified_data["included_alarm_codes"] = ["GRID", "MAINT"]  # removed "WX"
    modified_data["variables"] = {"planned_maintenance_cap_hours": 150.0}

    v2_id = client.post(
        f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration/drafts",
        json={"base_version": 1, "snapshot_data": modified_data},
    ).json()["id"]

    # Diff v1 and v2
    diff_res = client.get(f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration/diff?v_from={v1_id}&v_to={v2_id}")
    assert diff_res.status_code == 200
    diff_data = diff_res.json()
    assert "WX" in diff_data["removed_alarms"]
    assert diff_data["variable_changes"]["planned_maintenance_cap_hours"]["from"] == 120.0
    assert diff_data["variable_changes"]["planned_maintenance_cap_hours"]["to"] == 150.0


def test_seeded_av_configurations_match_their_contract(db_session: Session) -> None:
    seed_database(db_session)

    contracts = list(db_session.scalars(select(Contract)))
    assert sorted(len(contract.availability_configurations) for contract in contracts) == [
        0, 1, 2, 3, 3, 12
    ]
    statuses = set()
    for contract in contracts:
        turbine_ids = {str(t.id) for farm in contract.wind_farms for t in farm.turbines}
        alarm_ids = {str(a.id) for category in contract.alarm_categories for a in category.alarms}
        for config in contract.availability_configurations:
            for version in config.versions:
                statuses.add(version.status)
                snapshot = version.snapshot_data
                assert set(snapshot["turbine_ids"]) <= turbine_ids
                assert version.checksum == ConfigurationVersion.calculate_checksum(snapshot)
                if config.name != LEGACY_CONFIGURATION_NAME:
                    assert snapshot["schema_version"] == 2
                    assert snapshot["basic_details"]["name"] == config.name
                    assert all(a["alarm_id"] in alarm_ids for a in snapshot["alarm_assignments"])
    assert statuses == {ConfigurationStatus.DRAFT, ConfigurationStatus.PUBLISHED}


def test_version_and_published_uniqueness_are_per_av_configuration(db_session: Session) -> None:
    seed_database(db_session)
    configs = list(db_session.scalars(select(AvailabilityConfiguration).where(
        AvailabilityConfiguration.contract_id == NORTH_RIDGE_CONTRACT_ID,
        AvailabilityConfiguration.name != LEGACY_CONFIGURATION_NAME,
    )))
    assert configs[0].id != configs[1].id

    for config in configs:
        config.versions[0].status = ConfigurationStatus.PUBLISHED
        config.versions[0].published_at = datetime.now(timezone.utc)
    db_session.flush()  # Two different configs may each have a published version.

    def add_version(number: int, state: ConfigurationStatus) -> None:
        db_session.add(ConfigurationVersion(
            availability_configuration_id=configs[0].id,
            version_number=number,
            status=state,
            snapshot_data={},
            checksum=ConfigurationVersion.calculate_checksum({}),
            created_by="Demo User",
        ))
        db_session.flush()

    with pytest.raises(IntegrityError), db_session.begin_nested():
        add_version(1, ConfigurationStatus.DRAFT)
    with pytest.raises(IntegrityError), db_session.begin_nested():
        add_version(2, ConfigurationStatus.PUBLISHED)


def test_legacy_api_cannot_modify_a_separate_av_configuration(
    client: TestClient, db_session: Session
) -> None:
    seed_database(db_session)
    version_id = db_session.scalar(
        select(ConfigurationVersion.id)
        .join(ConfigurationVersion.availability_configuration)
        .where(
            AvailabilityConfiguration.contract_id == NORTH_RIDGE_CONTRACT_ID,
            AvailabilityConfiguration.name != LEGACY_CONFIGURATION_NAME,
        )
    )
    assert version_id is not None

    response = client.post(
        f"/api/v1/contracts/{NORTH_RIDGE_ID}/configuration/versions/{version_id}/publish"
    )

    assert response.status_code == 404
