'use client';

import { useEffect, useState } from 'react';
import AppLayout from '@/components/AppLayout';
import { api } from '@/lib/api';
import { WeatherSource } from '@/lib/types';
import { Activity, ServerCrash, RefreshCw } from 'lucide-react';

export default function ProvidersPage() {
  const [providers, setProviders] = useState<WeatherSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchProviders = async () => {
    try {
      const data = await api.getProvidersHealth();
      setProviders(data);
    } catch (e) {
      console.error('Failed to fetch providers', e);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchProviders();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchProviders();
  };

  const handleManualPoll = async () => {
    try {
      await api.triggerWeatherPoll();
      alert('Poll triggered successfully!');
    } catch (e) {
      alert('Failed to trigger poll');
    }
  };

  return (
    <AppLayout>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 className="tf-heading">Data Providers</h1>
          <p className="tf-body" style={{ marginTop: '4px' }}>Health and status of configured weather APIs</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button 
            className="tf-button tf-button-secondary"
            onClick={handleManualPoll}
          >
            <Activity size={16} />
            Force Weather Poll
          </button>
          <button 
            className="tf-button tf-button-primary"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
            Refresh Status
          </button>
        </div>
      </div>

      {loading ? (
        <div className="tf-card" style={{ padding: '32px', textAlign: 'center', color: 'var(--color-tf-text-muted)' }}>
          Loading providers...
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '16px' }}>
          {providers.map(p => (
            <div key={p.name} className="tf-card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: 600 }}>{p.name}</h3>
                <div style={{ 
                  display: 'flex', alignItems: 'center', gap: '6px',
                  padding: '4px 8px', borderRadius: '4px',
                  backgroundColor: p.status === 'ONLINE' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                  color: p.status === 'ONLINE' ? '#10b981' : '#ef4444',
                  fontSize: '12px', fontWeight: 600
                }}>
                  {p.status === 'ONLINE' ? <Activity size={12} /> : <ServerCrash size={12} />}
                  {p.status}
                </div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', color: 'var(--color-tf-text-dim)' }}>
                <span>Latency</span>
                <span style={{ color: 'var(--color-tf-text)' }}>{p.latency_ms} ms</span>
              </div>
            </div>
          ))}
          {providers.length === 0 && (
            <div className="tf-card" style={{ gridColumn: '1 / -1', padding: '32px', textAlign: 'center', color: 'var(--color-tf-text-muted)' }}>
              No providers registered or API unreachable.
            </div>
          )}
        </div>
      )}
    </AppLayout>
  );
}

