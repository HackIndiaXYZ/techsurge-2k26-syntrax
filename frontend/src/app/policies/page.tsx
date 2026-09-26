'use client';

import { useEffect, useState } from 'react';
import AppLayout from '@/components/AppLayout';
import { api } from '@/lib/api';
import { useApp } from '@/lib/context';
import { PolicyResponse } from '@/lib/types';
import { Plus, CloudRain, Radio, Zap, ShieldCheck, Eye, ChevronLeft, ChevronRight, Loader2, WifiOff, CreditCard } from 'lucide-react';

export default function PoliciesPage() {
  const { identity, identityLoading } = useApp();
  const [policy, setPolicy] = useState<PolicyResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [paymentMessage, setPaymentMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!identity && !identityLoading) {
        setLoading(false);
        return;
      }
      const policyId = identity?.policies?.[0]?.policy_id;
      if (!policyId) {
        if (!identityLoading) setLoading(false);
        return;
      }
      try {
        const p = await api.getPolicy(policyId);
        if (!cancelled) setPolicy(p);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load policy');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [identity, identityLoading]);

  if (loading) {
    return (
      <AppLayout>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px', gap: '16px' }}>
          <Loader2 size={32} color="var(--color-tf-green)" style={{ animation: 'spin 1s linear infinite' }} />
          <div style={{ fontSize: '14px', color: 'var(--color-tf-text-muted)' }}>Loading policy data...</div>
        </div>
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </AppLayout>
    );
  }

  const formatDate = (iso: string | null | undefined) => {
    if (!iso) return 'N/A';
    try { return new Date(iso).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' }); }
    catch { return String(iso); }
  };

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
          <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>Your Policies</h1>
          <p style={{ fontSize: '13px', color: 'var(--color-tf-text-muted)', marginTop: '2px' }}>Active climate protection for a more secure tomorrow.</p>
        </div>
        <button 
          className="tf-btn tf-btn-primary" 
          style={{ padding: '8px 16px', fontSize: '12px', opacity: 0.5, cursor: 'not-allowed' }}
          disabled
          title="Policy purchasing will be available in Phase 3."
        >
          <Plus size={14} /> Add New Policy
        </button>
      </div>

      {/* Primary Policy Card */}
      {policy && (
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
                <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#fff' }}>{policy.name}</h2>
                <p style={{ fontSize: '12px', color: 'var(--color-tf-text-dim)' }}>Parametric insurance based on verified rainfall data.</p>
              </div>
            </div>
            <span className={`tf-badge ${policy.status === 'ACTIVE' ? 'tf-badge-green' : policy.status === 'EXPIRED' ? 'tf-badge-red' : policy.status === 'PAYMENT_PENDING' ? 'tf-badge-orange' : policy.status === 'DRAFT' ? 'tf-badge-orange' : 'tf-badge-orange'}`} style={{ fontSize: '11px', padding: '4px 12px', marginBottom: '16px', display: 'inline-flex' }}>{policy.status === 'PAYMENT_PENDING' ? 'Payment Pending' : policy.status}</span>

            {/* Phase 3C: Pay Premium button */}
            {policy.status === 'PAYMENT_PENDING' && policy.premium_amount_paise && (
              <button
                className="tf-btn tf-btn-primary"
                disabled={paymentLoading}
                style={{ marginLeft: '12px', padding: '6px 20px', fontSize: '12px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                onClick={async () => {
                  setPaymentLoading(true);
                  setPaymentMessage(null);
                  try {
                    const order = await api.createPaymentOrder(policy.policy_id);
                    const options = {
                      key: order.razorpay_key_id,
                      amount: order.amount_paise,
                      currency: order.currency,
                      name: 'TerraFlux',
                      description: `Premium for ${policy.name}`,
                      order_id: order.razorpay_order_id,
                      handler: async (response: { razorpay_order_id: string; razorpay_payment_id: string; razorpay_signature: string }) => {
                        try {
                          const result = await api.verifyPayment(policy.policy_id, {
                            razorpay_order_id: response.razorpay_order_id,
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_signature: response.razorpay_signature,
                          });
                          if (result.verified && result.policy_status === 'ACTIVE') {
                            setPaymentMessage('Payment verified! Policy is now ACTIVE.');
                            setPolicy({ ...policy, status: 'ACTIVE' });
                          } else {
                            setPaymentMessage('Payment verification failed.');
                          }
                        } catch {
                          setPaymentMessage('Payment verification error.');
                        }
                        setPaymentLoading(false);
                      },
                      modal: {
                        ondismiss: () => {
                          setPaymentLoading(false);
                          setPaymentMessage('Payment cancelled.');
                        },
                      },
                      theme: { color: '#10b981' },
                    };
                    const rzp = new (window as any).Razorpay(options);
                    rzp.open();
                  } catch (e) {
                    setPaymentMessage(e instanceof Error ? e.message : 'Failed to create order');
                    setPaymentLoading(false);
                  }
                }}
              >
                <CreditCard size={14} />
                {paymentLoading ? 'Processing...' : `Pay Premium ${policy.premium_amount_inr_display || ''}`}
              </button>
            )}
            {paymentMessage && (
              <div style={{ marginTop: '8px', fontSize: '12px', color: paymentMessage.includes('ACTIVE') ? 'var(--color-tf-green)' : '#f59e0b' }}>
                {paymentMessage}
              </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginTop: '16px' }}>
              <div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Policy ID</div>
                <div style={{ fontSize: '13px', fontWeight: 500, color: '#fff', marginTop: '2px', fontFamily: 'monospace' }}>{policy.policy_id.substring(0, 12)}...</div>
              </div>
              <div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Region</div>
                <div style={{ fontSize: '13px', fontWeight: 500, color: '#fff', marginTop: '2px' }}>{policy.region_id.substring(0, 12)}...</div>
              </div>
              <div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Type</div>
                <div style={{ fontSize: '13px', fontWeight: 500, color: '#fff', marginTop: '2px' }}>Rainfall Index</div>
              </div>
              <div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Coverage Period</div>
                <div style={{ fontSize: '13px', fontWeight: 500, color: '#fff', marginTop: '2px' }}>{formatDate(policy.valid_from)} - {formatDate(policy.valid_until)}</div>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--color-tf-border)' }}>
              <div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Trigger</div>
                <div style={{ fontSize: '13px', fontWeight: 500, color: '#fff', marginTop: '2px' }}>{policy.trigger_operator} {policy.trigger_threshold_mm} mm / {policy.observation_window_minutes} minutes</div>
              </div>
              <div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Payout (Simulated)</div>
                <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-tf-green)', marginTop: '2px' }}>{policy.payout_amount_inr_display}</div>
              </div>
              <div>
                <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Status</div>
                <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--color-tf-green)', marginTop: '2px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: 'var(--color-tf-green)' }} /> {policy.status}
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
          </div>
        </div>
      )}

      {/* All Policies Table */}
      <div className="tf-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#fff' }}>All Policies</h3>
            <p style={{ fontSize: '12px', color: 'var(--color-tf-text-dim)', marginTop: '2px' }}>Manage and view your climate protection policies.</p>
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
            </tr>
          </thead>
          <tbody>
            {policy && (
              <tr>
                <td style={{ fontFamily: 'monospace', fontSize: '12px', color: '#fff' }}>{policy.policy_id.substring(0, 12)}...</td>
                <td style={{ fontWeight: 500, color: '#fff' }}>{policy.name}</td>
                <td>{policy.region_id.substring(0, 12)}...</td>
                <td>{policy.trigger_operator} {policy.trigger_threshold_mm} mm / {policy.observation_window_minutes} min</td>
                <td style={{ color: 'var(--color-tf-green)' }}>{policy.payout_amount_inr_display}</td>
                <td>
                  <span className={`tf-badge ${policy.status === 'ACTIVE' ? 'tf-badge-green' : policy.status === 'EXPIRED' ? 'tf-badge-red' : 'tf-badge-orange'}`}>
                    <div style={{ width: '5px', height: '5px', borderRadius: '50%', backgroundColor: policy.status === 'ACTIVE' ? 'var(--color-tf-green)' : policy.status === 'EXPIRED' ? '#ef4444' : '#f59e0b' }} />
                    {policy.status === 'PAYMENT_PENDING' ? 'Payment Pending' : policy.status}
                  </span>
                </td>
                <td>{formatDate(policy.valid_from)} - {formatDate(policy.valid_until)}</td>
              </tr>
            )}
            {!policy && !error && (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', color: 'var(--color-tf-text-dim)' }}>No policies found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </AppLayout>
  );
}
