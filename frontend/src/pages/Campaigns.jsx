import React, { useState, useEffect } from 'react';
import { campaignsAPI } from '../services/api';
import { Link } from 'react-router-dom';
import { Send, Loader2, Plus, BarChart2 } from 'lucide-react';
import { cn } from '../utils/cn';

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      setLoading(true);
      const data = await campaignsAPI.list();
      setCampaigns(data.campaigns || []);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch campaigns.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-500/10 text-green-500 border-green-500/20';
      case 'running': return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      case 'failed': return 'bg-red-500/10 text-red-500 border-red-500/20';
      default: return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Campaigns</h1>
          <p className="text-muted-foreground">Manage, launch, and track your marketing campaigns.</p>
        </div>
        <div className="flex gap-2">
          <Link to="/ai-generator" className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors">
            <Plus className="h-4 w-4" />
            New Campaign
          </Link>
        </div>
      </div>

      {error && <div className="p-4 bg-destructive/10 text-destructive rounded-md">{error}</div>}

      <div className="rounded-xl border border-border bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-muted text-muted-foreground">
              <tr>
                <th className="px-6 py-3 font-medium">Campaign Name</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">Channel</th>
                <th className="px-6 py-3 font-medium">Sent</th>
                <th className="px-6 py-3 font-medium">Opened</th>
                <th className="px-6 py-3 font-medium">Clicked</th>
                <th className="px-6 py-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {loading ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center text-muted-foreground">
                    <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2 text-primary" />
                    Loading campaigns...
                  </td>
                </tr>
              ) : campaigns.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center text-muted-foreground">
                    No campaigns found. Start one with the AI Generator.
                  </td>
                </tr>
              ) : (
                campaigns.map((c) => (
                  <tr key={c.id} className="hover:bg-muted/50 transition-colors">
                    <td className="px-6 py-4 font-medium text-foreground">
                      <Link to={`/campaigns/${c.id}`} className="hover:text-primary transition-colors">
                        {c.name}
                      </Link>
                    </td>
                    <td className="px-6 py-4">
                      <span className={cn('inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold capitalize', getStatusColor(c.status))}>
                        {c.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-muted-foreground uppercase text-xs tracking-wider">{c.channel}</td>
                    <td className="px-6 py-4 text-foreground">{c.total_sent || 0}</td>
                    <td className="px-6 py-4 text-foreground">{c.opened || 0}</td>
                    <td className="px-6 py-4 text-foreground">{c.clicked || 0}</td>
                    <td className="px-6 py-4 text-right">
                      <Link to={`/campaigns/${c.id}`} className="inline-flex items-center text-primary hover:underline text-xs font-medium">
                        View Details <BarChart2 className="ml-1 h-3 w-3" />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
