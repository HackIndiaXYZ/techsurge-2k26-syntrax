"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Wallet as WalletType } from "@/lib/types";
import { formatPaise } from "@/lib/types";
import { Wallet, ArrowUpRight } from "lucide-react";

export function WalletCard({ wallet }: { wallet: WalletType }) {
  const hasBalance = wallet.balance_paise > 0;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Wallet className="h-5 w-5 text-violet-600" />
            <CardTitle className="text-lg">Synthetic Wallet</CardTitle>
          </div>
          <span className="text-[10px] uppercase tracking-wider font-semibold text-orange-600 bg-orange-100 dark:bg-orange-950 dark:text-orange-400 px-2 py-0.5 rounded">
            Demo Only
          </span>
        </div>
        <p className="text-xs font-mono text-muted-foreground">{wallet.wallet_id}</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-center py-4">
          <p className="text-xs uppercase tracking-wider text-muted-foreground font-medium mb-1">Available Balance</p>
          <p className={`text-4xl font-bold tracking-tight ${hasBalance ? "text-emerald-600 dark:text-emerald-400" : "text-muted-foreground"}`}>
            {formatPaise(wallet.balance_paise, wallet.currency)}
          </p>
        </div>

        {wallet.last_credit_paise !== null && wallet.last_credit_paise > 0 && (
          <div className="rounded-lg bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 p-3">
            <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-400">
              <ArrowUpRight className="h-4 w-4" />
              <span className="text-sm font-medium">
                Latest credit: {formatPaise(wallet.last_credit_paise, wallet.currency)}
              </span>
            </div>
            {wallet.last_transaction_id && (
              <p className="text-xs text-muted-foreground font-mono mt-1">
                Tx: {wallet.last_transaction_id}
              </p>
            )}
          </div>
        )}

        {!hasBalance && (
          <p className="text-center text-xs text-muted-foreground">No credits received yet.</p>
        )}
      </CardContent>
    </Card>
  );
}

