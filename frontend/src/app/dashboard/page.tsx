"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CloudRain, Activity, CheckCircle2, AlertCircle, Clock } from "lucide-react";
import { TrustPipeline } from "@/components/dashboard/trust-pipeline";
import { ApiClient } from "@/lib/api/client";
import { DashboardData, formatPaise, ScenarioId } from "@/lib/types";

function DashboardContent() {
  const searchParams = useSearchParams();
  const scenario = (searchParams.get("scenario") as ScenarioId) || "normal";
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    ApiClient.getDashboard(scenario).then(setData).catch(console.error);
  }, [scenario]);

  if (!data) return <div className="p-8 text-muted-foreground animate-pulse">Loading dashboard...</div>;

  const getPipelineStages = () => {
    if (data.scenario === "no-consensus") {
      return { telemetry: "COMPLETED", validation: "COMPLETED", consensus: "BLOCKED", policy: "BLOCKED", settlement: "BLOCKED", wallet: "BLOCKED" } as const;
    }
    return { telemetry: "COMPLETED", validation: "COMPLETED", consensus: "COMPLETED", policy: "COMPLETED", settlement: "COMPLETED", wallet: "COMPLETED" } as const;
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-5xl">
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            Good morning, Sanju <span className="text-xl">👋</span>
          </h1>
          <p className="text-sm text-muted-foreground mt-1">Here&apos;s your climate protection status today.</p>
        </div>
        <div className="flex flex-col items-end">
          <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 gap-1.5 py-1 px-3">
            <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            System Operational
          </Badge>
          <span className="text-xs text-muted-foreground mt-2 font-mono">
            {new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })} {new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
      </div>

      <Card className="bg-card/50 border-border/50 backdrop-blur-sm overflow-hidden">
        <CardContent className="p-0">
          <div className="p-6 border-b border-border/50">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-blue-500/10 text-blue-400 rounded-xl border border-blue-500/20">
                  <CloudRain className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Active Protection</p>
                  <h2 className="text-lg font-bold text-foreground">Rainfall Index Insurance</h2>
                  <p className="text-xs text-muted-foreground">Policy: {data.policy.id} | {data.policy.region_name}</p>
                </div>
              </div>
              
              <div className="flex gap-8 px-6 md:px-0">
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Coverage</p>
                  <p className="text-xl font-bold text-emerald-400">{formatPaise(data.policy.payout_amount_paise)}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Threshold</p>
                  <p className="text-xl font-bold text-foreground">≥ {data.policy.threshold} mm <span className="text-xs font-normal text-muted-foreground">/ {data.policy.window_minutes} min</span></p>
                </div>
              </div>
            </div>
          </div>

          <div className="px-6 py-8">
            <TrustPipeline stages={getPipelineStages()} />
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 divide-x divide-y md:divide-y-0 divide-border/50 border-t border-border/50 bg-background/30">
            <div className="p-6">
              <p className="text-3xl font-bold text-foreground">{data.consensus.value !== null ? data.consensus.value.toFixed(1) : "—"} <span className="text-sm font-normal text-muted-foreground">mm</span></p>
              <p className="text-xs text-muted-foreground mt-1 mb-3">Trusted Rainfall</p>
              <div className="inline-flex items-center gap-1.5 text-emerald-400 text-xs font-medium bg-emerald-500/10 px-2 py-1 rounded-md border border-emerald-500/20">
                <CheckCircle2 className="h-3.5 w-3.5" />
                {data.consensus.agreeing_sources}/{data.consensus.quorum_required} Sources Agree
              </div>
            </div>
            
            <div className="p-6">
              <div className="flex items-center gap-2 mb-3">
                {data.trigger.state === "TRIGGERED" ? (
                  <div className="inline-flex items-center gap-1.5 text-emerald-400 text-xs font-bold uppercase tracking-wider">
                    <CheckCircle2 className="h-4 w-4" /> TRIGGER SATISFIED
                  </div>
                ) : (
                  <div className="inline-flex items-center gap-1.5 text-amber-400 text-xs font-bold uppercase tracking-wider">
                    <AlertCircle className="h-4 w-4" /> {data.trigger.state.replace("_", " ")}
                  </div>
                )}
              </div>
              <div className="space-y-1.5">
                <div className="text-xs flex justify-between">
                  <span className="text-muted-foreground">Threshold</span>
                  <span className="font-medium text-foreground">{data.trigger.threshold} mm</span>
                </div>
                <div className="text-xs flex justify-between">
                  <span className="text-muted-foreground">Observed</span>
                  <span className="font-medium text-foreground">{data.trigger.observed_value ?? "—"} mm</span>
                </div>
              </div>
            </div>

            <div className="p-6">
              <p className="text-3xl font-bold text-emerald-400">{formatPaise(data.settlement.payout_amount_paise)}</p>
              <p className="text-xs text-muted-foreground mt-1 mb-3">Simulated Payout</p>
              <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[10px] uppercase font-bold tracking-wider">
                <CheckCircle2 className="h-3 w-3 mr-1" /> SETTLED
              </Badge>
            </div>

            <div className="p-6">
              <p className="text-3xl font-bold text-foreground">~ 820 ms</p>
              <p className="text-xs text-muted-foreground mt-1 mb-3">Event → Settlement</p>
              <div className="inline-flex items-center gap-1.5 text-muted-foreground text-xs bg-muted/50 px-2 py-1 rounded-md border border-border/50">
                <Activity className="h-3.5 w-3.5" />
                System Latency
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid md:grid-cols-3 gap-6">
        <Card className="md:col-span-2 bg-card/50 border-border/50 backdrop-blur-sm">
          <div className="px-6 py-4 border-b border-border/50 flex flex-row items-center justify-between">
            <h3 className="font-semibold text-sm">Recent Events</h3>
            <span className="text-xs text-emerald-400 cursor-pointer hover:underline font-medium">View all →</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="text-[10px] text-muted-foreground uppercase tracking-wider bg-background/30 border-b border-border/50">
                <tr>
                  <th className="px-6 py-3 font-medium">Time</th>
                  <th className="px-6 py-3 font-medium">Event ID</th>
                  <th className="px-6 py-3 font-medium">Consensus</th>
                  <th className="px-6 py-3 font-medium">Decision</th>
                  <th className="px-6 py-3 font-medium text-right">Settlement</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/30">
                {data.event_list.map((evt) => (
                  <tr key={evt.id} className="hover:bg-muted/30 transition-colors">
                    <td className="px-6 py-3.5 font-mono text-muted-foreground">{new Date(evt.timestamp).toLocaleTimeString('en-GB', {hour: '2-digit', minute:'2-digit', second:'2-digit'})}</td>
                    <td className="px-6 py-3.5 font-medium text-foreground">{evt.id}</td>
                    <td className="px-6 py-3.5 text-muted-foreground">{evt.consensus_value ? `${evt.consensus_value} mm` : '—'}</td>
                    <td className="px-6 py-3.5">
                      <span className={evt.decision === "Triggered" ? "text-emerald-400 font-medium" : "text-muted-foreground"}>
                        {evt.decision}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 font-medium text-right text-foreground">{evt.settlement_amount > 0 ? formatPaise(evt.settlement_amount) : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card className="bg-card/50 border-border/50 backdrop-blur-sm">
          <div className="px-6 py-4 border-b border-border/50">
            <h3 className="font-semibold text-sm">System Health</h3>
          </div>
          <div className="p-6 space-y-4">
            {[
              { label: "Weather Source A", status: "Online", icon: CloudRain },
              { label: "Weather Source B", status: "Online", icon: CloudRain },
              { label: "Weather Source C", status: "Online", icon: CloudRain },
              { label: "Consensus Engine", status: "Ready", icon: Activity },
              { label: "Settlement Engine", status: "Ready", icon: CheckCircle2 },
              { label: "Synthetic Wallet", status: "Ready", icon: Clock },
              { label: "AI Explanation", status: "Ready", icon: Activity },
            ].map((sys) => (
              <div key={sys.label} className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground flex items-center gap-2">
                  <sys.icon className="h-3.5 w-3.5 opacity-50" />
                  {sys.label}
                </span>
                <div className="flex items-center gap-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                  <span className="font-medium text-emerald-400">{sys.status}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return <Suspense><DashboardContent /></Suspense>;
}
