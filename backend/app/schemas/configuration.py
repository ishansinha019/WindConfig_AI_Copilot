from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.configuration import ConfigurationStatus


class SaveDraftRequest(BaseModel):
    base_version: int | None = Field(default=None, description="Expected latest version for optimistic concurrency check")
    snapshot_data: dict[str, Any] = Field(..., description="Complete serialized configuration state")


class TransitionRequest(BaseModel):
    target_status: ConfigurationStatus


class ConfigurationVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    contract_id: UUID
    version_number: int
    status: ConfigurationStatus
    snapshot_data: dict[str, Any]
    checksum: str
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ActiveConfigurationResponse(BaseModel):
    contract_id: UUID
    current_version: ConfigurationVersionResponse | None = None
    versions: list[ConfigurationVersionResponse] = []


class ValidationReadinessResponse(BaseModel):
    is_valid: bool
    blocking_errors: list[str] = []
    warnings: list[str] = []


class DiffResponse(BaseModel):
    v_from_number: int
    v_to_number: int
    added_alarms: list[str] = []
    removed_alarms: list[str] = []
    added_turbines: list[str] = []
    removed_turbines: list[str] = []
    variable_changes: dict[str, dict[str, Any]] = {}
