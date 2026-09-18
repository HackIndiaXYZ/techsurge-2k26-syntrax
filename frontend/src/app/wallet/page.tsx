'use client';

import AppLayout from '@/components/AppLayout';
import { walletTransactions } from '@/lib/mock-data';
import { Wallet, CreditCard, RefreshCw, ArrowRight, Download, BarChart3, Zap, CheckCircle, XCircle, AlertTriangle, Clock, Info } from 'lucide-react';

export default function WalletPage() {
  return (
    <AppLayout>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>Wallet &amp; Settlement</h1>
          <p style={{ fontSize: '13px', color: 'var(--color-tf-text-muted)', marginTop: '2px' }}>Secure. Transparent. Simulated for a safer tomorrow.</p>
        </div>
        <button className="tf-btn tf-btn-outline" style={{ padding: '8px 14px', fontSize: '12px' }}>
          <RefreshCw size={13} /> Refresh
        </button>
      </div>

      {/* Top row: wallet + settlement + status */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 280px', gap: '12px', marginBottom: '16px' }}>
        {/* Synthetic Wallet */}
        <div className="tf-card" style={{ backgroundImage: 'linear-gradient(135deg, rgba(16,185,129,0.05) 0%, transparent 60%)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Wallet size={18} color="var(--color-tf-green)" />
              <span style={{ fontSize: '14px', fontWeight: 600, color: '#fff' }}>Synthetic Wallet</span>
            </div>
            <span className="tf-badge" style={{ backgroundColor: 'rgba(16,185,129,0.15)', color: 'var(--color-tf-green)', fontSize: '9px', padding: '2px 8px' }}>Simulated Mode</span>
          </div>
          <div style={{ fontSize: '36px', fontWeight: 800, color: 'var(--color-tf-green)', marginBottom: '4px' }}>₹10,000</div>
          <div style={{ fontSize: '12px', color: 'var(--color-tf-text-dim)', marginBottom: '16px' }}>Available Balance (Simulated)</div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button className="tf-btn tf-btn-outline" style={{ flex: 1, padding: '8px', fontSize: '12px' }}>View Transactions</button>
            <button className="tf-btn tf-btn-outline" style={{ flex: 1, padding: '8px', fontSize: '12px' }}>Export Statement</button>
          </div>
        </div>

        {/* Settlement summary */}
        <div className="tf-card">
          <div style={{ display: 'grid', gridTemplateRows: '1fr 1fr', gap: '16px', height: '100%' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '10px', backgroundColor: 'rgba(16,185,129,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <CreditCard size={20} color="var(--color-tf-green)" />
              </div>
              <div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase' }}>Total Settlements</div>
                <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--color-tf-green)' }}>₹10,000</div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>1 successful payout</div>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '10px', backgroundColor: 'rgba(100,116,139,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Clock size={20} color="var(--color-tf-text-dim)" />
              </div>
              <div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase' }}>Pending Settlements</div>
                <div style={{ fontSize: '18px', fontWeight: 700, color: '#fff' }}>₹0</div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>No pending payouts</div>
              </div>
            </div>
          </div>
          <div style={{ borderTop: '1px solid var(--color-tf-border)', paddingTop: '12px', marginTop: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Clock size={12} color="var(--color-tf-text-dim)" />
            <div>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>Last Settlement</div>
              <div style={{ fontSize: '12px', color: '#fff', fontWeight: 500 }}>18 Sep 2026, 10:24 AM</div>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>Event EVT-1042</div>
            </div>
          </div>
        </div>

        {/* Wallet status */}
        <div className="tf-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h3 style={{ fontSize: '13px', fontWeight: 600, color: '#fff' }}>Wallet Status</h3>
            <span className="tf-badge tf-badge-green"><div style={{ width: '5px', height: '5px', borderRadius: '50%', backgroundColor: 'var(--color-tf-green)' }} /> Active</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
            {[
              ['Policyholder', 'Sanju'],
              ['Wallet ID', 'WLT-001'],
              ['Currency', 'INR (Simulated)'],
              ['KYC Status', 'Verified (Demo)'],
              ['Account Type', 'Synthetic Wallet'],
              ['Created On', '01 Sep 2026'],
            ].map(([k, v]) => (
              <div key={k} style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '6px', borderBottom: '1px solid var(--color-tf-border)' }}>
                <span style={{ color: 'var(--color-tf-text-dim)' }}>{k}</span>
                <span style={{ color: '#fff', fontWeight: 500 }}>{v}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Transaction History + Quick Actions */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: '16px', marginBottom: '16px' }}>
        <div className="tf-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#fff' }}>Transaction History</h3>
            <a href="#" style={{ fontSize: '11px', color: 'var(--color-tf-green)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px' }}>View All <ArrowRight size={10} /></a>
          </div>
          <table className="tf-table">
            <thead>
              <tr>
                <th>Date &amp; Time</th>
                <th>Event ID</th>
                <th>Description</th>
                <th>Amount</th>
                <th>Balance</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {walletTransactions.map((tx, i) => (
                <tr key={i}>
                  <td style={{ fontSize: '11px' }}>{tx.date}</td>
                  <td style={{ fontWeight: 500, color: '#fff', fontSize: '12px' }}>{tx.eventId}</td>
                  <td style={{ fontSize: '12px' }}>{tx.description}</td>
                  <td style={{ color: tx.amount > 0 ? 'var(--color-tf-green)' : 'var(--color-tf-text-dim)', fontWeight: 500 }}>
                    {tx.amount > 0 ? `+ ₹${tx.amount.toLocaleString()}` : '₹0'}
                  </td>
                  <td style={{ fontWeight: 500, color: '#fff' }}>₹{tx.balance.toLocaleString()}</td>
                  <td>
                    <span className={
                      tx.status === 'Completed' ? 'tf-badge tf-badge-green' :
                      tx.status === 'Duplicate' ? 'tf-badge tf-badge-orange' :
                      'tf-badge tf-badge-red'
                    }>
                      {tx.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Quick Actions */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div className="tf-card" style={{ cursor: 'pointer' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: 'rgba(16,185,129,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Zap size={18} color="var(--color-tf-green)" />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '13px', fontWeight: 600, color: '#fff' }}>Simulate Settlement</div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>Run a demo settlement event</div>
              </div>
              <ArrowRight size={14} color="var(--color-tf-text-dim)" />
            </div>
          </div>
          <div className="tf-card" style={{ cursor: 'pointer' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: 'rgba(16,185,129,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Download size={18} color="var(--color-tf-green)" />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '13px', fontWeight: 600, color: '#fff' }}>Download Statement</div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>Export wallet transaction history</div>
              </div>
              <ArrowRight size={14} color="var(--color-tf-text-dim)" />
            </div>
          </div>
          <div className="tf-card" style={{ cursor: 'pointer' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: 'rgba(16,185,129,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <BarChart3 size={18} color="var(--color-tf-green)" />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '13px', fontWeight: 600, color: '#fff' }}>View Analytics</div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>See settlement insights</div>
              </div>
              <ArrowRight size={14} color="var(--color-tf-text-dim)" />
            </div>
          </div>
        </div>
      </div>

      {/* Settlement Insights + Important Notice */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="tf-card">
          <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#fff', marginBottom: '16px' }}>Settlement Insights</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
            {[
              { icon: <BarChart3 size={18} color="var(--color-tf-green)" />, val: '2', label: 'Total Events' },
              { icon: <CheckCircle size={18} color="var(--color-tf-green)" />, val: '1', label: 'Successful' },
              { icon: <XCircle size={18} color="var(--color-tf-red)" />, val: '1', label: 'No Payout' },
              { icon: <AlertTriangle size={18} color="var(--color-tf-orange)" />, val: '1', label: 'Duplicate' },
            ].map((item, i) => (
              <div key={i} style={{ textAlign: 'center', padding: '12px', backgroundColor: 'var(--color-tf-surface)', borderRadius: '8px', border: '1px solid var(--color-tf-border)' }}>
                <div style={{ marginBottom: '6px' }}>{item.icon}</div>
                <div style={{ fontSize: '20px', fontWeight: 700, color: '#fff' }}>{item.val}</div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>{item.label}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="tf-card" style={{ borderColor: 'rgba(245, 158, 11, 0.2)' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
            <Info size={20} color="var(--color-tf-orange)" style={{ marginTop: '2px', flexShrink: 0 }} />
            <div>
              <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#fff', marginBottom: '8px' }}>Important Notice</h3>
              <p style={{ fontSize: '12px', color: 'var(--color-tf-text-muted)', lineHeight: 1.6 }}>
                This is a synthetic wallet for demonstration purposes only. No real money is involved. This prototype settles against a predefined weather index; the index does not guarantee that the payout equals the policyholder&apos;s actual loss.
              </p>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
