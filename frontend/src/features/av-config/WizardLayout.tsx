import type { ReactNode } from "react";
import { CheckCircle2, ChevronLeft, ChevronRight, Save } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export const WIZARD_STEPS = [
  { number: 1, title: "Basic details", subtitle: "Name, calc type, dates" },
  { number: 2, title: "Turbines", subtitle: "Fleet scope selection" },
  { number: 3, title: "Formula & alarms", subtitle: "Formula & alarm tree" },
  { number: 4, title: "Details", subtitle: "SLA & wind variants" },
] as const;

type WizardLayoutProps = {
  currentStep: number;
  completedSteps: Record<number, boolean>;
  isDirty: boolean;
  isSaving: boolean;
  onStepChange: (step: number) => void;
  onSaveDraft: () => void;
  children: ReactNode;
};

export function WizardLayout({
  currentStep,
  completedSteps,
  isDirty,
  isSaving,
  onStepChange,
  onSaveDraft,
  children,
}: WizardLayoutProps) {
  return (
    <div className="grid gap-6 lg:grid-cols-[260px_1fr]">
      {/* Left step navigation */}
      <aside className="space-y-2">
        <nav aria-label="Wizard steps" className="space-y-1.5">
          {WIZARD_STEPS.map((step) => {
            const active = step.number === currentStep;
            const complete = Boolean(completedSteps[step.number]);
            return (
              <button
                key={step.number}
                type="button"
                onClick={() => onStepChange(step.number)}
                className={cn(
                  "flex w-full items-center gap-3 rounded-lg border px-3.5 py-3 text-left transition",
                  active
                    ? "border-primary bg-primary/5 text-foreground shadow-sm"
                    : "border-border bg-card text-muted-foreground hover:border-primary/40 hover:text-foreground",
                )}
              >
                <span
                  className={cn(
                    "flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold",
                    complete
                      ? "bg-emerald-100 text-emerald-800"
                      : active
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground",
                  )}
                >
                  {complete ? <CheckCircle2 className="h-4 w-4" /> : step.number}
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-sm font-semibold">{step.title}</span>
                  <span className="block truncate text-xs text-muted-foreground">
                    {step.subtitle}
                  </span>
                </span>
              </button>
            );
          })}
        </nav>
      </aside>

      {/* Main step card + sticky footer */}
      <div className="flex flex-col justify-between space-y-6">
        <Card>
          <CardContent className="p-6">{children}</CardContent>
        </Card>

        <div className="sticky bottom-4 z-10 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-border bg-card/95 px-5 py-3.5 shadow-md backdrop-blur">
          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={currentStep <= 1}
              onClick={() => onStepChange(currentStep - 1)}
            >
              <ChevronLeft className="mr-1 h-4 w-4" />
              Back
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={currentStep >= 4}
              onClick={() => onStepChange(currentStep + 1)}
            >
              Next
              <ChevronRight className="ml-1 h-4 w-4" />
            </Button>
          </div>

          <div className="flex items-center gap-3">
            {isDirty && (
              <Badge variant="outline" className="border-amber-200 bg-amber-50 text-amber-800">
                Unsaved changes
              </Badge>
            )}
            <Button type="button" size="sm" disabled={isSaving} onClick={onSaveDraft}>
              <Save className="mr-1.5 h-4 w-4" />
              {isSaving ? "Saving..." : "Save draft"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
