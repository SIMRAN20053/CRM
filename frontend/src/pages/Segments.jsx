import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { segmentsAPI } from '../services/api';
import { Filter, Loader2, Plus } from 'lucide-react';

export default function Segments() {
  const [segments, setSegments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSegments();
  }, []);

  const fetchSegments = async () => {
    try {
      setLoading(true);
      const data = await segmentsAPI.list();
      setSegments(data.segments || []);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch segments.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Segments</h1>
          <p className="text-muted-foreground">Define and manage target audiences for your campaigns.</p>
        </div>
        <Link to="/ai-generator" className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors">
          <Plus className="h-4 w-4" />
          Create Segment
        </Link>
      </div>

      {error && <div className="p-4 bg-destructive/10 text-destructive rounded-md">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full py-12 flex flex-col items-center justify-center text-muted-foreground">
            <Loader2 className="h-8 w-8 animate-spin text-primary mb-2" />
            <p>Loading segments...</p>
          </div>
        ) : segments.length === 0 ? (
          <div className="col-span-full py-12 text-center text-muted-foreground bg-card border border-border rounded-xl">
            <Filter className="h-10 w-10 mx-auto mb-3 text-muted-foreground/50" />
            <p>No segments found. Create one to get started.</p>
          </div>
        ) : (
          segments.map((s) => (
            <div key={s.id} className="rounded-xl border border-border bg-card p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <h3 className="font-semibold text-lg text-foreground truncate" title={s.name}>{s.name}</h3>
                <span className="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary">
                  {s.audience_size} Users
                </span>
              </div>
              <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                {s.description || 'No description provided.'}
              </p>
              {s.ai_reasoning && (
                <div className="bg-muted p-3 rounded-md text-xs text-muted-foreground mb-4 line-clamp-2">
                  <span className="font-semibold text-primary">AI Logic: </span>
                  {s.ai_reasoning}
                </div>
              )}
              <div className="text-xs text-muted-foreground mt-auto pt-4 border-t border-border flex justify-between">
                <span>Created {new Date(s.created_at).toLocaleDateString()}</span>
                <button className="text-primary hover:underline font-medium">View Audience</button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
