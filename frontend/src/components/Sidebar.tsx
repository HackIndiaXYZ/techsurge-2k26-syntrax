'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, FileText, Radio, Wallet, Shield, Settings, LogOut, Leaf } from 'lucide-react';

const navItems = [
  { href: '/dashboard', label: 'Overview', icon: Home },
  { href: '/policies', label: 'Policies', icon: FileText },
  { href: '/weather', label: 'Live Monitor', icon: Radio },
  { href: '/wallet', label: 'Wallet', icon: Wallet },
  { href: '/events', label: 'Evidence', icon: Shield },
  { href: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside style={{
      width: '200px',
      minWidth: '200px',
      height: '100vh',
      backgroundColor: 'var(--color-tf-sidebar)',
      borderRight: '1px solid var(--color-tf-border)',
      display: 'flex',
      flexDirection: 'column',
      position: 'fixed',
      left: 0,
      top: 0,
      zIndex: 40,
    }}>
      {/* Logo */}
      <div style={{
        padding: '16px 16px 12px',
        borderBottom: '1px solid var(--color-tf-border)',
      }}>
        <Link href="/dashboard" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: 'linear-gradient(135deg, #10b981, #059669)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <Leaf size={18} color="#0a0e14" strokeWidth={2.5} />
          </div>
          <div>
            <div style={{ fontSize: '15px', fontWeight: 700, color: '#e2e8f0', letterSpacing: '1px' }}>TERRAFLUX</div>
            <div style={{ fontSize: '8px', color: 'var(--color-tf-text-dim)', letterSpacing: '1.5px', textTransform: 'uppercase' }}>Trusted Weather. Automatic Protection.</div>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: '12px 0', display: 'flex', flexDirection: 'column', gap: '2px' }}>
        {navItems.map(item => {
          const isActive = pathname === item.href || (item.href === '/dashboard' && pathname === '/');
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                padding: '10px 16px',
                fontSize: '13px',
                fontWeight: isActive ? 600 : 400,
                color: isActive ? 'var(--color-tf-green)' : 'var(--color-tf-text-muted)',
                textDecoration: 'none',
                borderLeft: isActive ? '3px solid var(--color-tf-green)' : '3px solid transparent',
                backgroundColor: isActive ? 'rgba(16, 185, 129, 0.08)' : 'transparent',
                transition: 'all 0.15s ease',
              }}
              onMouseEnter={e => {
                if (!isActive) {
                  (e.currentTarget as HTMLElement).style.backgroundColor = 'rgba(16, 185, 129, 0.04)';
                  (e.currentTarget as HTMLElement).style.color = 'var(--color-tf-text)';
                }
              }}
              onMouseLeave={e => {
                if (!isActive) {
                  (e.currentTarget as HTMLElement).style.backgroundColor = 'transparent';
                  (e.currentTarget as HTMLElement).style.color = 'var(--color-tf-text-muted)';
                }
              }}
            >
              <Icon size={16} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Climate message */}
      <div style={{
        padding: '12px 16px',
        fontSize: '9px',
        color: 'var(--color-tf-text-dim)',
        textTransform: 'uppercase',
        letterSpacing: '0.5px',
        lineHeight: 1.5,
      }}>
        Climate Intelligence<br />for a More<br />Resilient Tomorrow.
      </div>

      {/* User */}
      <div style={{
        padding: '12px 16px',
        borderTop: '1px solid var(--color-tf-border)',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
      }}>
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '50%',
          backgroundColor: 'var(--color-tf-green)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '12px',
          fontWeight: 700,
          color: '#0a0e14',
        }}>
          SA
        </div>
        <div>
          <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--color-tf-text)' }}>Sanju</div>
          <div style={{ fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>Policyholder</div>
        </div>
      </div>

      {/* Logout */}
      <Link href="/login" style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '10px 16px',
        fontSize: '12px',
        color: 'var(--color-tf-text-dim)',
        textDecoration: 'none',
        borderTop: '1px solid var(--color-tf-border)',
      }}>
        <LogOut size={14} />
        Log out
      </Link>
    </aside>
  );
}
