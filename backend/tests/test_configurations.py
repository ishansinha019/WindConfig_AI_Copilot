from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.seed import COASTAL_PLAINS_CONTRACT_ID, NORTH_RIDGE_CONTRACT_ID, seed_database

NORTH_RIDGE_ID = str(NORTH_RIDGE_CONTRACT_ID)
COASTAL_PLAINS_ID = str(COASTAL_PLAINS_CONTRACT_ID)

VALID_SNAPSHOT_DATA = {
    "formula_type": "time_based_iec",
    "formula_name": "IEC 61400-26-1 Time-based Availability",
    "target_availability": 97.5,
    "included_alarm_codes": ["GRID", "MAINT", "WX"],
    "turbine_ids": [
        "1101f056-80d5-47bd-a8ee-208b913cf612",
        "1102f056-80d5-47bd-a8ee-208b913cf612",
        "1103f056-80d5-47bd-a8ee-208b913cf612",
        "1104f056-80d5-47bd-a8ee-208b913cf612",
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
        "2201f056-80d5-47bd-a8ee-208b913cf612",
        "2202f056-80d5-47bd-a8ee-208b913cf612",
        "2203f056-80d5-47bd-a8ee-208b913cf612",
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

    # Include only 2 of the 4 contract turbines
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
