import { useMemo } from "react";
import type { UseFormReturn } from "react-hook-form";

import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { ContractDetail, Turbine } from "@/lib/api";
import type { AvailabilitySnapshotFormValues } from "../schema";

type TurbinesStepProps = {
  form: UseFormReturn<AvailabilitySnapshotFormValues>;
  contract: ContractDetail;
};

type TurbineGroupBucket = {
  groupName: string;
  turbines: Turbine[];
};

export function TurbinesStep({ form, contract }: TurbinesStepProps) {
  const selectedIds = form.watch("turbine_ids");
  const selectedSet = useMemo(() => new Set(selectedIds), [selectedIds]);

  const allTurbines = useMemo(
    () => contract.wind_farms.flatMap((wf) => wf.turbines),
    [contract.wind_farms],
  );

  const groups = useMemo<TurbineGroupBucket[]>(() => {
    const map = new Map<string, Turbine[]>();
    for (const turbine of allTurbines) {
      const groupName = turbine.turbine_group?.name ?? "Ungrouped";
      const list = map.get(groupName) ?? [];
      list.push(turbine);
      map.set(groupName, list);
    }
    return Array.from(map.entries()).map(([groupName, turbines]) => ({
      groupName,
      turbines,
    }));
  }, [allTurbines]);

  const updateSelectedTurbines = (nextIds: string[]) => {
    const nextSet = new Set(nextIds);
    form.setValue("turbine_ids", nextIds, { shouldDirty: true });

    // D4 invariant: prune removed turbines from all alarm assignments
    const currentAssignments = form.getValues("alarm_assignments");
    const prunedAssignments = currentAssignments.map((assignment) => ({
      ...assignment,
      turbine_ids: assignment.turbine_ids.filter((tid) => nextSet.has(tid)),
    }));
    form.setValue("alarm_assignments", prunedAssignments, { shouldDirty: true });
  };

  const toggleAll = (checked: boolean) => {
    if (checked) {
      updateSelectedTurbines(allTurbines.map((t) => t.id));
    } else {
      updateSelectedTurbines([]);
    }
  };

  const toggleGroup = (turbines: Turbine[], checked: boolean) => {
    const groupIds = new Set(turbines.map((t) => t.id));
    if (checked) {
      const merged = new Set(selectedIds);
      for (const id of groupIds) merged.add(id);
      updateSelectedTurbines(Array.from(merged));
    } else {
      updateSelectedTurbines(selectedIds.filter((id) => !groupIds.has(id)));
    }
  };

  const toggleOne = (turbineId: string, checked: boolean) => {
    if (checked) {
      if (!selectedSet.has(turbineId)) {
        updateSelectedTurbines([...selectedIds, turbineId]);
      }
    } else {
      updateSelectedTurbines(selectedIds.filter((id) => id !== turbineId));
    }
  };

  const allChecked: boolean | "indeterminate" =
    allTurbines.length > 0 && selectedIds.length === allTurbines.length
      ? true
      : selectedIds.length > 0
        ? "indeterminate"
        : false;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-foreground">2. Turbines in scope</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Select the turbines from <span className="font-medium">{contract.wind_farm_name}</span>{" "}
            covered by this availability configuration.
          </p>
        </div>
        <Badge variant="secondary" className="text-xs">
          {selectedIds.length} of {allTurbines.length} selected
        </Badge>
      </div>

      <div className="flex items-center gap-2.5 rounded-md border border-border bg-muted/30 px-4 py-2.5">
        <Checkbox
          id="select-all-turbines"
          checked={allChecked}
          onCheckedChange={(state) => toggleAll(state === true)}
        />
        <label
          htmlFor="select-all-turbines"
          className="cursor-pointer text-sm font-medium text-foreground"
        >
          Select all turbines ({allTurbines.length})
        </label>
      </div>

      <div className="space-y-4">
        {groups.map((group) => {
          const groupSelectedCount = group.turbines.filter((t) => selectedSet.has(t.id)).length;
          const groupState: boolean | "indeterminate" =
            groupSelectedCount === group.turbines.length
              ? true
              : groupSelectedCount > 0
                ? "indeterminate"
                : false;

          return (
            <div key={group.groupName} className="overflow-hidden rounded-md border border-border">
              <div className="flex items-center justify-between border-b border-border bg-muted/40 px-4 py-2.5">
                <div className="flex items-center gap-2.5">
                  <Checkbox
                    id={`group-${group.groupName}`}
                    checked={groupState}
                    onCheckedChange={(state) => toggleGroup(group.turbines, state === true)}
                  />
                  <label
                    htmlFor={`group-${group.groupName}`}
                    className="cursor-pointer text-sm font-semibold text-foreground"
                  >
                    {group.groupName}
                  </label>
                </div>
                <span className="text-xs text-muted-foreground">
                  {groupSelectedCount} / {group.turbines.length} selected
                </span>
              </div>

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12" />
                    <TableHead>Code</TableHead>
                    <TableHead>Model</TableHead>
                    <TableHead className="text-right">Rated Power</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {group.turbines.map((turbine) => {
                    const isChecked = selectedSet.has(turbine.id);
                    return (
                      <TableRow
                        key={turbine.id}
                        className="cursor-pointer"
                        onClick={() => toggleOne(turbine.id, !isChecked)}
                      >
                        <TableCell onClick={(e) => e.stopPropagation()}>
                          <Checkbox
                            checked={isChecked}
                            onCheckedChange={(state) => toggleOne(turbine.id, state === true)}
                            aria-label={`Select turbine ${turbine.code}`}
                          />
                        </TableCell>
                        <TableCell className="font-mono font-medium">{turbine.code}</TableCell>
                        <TableCell>{turbine.model_name}</TableCell>
                        <TableCell className="text-right">{turbine.rated_power_mw} MW</TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          );
        })}
      </div>
    </div>
  );
}
