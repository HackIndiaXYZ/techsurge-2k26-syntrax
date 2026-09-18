"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ChevronRight } from "lucide-react";
import { ApiClient } from "@/lib/api/client";
import { DashboardData, formatPaise, ScenarioId } from "@/lib/types";

function EventsContent() {
  const searchParams = useSearchParams();
  const scenario = (searchParams.get("scenario") as ScenarioId) || "normal";
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    ApiClient.getDashboard(scenario).then(setData).catch(console.error);
  }, [scenario]);

  if (!data) return <div className="p-8 text-muted-foreground animate-pulse">Loading events...</div>;

  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Climate Events</h1>
        <p className="text-sm text-muted-foreground mt-1">Audit log of all monitored weather events and decisions.</p>
      </div>

      <Card className="bg-card/50 border-border/50 backdrop-blur-sm">
        <div className="px-6 py-4 border-b border-border/50">
          <h3 className="font-semibold text-sm">Event History</h3>
        </div>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="text-[10px] text-muted-foreground uppercase tracking-wider bg-background/30 border-b border-border/50">
                <tr>
                  <th className="px-6 py-4 font-medium">Time</th>
                  <th className="px-6 py-4 font-medium">Event ID</th>
                  <th className="px-6 py-4 font-medium">Consensus</th>
                  <th className="px-6 py-4 font-medium">Decision</th>
                  <th className="px-6 py-4 font-medium">Settlement</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                  <th className="px-6 py-4"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/30">
                {data.event_list.map((evt) => (
                  <tr key={evt.id} className="hover:bg-muted/30 group transition-colors">
                    <td className="px-6 py-4 font-mono text-muted-foreground">{new Date(evt.timestamp).toLocaleString('en-GB', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', second: '2-digit' })}</td>
                    <td className="px-6 py-4 font-medium text-foreground">{evt.id}</td>
                    <td className="px-6 py-4 text-muted-foreground">{evt.consensus_value ? `${evt.consensus_value} mm` : '—'}</td>
                    <td className="px-6 py-4">
                      <span className={evt.decision === "Triggered" ? "text-emerald-400 font-medium" : "text-muted-foreground"}>
                        {evt.decision}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-medium text-foreground">{evt.settlement_amount > 0 ? formatPaise(evt.settlement_amount) : '—'}</td>
                    <td className="px-6 py-4">
                      {evt.status === "Settled" ? (
                        <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[10px] font-medium py-0 px-2 rounded-sm">Settled</Badge>
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link href={`/events/${evt.id}`}>
                        <div className="inline-flex items-center justify-center rounded-md h-7 w-7 hover:bg-muted text-muted-foreground group-hover:text-emerald-400 transition-colors">
                          <ChevronRight className="h-4 w-4" />
                        </div>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function EventsPage() {
  return <Suspense><EventsContent /></Suspense>;
}
