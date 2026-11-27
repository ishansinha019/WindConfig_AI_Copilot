from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.contract import ContractStatus
from app.schemas.availability_configuration import AvailabilityConfigSummary


class ContractSummary(BaseModel):
    id: UUID
    name: str
    customer_name: str
    customer_names: list[str]
    order_reason: str
    sales_document_number: str
    wind_farm_name: str
    region: str
    status: ContractStatus
    start_date: date
    end_date: date
    target_availability: float = Field(ge=0, le=100)
    is_live: bool = False
    turbine_count: int = 0
    availability_configurations: list[AvailabilityConfigSummary] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ContractListResponse(BaseModel):
    contracts: list[ContractSummary]


class TurbineGroupSummary(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class TurbineSummary(BaseModel):
    id: UUID
    code: str
    model_name: str
    rated_power_mw: float = Field(gt=0)
    turbine_group: TurbineGroupSummary | None

    model_config = ConfigDict(from_attributes=True)


class WindFarmDetail(BaseModel):
    id: UUID
    name: str
    region: str
    turbines: list[TurbineSummary]

    model_config = ConfigDict(from_attributes=True)


class ProductionPeriodSummary(BaseModel):
    id: UUID
    name: str
    start_date: date
    end_date: date

    model_config = ConfigDict(from_attributes=True)


class AlarmSummary(BaseModel):
    id: UUID
    code: str
    name: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class AlarmCategorySummary(BaseModel):
    id: UUID
    code: str
    name: str
    is_required: bool
    alarms: list[AlarmSummary]

    model_config = ConfigDict(from_attributes=True)


class ContractDetail(ContractSummary):
    wind_farms: list[WindFarmDetail]
    production_periods: list[ProductionPeriodSummary]
    alarm_categories: list[AlarmCategorySummary]

