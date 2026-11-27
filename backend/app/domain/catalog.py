from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CalculationTypeItem:
    code: str
    name: str
    description: str


@dataclass(frozen=True)
class FormulaItem:
    code: str
    calculation_type: str
    name: str
    expression: str


@dataclass(frozen=True)
class WindVariantItem:
    code: str
    name: str
    description: str


CALCULATION_TYPES: tuple[CalculationTypeItem, ...] = (
    CalculationTypeItem(
        code="TBA",
        name="Time-Based Availability",
        description="Measures the fraction of contractual period hours turbines are available to operate.",
    ),
    CalculationTypeItem(
        code="YBA",
        name="Yield-Based Availability",
        description="Measures actual energy yield relative to potential energy yield.",
    ),
    CalculationTypeItem(
        code="RBA",
        name="Revenue-Based Availability",
        description="Measures actual revenue relative to potential revenue across tariff periods.",
    ),
)

FORMULAS: tuple[FormulaItem, ...] = (
    FormulaItem(
        code="TBA_STD",
        calculation_type="TBA",
        name="Standard Time-Based Availability",
        expression="Available hours / Period hours",
    ),
    FormulaItem(
        code="TBA_EXCL",
        calculation_type="TBA",
        name="Exclusion-Adjusted Time Availability",
        expression="(Period - Excluded - Unavailable) / (Period - Excluded)",
    ),
    FormulaItem(
        code="YBA_STD",
        calculation_type="YBA",
        name="Standard Yield-Based Availability",
        expression="Actual yield / Potential yield",
    ),
    FormulaItem(
        code="YBA_LOSS",
        calculation_type="YBA",
        name="Loss-Deducted Yield Availability",
        expression="1 - Lost yield / Potential yield",
    ),
    FormulaItem(
        code="RBA_STD",
        calculation_type="RBA",
        name="Standard Revenue-Based Availability",
        expression="Actual revenue / Potential revenue",
    ),
    FormulaItem(
        code="RBA_LOSS",
        calculation_type="RBA",
        name="Loss-Deducted Revenue Availability",
        expression="1 - Lost revenue / Potential revenue",
    ),
)

LOW_WIND_VARIANTS: tuple[WindVariantItem, ...] = (
    WindVariantItem(
        code="LW_EXCLUDE_BELOW_CUT_IN",
        name="Exclude below cut-in",
        description="Periods below turbine cut-in wind speed are excluded from availability penalties.",
    ),
    WindVariantItem(
        code="LW_COUNT_AS_AVAILABLE",
        name="Count as available",
        description="Low-wind idle periods are counted as fully available.",
    ),
    WindVariantItem(
        code="LW_PRO_RATA_POWER_CURVE",
        name="Pro-rata power curve",
        description="Weight low-wind intervals using the warranted power curve.",
    ),
)

HIGH_WIND_VARIANTS: tuple[WindVariantItem, ...] = (
    WindVariantItem(
        code="HW_EXCLUDE_ABOVE_CUT_OUT",
        name="Exclude above cut-out",
        description="High-wind shutdowns above cut-out wind speed are excluded from downtime.",
    ),
    WindVariantItem(
        code="HW_COUNT_AS_UNAVAILABLE",
        name="Count as unavailable",
        description="High-wind shutdowns are treated as unavailable unless exempted.",
    ),
    WindVariantItem(
        code="HW_STORM_GRACE_WINDOW",
        name="Storm grace window",
        description="Apply a contractual storm hysteresis grace window around cut-out.",
    ),
)

ACTING_USERS: tuple[str, ...] = (
    "Avery Demo",
    "Rowan Demo",
    "Sage Demo",
    "Demo User",
)

CALCULATION_TYPE_CODES: frozenset[str] = frozenset(item.code for item in CALCULATION_TYPES)
FORMULA_BY_CODE: dict[str, FormulaItem] = {item.code: item for item in FORMULAS}
LOW_WIND_CODES: frozenset[str] = frozenset(item.code for item in LOW_WIND_VARIANTS)
HIGH_WIND_CODES: frozenset[str] = frozenset(item.code for item in HIGH_WIND_VARIANTS)
