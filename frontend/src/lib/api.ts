import { getActingUser } from "./actingUser";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "";

export type HealthResponse = {
  status: string;
  service: string;
};

export type ContractStatus = "draft" | "needs_review" | "published";
export type ConfigurationStatus = "draft" | "in_review" | "published" | "archived";

export type AvailabilityConfigSummary = {
  id: string;
  contract_id: string;
  name: string;
  status: "draft" | "published";
  has_unpublished_draft: boolean;
  calculation_type: string | null;
  start_date: string | null;
  end_date: string | null;
  latest_version_number: number;
  created_by: string;
  updated_by: string;
  created_at: string;
  updated_at: string;
};

export type ContractSummary = {
  id: string;
  name: string;
  customer_name: string;
  customer_names: string[];
  order_reason: string;
  sales_document_number: string;
  wind_farm_name: string;
  region: string;
  status: ContractStatus;
  start_date: string;
  end_date: string;
  target_availability: number;
  is_live: boolean;
  turbine_count: number;
  availability_configurations: AvailabilityConfigSummary[];
};

export type Turbine = {
  id: string;
  code: string;
  model_name: string;
  rated_power_mw: number;
  turbine_group: { id: string; name: string } | null;
};

export type Alarm = {
  id: string;
  code: string;
  name: string;
  description: string | null;
};

export type ContractDetail = ContractSummary & {
  wind_farms: Array<{
    id: string;
    name: string;
    region: string;
    turbines: Turbine[];
  }>;
  production_periods: Array<{
    id: string;
    name: string;
    start_date: string;
    end_date: string;
  }>;
  alarm_categories: Array<{
    id: string;
    code: string;
    name: string;
    is_required: boolean;
    alarms: Alarm[];
  }>;
};

export type AvConfigVersion = {
  id: string;
  availability_configuration_id: string;
  version_number: number;
  status: ConfigurationStatus;
  snapshot_data: Record<string, unknown>;
  checksum: string;
  created_by: string;
  published_at: string | null;
  created_at: string;
  updated_at: string;
};

export type AvailabilityConfigDetail = AvailabilityConfigSummary & {
  latest_version: AvConfigVersion;
  published_version: AvConfigVersion | null;
};

export type ReadinessIssue = {
  step: number;
  field: string;
  message: string;
};

export type AvReadinessResponse = {
  is_valid: boolean;
  blocking_errors: ReadinessIssue[];
  warnings: ReadinessIssue[];
};

export type AvDiffResponse = {
  v_from_number: number;
  v_to_number: number;
  basic_details_changes: Record<string, { from: unknown; to: unknown }>;
  added_turbines: string[];
  removed_turbines: string[];
  formula_change: { from: string | null; to: string | null } | null;
  added_alarms: string[];
  removed_alarms: string[];
  alarm_assignment_changes: Array<{ alarm_id: string; from: string[]; to: string[] }>;
  details_changes: Record<string, { from: unknown; to: unknown }>;
};

export type AlarmAssignment = {
  alarm_id: string;
  turbine_ids: string[];
};

