from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.configuration import ConfigurationStatus


class BasicDetailsDraft(BaseModel):
    name: str = Field(..., min_length=1, max_length=160)
    calculation_type: str | None = None
    start_date: date | None = None
    end_date: date | None = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Availability configuration name must not be blank.")
        return stripped


class AlarmAssignment(BaseModel):
    alarm_id: UUID
    turbine_ids: list[UUID] = Field(default_factory=list)


class DetailsDraft(BaseModel):
    park_availability_pct: float | None = None
    low_wind_variant: str | None = None
    high_wind_variant: str | None = None


class AvailabilitySnapshotDraft(BaseModel):
    schema_version: Literal[2] = 2
    basic_details: BasicDetailsDraft
    turbine_ids: list[UUID] = Field(default_factory=list)
    formula_code: str | None = None
    alarm_assignments: list[AlarmAssignment] = Field(default_factory=list)
    details: DetailsDraft = Field(default_factory=DetailsDraft)


class CreateAvailabilityConfigRequest(BaseModel):
    snapshot_data: AvailabilitySnapshotDraft


class SaveAvDraftRequest(BaseModel):
    base_version: int | None = Field(
        default=None,
        description="Expected latest version number for optimistic concurrency control",
    )
    snapshot_data: AvailabilitySnapshotDraft


class AvConfigVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    availability_configuration_id: UUID
    version_number: int
    status: ConfigurationStatus
    snapshot_data: dict[str, Any]
    checksum: str
    created_by: str
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class AvailabilityConfigSummary(BaseModel):
    id: UUID
    contract_id: UUID
    name: str
    status: Literal["draft", "published"]
    has_unpublished_draft: bool
    calculation_type: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    latest_version_number: int
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime


class AvailabilityConfigListResponse(BaseModel):
    availability_configurations: list[AvailabilityConfigSummary]


class AvailabilityConfigDetail(AvailabilityConfigSummary):
    latest_version: AvConfigVersionResponse
    published_version: AvConfigVersionResponse | None = None


class ReadinessIssue(BaseModel):
    step: int = Field(ge=1, le=4)
    field: str
    message: str


class AvValidationReadinessResponse(BaseModel):
    is_valid: bool
    blocking_errors: list[ReadinessIssue] = Field(default_factory=list)
    warnings: list[ReadinessIssue] = Field(default_factory=list)


class AvDiffResponse(BaseModel):
    v_from_number: int
    v_to_number: int
    basic_details_changes: dict[str, dict[str, Any]] = Field(default_factory=dict)
    added_turbines: list[str] = Field(default_factory=list)
    removed_turbines: list[str] = Field(default_factory=list)
    formula_change: dict[str, Any] | None = None
    added_alarms: list[str] = Field(default_factory=list)
    removed_alarms: list[str] = Field(default_factory=list)
    alarm_assignment_changes: list[dict[str, Any]] = Field(default_factory=list)
    details_changes: dict[str, dict[str, Any]] = Field(default_factory=dict)
