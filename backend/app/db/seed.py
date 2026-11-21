"""Synthetic development data for the local WindConfig database."""

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.configuration import AlarmCategory, ProductionPeriod
from app.models.contract import Contract, ContractStatus
from app.models.turbine import Turbine
from app.models.wind_farm import TurbineGroup, WindFarm

NORTH_RIDGE_CONTRACT_ID = UUID("8fc90b56-80d5-47bd-a8ee-208b913cf612")
COASTAL_PLAINS_CONTRACT_ID = UUID("f7cb4118-1733-40c3-ae83-72a5f6a36d28")
NORTH_RIDGE_WIND_FARM_ID = UUID("11b0f056-80d5-47bd-a8ee-208b913cf612")
COASTAL_PLAINS_WIND_FARM_ID = UUID("22b0f056-80d5-47bd-a8ee-208b913cf612")
NORTH_SECTION_ID = UUID("1010f056-80d5-47bd-a8ee-208b913cf612")
SOUTH_SECTION_ID = UUID("1020f056-80d5-47bd-a8ee-208b913cf612")
COASTAL_ARRAY_ID = UUID("2010f056-80d5-47bd-a8ee-208b913cf612")

SYNTHETIC_CONTRACTS = (
    {
        "id": NORTH_RIDGE_CONTRACT_ID,
        "name": "North Ridge Availability 2026",
        "customer_name": "Aster Renewables",
        "wind_farm_name": "North Ridge Wind Farm",
        "region": "Tamil Nadu",
        "status": ContractStatus.NEEDS_REVIEW,
        "start_date": date(2026, 1, 1),
        "end_date": date(2028, 12, 31),
        "target_availability": 97.5,
    },
    {
        "id": COASTAL_PLAINS_CONTRACT_ID,
        "name": "Coastal Plains Service Agreement",
        "customer_name": "HelioWind Operations",
        "wind_farm_name": "Coastal Plains Cluster",
        "region": "Gujarat",
        "status": ContractStatus.DRAFT,
        "start_date": date(2026, 4, 1),
        "end_date": date(2029, 3, 31),
        "target_availability": 96.8,
    },
)

SYNTHETIC_WIND_FARMS = (
    {
        "id": NORTH_RIDGE_WIND_FARM_ID,
        "contract_id": NORTH_RIDGE_CONTRACT_ID,
        "name": "North Ridge Wind Farm",
        "region": "Tamil Nadu",
    },
    {
        "id": COASTAL_PLAINS_WIND_FARM_ID,
        "contract_id": COASTAL_PLAINS_CONTRACT_ID,
        "name": "Coastal Plains Cluster",
        "region": "Gujarat",
    },
)

SYNTHETIC_TURBINE_GROUPS = (
    {"id": NORTH_SECTION_ID, "wind_farm_id": NORTH_RIDGE_WIND_FARM_ID, "name": "North Section"},
    {"id": SOUTH_SECTION_ID, "wind_farm_id": NORTH_RIDGE_WIND_FARM_ID, "name": "South Section"},
    {"id": COASTAL_ARRAY_ID, "wind_farm_id": COASTAL_PLAINS_WIND_FARM_ID, "name": "Coastal Array"},
)


def turbine(
    identifier: str,
    wind_farm_id: UUID,
    turbine_group_id: UUID,
    code: str,
    model_name: str,
    rated_power_mw: float,
) -> dict:
    return {
        "id": UUID(identifier),
        "wind_farm_id": wind_farm_id,
        "turbine_group_id": turbine_group_id,
        "code": code,
        "model_name": model_name,
        "rated_power_mw": rated_power_mw,
    }


