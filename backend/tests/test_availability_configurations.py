from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.seed import (
    COASTAL_PLAINS_CONTRACT_ID,
    NORTH_RIDGE_CONTRACT_ID,
    seed_database,
)

NORTH_RIDGE_ID = str(NORTH_RIDGE_CONTRACT_ID)
COASTAL_PLAINS_ID = str(COASTAL_PLAINS_CONTRACT_ID)


def _get_contract_assets(client: TestClient, contract_id: str) -> tuple[list[str], dict[str, list[str]]]:
    """Return (turbine_ids, {category_code: [alarm_ids]}) for a contract."""
    res = client.get(f"/api/v1/contracts/{contract_id}")
    assert res.status_code == 200
    data = res.json()
    turbine_ids = [
        t["id"]
        for wf in data["wind_farms"]
        for t in wf["turbines"]
    ]
    alarms_by_cat = {
        cat["code"]: [a["id"] for a in cat["alarms"]]
        for cat in data["alarm_categories"]
    }
    return turbine_ids, alarms_by_cat


def _make_valid_snapshot(
    name: str,
    turbine_ids: list[str],
    alarms_by_cat: dict[str, list[str]],
    start_date: str = "2028-01-01",
    end_date: str = "2028-12-31",
    calc_type: str = "TBA",
    formula_code: str = "TBA_STD",
) -> dict[str, Any]:
    required_alarm_ids = [
        alarms_by_cat["GRID"][0],
        alarms_by_cat["MAINT"][0],
    ]
    return {
        "schema_version": 2,
        "basic_details": {
            "name": name,
            "calculation_type": calc_type,
            "start_date": start_date,
            "end_date": end_date,
        },
        "turbine_ids": turbine_ids,
        "formula_code": formula_code,
        "alarm_assignments": [
            {"alarm_id": aid, "turbine_ids": turbine_ids}
            for aid in required_alarm_ids
        ],
        "details": {
            "park_availability_pct": 97.5,
            "low_wind_variant": "LW_EXCLUDE_BELOW_CUT_IN",
            "high_wind_variant": "HW_EXCLUDE_ABOVE_CUT_OUT",
        },
    }


def test_catalog_and_users_endpoints(client: TestClient) -> None:
    cat_res = client.get("/api/v1/catalog")
    assert cat_res.status_code == 200
    cat_data = cat_res.json()
    calc_codes = {c["code"] for c in cat_data["calculation_types"]}
    assert calc_codes == {"TBA", "YBA", "RBA"}
    assert len(cat_data["formulas"]) >= 6
    assert len(cat_data["low_wind_variants"]) >= 3
    assert len(cat_data["high_wind_variants"]) >= 3

    users_res = client.get("/api/v1/users")
    assert users_res.status_code == 200
    assert "Demo User" in users_res.json()["users"]


def test_contracts_list_returns_card_fields_and_av_summaries(
    client: TestClient, db_session: Session
) -> None:
    seed_database(db_session)

    res = client.get("/api/v1/contracts")
    assert res.status_code == 200
    contracts = res.json()["contracts"]
    assert len(contracts) == 6

    first = contracts[0]
    assert "order_reason" in first
    assert "sales_document_number" in first
    assert "customer_names" in first
    assert "is_live" in first
    assert "turbine_count" in first
    assert "availability_configurations" in first
    assert isinstance(first["turbine_count"], int)
    assert first["turbine_count"] > 0

    north_ridge = next(c for c in contracts if c["id"] == NORTH_RIDGE_ID)
    assert north_ridge["turbine_count"] == 10
    assert len(north_ridge["availability_configurations"]) >= 2


