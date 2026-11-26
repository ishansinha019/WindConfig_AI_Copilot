"""Synthetic development data for the local WindConfig database."""

from datetime import date, datetime, timedelta, timezone
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.configuration import (
    DEMO_ACTOR,
    LEGACY_CONFIGURATION_NAME,
    Alarm,
    AlarmCategory,
    AvailabilityConfiguration,
    ConfigurationStatus,
    ConfigurationVersion,
    ProductionPeriod,
)
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


def demo_id(key: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"windconfig/demo/{key}")


EXTRA_SITES = (
    # Key, wind farm, region, customer names, fleet size, model, MW, config count
    ("mesa", "Copper Mesa", "Rajasthan",
     ["Juniper Current", "Mesa Wind Partners"], 9, "Demo M48", 4.8, 12),
    ("valley", "Silver Valley", "Karnataka", ["Cirrus Grid"], 7, "Demo V36", 3.6, 3),
    ("moor", "Amber Moor", "Maharashtra",
     ["Thistle Energy", "Moor Operations", "Moor Service"], 6, "Demo A42", 4.2, 2),
    ("lake", "Lark Lake", "Madhya Pradesh", ["Lark Generation"], 10, "Demo L54", 5.4, 1),
)

SYNTHETIC_CONTRACTS = (
    {
        "id": NORTH_RIDGE_CONTRACT_ID,
        "name": "North Ridge Availability 2026",
        "customer_names": ["Aster Renewables"],
        "order_reason": "Long-term service agreement",
        "sales_document_number": "9100000001",
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
        "customer_names": ["HelioWind Operations", "Blue Dune Services"],
        "order_reason": "Long-term service agreement",
        "sales_document_number": "9100000002",
        "wind_farm_name": "Coastal Plains Cluster",
        "region": "Gujarat",
        "status": ContractStatus.DRAFT,
        "start_date": date(2026, 4, 1),
        "end_date": date(2029, 3, 31),
        "target_availability": 96.8,
    },
    *(
        {
            "id": demo_id(f"{key}/contract"),
            "name": f"{site} Wind Service",
            "customer_names": customers,
            "order_reason": "Warranty" if index % 2 == 0 else "Long-term service agreement",
            "sales_document_number": f"{9100000003 + index}",
            "wind_farm_name": f"{site} Wind Farm",
            "region": region,
            "status": ContractStatus.PUBLISHED,
            "start_date": date(2026, 2, 1) if index % 2 == 0 else date(2023, 2, 1),
            "end_date": date(2030, 1, 31) if index % 2 == 0 else date(2025, 1, 31),
            "target_availability": 96.0 + index / 2,
        }
        for index, (key, site, region, customers, *_) in enumerate(EXTRA_SITES)
    ),
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
    *(
        {
            "id": demo_id(f"{key}/farm"),
            "contract_id": demo_id(f"{key}/contract"),
            "name": f"{site} Wind Farm",
            "region": region,
        }
        for key, site, region, *_ in EXTRA_SITES
    ),
)

INLAND_ARRAY_ID = demo_id("coastal/inland")

SYNTHETIC_TURBINE_GROUPS = (
    {"id": NORTH_SECTION_ID, "wind_farm_id": NORTH_RIDGE_WIND_FARM_ID, "name": "North Section"},
    {"id": SOUTH_SECTION_ID, "wind_farm_id": NORTH_RIDGE_WIND_FARM_ID, "name": "South Section"},
    {"id": COASTAL_ARRAY_ID, "wind_farm_id": COASTAL_PLAINS_WIND_FARM_ID, "name": "Coastal Array"},
    {"id": INLAND_ARRAY_ID, "wind_farm_id": COASTAL_PLAINS_WIND_FARM_ID, "name": "Inland Array"},
    *(
        {"id": demo_id(f"{key}/group"), "wind_farm_id": demo_id(f"{key}/farm"), "name": f"{site} Array"}
        for key, site, *_ in EXTRA_SITES
    ),
)


def turbine(
    turbine_id: UUID,
    wind_farm_id: UUID,
    turbine_group_id: UUID,
    code: str,
    model_name: str,
    rated_power_mw: float,
) -> dict:
    return {
        "id": turbine_id,
        "wind_farm_id": wind_farm_id,
        "turbine_group_id": turbine_group_id,
        "code": code,
        "model_name": model_name,
        "rated_power_mw": rated_power_mw,
    }


NORTH_RIDGE_LEGACY_TURBINES = tuple(
    UUID(f"110{i}f056-80d5-47bd-a8ee-208b913cf612") for i in range(1, 5)
)
COASTAL_PLAINS_LEGACY_TURBINES = tuple(
    UUID(f"220{i}f056-80d5-47bd-a8ee-208b913cf612") for i in range(1, 4)
)

