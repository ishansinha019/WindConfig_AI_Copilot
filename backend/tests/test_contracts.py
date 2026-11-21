from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.seed import SYNTHETIC_CONTRACTS, SYNTHETIC_TURBINES, seed_database
from app.models.contract import Contract
from app.models.turbine import Turbine


def test_contracts_endpoint_returns_seeded_contracts(client: TestClient, db_session: Session) -> None:
    seed_database(db_session)

    response = client.get("/api/v1/contracts")

    assert response.status_code == 200
    data = response.json()
    assert len(data["contracts"]) == 2
    assert data["contracts"][0]["name"] == "North Ridge Availability 2026"
    assert data["contracts"][0]["status"] == "needs_review"


def test_contract_detail_endpoint_returns_seeded_contract(client: TestClient, db_session: Session) -> None:
    seed_database(db_session)

    response = client.get("/api/v1/contracts/8fc90b56-80d5-47bd-a8ee-208b913cf612")

    assert response.status_code == 200
    assert response.json()["customer_name"] == "Aster Renewables"
    assert len(response.json()["wind_farms"][0]["turbines"]) == 4
    assert len(response.json()["production_periods"]) == 2
    assert len(response.json()["alarm_categories"]) == 3


def test_contract_detail_endpoint_returns_404_for_unknown_contract(client: TestClient) -> None:
    response = client.get("/api/v1/contracts/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json() == {"detail": "Contract not found."}


def test_seed_contracts_is_idempotent(db_session: Session) -> None:
    seed_database(db_session)
    seed_database(db_session)

    count = db_session.scalar(select(func.count()).select_from(Contract))

    assert count == len(SYNTHETIC_CONTRACTS)
    assert db_session.get(Contract, UUID("8fc90b56-80d5-47bd-a8ee-208b913cf612")) is not None
    turbine_count = db_session.scalar(select(func.count()).select_from(Turbine))

    assert turbine_count == len(SYNTHETIC_TURBINES)
