"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { SCENARIOS, ScenarioId } from "@/lib/types";
import { cn } from "@/lib/utils";

export function ScenarioSwitcher() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const currentScenario = (searchParams.get("scenario") as ScenarioId) || "normal";

  const handleSwitch = (id: ScenarioId) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set("scenario", id);
    router.push(`${pathname}?${params.toString()}`);
  };

  return (
    <div className="flex flex-col space-y-3">
      <div className="text-[10px] font-bold text-foreground uppercase tracking-wider">
        Demo Scenarios <span className="text-muted-foreground font-normal normal-case">(Click to simulate)</span>
      </div>
      <div className="flex flex-wrap gap-3">
        {SCENARIOS.map((s) => {
          const isActive = currentScenario === s.id;
          return (
            <button
              key={s.id}
              onClick={() => handleSwitch(s.id)}
              className={cn(
                "px-4 py-2.5 rounded-md border text-xs font-medium transition-all text-left flex flex-col min-w-[140px] flex-1 md:flex-none",
                isActive 
                  ? "border-emerald-500/50 bg-emerald-500/10 text-foreground ring-1 ring-emerald-500/20" 
                  : "border-border/50 bg-background/50 text-foreground hover:bg-muted/50"
              )}
            >
              <span className="mb-0.5 whitespace-nowrap">{s.label}</span>
              <span className={cn("text-[10px] font-normal leading-tight", isActive ? "text-emerald-400" : "text-muted-foreground")}>
                ({s.description.split('.')[0]})
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
