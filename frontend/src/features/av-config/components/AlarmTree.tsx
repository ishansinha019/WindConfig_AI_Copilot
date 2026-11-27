import { useMemo, useState } from "react";
import { ChevronDown, ChevronRight, ChevronsUpDown } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import type { AlarmAssignment, ContractDetail, Turbine } from "@/lib/api";

type AlarmTreeProps = {
  alarmCategories: ContractDetail["alarm_categories"];
  selectedTurbines: Turbine[];
  assignments: AlarmAssignment[];
  onChange: (nextAssignments: AlarmAssignment[]) => void;
};

export function AlarmTree({
  alarmCategories,
  selectedTurbines,
  assignments,
  onChange,
}: AlarmTreeProps) {
  const [openCategories, setOpenCategories] = useState<Record<string, boolean>>(() =>
    Object.fromEntries(alarmCategories.map((c) => [c.id, true])),
  );

  const assignmentMap = useMemo(() => {
    const map = new Map<string, string[]>();
    for (const item of assignments) {
      map.set(item.alarm_id, item.turbine_ids);
    }
    return map;
  }, [assignments]);

  const allStep2TurbineIds = useMemo(
    () => selectedTurbines.map((t) => t.id),
    [selectedTurbines],
  );

  const toggleCategory = (category: ContractDetail["alarm_categories"][number], checked: boolean) => {
    const categoryAlarmIds = new Set(category.alarms.map((a) => a.id));
    if (checked) {
      const next = [...assignments];
      for (const alarm of category.alarms) {
        if (!assignmentMap.has(alarm.id)) {
          next.push({ alarm_id: alarm.id, turbine_ids: [...allStep2TurbineIds] });
        }
      }
      onChange(next);
    } else {
      onChange(assignments.filter((a) => !categoryAlarmIds.has(a.alarm_id)));
    }
  };

  const toggleAlarm = (alarmId: string, checked: boolean) => {
    if (checked) {
      if (!assignmentMap.has(alarmId)) {
        onChange([...assignments, { alarm_id: alarmId, turbine_ids: [...allStep2TurbineIds] }]);
      }
    } else {
      onChange(assignments.filter((a) => a.alarm_id !== alarmId));
    }
  };

  const updateAlarmTurbines = (alarmId: string, nextTurbineIds: string[]) => {
    onChange(
      assignments.map((a) =>
        a.alarm_id === alarmId ? { ...a, turbine_ids: nextTurbineIds } : a,
      ),
    );
  };

  return (
    <div className="space-y-3">
      {alarmCategories.map((category) => {
        const includedCount = category.alarms.filter((a) => assignmentMap.has(a.id)).length;
        const categoryState: boolean | "indeterminate" =
          category.alarms.length > 0 && includedCount === category.alarms.length
            ? true
            : includedCount > 0
              ? "indeterminate"
              : false;
        const isOpen = openCategories[category.id] ?? true;

        return (
          <Collapsible
            key={category.id}
            open={isOpen}
            onOpenChange={(open) =>
              setOpenCategories((prev) => ({ ...prev, [category.id]: open }))
            }
            className="overflow-hidden rounded-md border border-border"
          >
            <div className="flex items-center justify-between gap-3 bg-muted/40 px-3.5 py-2.5">
              <div className="flex items-center gap-2.5">
                <CollapsibleTrigger asChild>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6"
                    aria-label={`Toggle ${category.name}`}
                  >
                    {isOpen ? (
                      <ChevronDown className="h-4 w-4" />
                    ) : (
                      <ChevronRight className="h-4 w-4" />
                    )}
                  </Button>
                </CollapsibleTrigger>

                <Checkbox
                  id={`cat-${category.id}`}
                  checked={categoryState}
                  onCheckedChange={(state) => toggleCategory(category, state === true)}
                />

                <label
                  htmlFor={`cat-${category.id}`}
                  className="cursor-pointer text-sm font-semibold text-foreground"
                >
                  <span className="font-mono">{category.code}</span> — {category.name}
                </label>

                {category.is_required ? (
                  <Badge variant="outline" className="border-rose-200 bg-rose-50 text-rose-700">
                    Required
                  </Badge>
                ) : (
                  <Badge variant="outline" className="text-muted-foreground">
                    Optional
                  </Badge>
                )}
              </div>

              <span className="text-xs text-muted-foreground">
                {includedCount} / {category.alarms.length} alarms
              </span>
            </div>

            <CollapsibleContent>
              <div className="divide-y divide-border bg-card">
                {category.alarms.map((alarm) => {
                  const isIncluded = assignmentMap.has(alarm.id);
                  const assignedIds = assignmentMap.get(alarm.id) ?? [];

                  return (
                    <div
                      key={alarm.id}
                      className="flex flex-wrap items-center justify-between gap-3 px-4 py-2.5 pl-11"
                    >
                      <div className="flex items-center gap-2.5">
                        <Checkbox
                          id={`alarm-${alarm.id}`}
                          checked={isIncluded}
                          onCheckedChange={(state) => toggleAlarm(alarm.id, state === true)}
                        />
                        <label
                          htmlFor={`alarm-${alarm.id}`}
                          className="cursor-pointer text-sm text-foreground"
                        >
                          <span className="font-mono text-xs font-semibold text-muted-foreground">
                            {alarm.code}
                          </span>{" "}
                          {alarm.name}
                        </label>
                      </div>

                      {isIncluded && (
                        <AlarmTurbineMultiSelect
                          selectedTurbines={selectedTurbines}
                          assignedIds={assignedIds}
                          onChange={(nextIds) => updateAlarmTurbines(alarm.id, nextIds)}
                        />
                      )}
                    </div>
                  );
                })}
              </div>
            </CollapsibleContent>
          </Collapsible>
        );
      })}
    </div>
  );
}

