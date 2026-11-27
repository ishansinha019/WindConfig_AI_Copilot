import { Controller, type UseFormReturn } from "react-hook-form";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { CatalogResponse } from "@/lib/api";
import type { AvailabilitySnapshotFormValues } from "../schema";

type DetailsStepProps = {
  form: UseFormReturn<AvailabilitySnapshotFormValues>;
  catalog?: CatalogResponse;
};

export function DetailsStep({ form, catalog }: DetailsStepProps) {
  const { control } = form;

  const lowWindOptions = catalog?.low_wind_variants ?? [];
  const highWindOptions = catalog?.high_wind_variants ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-foreground">4. Details & wind parameters</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Set the warranted park availability percentage and contractual low/high wind behavior.
        </p>
      </div>

      <div className="grid gap-5 sm:grid-cols-2">
        <div className="space-y-2 sm:col-span-2">
          <Label htmlFor="park-availability">Park availability (%)</Label>
          <Controller
            control={control}
            name="details.park_availability_pct"
            render={({ field }) => (
              <Input
                id="park-availability"
                type="number"
                min={0}
                max={100}
                step={0.1}
                placeholder="e.g. 97.5"
                value={field.value ?? ""}
                onChange={(e) => {
                  const raw = e.target.value;
                  field.onChange(raw === "" ? null : Number(raw));
                }}
              />
            )}
          />
          {fieldError(form.watch("details.park_availability_pct")) && (
            <p className="text-xs font-medium text-destructive">
              Park availability must be between 0 and 100.
            </p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="low-wind-variant">Low wind variant</Label>
          <Controller
            control={control}
            name="details.low_wind_variant"
            render={({ field }) => (
              <Select
                value={field.value ?? ""}
                onValueChange={(val) => field.onChange(val || null)}
              >
                <SelectTrigger id="low-wind-variant">
                  <SelectValue placeholder="Select low wind variant" />
                </SelectTrigger>
                <SelectContent>
                  {lowWindOptions.map((opt) => (
                    <SelectItem key={opt.code} value={opt.code}>
                      {opt.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="high-wind-variant">High wind variant</Label>
          <Controller
            control={control}
            name="details.high_wind_variant"
            render={({ field }) => (
              <Select
                value={field.value ?? ""}
                onValueChange={(val) => field.onChange(val || null)}
              >
                <SelectTrigger id="high-wind-variant">
                  <SelectValue placeholder="Select high wind variant" />
                </SelectTrigger>
                <SelectContent>
                  {highWindOptions.map((opt) => (
                    <SelectItem key={opt.code} value={opt.code}>
                      {opt.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          />
        </div>
      </div>
    </div>
  );
}

function fieldError(val: number | null): boolean {
  return val !== null && (Number.isNaN(val) || val < 0 || val > 100);
}
