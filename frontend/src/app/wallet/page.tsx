"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Wallet as WalletIcon, AlertTriangle, CheckCircle2, ShieldBan, Info } from "lucide-react";
import { ApiClient } from "@/lib/api/client";
import { DashboardData, formatPaise, ScenarioId } from "@/lib/types";

function WalletContent() {
  const searchParams = useSearchParams();
  const scenario = (searchParams.get("scenario") as ScenarioId) || "normal";
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    ApiClient.getDashboard(scenario).then(setData).catch(console.error);
  }, [scenario]);

  if (!data) return <div className="p-8 text-muted-foreground animate-pulse">Loading wallet...</div>;

  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-5xl">
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Synthetic Wallet</h1>
          <p className="text-sm text-muted-foreground mt-1">Simulated settlements from climate events.</p>
        </div>
        <Badge variant="outline" className="bg-amber-500/10 text-amber-400 border-amber-500/20 gap-1.5 py-1 px-3 text-[10px] uppercase font-bold tracking-wider">
          <AlertTriangle className="h-3 w-3" />
          SIMULATION MODE
          <span className="font-normal text-muted-foreground lowercase hidden sm:inline ml-1">No real money involved.</span>
        </Badge>
      </div>

      <Card className="bg-card/50 border-border/50 backdrop-blur-sm max-w-2xl">
        <CardContent className="p-8">
          <div className="flex items-center gap-6 mb-6">
            <div className="h-16 w-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <WalletIcon className="h-8 w-8" />
            </div>
            <div>
              <h2 className="text-4xl font-bold text-foreground tracking-tight mb-1">
                {formatPaise(data.wallet.balance_paise)}
              </h2>
              <p className="text-sm text-muted-foreground">Available Balance (Simulated)</p>
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-3 pt-6 border-t border-border/50">
            <Button variant="outline" className="flex-1 bg-background/50 border-border/50 text-foreground hover:bg-muted/50 text-xs h-9">
              View Transactions
            </Button>
            <Button variant="outline" className="flex-1 bg-background/50 border-border/50 text-foreground hover:bg-muted/50 text-xs h-9">
              Export Statement
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4 pt-4">
        <h3 className="font-semibold text-sm">Transaction History</h3>
        <Card className="bg-card/50 border-border/50 backdrop-blur-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="text-[10px] text-muted-foreground uppercase tracking-wider bg-background/30 border-b border-border/50">
                <tr>
                  <th className="px-6 py-3 font-medium">Date & Time</th>
                  <th className="px-6 py-3 font-medium">Event ID</th>
                  <th className="px-6 py-3 font-medium">Description</th>
                  <th className="px-6 py-3 font-medium text-right">Amount</th>
                  <th className="px-6 py-3 font-medium text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/30">
                {data.wallet.transactions.map((tx) => (
                  <tr key={tx.id} className="hover:bg-muted/30 transition-colors">
                    <td className="px-6 py-4 font-mono text-muted-foreground">
                      {new Date(tx.timestamp).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="px-6 py-4 font-medium text-foreground">{tx.event_id}</td>
                    <td className="px-6 py-4 text-muted-foreground">{tx.description}</td>
                    <td className="px-6 py-4 text-right font-medium">
                      {tx.type === "CREDIT" ? (
                        <span className="text-emerald-400">+{formatPaise(tx.amount_paise)}</span>
                      ) : (
                        <span className="text-muted-foreground">{formatPaise(tx.amount_paise)}</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Badge variant="outline" className={
                        tx.status === "Credited" ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20 text-[10px]" :
                        tx.status === "Blocked" ? "bg-destructive/10 text-destructive border-destructive/20 text-[10px]" : "bg-muted/50 text-muted-foreground border-border/50 text-[10px]"
                      }>
                        {tx.status}
                      </Badge>
                    </td>
                  </tr>
                ))}
                
                {/* Mock historical transactions matching reference image for fidelity */}
                <tr className="hover:bg-muted/30 transition-colors">
                  <td className="px-6 py-4 font-mono text-muted-foreground">25 Aug 13:58</td>
                  <td className="px-6 py-4 font-medium text-foreground">EVT-1041</td>
                  <td className="px-6 py-4 text-muted-foreground">No payout (below threshold)</td>
                  <td className="px-6 py-4 text-right font-medium text-muted-foreground">₹0</td>
                  <td className="px-6 py-4 text-right text-muted-foreground">—</td>
                </tr>
                <tr className="hover:bg-muted/30 transition-colors">
                  <td className="px-6 py-4 font-mono text-muted-foreground">25 Aug 13:21</td>
                  <td className="px-6 py-4 font-medium text-foreground">EVT-1040</td>
                  <td className="px-6 py-4 text-muted-foreground">No payout (no consensus)</td>
                  <td className="px-6 py-4 text-right font-medium text-muted-foreground">₹0</td>
                  <td className="px-6 py-4 text-right text-muted-foreground">—</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
}

export default function WalletPage() {
  return <Suspense><WalletContent /></Suspense>;
}
