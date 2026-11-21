from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.contract import ContractStatus


class ContractSummary(BaseModel):
    id: UUID
    name: str
    customer_name: str
    wind_farm_name: str
    region: str
    status: ContractStatus
    start_date: date
    end_date: date
    target_availability: float = Field(ge=0, le=100)

    model_config = ConfigDict(from_attributes=True)


class ContractListResponse(BaseModel):
    contracts: list[ContractSummary]


class ContractDetail(ContractSummary):
    """The current contract representation used by the detail endpoint.

    This deliberately extends the list summary so new configuration fields can
    be added later without changing the contract-list response.
    """

