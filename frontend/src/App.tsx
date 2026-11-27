import { Link, Navigate, Route, Routes } from "react-router-dom";
import { Wind } from "lucide-react";

import { ActingUserPicker } from "./components/ActingUserPicker";
import { HealthStatus } from "./components/HealthStatus";
import { Toaster } from "./components/ui/sonner";
import { AvConfigWizardPage } from "./pages/AvConfigWizardPage";
import { ContractDetailPage } from "./pages/ContractDetailPage";
import { HomePage } from "./pages/HomePage";

export function App() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="border-b border-border bg-card">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
          <Link to="/" className="flex items-center gap-3 text-sm font-semibold text-primary">
            <span className="flex h-10 w-10 items-center justify-center rounded-md bg-muted">
              <Wind className="h-5 w-5" aria-hidden="true" />
            </span>
            <span>
              <span className="block text-base text-foreground">WindConfig</span>
              <span className="block text-xs font-normal text-muted-foreground">
                Wind farm contracts
              </span>
            </span>
          </Link>
          <div className="flex flex-wrap items-center gap-4">
            <ActingUserPicker />
            <HealthStatus />
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-7xl px-6 py-8">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/contracts/:contractId" element={<ContractDetailPage />} />
          <Route
            path="/contracts/:contractId/configurations/new"
            element={<AvConfigWizardPage />}
          />
          <Route
            path="/contracts/:contractId/configurations/:configId"
            element={<AvConfigWizardPage />}
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </section>
      <Toaster />
    </main>
  );
}
