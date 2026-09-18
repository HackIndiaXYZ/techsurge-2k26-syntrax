"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Policy } from "@/lib/types";
import { formatPaise } from "@/lib/types";
import { Shield, MapPin, Clock, Droplets } from "lucide-react";

function statusVariant(status: string) {
  switch (status) {
    case "ACTIVE": return "default" as const;
    case "TRIGGERED": return "default" as const;
    case "PAID": return "secondary" as const;
    case "EXPIRED":
    case "CANCELLED": return "destructive" as const;
    default: return "outline" as const;
  }
}

function statusColor(status: string) {
  switch (status) {
    case "ACTIVE": return "bg-emerald-500/10 text-emerald-700 border-emerald-200";
    case "TRIGGERED": return "bg-amber-500/10 text-amber-700 border-amber-200";
    case "PAID": return "bg-blue-500/10 text-blue-700 border-blue-200";
    default: return "";
  }
}

export function PolicyCard({ policy }: { policy: Policy }) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" />
            <CardTitle className="text-lg">Policy</CardTitle>
          </div>
          <Badge variant={statusVariant(policy.status)} className={statusColor(policy.status)}>
            {policy.status}
          </Badge>
        </div>
        <p className="text-xs font-mono text-muted-foreground">{policy.id}</p>
      </CardHeader>
      <CardContent className="space-y-3">
        <Row label="Policyholder" value={policy.policyholder} />
        <Row label="Region" value={policy.region_name} icon={<MapPin className="h-3.5 w-3.5" />} />
        <Row label="Metric" value={policy.metric} icon={<Droplets className="h-3.5 w-3.5" />} />
        <Row label="Trigger Rule" value={policy.trigger_rule} />
        <Row label="Threshold" value={`${policy.threshold} mm`} />
        <Row label="Window" value={`${policy.window_minutes} minutes`} icon={<Clock className="h-3.5 w-3.5" />} />
        <div className="pt-2 border-t">
          <Row
            label="Payout Amount"
            value={formatPaise(policy.payout_amount_paise, policy.currency)}
            bold
          />
        </div>
      </CardContent>
    </Card>
  );
}

function Row({ label, value, icon, bold }: { label: string; value: string; icon?: React.ReactNode; bold?: boolean }) {
  return (
    <div className="flex justify-between items-center text-sm">
      <span className="text-muted-foreground flex items-center gap-1.5">
        {icon}
        {label}
      </span>
      <span className={bold ? "font-semibold text-base" : "font-medium"}>{value}</span>
    </div>
  );
}

