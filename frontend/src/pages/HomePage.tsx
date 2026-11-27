import { useQuery } from "@tanstack/react-query";
import { AlertCircle } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ContractCard } from "@/features/contracts/ContractCard";
import { getContracts } from "@/lib/api";

export function HomePage() {
  const contractsQuery = useQuery({
    queryKey: ["contracts"],
    queryFn: getContracts,
  });

  if (contractsQuery.isLoading) {
    return (
      <section className="space-y-6">
        <HomeHeader />
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, idx) => (
            <Card key={idx} className="space-y-4 p-5">
              <CardHeader className="p-0">
                <div className="flex items-center gap-3">
                  <Skeleton className="h-10 w-10 rounded-md" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-3 w-1/3" />
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3 p-0">
                <Skeleton className="h-3 w-full" />
                <Skeleton className="h-3 w-5/6" />
                <Skeleton className="h-3 w-2/3" />
                <Skeleton className="h-24 w-full rounded-md" />
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    );
  }

  if (contractsQuery.isError) {
    return (
      <section className="space-y-6">
        <HomeHeader />
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Backend API Unavailable</AlertTitle>
          <AlertDescription>
            Could not load the contract portfolio. Verify the backend container is running and
            refresh the page.
          </AlertDescription>
        </Alert>
      </section>
    );
  }

  const contracts = contractsQuery.data ?? [];

  return (
    <section className="space-y-6">
      <HomeHeader />
      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {contracts.map((contract) => (
          <ContractCard key={contract.id} contract={contract} />
        ))}
      </div>
    </section>
  );
}

function HomeHeader() {
  return (
    <div className="rounded-lg border border-border bg-card p-6">
      <p className="text-sm font-semibold text-primary">Synthetic operations portfolio</p>
      <h1 className="mt-1.5 text-xl font-semibold text-foreground">
        Wind farm contracts & availability configurations
      </h1>
      <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
        Browse active and expired service agreements, inspect fleet sizes, and create or manage
        versioned availability configurations.
      </p>
    </div>
  );
}
