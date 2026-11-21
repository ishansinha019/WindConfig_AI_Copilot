const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type HealthResponse = {
  status: string;
  service: string;
};

export type ContractStatus = "draft" | "needs_review" | "published";

export type ContractSummary = {
  id: string;
  name: string;
  customer_name: string;
  wind_farm_name: string;
  region: string;
  status: ContractStatus;
  start_date: string;
  end_date: string;
  target_availability: number;
};

export type Turbine = {
  id: string;
  code: string;
  model_name: string;
  rated_power_mw: number;
  turbine_group: { id: string; name: string } | null;
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
  }>;
};

export type ConfigurationStatus = "draft" | "in_review" | "published" | "archived";

export type ConfigurationVersion = {
  id: string;
  contract_id: string;
  version_number: number;
  status: ConfigurationStatus;
  snapshot_data: {
    formula_type?: string;
    formula_name?: string;
    target_availability?: number;
    included_alarm_codes?: string[];
    turbine_ids?: string[];
    production_period_ids?: string[];
    variables?: Record<string, number | string>;
  };
  checksum: string;
  published_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ActiveConfigurationResponse = {
  contract_id: string;
  current_version: ConfigurationVersion | null;
  versions: ConfigurationVersion[];
};

export type ValidationReadinessResponse = {
  is_valid: boolean;
  blocking_errors: string[];
  warnings: string[];
};

export type DiffResponse = {
  v_from_number: number;
  v_to_number: number;
  added_alarms: string[];
  removed_alarms: string[];
  added_turbines: string[];
  removed_turbines: string[];
  variable_changes: Record<string, { from: unknown; to: unknown }>;
};

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${apiBaseUrl}/api/v1/health`);
  if (!response.ok) {
    throw new Error("Backend health check failed");
  }
  return response.json() as Promise<HealthResponse>;
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

export async function getActiveConfiguration(contractId: string): Promise<ActiveConfigurationResponse> {
  const response = await fetch(`${apiBaseUrl}/api/v1/contracts/${contractId}/configuration`);
  if (!response.ok) {
    throw new Error("Could not load active configuration");
  }
  return response.json() as Promise<ActiveConfigurationResponse>;
}

export async function getConfigurationReadiness(
  contractId: string,
  versionId: string,
): Promise<ValidationReadinessResponse> {
  const response = await fetch(`${apiBaseUrl}/api/v1/contracts/${contractId}/configuration/versions/${versionId}/readiness`);
  if (!response.ok) {
    throw new Error("Could not check configuration readiness");
  }
  return response.json() as Promise<ValidationReadinessResponse>;
}

export async function publishConfiguration(
  contractId: string,
  versionId: string,
): Promise<ConfigurationVersion> {
  const response = await fetch(`${apiBaseUrl}/api/v1/contracts/${contractId}/configuration/versions/${versionId}/publish`, {
    method: "POST",
  });
  if (!response.ok) {
    const errorBody = (await response.json().catch(() => ({}))) as { detail?: string };
    throw new Error(errorBody.detail ?? "Failed to publish configuration");
  }
  return response.json() as Promise<ConfigurationVersion>;
}

export async function saveDraftConfiguration(
  contractId: string,
  baseVersion: number | null,
  snapshotData: Record<string, unknown>,
): Promise<ConfigurationVersion> {
  const response = await fetch(`${apiBaseUrl}/api/v1/contracts/${contractId}/configuration/drafts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ base_version: baseVersion, snapshot_data: snapshotData }),
  });
  if (!response.ok) {
    const errorBody = (await response.json().catch(() => ({}))) as { detail?: string };
    throw new Error(errorBody.detail ?? "Failed to save draft");
  }
  return response.json() as Promise<ConfigurationVersion>;
}
