import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getAvailabilityConfiguration, getContract } from "@/lib/api";

export function AvConfigWizardPage() {
  const { contractId, configId } = useParams<{ contractId: string; configId?: string }>();
  const isNew = !configId;

  const contractQuery = useQuery({
    queryKey: ["contract", contractId],
    queryFn: () => getContract(contractId ?? ""),
    enabled: Boolean(contractId),
  });

  const configQuery = useQuery({
    queryKey: ["av-config", contractId, configId],
    queryFn: () => getAvailabilityConfiguration(contractId ?? "", configId ?? ""),
    enabled: Boolean(contractId && configId),
  });

  return (
    <section className="space-y-6">
      <div className="space-y-2">
        <Link to="/" className="text-sm font-medium text-primary hover:underline">
          ← All contracts
        </Link>
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-semibold text-foreground">
            {isNew
              ? "New Availability Configuration"
              : configQuery.data?.name ?? "Availability Configuration"}
          </h1>
          {configQuery.data && (
            <Badge variant="outline">
              v{configQuery.data.latest_version_number} &bull; {configQuery.data.status}
            </Badge>
          )}
        </div>
        {contractQuery.data && (
          <p className="text-sm text-muted-foreground">
            Contract: {contractQuery.data.name} ({contractQuery.data.wind_farm_name})
          </p>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">4-Step Configuration Wizard (Milestone A5–A6)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <p>
            {isNew
              ? "This route opens an empty wizard for creating a new availability configuration. Nothing is persisted until the first Save draft."
              : `Loaded configuration GUID: ${configId}.`}
          </p>
          {configQuery.data && (
            <pre className="max-h-80 overflow-auto rounded-md bg-muted p-4 text-xs text-foreground">
              {JSON.stringify(configQuery.data.latest_version.snapshot_data, null, 2)}
            </pre>
          )}
        </CardContent>
      </Card>
    </section>
  );
}
