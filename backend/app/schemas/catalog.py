from pydantic import BaseModel


class CalculationTypeSchema(BaseModel):
    code: str
    name: str
    description: str


class FormulaSchema(BaseModel):
    code: str
    calculation_type: str
    name: str
    expression: str


class WindVariantSchema(BaseModel):
    code: str
    name: str
    description: str


class CatalogResponse(BaseModel):
    calculation_types: list[CalculationTypeSchema]
    formulas: list[FormulaSchema]
    low_wind_variants: list[WindVariantSchema]
    high_wind_variants: list[WindVariantSchema]


class UsersResponse(BaseModel):
    users: list[str]
