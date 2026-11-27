import { Info } from "lucide-react";
import { Controller, type UseFormReturn } from "react-hook-form";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { CatalogResponse, ContractDetail } from "@/lib/api";
import { DatePicker } from "../components/DatePicker";
import type { AvailabilitySnapshotFormValues } from "../schema";

type BasicDetailsStepProps = {
  form: UseFormReturn<AvailabilitySnapshotFormValues>;
  contract: ContractDetail;
  catalog?: CatalogResponse;
};

export function BasicDetailsStep({ form, contract, catalog }: BasicDetailsStepProps) {
  const {
    control,
    register,
    watch,
    formState: { errors },
  } = form;

  const startDate = watch("basic_details.start_date");
  const endDate = watch("basic_details.end_date");

  const isOutsideContractDates = Boolean(
    (startDate && startDate < contract.start_date) ||
      (endDate && endDate > contract.end_date) ||
      (startDate && startDate > contract.end_date) ||
      (endDate && endDate < contract.start_date),
  );

  const calcTypes = catalog?.calculation_types ?? [
    { code: "TBA", name: "Time-Based Availability", description: "" },
    { code: "YBA", name: "Yield-Based Availability", description: "" },
    { code: "RBA", name: "Revenue-Based Availability", description: "" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-foreground">1. Basic details</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Define the configuration name, warranted calculation type, and effective date window.
        </p>
      </div>

      <div className="grid gap-5 sm:grid-cols-2">
        <div className="space-y-2 sm:col-span-2">
          <Label htmlFor="contract-name">Contract name</Label>
          <Input
            id="contract-name"
            value={contract.name}
            readOnly
            disabled
            className="bg-muted/50"
          />
        </div>

        <div className="space-y-2 sm:col-span-2">
          <Label htmlFor="av-config-name">
            AV configuration name <span className="text-destructive">*</span>
          </Label>
          <Input
            id="av-config-name"
            placeholder="e.g. North Ridge 2026 – Base TBA"
            {...register("basic_details.name")}
          />
          {errors.basic_details?.name && (
            <p className="text-xs font-medium text-destructive">
              {errors.basic_details.name.message}
            </p>
          )}
        </div>

        <div className="space-y-2 sm:col-span-2">
          <Label htmlFor="calculation-type">Warranted calculation type</Label>
          <Controller
            control={control}
            name="basic_details.calculation_type"
            render={({ field }) => (
              <Select
                value={field.value ?? ""}
                onValueChange={(val) => field.onChange(val || null)}
              >
                <SelectTrigger id="calculation-type">
                  <SelectValue placeholder="Select calculation type (TBA, YBA, RBA)" />
                </SelectTrigger>
                <SelectContent>
                  {calcTypes.map((ct) => (
                    <SelectItem key={ct.code} value={ct.code}>
                      <span className="font-medium">{ct.code}</span> — {ct.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="start-date">Start date</Label>
          <Controller
            control={control}
            name="basic_details.start_date"
            render={({ field }) => (
              <DatePicker
                id="start-date"
                value={field.value}
                onChange={field.onChange}
                placeholder="Select start date"
              />
            )}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="end-date">End date</Label>
          <Controller
            control={control}
            name="basic_details.end_date"
            render={({ field }) => (
              <DatePicker
                id="end-date"
                value={field.value}
                onChange={field.onChange}
                placeholder="Select end date"
              />
            )}
          />
          {errors.basic_details?.end_date && (
            <p className="text-xs font-medium text-destructive">
              {errors.basic_details.end_date.message}
            </p>
          )}
        </div>
      </div>

      {isOutsideContractDates && (
        <Alert className="border-sky-200 bg-sky-50/70 text-sky-900">
          <Info className="h-4 w-4 text-sky-700" />
          <AlertDescription className="text-xs">
            Selected dates extend outside the contract term ({contract.start_date} to{" "}
            {contract.end_date}). This is allowed for contract renewals and extensions.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}
