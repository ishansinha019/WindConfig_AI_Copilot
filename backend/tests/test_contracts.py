from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.seed import (
    COASTAL_PLAINS_CONTRACT_ID,
    NORTH_RIDGE_CONTRACT_ID,
    NORTH_RIDGE_LEGACY_TURBINES,
    NORTH_RIDGE_WIND_FARM_ID,
    SYNTHETIC_CONTRACTS,
    SYNTHETIC_TURBINE_GROUPS,
    SYNTHETIC_TURBINES,
    SYNTHETIC_WIND_FARMS,
    seed_database,
)
from app.models.configuration import (
    LEGACY_CONFIGURATION_NAME,
    Alarm,
    AvailabilityConfiguration,
    ConfigurationVersion,
)
from app.models.contract import Contract
from app.models.turbine import Turbine
from app.models.wind_farm import TurbineGroup, WindFarm


def test_contracts_endpoint_returns_seeded_contracts(client: TestClient, db_session: Session) -> None:
    seed_database(db_session)

    response = client.get("/api/v1/contracts")

    assert response.status_code == 200
    data = response.json()
    assert len(data["contracts"]) == 6
    contracts = {contract["id"]: contract for contract in data["contracts"]}
    north = contracts[str(NORTH_RIDGE_CONTRACT_ID)]
    assert north["name"] == "North Ridge Availability 2026"
    assert north["status"] == "needs_review"
    assert north["order_reason"] == "Long-term service agreement"
    assert north["sales_document_number"] == "9100000001"
    assert len(contracts[str(COASTAL_PLAINS_CONTRACT_ID)]["customer_names"]) == 2


def test_contract_detail_endpoint_returns_seeded_contract(client: TestClient, db_session: Session) -> None:
    seed_database(db_session)

    response = client.get("/api/v1/contracts/8fc90b56-80d5-47bd-a8ee-208b913cf612")

    assert response.status_code == 200
    assert response.json()["customer_name"] == "Aster Renewables"
    assert len(response.json()["wind_farms"][0]["turbines"]) == 10
    assert len(response.json()["production_periods"]) == 2
    assert len(response.json()["alarm_categories"]) == 3
    categories = {category["code"]: category for category in response.json()["alarm_categories"]}
    assert {alarm["code"] for alarm in categories["GRID"]["alarms"]} == {"GRID_LOW", "GRID_LOSS"}
    assert {alarm["code"] for alarm in categories["MAINT"]["alarms"]} == {"SERVICE", "BLADE"}


def test_contract_detail_scopes_turbines_and_alarms(client: TestClient, db_session: Session) -> None:
    seed_database(db_session)

    north = client.get(f"/api/v1/contracts/{NORTH_RIDGE_CONTRACT_ID}").json()
    coastal = client.get(f"/api/v1/contracts/{COASTAL_PLAINS_CONTRACT_ID}").json()
    north_turbines = north["wind_farms"][0]["turbines"]
    coastal_turbines = coastal["wind_farms"][0]["turbines"]

    assert {turbine["code"] for turbine in north_turbines} == {f"T{i:02}" for i in range(1, 11)}
    assert {turbine["code"] for turbine in coastal_turbines} == {f"T{i:02}" for i in range(1, 9)}
    for field in ("id", "model_name"):
        assert {t[field] for t in north_turbines}.isdisjoint(t[field] for t in coastal_turbines)
    north_alarm_ids = {a["id"] for category in north["alarm_categories"] for a in category["alarms"]}
    coastal_alarm_ids = {a["id"] for category in coastal["alarm_categories"] for a in category["alarms"]}
    assert len(north_alarm_ids) == len(coastal_alarm_ids) == 6
    assert north_alarm_ids.isdisjoint(coastal_alarm_ids)


def test_contract_detail_endpoint_returns_404_for_unknown_contract(client: TestClient) -> None:
    response = client.get("/api/v1/contracts/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json() == {"detail": "Contract not found."}


def test_seed_contracts_is_idempotent(db_session: Session) -> None:
    seed_database(db_session)

    def row_counts() -> list[int | None]:
        return [
            db_session.scalar(select(func.count()).select_from(model))
            for model in (Contract, Turbine, Alarm, AvailabilityConfiguration, ConfigurationVersion)
        ]

    counts_before = row_counts()
    contract = db_session.get(Contract, NORTH_RIDGE_CONTRACT_ID)
    assert contract is not None
    contract.order_reason = "Local demo edit"
    db_session.commit()

    seed_database(db_session)
    assert row_counts() == counts_before
    assert counts_before[:2] == [len(SYNTHETIC_CONTRACTS), len(SYNTHETIC_TURBINES)]
    assert contract.order_reason == "Local demo edit"


def test_seed_preserves_existing_fleet_and_backfilled_snapshot(db_session: Session) -> None:
    config_id = uuid4()
    snapshot = {"turbine_ids": [str(turbine_id) for turbine_id in NORTH_RIDGE_LEGACY_TURBINES]}
    checksum = ConfigurationVersion.calculate_checksum(snapshot)
    contract = Contract(**SYNTHETIC_CONTRACTS[0])
    contract.wind_farms = [WindFarm(**SYNTHETIC_WIND_FARMS[0])]
    contract.wind_farms[0].turbine_groups = [
        TurbineGroup(**row) for row in SYNTHETIC_TURBINE_GROUPS
        if row["wind_farm_id"] == NORTH_RIDGE_WIND_FARM_ID
    ]
    contract.wind_farms[0].turbines = [
        Turbine(**{**row, "code": f"NR-{i:02}"})
        for i, row in enumerate(SYNTHETIC_TURBINES[:4], start=1)
    ]
    contract.availability_configurations = [
        AvailabilityConfiguration(
            id=config_id, name=LEGACY_CONFIGURATION_NAME, created_by="Demo User",
            updated_by="Demo User", versions=[
                ConfigurationVersion(
                    version_number=1, snapshot_data=snapshot, checksum=checksum,
                    created_by="Demo User",
                )
            ],
        )
    ]
    db_session.add(contract)
    db_session.commit()

    seed_database(db_session)

    assert {t.code for t in contract.wind_farms[0].turbines} == {"NR-01", "NR-02", "NR-03", "NR-04"}
    legacy = [
        config for config in contract.availability_configurations
        if config.name == LEGACY_CONFIGURATION_NAME
    ]
    assert [config.id for config in legacy] == [config_id]
    assert [version.snapshot_data for version in legacy[0].versions] == [snapshot]
    assert legacy[0].versions[0].checksum == checksum
