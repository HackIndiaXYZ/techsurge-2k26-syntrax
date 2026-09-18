"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Settlement } from "@/lib/types";
import { formatPaise } from "@/lib/types";
import { Banknote, CheckCircle2, Copy, XCircle, Clock, ShieldAlert } from "lucide-react";

function settlementBadge(status: string, isDuplicate: boolean) {
  if (isDuplicate) {
    return <Badge className="gap-1 bg-purple-100 text-purple-700 border-purple-200"><Copy className="h-3.5 w-3.5" />DUPLICATE</Badge>;
  }
  switch (status) {
    case "SETTLED":
      return <Badge className="bg-emerald-600 text-white gap-1"><CheckCircle2 className="h-3.5 w-3.5" />SETTLED</Badge>;
    case "PENDING":
      return <Badge variant="secondary" className="gap-1"><Clock className="h-3.5 w-3.5" />PENDING</Badge>;
    case "TRIGGERED":
      return <Badge className="bg-amber-600 text-white gap-1">TRIGGERED</Badge>;
    case "BLOCKED":
      return <Badge variant="destructive" className="gap-1"><ShieldAlert className="h-3.5 w-3.5" />BLOCKED</Badge>;
    case "FAILED":
      return <Badge variant="destructive" className="gap-1"><XCircle className="h-3.5 w-3.5" />FAILED</Badge>;
    default:
      return <Badge variant="outline">{status}</Badge>;
  }
}

export function SettlementCard({ settlement }: { settlement: Settlement }) {
  const isSettled = settlement.status === "SETTLED";
  const isBlocked = settlement.status === "BLOCKED";
  const isDuplicate = settlement.is_duplicate;

  return (
    <Card className={isDuplicate ? "border-purple-300 bg-purple-50/20 dark:border-purple-900 dark:bg-purple-950/20" : ""}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Banknote className="h-5 w-5 text-emerald-600" />
            <CardTitle className="text-lg">Settlement</CardTitle>
          </div>
          {settlementBadge(settlement.status, isDuplicate)}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {(isSettled || isDuplicate) && (
          <div className="rounded-lg bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 p-4 text-center">
            <p className="text-xs uppercase tracking-wider text-muted-foreground font-medium">Payout Amount</p>
            <p className="text-3xl font-bold text-emerald-700 dark:text-emerald-400 mt-1">
              {formatPaise(settlement.payout_amount_paise, settlement.currency)}
            </p>
          </div>
        )}

        {isDuplicate && (
          <div className="rounded-lg bg-purple-50 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-800 p-3 text-center">
            <Copy className="h-5 w-5 text-purple-600 mx-auto mb-1" />
            <p className="text-sm font-medium text-purple-700 dark:text-purple-400">
              Duplicate request detected — original settlement returned.
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Idempotency key matched. No additional payout executed.
            </p>
          </div>
        )}

        {isBlocked && (
          <div className="rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 p-3 text-center">
            <ShieldAlert className="h-5 w-5 text-red-500 mx-auto mb-1" />
            <p className="text-sm font-medium text-red-700 dark:text-red-400">
              Settlement blocked — no consensus available.
            </p>
          </div>
        )}

        <div className="text-sm space-y-2 pt-2 border-t">
          <Row label="Payout ID" value={settlement.payout_id} mono />
          {settlement.transaction_id && <Row label="Transaction ID" value={settlement.transaction_id} mono />}
          {settlement.idempotency_key && <Row label="Idempotency Key" value={settlement.idempotency_key} mono />}
          {settlement.executed_at && <Row label="Executed At" value={new Date(settlement.executed_at).toLocaleString()} />}
        </div>
      </CardContent>
    </Card>
  );
}

function Row({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-muted-foreground text-xs">{label}</span>
      <span className={`text-xs ${mono ? "font-mono" : "font-medium"}`}>{value}</span>
    </div>
  );
}