function AlarmTurbineMultiSelect({
  selectedTurbines,
  assignedIds,
  onChange,
}: {
  selectedTurbines: Turbine[];
  assignedIds: string[];
  onChange: (nextIds: string[]) => void;
}) {
  const [open, setOpen] = useState(false);
  const assignedSet = useMemo(() => new Set(assignedIds), [assignedIds]);

  const label =
    selectedTurbines.length === 0
      ? "No turbines in Step 2"
      : assignedIds.length === selectedTurbines.length
        ? `All ${selectedTurbines.length} turbines`
        : `${assignedIds.length} of ${selectedTurbines.length} turbines`;

  const toggleTurbine = (turbineId: string) => {
    if (assignedSet.has(turbineId)) {
      onChange(assignedIds.filter((id) => id !== turbineId));
    } else {
      onChange([...assignedIds, turbineId]);
    }
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className={`h-8 justify-between gap-2 text-xs ${
            assignedIds.length === 0 ? "border-rose-300 text-rose-700" : ""
          }`}
        >
          <span>{label}</span>
          <ChevronsUpDown className="h-3.5 w-3.5 opacity-60" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-64 p-0" align="end">
        <Command>
          <CommandInput placeholder="Filter turbines..." className="h-8 text-xs" />
          <CommandList>
            <CommandEmpty>No turbines selected in Step 2.</CommandEmpty>
            {selectedTurbines.length > 0 && (
              <CommandGroup>
                <CommandItem
                  onSelect={() => {
                    if (assignedIds.length === selectedTurbines.length) {
                      onChange([]);
                    } else {
                      onChange(selectedTurbines.map((t) => t.id));
                    }
                  }}
                  className="text-xs font-medium"
                >
                  <Checkbox
                    checked={assignedIds.length === selectedTurbines.length}
                    className="mr-2"
                  />
                  Select all ({selectedTurbines.length})
                </CommandItem>
                {selectedTurbines.map((turbine) => (
                  <CommandItem
                    key={turbine.id}
                    value={`${turbine.code} ${turbine.model_name}`}
                    onSelect={() => toggleTurbine(turbine.id)}
                    className="text-xs"
                  >
                    <Checkbox checked={assignedSet.has(turbine.id)} className="mr-2" />
                    <span className="font-mono font-semibold">{turbine.code}</span>
                    <span className="ml-1.5 text-muted-foreground">{turbine.model_name}</span>
                  </CommandItem>
                ))}
              </CommandGroup>
            )}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
