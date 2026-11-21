import { useQuery } from "@tanstack/react-query";
import { Server } from "lucide-react";

import { getHealth } from "../lib/api";

export function HealthStatus() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    retry: 1,
  });

  const label = isLoading
    ? "Checking API"
    : isError
      ? "API offline"
      : data
        ? `${data.status.toUpperCase()} - ${data.service}`
        : "API status unavailable";

  return (
    <div className="flex min-w-72 items-center gap-3 rounded-lg border border-border bg-slate-50 px-4 py-3">
      <div className="flex h-10 w-10 items-center justify-center rounded-md bg-white text-primary shadow-sm">
        <Server className="h-5 w-5" aria-hidden="true" />
      </div>
      <div>
        <div className="text-xs font-semibold uppercase tracking-normal text-slate-500">
          Backend health
        </div>
        <div className="mt-1 text-sm font-semibold text-slate-950">{label}</div>
      </div>
    </div>
  );
}
