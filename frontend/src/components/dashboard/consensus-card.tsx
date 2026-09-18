"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { Consensus, Policy } from "@/lib/types";
import { CloudRain, CheckCircle2, XCircle, AlertTriangle, Radio } from "lucide-react";

function sourceStatusBadge(status: string, inGroup: boolean) {
  if (status === "VALID" && inGroup) {
    return <Badge variant="outline" className="bg-emerald-500/10 text-emerald-700 border-emerald-200 gap-1"><CheckCircle2 className="h-3 w-3" />VALID</Badge>;
  }
  if (status === "OUTLIER") {
    return <Badge variant="destructive" className="gap-1"><AlertTriangle className="h-3 w-3" />OUTLIER</Badge>;
  }
  if (status === "SOURCE_DISAGREEMENT") {
    return <Badge variant="destructive" className="gap-1 bg-orange-600"><XCircle className="h-3 w-3" />DISAGREES</Badge>;
  }
  if (status === "IMPOSSIBLE_VALUE" || status === "STALE" || status === "FUTURE_TIMESTAMP") {
    return <Badge variant="destructive" className="gap-1"><XCircle className="h-3 w-3" />{status.replace(/_/g, " ")}</Badge>;
  }
  return <Badge variant="outline">{status}</Badge>;
}

function consensusStateBadge(state: string) {
  switch (state) {
    case "ACHIEVED":
      return <Badge className="bg-emerald-600 text-white gap-1"><CheckCircle2 className="h-3.5 w-3.5" />CONSENSUS ACHIEVED</Badge>;
    case "NO_CONSENSUS":
      return <Badge variant="destructive" className="gap-1 text-sm"><XCircle className="h-3.5 w-3.5" />NO CONSENSUS</Badge>;
    case "PENDING":
      return <Badge variant="secondary" className="gap-1"><Radio className="h-3.5 w-3.5 animate-pulse" />PENDING</Badge>;
    case "EXPIRED":
      return <Badge variant="secondary" className="gap-1">EXPIRED</Badge>;
    default:
      return <Badge variant="outline">{state}</Badge>;
  }
}

export function ConsensusCard({ consensus, threshold }: { consensus: Consensus; threshold: number }) {
  const isAchieved = consensus.state === "ACHIEVED";
  const isNoConsensus = consensus.state === "NO_CONSENSUS";

  return (
    <Card className={isNoConsensus ? "border-red-300 bg-red-50/30 dark:border-red-900 dark:bg-red-950/20" : ""}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CloudRain className="h-5 w-5 text-blue-600" />
            <CardTitle className="text-lg">Weather Consensus</CardTitle>
          </div>
          {consensusStateBadge(consensus.state)}
        </div>
        <p className="text-xs text-muted-foreground">
          {consensus.agreeing_sources}/{consensus.total_sources} sources agreeing · Quorum: {consensus.quorum_required} required
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Source Readings Table */}
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Source</TableHead>
              <TableHead className="text-right">Reading</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-center">In Group</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {consensus.sources.map((source) => (
              <TableRow
                key={source.id}
                className={!source.is_in_consensus_group ? "opacity-60" : ""}
              >
                <TableCell>
                  <div>
                    <p className="font-medium text-sm">{source.name}</p>
                    <p className="text-xs text-muted-foreground font-mono">{source.id}</p>
                  </div>
                </TableCell>
                <TableCell className="text-right">
                  <span className={`font-mono font-semibold text-base ${!source.is_in_consensus_group ? "line-through text-muted-foreground" : ""}`}>
                    {source.value} {source.unit}
                  </span>
                </TableCell>
                <TableCell>{sourceStatusBadge(source.validation_status, source.is_in_consensus_group)}</TableCell>
                <TableCell className="text-center">
                  {source.is_in_consensus_group ? (
                    <CheckCircle2 className="h-4 w-4 text-emerald-600 mx-auto" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-400 mx-auto" />
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        {/* Consensus Result */}
        {isAchieved && consensus.value !== null && (
          <div className="rounded-lg border bg-emerald-50 dark:bg-emerald-950/30 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Trusted Consensus Value</p>
                <p className="text-3xl font-bold text-emerald-700 dark:text-emerald-400 mt-1">
                  {consensus.value} mm
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">vs Threshold</p>
                <p className="text-xl font-semibold mt-1">{threshold} mm</p>
              </div>
            </div>
          </div>
        )}

        {isNoConsensus && (
          <div className="rounded-lg border border-red-300 bg-red-50 dark:bg-red-950/30 dark:border-red-800 p-4 text-center">
            <XCircle className="h-8 w-8 text-red-500 mx-auto mb-2" />
            <p className="font-semibold text-red-700 dark:text-red-400">Insufficient consensus — settlement not authorized.</p>
            <p className="text-xs text-muted-foreground mt-1">
              No pair of sources agreed within the 5 mm tolerance. A trusted weather value cannot be established.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

