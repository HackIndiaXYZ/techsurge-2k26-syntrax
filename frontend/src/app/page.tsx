"use client";

import { useEffect, useState, useCallback } from "react";
import type { DashboardData, ScenarioId } from "@/lib/types";
import { SCENARIOS } from "@/lib/types";

import { ScenarioSelector } from "@/components/dashboard/scenario-selector";
import { PipelineStatus } from "@/components/dashboard/pipeline-status";
import { PolicyCard } from "@/components/dashboard/policy-card";
import { ConsensusCard } from "@/components/dashboard/consensus-card";
import { TriggerCard } from "@/components/dashboard/trigger-card";
import { SettlementCard } from "@/components/dashboard/settlement-card";
import { WalletCard } from "@/components/dashboard/wallet-card";
import { AuditTrail } from "@/components/dashboard/audit-trail";
import { AiInsightCard } from "@/components/dashboard/ai-insight-card";

export default function Dashboard() {
  const [scenario, setScenario] = useState<ScenarioId>("normal");
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboard = useCallback(async (s: ScenarioId) => {
    try {
      const res = await fetch(`/api/dashboard?scenario=${s}`);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const json: DashboardData = await res.json();
      setData(json);
      setError(null);
    } catch (err) {
      console.error("Dashboard fetch failed:", err);
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial fetch + polling
  useEffect(() => {
    setLoading(true);
    fetchDashboard(scenario);
    const interval = setInterval(() => fetchDashboard(scenario), 1000);
    return () => clearInterval(interval);
  }, [scenario, fetchDashboard]);

  const handleScenarioChange = (id: ScenarioId) => {
    setScenario(id);
    setData(null);
    setLoading(true);
  };

  const activeScenario = SCENARIOS.find((s) => s.id === scenario);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-white/80 dark:bg-slate-950/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">
                <span className="text-primary">SYNTRAX</span>
              </h1>
              <p className="text-xs text-muted-foreground">
                Parametric Weather Insurance · Deterministic Settlement · Synthetic Demo
              </p>
            </div>
            <div className="text-right hidden sm:block">
              <p className="text-xs text-muted-foreground">PS-F03 · TechSurge 2026</p>
              <p className="text-[10px] text-muted-foreground">Team SYNTRAX</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Scenario Selector */}
        <section>
          <h2 className="text-sm font-medium text-muted-foreground mb-2">Demo Scenario</h2>
          <ScenarioSelector active={scenario} onChange={handleScenarioChange} />
          {activeScenario && (
            <p className="text-xs text-muted-foreground mt-2">{activeScenario.description}</p>
          )}
        </section>

        {/* Loading State */}
        {loading && !data && (
          <div className="flex items-center justify-center py-20">
            <div className="text-center space-y-3">
              <div className="h-8 w-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-sm text-muted-foreground">Loading dashboard data…</p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="rounded-lg border border-red-300 bg-red-50 dark:bg-red-950/30 p-4 text-center">
            <p className="font-medium text-red-700 dark:text-red-400">Failed to load dashboard</p>
            <p className="text-sm text-muted-foreground mt-1">{error}</p>
          </div>
        )}

        {/* Dashboard Content */}
        {data && (
          <>
            {/* Pipeline Status */}
            <section>
              <h2 className="text-sm font-medium text-muted-foreground mb-2">Lifecycle Pipeline</h2>
              <PipelineStatus data={data} />
            </section>

            {/* Main Grid */}
            <div className="grid gap-6 lg:grid-cols-3">
              {/* Left column: Policy + Trigger + Settlement + Wallet */}
              <div className="space-y-6">
                <PolicyCard policy={data.policy} />
                <TriggerCard trigger={data.trigger} />
                <SettlementCard settlement={data.settlement} />
                <WalletCard wallet={data.wallet} />
              </div>

              {/* Center column: Consensus (full width on center) */}
              <div className="lg:col-span-2 space-y-6">
                <ConsensusCard consensus={data.consensus} threshold={data.policy.threshold} />
                <AiInsightCard insight={data.ai_insight} />
                <AuditTrail events={data.audit} />
              </div>
            </div>

            {/* Basis Risk Disclosure */}
            <footer className="border-t pt-4 mt-8">
              <p className="text-xs text-muted-foreground text-center max-w-2xl mx-auto">
                <span className="font-semibold">Basis risk:</span> this prototype settles against the predefined weather index
                and does not individually assess actual physical loss. All data is synthetic. No real financial transactions are
                executed. SYNTRAX is a hackathon demonstration — not a production insurance platform.
              </p>
            </footer>
          </>
        )}
      </main>
    </div>
  );
}
