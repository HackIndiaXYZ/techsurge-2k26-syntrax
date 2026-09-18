"use client";

import { usePathname } from "next/navigation";
import { Moon, Sun, Monitor, ShieldCheck, Zap } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";

export function Header() {
  const pathname = usePathname();
  const { setTheme, theme } = useTheme();

  if (pathname === "/login") return null;

  return (
    <header className="h-16 border-b bg-card/50 backdrop-blur-sm flex items-center justify-between px-6 sticky top-0 z-40 flex-shrink-0">
      <div className="flex items-center gap-4">
        <h1 className="text-lg font-bold tracking-tight hidden sm:block text-foreground">
          COMPLETE FRONTEND EXPERIENCE
        </h1>
        <div className="h-4 w-px bg-border hidden sm:block" />
        <span className="text-xs text-muted-foreground uppercase tracking-wider font-medium hidden md:block">
          From Login to Settlement — A Seamless Climate Insurance Journey
        </span>
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
          <ShieldCheck className="h-3.5 w-3.5" />
          REAL WEATHER. VERIFIED DATA. FAIR OUTCOMES.
        </div>
        
        <div className="flex items-center bg-background/50 rounded-md border border-border p-0.5">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme("light")}
            className={`h-7 w-7 rounded-sm transition-all ${theme === 'light' ? 'bg-muted text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'}`}
          >
            <Sun className="h-3.5 w-3.5" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme("system")}
            className={`h-7 w-7 rounded-sm transition-all ${theme === 'system' ? 'bg-muted text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'}`}
          >
            <Monitor className="h-3.5 w-3.5" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme("dark")}
            className={`h-7 w-7 rounded-sm transition-all ${theme === 'dark' ? 'bg-muted text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'}`}
          >
            <Moon className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>
    </header>
  );
}
