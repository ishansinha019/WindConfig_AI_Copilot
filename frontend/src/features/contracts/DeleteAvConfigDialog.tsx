import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { deleteAvailabilityConfiguration, type AvailabilityConfigSummary } from "@/lib/api";

type DeleteAvConfigDialogProps = {
  contractId: string;
  config: AvailabilityConfigSummary | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export function DeleteAvConfigDialog({
  contractId,
  config,
  open,
  onOpenChange,
}: DeleteAvConfigDialogProps) {
  const queryClient = useQueryClient();

  const deleteMutation = useMutation({
    mutationFn: () => deleteAvailabilityConfiguration(contractId, config?.id ?? ""),
    onSuccess: () => {
      toast.success(`Deleted "${config?.name ?? "configuration"}"`);
      onOpenChange(false);
      void queryClient.invalidateQueries({ queryKey: ["contracts"] });
      void queryClient.invalidateQueries({ queryKey: ["contract", contractId] });
    },
    onError: (err: Error) => {
      toast.error(err.message);
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete availability configuration</DialogTitle>
          <DialogDescription>
            Are you sure you want to delete{" "}
            <span className="font-semibold text-foreground">{config?.name}</span>? This will
            permanently remove the configuration and all of its draft versions.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            disabled={deleteMutation.isPending}
            onClick={() => onOpenChange(false)}
          >
            Cancel
          </Button>
          <Button
            type="button"
            variant="destructive"
            disabled={deleteMutation.isPending || !config}
            onClick={() => deleteMutation.mutate()}
          >
            {deleteMutation.isPending ? "Deleting..." : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
