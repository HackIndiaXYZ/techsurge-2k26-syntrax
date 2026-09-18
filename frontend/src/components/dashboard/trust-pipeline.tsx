import { cn } from "@/lib/utils";
import { CheckCircle2, AlertCircle, Clock, XCircle, CloudRain, ShieldCheck, Cpu, PlaySquare, Wallet } from "lucide-react";

interface TrustPipelineProps {
  stages: {
    telemetry: "PENDING" | "ACTIVE" | "COMPLETED" | "FAILED";
    validation: "PENDING" | "ACTIVE" | "COMPLETED" | "FAILED";
    consensus: "PENDING" | "ACTIVE" | "COMPLETED" | "FAILED" | "BLOCKED";
    policy: "PENDING" | "ACTIVE" | "COMPLETED" | "FAILED" | "BLOCKED";
    settlement: "PENDING" | "ACTIVE" | "COMPLETED" | "FAILED" | "BLOCKED";
    wallet: "PENDING" | "ACTIVE" | "COMPLETED" | "FAILED" | "BLOCKED";
  };
}

export function TrustPipeline({ stages }: TrustPipelineProps) {
  const steps = [
    { id: "telemetry", label: "Weather Sources", sub: "Collect Data", icon: CloudRain, status: stages.telemetry },
    { id: "validation", label: "Validation", sub: "Check Consistency", icon: ShieldCheck, status: stages.validation },
    { id: "consensus", label: "Consensus", sub: "2/3 Sources", icon: Cpu, status: stages.consensus },
    { id: "policy", label: "Policy Evaluation", sub: "Check Threshold", icon: PlaySquare, status: stages.policy },
    { id: "settlement", label: "Settlement", sub: "Auto Payout", icon: Wallet, status: stages.settlement },
  ];

  return (
    <div className="w-full relative py-2">
      <div className="flex items-center justify-between relative max-w-3xl mx-auto">
        <div className="absolute left-[5%] right-[5%] top-5 h-px bg-border/50 z-0" />
        
        {steps.map((step, idx) => {
          let colorClass = "text-muted-foreground bg-background border-border/50";
          let iconColor = "text-muted-foreground";
          
          if (step.status === "COMPLETED") {
            colorClass = "bg-background border-emerald-500/50 shadow-[0_0_10px_rgba(16,185,129,0.1)]";
            iconColor = "text-emerald-400";
          } else if (step.status === "ACTIVE") {
            colorClass = "bg-background border-amber-500/50";
            iconColor = "text-amber-400 animate-pulse";
          } else if (step.status === "FAILED" || step.status === "BLOCKED") {
            colorClass = "bg-background border-destructive/50";
            iconColor = "text-destructive";
          }

          const hasLine = idx < steps.length - 1;
          const lineActive = step.status === "COMPLETED";

          return (
            <div key={step.id} className="relative z-10 flex flex-col items-center gap-3 w-1/5">
              <div className={cn("h-10 w-10 rounded-full flex items-center justify-center border", colorClass)}>
                <step.icon className={cn("h-4 w-4", iconColor)} />
              </div>
              <div className="text-center">
                <p className={cn("text-xs font-semibold whitespace-nowrap", step.status !== "PENDING" ? "text-foreground" : "text-muted-foreground")}>{step.label}</p>
                <p className="text-[10px] text-muted-foreground whitespace-nowrap">{step.sub}</p>
              </div>

              {hasLine && (
                <div className={cn(
                  "absolute top-5 left-[50%] w-full h-px -z-10 transition-colors",
                  lineActive ? "bg-emerald-500/50" : "bg-transparent"
                )} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
