import { useEffect, useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertCircle } from "lucide-react";
import { useForm } from "react-hook-form";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { toast } from "sonner";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { VersionHistoryDialog } from "@/features/av-config/components/VersionHistoryDialog";
import { ReviewPublishPanel } from "@/features/av-config/ReviewPublishPanel";
import {
  availabilitySnapshotDraftSchema,
  type AvailabilitySnapshotFormValues,
  createEmptySnapshot,
  isStepComplete,
  normalizeSnapshot,
} from "@/features/av-config/schema";
import { BasicDetailsStep } from "@/features/av-config/steps/BasicDetailsStep";
import { DetailsStep } from "@/features/av-config/steps/DetailsStep";
import { FormulaAlarmsStep } from "@/features/av-config/steps/FormulaAlarmsStep";
import { TurbinesStep } from "@/features/av-config/steps/TurbinesStep";
import { WizardLayout } from "@/features/av-config/WizardLayout";
import {
  ApiError,
  createAvailabilityConfiguration,
  getAvailabilityConfiguration,
  getCatalog,
  getContract,
  saveAvailabilityDraft,
} from "@/lib/api";

function parseStep(raw: string | null): number {
  const num = Number(raw);
  if (Number.isInteger(num) && num >= 1 && num <= 4) {
    return num;
  }
  return 1;
}

