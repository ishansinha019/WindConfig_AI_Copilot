import { useMemo } from "react";
import { Info } from "lucide-react";
import { Controller, type UseFormReturn } from "react-hook-form";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { CatalogResponse, ContractDetail } from "@/lib/api";
import { AlarmTree } from "../components/AlarmTree";
import type { AvailabilitySnapshotFormValues } from "../schema";

type FormulaAlarmsStepProps = {
  form: UseFormReturn<AvailabilitySnapshotFormValues>;
  contract: ContractDetail;
  catalog?: CatalogResponse;
};

export function FormulaAlarmsStep({
  form,
  contract,
  catalog,
}: FormulaAlarmsStepProps) {
  const calcType = form.watch("basic_details.calculation_type");
  const selectedTurbineIds = form.watch("turbine_ids");
  const assignments = form.watch("alarm_assignments");

  const filteredFormulas = useMemo(() => {
    const all = catalog?.formulas ?? [];
    if (!calcType) return [];
    return all.filter((f) => f.calculation_type === calcType);
  }, [catalog?.formulas, calcType]);

  const selectedTurbines = useMemo(() => {
    const set = new Set(selectedTurbineIds);
    return contract.wind_farms
      .flatMap((wf) => wf.turbines)
      .filter((t) => set.has(t.id));
  }, [contract.wind_farms, selectedTurbineIds]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-foreground">3. Formula & alarm categories</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Choose the availability calculation formula and map contract alarms to turbines in scope.
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="formula-select">Availability formula</Label>
        {!calcType ? (
          <Alert className="border-amber-200 bg-amber-50/70 text-amber-900">
            <Info className="h-4 w-4 text-amber-700" />
            <AlertDescription className="text-xs">
              Select a calculation type (TBA, YBA, or RBA) in Step 1 to see matching formulas.
            </AlertDescription>
          </Alert>
        ) : (
          <Controller
            control={form.control}
            name="formula_code"
            render={({ field }) => (
              <Select
                value={field.value ?? ""}
                onValueChange={(val) => field.onChange(val || null)}
              >
                <SelectTrigger id="formula-select">
                  <SelectValue placeholder={`Select a ${calcType} formula`} />
                </SelectTrigger>
                <SelectContent>
                  {filteredFormulas.map((formula) => (
                    <SelectItem key={formula.code} value={formula.code}>
                      <span className="font-medium">{formula.name}</span>{" "}
                      <span className="font-mono text-xs text-muted-foreground">
                        ({formula.expression})
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          />
        )}
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Label>Alarm tree & turbine assignments</Label>
          <span className="text-xs text-muted-foreground">
            {assignments.length} {assignments.length === 1 ? "alarm" : "alarms"} included
          </span>
        </div>

        {selectedTurbines.length === 0 && (
          <Alert className="border-amber-200 bg-amber-50/70 text-amber-900">
            <Info className="h-4 w-4 text-amber-700" />
            <AlertDescription className="text-xs">
              No turbines are selected in Step 2 yet. Select turbines first so newly added alarms
              can be assigned automatically.
            </AlertDescription>
          </Alert>
        )}

        <AlarmTree
          alarmCategories={contract.alarm_categories}
          selectedTurbines={selectedTurbines}
          assignments={assignments}
          onChange={(next) =>
            form.setValue("alarm_assignments", next, { shouldDirty: true })
          }
        />
      </div>
    </div>
  );
}
