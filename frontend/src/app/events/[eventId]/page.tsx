'use client';

import AppLayout from '@/components/AppLayout';
import { eventTimeline } from '@/lib/mock-data';
import { use } from 'react';
import { useState } from 'react';
import { CheckCircle, AlertTriangle, Clock, IndianRupee, Shield, Brain, FileText, BarChart3, ClipboardList } from 'lucide-react';

export default function EventDetailPage({ params }: { params: Promise<{ eventId: string }> }) {
  const { eventId } = use(params);
  const [activeTab, setActiveTab] = useState('timeline');

  const tabs = [
    { key: 'timeline', label: 'Timeline', icon: Clock },
    { key: 'weather', label: 'Weather Data', icon: BarChart3 },
    { key: 'policy', label: 'Policy Evaluation', icon: Shield },
    { key: 'audit', label: 'Audit Logs', icon: ClipboardList },
  ];

  return (
    <AppLayout>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>Event {eventId}</h1>
          <div style={{ display: 'flex', gap: '12px', marginTop: '6px', alignItems: 'center' }}>
            <span className="tf-badge tf-badge-green" style={{ fontSize: '11px', padding: '3px 10px' }}>Settled</span>
            <span style={{ fontSize: '18px', fontWeight: 700, color: 'var(--color-tf-green)' }}>₹10,000</span>
            <span style={{ fontSize: '12px', color: 'var(--color-tf-text-dim)' }}>Simulated Payout</span>
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
                padding: '10px 16px',
                fontSize: '12px',
                fontWeight: activeTab === tab.key ? 600 : 400,
                color: activeTab === tab.key ? 'var(--color-tf-green)' : 'var(--color-tf-text-muted)',
                backgroundColor: 'transparent',
                border: 'none',
                borderBottom: activeTab === tab.key ? '2px solid var(--color-tf-green)' : '2px solid transparent',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                transition: 'all 0.15s',
              }}
            >
              <Icon size={14} /> {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      {activeTab === 'timeline' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          {/* Timeline */}
          <div className="tf-card">
            <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#fff', marginBottom: '16px' }}>Event Timeline</h3>
            <div style={{ position: 'relative' }}>
              {/* Vertical line */}
              <div style={{ position: 'absolute', left: '15px', top: '8px', bottom: '8px', width: '2px', backgroundColor: 'var(--color-tf-border)' }} />

              {eventTimeline.map((item, i) => (
                <div key={i} style={{ display: 'flex', gap: '16px', marginBottom: '16px', position: 'relative' }}>
                  <div style={{
                    width: '32px', height: '32px', borderRadius: '50%', flexShrink: 0,
                    backgroundColor: item.status === 'complete' ? 'rgba(16,185,129,0.15)' : 'rgba(245,158,11,0.15)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    zIndex: 1,
                  }}>
                    {item.status === 'complete' ? <CheckCircle size={16} color="var(--color-tf-green)" /> : <AlertTriangle size={16} color="var(--color-tf-orange)" />}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '13px', fontWeight: 600, color: '#fff' }}>{item.title}</span>
                      <span style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', fontFamily: 'monospace' }}>{item.time}</span>
                    </div>
                    <p style={{ fontSize: '11px', color: 'var(--color-tf-text-muted)', marginTop: '2px' }}>{item.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Why This Decision */}
            <div className="tf-card" style={{ borderColor: 'rgba(16,185,129,0.2)' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#fff', marginBottom: '16px' }}>Why This Decision?</h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {[
                  { label: 'Weather sources', value: '3 received' },
                  { label: 'Valid sources', value: '2' },
                  { label: 'Consensus', value: '102.0 mm' },
                  { label: 'Threshold', value: '100 mm' },
                  { label: 'Result', value: 'Trigger satisfied', highlight: true },
                  { label: 'Settlement', value: '₹10,000 simulated', highlight: true },
                ].map((item, i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '8px', borderBottom: '1px solid var(--color-tf-border)' }}>
                    <span style={{ fontSize: '12px', color: 'var(--color-tf-text-dim)' }}>{item.label}</span>
                    <span style={{ fontSize: '13px', fontWeight: item.highlight ? 700 : 500, color: item.highlight ? 'var(--color-tf-green)' : '#fff' }}>{item.value}</span>
                  </div>
                ))}
              </div>

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

            {/* AI Explanation */}
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
                &ldquo;Two or more validated weather sources agreed on rainfall above the policy threshold. The deterministic policy engine therefore marked the event eligible for the simulated payout. Source C (Community) was excluded as a statistical outlier due to significant deviation from the consensus group.&rdquo;
              </p>

              <div style={{ marginTop: '12px', padding: '8px 12px', backgroundColor: 'rgba(100,116,139,0.05)', border: '1px solid var(--color-tf-border)', borderRadius: '6px' }}>
                <p style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', lineHeight: 1.5 }}>
                  AI assistance provides context for understanding decisions. All settlement decisions are made by the deterministic policy engine, not by AI.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'weather' && (
        <div className="tf-card">
          <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#fff', marginBottom: '16px' }}>Weather Data for Event</h3>
          <table className="tf-table">
            <thead>
              <tr>
                <th>Source</th>
                <th>Rainfall (mm)</th>
                <th>Status</th>
                <th>Temperature</th>
                <th>Humidity</th>
                <th>Wind</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ color: '#fff', fontWeight: 500 }}>Source A (IMD)</td>
                <td style={{ fontWeight: 600, color: '#fff' }}>103.0</td>
                <td><span className="tf-badge tf-badge-green">Valid</span></td>
                <td>26.4°C</td>
                <td>78%</td>
                <td>12 km/h</td>
              </tr>
              <tr>
                <td style={{ color: '#fff', fontWeight: 500 }}>Source B (OpenWeather)</td>
                <td style={{ fontWeight: 600, color: '#fff' }}>101.0</td>
                <td><span className="tf-badge tf-badge-green">Valid</span></td>
                <td>26.1°C</td>
                <td>80%</td>
                <td>10 km/h</td>
              </tr>
              <tr>
                <td style={{ color: '#fff', fontWeight: 500 }}>Source C (Community)</td>
                <td style={{ fontWeight: 600, color: 'var(--color-tf-red)' }}>7.0</td>
                <td><span className="tf-badge tf-badge-red">Outlier</span></td>
                <td>27.8°C</td>
                <td>82%</td>
                <td>8 km/h</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'policy' && (
        <div className="tf-card">
          <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#fff', marginBottom: '16px' }}>Policy Evaluation Result</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            <div style={{ padding: '16px', backgroundColor: 'var(--color-tf-surface)', border: '1px solid var(--color-tf-border)', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', marginBottom: '4px', textTransform: 'uppercase' }}>Trusted Rainfall</div>
              <div style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>102.0 mm</div>
            </div>
            <div style={{ padding: '16px', backgroundColor: 'var(--color-tf-surface)', border: '1px solid var(--color-tf-border)', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', marginBottom: '4px', textTransform: 'uppercase' }}>Threshold</div>
              <div style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>≥ 100 mm</div>
            </div>
            <div style={{ padding: '16px', backgroundColor: 'rgba(16,185,129,0.05)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', marginBottom: '4px', textTransform: 'uppercase' }}>Result</div>
              <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-tf-green)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}>
                <CheckCircle size={20} /> TRIGGER SATISFIED
              </div>
            </div>
          </div>
          <div style={{ marginTop: '16px', padding: '12px', backgroundColor: 'var(--color-tf-surface)', border: '1px solid var(--color-tf-border)', borderRadius: '8px' }}>
            <div style={{ fontSize: '11px', color: 'var(--color-tf-text-dim)' }}>Policy conditions met. 102.0 mm ≥ 100 mm threshold. Settlement of ₹10,000 (simulated) authorized by the deterministic policy engine.</div>
          </div>
        </div>
      )}

      {activeTab === 'audit' && (
        <div className="tf-card">
          <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#fff', marginBottom: '16px' }}>Audit Log</h3>
          <table className="tf-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Action</th>
                <th>Actor</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {[
                { ts: '10:24:00.123', action: 'TELEMETRY_RECEIVED', actor: 'System', detail: '3 weather sources ingested' },
                { ts: '10:24:02.456', action: 'VALIDATION_COMPLETE', actor: 'Validation Engine', detail: 'Source C flagged as outlier' },
                { ts: '10:24:03.789', action: 'CONSENSUS_ACHIEVED', actor: 'Consensus Engine', detail: '2/3 sources, 102.0 mm trusted' },
                { ts: '10:24:04.012', action: 'TRIGGER_EVALUATED', actor: 'Policy Engine', detail: '102.0 mm ≥ 100 mm — SATISFIED' },
                { ts: '10:24:05.345', action: 'PAYOUT_AUTHORIZED', actor: 'Settlement Engine', detail: '₹10,000 simulated payout' },
                { ts: '10:24:06.678', action: 'SETTLEMENT_COMPLETE', actor: 'Wallet Service', detail: 'WLT-001 credited' },
                { ts: '10:24:07.901', action: 'AUDIT_CREATED', actor: 'Audit Service', detail: 'Immutable record stored' },
              ].map((log, i) => (
                <tr key={i}>
                  <td style={{ fontFamily: 'monospace', fontSize: '11px' }}>{log.ts}</td>
                  <td style={{ fontWeight: 500, color: '#fff', fontSize: '11px' }}>{log.action}</td>
                  <td style={{ fontSize: '12px' }}>{log.actor}</td>
                  <td style={{ fontSize: '12px' }}>{log.detail}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </AppLayout>
  );
}
