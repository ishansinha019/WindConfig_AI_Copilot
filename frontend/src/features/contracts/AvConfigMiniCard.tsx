import { format } from "date-fns";
import { MoreVertical, Pencil, Trash2 } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import type { AvailabilityConfigSummary } from "@/lib/api";

type AvConfigMiniCardProps = {
  contractId: string;
  config: AvailabilityConfigSummary;
  onRequestDelete: (config: AvailabilityConfigSummary) => void;
};

function formatDate(iso: string): string {
  try {
    return format(new Date(iso), "yyyy-MM-dd");
  } catch {
    return iso.slice(0, 10);
  }
}

export function AvConfigMiniCard({
  contractId,
  config,
  onRequestDelete,
}: AvConfigMiniCardProps) {
  const navigate = useNavigate();
  const wizardPath = `/contracts/${contractId}/configurations/${config.id}`;
  const isPublished = config.status === "published";
  const dateRange =
    config.start_date && config.end_date
      ? `${config.start_date} to ${config.end_date}`
      : "Dates not set";

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => navigate(wizardPath)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          navigate(wizardPath);
        }
      }}
      className="group cursor-pointer rounded-md border border-border bg-muted/30 p-3.5 text-left transition hover:border-primary/60 hover:bg-muted/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <h4 className="truncate text-sm font-semibold text-foreground">{config.name}</h4>
          <div className="mt-1.5 flex flex-wrap items-center gap-2 text-xs">
            <Badge
              variant="outline"
              className={
                isPublished
                  ? "border-emerald-200 bg-emerald-50 text-emerald-800"
                  : "border-amber-200 bg-amber-50 text-amber-800"
              }
            >
              {isPublished ? "Published" : "Draft"}
            </Badge>
            {config.has_unpublished_draft && (
              <Badge variant="outline" className="border-blue-200 bg-blue-50 text-blue-800">
                Unpublished draft
              </Badge>
            )}
            <span className="text-muted-foreground">| {dateRange}</span>
          </div>
        </div>

        <div onClick={(e) => e.stopPropagation()} onKeyDown={(e) => e.stopPropagation()}>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="h-7 w-7 shrink-0 text-muted-foreground hover:text-foreground"
                aria-label={`Actions for ${config.name}`}
              >
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => navigate(wizardPath)}>
                <Pencil className="mr-2 h-3.5 w-3.5" />
                Edit
              </DropdownMenuItem>
              {isPublished ? (
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <div>
                        <DropdownMenuItem
                          disabled
                          className="cursor-not-allowed text-muted-foreground"
                        >
                          <Trash2 className="mr-2 h-3.5 w-3.5" />
                          Delete
                        </DropdownMenuItem>
                      </div>
                    </TooltipTrigger>
                    <TooltipContent>
                      Published configurations cannot be deleted.
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              ) : (
                <DropdownMenuItem
                  className="text-destructive focus:text-destructive"
                  onClick={() => onRequestDelete(config)}
                >
                  <Trash2 className="mr-2 h-3.5 w-3.5" />
                  Delete
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <div className="mt-3 space-y-0.5 text-[11px] text-muted-foreground">
        <p className="truncate">
          Created on {formatDate(config.created_at)} by{" "}
          <span className="font-medium text-foreground/80">{config.created_by}</span>
        </p>
        <p className="truncate">
          Last updated on {formatDate(config.updated_at)} by{" "}
          <span className="font-medium text-foreground/80">{config.updated_by}</span>
        </p>
      </div>
    </div>
  );
}