SYNTHETIC_TURBINES = (
    turbine("1101f056-80d5-47bd-a8ee-208b913cf612", NORTH_RIDGE_WIND_FARM_ID, NORTH_SECTION_ID, "NR-01", "Vestas V136", 4.2),
    turbine("1102f056-80d5-47bd-a8ee-208b913cf612", NORTH_RIDGE_WIND_FARM_ID, NORTH_SECTION_ID, "NR-02", "Vestas V136", 4.2),
    turbine("1103f056-80d5-47bd-a8ee-208b913cf612", NORTH_RIDGE_WIND_FARM_ID, SOUTH_SECTION_ID, "NR-03", "Vestas V136", 4.2),
    turbine("1104f056-80d5-47bd-a8ee-208b913cf612", NORTH_RIDGE_WIND_FARM_ID, SOUTH_SECTION_ID, "NR-04", "Vestas V136", 4.2),
    turbine("2201f056-80d5-47bd-a8ee-208b913cf612", COASTAL_PLAINS_WIND_FARM_ID, COASTAL_ARRAY_ID, "CP-01", "Suzlon S120", 3.0),
    turbine("2202f056-80d5-47bd-a8ee-208b913cf612", COASTAL_PLAINS_WIND_FARM_ID, COASTAL_ARRAY_ID, "CP-02", "Suzlon S120", 3.0),
    turbine("2203f056-80d5-47bd-a8ee-208b913cf612", COASTAL_PLAINS_WIND_FARM_ID, COASTAL_ARRAY_ID, "CP-03", "Suzlon S120", 3.0),
)

SYNTHETIC_PRODUCTION_PERIODS = (
    {
        "id": UUID("3101f056-80d5-47bd-a8ee-208b913cf612"),
        "contract_id": NORTH_RIDGE_CONTRACT_ID,
        "name": "Southwest Monsoon",
        "start_date": date(2026, 6, 1),
        "end_date": date(2026, 9, 30),
    },
    {
        "id": UUID("3102f056-80d5-47bd-a8ee-208b913cf612"),
        "contract_id": NORTH_RIDGE_CONTRACT_ID,
        "name": "Northeast Monsoon",
        "start_date": date(2026, 10, 1),
        "end_date": date(2026, 12, 31),
    },
    {
        "id": UUID("3201f056-80d5-47bd-a8ee-208b913cf612"),
        "contract_id": COASTAL_PLAINS_CONTRACT_ID,
        "name": "High Wind Season",
        "start_date": date(2026, 5, 1),
        "end_date": date(2026, 8, 31),
    },
)


def alarm(identifier: str, contract_id: UUID, code: str, name: str, required: bool) -> dict:
    return {
        "id": UUID(identifier),
        "contract_id": contract_id,
        "code": code,
        "name": name,
        "is_required": required,
    }


SYNTHETIC_ALARM_CATEGORIES = (
    alarm("4101f056-80d5-47bd-a8ee-208b913cf612", NORTH_RIDGE_CONTRACT_ID, "GRID", "Grid interruption", True),
    alarm("4102f056-80d5-47bd-a8ee-208b913cf612", NORTH_RIDGE_CONTRACT_ID, "MAINT", "Planned maintenance", True),
    alarm("4103f056-80d5-47bd-a8ee-208b913cf612", NORTH_RIDGE_CONTRACT_ID, "WX", "Weather event", False),
    alarm("4201f056-80d5-47bd-a8ee-208b913cf612", COASTAL_PLAINS_CONTRACT_ID, "GRID", "Grid interruption", True),
    alarm("4202f056-80d5-47bd-a8ee-208b913cf612", COASTAL_PLAINS_CONTRACT_ID, "MAINT", "Planned maintenance", True),
)


def seed_contracts(db: Session) -> None:
    _seed_rows(db, Contract, SYNTHETIC_CONTRACTS)


def _seed_rows(db: Session, model: type[object], rows: tuple[dict, ...]) -> None:
    for row in rows:
        if db.get(model, row["id"]) is None:
            db.add(model(**row))
    db.commit()


def seed_database(db: Session) -> None:
    """Insert stable synthetic records once, preserving existing local edits."""
    seed_contracts(db)
    _seed_rows(db, WindFarm, SYNTHETIC_WIND_FARMS)
    _seed_rows(db, TurbineGroup, SYNTHETIC_TURBINE_GROUPS)
    _seed_rows(db, Turbine, SYNTHETIC_TURBINES)
    _seed_rows(db, ProductionPeriod, SYNTHETIC_PRODUCTION_PERIODS)
    _seed_rows(db, AlarmCategory, SYNTHETIC_ALARM_CATEGORIES)


def main() -> None:
    with SessionLocal() as db:
        seed_database(db)


if __name__ == "__main__":
    main()
