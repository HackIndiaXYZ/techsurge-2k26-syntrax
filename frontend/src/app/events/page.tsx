'use client';

import { useEffect, useState } from 'react';
import AppLayout from '@/components/AppLayout';
import { api } from '@/lib/api';
import { DEMO_POLICY_ID } from '@/lib/context';
import { AuditListResponse } from '@/lib/types';
import Link from 'next/link';
import { Eye, Filter, Loader2, WifiOff } from 'lucide-react';

export default function EventsPage() {
  const [audit, setAudit] = useState<AuditListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await api.getAuditEvents(DEMO_POLICY_ID, 50);
        if (!cancelled) setAudit(data);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load events');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  if (loading) {
    return (
      <AppLayout>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px', gap: '16px' }}>
          <Loader2 size={32} color="var(--color-tf-green)" style={{ animation: 'spin 1s linear infinite' }} />
          <div style={{ fontSize: '14px', color: 'var(--color-tf-text-muted)' }}>Loading audit events...</div>
        </div>
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      {error && (
        <div style={{ padding: '12px 16px', marginBottom: '16px', backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <WifiOff size={16} color="#ef4444" />
          <span style={{ fontSize: '12px', color: '#ef4444' }}>{error}</span>
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>Event Evidence</h1>
          <p style={{ fontSize: '13px', color: 'var(--color-tf-text-muted)', marginTop: '2px' }}>
            Complete audit trail for all climate protection events.
            {audit && <span style={{ marginLeft: '8px', color: 'var(--color-tf-green)' }}>({audit.total} total events)</span>}
          </p>
        </div>
        <button className="tf-btn tf-btn-outline" style={{ fontSize: '12px' }}>
          <Filter size={13} /> Filter Events
        </button>
      </div>

      <div className="tf-card">
        {audit && audit.events.length > 0 ? (
          <table className="tf-table">
            <thead>
              <tr>
                <th>Created At</th>
                <th>Event Type</th>
                <th>Entity</th>
                <th>Status</th>
                <th>Message</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {audit.events.map(evt => (
                <tr key={evt.audit_id}>
                  <td style={{ fontSize: '11px', fontFamily: 'monospace' }}>{new Date(evt.created_at).toLocaleString()}</td>
                  <td style={{ fontWeight: 600, color: '#fff', fontSize: '11px' }}>{evt.event_type}</td>
                  <td style={{ fontSize: '11px' }}>{evt.entity_type}: {evt.entity_id.substring(0, 12)}...</td>
                  <td>
                    <span className={
                      evt.status === 'SUCCESS' || evt.status === 'COMPLETED' ? 'tf-badge tf-badge-green' :
                      evt.status === 'DUPLICATE' || evt.status === 'ALREADY_SETTLED' ? 'tf-badge tf-badge-orange' :
                      evt.status === 'FAILED' ? 'tf-badge tf-badge-red' :
                      'tf-badge tf-badge-blue'
                    }>
                      {evt.status}
                    </span>
                  </td>
                  <td style={{ fontSize: '11px', maxWidth: '250px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{evt.message || '—'}</td>
                  <td>
                    <Link href={`/events/${evt.correlation_id || evt.audit_id}`} className="tf-btn tf-btn-outline" style={{ padding: '4px 10px', fontSize: '11px', textDecoration: 'none' }}>
                      <Eye size={12} /> View Evidence
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div style={{ padding: '48px', textAlign: 'center', color: 'var(--color-tf-text-dim)', fontSize: '13px' }}>
            No audit events yet. Run a simulation from the Weather Intelligence page to generate events.
          </div>
        )}
      </div>
    </AppLayout>
  );
}
