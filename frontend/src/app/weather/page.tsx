"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, AlertCircle, XCircle } from "lucide-react";
import { ApiClient } from "@/lib/api/client";
import { DashboardData, ScenarioId } from "@/lib/types";
import { ScenarioSwitcher } from "@/components/scenario-switcher";
import { WeatherCharts } from "@/components/dashboard/weather-charts";

function WeatherContent() {
  const searchParams = useSearchParams();
  const scenario = (searchParams.get("scenario") as ScenarioId) || "normal";
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    ApiClient.getDashboard(scenario).then(setData).catch(console.error);
  }, [scenario]);

  if (!data) return <div className="p-8 text-muted-foreground animate-pulse">Loading weather intelligence...</div>;

  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-5xl">
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Live Weather Telemetry</h1>
          <p className="text-sm text-muted-foreground mt-1">Real-time data from multiple sources with validation and consensus.</p>
        </div>
        <div className="flex flex-col items-end">
          <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 gap-1.5 py-1 px-3">
            <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Live Data
          </Badge>
          <span className="text-[10px] text-muted-foreground mt-2 font-mono">
            Last updated: {new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {data.consensus.sources.map((source, idx) => (
          <Card key={source.id} className="bg-card/50 border-border/50 backdrop-blur-sm relative overflow-hidden">
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className="h-6 w-6 rounded-md bg-muted/50 flex items-center justify-center border border-border/50 text-[10px] font-bold text-muted-foreground">
                    {source.name.substring(0,1)}
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs font-bold text-foreground">Source {String.fromCharCode(65 + idx)}</span>
                    <span className="text-[10px] text-muted-foreground">({source.name})</span>
                  </div>
                </div>
              </div>
              <div className="text-3xl font-bold text-foreground mb-4">
                {source.metrics.rainfall_mm.toFixed(1)} <span className="text-sm font-normal text-muted-foreground">mm</span>
              </div>
              <div className="flex items-center gap-1.5">
                {source.validation_status === "VALID" ? (
                  <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[10px] font-bold gap-1 rounded-sm px-1.5 py-0">
                    <CheckCircle2 className="h-3 w-3" /> Valid
                  </Badge>
                ) : (
                  <Badge variant="outline" className="bg-destructive/10 text-destructive border-destructive/20 text-[10px] font-bold gap-1 rounded-sm px-1.5 py-0">
                    <XCircle className="h-3 w-3" /> Outlier
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-card/50 border-border/50 backdrop-blur-sm">
          <div className="px-6 py-4 border-b border-border/50">
            <h3 className="font-semibold text-sm">Consensus Engine</h3>
          </div>
          <CardContent className="p-6 flex items-center gap-6">
            <div className="h-24 w-24 rounded-full border-4 border-emerald-500/20 flex flex-col items-center justify-center shrink-0 relative">
              <div className="absolute inset-0 rounded-full border-4 border-emerald-500/60" style={{ clipPath: `polygon(0 0, 100% 0, 100% ${(data.consensus.agreeing_sources/data.consensus.total_sources)*100}%, 0 ${(data.consensus.agreeing_sources/data.consensus.total_sources)*100}%)` }} />
              <span className="text-2xl font-bold text-foreground leading-none">{data.consensus.agreeing_sources}/{data.consensus.total_sources}</span>
              <span className="text-[8px] text-muted-foreground uppercase mt-1">Sources</span>
            </div>
            <div className="space-y-3">
              <div className="inline-flex items-center gap-1.5 text-emerald-400 text-xs font-bold bg-emerald-500/10 px-2 py-1 rounded-sm">
                {data.consensus.agreeing_sources} out of {data.consensus.total_sources} sources agree
              </div>
              <div>
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-0.5">Trusted rainfall value</p>
                <p className="text-xl font-bold text-foreground">{data.consensus.value !== null ? data.consensus.value.toFixed(1) : "—"} <span className="text-sm font-normal text-muted-foreground">mm</span></p>
              </div>
              <div>
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-0.5">Tolerance</p>
                <p className="text-xs font-medium text-foreground">± 5 mm</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-card/50 border-border/50 backdrop-blur-sm">
          <div className="px-6 py-4 border-b border-border/50">
            <h3 className="font-semibold text-sm">Policy Evaluation</h3>
          </div>
          <CardContent className="p-6 flex flex-col items-center justify-center text-center h-[184px]">
            <p className="text-3xl font-bold text-foreground">{data.trigger.observed_value !== null ? data.trigger.observed_value.toFixed(1) : "—"} <span className="text-lg font-normal text-muted-foreground">mm</span></p>
            <p className="text-xs text-muted-foreground mt-1 mb-6">≥ {data.trigger.threshold} mm threshold</p>
            
            {data.trigger.state === "TRIGGERED" ? (
              <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-xs font-bold uppercase tracking-wider py-1.5 px-3 gap-2">
                <CheckCircle2 className="h-4 w-4" /> TRIGGER SATISFIED
              </Badge>
            ) : data.trigger.state === "NO_CONSENSUS" ? (
              <Badge variant="outline" className="bg-destructive/10 text-destructive border-destructive/20 text-xs font-bold uppercase tracking-wider py-1.5 px-3 gap-2">
                <AlertCircle className="h-4 w-4" /> NO CONSENSUS
              </Badge>
            ) : (
              <Badge variant="outline" className="bg-amber-500/10 text-amber-400 border-amber-500/20 text-xs font-bold uppercase tracking-wider py-1.5 px-3 gap-2">
                <AlertCircle className="h-4 w-4" /> {data.trigger.state.replace("_", " ")}
              </Badge>
            )}
            <p className="text-[10px] text-muted-foreground mt-2">{data.trigger.reason}</p>
          </CardContent>
        </Card>
      </div>
      
      <WeatherCharts data={data.history.rainfall} />

      <Card className="bg-card/50 border-border/50 backdrop-blur-sm">
        <CardContent className="p-6">
          <ScenarioSwitcher />
        </CardContent>
      </Card>
    </div>
  );
}

export default function WeatherPage() {
  return <Suspense><WeatherContent /></Suspense>;
}
