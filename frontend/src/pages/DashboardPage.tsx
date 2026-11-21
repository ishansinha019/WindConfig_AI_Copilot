import { CalendarClock, FileText, Gauge, Layers3 } from "lucide-react";

const cards = [
  {
    title: "Contract dashboard",
    description: "Milestone 4 will list wind farm contracts with draft and publish status.",
    icon: FileText,
  },
  {
    title: "Availability wizard",
    description: "Milestone 5 will add the four-step configuration flow.",
    icon: Layers3,
  },
  {
    title: "Draft snapshots",
    description: "Milestone 6 will persist draft JSON and compare versions.",
    icon: CalendarClock,
  },
  {
    title: "Publish readiness",
    description: "Milestone 7 will explain validation findings with local AI.",
    icon: Gauge,
  },
];

export function DashboardPage() {
  return (
    <section className="space-y-6">
      <div className="rounded-lg border border-border bg-white p-6">
        <h2 className="text-xl font-semibold text-slate-950">Milestone 1 app shell</h2>
        <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
          This first screen proves the frontend, backend, documentation, and local runtime shape
          are in place. Domain features will be added one milestone at a time so the project
          remains easy to learn and explain.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {cards.map((card) => {
          const Icon = card.icon;

          return (
            <article key={card.title} className="rounded-lg border border-border bg-white p-5">
              <div className="flex items-start gap-4">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-slate-100 text-primary">
                  <Icon className="h-5 w-5" aria-hidden="true" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-950">{card.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{card.description}</p>
                </div>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
