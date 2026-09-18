import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Leaf, ShieldCheck, Database, Zap } from "lucide-react";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-background">
      {/* Left split - Brand Hero */}
      <div className="w-full md:w-1/2 bg-slate-950 p-12 flex flex-col justify-between relative overflow-hidden text-white border-r border-border/50">
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1518331647614-7a1f04cd34f5?q=80&w=2069&auto=format&fit=crop')] bg-cover bg-center opacity-30 mix-blend-luminosity" />
        <div className="absolute inset-0 bg-gradient-to-b from-slate-950/80 via-slate-950/90 to-slate-950" />
        
        <div className="relative z-10 flex items-center gap-3">
          <Leaf className="h-10 w-10 text-emerald-500" />
          <span className="text-3xl font-bold tracking-tight text-white">TerraFlux</span>
        </div>

        <div className="relative z-10 space-y-6 max-w-lg mt-16 md:mt-0">
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight leading-tight text-white/90">
            Autonomous climate protection, built on trusted weather intelligence.
          </h1>
          
          <div className="space-y-6 pt-8">
            <div className="flex items-center gap-4 text-slate-300">
              <div className="p-2 bg-emerald-500/10 rounded border border-emerald-500/20 text-emerald-500"><Database className="h-5 w-5" /></div>
              <span className="text-sm font-semibold tracking-wider">TRUSTED DATA</span>
            </div>
            <div className="flex items-center gap-4 text-slate-300">
              <div className="p-2 bg-emerald-500/10 rounded border border-emerald-500/20 text-emerald-500"><ShieldCheck className="h-5 w-5" /></div>
              <span className="text-sm font-semibold tracking-wider">FAIR SETTLEMENTS</span>
            </div>
            <div className="flex items-center gap-4 text-slate-300">
              <div className="p-2 bg-emerald-500/10 rounded border border-emerald-500/20 text-emerald-500"><Zap className="h-5 w-5" /></div>
              <span className="text-sm font-semibold tracking-wider">A MORE RESILIENT TOMORROW</span>
            </div>
          </div>
        </div>

        <div className="relative z-10 mt-16 md:mt-0 text-slate-500 text-xs tracking-wider">
          Climate risks are real.<br/>So is the solution.
        </div>
      </div>

      {/* Right split - Login Form */}
      <div className="w-full md:w-1/2 p-8 md:p-12 lg:p-24 flex flex-col justify-center bg-card">
        <div className="mx-auto w-full max-w-sm space-y-8 bg-background p-8 rounded-xl border border-border/50 shadow-xl">
          <div className="space-y-2 text-center mb-8">
            <h2 className="text-2xl font-bold tracking-tight text-foreground">Welcome back</h2>
            <p className="text-xs text-muted-foreground">
              Sign in to your TerraFlux account
            </p>
          </div>

          <div className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-[10px] uppercase tracking-wider text-muted-foreground">Email</Label>
              <Input id="email" type="email" placeholder="you@example.com" disabled className="bg-muted/50 border-border/50 h-10 text-sm" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password" className="text-[10px] uppercase tracking-wider text-muted-foreground">Password</Label>
              <Input id="password" type="password" value="••••••••" disabled className="bg-muted/50 border-border/50 h-10 text-sm" />
            </div>
            <Button className="w-full bg-emerald-500 hover:bg-emerald-600 text-background font-semibold h-10" disabled>
              Sign in
            </Button>
          </div>

          <div className="relative py-4">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-border/50" />
            </div>
            <div className="relative flex justify-center text-[10px] uppercase font-bold tracking-wider">
              <span className="bg-background px-2 text-muted-foreground">OR</span>
            </div>
          </div>

          <Link href="/dashboard" className="block">
            <Button variant="outline" className="w-full border-emerald-500/50 text-emerald-400 hover:bg-emerald-500/10 bg-emerald-500/5 h-10">
              ▶ Enter Demo Environment
            </Button>
          </Link>
          
          <p className="text-center text-[10px] text-muted-foreground mt-4 leading-tight px-4">
            Demo account gives you full access to explore the platform.
          </p>
        </div>
      </div>
    </div>
  );
}
