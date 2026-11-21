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
