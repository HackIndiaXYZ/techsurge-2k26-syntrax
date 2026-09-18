'use client';

import AppLayout from '@/components/AppLayout';
import { useApp } from '@/lib/context';
import { scenarioData, recentEvents, systemHealth } from '@/lib/mock-data';
import { MapPin, Calendar, CheckCircle, CloudRain, Users, Zap, IndianRupee, Clock, ArrowRight, Cloud, Cpu, Shield, Wallet, Brain, TrendingUp } from 'lucide-react';

export default function DashboardPage() {
  const { scenario } = useApp();
  const data = scenarioData[scenario];
  const now = new Date();
  const dateStr = now.toLocaleDateString('en-IN', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' });

  return (
    <AppLayout>
      {/* Page header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>Good morning, Sanju 👋</h1>
          <p style={{ fontSize: '13px', color: 'var(--color-tf-text-muted)', marginTop: '2px' }}>Here&apos;s your climate protection status today.</p>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 14px', backgroundColor: 'var(--color-tf-card)', border: '1px solid var(--color-tf-border)', borderRadius: '6px', fontSize: '12px', color: 'var(--color-tf-text-muted)' }}>
            <MapPin size={13} /> Tamil Nadu (TN)
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 14px', backgroundColor: 'var(--color-tf-card)', border: '1px solid var(--color-tf-border)', borderRadius: '6px', fontSize: '12px', color: 'var(--color-tf-text-muted)' }}>
            <Calendar size={13} /> {dateStr}
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
              <div style={{ fontSize: '17px', fontWeight: 600, color: '#fff' }}>Rainfall Index Insurance</div>
              <div style={{ fontSize: '12px', color: 'var(--color-tf-text-dim)', marginTop: '2px' }}>Real-time data. Verified sources. Automatic settlement.</div>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '32px', alignItems: 'center' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', marginBottom: '2px' }}>Coverage</div>
              <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-tf-green)' }}>₹10,000</div>
              <div style={{ fontSize: '9px', color: 'var(--color-tf-text-dim)' }}>(Simulated)</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', marginBottom: '2px' }}>Threshold</div>
              <div style={{ fontSize: '16px', fontWeight: 600, color: '#fff' }}>≥ 100 mm / 60 min</div>
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
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'relative' }}>
          {/* Pipeline line */}
          <div style={{ position: 'absolute', top: '20px', left: '60px', right: '60px', height: '2px', background: data.evaluation.triggered ? 'var(--color-tf-green)' : 'var(--color-tf-border-light)' }} />

          {[
            { label: 'Telemetry', sub: 'Data Received', done: true },
            { label: 'Validation', sub: 'Sources Checked', done: true },
            { label: 'Consensus', sub: data.consensus.achieved ? `${data.consensus.agreeSources} / ${data.consensus.totalSources} Agreed` : 'No Agreement', done: data.consensus.achieved },
            { label: 'Policy Evaluation', sub: data.evaluation.triggered ? 'Trigger Satisfied' : 'Not Triggered', done: data.evaluation.triggered },
            { label: 'Settlement', sub: data.evaluation.triggered ? 'Completed' : 'Pending', done: data.evaluation.triggered },
          ].map((step, i) => (
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
              <div style={{ fontSize: '9px', color: step.done ? 'var(--color-tf-text-muted)' : 'var(--color-tf-text-dim)' }}>{step.sub}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Metric Cards Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '12px', marginBottom: '16px' }}>
        {/* Trusted Rainfall */}
        <div className="tf-metric-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <CloudRain size={16} color="var(--color-tf-green)" />
            <span style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Trusted Rainfall</span>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>{data.consensus.trustedRainfall} mm</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '10px', color: 'var(--color-tf-green)' }}>
            <TrendingUp size={10} /> +12% vs. last hour
          </div>
        </div>

        {/* Source Agreement */}
        <div className="tf-metric-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Users size={16} color="var(--color-tf-green)" />
            <span style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Sources Agree</span>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>{data.consensus.agreeSources} / {data.consensus.totalSources}</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '10px', color: 'var(--color-tf-green)' }}>
            <CheckCircle size={10} /> {data.consensus.achieved ? 'Quorum Met' : 'No Quorum'}
          </div>
        </div>

        {/* Trigger */}
        <div className="tf-metric-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Zap size={16} color={data.evaluation.triggered ? 'var(--color-tf-green)' : 'var(--color-tf-red)'} />
            <span style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Trigger</span>
          </div>
          <div style={{ fontSize: '18px', fontWeight: 700, color: data.evaluation.triggered ? 'var(--color-tf-green)' : 'var(--color-tf-red)' }}>
            {data.evaluation.triggered ? 'SATISFIED' : 'NOT MET'}
          </div>
          <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>Rainfall ≥ 100 mm (60 min)</div>
        </div>

        {/* Simulated Payout */}
        <div className="tf-metric-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <IndianRupee size={16} color="var(--color-tf-green)" />
            <span style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Simulated Payout</span>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>₹{(data.evaluation.payoutAmountPaise / 100).toLocaleString()}</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '10px', color: data.evaluation.triggered ? 'var(--color-tf-green)' : 'var(--color-tf-text-dim)' }}>
            <CheckCircle size={10} /> {data.evaluation.triggered ? 'Eligible' : 'Not Eligible'}
          </div>
        </div>

        {/* Latency */}
        <div className="tf-metric-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Clock size={16} color="var(--color-tf-green)" />
            <span style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Settlement Latency</span>
          </div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>~ 820 ms</div>
          <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>Event → Settlement</div>
        </div>
      </div>

      {/* Recent Events + System Health */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        {/* Recent Events */}
        <div className="tf-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#fff' }}>Recent Events</h3>
            <a href="/events" style={{ fontSize: '11px', color: 'var(--color-tf-green)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px' }}>View All <ArrowRight size={10} /></a>
          </div>
          <table className="tf-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Event ID</th>
                <th>Rainfall (mm)</th>
                <th>Decision</th>
                <th>Settlement</th>
              </tr>
            </thead>
            <tbody>
              {recentEvents.map(evt => (
                <tr key={evt.id}>
                  <td style={{ fontFamily: 'monospace', fontSize: '12px' }}>{evt.time}</td>
                  <td style={{ fontWeight: 500, color: '#fff' }}>{evt.id}</td>
                  <td>{evt.rainfall}</td>
                  <td>
                    <span className={
                      evt.decision === 'Triggered' ? 'tf-badge tf-badge-green' :
                      evt.decision === 'Below Threshold' ? 'tf-badge tf-badge-orange' :
                      evt.decision === 'No Consensus' ? 'tf-badge tf-badge-red' :
                      'tf-badge tf-badge-blue'
                    }>
                      {evt.decision}
                    </span>
                  </td>
                  <td style={{ color: evt.settlement > 0 ? 'var(--color-tf-green)' : 'var(--color-tf-text-dim)' }}>
                    ₹{evt.settlement.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* System Health */}
        <div className="tf-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#fff' }}>System Health</h3>
            <span style={{ fontSize: '11px', color: 'var(--color-tf-green)' }}>All Systems Operational</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {systemHealth.map((item, i) => {
              const IconMap: Record<string, React.ReactNode> = {
                cloud: <Cloud size={14} color="var(--color-tf-text-muted)" />,
                cpu: <Cpu size={14} color="var(--color-tf-text-muted)" />,
                shield: <Shield size={14} color="var(--color-tf-text-muted)" />,
                zap: <Zap size={14} color="var(--color-tf-text-muted)" />,
                wallet: <Wallet size={14} color="var(--color-tf-text-muted)" />,
                brain: <Brain size={14} color="var(--color-tf-text-muted)" />,
              };
              return (
                <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 0', borderBottom: i < systemHealth.length - 1 ? '1px solid var(--color-tf-border)' : 'none' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--color-tf-text-muted)' }}>
                    {IconMap[item.icon]}
                    {item.name}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ fontSize: '11px', color: 'var(--color-tf-green)' }}>{item.status}</span>
                    <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: 'var(--color-tf-green)' }} />
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
