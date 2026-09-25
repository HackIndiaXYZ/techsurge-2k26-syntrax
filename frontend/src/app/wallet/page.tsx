'use client';

import { useEffect, useState, useCallback } from 'react';
import AppLayout from '@/components/AppLayout';
import { api } from '@/lib/api';
import { useApp } from '@/lib/context';
import { WalletResponse } from '@/lib/types';
import { Wallet, CreditCard, RefreshCw, ArrowRight, Download, BarChart3, Zap, CheckCircle, XCircle, AlertTriangle, Clock, Info, Loader2, WifiOff } from 'lucide-react';

export default function WalletPage() {
  const { identity, identityLoading } = useApp();
  const [wallet, setWallet] = useState<WalletResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadWallet = useCallback(async () => {
    if (!identity && !identityLoading) {
      setLoading(false);
      setRefreshing(false);
      return;
    }
    const walletId = identity?.policies?.[0]?.wallet_id;
    if (!walletId) {
      if (!identityLoading) {
        setLoading(false);
        setRefreshing(false);
      }
      return;
    }
    try {
      const w = await api.getWallet(walletId);
      setWallet(w);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load wallet');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [identity, identityLoading]);

  useEffect(() => { loadWallet(); }, [loadWallet]);

  const handleRefresh = () => {
    setRefreshing(true);
    loadWallet();
  };

  const paiseToInr = (paise: number) => `₹${(paise / 100).toLocaleString()}`;

  if (loading) {
    return (
      <AppLayout>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px', gap: '16px' }}>
          <Loader2 size={32} color="var(--color-tf-green)" style={{ animation: 'spin 1s linear infinite' }} />
          <div style={{ fontSize: '14px', color: 'var(--color-tf-text-muted)' }}>Loading wallet data...</div>
        </div>
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </AppLayout>
    );
  }

  const txCount = wallet?.transactions.length ?? 0;
  const successfulPayouts = wallet?.transactions.filter(t => t.amount_paise > 0).length ?? 0;

  return (
    <AppLayout>
      {/* Error banner */}
      {error && (
        <div style={{ padding: '12px 16px', marginBottom: '16px', backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <WifiOff size={16} color="#ef4444" />
          <span style={{ fontSize: '12px', color: '#ef4444' }}>{error}</span>
        </div>
      )}

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>Wallet &amp; Settlement</h1>
          <p style={{ fontSize: '13px', color: 'var(--color-tf-text-muted)', marginTop: '2px' }}>Secure. Transparent. Simulated for a safer tomorrow.</p>
        </div>
        <button className="tf-btn tf-btn-outline" style={{ padding: '8px 14px', fontSize: '12px' }} onClick={handleRefresh} disabled={refreshing}>
          <RefreshCw size={13} style={refreshing ? { animation: 'spin 1s linear infinite' } : {}} /> {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {/* Top row */}
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
          <div style={{ fontSize: '36px', fontWeight: 800, color: 'var(--color-tf-green)', marginBottom: '4px' }}>
            {wallet?.balance_inr_display || '₹0'}
          </div>
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
                <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--color-tf-green)' }}>{wallet?.balance_inr_display || '₹0'}</div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>{successfulPayouts} successful payout{successfulPayouts !== 1 ? 's' : ''}</div>
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
        </div>

        {/* Wallet status */}
        <div className="tf-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h3 style={{ fontSize: '13px', fontWeight: 600, color: '#fff' }}>Wallet Status</h3>
            <span className="tf-badge tf-badge-green"><div style={{ width: '5px', height: '5px', borderRadius: '50%', backgroundColor: 'var(--color-tf-green)' }} /> Active</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
            {[
              ['Wallet ID', wallet ? `${wallet.wallet_id.substring(0, 12)}...` : 'No wallet created yet'],
              ['Policy ID', wallet ? `${wallet.policy_id.substring(0, 12)}...` : 'No policy found'],
              ['Currency', `${wallet?.currency || 'INR'} (Simulated)`],
              ['Balance (paise)', wallet?.balance_paise?.toLocaleString() || '0'],
              ['Transactions', String(txCount)],
              ['Account Type', 'Synthetic Wallet'],
            ].map(([k, v]) => (
              <div key={k} style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '6px', borderBottom: '1px solid var(--color-tf-border)' }}>
                <span style={{ color: 'var(--color-tf-text-dim)' }}>{k}</span>
                <span style={{ color: '#fff', fontWeight: 500, fontFamily: k === 'Wallet ID' || k === 'Policy ID' ? 'monospace' : 'inherit', fontSize: '11px' }}>{v}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Transaction History */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: '16px', marginBottom: '16px' }}>
        <div className="tf-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#fff' }}>Transaction History</h3>
          </div>
          {txCount > 0 ? (
            <table className="tf-table">
              <thead>
                <tr>
                  <th>Date &amp; Time</th>
                  <th>Transaction ID</th>
                  <th>Payout ID</th>
                  <th>Amount</th>
                  <th>Balance After</th>
                </tr>
              </thead>
              <tbody>
                {wallet!.transactions.map(tx => (
                  <tr key={tx.transaction_id}>
                    <td style={{ fontSize: '11px' }}>{new Date(tx.created_at).toLocaleString()}</td>
                    <td style={{ fontWeight: 500, color: '#fff', fontSize: '11px', fontFamily: 'monospace' }}>{tx.transaction_id.substring(0, 12)}...</td>
                    <td style={{ fontSize: '11px', fontFamily: 'monospace' }}>{tx.payout_id.substring(0, 12)}...</td>
                    <td style={{ color: tx.amount_paise > 0 ? 'var(--color-tf-green)' : 'var(--color-tf-text-dim)', fontWeight: 500 }}>
                      {tx.amount_paise > 0 ? `+ ${paiseToInr(tx.amount_paise)}` : paiseToInr(tx.amount_paise)}
                    </td>
                    <td style={{ fontWeight: 500, color: '#fff' }}>{paiseToInr(tx.balance_after_paise)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div style={{ padding: '24px', textAlign: 'center', color: 'var(--color-tf-text-dim)', fontSize: '12px' }}>
              No transactions yet. Run a simulation to generate wallet transactions.
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <a href="/weather" className="tf-card" style={{ cursor: 'pointer', textDecoration: 'none', color: 'inherit' }}>
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
          </a>
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
        </div>
      </div>

      {/* Important Notice */}
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

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </AppLayout>
  );
}
