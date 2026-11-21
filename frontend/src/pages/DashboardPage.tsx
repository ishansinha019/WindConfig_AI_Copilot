import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Factory, Layers3, Wind } from "lucide-react";

import { getContract, getContracts, type ContractStatus } from "../lib/api";

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

export function DashboardPage() {
  const [selectedContractId, setSelectedContractId] = useState<string>();
  const contractsQuery = useQuery({ queryKey: ["contracts"], queryFn: getContracts });
  const activeContractId = selectedContractId ?? contractsQuery.data?.[0]?.id;
  const detailQuery = useQuery({
    queryKey: ["contract", activeContractId],
    queryFn: () => getContract(activeContractId ?? ""),
    enabled: Boolean(activeContractId),
  });

  if (contractsQuery.isLoading) {
    return <DashboardMessage message="Loading the synthetic contract portfolio..." />;
  }

  if (contractsQuery.isError) {
    return <DashboardMessage message="The contract API is unavailable. Start the backend and refresh." />;
  }

  return (
    <section className="space-y-6">
      <div className="rounded-lg border border-border bg-white p-6">
        <p className="text-sm font-semibold text-primary">Synthetic operations portfolio</p>
        <h2 className="mt-2 text-xl font-semibold text-slate-950">Contract configuration overview</h2>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
          Select a contract to inspect its seeded wind farm, turbine sections, production periods,
          and availability alarm categories.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {contractsQuery.data?.map((contract) => (
          <button
            key={contract.id}
            type="button"
            onClick={() => setSelectedContractId(contract.id)}
            className={`rounded-lg border bg-white p-5 text-left transition hover:border-primary ${
              activeContractId === contract.id ? "border-primary ring-1 ring-primary" : "border-border"
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="font-semibold text-slate-950">{contract.name}</h3>
                <p className="mt-1 text-sm text-slate-600">{contract.customer_name}</p>
              </div>
              <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${statusClasses[contract.status]}`}>
                {statusLabels[contract.status]}
              </span>
            </div>
            <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
              <Metric label="Wind farm" value={contract.wind_farm_name} />
              <Metric label="Target" value={`${contract.target_availability}%`} />
            </div>
          </button>
        ))}
      </div>

      {detailQuery.isLoading && <DashboardMessage message="Loading contract configuration..." />}
      {detailQuery.isError && <DashboardMessage message="Could not load the selected contract details." />}

      {detailQuery.data && (
        <div className="grid gap-4 lg:grid-cols-2">
          <article className="rounded-lg border border-border bg-white p-5">
            <SectionTitle icon={Factory} title="Wind farm and turbines" />
            {detailQuery.data.wind_farms.map((windFarm) => (
              <div key={windFarm.id} className="mt-4">
                <p className="font-semibold text-slate-950">{windFarm.name}</p>
                <p className="text-sm text-slate-600">{windFarm.region}</p>
                <div className="mt-3 grid gap-2 sm:grid-cols-2">
                  {windFarm.turbines.map((turbine) => (
                    <div key={turbine.id} className="rounded-md bg-slate-50 px-3 py-2 text-sm">
                      <div className="font-semibold text-slate-900">{turbine.code}</div>
                      <div className="text-slate-600">
                        {turbine.model_name} - {turbine.rated_power_mw} MW
                      </div>
                      <div className="mt-1 text-xs text-primary">
                        {turbine.turbine_group?.name ?? "Ungrouped"}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </article>

          <div className="space-y-4">
            <article className="rounded-lg border border-border bg-white p-5">
              <SectionTitle icon={Layers3} title="Production periods" />
              <div className="mt-4 space-y-3">
                {detailQuery.data.production_periods.map((period) => (
                  <div key={period.id} className="flex justify-between gap-3 text-sm">
                    <span className="font-medium text-slate-900">{period.name}</span>
                    <span className="text-right text-slate-600">
                      {period.start_date} to {period.end_date}
                    </span>
                  </div>
                ))}
              </div>
            </article>

            <article className="rounded-lg border border-border bg-white p-5">
              <SectionTitle icon={AlertTriangle} title="Alarm categories" />
              <div className="mt-4 space-y-3">
                {detailQuery.data.alarm_categories.map((alarm) => (
                  <div key={alarm.id} className="flex items-center justify-between gap-3 text-sm">
                    <span className="text-slate-900">
                      <span className="font-semibold">{alarm.code}</span> - {alarm.name}
                    </span>
                    <span className={alarm.is_required ? "text-rose-700" : "text-slate-500"}>
                      {alarm.is_required ? "Required" : "Optional"}
                    </span>
                  </div>
                ))}
              </div>
            </article>
          </div>
        </div>
      )}
    </section>
  );
}

function DashboardMessage({ message }: { message: string }) {
  return <div className="rounded-lg border border-border bg-white p-6 text-sm text-slate-600">{message}</div>;
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 truncate font-medium text-slate-900">{value}</div>
    </div>
  );
}

function SectionTitle({ icon: Icon, title }: { icon: typeof Wind; title: string }) {
  return (
    <h3 className="flex items-center gap-2 font-semibold text-slate-950">
      <Icon className="h-5 w-5 text-primary" aria-hidden="true" />
      {title}
    </h3>
  );
}
