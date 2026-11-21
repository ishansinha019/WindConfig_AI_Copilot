import { Activity, Bot, CheckCircle2, Database, Wind } from "lucide-react";

import { HealthStatus } from "./components/HealthStatus";
import { DashboardPage } from "./pages/DashboardPage";

const milestones = [
  "Project setup",
  "Backend foundation",
  "Database and seed data",
  "Configuration wizard",
  "Local AI assistant",
];

export function App() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <section className="border-b border-border bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-6 px-6 py-8 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-3xl">
            <div className="mb-4 flex items-center gap-3 text-sm font-semibold text-primary">
              <Wind className="h-5 w-5" aria-hidden="true" />
              WindConfig AI Copilot
            </div>
            <h1 className="text-4xl font-semibold tracking-normal text-slate-950">
              Local AI support for wind farm contract configuration
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-slate-600">
              A resume-ready enterprise workflow for contracts, turbines, availability rules,
              draft saves, publishing, and practical local AI assistance.
            </p>
          </div>
          <HealthStatus />
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-6 px-6 py-8 lg:grid-cols-[1fr_320px]">
        <DashboardPage />

        <aside className="space-y-4">
          <div className="rounded-lg border border-border bg-white p-4">
            <div className="flex items-center gap-2 font-semibold text-slate-950">
              <CheckCircle2 className="h-5 w-5 text-emerald-600" aria-hidden="true" />
              Milestone path
            </div>
            <div className="mt-4 space-y-3">
              {milestones.map((milestone, index) => (
                <div key={milestone} className="flex items-center gap-3 text-sm text-slate-600">
                  <span className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-100 text-xs font-semibold text-slate-700">
                    {index + 1}
                  </span>
                  {milestone}
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-lg border border-border bg-white p-4">
            <div className="flex items-center gap-2 font-semibold text-slate-950">
              <Bot className="h-5 w-5 text-cyan-700" aria-hidden="true" />
              AI arrives later
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              Milestone 1 keeps the app simple. Ollama, Chroma, and local embeddings will be
              integrated after the contract workflow is useful without AI.
            </p>
          </div>

          <div className="rounded-lg border border-border bg-white p-4">
            <div className="flex items-center gap-2 font-semibold text-slate-950">
              <Database className="h-5 w-5 text-indigo-700" aria-hidden="true" />
              Local data only
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              The project will use synthetic wind-domain data and run locally without paid API
              keys or cloud services.
            </p>
          </div>

          <div className="rounded-lg border border-border bg-white p-4">
            <div className="flex items-center gap-2 font-semibold text-slate-950">
              <Activity className="h-5 w-5 text-rose-700" aria-hidden="true" />
              Backend first signal
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              The health check verifies the frontend can communicate with the FastAPI service.
            </p>
          </div>
        </aside>
      </section>
    </main>
  );
}
