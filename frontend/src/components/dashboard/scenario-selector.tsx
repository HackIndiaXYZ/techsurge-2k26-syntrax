"use client";

import { SCENARIOS } from "@/lib/types";
import type { ScenarioId } from "@/lib/types";
import { cn } from "@/lib/utils";
import { CheckCircle2, AlertTriangle, XCircle, Copy } from "lucide-react";

const SCENARIO_ICONS: Record<ScenarioId, React.ReactNode> = {
  normal: <CheckCircle2 className="h-4 w-4" />,
  "corrupted-source": <AlertTriangle className="h-4 w-4" />,
  "no-consensus": <XCircle className="h-4 w-4" />,
  "duplicate-settlement": <Copy className="h-4 w-4" />,
};

const SCENARIO_COLORS: Record<ScenarioId, string> = {
  normal: "border-emerald-300 bg-emerald-50 text-emerald-800 dark:border-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300",
  "corrupted-source": "border-amber-300 bg-amber-50 text-amber-800 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-300",
  "no-consensus": "border-red-300 bg-red-50 text-red-800 dark:border-red-700 dark:bg-red-950/40 dark:text-red-300",
  "duplicate-settlement": "border-purple-300 bg-purple-50 text-purple-800 dark:border-purple-700 dark:bg-purple-950/40 dark:text-purple-300",
};

export function ScenarioSelector({
  active,
  onChange,
}: {
  active: ScenarioId;
  onChange: (id: ScenarioId) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {SCENARIOS.map((s) => {
        const isActive = s.id === active;
        return (
          <button
            key={s.id}
            onClick={() => onChange(s.id)}
            className={cn(
              "flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium transition-all cursor-pointer",
              isActive
                ? SCENARIO_COLORS[s.id]
                : "border-border bg-card text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            )}
          >
            {SCENARIO_ICONS[s.id]}
            <span>{s.label}</span>
          </button>
        );
      })}
    </div>
  );
}