export type AvailabilitySnapshotDraft = {
  schema_version: 2;
  basic_details: {
    name: string;
    calculation_type: string | null;
    start_date: string | null;
    end_date: string | null;
  };
  turbine_ids: string[];
  formula_code: string | null;
  alarm_assignments: AlarmAssignment[];
  details: {
    park_availability_pct: number | null;
    low_wind_variant: string | null;
    high_wind_variant: string | null;
  };
};

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export type CatalogResponse = {
  calculation_types: Array<{ code: string; name: string; description: string }>;
  formulas: Array<{ code: string; calculation_type: string; name: string; expression: string }>;
  low_wind_variants: Array<{ code: string; name: string; description: string }>;
  high_wind_variants: Array<{ code: string; name: string; description: string }>;
};

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${apiBaseUrl}/api/v1/health`);
  if (!response.ok) {
    throw new Error("Backend health check failed");
  }
  return response.json() as Promise<HealthResponse>;
}

export async function getUsers(): Promise<string[]> {
  const response = await fetch(`${apiBaseUrl}/api/v1/users`);
  if (!response.ok) {
    throw new Error("Could not load acting users");
  }
  const data = (await response.json()) as { users: string[] };
  return data.users;
}

export async function getCatalog(): Promise<CatalogResponse> {
  const response = await fetch(`${apiBaseUrl}/api/v1/catalog`);
  if (!response.ok) {
    throw new Error("Could not load catalog");
  }
  return response.json() as Promise<CatalogResponse>;
}

export async function getContracts(): Promise<ContractSummary[]> {
  const response = await fetch(`${apiBaseUrl}/api/v1/contracts`);
  if (!response.ok) {
    throw new Error("Could not load contracts");
  }
  const data = (await response.json()) as { contracts: ContractSummary[] };
  return data.contracts;
}

export async function getContract(contractId: string): Promise<ContractDetail> {
  const response = await fetch(`${apiBaseUrl}/api/v1/contracts/${contractId}`);
  if (!response.ok) {
    throw new Error("Could not load contract details");
  }
  return response.json() as Promise<ContractDetail>;
}

export async function getAvailabilityConfiguration(
  contractId: string,
  configId: string,
): Promise<AvailabilityConfigDetail> {
  const response = await fetch(
    `${apiBaseUrl}/api/v1/contracts/${contractId}/availability-configurations/${configId}`,
  );
  if (!response.ok) {
    throw new Error("Could not load availability configuration");
  }
  return response.json() as Promise<AvailabilityConfigDetail>;
}

export async function getAvailabilityReadiness(
  contractId: string,
  configId: string,
  versionId: string,
): Promise<AvReadinessResponse> {
  const response = await fetch(
    `${apiBaseUrl}/api/v1/contracts/${contractId}/availability-configurations/${configId}/versions/${versionId}/readiness`,
  );
  if (!response.ok) {
    throw new Error("Could not check configuration readiness");
  }
  return response.json() as Promise<AvReadinessResponse>;
}

export async function publishAvailabilityVersion(
  contractId: string,
  configId: string,
  versionId: string,
): Promise<AvConfigVersion> {
  const response = await fetch(
    `${apiBaseUrl}/api/v1/contracts/${contractId}/availability-configurations/${configId}/versions/${versionId}/publish`,
    {
      method: "POST",
      headers: {
        "X-User-Name": getActingUser(),
      },
    },
  );
  if (!response.ok) {
    const errorBody = (await response.json().catch(() => ({}))) as { detail?: string };
    throw new Error(errorBody.detail ?? "Failed to publish configuration");
  }
  return response.json() as Promise<AvConfigVersion>;
}

export async function deleteAvailabilityConfiguration(
  contractId: string,
  configId: string,
): Promise<void> {
  const response = await fetch(
    `${apiBaseUrl}/api/v1/contracts/${contractId}/availability-configurations/${configId}`,
    {
      method: "DELETE",
      headers: {
        "X-User-Name": getActingUser(),
      },
    },
  );
  if (!response.ok) {
    const errorBody = (await response.json().catch(() => ({}))) as { detail?: string };
    throw new ApiError(response.status, errorBody.detail ?? "Failed to delete availability configuration");
  }
}

export async function createAvailabilityConfiguration(
  contractId: string,
  snapshotData: AvailabilitySnapshotDraft,
): Promise<AvailabilityConfigDetail> {
  const response = await fetch(
    `${apiBaseUrl}/api/v1/contracts/${contractId}/availability-configurations`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-User-Name": getActingUser(),
      },
      body: JSON.stringify({ snapshot_data: snapshotData }),
    },
  );
  if (!response.ok) {
    const errorBody = (await response.json().catch(() => ({}))) as { detail?: string };
    throw new ApiError(
      response.status,
      typeof errorBody.detail === "string"
        ? errorBody.detail
        : "Failed to create availability configuration",
    );
  }
  return response.json() as Promise<AvailabilityConfigDetail>;
}

export async function saveAvailabilityDraft(
  contractId: string,
  configId: string,
  baseVersion: number | null,
  snapshotData: AvailabilitySnapshotDraft,
): Promise<AvConfigVersion> {
  const response = await fetch(
    `${apiBaseUrl}/api/v1/contracts/${contractId}/availability-configurations/${configId}/drafts`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-User-Name": getActingUser(),
      },
      body: JSON.stringify({ base_version: baseVersion, snapshot_data: snapshotData }),
    },
  );
  if (!response.ok) {
    const errorBody = (await response.json().catch(() => ({}))) as { detail?: string };
    throw new ApiError(
      response.status,
      typeof errorBody.detail === "string" ? errorBody.detail : "Failed to save draft",
    );
  }
  return response.json() as Promise<AvConfigVersion>;
}

export async function getAvailabilityVersions(
  contractId: string,
  configId: string,
): Promise<AvConfigVersion[]> {
  const response = await fetch(
    `${apiBaseUrl}/api/v1/contracts/${contractId}/availability-configurations/${configId}/versions`,
  );
  if (!response.ok) {
    throw new Error("Could not load version history");
  }
  return response.json() as Promise<AvConfigVersion[]>;
}

export async function getAvailabilityDiff(
  contractId: string,
  configId: string,
  vFromId: string,
  vToId: string,
): Promise<AvDiffResponse> {
  const response = await fetch(
    `${apiBaseUrl}/api/v1/contracts/${contractId}/availability-configurations/${configId}/diff?v_from=${encodeURIComponent(vFromId)}&v_to=${encodeURIComponent(vToId)}`,
  );
  if (!response.ok) {
    throw new Error("Could not compute version diff");
  }
  return response.json() as Promise<AvDiffResponse>;
}
