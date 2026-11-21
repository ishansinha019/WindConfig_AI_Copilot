"""Synthetic development data for the local WindConfig database."""

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.contract import Contract, ContractStatus


SYNTHETIC_CONTRACTS = (
    {
        "id": UUID("8fc90b56-80d5-47bd-a8ee-208b913cf612"),
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
        "id": UUID("f7cb4118-1733-40c3-ae83-72a5f6a36d28"),
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


def seed_contracts(db: Session) -> None:
    """Insert demo contracts once; existing rows are left untouched."""
    for contract_data in SYNTHETIC_CONTRACTS:
        if db.get(Contract, contract_data["id"]) is None:
            db.add(Contract(**contract_data))
    db.commit()


def main() -> None:
    with SessionLocal() as db:
        seed_contracts(db)


if __name__ == "__main__":
    main()
