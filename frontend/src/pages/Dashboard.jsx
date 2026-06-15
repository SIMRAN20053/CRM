import React from 'react';
import { Users, PieChart, Send, MousePointerClick } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { name: 'Jan', campaigns: 4 },
  { name: 'Feb', campaigns: 3 },
  { name: 'Mar', campaigns: 2 },
  { name: 'Apr', campaigns: 6 },
  { name: 'May', campaigns: 5 },
  { name: 'Jun', campaigns: 8 },
];

export default function Dashboard() {
  const stats = [
    { name: 'Total Customers', value: '12,456', icon: Users, change: '+12%', changeType: 'positive' },
    { name: 'Active Segments', value: '8', icon: PieChart, change: '+2', changeType: 'positive' },
    { name: 'Campaigns Sent', value: '145', icon: Send, change: '+18%', changeType: 'positive' },
    { name: 'Avg. Open Rate', value: '24.5%', icon: MousePointerClick, change: '-1.2%', changeType: 'negative' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Dashboard</h1>
        <p className="text-muted-foreground">Welcome back! Here's an overview of your platform.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((item) => (
          <div key={item.name} className="overflow-hidden rounded-xl bg-card p-6 shadow-sm border border-border">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <item.icon className="h-8 w-8 text-primary" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="truncate text-sm font-medium text-muted-foreground">{item.name}</dt>
                  <dd>
                    <div className="text-2xl font-bold text-foreground">{item.value}</div>
                  </dd>
                </dl>
              </div>
            </div>
            <div className="mt-4">
              <div className={`text-sm ${item.changeType === 'positive' ? 'text-green-500' : 'text-red-500'}`}>
                {item.change} from last month
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl bg-card p-6 shadow-sm border border-border">
          <h2 className="text-lg font-medium text-foreground mb-4">Campaign Activity</h2>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" />
                <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'hsl(var(--popover))', borderColor: 'hsl(var(--border))', color: 'hsl(var(--popover-foreground))' }}
                  itemStyle={{ color: 'hsl(var(--foreground))' }}
                />
                <Bar dataKey="campaigns" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-xl bg-card p-6 shadow-sm border border-border">
          <h2 className="text-lg font-medium text-foreground mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {[
              { text: 'Campaign "Summer Sale" launched to VIP Segment', time: '2 hours ago' },
              { text: 'AI generated new segment "Churn Risk"', time: '4 hours ago' },
              { text: '500 new customers imported', time: '1 day ago' },
              { text: 'Campaign "Welcome Flow" finished', time: '1 day ago' }
            ].map((activity, idx) => (
              <div key={idx} className="flex flex-col border-b border-border pb-3 last:border-0 last:pb-0">
                <span className="text-sm font-medium text-foreground">{activity.text}</span>
                <span className="text-xs text-muted-foreground">{activity.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
