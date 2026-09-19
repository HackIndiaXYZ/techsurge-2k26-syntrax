'use client';

import { useEffect, useState } from 'react';
import AppLayout from '@/components/AppLayout';
import { api } from '@/lib/api';
import { DEMO_POLICY_ID, useApp } from '@/lib/context';
import { AuditListResponse, AuditEventResponse } from '@/lib/types';
import { use } from 'react';
import { CheckCircle, AlertTriangle, Clock, IndianRupee, Shield, Brain, FileText, BarChart3, ClipboardList, Loader2, WifiOff } from 'lucide-react';

export default function EventDetailPage({ params }: { params: Promise<{ eventId: string }> }) {
  const { eventId } = use(params);
  const { simulationResult } = useApp();
  const [activeTab, setActiveTab] = useState('timeline');
  const [audit, setAudit] = useState<AuditListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const data = await api.getAuditEvents(DEMO_POLICY_ID, 100);
        if (!cancelled) setAudit(data);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load event data');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [eventId]);

  // Filter audit events matching this event's correlation_id
  const relatedEvents: AuditEventResponse[] = audit?.events.filter(
    e => e.correlation_id === eventId || e.audit_id === eventId
  ) ?? [];

  // Use all audit events if no specific match (allows browsing)
  const displayEvents = relatedEvents.length > 0 ? relatedEvents : (audit?.events.slice(0, 10) ?? []);

  const sim = simulationResult;

  const tabs = [
    { key: 'timeline', label: 'Timeline', icon: Clock },
    { key: 'weather', label: 'Weather Data', icon: BarChart3 },
    { key: 'policy', label: 'Policy Evaluation', icon: Shield },
    { key: 'audit', label: 'Audit Logs', icon: ClipboardList },
  ];

  if (loading) {
    return (
      <AppLayout>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px', gap: '16px' }}>
          <Loader2 size={32} color="var(--color-tf-green)" style={{ animation: 'spin 1s linear infinite' }} />
          <div style={{ fontSize: '14px', color: 'var(--color-tf-text-muted)' }}>Loading event details...</div>
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

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>Event {eventId.substring(0, 12)}...</h1>
          <div style={{ display: 'flex', gap: '12px', marginTop: '6px', alignItems: 'center' }}>
            {sim?.settlement.status === 'SUCCESS' && (
              <>
                <span className="tf-badge tf-badge-green" style={{ fontSize: '11px', padding: '3px 10px' }}>Settled</span>
                <span style={{ fontSize: '18px', fontWeight: 700, color: 'var(--color-tf-green)' }}>{sim.settlement.payout_amount_inr_display}</span>
                <span style={{ fontSize: '12px', color: 'var(--color-tf-text-dim)' }}>Simulated Payout</span>
              </>
            )}
          </div>
        </div>
        <button className="tf-btn tf-btn-outline" style={{ fontSize: '12px' }}>
          <FileText size={13} /> Export Report
        </button>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '4px', marginBottom: '16px', borderBottom: '1px solid var(--color-tf-border)', paddingBottom: '0' }}>
        {tabs.map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              style={{
                padding: '10px 16px', fontSize: '12px',
                fontWeight: activeTab === tab.key ? 600 : 400,
                color: activeTab === tab.key ? 'var(--color-tf-green)' : 'var(--color-tf-text-muted)',
                backgroundColor: 'transparent', border: 'none',
                borderBottom: activeTab === tab.key ? '2px solid var(--color-tf-green)' : '2px solid transparent',
                cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', transition: 'all 0.15s',
              }}
            >
              <Icon size={14} /> {tab.label}
            </button>
          );
        })}
      </div>

      {/* Timeline Tab */}
      {activeTab === 'timeline' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div className="tf-card">
            <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#fff', marginBottom: '16px' }}>Event Timeline</h3>
            {displayEvents.length > 0 ? (
              <div style={{ position: 'relative' }}>
                <div style={{ position: 'absolute', left: '15px', top: '8px', bottom: '8px', width: '2px', backgroundColor: 'var(--color-tf-border)' }} />
                {displayEvents.map((item, i) => (
                  <div key={i} style={{ display: 'flex', gap: '16px', marginBottom: '16px', position: 'relative' }}>
                    <div style={{
                      width: '32px', height: '32px', borderRadius: '50%', flexShrink: 0,
                      backgroundColor: item.status === 'SUCCESS' || item.status === 'COMPLETED' ? 'rgba(16,185,129,0.15)' : 'rgba(245,158,11,0.15)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1,
                    }}>
                      {item.status === 'SUCCESS' || item.status === 'COMPLETED' ? <CheckCircle size={16} color="var(--color-tf-green)" /> : <AlertTriangle size={16} color="var(--color-tf-orange)" />}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '13px', fontWeight: 600, color: '#fff' }}>{item.event_type}</span>
                        <span style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', fontFamily: 'monospace' }}>{new Date(item.created_at).toLocaleTimeString()}</span>
                      </div>
                      <p style={{ fontSize: '11px', color: 'var(--color-tf-text-muted)', marginTop: '2px' }}>{item.message || `${item.entity_type}: ${item.status}`}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ padding: '24px', textAlign: 'center', color: 'var(--color-tf-text-dim)', fontSize: '12px' }}>
                No timeline events found for this event.
              </div>
            )}
          </div>

          {/* Why This Decision */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div className="tf-card" style={{ borderColor: 'rgba(16,185,129,0.2)' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#fff', marginBottom: '16px' }}>Why This Decision?</h3>
              {sim ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {[
                    { label: 'Weather sources', value: `${sim.telemetry.submitted} received` },
                    { label: 'Accepted', value: String(sim.telemetry.accepted) },
                    { label: 'Rejected / Outliers', value: `${sim.telemetry.rejected} rejected, ${sim.consensus.outlier_sources.length} outliers` },
                    { label: 'Consensus', value: sim.consensus.status === 'REACHED' ? `${sim.consensus.consensus_value_mm} mm` : 'NO CONSENSUS' },
                    { label: 'Threshold', value: `${sim.trigger.threshold_mm} mm` },
                    { label: 'Result', value: sim.trigger.status === 'TRIGGERED' ? 'Trigger satisfied' : sim.trigger.reason, highlight: true },
                    { label: 'Settlement', value: sim.settlement.status === 'SUCCESS' ? `${sim.settlement.payout_amount_inr_display} simulated` : sim.settlement.status, highlight: sim.settlement.status === 'SUCCESS' },
                  ].map((item, i) => (
                    <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '8px', borderBottom: '1px solid var(--color-tf-border)' }}>
                      <span style={{ fontSize: '12px', color: 'var(--color-tf-text-dim)' }}>{item.label}</span>
                      <span style={{ fontSize: '13px', fontWeight: item.highlight ? 700 : 500, color: item.highlight ? 'var(--color-tf-green)' : '#fff' }}>{item.value}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ padding: '16px', textAlign: 'center', color: 'var(--color-tf-text-dim)', fontSize: '12px' }}>
                  Run a simulation to see decision details.
                </div>
              )}

              <div style={{
                marginTop: '16px', padding: '12px', backgroundColor: 'rgba(16,185,129,0.05)',
                border: '1px solid rgba(16,185,129,0.15)', borderRadius: '8px',
              }}>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>Decision Authority</div>
                <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--color-tf-green)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Shield size={16} /> Deterministic Policy Engine
                </div>
              </div>
            </div>

            {/* AI Explanation placeholder */}
            <div className="tf-card" style={{ borderColor: 'rgba(100,116,139,0.3)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <Brain size={18} color="var(--color-tf-text-muted)" />
                <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#fff' }}>AI Explanation</h3>
              </div>
              <div style={{
                display: 'inline-flex', alignItems: 'center', gap: '4px',
                padding: '2px 8px', backgroundColor: 'rgba(100,116,139,0.15)',
                borderRadius: '4px', fontSize: '9px', color: 'var(--color-tf-text-dim)',
                textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '12px',
              }}>
                Explanatory Only — Does not determine settlement.
              </div>
              <p style={{ fontSize: '13px', color: 'var(--color-tf-text-muted)', lineHeight: 1.7, fontStyle: 'italic' }}>
                AI explanation will be available in a future block. All settlement decisions are made by the deterministic policy engine, not by AI.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Weather Data Tab */}
      {activeTab === 'weather' && (
        <div className="tf-card">
          <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#fff', marginBottom: '16px' }}>Weather Data for Event</h3>
          {sim ? (
            <table className="tf-table">
              <thead>
                <tr>
                  <th>Source ID</th>
                  <th>Rainfall (mm)</th>
                  <th>Status</th>
                  <th>Rejection Reason</th>
                </tr>
              </thead>
              <tbody>
                {sim.telemetry.observations.map((obs, i) => (
                  <tr key={i}>
                    <td style={{ color: '#fff', fontWeight: 500, fontFamily: 'monospace', fontSize: '11px' }}>{obs.source_id.substring(0, 16)}...</td>
                    <td style={{ fontWeight: 600, color: obs.status === 'ACCEPTED' ? '#fff' : 'var(--color-tf-red)' }}>{obs.value.toFixed(1)}</td>
                    <td><span className={obs.status === 'ACCEPTED' ? 'tf-badge tf-badge-green' : 'tf-badge tf-badge-red'}>{obs.status}</span></td>
                    <td style={{ fontSize: '11px', color: 'var(--color-tf-text-dim)' }}>{obs.rejection_reason || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div style={{ padding: '24px', textAlign: 'center', color: 'var(--color-tf-text-dim)', fontSize: '12px' }}>
              Run a simulation to see weather data for this event.
            </div>
          )}
        </div>
      )}

      {/* Policy Evaluation Tab */}
      {activeTab === 'policy' && (
        <div className="tf-card">
          <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#fff', marginBottom: '16px' }}>Policy Evaluation Result</h3>
          {sim ? (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                <div style={{ padding: '16px', backgroundColor: 'var(--color-tf-surface)', border: '1px solid var(--color-tf-border)', borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', marginBottom: '4px', textTransform: 'uppercase' }}>Trusted Rainfall</div>
                  <div style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>{sim.trigger.consensus_value_mm?.toFixed(1) || 'N/A'} mm</div>
                </div>
                <div style={{ padding: '16px', backgroundColor: 'var(--color-tf-surface)', border: '1px solid var(--color-tf-border)', borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', marginBottom: '4px', textTransform: 'uppercase' }}>Threshold</div>
                  <div style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>≥ {sim.trigger.threshold_mm} mm</div>
                </div>
                <div style={{ padding: '16px', backgroundColor: sim.trigger.status === 'TRIGGERED' ? 'rgba(16,185,129,0.05)' : 'rgba(239,68,68,0.05)', border: `1px solid ${sim.trigger.status === 'TRIGGERED' ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}`, borderRadius: '8px', textAlign: 'center' }}>
                  <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', marginBottom: '4px', textTransform: 'uppercase' }}>Result</div>
                  <div style={{ fontSize: '20px', fontWeight: 700, color: sim.trigger.status === 'TRIGGERED' ? 'var(--color-tf-green)' : 'var(--color-tf-red)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}>
                    {sim.trigger.status === 'TRIGGERED' ? <><CheckCircle size={20} /> TRIGGER SATISFIED</> : <>{sim.trigger.status}</>}
                  </div>
                </div>
              </div>
              <div style={{ marginTop: '16px', padding: '12px', backgroundColor: 'var(--color-tf-surface)', border: '1px solid var(--color-tf-border)', borderRadius: '8px' }}>
                <div style={{ fontSize: '11px', color: 'var(--color-tf-text-dim)' }}>{sim.trigger.reason}</div>
              </div>
            </>
          ) : (
            <div style={{ padding: '24px', textAlign: 'center', color: 'var(--color-tf-text-dim)', fontSize: '12px' }}>
              Run a simulation to see policy evaluation results.
            </div>
          )}
        </div>
      )}

      {/* Audit Logs Tab */}
      {activeTab === 'audit' && (
        <div className="tf-card">
          <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#fff', marginBottom: '16px' }}>Audit Log</h3>
          {displayEvents.length > 0 ? (
            <table className="tf-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Event Type</th>
                  <th>Entity</th>
                  <th>Status</th>
                  <th>Message</th>
                </tr>
              </thead>
              <tbody>
                {displayEvents.map((log, i) => (
                  <tr key={i}>
                    <td style={{ fontFamily: 'monospace', fontSize: '11px' }}>{new Date(log.created_at).toLocaleTimeString()}</td>
                    <td style={{ fontWeight: 500, color: '#fff', fontSize: '11px' }}>{log.event_type}</td>
                    <td style={{ fontSize: '12px' }}>{log.entity_type}</td>
                    <td>
                      <span className={log.status === 'SUCCESS' || log.status === 'COMPLETED' ? 'tf-badge tf-badge-green' : 'tf-badge tf-badge-blue'}>
                        {log.status}
                      </span>
                    </td>
                    <td style={{ fontSize: '12px' }}>{log.message || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div style={{ padding: '24px', textAlign: 'center', color: 'var(--color-tf-text-dim)', fontSize: '12px' }}>
              No audit logs found. Run a simulation to generate audit events.
            </div>
          )}
        </div>
      )}
    </AppLayout>
  );
}
