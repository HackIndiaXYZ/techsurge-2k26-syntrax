"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Shield,
  CloudRain,
  Wallet,
  FileText,
  Settings,
  Leaf
} from "lucide-react";

const navItems = [
  { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { name: "Policies", href: "/policies", icon: Shield },
  { name: "Live Monitor", href: "/weather", icon: CloudRain },
  { name: "Wallet", href: "/wallet", icon: Wallet },
  { name: "Evidence", href: "/events", icon: FileText },
];

export function Sidebar() {
  const pathname = usePathname();

  // Hide sidebar on login page
  if (pathname === "/login") return null;

  return (
    <aside className="w-[240px] border-r bg-card/50 hidden md:flex flex-col flex-shrink-0 z-20 backdrop-blur-sm">
      <div className="h-16 flex items-center px-6 border-b">
        <Link href="/" className="flex items-center gap-2 group">
          <Leaf className="h-6 w-6 text-emerald-500 group-hover:text-emerald-400 transition-colors" />
          <span className="text-xl font-bold tracking-tight text-foreground group-hover:text-white transition-colors">TerraFlux</span>
        </Link>
      </div>
      
      <div className="flex-1 py-6 px-4 flex flex-col gap-1.5 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href === "/dashboard" && pathname === "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                  : "text-muted-foreground hover:bg-muted/50 hover:text-foreground border border-transparent"
              )}
            >
              <item.icon className={cn("h-4 w-4", isActive ? "text-emerald-400" : "text-muted-foreground")} />
              {item.name}
            </Link>
          );
        })}
        <div className="mt-4 pt-4 border-t">
          <Link
            href="/settings"
            className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-muted-foreground hover:bg-muted/50 hover:text-foreground border border-transparent transition-all duration-200"
          >
            <Settings className="h-4 w-4" />
            Settings
          </Link>
        </div>
      </div>

      <div className="p-4 border-t bg-card/30">
        <div className="flex items-center gap-3 rounded-md p-2 hover:bg-muted/50 transition-colors cursor-pointer">
          <div className="h-9 w-9 rounded-full bg-emerald-900/50 border border-emerald-700/50 flex items-center justify-center text-emerald-400 font-bold text-xs shrink-0">
            SA
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-sm font-medium text-foreground truncate">Sanju</span>
            <span className="text-xs text-muted-foreground truncate">Policyholder</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
