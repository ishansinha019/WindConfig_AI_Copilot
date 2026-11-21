const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type HealthResponse = {
  status: string;
  service: string;
};

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${apiBaseUrl}/api/v1/health`);

  if (!response.ok) {
    throw new Error("Backend health check failed");
  }

  return response.json() as Promise<HealthResponse>;
}