def test_create_av_config_guid_and_acting_user_and_roundtrip(
    client: TestClient, db_session: Session
) -> None:
    seed_database(db_session)
    turbine_ids, alarms_by_cat = _get_contract_assets(client, COASTAL_PLAINS_ID)

    # Dates outside contract dates (Coastal Plains is 2026-04-01 to 2029-03-31) must be accepted
    snap1 = _make_valid_snapshot(
        "Renewal 2030 TBA",
        turbine_ids[:4],
        alarms_by_cat,
        start_date="2030-01-01",
        end_date="2030-12-31",
    )
    res1 = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations",
        json={"snapshot_data": snap1},
        headers={"X-User-Name": "Avery Demo"},
    )
    assert res1.status_code == 201
    c1 = res1.json()
    assert c1["name"] == "Renewal 2030 TBA"
    assert c1["created_by"] == "Avery Demo"
    assert c1["updated_by"] == "Avery Demo"
    assert c1["latest_version"]["version_number"] == 1
    assert c1["latest_version"]["created_by"] == "Avery Demo"
    assert c1["latest_version"]["snapshot_data"] == snap1

    # Second config gets a distinct GUID; missing X-User-Name falls back to "Demo User"
    snap2 = _make_valid_snapshot("Renewal 2031 YBA", turbine_ids[4:], alarms_by_cat, calc_type="YBA", formula_code="YBA_STD")
    res2 = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations",
        json={"snapshot_data": snap2},
    )
    assert res2.status_code == 201
    c2 = res2.json()
    assert c2["id"] != c1["id"]
    assert c2["created_by"] == "Demo User"

    # Reload by GUID preserves full wizard JSON
    get_res = client.get(f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{c1['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["latest_version"]["snapshot_data"] == snap1


def test_create_without_name_returns_422(client: TestClient, db_session: Session) -> None:
    seed_database(db_session)

    res = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations",
        json={
            "snapshot_data": {
                "schema_version": 2,
                "basic_details": {"name": "   "},
            }
        },
    )
    assert res.status_code == 422


def test_save_draft_occ_conflict_and_foreign_scoping(
    client: TestClient, db_session: Session
) -> None:
    seed_database(db_session)
    cp_turbines, cp_alarms = _get_contract_assets(client, COASTAL_PLAINS_ID)
    nr_turbines, nr_alarms = _get_contract_assets(client, NORTH_RIDGE_ID)

    # Create initial v1
    snap = _make_valid_snapshot("OCC Test Config", cp_turbines, cp_alarms)
    create_res = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations",
        json={"snapshot_data": snap},
        headers={"X-User-Name": "Rowan Demo"},
    )
    assert create_res.status_code == 201
    acid = create_res.json()["id"]

    # Foreign turbine UUID -> 422
    foreign_turbine_snap = _make_valid_snapshot("OCC Test Config", [nr_turbines[0]], cp_alarms)
    bad_t = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{acid}/drafts",
        json={"base_version": 1, "snapshot_data": foreign_turbine_snap},
    )
    assert bad_t.status_code == 422

    # Foreign alarm UUID -> 422
    foreign_alarm_snap = _make_valid_snapshot("OCC Test Config", cp_turbines, nr_alarms)
    bad_a = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{acid}/drafts",
        json={"base_version": 1, "snapshot_data": foreign_alarm_snap},
    )
    assert bad_a.status_code == 422

    # Valid save draft v2
    v2_res = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{acid}/drafts",
        json={"base_version": 1, "snapshot_data": snap},
        headers={"X-User-Name": "Sage Demo"},
    )
    assert v2_res.status_code == 201
    assert v2_res.json()["version_number"] == 2
    assert v2_res.json()["created_by"] == "Sage Demo"

    # Stale base_version=1 -> 409 Conflict
    conflict_res = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{acid}/drafts",
        json={"base_version": 1, "snapshot_data": snap},
    )
    assert conflict_res.status_code == 409


def test_readiness_validation_rules_and_step_hints(
    client: TestClient, db_session: Session
) -> None:
    seed_database(db_session)
    cp_turbines, cp_alarms = _get_contract_assets(client, COASTAL_PLAINS_ID)

    # Partial draft missing almost everything
    partial_snap = {
        "schema_version": 2,
        "basic_details": {
            "name": "Incomplete Config",
            "calculation_type": "TBA",
            "start_date": "2028-12-31",
            "end_date": "2028-01-01",  # inverted dates
        },
        "turbine_ids": [],  # empty turbines
        "formula_code": "YBA_STD",  # mismatches TBA
        "alarm_assignments": [],  # missing required GRID & MAINT
        "details": {
            "park_availability_pct": 105.0,  # > 100
            "low_wind_variant": "INVALID_LW",
            "high_wind_variant": None,
        },
    }
    create_res = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations",
        json={"snapshot_data": partial_snap},
    )
    assert create_res.status_code == 201
    acid = create_res.json()["id"]
    vid = create_res.json()["latest_version"]["id"]

    readiness_res = client.get(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{acid}/versions/{vid}/readiness"
    )
    assert readiness_res.status_code == 200
    r = readiness_res.json()
    assert r["is_valid"] is False
    steps_with_errors = {err["step"] for err in r["blocking_errors"]}
    assert {1, 2, 3, 4}.issubset(steps_with_errors)

    # Publishing must fail with 422
    pub_res = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{acid}/versions/{vid}/publish"
    )
    assert pub_res.status_code == 422

    # Warning when a turbine in scope has no alarm assigned
    warn_snap = _make_valid_snapshot("Warning Check", cp_turbines[:2], cp_alarms)
    warn_snap["alarm_assignments"] = [
        {"alarm_id": cp_alarms["GRID"][0], "turbine_ids": [cp_turbines[0]]},
        {"alarm_id": cp_alarms["MAINT"][0], "turbine_ids": [cp_turbines[0]]},
    ]
    w_res = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations",
        json={"snapshot_data": warn_snap},
    )
    w_acid = w_res.json()["id"]
    w_vid = w_res.json()["latest_version"]["id"]
    w_readiness = client.get(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{w_acid}/versions/{w_vid}/readiness"
    ).json()
    assert w_readiness["is_valid"] is True
    assert len(w_readiness["warnings"]) >= 1


