import { useQuery } from "@tanstack/react-query";
import { ArrowUpRight, CalendarDays, Factory } from "lucide-react";
import { Link } from "react-router-dom";

import { getContracts, type ContractStatus } from "../lib/api";

const statusLabels: Record<ContractStatus, string> = {
  draft: "Draft",
  needs_review: "Needs review",
  published: "Published",
};

const statusClasses: Record<ContractStatus, string> = {
  draft: "bg-amber-50 text-amber-800",
  needs_review: "bg-rose-50 text-rose-800",
  published: "bg-emerald-50 text-emerald-800",
};

export function HomePage() {
  const contractsQuery = useQuery({ queryKey: ["contracts"], queryFn: getContracts });

  if (contractsQuery.isLoading) {
    return <PageMessage message="Loading the synthetic contract portfolio..." />;
  }

  if (contractsQuery.isError) {
    return <PageMessage message="The contract API is unavailable. Start the backend and refresh." />;
  }

  const contracts = contractsQuery.data ?? [];

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm font-semibold text-primary">Synthetic operations portfolio</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-foreground">Contracts</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
          Select a contract to inspect its wind farm assets and availability configuration.
        </p>
      </div>

      {contracts.length === 0 ? (
        <PageMessage message="No contracts are available yet." />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {contracts.map((contract) => (
            <Link
              key={contract.id}
              to={`/contracts/${contract.id}`}
              className="group rounded-lg border border-border bg-card p-5 transition hover:border-primary hover:shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="font-semibold text-card-foreground">{contract.name}</h2>
                  <p className="mt-1 text-sm text-muted-foreground">{contract.customer_name}</p>
                </div>
                <span
                  className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-semibold ${statusClasses[contract.status]}`}
                >
                  {statusLabels[contract.status]}
                </span>
              </div>

              <div className="mt-5 space-y-3 text-sm">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Factory className="h-4 w-4 shrink-0" aria-hidden="true" />
                  <span className="truncate">{contract.wind_farm_name}</span>
                </div>
                <div className="flex items-center gap-2 text-muted-foreground">
                  <CalendarDays className="h-4 w-4 shrink-0" aria-hidden="true" />
                  <span>
                    {contract.start_date} to {contract.end_date}
                  </span>
                </div>
              </div>

              <div className="mt-5 flex items-center justify-between border-t border-border pt-4 text-sm">
                <span className="text-muted-foreground">
                  Target availability{" "}
                  <span className="font-semibold text-foreground">{contract.target_availability}%</span>
                </span>
                <ArrowUpRight
                  className="h-4 w-4 text-muted-foreground transition group-hover:text-primary"
                  aria-hidden="true"
                />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

function PageMessage({ message }: { message: string }) {
  return <div className="rounded-lg border border-border bg-card p-6 text-sm text-muted-foreground">{message}</div>;
}
