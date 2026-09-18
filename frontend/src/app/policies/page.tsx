'use client';

import AppLayout from '@/components/AppLayout';
import { policies } from '@/lib/mock-data';
import { Plus, CloudRain, Radio, Zap, ShieldCheck, Eye, ChevronLeft, ChevronRight } from 'lucide-react';

export default function PoliciesPage() {
  const primary = policies[0];

  return (
    <AppLayout>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>Your Policies</h1>
          <p style={{ fontSize: '13px', color: 'var(--color-tf-text-muted)', marginTop: '2px' }}>Active climate protection for a more secure tomorrow.</p>
        </div>
        <button className="tf-btn tf-btn-primary" style={{ padding: '8px 16px', fontSize: '12px' }}>
          <Plus size={14} /> Add New Policy
        </button>
      </div>

      {/* Primary Policy Card */}
      <div style={{
        backgroundColor: 'var(--color-tf-card)',
        border: '1px solid var(--color-tf-border)',
        borderRadius: '10px',
        padding: '24px',
        marginBottom: '20px',
        display: 'grid',
        gridTemplateColumns: '1fr 280px',
        gap: '24px',
        backgroundImage: 'linear-gradient(135deg, rgba(16,185,129,0.03) 0%, transparent 50%)',
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <CloudRain size={24} color="var(--color-tf-green)" />
            <div>
              <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#fff' }}>Rainfall Index Protection</h2>
              <p style={{ fontSize: '12px', color: 'var(--color-tf-text-dim)' }}>Parametric insurance based on verified rainfall data.</p>
            </div>
          </div>
          <span className="tf-badge tf-badge-green" style={{ fontSize: '11px', padding: '4px 12px', marginBottom: '16px', display: 'inline-flex' }}>Active</span>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginTop: '16px' }}>
            <div>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Policy ID</div>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#fff', marginTop: '2px' }}>SYN-F03-001</div>
            </div>
            <div>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Region</div>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#fff', marginTop: '2px' }}>Tamil Nadu (TN)</div>
            </div>
            <div>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Type</div>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#fff', marginTop: '2px' }}>Rainfall Index</div>
            </div>
            <div>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Coverage Period</div>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#fff', marginTop: '2px' }}>Aug 2026 - Dec 2026</div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--color-tf-border)' }}>
            <div>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Trigger</div>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#fff', marginTop: '2px' }}>≥ 100 mm / 60 minutes</div>
            </div>
            <div>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Payout (Simulated)</div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-tf-green)', marginTop: '2px' }}>₹10,000</div>
            </div>
            <div>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Status</div>
              <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--color-tf-green)', marginTop: '2px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: 'var(--color-tf-green)' }} /> Active
              </div>
            </div>
            <div>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Auto Settlement</div>
              <div style={{ fontSize: '13px', fontWeight: 500, color: '#fff', marginTop: '2px' }}>Enabled</div>
            </div>
          </div>
        </div>

        {/* Right side features */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px 12px', backgroundColor: 'rgba(16,185,129,0.05)', border: '1px solid var(--color-tf-border)', borderRadius: '8px' }}>
            <Radio size={18} color="var(--color-tf-green)" />
            <div>
              <div style={{ fontSize: '12px', fontWeight: 600, color: '#fff' }}>Real-time Monitoring</div>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>Continuous weather data validation</div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px 12px', backgroundColor: 'rgba(16,185,129,0.05)', border: '1px solid var(--color-tf-border)', borderRadius: '8px' }}>
            <Zap size={18} color="var(--color-tf-green)" />
            <div>
              <div style={{ fontSize: '12px', fontWeight: 600, color: '#fff' }}>Automatic Settlement</div>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>Triggered when conditions are met</div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px 12px', backgroundColor: 'rgba(16,185,129,0.05)', border: '1px solid var(--color-tf-border)', borderRadius: '8px' }}>
            <ShieldCheck size={18} color="var(--color-tf-green)" />
            <div>
              <div style={{ fontSize: '12px', fontWeight: 600, color: '#fff' }}>Transparent &amp; Fair</div>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>Verified data. No manual intervention.</div>
            </div>
          </div>

          <button className="tf-btn tf-btn-primary" style={{ marginTop: '4px', width: '100%', padding: '10px' }}>
            View Policy Details →
          </button>
        </div>
      </div>

      {/* All Policies Table */}
      <div className="tf-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#fff' }}>All Policies</h3>
            <p style={{ fontSize: '12px', color: 'var(--color-tf-text-dim)', marginTop: '2px' }}>Manage and view your climate protection policies.</p>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <select style={{
              padding: '6px 12px', backgroundColor: 'var(--color-tf-surface)', border: '1px solid var(--color-tf-border)',
              borderRadius: '6px', color: 'var(--color-tf-text-muted)', fontSize: '12px', outline: 'none',
            }}>
              <option>All Status</option>
              <option>Active</option>
              <option>Inactive</option>
            </select>
            <select style={{
              padding: '6px 12px', backgroundColor: 'var(--color-tf-surface)', border: '1px solid var(--color-tf-border)',
              borderRadius: '6px', color: 'var(--color-tf-text-muted)', fontSize: '12px', outline: 'none',
            }}>
              <option>All Regions</option>
              <option>Tamil Nadu</option>
              <option>Maharashtra</option>
            </select>
            <input placeholder="Search policies..." style={{
              padding: '6px 12px', backgroundColor: 'var(--color-tf-surface)', border: '1px solid var(--color-tf-border)',
              borderRadius: '6px', color: 'var(--color-tf-text)', fontSize: '12px', outline: 'none', width: '160px',
            }} />
          </div>
        </div>

        <table className="tf-table">
          <thead>
            <tr>
              <th>Policy ID</th>
              <th>Policy Name</th>
              <th>Region</th>
              <th>Trigger</th>
              <th>Payout</th>
              <th>Status</th>
              <th>Coverage Period</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {policies.map(p => (
              <tr key={p.id}>
                <td style={{ fontFamily: 'monospace', fontSize: '12px', color: '#fff' }}>{p.id}</td>
                <td style={{ fontWeight: 500, color: '#fff' }}>{p.name}</td>
                <td>{p.region}</td>
                <td>{p.trigger}</td>
                <td style={{ color: 'var(--color-tf-green)' }}>{p.payout}</td>
                <td>
                  <span className={
                    p.status === 'Active' ? 'tf-badge tf-badge-green' :
                    p.status === 'Expiring Soon' ? 'tf-badge tf-badge-orange' :
                    'tf-badge tf-badge-red'
                  }>
                    <div style={{ width: '5px', height: '5px', borderRadius: '50%', backgroundColor: p.status === 'Active' ? 'var(--color-tf-green)' : p.status === 'Expiring Soon' ? 'var(--color-tf-orange)' : 'var(--color-tf-red)' }} />
                    {p.status}
                  </span>
                </td>
                <td>{p.period}</td>
                <td>
                  <button className="tf-btn tf-btn-outline" style={{ padding: '4px 10px', fontSize: '11px' }}>
                    <Eye size={12} /> View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '12px', paddingTop: '12px', borderTop: '1px solid var(--color-tf-border)' }}>
          <span style={{ fontSize: '12px', color: 'var(--color-tf-text-dim)' }}>Showing 1 to {policies.length} of {policies.length} policies</span>
          <div style={{ display: 'flex', gap: '4px' }}>
            <button style={{ width: '28px', height: '28px', borderRadius: '6px', backgroundColor: 'var(--color-tf-surface)', border: '1px solid var(--color-tf-border)', color: 'var(--color-tf-text-dim)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><ChevronLeft size={14} /></button>
            <button style={{ width: '28px', height: '28px', borderRadius: '6px', backgroundColor: 'var(--color-tf-green)', border: 'none', color: '#0a0e14', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600, fontSize: '12px' }}>1</button>
            <button style={{ width: '28px', height: '28px', borderRadius: '6px', backgroundColor: 'var(--color-tf-surface)', border: '1px solid var(--color-tf-border)', color: 'var(--color-tf-text-dim)', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><ChevronRight size={14} /></button>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
