import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  Factory,
  Layers3,
  Send,
  Sliders,
  Wind,
} from "lucide-react";
import { Link, useParams } from "react-router-dom";

import {
  getActiveConfiguration,
  getConfigurationReadiness,
  getContract,
  publishConfiguration,
  type ConfigurationStatus,
} from "../lib/api";

const configStatusClasses: Record<ConfigurationStatus, string> = {
  draft: "bg-amber-50 text-amber-800 border-amber-200",
  in_review: "bg-blue-50 text-blue-800 border-blue-200",
  published: "bg-emerald-50 text-emerald-800 border-emerald-200",
  archived: "bg-slate-100 text-slate-700 border-slate-200",
};

export function ContractDetailPage() {
  const { contractId } = useParams<{ contractId: string }>();
  const [publishMessage, setPublishMessage] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const detailQuery = useQuery({
    queryKey: ["contract", contractId],
    queryFn: () => getContract(contractId ?? ""),
    enabled: Boolean(contractId),
  });

  const configQuery = useQuery({
    queryKey: ["contract-config", contractId],
    queryFn: () => getActiveConfiguration(contractId ?? ""),
    enabled: Boolean(contractId),
  });

  const currentVersion = configQuery.data?.current_version;

  const readinessQuery = useQuery({
    queryKey: ["config-readiness", contractId, currentVersion?.id],
    queryFn: () => getConfigurationReadiness(contractId ?? "", currentVersion?.id ?? ""),
    enabled: Boolean(contractId && currentVersion?.id),
  });

  const publishMutation = useMutation({
    mutationFn: () => publishConfiguration(contractId ?? "", currentVersion?.id ?? ""),
    onSuccess: (publishedVersion) => {
      setPublishMessage(`Successfully published Version ${publishedVersion.version_number}!`);
      void queryClient.invalidateQueries({ queryKey: ["contracts"] });
      void queryClient.invalidateQueries({ queryKey: ["contract", contractId] });
      void queryClient.invalidateQueries({ queryKey: ["contract-config", contractId] });
      void queryClient.invalidateQueries({ queryKey: ["config-readiness", contractId] });
    },
    onError: (err: Error) => {
      setPublishMessage(`Publish failed: ${err.message}`);
    },
  });

  if (!contractId || detailQuery.isLoading) {
    return <DashboardMessage message="Loading contract details..." />;
  }

  if (detailQuery.isError || !detailQuery.data) {
    return <DashboardMessage message="Could not load the selected contract details." />;
  }

  return (
    <section className="space-y-6">
      <div className="space-y-2">
        <Link to="/" className="text-sm font-medium text-primary hover:underline">
          ← All contracts
        </Link>
        <div>
          <p className="text-sm font-semibold text-primary">Contract overview</p>
          <h1 className="mt-1 text-2xl font-semibold text-foreground">{detailQuery.data.name}</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {detailQuery.data.customer_name} · {detailQuery.data.wind_farm_name}
          </p>
        </div>
      </div>

      <div className="space-y-6">
          {/* Active Configuration Snapshot & Deterministic Readiness Card */}
          <article className="rounded-lg border border-border bg-white p-5 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-4">
              <div>
                <SectionTitle icon={Sliders} title="Active Availability Configuration" />
                <p className="mt-1 text-xs text-slate-500">
                  Versioned snapshot defining IEC 61400-26-1 formulas, turbine scope, and alarm inclusion rules.
                </p>
              </div>
              {currentVersion ? (
                <div className="flex items-center gap-3">
                  <span
                    className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wider ${
                      configStatusClasses[currentVersion.status]
                    }`}
                  >
                    Version {currentVersion.version_number} &bull; {currentVersion.status}
                  </span>
                  {currentVersion.status !== "published" && (
                    <button
                      type="button"
                      disabled={publishMutation.isPending || readinessQuery.data?.is_valid === false}
                      onClick={() => publishMutation.mutate()}
                      className="inline-flex items-center gap-1.5 rounded-md bg-primary px-3.5 py-1.5 text-xs font-semibold text-white shadow-sm transition hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      <Send className="h-3.5 w-3.5" />
                      {publishMutation.isPending ? "Validating & Publishing..." : "Publish Configuration"}
                    </button>
                  )}
                </div>
              ) : (
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                  No active version draft
                </span>
              )}
            </div>

            {publishMessage && (
              <div
                className={`mt-4 rounded-md p-3 text-xs font-medium ${
                  publishMessage.startsWith("Publish failed")
                    ? "bg-rose-50 text-rose-800"
                    : "bg-emerald-50 text-emerald-800"
                }`}
              >
                {publishMessage}
              </div>
            )}

            {currentVersion ? (
              <div className="mt-5 grid gap-5 md:grid-cols-3">
                <div className="rounded-lg bg-slate-50 p-4">
                  <span className="text-xs font-semibold uppercase text-slate-500">Availability Formula</span>
                  <p className="mt-1 font-semibold text-slate-900">
                    {currentVersion.snapshot_data.formula_name ?? "Standard Time-based"}
                  </p>
                  <p className="mt-1 font-mono text-xs text-slate-600">
                    Type: {currentVersion.snapshot_data.formula_type}
                  </p>
                  <div className="mt-3 text-xs text-slate-600">
                    Target SLA: <span className="font-semibold text-slate-900">{currentVersion.snapshot_data.target_availability}%</span>
                  </div>
                </div>

                <div className="rounded-lg bg-slate-50 p-4">
                  <span className="text-xs font-semibold uppercase text-slate-500">Deterministic Validation</span>
                  {readinessQuery.isLoading && <p className="mt-1 text-xs text-slate-500">Evaluating rules...</p>}
                  {readinessQuery.data && (
                    <div className="mt-2 space-y-2">
                      <div className="flex items-center gap-1.5">
                        {readinessQuery.data.is_valid ? (
                          <>
                            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                            <span className="text-xs font-medium text-emerald-800">
                              Ready to Publish (0 blocking errors)
                            </span>
                          </>
                        ) : (
                          <>
                            <AlertCircle className="h-4 w-4 text-rose-600" />
                            <span className="text-xs font-medium text-rose-800">
                              {readinessQuery.data.blocking_errors.length} Blocking Validation Error(s)
                            </span>
                          </>
                        )}
                      </div>
                      {readinessQuery.data.blocking_errors.map((err, i) => (
                        <p key={i} className="text-xs text-rose-700">
                          &bull; {err}
                        </p>
                      ))}
                    </div>
                  )}
                </div>

                <div className="rounded-lg bg-slate-50 p-4">
                  <span className="text-xs font-semibold uppercase text-slate-500">Parameters & Governance</span>
                  <div className="mt-2 space-y-1 text-xs text-slate-700">
                    <div>
                      Turbines in scope: <span className="font-semibold">{currentVersion.snapshot_data.turbine_ids?.length ?? 0}</span>
                    </div>
                    <div>
                      Alarms in formula: <span className="font-semibold">{currentVersion.snapshot_data.included_alarm_codes?.join(", ") ?? "None"}</span>
                    </div>
                    <div className="truncate font-mono text-[10px] text-slate-400">
                      Checksum: {currentVersion.checksum.substring(0, 16)}...
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="mt-4 text-sm text-slate-500">No configuration snapshot has been created yet.</div>
            )}
          </article>

          {/* Wind farm & Turbine Asset Table + Operational Periods */}
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
                <SectionTitle icon={AlertTriangle} title="Alarm categories & SLA mapping" />
                <div className="mt-4 space-y-3">
                  {detailQuery.data.alarm_categories.map((alarm) => (
                    <div key={alarm.id} className="flex items-center justify-between gap-3 text-sm">
                      <span className="text-slate-900">
                        <span className="font-semibold">{alarm.code}</span> - {alarm.name}
                      </span>
                      <span
                        className={`rounded px-2 py-0.5 text-xs font-semibold ${
                          alarm.is_required ? "bg-rose-50 text-rose-700" : "bg-slate-100 text-slate-600"
                        }`}
                      >
                        {alarm.is_required ? "Mandatory in Formula" : "Optional"}
                      </span>
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
