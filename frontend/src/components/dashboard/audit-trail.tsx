"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { AuditEvent } from "@/lib/types";
import { ScrollText, CloudRain, CheckCircle2, XCircle, Zap, Banknote, Wallet, Bell, Copy, ShieldCheck } from "lucide-react";

function auditIcon(type: string) {
  switch (type) {
    case "TELEMETRY_RECEIVED":
    case "TELEMETRY_VALIDATED":
      return <CloudRain className="h-3.5 w-3.5 text-blue-500" />;
    case "TELEMETRY_REJECTED":
      return <XCircle className="h-3.5 w-3.5 text-red-500" />;
    case "CONSENSUS_ACHIEVED":
      return <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />;
    case "CONSENSUS_FAILED":
      return <XCircle className="h-3.5 w-3.5 text-red-500" />;
    case "POLICY_TRIGGERED":
      return <Zap className="h-3.5 w-3.5 text-amber-500" />;
    case "POLICY_NOT_MET":
      return <ShieldCheck className="h-3.5 w-3.5 text-muted-foreground" />;
    case "SETTLEMENT_INITIATED":
    case "SETTLEMENT_EXECUTED":
      return <Banknote className="h-3.5 w-3.5 text-emerald-500" />;
    case "SETTLEMENT_DUPLICATE":
      return <Copy className="h-3.5 w-3.5 text-purple-500" />;
    case "SETTLEMENT_FAILED":
      return <XCircle className="h-3.5 w-3.5 text-red-500" />;
    case "WALLET_CREDITED":
      return <Wallet className="h-3.5 w-3.5 text-violet-500" />;
    case "NOTIFICATION_SENT":
      return <Bell className="h-3.5 w-3.5 text-sky-500" />;
    default:
      return <ScrollText className="h-3.5 w-3.5 text-muted-foreground" />;
  }
}

function auditBadgeVariant(type: string) {
  if (type.includes("REJECTED") || type.includes("FAILED") || type === "CONSENSUS_FAILED") return "destructive" as const;
  if (type === "SETTLEMENT_DUPLICATE") return "secondary" as const;
  return "outline" as const;
}

export function AuditTrail({ events }: { events: AuditEvent[] }) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <ScrollText className="h-5 w-5 text-muted-foreground" />
          <CardTitle className="text-lg">Audit Trail</CardTitle>
        </div>
        <p className="text-xs text-muted-foreground">Immutable evidence chain · {events.length} events</p>
      </CardHeader>
      <CardContent>
        <div className="relative space-y-0 max-h-[420px] overflow-y-auto pr-2">
          {/* Vertical timeline line */}
          <div className="absolute left-[7px] top-2 bottom-2 w-px bg-border" />

          {events.map((event, i) => (
            <div key={event.id} className="relative flex gap-3 pb-4 last:pb-0">
              {/* Timeline dot */}
              <div className="relative z-10 mt-1.5 flex-shrink-0 h-4 w-4 rounded-full border-2 border-background bg-muted flex items-center justify-center">
                {auditIcon(event.type)}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant={auditBadgeVariant(event.type)} className="text-[10px] px-1.5 py-0">
                    {event.type.replace(/_/g, " ")}
                  </Badge>
                  <span className="text-[10px] text-muted-foreground">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-xs text-foreground mt-0.5">{event.detail}</p>
                <p className="text-[10px] text-muted-foreground font-mono mt-0.5">
                  {event.actor} · {event.correlation_id}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

