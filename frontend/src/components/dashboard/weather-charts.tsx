"use client";

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, ReferenceLine, CartesianGrid } from "recharts";
import { TimeSeriesPoint } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";

export function WeatherCharts({ data }: { data: TimeSeriesPoint[] }) {
  return (
    <Card className="bg-card/50 border-border/50 backdrop-blur-sm shadow-sm overflow-hidden w-full">
      <div className="px-6 py-4 border-b border-border/50">
        <h3 className="font-semibold text-sm">Rainfall Accumulation (60 min)</h3>
      </div>
      <CardContent className="p-6">
        <div className="h-[280px] w-full mt-2">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="currentColor" className="opacity-10" />
              <XAxis dataKey="time" stroke="currentColor" className="text-muted-foreground text-[10px]" tickLine={false} axisLine={false} dy={10} />
              <YAxis stroke="currentColor" className="text-muted-foreground text-[10px]" tickLine={false} axisLine={false} dx={-10} />
              <Tooltip 
                contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '6px', fontSize: '12px' }}
                itemStyle={{ color: 'hsl(var(--foreground))' }}
                labelStyle={{ color: 'hsl(var(--muted-foreground))', marginBottom: '4px' }}
              />
              <ReferenceLine y={100} stroke="hsl(var(--emerald-500))" strokeDasharray="3 3" opacity={0.5}>
              </ReferenceLine>
              
              <Line type="monotone" dataKey="source_a" name="Source A" stroke="#3b82f6" strokeWidth={2} dot={false} opacity={0.3} />
              <Line type="monotone" dataKey="source_b" name="Source B" stroke="#a855f7" strokeWidth={2} dot={false} opacity={0.3} />
              <Line type="monotone" dataKey="source_c" name="Source C" stroke="#f97316" strokeWidth={2} dot={false} opacity={0.3} />
              <Line type="monotone" dataKey="consensus" name="Trusted Consensus" stroke="#10b981" strokeWidth={2} dot={{ r: 3, fill: '#10b981', strokeWidth: 0 }} activeDot={{ r: 5, fill: '#10b981' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
