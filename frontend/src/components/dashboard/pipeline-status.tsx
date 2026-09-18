"use client";

import type { DashboardData } from "@/lib/types";
import { CloudRain, ShieldCheck, Users, Zap, Banknote, Wallet, ScrollText } from "lucide-react";
import { cn } from "@/lib/utils";

interface PipelineStep {
  icon: React.ReactNode;
  label: string;
  status: "complete" | "active" | "error" | "blocked" | "pending";
}

function getSteps(data: DashboardData): PipelineStep[] {
  const consensusOk = data.consensus.state === "ACHIEVED";
  const triggered = data.trigger.state === "TRIGGERED" || data.trigger.state === "ALREADY_TRIGGERED";
  const settled = data.settlement.status === "SETTLED" || data.settlement.status === "DUPLICATE";
  const walletCredited = data.wallet.balance_paise > 0;
  const noConsensus = data.consensus.state === "NO_CONSENSUS";

  return [
    {
      icon: <CloudRain className="h-4 w-4" />,
      label: "Weather",
      status: "complete",
    },
    {
      icon: <ShieldCheck className="h-4 w-4" />,
      label: "Validation",
      status: data.consensus.sources.some(s => s.validation_status === "OUTLIER" || s.validation_status === "SOURCE_DISAGREEMENT")
        ? "error"
        : "complete",
    },
    {
      icon: <Users className="h-4 w-4" />,
      label: "Consensus",
      status: consensusOk ? "complete" : noConsensus ? "error" : "pending",
    },
    {
      icon: <Zap className="h-4 w-4" />,
      label: "Trigger",
      status: triggered ? "complete" : noConsensus ? "blocked" : "pending",
    },
    {
      icon: <Banknote className="h-4 w-4" />,
      label: "Settlement",
      status: settled ? "complete" : data.settlement.status === "BLOCKED" ? "blocked" : "pending",
    },
    {
      icon: <Wallet className="h-4 w-4" />,
      label: "Wallet",
      status: walletCredited ? "complete" : data.settlement.status === "BLOCKED" ? "blocked" : "pending",
    },
    {
      icon: <ScrollText className="h-4 w-4" />,
      label: "Audit",
      status: data.audit.length > 0 ? "complete" : "pending",
    },
  ];
}

const STATUS_STYLES: Record<PipelineStep["status"], string> = {
  complete: "bg-emerald-100 text-emerald-700 border-emerald-300 dark:bg-emerald-900/40 dark:text-emerald-400 dark:border-emerald-700",
  active: "bg-blue-100 text-blue-700 border-blue-300 dark:bg-blue-900/40 dark:text-blue-400 dark:border-blue-700",
  error: "bg-amber-100 text-amber-700 border-amber-300 dark:bg-amber-900/40 dark:text-amber-400 dark:border-amber-700",
  blocked: "bg-red-100 text-red-500 border-red-300 dark:bg-red-900/40 dark:text-red-400 dark:border-red-700",
  pending: "bg-muted text-muted-foreground border-border",
};

const CONNECTOR_STYLES: Record<PipelineStep["status"], string> = {
  complete: "bg-emerald-400 dark:bg-emerald-600",
  active: "bg-blue-400 dark:bg-blue-600",
  error: "bg-amber-400 dark:bg-amber-600",
  blocked: "bg-red-300 dark:bg-red-700",
  pending: "bg-border",
};

export function PipelineStatus({ data }: { data: DashboardData }) {
  const steps = getSteps(data);

  return (
    <div className="flex items-center gap-0 overflow-x-auto pb-2">
      {steps.map((step, i) => (
        <div key={step.label} className="flex items-center">
          <div
            className={cn(
              "flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium whitespace-nowrap",
              STATUS_STYLES[step.status]
            )}
          >
            {step.icon}
            {step.label}
          </div>
          {i < steps.length - 1 && (
            <div className={cn("h-0.5 w-4 flex-shrink-0", CONNECTOR_STYLES[steps[i + 1].status])} />
          )}
        </div>
      ))}
    </div>
  );
}

