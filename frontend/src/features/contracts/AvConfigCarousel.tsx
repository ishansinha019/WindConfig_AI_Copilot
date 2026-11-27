import { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Plus } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import {
  Carousel,
  type CarouselApi,
  CarouselContent,
  CarouselItem,
} from "@/components/ui/carousel";
import type { AvailabilityConfigSummary } from "@/lib/api";
import { AvConfigMiniCard } from "./AvConfigMiniCard";

type AvConfigCarouselProps = {
  contractId: string;
  configs: AvailabilityConfigSummary[];
  onRequestDelete: (config: AvailabilityConfigSummary) => void;
};

export function AvConfigCarousel({
  contractId,
  configs,
  onRequestDelete,
}: AvConfigCarouselProps) {
  const [api, setApi] = useState<CarouselApi>();
  const [current, setCurrent] = useState(0);
  const [canPrev, setCanPrev] = useState(false);
  const [canNext, setCanNext] = useState(false);

  useEffect(() => {
    if (!api) return;

    const updateState = () => {
      setCurrent(api.selectedScrollSnap());
      setCanPrev(api.canScrollPrev());
      setCanNext(api.canScrollNext());
    };

    updateState();
    api.on("select", updateState);
    api.on("reInit", updateState);
    return () => {
      api.off("select", updateState);
      api.off("reInit", updateState);
    };
  }, [api]);

  if (configs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-md border border-dashed border-border bg-muted/20 px-4 py-6 text-center">
        <p className="text-xs text-muted-foreground">No availability configurations yet.</p>
        <Button asChild variant="outline" size="sm" className="mt-3 h-8 text-xs">
          <Link to={`/contracts/${contractId}/configurations/new`}>
            <Plus className="mr-1.5 h-3.5 w-3.5" />
            Create first configuration
          </Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-2.5">
      <Carousel setApi={setApi} opts={{ align: "start" }} className="w-full">
        <CarouselContent>
          {configs.map((config) => (
            <CarouselItem key={config.id}>
              <AvConfigMiniCard
                contractId={contractId}
                config={config}
                onRequestDelete={onRequestDelete}
              />
            </CarouselItem>
          ))}
        </CarouselContent>
      </Carousel>

      {configs.length > 1 && (
        <div className="flex items-center justify-between pt-0.5">
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="h-7 w-7"
            disabled={!canPrev}
            onClick={() => api?.scrollPrev()}
            aria-label="Previous configuration"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>

          {configs.length <= 10 ? (
            <div className="flex items-center gap-1.5" role="tablist" aria-label="Configuration slides">
              {configs.map((cfg, idx) => (
                <button
                  key={cfg.id}
                  type="button"
                  aria-label={`Go to configuration ${idx + 1}`}
                  aria-selected={idx === current}
                  onClick={() => api?.scrollTo(idx)}
                  className={`h-1.5 rounded-full transition-all ${
                    idx === current ? "w-4 bg-primary" : "w-1.5 bg-muted-foreground/30 hover:bg-muted-foreground/50"
                  }`}
                />
              ))}
            </div>
          ) : (
            <span className="text-xs font-medium text-muted-foreground">
              {current + 1} / {configs.length}
            </span>
          )}

          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="h-7 w-7"
            disabled={!canNext}
            onClick={() => api?.scrollNext()}
            aria-label="Next configuration"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
