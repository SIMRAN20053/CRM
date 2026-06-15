import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

const deliveryData = [
  { name: 'Mon', delivered: 4000, opened: 2400, clicked: 1200 },
  { name: 'Tue', delivered: 3000, opened: 1398, clicked: 800 },
  { name: 'Wed', delivered: 2000, opened: 9800, clicked: 3200 },
  { name: 'Thu', delivered: 2780, opened: 3908, clicked: 1500 },
  { name: 'Fri', delivered: 1890, opened: 4800, clicked: 2100 },
  { name: 'Sat', delivered: 2390, opened: 3800, clicked: 1800 },
  { name: 'Sun', delivered: 3490, opened: 4300, clicked: 2100 },
];

export default function DeliveryAnalytics() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Delivery Analytics</h1>
        <p className="text-muted-foreground">Monitor performance and engagement across all channels.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-card border border-border p-6 rounded-xl shadow-sm text-center">
          <p className="text-sm font-medium text-muted-foreground mb-1">Global Delivery Rate</p>
          <p className="text-4xl font-bold text-foreground">98.2%</p>
          <p className="text-xs text-green-500 mt-2">+1.2% from last week</p>
        </div>
        <div className="bg-card border border-border p-6 rounded-xl shadow-sm text-center">
          <p className="text-sm font-medium text-muted-foreground mb-1">Global Open Rate</p>
          <p className="text-4xl font-bold text-foreground">32.4%</p>
          <p className="text-xs text-green-500 mt-2">+4.1% from last week</p>
        </div>
        <div className="bg-card border border-border p-6 rounded-xl shadow-sm text-center">
          <p className="text-sm font-medium text-muted-foreground mb-1">Global Click Rate</p>
          <p className="text-4xl font-bold text-foreground">12.8%</p>
          <p className="text-xs text-red-500 mt-2">-0.5% from last week</p>
        </div>
      </div>

      <div className="bg-card border border-border p-6 rounded-xl shadow-sm">
        <h2 className="text-lg font-medium text-foreground mb-6">Engagement Trends</h2>
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={deliveryData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" />
              <YAxis stroke="hsl(var(--muted-foreground))" />
              <Tooltip 
                contentStyle={{ backgroundColor: 'hsl(var(--popover))', borderColor: 'hsl(var(--border))', color: 'hsl(var(--popover-foreground))' }}
              />
              <Line type="monotone" dataKey="delivered" stroke="hsl(var(--muted-foreground))" strokeWidth={2} />
              <Line type="monotone" dataKey="opened" stroke="hsl(var(--primary))" strokeWidth={3} />
              <Line type="monotone" dataKey="clicked" stroke="hsl(var(--destructive))" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
