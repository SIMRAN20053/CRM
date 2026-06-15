import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { aiAPI, campaignsAPI, segmentsAPI } from '../services/api';
import { Wand2, Loader2, Sparkles, AlertCircle, Send, PieChart } from 'lucide-react';
import { cn } from '../utils/cn';

export default function AICampaignGenerator() {
  const navigate = useNavigate();
  const [objective, setObjective] = useState('');
  const [generating, setGenerating] = useState(false);
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!objective.trim()) return;

    try {
      setGenerating(true);
      setError(null);
      const data = await aiAPI.generatePlan({ objective });
      setPlan(data);
    } catch (err) {
      console.error(err);
      setError('AI failed to generate a plan. Please try again with a different objective.');
    } finally {
      setGenerating(false);
    }
  };

  const handleAcceptPlan = async () => {
    try {
      setSaving(true);
      setError(null);

      const segment = await segmentsAPI.create({
        name: plan.segment_name,
        rules: plan.rules,
        ai_reasoning: plan.reasoning,
        description: `Generated for objective: ${objective}`
      });

      const campaign = await campaignsAPI.create({
        segment_id: segment.id,
        name: `${plan.segment_name} Campaign`,
        objective: plan.objective,
        channel: plan.channel || 'whatsapp',
        message_template: plan.message_template,
        ai_reasoning: plan.reasoning
      });

      navigate(`/campaigns/${campaign.id}`);
    } catch (err) {
      console.error(err);
      setError('Failed to save the generated plan. Please try again.');
      setSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center space-y-4">
        <div className="inline-flex items-center justify-center p-3 bg-primary/10 rounded-full mb-2">
          <Wand2 className="h-8 w-8 text-primary" />
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">AI Campaign Generator</h1>
        <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
          Tell SmartReach AI what you want to achieve, and we'll instantly build the perfect audience segment and message template for you.
        </p>
      </div>

      <div className="bg-card border border-border rounded-xl p-1 shadow-sm">
        <form onSubmit={handleGenerate} className="flex flex-col sm:flex-row gap-2">
          <input
            type="text"
            value={objective}
            onChange={(e) => setObjective(e.target.value)}
            placeholder="e.g., Run a re-engagement campaign offering 20% off to users who haven't purchased in 60 days"
            className="flex-1 bg-transparent border-0 py-4 px-6 text-foreground focus:ring-0 placeholder:text-muted-foreground/60 text-lg outline-none"
            disabled={generating || saving}
          />
          <button
            type="submit"
            disabled={!objective.trim() || generating || saving}
            className="flex items-center justify-center gap-2 bg-primary text-primary-foreground px-8 py-4 rounded-lg font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50 m-1"
          >
            {generating ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Sparkles className="h-5 w-5" />
            )}
            Generate
          </button>
        </form>
      </div>

      {error && (
        <div className="p-4 bg-destructive/10 border border-destructive/20 text-destructive rounded-xl flex items-start gap-3">
          <AlertCircle className="h-5 w-5 mt-0.5" />
          <p>{error}</p>
        </div>
      )}

      {plan && (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
              <div className="flex items-center gap-2 mb-4 text-primary">
                <PieChart className="h-5 w-5" />
                <h2 className="text-lg font-semibold">Target Audience</h2>
              </div>
              <h3 className="font-bold text-xl mb-2 text-foreground">{plan.segment_name}</h3>
              <p className="text-muted-foreground text-sm mb-4">
                Estimated Size: <span className="font-bold text-foreground">{plan.audience_size} users</span>
              </p>
              <div className="bg-muted p-4 rounded-md border border-border">
                <p className="text-sm font-mono text-muted-foreground overflow-auto">
                  {JSON.stringify(plan.rules, null, 2)}
                </p>
              </div>
            </div>

            <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
              <div className="flex items-center gap-2 mb-4 text-primary">
                <Send className="h-5 w-5" />
                <h2 className="text-lg font-semibold">Message Template</h2>
              </div>
              <div className="bg-muted p-4 rounded-md border border-border h-full max-h-64 overflow-y-auto">
                <p className="text-sm text-foreground whitespace-pre-wrap">{plan.message_template}</p>
              </div>
            </div>
          </div>

          <div className="bg-primary/5 border border-primary/20 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-primary mb-2">AI Strategy Reasoning</h2>
            <p className="text-muted-foreground text-sm leading-relaxed">{plan.reasoning}</p>
          </div>

          <div className="flex justify-end pt-4 border-t border-border">
            <button
              onClick={() => setPlan(null)}
              className="px-6 py-2 text-muted-foreground hover:text-foreground font-medium transition-colors mr-4"
              disabled={saving}
            >
              Discard
            </button>
            <button
              onClick={handleAcceptPlan}
              disabled={saving}
              className="flex items-center gap-2 bg-primary text-primary-foreground px-6 py-2 rounded-md font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              {saving && <Loader2 className="h-4 w-4 animate-spin" />}
              Accept & Create Campaign
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
