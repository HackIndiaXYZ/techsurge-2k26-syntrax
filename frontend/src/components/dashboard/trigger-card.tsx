"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { TriggerEvaluation } from "@/lib/types";
import { Zap, ArrowDown, CheckCircle2, XCircle, AlertTriangle } from "lucide-react";

function triggerBadge(state: string) {
  switch (state) {
    case "TRIGGERED":
      return <Badge className="bg-amber-600 text-white gap-1"><Zap className="h-3.5 w-3.5" />TRIGGERED</Badge>;
    case "NOT_MET":
      return <Badge variant="secondary" className="gap-1"><XCircle className="h-3.5 w-3.5" />NOT MET</Badge>;
    case "NO_CONSENSUS":
      return <Badge variant="destructive" className="gap-1"><XCircle className="h-3.5 w-3.5" />NO CONSENSUS</Badge>;
    case "ALREADY_TRIGGERED":
      return <Badge variant="secondary" className="gap-1 bg-blue-100 text-blue-700 border-blue-200"><CheckCircle2 className="h-3.5 w-3.5" />ALREADY TRIGGERED</Badge>;
    case "NOT_ELIGIBLE":
      return <Badge variant="secondary" className="gap-1"><AlertTriangle className="h-3.5 w-3.5" />NOT ELIGIBLE</Badge>;
    case "EXPIRED":
      return <Badge variant="secondary" className="gap-1">EXPIRED</Badge>;
    default:
      return <Badge variant="outline">{state}</Badge>;
  }
}

export function TriggerCard({ trigger }: { trigger: TriggerEvaluation }) {
  const isTriggered = trigger.state === "TRIGGERED";
  const hasValue = trigger.observed_value !== null;

  return (
    <Card className={isTriggered ? "border-amber-300 bg-amber-50/30 dark:border-amber-900 dark:bg-amber-950/20" : ""}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-amber-600" />
            <CardTitle className="text-lg">Trigger Evaluation</CardTitle>
          </div>
          {triggerBadge(trigger.state)}
        </div>
      </CardHeader>
      <CardContent>
        {hasValue ? (
          <div className="flex flex-col items-center py-4 space-y-2">
            {/* Visual comparison */}
            <div className="text-center">
              <p className="text-xs uppercase tracking-wider text-muted-foreground font-medium">Observed</p>
              <p className={`text-3xl font-bold ${isTriggered ? "text-amber-700 dark:text-amber-400" : ""}`}>
                {trigger.observed_value} mm
              </p>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <span className="text-xs">vs</span>
            </div>
            <div className="text-center">
              <p className="text-xs uppercase tracking-wider text-muted-foreground font-medium">Threshold</p>
              <p className="text-2xl font-semibold">{trigger.threshold} mm</p>
            </div>
            <ArrowDown className={`h-6 w-6 mt-2 ${isTriggered ? "text-amber-600" : "text-muted-foreground"}`} />
            <div className={`rounded-lg px-4 py-2 text-center font-semibold text-lg ${
              isTriggered
                ? "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300"
                : "bg-muted text-muted-foreground"
            }`}>
              {trigger.state === "TRIGGERED" ? "→ TRIGGERED" : trigger.state === "ALREADY_TRIGGERED" ? "→ ALREADY TRIGGERED" : `→ ${trigger.state.replace(/_/g, " ")}`}
            </div>
          </div>
        ) : (
          <div className="py-4 text-center">
            <XCircle className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">No trusted value available for comparison</p>
          </div>
        )}
        <p className="text-xs text-muted-foreground mt-3 border-t pt-3">{trigger.reason}</p>
      </CardContent>
    </Card>
  );
}