export function AvConfigWizardPage() {
  const { contractId = "", configId } = useParams<{
    contractId: string;
    configId?: string;
  }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const isNew = !configId;
  const currentStep = parseStep(searchParams.get("step"));
  const [loadedVersion, setLoadedVersion] = useState<number | null>(null);
  const [initializedKey, setInitializedKey] = useState<string | null>(null);

  const contractQuery = useQuery({
    queryKey: ["contract", contractId],
    queryFn: () => getContract(contractId),
    enabled: Boolean(contractId),
  });

  const catalogQuery = useQuery({
    queryKey: ["catalog"],
    queryFn: getCatalog,
    staleTime: 10 * 60 * 1000,
  });

  const configQuery = useQuery({
    queryKey: ["av-config", contractId, configId],
    queryFn: () => getAvailabilityConfiguration(contractId, configId ?? ""),
    enabled: Boolean(contractId && configId),
  });

  const form = useForm<AvailabilitySnapshotFormValues>({
    resolver: zodResolver(availabilitySnapshotDraftSchema),
    defaultValues: createEmptySnapshot(),
    mode: "onChange",
  });

  // Hydrate form in New mode once contract loads
  useEffect(() => {
    if (!isNew || !contractQuery.data) return;
    const key = `new:${contractId}`;
    if (initializedKey === key) return;

    form.reset(createEmptySnapshot(contractQuery.data.target_availability));
    setLoadedVersion(null);
    setInitializedKey(key);
  }, [isNew, contractId, contractQuery.data, initializedKey, form]);

  // Hydrate form in Edit mode once config loads
  useEffect(() => {
    if (isNew || !configQuery.data) return;
    const cfg = configQuery.data;
    const key = `edit:${cfg.id}:v${cfg.latest_version.version_number}`;
    if (initializedKey === key) return;

    const normalized = normalizeSnapshot(
      cfg.latest_version.snapshot_data,
      cfg.name,
      contractQuery.data?.target_availability,
    );
    form.reset(normalized);
    setLoadedVersion(cfg.latest_version.version_number);
    setInitializedKey(key);
  }, [isNew, configQuery.data, contractQuery.data, initializedKey, form]);

  // Browser-level unsaved-changes guard (D15)
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (form.formState.isDirty) {
        e.preventDefault();
        e.returnValue = "";
      }
    };
    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [form.formState.isDirty]);

  const handleStepChange = (step: number) => {
    const clamped = Math.max(1, Math.min(4, step));
    setSearchParams({ step: String(clamped) }, { replace: true });
  };

  const handleBackToContracts = () => {
    if (
      form.formState.isDirty &&
      !window.confirm("You have unsaved changes. Leave without saving?")
    ) {
      return;
    }
    navigate("/");
  };

  const saveMutation = useMutation({
    mutationFn: async (values: AvailabilitySnapshotFormValues) => {
      if (isNew) {
        const created = await createAvailabilityConfiguration(contractId, values);
        return { mode: "create" as const, created };
      }
      const savedVersion = await saveAvailabilityDraft(
        contractId,
        configId ?? "",
        loadedVersion,
        values,
      );
      return { mode: "update" as const, savedVersion };
    },
    onSuccess: (result, values) => {
      form.reset(values);
      void queryClient.invalidateQueries({ queryKey: ["contracts"] });
      void queryClient.invalidateQueries({ queryKey: ["contract", contractId] });

      if (result.mode === "create") {
        const { created } = result;
        setLoadedVersion(created.latest_version.version_number);
        setInitializedKey(`edit:${created.id}:v${created.latest_version.version_number}`);
        toast.success(`Saved draft v${created.latest_version.version_number}`);
        navigate(
          `/contracts/${contractId}/configurations/${created.id}?step=${currentStep}`,
          { replace: true },
        );
      } else {
        const { savedVersion } = result;
        setLoadedVersion(savedVersion.version_number);
        setInitializedKey(`edit:${configId}:v${savedVersion.version_number}`);
        void queryClient.invalidateQueries({ queryKey: ["av-config", contractId, configId] });
        toast.success(`Saved draft v${savedVersion.version_number}`);
      }
    },
    onError: (err: Error) => {
      if (err instanceof ApiError && err.status === 409) {
        toast.error("Someone else saved a newer version.", {
          description: err.message,
          action: {
            label: "Reload latest",
            onClick: () => {
              setInitializedKey(null);
              void configQuery.refetch();
            },
          },
        });
        return;
      }
      toast.error(err.message);
    },
  });

  const handleSaveDraft = () => {
    void form.handleSubmit(
      (values) => saveMutation.mutate(values),
      (errors) => {
        if (errors.basic_details) {
          handleStepChange(1);
        }
        toast.error("Please fix the highlighted fields before saving.");
      },
    )();
  };

  if (contractQuery.isLoading || (!isNew && configQuery.isLoading)) {
    return (
      <section className="space-y-6">
        <Skeleton className="h-8 w-64" />
        <div className="grid gap-6 lg:grid-cols-[260px_1fr]">
          <Skeleton className="h-64 w-full rounded-lg" />
          <Skeleton className="h-96 w-full rounded-lg" />
        </div>
      </section>
    );
  }

  if (contractQuery.isError || !contractQuery.data || (!isNew && configQuery.isError)) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Could not load wizard</AlertTitle>
        <AlertDescription>
          Failed to load the contract or availability configuration. Return to the home page and try
          again.
        </AlertDescription>
      </Alert>
    );
  }

  const contract = contractQuery.data;
  const watchedValues = form.watch();
  const completedSteps: Record<number, boolean> = {
    1: isStepComplete(1, watchedValues),
    2: isStepComplete(2, watchedValues),
    3: isStepComplete(3, watchedValues),
    4: isStepComplete(4, watchedValues),
  };

  return (
    <section className="space-y-6">
      <div className="space-y-2">
        <button
          type="button"
          onClick={handleBackToContracts}
          className="text-sm font-medium text-primary hover:underline"
        >
          ← All contracts
        </button>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-semibold text-foreground">
              {watchedValues.basic_details.name.trim() ||
                (isNew ? "New Availability Configuration" : configQuery.data?.name)}
            </h1>
            {!isNew && configQuery.data && (
              <Badge variant="outline">
                v{loadedVersion ?? configQuery.data.latest_version_number} &bull;{" "}
                {configQuery.data.status}
              </Badge>
            )}
          </div>
          {!isNew && configId && (
            <VersionHistoryDialog contractId={contractId} configId={configId} />
          )}
        </div>
        <p className="text-sm text-muted-foreground">
          Contract: {contract.name} ({contract.wind_farm_name})
        </p>
      </div>

      <WizardLayout
        currentStep={currentStep}
        completedSteps={completedSteps}
        isDirty={form.formState.isDirty}
        isSaving={saveMutation.isPending}
        onStepChange={handleStepChange}
        onSaveDraft={handleSaveDraft}
      >
        {currentStep === 1 && (
          <BasicDetailsStep
            form={form}
            contract={contract}
            catalog={catalogQuery.data}
          />
        )}
        {currentStep === 2 && <TurbinesStep form={form} contract={contract} />}
        {currentStep === 3 && (
          <FormulaAlarmsStep
            form={form}
            contract={contract}
            catalog={catalogQuery.data}
          />
        )}
        {currentStep === 4 && (
          <DetailsStep form={form} catalog={catalogQuery.data} />
        )}
      </WizardLayout>

      <ReviewPublishPanel
        contractId={contractId}
        configId={configId}
        latestVersionId={configQuery.data?.latest_version.id}
        isNew={isNew}
        isDirty={form.formState.isDirty}
        isAlreadyPublished={
          configQuery.data?.latest_version.status === "published"
        }
        values={watchedValues}
        onJumpToStep={handleStepChange}
      />
    </section>
  );
}
