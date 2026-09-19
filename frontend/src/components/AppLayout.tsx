'use client';

import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <Sidebar />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', marginLeft: '200px', height: '100vh' }}>
        <Header />
        <main style={{
          flex: 1,
          overflow: 'auto',
          padding: '20px 24px',
          backgroundColor: 'var(--color-tf-bg)',
        }}>
          {children}
        </main>
        <Footer />
      </div>
    </div>
  );
}
