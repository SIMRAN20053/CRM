import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { campaignsAPI } from '../services/api';
import { Loader2, ArrowLeft, Send, Activity } from 'lucide-react';
import { cn } from '../utils/cn';

export default function CampaignDetail() {
  const { id } = useParams();
  const [campaign, setCampaign] = useState(null);
  const [loading, setLoading] = useState(true);
  const [launching, setLaunching] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCampaignDetails();
  }, [id]);

  const fetchCampaignDetails = async () => {
    try {
      setLoading(true);
      const data = await campaignsAPI.get(id);
      setCampaign(data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch campaign details.');
    } finally {
      setLoading(false);
    }
  };

  const handleLaunch = async () => {
    if (!window.confirm('Are you sure you want to launch this campaign?')) return;
    try {
      setLaunching(true);
      await campaignsAPI.launch(id);
      await fetchCampaignDetails();
    } catch (err) {
      console.error(err);
      alert('Failed to launch campaign.');
    } finally {
      setLaunching(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error || !campaign) {
    return (
      <div className="text-center p-6 text-destructive bg-destructive/10 rounded-xl">
        {error || 'Campaign not found'}
      </div>
    );
  }

  const isDraft = campaign.status === 'draft';

  return (
    <div className="space-y-6">
      <div>
        <Link to="/campaigns" className="inline-flex items-center text-sm font-medium text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Campaigns
        </Link>
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground">{campaign.name}</h1>
            <p className="text-muted-foreground">ID: {campaign.id}</p>
          </div>
          <div className="flex items-center gap-2">
            {isDraft && (
              <button 
                onClick={handleLaunch} 
                disabled={launching}
                className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
              >
                {launching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                Launch Campaign
              </button>
            )}
            <Link to="/analytics" className="flex items-center gap-2 bg-accent text-accent-foreground border border-border px-4 py-2 rounded-md text-sm font-medium hover:bg-muted transition-colors">
              <Activity className="h-4 w-4" />
              View Analytics
            </Link>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
            <h2 className="text-lg font-medium mb-4">Message Template</h2>
            <div className="bg-muted p-4 rounded-md border border-border">
              <p className="text-foreground whitespace-pre-wrap font-mono text-sm">{campaign.message_template}</p>
            </div>
            
            {campaign.ai_reasoning && (
              <div className="mt-6">
                <h3 className="text-sm font-medium mb-2 text-primary">AI Reasoning</h3>
                <p className="text-sm text-muted-foreground bg-primary/5 p-4 rounded-md border border-primary/20">
                  {campaign.ai_reasoning}
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
            <h2 className="text-lg font-medium mb-4">Details</h2>
            <dl className="space-y-4">
              <div>
                <dt className="text-sm font-medium text-muted-foreground">Status</dt>
                <dd className="mt-1">
                  <span className={cn('inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold capitalize', 
                    campaign.status === 'completed' ? 'bg-green-500/10 text-green-500 border-green-500/20' : 
                    campaign.status === 'running' ? 'bg-blue-500/10 text-blue-500 border-blue-500/20' : 
                    'bg-gray-500/10 text-gray-400 border-gray-500/20'
                  )}>
                    {campaign.status}
                  </span>
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-muted-foreground">Channel</dt>
                <dd className="mt-1 text-sm text-foreground uppercase tracking-wider">{campaign.channel}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-muted-foreground">Created</dt>
                <dd className="mt-1 text-sm text-foreground">{new Date(campaign.created_at).toLocaleString()}</dd>
              </div>
              {campaign.launched_at && (
                <div>
                  <dt className="text-sm font-medium text-muted-foreground">Launched</dt>
                  <dd className="mt-1 text-sm text-foreground">{new Date(campaign.launched_at).toLocaleString()}</dd>
                </div>
              )}
            </dl>
          </div>

          <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
            <h2 className="text-lg font-medium mb-4">Performance</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-muted p-3 rounded-lg border border-border">
                <p className="text-xs text-muted-foreground font-medium">Sent</p>
                <p className="text-2xl font-bold text-foreground">{campaign.total_sent || 0}</p>
              </div>
              <div className="bg-muted p-3 rounded-lg border border-border">
                <p className="text-xs text-muted-foreground font-medium">Delivered</p>
                <p className="text-2xl font-bold text-foreground">{campaign.delivered || 0}</p>
              </div>
              <div className="bg-muted p-3 rounded-lg border border-border">
                <p className="text-xs text-muted-foreground font-medium">Opened</p>
                <p className="text-2xl font-bold text-foreground">{campaign.opened || 0}</p>
              </div>
              <div className="bg-muted p-3 rounded-lg border border-border">
                <p className="text-xs text-muted-foreground font-medium">Clicked</p>
                <p className="text-2xl font-bold text-foreground">{campaign.clicked || 0}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
