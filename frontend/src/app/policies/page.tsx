"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Shield } from "lucide-react";
import { formatPaise } from "@/lib/types";

export default function PoliciesPage() {
  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Your Policies</h1>
        <p className="text-sm text-muted-foreground mt-1">Active climate protection for a more secure tomorrow.</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <Card className="md:col-span-2 bg-card/50 border-border/50 backdrop-blur-sm overflow-hidden flex flex-col">
          <div className="h-48 w-full relative">
            <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1594587399436-1e6efd59fb4c?q=80&w=2000&auto=format&fit=crop')] bg-cover bg-center" />
            <div className="absolute inset-0 bg-gradient-to-t from-background to-transparent" />
            <div className="absolute bottom-6 left-6">
              <h2 className="text-2xl font-bold text-foreground drop-shadow-md mb-2">Rainfall Index Protection</h2>
              <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 gap-1.5 py-1 px-3 text-[10px] uppercase font-bold tracking-wider hover:bg-emerald-500/20">
                <div className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                Active
              </Badge>
            </div>
          </div>
          
          <CardContent className="p-8 grid sm:grid-cols-2 gap-8 flex-1 bg-background/50">
            <div className="space-y-6">
              <div>
                <p className="text-[10px] uppercase tracking-wider font-semibold text-muted-foreground mb-1">Policy ID</p>
                <p className="text-sm font-medium text-foreground">SYN-F03-001</p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider font-semibold text-muted-foreground mb-1">Trigger</p>
                <p className="text-sm font-medium text-foreground">≥ 100 mm / 60 minutes</p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider font-semibold text-muted-foreground mb-1">Status</p>
                <div className="flex items-center gap-1.5 mt-1">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  <span className="text-sm font-medium text-foreground">Active</span>
                </div>
              </div>
            </div>
            
            <div className="space-y-6">
              <div>
                <p className="text-[10px] uppercase tracking-wider font-semibold text-muted-foreground mb-1">Region</p>
                <p className="text-sm font-medium text-foreground">Hyderabad (Synthetic Micro-Region)</p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider font-semibold text-muted-foreground mb-1">Payout</p>
                <p className="text-sm font-medium text-foreground">{formatPaise(1000000)} (Simulated)</p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider font-semibold text-muted-foreground mb-1">Coverage Period</p>
                <p className="text-sm font-medium text-foreground">Jan 2025 – Dec 2025</p>
              </div>
            </div>
          </CardContent>
          <div className="p-4 bg-muted/30 border-t border-border/50 flex justify-center text-xs text-emerald-400 font-medium cursor-pointer hover:bg-muted/50 transition-colors">
            View Policy Details →
          </div>
        </Card>

        <Card className="md:col-span-1 bg-card/50 border-border/50 backdrop-blur-sm h-fit">
          <CardHeader className="pb-3 border-b border-border/50">
            <CardTitle className="text-sm">About This Policy</CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <p className="text-xs text-muted-foreground leading-relaxed">
              This parametric insurance policy automatically triggers a payout when the trusted 60-minute rainfall in your region exceeds 100 mm, based on validated data from multiple weather sources.
            </p>
            <div className="mt-6 p-4 rounded-lg bg-amber-500/5 border border-amber-500/20">
              <p className="text-[10px] font-bold text-amber-500 uppercase tracking-wider mb-2">Basis Risk Notice</p>
              <p className="text-[10px] text-muted-foreground leading-relaxed">
                Settlement is based strictly on measured weather-index thresholds, not individual damage assessment. Actual losses may differ from the measured trigger.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
