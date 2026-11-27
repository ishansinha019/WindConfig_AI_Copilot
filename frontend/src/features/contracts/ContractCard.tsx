import { useState } from "react";
import {
  Briefcase,
  Calendar,
  FileText,
  Hash,
  Plus,
  Settings,
  Users,
  Wind,
} from "lucide-react";
import { Link } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import type { AvailabilityConfigSummary, ContractSummary } from "@/lib/api";
import { AvConfigCarousel } from "./AvConfigCarousel";
import { DeleteAvConfigDialog } from "./DeleteAvConfigDialog";

const ICON_ACCENTS = [
  "bg-sky-50 text-sky-700 border-sky-200",
  "bg-emerald-50 text-emerald-700 border-emerald-200",
  "bg-violet-50 text-violet-700 border-violet-200",
  "bg-amber-50 text-amber-700 border-amber-200",
  "bg-rose-50 text-rose-700 border-rose-200",
  "bg-teal-50 text-teal-700 border-teal-200",
];

function getIconAccent(seed: string): string {
  let hash = 0;
  for (let i = 0; i < seed.length; i += 1) {
    hash = (hash * 31 + seed.charCodeAt(i)) >>> 0;
  }
  return ICON_ACCENTS[hash % ICON_ACCENTS.length];
}

export function ContractCard({ contract }: { contract: ContractSummary }) {
  const [configToDelete, setConfigToDelete] = useState<AvailabilityConfigSummary | null>(null);
  const configs = contract.availability_configurations;
  const iconClass = getIconAccent(contract.order_reason || contract.id);

  return (
    <Card className="flex flex-col justify-between overflow-hidden">
      <CardHeader className="pb-3">
        <div className="flex items-start gap-3">
          <div
            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-md border ${iconClass}`}
          >
            <FileText className="h-5 w-5" aria-hidden="true" />
          </div>
          <div className="min-w-0 flex-1">
            <Link
              to={`/contracts/${contract.id}`}
              className="block truncate text-base font-semibold text-foreground hover:text-primary hover:underline"
              title={contract.name}
            >
              {contract.name}
            </Link>
            <p className="mt-0.5 text-xs text-muted-foreground">{contract.region}</p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex flex-1 flex-col space-y-4">
        <dl className="space-y-2 text-xs">
          <div className="flex items-start gap-2">
            <Briefcase className="mt-0.5 h-3.5 w-3.5 shrink-0 text-muted-foreground" aria-hidden="true" />
            <dt className="shrink-0 text-muted-foreground">Order reason:</dt>
            <dd className="font-medium text-foreground">{contract.order_reason}</dd>
          </div>

          <div className="flex items-center gap-2">
            <Hash className="h-3.5 w-3.5 shrink-0 text-muted-foreground" aria-hidden="true" />
            <dt className="shrink-0 text-muted-foreground">Sales document #:</dt>
            <dd className="font-mono font-medium text-foreground">{contract.sales_document_number}</dd>
          </div>

          <div className="flex items-start gap-2">
            <Wind className="mt-0.5 h-3.5 w-3.5 shrink-0 text-muted-foreground" aria-hidden="true" />
            <dt className="sr-only">Wind farm and turbines</dt>
            <dd className="text-foreground">
              <span className="text-muted-foreground">Windfarm </span>
              <span className="font-medium">{contract.wind_farm_name}</span>
              <span className="mx-1.5 text-muted-foreground">|</span>
              <span className="text-muted-foreground">turbines # </span>
              <span className="font-semibold">{contract.turbine_count}</span>
            </dd>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Calendar className="h-3.5 w-3.5 shrink-0 text-muted-foreground" aria-hidden="true" />
            <dt className="sr-only">Contract dates</dt>
            <dd className="flex flex-wrap items-center gap-2">
              <span className="font-medium text-foreground">
                {contract.start_date} to {contract.end_date}
              </span>
              <Badge
                variant="outline"
                className={
                  contract.is_live
                    ? "border-emerald-200 bg-emerald-50 text-emerald-800"
                    : "border-slate-200 bg-slate-100 text-slate-600"
                }
              >
                {contract.is_live ? "Live" : "Expired"}
              </Badge>
            </dd>
          </div>

          <div className="flex items-start gap-2">
            <Users className="mt-0.5 h-3.5 w-3.5 shrink-0 text-muted-foreground" aria-hidden="true" />
            <dt className="shrink-0 text-muted-foreground">Customer:</dt>
            <dd className="font-medium text-foreground">
              {contract.customer_names.length > 0
                ? contract.customer_names.join(" | ")
                : contract.customer_name}
            </dd>
          </div>
        </dl>

        <Separator />

        <div className="space-y-3">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-foreground">
                Availability Configuration
              </span>
              <Badge variant="secondary" className="gap-1 px-2 py-0.5 text-[11px] font-medium">
                <Settings className="h-3 w-3" aria-hidden="true" />
                {configs.length} {configs.length === 1 ? "Configuration" : "Configurations"}
              </Badge>
            </div>
            <Button
              asChild
              variant="outline"
              size="icon"
              className="h-7 w-7"
              aria-label={`New availability configuration for ${contract.name}`}
            >
              <Link to={`/contracts/${contract.id}/configurations/new`}>
                <Plus className="h-4 w-4" />
              </Link>
            </Button>
          </div>

          <AvConfigCarousel
            contractId={contract.id}
            configs={configs}
            onRequestDelete={(cfg) => setConfigToDelete(cfg)}
          />
        </div>
      </CardContent>

      <DeleteAvConfigDialog
        contractId={contract.id}
        config={configToDelete}
        open={configToDelete !== null}
        onOpenChange={(open) => {
          if (!open) setConfigToDelete(null);
        }}
      />
    </Card>
  );
}