def test_publish_republish_and_overlap_blocking(
    client: TestClient, db_session: Session
) -> None:
    seed_database(db_session)
    cp_turbines, cp_alarms = _get_contract_assets(client, COASTAL_PLAINS_ID)

    # 1. Publish Config A (turbines 0..3, 2028-01-01 to 2028-12-31)
    snap_a = _make_valid_snapshot("Config A", cp_turbines[:4], cp_alarms, "2028-01-01", "2028-12-31")
    a_res = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations",
        json={"snapshot_data": snap_a},
    ).json()
    a_id, a_v1_id = a_res["id"], a_res["latest_version"]["id"]
    pub_a = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{a_id}/versions/{a_v1_id}/publish"
    )
    assert pub_a.status_code == 200
    assert pub_a.json()["status"] == "published"

    # Republishing Config A v2 should succeed (ignores its own v1) and archive v1
    a_v2_res = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{a_id}/drafts",
        json={"base_version": 1, "snapshot_data": snap_a},
    ).json()
    pub_a2 = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{a_id}/versions/{a_v2_res['id']}/publish"
    )
    assert pub_a2.status_code == 200
    v1_after = client.get(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{a_id}/versions/{a_v1_id}"
    ).json()
    assert v1_after["status"] == "archived"

    # 2. Non-overlapping Config B (same dates, disjoint turbines 4..7) -> allowed to publish
    snap_b = _make_valid_snapshot("Config B", cp_turbines[4:], cp_alarms, "2028-01-01", "2028-12-31")
    b_res = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations",
        json={"snapshot_data": snap_b},
    ).json()
    pub_b = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{b_res['id']}/versions/{b_res['latest_version']['id']}/publish"
    )
    assert pub_b.status_code == 200

    # 3. Non-overlapping Config C (same turbines 0..3, non-intersecting dates 2029-01-01..2029-12-31) -> allowed
    snap_c = _make_valid_snapshot("Config C", cp_turbines[:4], cp_alarms, "2029-01-01", "2029-12-31")
    c_res = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations",
        json={"snapshot_data": snap_c},
    ).json()
    pub_c = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{c_res['id']}/versions/{c_res['latest_version']['id']}/publish"
    )
    assert pub_c.status_code == 200

    # 4. Overlapping Config D (shares turbine[0] with Config A AND intersects 2028-12-31 inclusive) -> blocked
    snap_d = _make_valid_snapshot("Config D Overlap", [cp_turbines[0]], cp_alarms, "2028-12-31", "2029-06-30")
    d_res = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations",
        json={"snapshot_data": snap_d},
    ).json()
    pub_d = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{d_res['id']}/versions/{d_res['latest_version']['id']}/publish"
    )
    assert pub_d.status_code == 422
    assert "Config A" in pub_d.json()["detail"]


def test_delete_rules_and_diff(client: TestClient, db_session: Session) -> None:
    seed_database(db_session)
    cp_turbines, cp_alarms = _get_contract_assets(client, COASTAL_PLAINS_ID)

    # Create draft with 2 versions and diff them
    snap1 = _make_valid_snapshot("Diff & Delete", cp_turbines[:2], cp_alarms)
    c_res = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations",
        json={"snapshot_data": snap1},
    ).json()
    acid, v1_id = c_res["id"], c_res["latest_version"]["id"]

    snap2 = _make_valid_snapshot("Diff & Delete", cp_turbines[:3], cp_alarms, calc_type="YBA", formula_code="YBA_STD")
    v2_res = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{acid}/drafts",
        json={"base_version": 1, "snapshot_data": snap2},
    ).json()
    v2_id = v2_res["id"]

    diff_res = client.get(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{acid}/diff?v_from={v1_id}&v_to={v2_id}"
    )
    assert diff_res.status_code == 200
    diff = diff_res.json()
    assert cp_turbines[2] in diff["added_turbines"]
    assert diff["formula_change"] == {"from": "TBA_STD", "to": "YBA_STD"}

    # Wrong contract GUID -> 404
    wrong_del = client.delete(f"/api/v1/contracts/{NORTH_RIDGE_ID}/availability-configurations/{acid}")
    assert wrong_del.status_code == 404

    # Delete draft -> 204, subsequent GET -> 404
    del_res = client.delete(f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{acid}")
    assert del_res.status_code == 204
    assert client.get(f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{acid}").status_code == 404

    # Cannot delete a published config -> 409
    snap_pub = _make_valid_snapshot("Published Lock", cp_turbines[:2], cp_alarms)
    p_res = client.post(
        f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations",
        json={"snapshot_data": snap_pub},
    ).json()
    p_id, p_vid = p_res["id"], p_res["latest_version"]["id"]
    client.post(f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{p_id}/versions/{p_vid}/publish")

    del_pub = client.delete(f"/api/v1/contracts/{COASTAL_PLAINS_ID}/availability-configurations/{p_id}")
    assert del_pub.status_code == 409
