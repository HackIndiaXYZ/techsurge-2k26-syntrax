'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Leaf, Mail, Lock, Eye, EyeOff, Play, ShieldCheck, Cloud, Shield, Umbrella, Users, CheckCircle, BarChart3, AlertCircle, Loader2 } from 'lucide-react';
import { createClient } from '@/lib/supabase';
import Link from 'next/link';

export default function LoginPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const supabase = createClient();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    
    if (!email || !password) {
      setError('Email and password are required');
      setLoading(false);
      return;
    }

    try {
      const { data, error: authError } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (authError) throw authError;

      if (data.session) {
        router.push('/dashboard');
        router.refresh();
      }
    } catch (err: any) {
      if (err.message && err.message.toLowerCase().includes('email not confirmed')) {
        setError('Please confirm your email address before signing in. Check your inbox for the confirmation link.');
      } else if (err.message && err.message.toLowerCase().includes('rate limit')) {
        setError('Login rate limit exceeded. Please wait a few minutes.');
      } else {
        setError(err.message || 'Failed to sign in');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#0a0e14' }}>
      {/* Top bar */}
      <div style={{
        height: '48px',
        backgroundColor: '#0c1117',
        borderBottom: '1px solid var(--color-tf-border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '28px', height: '28px', borderRadius: '6px',
            background: 'linear-gradient(135deg, #10b981, #059669)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Leaf size={16} color="#0a0e14" strokeWidth={2.5} />
          </div>
          <span style={{ fontSize: '15px', fontWeight: 700, letterSpacing: '2px', color: '#e2e8f0' }}>TERRAFLUX</span>
          <span style={{ fontSize: '9px', color: 'var(--color-tf-text-dim)', letterSpacing: '1.5px', marginLeft: '8px', textTransform: 'uppercase' }}>Trusted Weather. Automatic Protection.</span>
        </div>
        <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)', letterSpacing: '1px', textTransform: 'uppercase' }}>
          Real Weather. Verified Data. Fair Outcomes.
        </div>
      </div>

      {/* Main content */}
      <div style={{ flex: 1, display: 'flex' }}>
        {/* Left panel - climate visual */}
        <div style={{
          flex: 1,
          position: 'relative',
          overflow: 'hidden',
          backgroundImage: 'url("https://images.unsplash.com/photo-1534274988757-a28bf1a57c17?w=1200&q=80")',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}>
          {/* Overlay */}
          <div style={{
            position: 'absolute',
            inset: 0,
            background: 'linear-gradient(135deg, rgba(10, 14, 20, 0.88) 0%, rgba(10, 14, 20, 0.55) 50%, rgba(10, 14, 20, 0.75) 100%)',
          }} />

          {/* Content */}
          <div style={{
            position: 'relative',
            zIndex: 1,
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            padding: '60px',
          }}>
            {/* Brand mark */}
            <div style={{ marginBottom: '24px' }}>
              <div style={{
                width: '64px', height: '64px', borderRadius: '16px',
                background: 'linear-gradient(135deg, #10b981, #059669)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                marginBottom: '20px',
              }}>
                <Leaf size={36} color="#0a0e14" strokeWidth={2} />
              </div>
              <h1 style={{ fontSize: '42px', fontWeight: 800, letterSpacing: '3px', color: '#fff', marginBottom: '12px' }}>TERRAFLUX</h1>
              <p style={{ fontSize: '18px', color: 'rgba(255,255,255,0.8)', lineHeight: 1.5, maxWidth: '420px' }}>
                Autonomous climate protection,<br />
                built on trusted weather intelligence.
              </p>
            </div>

            {/* Feature pills */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '40px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ width: '36px', height: '36px', borderRadius: '50%', backgroundColor: 'rgba(16,185,129,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <CheckCircle size={18} color="#10b981" />
                </div>
                <span style={{ fontSize: '14px', color: 'rgba(255,255,255,0.9)', fontWeight: 500 }}>Trusted Data</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ width: '36px', height: '36px', borderRadius: '50%', backgroundColor: 'rgba(16,185,129,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <BarChart3 size={18} color="#10b981" />
                </div>
                <span style={{ fontSize: '14px', color: 'rgba(255,255,255,0.9)', fontWeight: 500 }}>Fair Settlements</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ width: '36px', height: '36px', borderRadius: '50%', backgroundColor: 'rgba(16,185,129,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <ShieldCheck size={18} color="#10b981" />
                </div>
                <span style={{ fontSize: '14px', color: 'rgba(255,255,255,0.9)', fontWeight: 500 }}>A More Resilient Tomorrow</span>
              </div>
            </div>

            <p style={{ marginTop: '48px', fontSize: '14px', color: 'rgba(255,255,255,0.5)', fontStyle: 'italic' }}>
              Climate risks are real.<br />So is the solution.
            </p>
          </div>
        </div>

        {/* Right panel - login form */}
        <div style={{
          width: '480px',
          minWidth: '480px',
          backgroundColor: 'var(--color-tf-surface)',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          padding: '60px',
          borderLeft: '1px solid var(--color-tf-border)',
        }}>
          <h2 style={{ fontSize: '28px', fontWeight: 700, color: '#fff', marginBottom: '6px' }}>Welcome back</h2>
          <p style={{ fontSize: '14px', color: 'var(--color-tf-text-muted)', marginBottom: '32px' }}>Sign in to your TerraFlux account</p>

          <form onSubmit={handleLogin}>
            {/* Email */}
            <div style={{ marginBottom: '16px' }}>
              <label style={{ fontSize: '12px', color: 'var(--color-tf-text-muted)', fontWeight: 500, display: 'block', marginBottom: '6px' }}>Email</label>
              <div style={{ position: 'relative' }}>
                <Mail size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-tf-text-dim)' }} />
                <input
                  type="email"
                  placeholder="you@terraflux.com"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '11px 12px 11px 40px',
                    backgroundColor: 'var(--color-tf-bg)',
                    border: '1px solid var(--color-tf-border)',
                    borderRadius: '8px',
                    color: '#fff',
                    fontSize: '14px',
                    outline: 'none',
                  }}
                />
              </div>
            </div>

            {/* Password */}
            <div style={{ marginBottom: '8px' }}>
              <label style={{ fontSize: '12px', color: 'var(--color-tf-text-muted)', fontWeight: 500, display: 'block', marginBottom: '6px' }}>Password</label>
              <div style={{ position: 'relative' }}>
                <Lock size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-tf-text-dim)' }} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '11px 40px 11px 40px',
                    backgroundColor: 'var(--color-tf-bg)',
                    border: '1px solid var(--color-tf-border)',
                    borderRadius: '8px',
                    color: '#fff',
                    fontSize: '14px',
                    outline: 'none',
                  }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-tf-text-dim)' }}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <div style={{ textAlign: 'right', marginBottom: '24px' }}>
              <a href="#" style={{ fontSize: '12px', color: 'var(--color-tf-green)', textDecoration: 'none' }}>Forgot password?</a>
            </div>

            {/* Error message */}
            {error && (
              <div style={{ padding: '10px 12px', marginBottom: '16px', backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertCircle size={16} color="#ef4444" />
                <span style={{ fontSize: '13px', color: '#ef4444' }}>{error}</span>
              </div>
            )}

            {/* Sign in button */}
            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                padding: '12px',
                backgroundColor: 'var(--color-tf-green)',
                color: '#0a0e14',
                border: 'none',
                borderRadius: '8px',
                fontSize: '15px',
                fontWeight: 700,
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.7 : 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                transition: 'background-color 0.2s',
              }}
            >
              {loading ? (
                <>
                  <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
                  Signing in...
                  <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
                </>
              ) : (
                'Sign in →'
              )}
            </button>
          </form>

          <div style={{ marginTop: '24px', textAlign: 'center' }}>
            <span style={{ fontSize: '13px', color: 'var(--color-tf-text-muted)' }}>Don&apos;t have an account? </span>
            <Link href="/register" style={{ fontSize: '13px', color: 'var(--color-tf-green)', textDecoration: 'none', fontWeight: 500 }}>
              Create one
            </Link>
          </div>
          {/* Trust badge */}
          <div style={{
            marginTop: '24px',
            padding: '12px 16px',
            backgroundColor: 'rgba(16, 185, 129, 0.05)',
            border: '1px solid rgba(16, 185, 129, 0.15)',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
          }}>
            <ShieldCheck size={20} color="var(--color-tf-green)" />
            <div>
              <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-tf-text)' }}>Secure. Transparent. Impactful.</div>
              <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>Building climate resilience for farmers and communities.</div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div style={{
        height: '36px',
        backgroundColor: '#0c1117',
        borderTop: '1px solid var(--color-tf-border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        fontSize: '10px',
        color: 'var(--color-tf-text-dim)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Leaf size={12} color="var(--color-tf-green)" />
          <span style={{ fontWeight: 600, letterSpacing: '1.5px' }}>TERRAFLUX</span>
          <span style={{ margin: '0 8px', color: 'var(--color-tf-border-light)' }}>|</span>
          <span style={{ letterSpacing: '0.5px', textTransform: 'uppercase', fontSize: '9px' }}>Climate Intelligence for a More Resilient Tomorrow.</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Cloud size={10} /> Weather</span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Shield size={10} /> Trust</span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Umbrella size={10} /> Protection</span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Users size={10} /> People</span>
        </div>
      </div>
    </div>
  );
}
