import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import { History } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { getAvailabilityDiff, getAvailabilityVersions } from "@/lib/api";

type VersionHistoryDialogProps = {
  contractId: string;
  configId: string;
};

export function VersionHistoryDialog({
  contractId,
  configId,
}: VersionHistoryDialogProps) {
  const [open, setOpen] = useState(false);
  const [vFrom, setVFrom] = useState<string>("");
  const [vTo, setVTo] = useState<string>("");

  const versionsQuery = useQuery({
    queryKey: ["av-versions", contractId, configId],
    queryFn: () => getAvailabilityVersions(contractId, configId),
    enabled: open && Boolean(contractId && configId),
  });

  const versions = useMemo(() => versionsQuery.data ?? [], [versionsQuery.data]);

  useEffect(() => {
    if (versions.length >= 2 && !vFrom && !vTo) {
      setVTo(versions[0].id);
      setVFrom(versions[1].id);
    } else if (versions.length === 1 && !vTo) {
      setVTo(versions[0].id);
      setVFrom(versions[0].id);
    }
  }, [versions, vFrom, vTo]);

  const diffQuery = useQuery({
    queryKey: ["av-diff", contractId, configId, vFrom, vTo],
    queryFn: () => getAvailabilityDiff(contractId, configId, vFrom, vTo),
    enabled: open && Boolean(vFrom && vTo),
  });

  const diff = diffQuery.data;
  const hasChanges =
    diff &&
    (Object.keys(diff.basic_details_changes).length > 0 ||
      diff.added_turbines.length > 0 ||
      diff.removed_turbines.length > 0 ||
      diff.formula_change !== null ||
      diff.added_alarms.length > 0 ||
      diff.removed_alarms.length > 0 ||
      diff.alarm_assignment_changes.length > 0 ||
      Object.keys(diff.details_changes).length > 0);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button type="button" variant="outline" size="sm">
          <History className="mr-1.5 h-4 w-4" />
          Version history & diff
        </Button>
      </DialogTrigger>
      <DialogContent className="max-h-[85vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Version history & structural diff</DialogTitle>
          <DialogDescription>
            Every saved draft creates an immutable snapshot. Compare any two versions below.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="max-h-48 space-y-2 overflow-y-auto pr-1">
            {versions.map((ver) => (
              <div
                key={ver.id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-border bg-muted/30 px-3 py-2 text-xs"
              >
                <div className="flex items-center gap-2">
                  <span className="font-semibold">v{ver.version_number}</span>
                  <Badge variant="outline">{ver.status}</Badge>
                  <span className="text-muted-foreground">by {ver.created_by}</span>
                </div>
                <div className="flex items-center gap-3 text-muted-foreground">
                  <span>{format(new Date(ver.created_at), "yyyy-MM-dd HH:mm")}</span>
                  <span className="font-mono text-[10px]">{ver.checksum.slice(0, 10)}</span>
                </div>
              </div>
            ))}
          </div>

          {versions.length >= 1 && (
            <>
              <Separator />
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="space-y-1.5">
                  <Label className="text-xs">Compare from</Label>
                  <Select value={vFrom} onValueChange={setVFrom}>
                    <SelectTrigger className="h-8 text-xs">
                      <SelectValue placeholder="Select base version" />
                    </SelectTrigger>
                    <SelectContent>
                      {versions.map((ver) => (
                        <SelectItem key={ver.id} value={ver.id} className="text-xs">
                          v{ver.version_number} ({ver.status})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-1.5">
                  <Label className="text-xs">Compare to</Label>
                  <Select value={vTo} onValueChange={setVTo}>
                    <SelectTrigger className="h-8 text-xs">
                      <SelectValue placeholder="Select target version" />
                    </SelectTrigger>
                    <SelectContent>
                      {versions.map((ver) => (
                        <SelectItem key={ver.id} value={ver.id} className="text-xs">
                          v{ver.version_number} ({ver.status})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {diff && (
                <div className="space-y-2 rounded-md border border-border bg-muted/20 p-3.5 text-xs">
                  <div className="font-semibold text-foreground">
                    Diff: v{diff.v_from_number} → v{diff.v_to_number}
                  </div>
                  {!hasChanges ? (
                    <p className="text-muted-foreground">No differences between these versions.</p>
                  ) : (
                    <div className="space-y-1.5 text-muted-foreground">
                      {Object.entries(diff.basic_details_changes).map(([field, ch]) => (
                        <div key={field}>
                          <span className="font-medium text-foreground">basic_details.{field}:</span>{" "}
                          {String(ch.from ?? "null")} → {String(ch.to ?? "null")}
                        </div>
                      ))}
                      {diff.added_turbines.length > 0 && (
                        <div className="text-emerald-700">
                          + Added turbines: {diff.added_turbines.length}
                        </div>
                      )}
                      {diff.removed_turbines.length > 0 && (
                        <div className="text-rose-700">
                          - Removed turbines: {diff.removed_turbines.length}
                        </div>
                      )}
                      {diff.formula_change && (
                        <div>
                          <span className="font-medium text-foreground">formula_code:</span>{" "}
                          {diff.formula_change.from ?? "null"} → {diff.formula_change.to ?? "null"}
                        </div>
                      )}
                      {diff.added_alarms.length > 0 && (
                        <div className="text-emerald-700">
                          + Added alarms: {diff.added_alarms.length}
                        </div>
                      )}
                      {diff.removed_alarms.length > 0 && (
                        <div className="text-rose-700">
                          - Removed alarms: {diff.removed_alarms.length}
                        </div>
                      )}
                      {diff.alarm_assignment_changes.length > 0 && (
                        <div>
                          Modified turbine assignments on {diff.alarm_assignment_changes.length}{" "}
                          alarm(s)
                        </div>
                      )}
                      {Object.entries(diff.details_changes).map(([field, ch]) => (
                        <div key={field}>
                          <span className="font-medium text-foreground">details.{field}:</span>{" "}
                          {String(ch.from ?? "null")} → {String(ch.to ?? "null")}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
