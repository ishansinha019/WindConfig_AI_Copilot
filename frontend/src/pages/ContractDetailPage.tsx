import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  Factory,
  Layers3,
  Plus,
  Sliders,
  Wind,
} from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { getContract } from "../lib/api";

export function ContractDetailPage() {
  const { contractId } = useParams<{ contractId: string }>();

  const detailQuery = useQuery({
    queryKey: ["contract", contractId],
    queryFn: () => getContract(contractId ?? ""),
    enabled: Boolean(contractId),
  });

  if (!contractId || detailQuery.isLoading) {
    return <DashboardMessage message="Loading contract details..." />;
  }

  if (detailQuery.isError || !detailQuery.data) {
    return <DashboardMessage message="Could not load the selected contract details." />;
  }

  const contract = detailQuery.data;

  return (
    <section className="space-y-6">
      <div className="space-y-2">
        <Link to="/" className="text-sm font-medium text-primary hover:underline">
          ← All contracts
        </Link>
        <div>
          <p className="text-sm font-semibold text-primary">Contract overview</p>
          <h1 className="mt-1 text-2xl font-semibold text-foreground">{contract.name}</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {contract.customer_names.join(" | ")} · {contract.wind_farm_name} ({contract.turbine_count} turbines)
          </p>
        </div>
      </div>

      <div className="space-y-6">
        <article className="rounded-lg border border-border bg-white p-5 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-4">
            <div>
              <SectionTitle icon={Sliders} title="Availability Configurations" />
              <p className="mt-1 text-xs text-slate-500">
                Each configuration is versioned under its own GUID and can be edited or published independently.
              </p>
            </div>
            <Button asChild size="sm">
              <Link to={`/contracts/${contract.id}/configurations/new`}>
                <Plus className="mr-1.5 h-4 w-4" />
                New Configuration
              </Link>
            </Button>
          </div>

          {contract.availability_configurations.length === 0 ? (
            <div className="mt-4 text-sm text-slate-500">No availability configurations created yet.</div>
          ) : (
            <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {contract.availability_configurations.map((cfg) => (
                <Link
                  key={cfg.id}
                  to={`/contracts/${contract.id}/configurations/${cfg.id}`}
                  className="rounded-md border border-border bg-slate-50 p-3.5 transition hover:border-primary"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="truncate text-sm font-semibold text-slate-900">{cfg.name}</span>
                    <Badge
                      variant="outline"
                      className={
                        cfg.status === "published"
                          ? "border-emerald-200 bg-emerald-50 text-emerald-800"
                          : "border-amber-200 bg-amber-50 text-amber-800"
                      }
                    >
                      {cfg.status}
                    </Badge>
                  </div>
                  <div className="mt-2 text-xs text-slate-600">
                    v{cfg.latest_version_number} · {cfg.calculation_type ?? "Unset"}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </article>

        <div className="grid gap-4 lg:grid-cols-2">
          <article className="rounded-lg border border-border bg-white p-5">
            <SectionTitle icon={Factory} title="Wind farm and turbines" />
            {contract.wind_farms.map((windFarm) => (
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
                {contract.production_periods.map((period) => (
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
              <SectionTitle icon={AlertTriangle} title="Alarm categories & nested alarms" />
              <div className="mt-4 space-y-4">
                {contract.alarm_categories.map((category) => (
                  <div key={category.id} className="space-y-1.5">
                    <div className="flex items-center justify-between gap-3 text-sm">
                      <span className="text-slate-900">
                        <span className="font-semibold">{category.code}</span> - {category.name}
                      </span>
                      <span
                        className={`rounded px-2 py-0.5 text-xs font-semibold ${
                          category.is_required ? "bg-rose-50 text-rose-700" : "bg-slate-100 text-slate-600"
                        }`}
                      >
                        {category.is_required ? "Mandatory" : "Optional"}
                      </span>
                    </div>
                    {category.alarms.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 pl-2">
                        {category.alarms.map((alarm) => (
                          <span
                            key={alarm.id}
                            className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-700"
                          >
                            {alarm.code}: {alarm.name}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </article>
          </div>
        </div>
      </div>
    </section>
  );
}

function DashboardMessage({ message }: { message: string }) {
  return <div className="rounded-lg border border-border bg-white p-6 text-sm text-slate-600">{message}</div>;
}

function SectionTitle({ icon: Icon, title }: { icon: typeof Wind; title: string }) {
  return (
    <h3 className="flex items-center gap-2 font-semibold text-slate-950">
      <Icon className="h-5 w-5 text-primary" aria-hidden="true" />
      {title}
    </h3>
  );
}
