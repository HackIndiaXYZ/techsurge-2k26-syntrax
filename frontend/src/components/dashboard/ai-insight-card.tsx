"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AiInsight } from "@/lib/types";
import { Bot, Globe } from "lucide-react";

export function AiInsightCard({ insight }: { insight: AiInsight | null }) {
  if (!insight) return null;

  return (
    <Card className="border-sky-200 bg-sky-50/30 dark:border-sky-900 dark:bg-sky-950/20">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-sky-600" />
          <CardTitle className="text-lg">AI Insight</CardTitle>
          <span className="text-[10px] uppercase tracking-wider font-semibold text-sky-600 bg-sky-100 dark:bg-sky-950 dark:text-sky-400 px-2 py-0.5 rounded ml-auto">
            Mock
          </span>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm">{insight.explanations.en}</p>

        {insight.anomaly_explanation && (
          <div className="rounded-lg bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 p-3">
            <p className="text-xs font-medium text-amber-700 dark:text-amber-400 mb-1">Anomaly Explanation</p>
            <p className="text-xs text-muted-foreground">{insight.anomaly_explanation}</p>
          </div>
        )}

        {insight.explanations.hi && (
          <div className="rounded-lg bg-muted/50 border p-3">
            <div className="flex items-center gap-1.5 mb-1">
              <Globe className="h-3.5 w-3.5 text-muted-foreground" />
              <p className="text-xs font-medium text-muted-foreground">Local Language</p>
            </div>
            <p className="text-sm">{insight.explanations.hi}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

