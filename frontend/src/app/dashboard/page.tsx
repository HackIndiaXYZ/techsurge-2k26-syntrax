'use client';

import { useEffect, useState } from 'react';
import AppLayout from '@/components/AppLayout';
import { useApp, DEMO_POLICY_ID, DEMO_WALLET_ID } from '@/lib/context';
import { api } from '@/lib/api';
import {
  HealthResponse,
  WeatherSource,
  PolicyResponse,
  WalletResponse,
  AuditListResponse,
} from '@/lib/types';
import { MapPin, Calendar, CheckCircle, CloudRain, Users, Zap, IndianRupee, Clock, ArrowRight, Cloud, Cpu, Shield, Wallet, Brain, TrendingUp, AlertTriangle, Loader2, XCircle, WifiOff } from 'lucide-react';

export default function DashboardPage() {
  const { simulationResult, simulationLoading } = useApp();

  // ── Backend state ──────────────────────────────────────────────────────────
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [providers, setProviders] = useState<WeatherSource[]>([]);
  const [policy, setPolicy] = useState<PolicyResponse | null>(null);
  const [wallet, setWallet] = useState<WalletResponse | null>(null);
  const [audit, setAudit] = useState<AuditListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const now = new Date();
  const dateStr = now.toLocaleDateString('en-IN', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' });

  // ── Fetch backend data on mount and when simulation completes ─────────────
  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [h, p, pol, w, a] = await Promise.allSettled([
          api.getHealth(),
          api.getProvidersHealth(),
          api.getPolicy(DEMO_POLICY_ID),
          api.getWallet(DEMO_WALLET_ID),
          api.getAuditEvents(DEMO_POLICY_ID, 10),
        ]);
        if (cancelled) return;
        setHealth(h.status === 'fulfilled' ? h.value : null);
        setProviders(p.status === 'fulfilled' ? p.value : []);
        setPolicy(pol.status === 'fulfilled' ? pol.value : null);
        setWallet(w.status === 'fulfilled' ? w.value : null);
        setAudit(a.status === 'fulfilled' ? a.value : null);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [simulationResult]); // re-fetch when simulation result changes

  // ── Derive pipeline state from simulation result ───────────────────────────
  const sim = simulationResult;
  const pipelineSteps = sim ? [
    { label: 'Telemetry', sub: `${sim.telemetry.accepted} accepted`, done: sim.telemetry.accepted > 0 },
    { label: 'Validation', sub: `${sim.telemetry.rejected} rejected`, done: true },
    { label: 'Consensus', sub: sim.consensus.status === 'REACHED' ? `${sim.consensus.accepted_sources.length} sources agreed` : 'No Agreement', done: sim.consensus.status === 'REACHED' },
    { label: 'Policy Evaluation', sub: sim.trigger.status === 'TRIGGERED' ? 'Trigger Satisfied' : sim.trigger.reason, done: sim.trigger.status === 'TRIGGERED' },
    { label: 'Settlement', sub: sim.settlement.status === 'SUCCESS' ? 'Completed' : sim.settlement.reason || sim.settlement.status, done: sim.settlement.status === 'SUCCESS' },
  ] : [
    { label: 'Telemetry', sub: 'Awaiting data', done: false },
    { label: 'Validation', sub: 'Awaiting data', done: false },
    { label: 'Consensus', sub: 'Awaiting data', done: false },
    { label: 'Policy Evaluation', sub: 'Awaiting data', done: false },
    { label: 'Settlement', sub: 'Awaiting data', done: false },
  ];

  const pipelineComplete = sim ? sim.trigger.status === 'TRIGGERED' : false;

  // ── System health items from real backend ──────────────────────────────────
  const systemHealthItems = [
    ...providers.map(p => ({
      name: p.name,
      status: p.status === 'ONLINE' ? 'Online' : p.status,
      icon: 'cloud' as const,
      ok: p.status === 'ONLINE',
    })),
    { name: 'Consensus Engine', status: health ? 'Ready' : 'Unknown', icon: 'cpu' as const, ok: !!health },
    { name: 'Policy Evaluation Engine', status: health ? 'Ready' : 'Unknown', icon: 'shield' as const, ok: !!health },
    { name: 'Settlement Engine', status: health ? 'Ready' : 'Unknown', icon: 'zap' as const, ok: !!health },
    { name: 'Synthetic Wallet', status: health ? 'Ready' : 'Unknown', icon: 'wallet' as const, ok: !!health },
    { name: 'Backend API', status: health?.status === 'ok' ? 'Healthy' : health?.status === 'degraded' ? 'Degraded' : 'Offline', icon: 'cpu' as const, ok: health?.status === 'ok' },
  ];

  const allHealthy = health?.status === 'ok' && providers.every(p => p.status === 'ONLINE');

  // ── Loading state ─────────────────────────────────────────────────────────
  if (loading) {
    return (
      <AppLayout>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px', gap: '16px' }}>
          <Loader2 size={32} color="var(--color-tf-green)" style={{ animation: 'spin 1s linear infinite' }} />
          <div style={{ fontSize: '14px', color: 'var(--color-tf-text-muted)' }}>Connecting to backend...</div>
        </div>
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      {/* Backend connection error banner */}
      {error && (
        <div style={{ padding: '12px 16px', marginBottom: '16px', backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <WifiOff size={16} color="#ef4444" />
          <span style={{ fontSize: '12px', color: '#ef4444' }}>Backend connection issue: {error}</span>
        </div>
      )}

      {/* Page header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>Good morning, Sanju 👋</h1>
          <p style={{ fontSize: '13px', color: 'var(--color-tf-text-muted)', marginTop: '2px' }}>Here&apos;s your climate protection status today.</p>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 14px', backgroundColor: 'var(--color-tf-card)', border: '1px solid var(--color-tf-border)', borderRadius: '6px', fontSize: '12px', color: 'var(--color-tf-text-muted)' }}>
            <MapPin size={13} /> {policy?.region_id || 'Loading...'}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 14px', backgroundColor: 'var(--color-tf-card)', border: '1px solid var(--color-tf-border)', borderRadius: '6px', fontSize: '12px', color: 'var(--color-tf-text-muted)' }}>
            <Calendar size={13} /> {dateStr}
          </div>
          {/* Backend status indicator */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 14px', backgroundColor: 'var(--color-tf-card)', border: `1px solid ${health ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`, borderRadius: '6px', fontSize: '12px', color: health ? 'var(--color-tf-green)' : '#ef4444' }}>
            <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: health ? 'var(--color-tf-green)' : '#ef4444' }} />
            Backend: {health?.status || 'Offline'}
          </div>
        </div>
      </div>

      {/* Active Protection Event Card */}
      <div style={{
        backgroundColor: 'var(--color-tf-card)',
        border: '1px solid var(--color-tf-border)',
        borderRadius: '10px',
        padding: '20px 24px',
        marginBottom: '16px',
        backgroundImage: 'linear-gradient(135deg, rgba(16,185,129,0.03) 0%, transparent 50%)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ width: '56px', height: '56px', borderRadius: '12px', backgroundColor: 'rgba(16,185,129,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <CloudRain size={28} color="var(--color-tf-green)" />
            </div>
            <div>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-green)', fontWeight: 700, letterSpacing: '1.5px', textTransform: 'uppercase', marginBottom: '4px' }}>Active Protection Event</div>
              <div style={{ fontSize: '17px', fontWeight: 600, color: '#fff' }}>{policy?.name || 'Rainfall Index Insurance'}</div>
              <div style={{ fontSize: '12px', color: 'var(--color-tf-text-dim)', marginTop: '2px' }}>Real-time data. Verified sources. Automatic settlement.</div>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '32px', alignItems: 'center' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', marginBottom: '2px' }}>Coverage</div>
              <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-tf-green)' }}>{policy?.payout_amount_inr_display || '...'}</div>
              <div style={{ fontSize: '9px', color: 'var(--color-tf-text-dim)' }}>(Simulated)</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', marginBottom: '2px' }}>Threshold</div>
              <div style={{ fontSize: '16px', fontWeight: 600, color: '#fff' }}>
                {policy ? `${policy.trigger_operator} ${policy.trigger_threshold_mm} mm / ${policy.observation_window_minutes} min` : '...'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Trust Pipeline */}
      <div style={{
        backgroundColor: 'var(--color-tf-card)',
        border: '1px solid var(--color-tf-border)',
        borderRadius: '10px',
        padding: '16px 24px',
        marginBottom: '16px',
      }}>
        {simulationLoading && (
          <div style={{ textAlign: 'center', padding: '8px', fontSize: '12px', color: 'var(--color-tf-green)', marginBottom: '8px' }}>
            <Loader2 size={14} style={{ display: 'inline', animation: 'spin 1s linear infinite', marginRight: '6px' }} />
            Running simulation pipeline...
          </div>
        )}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'relative' }}>
          <div style={{ position: 'absolute', top: '20px', left: '60px', right: '60px', height: '2px', background: pipelineComplete ? 'var(--color-tf-green)' : 'var(--color-tf-border-light)' }} />
          {pipelineSteps.map((step, i) => (
            <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px', zIndex: 1 }}>
              <div style={{
                width: '40px', height: '40px', borderRadius: '50%',
                backgroundColor: step.done ? 'var(--color-tf-green)' : 'var(--color-tf-card)',
                border: step.done ? 'none' : '2px solid var(--color-tf-border-light)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <CheckCircle size={20} color={step.done ? '#0a0e14' : 'var(--color-tf-text-dim)'} />
              </div>
              <div style={{ fontSize: '11px', fontWeight: 600, color: step.done ? '#fff' : 'var(--color-tf-text-dim)' }}>{step.label}</div>
              <div style={{ fontSize: '9px', color: step.done ? 'var(--color-tf-text-muted)' : 'var(--color-tf-text-dim)', maxWidth: '100px', textAlign: 'center' }}>{step.sub}</div>
            </div>
          ))}
        </div>
        {!sim && !simulationLoading && (
          <div style={{ textAlign: 'center', marginTop: '12px', fontSize: '11px', color: 'var(--color-tf-text-dim)' }}>
            Run a simulation from the Weather Intelligence page to see the pipeline in action.
          </div>
        )}
      </div>

      {/* Metric Cards Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '12px', marginBottom: '16px' }}>
        {/* Trusted Rainfall */}
        <div className="tf-metric-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <CloudRain size={16} color="var(--color-tf-green)" />
            <span style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Trusted Rainfall</span>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>
            {sim?.consensus.consensus_value_mm != null ? `${sim.consensus.consensus_value_mm.toFixed(1)} mm` : '— mm'}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '10px', color: sim?.consensus.status === 'REACHED' ? 'var(--color-tf-green)' : 'var(--color-tf-text-dim)' }}>
            {sim?.consensus.status === 'REACHED' ? <><CheckCircle size={10} /> Consensus Reached</> : <><Clock size={10} /> Awaiting simulation</>}
          </div>
        </div>

        {/* Source Agreement */}
        <div className="tf-metric-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Users size={16} color="var(--color-tf-green)" />
            <span style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Sources Agree</span>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>
            {sim ? `${sim.consensus.accepted_sources.length} / ${sim.telemetry.submitted}` : '— / —'}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '10px', color: sim?.consensus.status === 'REACHED' ? 'var(--color-tf-green)' : 'var(--color-tf-text-dim)' }}>
            {sim?.consensus.status === 'REACHED' ? <><CheckCircle size={10} /> Quorum Met</> : sim?.consensus.status === 'NO_CONSENSUS' ? <><XCircle size={10} /> No Quorum</> : <><Clock size={10} /> Awaiting</>}
          </div>
        </div>

        {/* Trigger */}
        <div className="tf-metric-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Zap size={16} color={sim?.trigger.status === 'TRIGGERED' ? 'var(--color-tf-green)' : 'var(--color-tf-text-dim)'} />
            <span style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Trigger</span>
          </div>
          <div style={{ fontSize: '18px', fontWeight: 700, color: sim?.trigger.status === 'TRIGGERED' ? 'var(--color-tf-green)' : sim ? 'var(--color-tf-red)' : 'var(--color-tf-text-dim)' }}>
            {sim?.trigger.status === 'TRIGGERED' ? 'SATISFIED' : sim ? 'NOT MET' : 'AWAITING'}
          </div>
          <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>
            {policy ? `Rainfall ${policy.trigger_operator} ${policy.trigger_threshold_mm} mm (${policy.observation_window_minutes} min)` : '...'}
          </div>
        </div>

        {/* Simulated Payout */}
        <div className="tf-metric-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <IndianRupee size={16} color="var(--color-tf-green)" />
            <span style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Simulated Payout</span>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>
            {sim?.settlement.payout_amount_inr_display || (wallet ? wallet.balance_inr_display : '₹0')}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '10px', color: sim?.settlement.status === 'SUCCESS' ? 'var(--color-tf-green)' : 'var(--color-tf-text-dim)' }}>
            {sim?.settlement.status === 'SUCCESS' ? <><CheckCircle size={10} /> Settled</> : sim ? <><XCircle size={10} /> {sim.settlement.status}</> : <><Clock size={10} /> Awaiting</>}
          </div>
        </div>

        {/* Latency */}
        <div className="tf-metric-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Clock size={16} color="var(--color-tf-green)" />
            <span style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Settlement Latency</span>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>
            {sim?.latency?.end_to_end_latency_ms != null ? `${sim.latency.end_to_end_latency_ms} ms` : '— ms'}
          </div>
          <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>Event → Settlement</div>
        </div>
      </div>

      {/* Recent Events + System Health */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        {/* Recent Audit Events */}
        <div className="tf-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#fff' }}>Recent Events</h3>
            <a href="/events" style={{ fontSize: '11px', color: 'var(--color-tf-green)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px' }}>View All <ArrowRight size={10} /></a>
          </div>
          {audit && audit.events.length > 0 ? (
            <table className="tf-table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Event</th>
                  <th>Status</th>
                  <th>Message</th>
                </tr>
              </thead>
              <tbody>
                {audit.events.slice(0, 5).map(evt => (
                  <tr key={evt.audit_id}>
                    <td style={{ fontFamily: 'monospace', fontSize: '11px' }}>{new Date(evt.created_at).toLocaleTimeString()}</td>
                    <td style={{ fontWeight: 500, color: '#fff', fontSize: '11px' }}>{evt.event_type}</td>
                    <td>
                      <span className={evt.status === 'SUCCESS' || evt.status === 'COMPLETED' ? 'tf-badge tf-badge-green' : evt.status === 'DUPLICATE' ? 'tf-badge tf-badge-orange' : 'tf-badge tf-badge-blue'}>
                        {evt.status}
                      </span>
                    </td>
                    <td style={{ fontSize: '11px', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{evt.message || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div style={{ padding: '24px', textAlign: 'center', color: 'var(--color-tf-text-dim)', fontSize: '12px' }}>
              No events yet. Run a simulation to generate audit events.
            </div>
          )}
        </div>

        {/* System Health */}
        <div className="tf-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#fff' }}>System Health</h3>
            <span style={{ fontSize: '11px', color: allHealthy ? 'var(--color-tf-green)' : 'var(--color-tf-orange)' }}>
              {allHealthy ? 'All Systems Operational' : 'Some Issues Detected'}
            </span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {systemHealthItems.map((item, i) => {
              const IconMap: Record<string, React.ReactNode> = {
                cloud: <Cloud size={14} color="var(--color-tf-text-muted)" />,
                cpu: <Cpu size={14} color="var(--color-tf-text-muted)" />,
                shield: <Shield size={14} color="var(--color-tf-text-muted)" />,
                zap: <Zap size={14} color="var(--color-tf-text-muted)" />,
                wallet: <Wallet size={14} color="var(--color-tf-text-muted)" />,
                brain: <Brain size={14} color="var(--color-tf-text-muted)" />,
              };
              return (
                <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 0', borderBottom: i < systemHealthItems.length - 1 ? '1px solid var(--color-tf-border)' : 'none' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--color-tf-text-muted)' }}>
                    {IconMap[item.icon]}
                    {item.name}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ fontSize: '11px', color: item.ok ? 'var(--color-tf-green)' : 'var(--color-tf-orange)' }}>{item.status}</span>
                    <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: item.ok ? 'var(--color-tf-green)' : 'var(--color-tf-orange)' }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
