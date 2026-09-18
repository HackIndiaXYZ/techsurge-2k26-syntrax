"use client";

import { useEffect, useState, Suspense } from "react";
import { useParams, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Volume2 } from "lucide-react";
import { ApiClient } from "@/lib/api/client";
import { DashboardData, formatPaise, AiLanguage, ScenarioId } from "@/lib/types";
import { cn } from "@/lib/utils";

function EventEvidenceContent() {
  const params = useParams();
  const searchParams = useSearchParams();
  const eventId = params.eventId as string;
  const scenario = (searchParams.get("scenario") as ScenarioId) || "normal";
  
  const [data, setData] = useState<DashboardData | null>(null);
  const [aiLang, setAiLang] = useState<AiLanguage>("en");
  const [activeTab, setActiveTab] = useState("timeline");

  useEffect(() => {
    ApiClient.getDashboard(scenario).then(setData).catch(console.error);
  }, [scenario]);

  if (!data) return <div className="p-8 text-muted-foreground animate-pulse">Loading event evidence...</div>;

  const isTriggered = data.trigger.state === "TRIGGERED";

  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-5xl">
      <Link href="/events" className="inline-flex items-center text-xs text-muted-foreground hover:text-foreground transition-colors mb-2">
        <ArrowLeft className="h-3 w-3 mr-1.5" /> Back to Events
      </Link>

      <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 pb-6 border-b border-border/50">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-3">
            Event {eventId}
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            {new Date(data.trigger.evaluated_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}, {new Date(data.trigger.evaluated_at).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>
        
        {isTriggered && (
          <div className="flex flex-col items-end">
            <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[10px] uppercase font-bold tracking-wider mb-2">
              Settled
            </Badge>
            <p className="text-2xl font-bold text-emerald-400">{formatPaise(data.settlement.payout_amount_paise)}</p>
            <p className="text-[10px] text-muted-foreground">Simulated Payout</p>
          </div>
        )}
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        <div className="md:col-span-2 space-y-6">
          <div className="flex items-center gap-2 border-b border-border/50">
            {["timeline", "weather", "policy", "audit"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={cn(
                  "px-4 py-2 text-xs font-medium border-b-2 transition-colors",
                  activeTab === tab 
                    ? "border-emerald-500 text-foreground" 
                    : "border-transparent text-muted-foreground hover:text-foreground"
                )}
              >
                {tab === "timeline" ? "Timeline" : 
                 tab === "weather" ? "Weather Data" : 
                 tab === "policy" ? "Policy Evaluation" : "Audit Logs"}
              </button>
            ))}
          </div>
          
          {activeTab === "timeline" && (
            <div className="space-y-6 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px before:h-full before:w-px before:bg-border/50 py-2">
              {data.audit.map((log) => {
                const isSuccess = !log.type.includes("FAILED") && !log.type.includes("REJECTED") && !log.type.includes("NOT_MET");
                const isAlert = log.type.includes("REJECTED") || log.type.includes("DUPLICATE");
                return (
                  <div key={log.id} className="relative flex items-start gap-4 pl-8 group">
                    <div className={cn(
                      "absolute left-0 w-4 h-4 rounded-full border-2 border-background shadow-sm mt-0.5",
                      isSuccess ? "bg-emerald-500" : isAlert ? "bg-amber-500" : "bg-destructive"
                    )} />
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <time className="text-[10px] text-muted-foreground font-mono w-14 shrink-0">
                          {new Date(log.timestamp).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                        </time>
                        <h3 className="font-semibold text-xs text-foreground">{log.detail.split('.')[0]}</h3>
                      </div>
                      <p className="text-[10px] text-muted-foreground ml-16">{log.detail.substring(log.detail.indexOf('.') + 1).trim() || log.detail}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          )}

          {activeTab !== "timeline" && (
            <div className="p-8 text-center text-sm text-muted-foreground bg-card/30 rounded-lg border border-border/50">
              Content for {activeTab} available in full data export.
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div>
            <h3 className="font-semibold text-sm mb-4">AI Explanation</h3>
            
            <div className="flex gap-2 mb-4">
              <button onClick={() => setAiLang('en')} className={cn("px-3 py-1 text-[10px] font-bold uppercase tracking-wider rounded-sm transition-colors", aiLang === 'en' ? 'bg-emerald-500 text-background' : 'bg-muted/50 text-muted-foreground hover:text-foreground')}>English</button>
              <button onClick={() => setAiLang('hi')} className={cn("px-3 py-1 text-[10px] font-bold uppercase tracking-wider rounded-sm transition-colors", aiLang === 'hi' ? 'bg-emerald-500 text-background' : 'bg-muted/50 text-muted-foreground hover:text-foreground')}>हिंदी</button>
              <button onClick={() => setAiLang('te')} className={cn("px-3 py-1 text-[10px] font-bold uppercase tracking-wider rounded-sm transition-colors", aiLang === 'te' ? 'bg-emerald-500 text-background' : 'bg-muted/50 text-muted-foreground hover:text-foreground')}>తెలుగు</button>
            </div>
            
            <div className="space-y-4 text-xs text-muted-foreground leading-relaxed">
              <p className="font-semibold text-foreground">Why was this payout triggered?</p>
              <p>{data.ai_insight?.explanations[aiLang]}</p>
            </div>
            
            <Button className="w-full mt-6 bg-emerald-500 hover:bg-emerald-600 text-background gap-2 text-xs h-9 font-semibold">
              <Volume2 className="h-4 w-4" /> Listen (Text-to-Speech)
            </Button>
            
            <div className="text-center mt-4">
              <p className="text-[9px] text-muted-foreground">AI-generated advisory explanation.</p>
              <p className="text-[9px] text-muted-foreground">Settlement decisions are made by the system, not by AI.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function EventEvidencePage() {
  return <Suspense><EventEvidenceContent /></Suspense>;
}
