'use client';

import { usePathname, useRouter } from 'next/navigation';
import { Search, Bell, Sun, Moon, Leaf, LogOut } from 'lucide-react';
import { useApp } from '@/lib/context';

const pageTitles: Record<string, string> = {
  '/dashboard': 'Overview',
  '/policies': 'Policies',
  '/weather': 'Live Monitor',
  '/wallet': 'Wallet',
  '/events': 'Evidence',
  '/settings': 'Settings',
};

export default function Header() {
  const pathname = usePathname();
  const { isDarkMode, setIsDarkMode } = useApp();
  const router = useRouter();
  const now = new Date();
  const dateStr = now.toLocaleDateString('en-IN', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' });
  const timeStr = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', hour12: true }).toUpperCase();

  const handleLogout = async () => {
    try {
      const { createClient } = await import('@/lib/supabase');
      const supabase = createClient();
      await supabase.auth.signOut();
      router.push('/login');
      router.refresh();
    } catch (err) {
      console.error('Logout failed', err);
    }
  };

  return (
    <header style={{
      height: '52px',
      backgroundColor: 'var(--color-tf-header)',
      borderBottom: '1px solid var(--color-tf-border)',
      display: 'flex',
      alignItems: 'center',
      padding: '0 20px',
      gap: '16px',
      position: 'sticky',
      top: 0,
      zIndex: 30,
    }}>
      {/* Logo in header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginRight: '8px' }}>
        <Leaf size={18} color="var(--color-tf-green)" />
        <span style={{ fontSize: '14px', fontWeight: 700, letterSpacing: '1.5px', color: 'var(--color-tf-text)' }}>TERRAFLUX</span>
        <span style={{ fontSize: '8px', color: 'var(--color-tf-text-dim)', letterSpacing: '1px', marginLeft: '4px' }}>TRUSTED WEATHER. AUTOMATIC PROTECTION.</span>
      </div>

      {/* Search */}
      <div style={{
        flex: 1,
        maxWidth: '400px',
        position: 'relative',
      }}>
        <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-tf-text-dim)' }} />
        <input
          type="text"
          placeholder="Search events, policies, or regions..."
          style={{
            width: '100%',
            padding: '7px 12px 7px 32px',
            backgroundColor: 'var(--color-tf-surface)',
            border: '1px solid var(--color-tf-border)',
            borderRadius: '6px',
            color: 'var(--color-tf-text)',
            fontSize: '12px',
            outline: 'none',
          }}
        />
      </div>

      <div style={{ flex: 1 }} />

      {/* System Status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <div style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          backgroundColor: 'var(--color-tf-green)',
          boxShadow: '0 0 6px rgba(16, 185, 129, 0.5)',
        }} className="pulse-dot" />
        <div>
          <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-tf-green)' }}>System Operational</div>
          <div style={{ fontSize: '9px', color: 'var(--color-tf-text-dim)' }}>{dateStr} | {timeStr}</div>
        </div>
      </div>

      {/* Theme toggle */}
      <button
        onClick={() => setIsDarkMode(!isDarkMode)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
          padding: '4px 8px',
          backgroundColor: 'var(--color-tf-surface)',
          border: '1px solid var(--color-tf-border)',
          borderRadius: '20px',
          cursor: 'pointer',
          color: 'var(--color-tf-text-muted)',
        }}
      >
        <Sun size={12} />
        <div style={{
          width: '24px',
          height: '14px',
          borderRadius: '7px',
          backgroundColor: 'var(--color-tf-green)',
          position: 'relative',
          transition: 'all 0.2s',
        }}>
          <div style={{
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            backgroundColor: '#0a0e14',
            position: 'absolute',
            top: '2px',
            right: isDarkMode ? '2px' : '12px',
            transition: 'all 0.2s',
          }} />
        </div>
        <Moon size={12} />
      </button>

      {/* Notification */}
      <button style={{
        width: '32px',
        height: '32px',
        borderRadius: '6px',
        backgroundColor: 'transparent',
        border: '1px solid var(--color-tf-border)',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'var(--color-tf-text-muted)',
      }}>
        <Bell size={15} />
      </button>

      {/* Logout */}
      <button 
        onClick={handleLogout}
        style={{
        width: '32px',
        height: '32px',
        borderRadius: '6px',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        border: '1px solid rgba(239, 68, 68, 0.3)',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#ef4444',
      }}>
        <LogOut size={15} />
      </button>
    </header>
  );
}
