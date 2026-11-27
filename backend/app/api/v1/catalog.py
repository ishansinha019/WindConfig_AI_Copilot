from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter

from app.domain.catalog import (
    ACTING_USERS,
    CALCULATION_TYPES,
    FORMULAS,
    HIGH_WIND_VARIANTS,
    LOW_WIND_VARIANTS,
)
from app.schemas.catalog import (
    CalculationTypeSchema,
    CatalogResponse,
    FormulaSchema,
    UsersResponse,
    WindVariantSchema,
)

router = APIRouter(tags=["catalog"])


@router.get("/catalog", response_model=CatalogResponse)
def get_catalog_endpoint() -> CatalogResponse:
    return CatalogResponse(
        calculation_types=[CalculationTypeSchema(**asdict(item)) for item in CALCULATION_TYPES],
        formulas=[FormulaSchema(**asdict(item)) for item in FORMULAS],
        low_wind_variants=[WindVariantSchema(**asdict(item)) for item in LOW_WIND_VARIANTS],
        high_wind_variants=[WindVariantSchema(**asdict(item)) for item in HIGH_WIND_VARIANTS],
    )


@router.get("/users", response_model=UsersResponse)
def get_users_endpoint() -> UsersResponse:
    return UsersResponse(users=list(ACTING_USERS))
