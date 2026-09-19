'use client';

import AppLayout from '@/components/AppLayout';
import { Settings, Bell, Shield, Globe, Moon } from 'lucide-react';

export default function SettingsPage() {
  return (
    <AppLayout>
      <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#fff', marginBottom: '4px' }}>Settings</h1>
      <p style={{ fontSize: '13px', color: 'var(--color-tf-text-muted)', marginBottom: '24px' }}>Manage your TerraFlux preferences.</p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        {[
          { icon: <Bell size={20} color="var(--color-tf-green)" />, title: 'Notifications', desc: 'Configure alert preferences for weather events and settlements.' },
          { icon: <Shield size={20} color="var(--color-tf-green)" />, title: 'Security', desc: 'Manage authentication and access control settings.' },
          { icon: <Globe size={20} color="var(--color-tf-green)" />, title: 'Region', desc: 'Set your default region and weather monitoring preferences.' },
          { icon: <Moon size={20} color="var(--color-tf-green)" />, title: 'Appearance', desc: 'Toggle dark/light mode and customize the interface.' },
        ].map((item, i) => (
          <div key={i} className="tf-card" style={{ cursor: 'pointer' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '10px', backgroundColor: 'rgba(16,185,129,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {item.icon}
              </div>
              <div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#fff' }}>{item.title}</div>
                <div style={{ fontSize: '12px', color: 'var(--color-tf-text-dim)', marginTop: '2px' }}>{item.desc}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </AppLayout>
  );
}