SYNTHETIC_TURBINES = (
    *(
        turbine(
            NORTH_RIDGE_LEGACY_TURBINES[i - 1] if i <= 4 else demo_id(f"north/turbine/{i}"),
            NORTH_RIDGE_WIND_FARM_ID, NORTH_SECTION_ID if i <= 5 else SOUTH_SECTION_ID,
            f"T{i:02}", "Demo N50", 5.0,
        )
        for i in range(1, 11)
    ),
    *(
        turbine(
            COASTAL_PLAINS_LEGACY_TURBINES[i - 1] if i <= 3 else demo_id(f"coastal/turbine/{i}"),
            COASTAL_PLAINS_WIND_FARM_ID, COASTAL_ARRAY_ID if i <= 3 else INLAND_ARRAY_ID,
            f"T{i:02}", "Demo C66", 6.6,
        )
        for i in range(1, 9)
    ),
    *(
        turbine(demo_id(f"{key}/turbine/{i}"), demo_id(f"{key}/farm"), demo_id(f"{key}/group"),
                f"T{i:02}", model, mw)
        for key, _, _, _, count, model, mw, _ in EXTRA_SITES
        for i in range(1, count + 1)
    ),
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


def alarm_category(category_id: UUID, contract_id: UUID, code: str, name: str, required: bool) -> dict:
    return {
        "id": category_id,
        "contract_id": contract_id,
        "code": code,
        "name": name,
        "is_required": required,
    }


ALARM_CATALOG = (
    ("GRID", "Grid interruption", True, (("GRID_LOW", "Grid voltage low"), ("GRID_LOSS", "Grid loss"))),
    ("MAINT", "Planned maintenance", True, (("SERVICE", "Scheduled service"), ("BLADE", "Blade inspection"))),
    ("WX", "Weather event", False, (("ICE", "Icing"), ("STORM", "Storm shutdown"))),
)
NORTH_RIDGE_CATEGORIES = tuple(
    UUID(f"410{i}f056-80d5-47bd-a8ee-208b913cf612") for i in range(1, 4)
)
COASTAL_PLAINS_CATEGORIES = (
    UUID("4201f056-80d5-47bd-a8ee-208b913cf612"),
    UUID("4202f056-80d5-47bd-a8ee-208b913cf612"),
    demo_id("coastal/alarm/WX"),
)

SYNTHETIC_ALARM_CATEGORIES = (
    *(
        alarm_category(category_id, contract_id, code, name, required)
        for contract_id, category_ids in (
            (NORTH_RIDGE_CONTRACT_ID, NORTH_RIDGE_CATEGORIES),
            (COASTAL_PLAINS_CONTRACT_ID, COASTAL_PLAINS_CATEGORIES),
        )
        for category_id, (code, name, required, _) in zip(category_ids, ALARM_CATALOG, strict=True)
    ),
    *(
        alarm_category(demo_id(f"{key}/alarm/{code}"), demo_id(f"{key}/contract"), code, name, required)
        for key, *_ in EXTRA_SITES
        for code, name, required, _ in ALARM_CATALOG
    ),
)

SYNTHETIC_ALARMS = tuple(
    {
        "id": demo_id(f"{category['id']}/{alarm_code}"),
        "alarm_category_id": category["id"],
        "code": alarm_code,
        "name": alarm_name,
    }
    for category in SYNTHETIC_ALARM_CATEGORIES
    for code, _, _, alarms in ALARM_CATALOG
    if category["code"] == code
    for alarm_code, alarm_name in alarms
)

NORTH_RIDGE_V1_SNAPSHOT = {
    "formula_type": "time_based_iec",
    "formula_name": "IEC 61400-26-1 Time-based Availability",
    "target_availability": 97.5,
    "included_alarm_codes": ["GRID", "MAINT", "WX"],
    "production_period_ids": [
        "3101f056-80d5-47bd-a8ee-208b913cf612",
        "3102f056-80d5-47bd-a8ee-208b913cf612",
    ],
    "variables": {
        "planned_maintenance_cap_hours": 120.0,
        "grid_outage_grace_period_hours": 4.0,
    },
}


def _turbine_ids(db: Session, farm_id: UUID, limit: int | None = None) -> list[str]:
    statement = select(Turbine.id).where(Turbine.wind_farm_id == farm_id).order_by(Turbine.code)
    if limit is not None:
        statement = statement.limit(limit)
    return [str(turbine_id) for turbine_id in db.scalars(statement)]


def _seed_legacy_configuration(db: Session) -> None:
    existing = db.scalar(
        select(AvailabilityConfiguration.id).where(
            AvailabilityConfiguration.contract_id == NORTH_RIDGE_CONTRACT_ID,
            AvailabilityConfiguration.name == LEGACY_CONFIGURATION_NAME,
        )
    )
    if existing is not None:
        return

    snapshot = {
        **NORTH_RIDGE_V1_SNAPSHOT,
        "turbine_ids": _turbine_ids(db, NORTH_RIDGE_WIND_FARM_ID),
    }
    db.add(
        AvailabilityConfiguration(
            id=demo_id("north/legacy"),
            contract_id=NORTH_RIDGE_CONTRACT_ID,
            name=LEGACY_CONFIGURATION_NAME,
            created_by=DEMO_ACTOR,
            updated_by=DEMO_ACTOR,
            versions=[
                ConfigurationVersion(
                    id=UUID("5101f056-80d5-47bd-a8ee-208b913cf612"),
                    version_number=1,
                    status=ConfigurationStatus.DRAFT,
                    snapshot_data=snapshot,
                    checksum=ConfigurationVersion.calculate_checksum(snapshot),
                    created_by=DEMO_ACTOR,
                )
            ],
        )
    )


def _seed_availability_configurations(db: Session) -> None:
    portfolios = (
        (NORTH_RIDGE_CONTRACT_ID, NORTH_RIDGE_WIND_FARM_ID, 2),
        *(
            (demo_id(f"{key}/contract"), demo_id(f"{key}/farm"), count)
            for key, *_, count in EXTRA_SITES
        ),
    )
    for contract_id, farm_id, count in portfolios:
        turbine_ids = _turbine_ids(db, farm_id, limit=3)
        alarm_ids = [
            str(demo_id(f"{category['id']}/{alarms[0][0]}"))
            for category in SYNTHETIC_ALARM_CATEGORIES
            if category["contract_id"] == contract_id
            for code, _, required, alarms in ALARM_CATALOG
            if category["code"] == code and required
        ]
        for i in range(count):
            configuration_id = demo_id(f"{contract_id}/configuration/{i}")
            version_id = demo_id(f"{configuration_id}/version/1")
            if db.get(AvailabilityConfiguration, configuration_id) is not None:
                continue
            # A downgrade and re-upgrade can leave this version under the default config.
            if db.get(ConfigurationVersion, version_id) is not None:
                continue
            published = i == 0 and contract_id != NORTH_RIDGE_CONTRACT_ID
            name = "Annual baseline" if published else f"Availability scenario {i + 1}"
            calc_type = ("TBA", "YBA", "RBA")[i % 3]
            created_at = datetime(2026, 11, 1, 9, tzinfo=timezone.utc) + timedelta(days=i)
            updated_at = created_at + timedelta(hours=4)
            actor = ("Avery Demo", "Rowan Demo", "Sage Demo")[i % 3]
            snapshot = {
                "schema_version": 2,
                "basic_details": {
                    "name": name,
                    "calculation_type": calc_type,
                    "start_date": "2027-01-01",
                    "end_date": "2027-12-31",
                },
                "turbine_ids": turbine_ids,
                "formula_code": f"{calc_type}_STD",
                "alarm_assignments": [
                    {"alarm_id": alarm_id, "turbine_ids": turbine_ids} for alarm_id in alarm_ids
                ],
                "details": {
                    "park_availability_pct": 96.0 + i / 4,
                    "low_wind_variant": "LW_EXCLUDE_BELOW_CUT_IN",
                    "high_wind_variant": "HW_EXCLUDE_ABOVE_CUT_OUT",
                },
            }
            db.add(
                AvailabilityConfiguration(
                    id=configuration_id,
                    contract_id=contract_id,
                    name=name,
                    created_at=created_at,
                    updated_at=updated_at,
                    created_by=actor,
                    updated_by=actor,
                    versions=[
                        ConfigurationVersion(
                            id=version_id,
                            version_number=1,
                            status=ConfigurationStatus.PUBLISHED if published else ConfigurationStatus.DRAFT,
                            snapshot_data=snapshot,
                            checksum=ConfigurationVersion.calculate_checksum(snapshot),
                            published_at=updated_at if published else None,
                            created_at=created_at,
                            updated_at=updated_at,
                            created_by=actor,
                        )
                    ],
                )
            )


def _seed_rows(db: Session, model: type[object], rows: tuple[dict, ...]) -> None:
    for row in rows:
        if db.get(model, row["id"]) is None:
            db.add(model(**row))
    db.flush()


def seed_database(db: Session) -> None:
    """Insert stable synthetic records once, preserving existing local edits."""
    # Do not expand an A1 demo fleet on upgrade: existing drafts still refer to it.
    existing_original_farms = {
        farm_id
        for farm_id in (NORTH_RIDGE_WIND_FARM_ID, COASTAL_PLAINS_WIND_FARM_ID)
        if db.get(WindFarm, farm_id) is not None
    }
    _seed_rows(db, Contract, SYNTHETIC_CONTRACTS)
    _seed_rows(db, WindFarm, SYNTHETIC_WIND_FARMS)
    _seed_rows(
        db, TurbineGroup,
        tuple(row for row in SYNTHETIC_TURBINE_GROUPS if row["wind_farm_id"] not in existing_original_farms),
    )
    _seed_rows(
        db, Turbine,
        tuple(row for row in SYNTHETIC_TURBINES if row["wind_farm_id"] not in existing_original_farms),
    )
    _seed_rows(db, ProductionPeriod, SYNTHETIC_PRODUCTION_PERIODS)
    _seed_rows(db, AlarmCategory, SYNTHETIC_ALARM_CATEGORIES)
    _seed_rows(db, Alarm, SYNTHETIC_ALARMS)
    _seed_legacy_configuration(db)
    _seed_availability_configurations(db)
    db.commit()


def main() -> None:
    with SessionLocal() as db:
        seed_database(db)


if __name__ == "__main__":
    main()
