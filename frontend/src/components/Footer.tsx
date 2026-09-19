'use client';

import { Cloud, Shield, Umbrella, Users } from 'lucide-react';
import { Leaf } from 'lucide-react';

export default function Footer() {
  return (
    <footer style={{
      height: '36px',
      backgroundColor: 'var(--color-tf-sidebar)',
      borderTop: '1px solid var(--color-tf-border)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 20px',
      fontSize: '10px',
      color: 'var(--color-tf-text-dim)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Leaf size={12} color="var(--color-tf-green)" />
        <span style={{ fontWeight: 600, letterSpacing: '1.5px', fontSize: '10px' }}>TERRAFLUX</span>
        <span style={{ margin: '0 8px', color: 'var(--color-tf-border-light)' }}>|</span>
        <span style={{ letterSpacing: '0.5px', textTransform: 'uppercase', fontSize: '9px' }}>Climate Intelligence for a More Resilient Tomorrow.</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Cloud size={10} /> Weather</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Shield size={10} /> Trust</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Umbrella size={10} /> Protection</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Users size={10} /> People</span>
      </div>
    </footer>
  );
}
