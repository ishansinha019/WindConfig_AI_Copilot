import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertCircle,
  AlertTriangle,
  ArrowUpRight,
  CheckCircle2,
  Send,
} from "lucide-react";
import { toast } from "sonner";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import {
  getAvailabilityReadiness,
  publishAvailabilityVersion,
} from "@/lib/api";
import type { AvailabilitySnapshotFormValues } from "./schema";

type ReviewPublishPanelProps = {
  contractId: string;
  configId?: string;
  latestVersionId?: string;
  isNew: boolean;
  isDirty: boolean;
  isAlreadyPublished: boolean;
  values: AvailabilitySnapshotFormValues;
  onJumpToStep: (step: number) => void;
};

export function ReviewPublishPanel({
  contractId,
  configId,
  latestVersionId,
  isNew,
  isDirty,
  isAlreadyPublished,
  values,
  onJumpToStep,
}: ReviewPublishPanelProps) {
  const queryClient = useQueryClient();

  const readinessQuery = useQuery({
    queryKey: ["av-readiness", contractId, configId, latestVersionId],
    queryFn: () =>
      getAvailabilityReadiness(contractId, configId ?? "", latestVersionId ?? ""),
    enabled: Boolean(!isNew && configId && latestVersionId),
  });

  const publishMutation = useMutation({
    mutationFn: () =>
      publishAvailabilityVersion(contractId, configId ?? "", latestVersionId ?? ""),
    onSuccess: (published) => {
      toast.success(`Published version v${published.version_number}!`);
      void queryClient.invalidateQueries({ queryKey: ["contracts"] });
      void queryClient.invalidateQueries({ queryKey: ["contract", contractId] });
      void queryClient.invalidateQueries({ queryKey: ["av-config", contractId, configId] });
      void queryClient.invalidateQueries({ queryKey: ["av-readiness", contractId, configId] });
      void queryClient.invalidateQueries({ queryKey: ["av-versions", contractId, configId] });
    },
    onError: (err: Error) => {
      toast.error(err.message);
    },
  });

  const readiness = readinessQuery.data;
  const canPublish =
    !isNew &&
    !isDirty &&
    !isAlreadyPublished &&
    readiness?.is_valid === true &&
    !publishMutation.isPending;

  return (
    <Card>
      <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-3 pb-4">
        <div>
          <CardTitle className="text-base">Review & Publish</CardTitle>
          <p className="mt-1 text-xs text-muted-foreground">
            Verify all 4 steps and resolve any blocking readiness errors before publishing.
          </p>
        </div>

        <Button
          type="button"
          size="sm"
          disabled={!canPublish}
          onClick={() => publishMutation.mutate()}
        >
          <Send className="mr-1.5 h-3.5 w-3.5" />
          {isAlreadyPublished
            ? "Published"
            : publishMutation.isPending
              ? "Publishing..."
              : "Publish"}
        </Button>
      </CardHeader>

      <CardContent className="space-y-5">
        {/* Read-only 4-step summary */}
        <div className="grid gap-3 text-xs sm:grid-cols-2 lg:grid-cols-4">
          <SummaryBox
            title="1. Basic details"
            onClick={() => onJumpToStep(1)}
            lines={[
              `Name: ${values.basic_details.name || "Unset"}`,
              `Type: ${values.basic_details.calculation_type ?? "Unset"}`,
              `Dates: ${
                values.basic_details.start_date && values.basic_details.end_date
                  ? `${values.basic_details.start_date} → ${values.basic_details.end_date}`
                  : "Unset"
              }`,
            ]}
          />
          <SummaryBox
            title="2. Turbines"
            onClick={() => onJumpToStep(2)}
            lines={[`Selected: ${values.turbine_ids.length} turbine(s)`]}
          />
          <SummaryBox
            title="3. Formula & alarms"
            onClick={() => onJumpToStep(3)}
            lines={[
              `Formula: ${values.formula_code ?? "Unset"}`,
              `Alarms: ${values.alarm_assignments.length} included`,
            ]}
          />
          <SummaryBox
            title="4. Details"
            onClick={() => onJumpToStep(4)}
            lines={[
              `Park avail: ${values.details.park_availability_pct ?? "Unset"}%`,
              `Low wind: ${values.details.low_wind_variant ?? "Unset"}`,
              `High wind: ${values.details.high_wind_variant ?? "Unset"}`,
            ]}
          />
        </div>

        <Separator />

        {/* Readiness results */}
        {isNew ? (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Draft not saved yet</AlertTitle>
            <AlertDescription className="text-xs">
              Click <strong>Save draft</strong> in the footer to create this configuration and run
              backend readiness validation.
            </AlertDescription>
          </Alert>
        ) : isDirty ? (
          <Alert className="border-amber-200 bg-amber-50 text-amber-900">
            <AlertTriangle className="h-4 w-4 text-amber-700" />
            <AlertTitle>Unsaved changes</AlertTitle>
            <AlertDescription className="text-xs">
              Save your draft before publishing so readiness checks evaluate your latest edits.
            </AlertDescription>
          </Alert>
        ) : readinessQuery.isLoading ? (
          <p className="text-xs text-muted-foreground">Running deterministic readiness checks...</p>
        ) : readiness ? (
          <div className="space-y-3">
            {readiness.is_valid ? (
              <div className="flex items-center gap-2 rounded-md border border-emerald-200 bg-emerald-50 px-3.5 py-2.5 text-xs font-medium text-emerald-800">
                <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600" />
                <span>
                  {isAlreadyPublished
                    ? "This version is published and active."
                    : "All deterministic checks passed. Ready to publish."}
                </span>
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-xs font-semibold text-destructive">
                  {readiness.blocking_errors.length} Blocking Error(s) — click an error to jump to
                  that step:
                </p>
                <div className="space-y-1.5">
                  {readiness.blocking_errors.map((err, idx) => (
                    <button
                      key={`${err.field}-${idx}`}
                      type="button"
                      onClick={() => onJumpToStep(err.step)}
                      className="flex w-full items-center justify-between gap-2 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-left text-xs text-rose-900 transition hover:bg-rose-100"
                    >
                      <span className="flex items-center gap-2">
                        <Badge variant="outline" className="border-rose-300 bg-white text-rose-800">
                          Step {err.step}
                        </Badge>
                        <span>{err.message}</span>
                      </span>
                      <ArrowUpRight className="h-3.5 w-3.5 shrink-0 text-rose-700" />
                    </button>
                  ))}
                </div>
              </div>
            )}

            {readiness.warnings.length > 0 && (
              <div className="space-y-1.5">
                <p className="text-xs font-semibold text-amber-800">
                  {readiness.warnings.length} Warning(s):
                </p>
                {readiness.warnings.map((warn, idx) => (
                  <button
                    key={`${warn.field}-${idx}`}
                    type="button"
                    onClick={() => onJumpToStep(warn.step)}
                    className="flex w-full items-center justify-between gap-2 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-left text-xs text-amber-900 transition hover:bg-amber-100"
                  >
                    <span className="flex items-center gap-2">
                      <Badge variant="outline" className="border-amber-300 bg-white text-amber-800">
                        Step {warn.step}
                      </Badge>
                      <span>{warn.message}</span>
                    </span>
                    <ArrowUpRight className="h-3.5 w-3.5 shrink-0 text-amber-700" />
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}

function SummaryBox({
  title,
  lines,
  onClick,
}: {
  title: string;
  lines: string[];
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="rounded-md border border-border bg-muted/30 p-3 text-left transition hover:border-primary/50 hover:bg-muted/50"
    >
      <div className="font-semibold text-foreground">{title}</div>
      <div className="mt-1.5 space-y-0.5 text-muted-foreground">
        {lines.map((line, i) => (
          <div key={i} className="truncate">
            {line}
          </div>
        ))}
      </div>
    </button>
  );
}
