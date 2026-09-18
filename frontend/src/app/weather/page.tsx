'use client';

import AppLayout from '@/components/AppLayout';
import { useApp } from '@/lib/context';
import { scenarioData, DemoScenario } from '@/lib/mock-data';
import { MapPin, Clock, CheckCircle, AlertTriangle, Thermometer, Droplets, Wind, Play, XCircle, Copy, ShieldCheck } from 'lucide-react';

function SparklineChart({ data, color, height = 60 }: { data: number[]; color: string; height?: number }) {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const w = 200;
  const points = data.map((v, i) => {
    const x = (i / (data.length - 1)) * w;
    const y = height - ((v - min) / range) * (height - 10) - 5;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg viewBox={`0 0 ${w} ${height}`} style={{ width: '100%', height: `${height}px` }}>
      <defs>
        <linearGradient id={`grad-${color.replace('#', '')}`} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      {/* Grid lines */}
      {[0, 1, 2, 3].map(i => (
        <line key={i} x1="0" y1={height * (i / 3)} x2={w} y2={height * (i / 3)} stroke="var(--color-tf-border)" strokeWidth="0.5" />
      ))}
      {/* Area */}
      <polygon
        points={`0,${height} ${points} ${w},${height}`}
        fill={`url(#grad-${color.replace('#', '')})`}
      />
      {/* Line */}
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function generateSparkline(base: number, variance: number, isOutlier: boolean) {
  const data = [];
  for (let i = 0; i < 12; i++) {
    if (isOutlier) {
      data.push(base * 0.06 + Math.random() * variance * 0.3);
    } else {
      data.push(base * 0.7 + Math.random() * variance);
    }
  }
  return data;
}

export default function WeatherPage() {
  const { scenario, setScenario } = useApp();
  const data = scenarioData[scenario];

  const scenarios: { key: DemoScenario; label: string; sub: string; values: string; color: string }[] = [
    { key: 'normal', label: 'Normal Event', sub: 'All sources agree', values: '(110, 108, 111 mm)', color: 'var(--color-tf-green)' },
    { key: 'corrupted', label: 'Corrupted Source', sub: 'One outlier source', values: '(110, 108, 7 mm)', color: 'var(--color-tf-orange)' },
    { key: 'no_consensus', label: 'No Consensus', sub: 'Sources disagree', values: '(120, 50, 5 mm)', color: 'var(--color-tf-red)' },
    { key: 'duplicate', label: 'Duplicate Settlement', sub: 'Replay same event', values: '(test idempotency)', color: '#3b82f6' },
  ];

  return (
    <AppLayout>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>Live Weather Telemetry</h1>
          <p style={{ fontSize: '13px', color: 'var(--color-tf-text-muted)', marginTop: '2px' }}>Real-time data from multiple sources with validation and consensus.</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 14px', backgroundColor: 'var(--color-tf-card)', border: '1px solid var(--color-tf-border)', borderRadius: '6px', fontSize: '12px', color: 'var(--color-tf-text-muted)' }}>
            <MapPin size={13} color="var(--color-tf-green)" /> Tamil Nadu (TN)
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 14px', backgroundColor: 'var(--color-tf-card)', border: '1px solid var(--color-tf-border)', borderRadius: '6px', fontSize: '12px', color: 'var(--color-tf-text-muted)' }}>
            <Clock size={13} /> Last 60 minutes
          </div>
        </div>
      </div>

      {/* Source Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '16px' }}>
        {data.sources.map(src => (
          <div key={src.id} className="tf-card" style={{
            borderColor: src.status === 'outlier' ? 'rgba(239, 68, 68, 0.3)' : 'var(--color-tf-border)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
              <div>
                <div style={{ fontSize: '13px', fontWeight: 600, color: '#fff' }}>{src.name}</div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>{src.fullName}</div>
              </div>
              <span className={src.status === 'valid' ? 'tf-badge tf-badge-green' : 'tf-badge tf-badge-red'}>
                {src.status === 'valid' ? <><CheckCircle size={10} /> Valid</> : <><AlertTriangle size={10} /> Outlier</>}
              </span>
            </div>
            <div style={{ fontSize: '28px', fontWeight: 700, color: src.status === 'valid' ? '#fff' : 'var(--color-tf-red)', marginBottom: '2px' }}>
              {src.rainfall.toFixed(1)} mm
            </div>
            <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', marginBottom: '8px' }}>Rainfall (1h)</div>
            <SparklineChart
              data={generateSparkline(src.rainfall, 30, src.status === 'outlier')}
              color={src.status === 'valid' ? '#10b981' : '#ef4444'}
            />
            <div style={{ display: 'flex', gap: '16px', marginTop: '8px', paddingTop: '8px', borderTop: '1px solid var(--color-tf-border)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: 'var(--color-tf-text-dim)' }}>
                <Thermometer size={11} /> {src.temperature}°C
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: 'var(--color-tf-text-dim)' }}>
                <Droplets size={11} /> {src.humidity}%
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: 'var(--color-tf-text-dim)' }}>
                <Wind size={11} /> {src.wind} km/h
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Consensus + Policy Evaluation */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
        {/* Consensus Engine */}
        <div className="tf-card">
          <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#fff', marginBottom: '4px' }}>Consensus Engine</h3>
          <p style={{ fontSize: '12px', color: 'var(--color-tf-text-dim)', marginBottom: '16px' }}>{data.consensus.agreeSources} out of {data.consensus.totalSources} sources agree</p>

          <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
            {/* Circular indicator */}
            <div style={{ position: 'relative', width: '100px', height: '100px' }}>
              <svg viewBox="0 0 100 100" style={{ width: '100px', height: '100px', transform: 'rotate(-90deg)' }}>
                <circle cx="50" cy="50" r="40" fill="none" stroke="var(--color-tf-border)" strokeWidth="8" />
                <circle cx="50" cy="50" r="40" fill="none" stroke={data.consensus.achieved ? 'var(--color-tf-green)' : 'var(--color-tf-red)'} strokeWidth="8"
                  strokeDasharray={`${(data.consensus.agreeSources / data.consensus.totalSources) * 251} 251`}
                  strokeLinecap="round"
                />
              </svg>
              <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ fontSize: '22px', fontWeight: 700, color: '#fff' }}>{data.consensus.agreeSources} / {data.consensus.totalSources}</div>
                <div style={{ fontSize: '8px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase' }}>Sources</div>
              </div>
            </div>

            {/* Source list */}
            <div style={{ flex: 1 }}>
              {data.sources.map(src => (
                <div key={src.id} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px', fontSize: '12px' }}>
                  {src.status === 'valid' ? <CheckCircle size={14} color="var(--color-tf-green)" /> : <XCircle size={14} color="var(--color-tf-red)" />}
                  <span style={{ color: 'var(--color-tf-text-muted)' }}>{src.name}</span>
                  <span style={{ marginLeft: 'auto', fontWeight: 600, color: src.status === 'valid' ? '#fff' : 'var(--color-tf-red)' }}>{src.rainfall.toFixed(1)} mm</span>
                </div>
              ))}
              <div style={{ borderTop: '1px solid var(--color-tf-border)', marginTop: '8px', paddingTop: '8px' }}>
                <div style={{ fontSize: '11px', color: 'var(--color-tf-text-dim)' }}>Trusted Rainfall (Median)</div>
                <div style={{ fontSize: '16px', fontWeight: 700, color: '#fff' }}>{data.consensus.trustedRainfall.toFixed(1)} mm</div>
              </div>
            </div>

            {/* Tolerance info */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ padding: '8px 12px', backgroundColor: 'var(--color-tf-surface)', border: '1px solid var(--color-tf-border)', borderRadius: '6px' }}>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>Tolerance: ±{data.consensus.tolerance} mm</div>
              </div>
              <div style={{ padding: '8px 12px', backgroundColor: 'var(--color-tf-surface)', border: '1px solid var(--color-tf-border)', borderRadius: '6px' }}>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>Outlier Detection:</div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>Statistical Deviation</div>
              </div>
              <div style={{ padding: '8px 12px', borderRadius: '6px' }}>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>Status:</div>
                <div style={{ fontSize: '11px', fontWeight: 600, color: data.consensus.achieved ? 'var(--color-tf-green)' : 'var(--color-tf-red)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  {data.consensus.achieved ? <><CheckCircle size={12} /> Consensus Achieved</> : <><XCircle size={12} /> No Consensus</>}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Policy Evaluation */}
        <div className="tf-card">
          <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#fff', marginBottom: '4px' }}>Policy Evaluation</h3>
          <p style={{ fontSize: '12px', color: 'var(--color-tf-text-dim)', marginBottom: '16px' }}>Checking if conditions are met</p>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-around' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '28px', fontWeight: 700, color: '#fff' }}>{data.evaluation.rainfall.toFixed(1)} mm</div>
              <div style={{ fontSize: '11px', color: 'var(--color-tf-text-dim)' }}>vs. ≥ {data.evaluation.threshold} mm threshold</div>
              <div style={{ fontSize: '11px', color: 'var(--color-tf-text-dim)' }}>(60 minutes)</div>
            </div>

            <div style={{ textAlign: 'center' }}>
              <div style={{
                width: '56px', height: '56px', borderRadius: '50%',
                backgroundColor: data.evaluation.triggered ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 8px',
              }}>
                {data.evaluation.triggered ? <CheckCircle size={28} color="var(--color-tf-green)" /> : <XCircle size={28} color="var(--color-tf-red)" />}
              </div>
              <div style={{ fontSize: '18px', fontWeight: 700, color: data.evaluation.triggered ? 'var(--color-tf-green)' : 'var(--color-tf-red)' }}>
                TRIGGER<br />{data.evaluation.triggered ? 'SATISFIED' : 'NOT MET'}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--color-tf-text-dim)', marginTop: '4px' }}>
                {data.evaluation.triggered ? 'Policy conditions met for settlement.' : 'Conditions not met.'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Demo Scenario Controls */}
      <div className="tf-card">
        <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#fff', marginBottom: '4px' }}>Demo Scenario Controls</h3>
        <p style={{ fontSize: '12px', color: 'var(--color-tf-text-dim)', marginBottom: '16px' }}>Test different weather conditions to see how the system responds.</p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
          {scenarios.map(s => (
            <button
              key={s.key}
              onClick={() => setScenario(s.key)}
              style={{
                padding: '14px',
                backgroundColor: scenario === s.key ? 'rgba(16,185,129,0.08)' : 'var(--color-tf-surface)',
                border: scenario === s.key ? '1px solid var(--color-tf-green)' : '1px solid var(--color-tf-border)',
                borderRadius: '8px',
                cursor: 'pointer',
                textAlign: 'left',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                transition: 'all 0.15s',
              }}
            >
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '13px', fontWeight: 600, color: s.color, marginBottom: '2px' }}>{s.label}</div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>{s.sub}</div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>{s.values}</div>
              </div>
              <Play size={16} fill={scenario === s.key ? 'var(--color-tf-green)' : 'var(--color-tf-text-dim)'} color={scenario === s.key ? 'var(--color-tf-green)' : 'var(--color-tf-text-dim)'} />
            </button>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
