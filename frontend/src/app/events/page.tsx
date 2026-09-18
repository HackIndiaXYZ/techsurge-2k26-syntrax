'use client';

import AppLayout from '@/components/AppLayout';
import { recentEvents } from '@/lib/mock-data';
import Link from 'next/link';
import { Eye, Filter } from 'lucide-react';

export default function EventsPage() {
  return (
    <AppLayout>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#fff' }}>Event Evidence</h1>
          <p style={{ fontSize: '13px', color: 'var(--color-tf-text-muted)', marginTop: '2px' }}>Complete audit trail for all climate protection events.</p>
        </div>
        <button className="tf-btn tf-btn-outline" style={{ fontSize: '12px' }}>
          <Filter size={13} /> Filter Events
        </button>
      </div>

      <div className="tf-card">
        <table className="tf-table">
          <thead>
            <tr>
              <th>Event ID</th>
              <th>Date &amp; Time</th>
              <th>Rainfall (mm)</th>
              <th>Decision</th>
              <th>Settlement</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {recentEvents.map(evt => (
              <tr key={evt.id}>
                <td style={{ fontWeight: 600, color: '#fff' }}>{evt.id}</td>
                <td style={{ fontSize: '12px' }}>{evt.date || evt.time}</td>
                <td>{evt.rainfall}</td>
                <td>
                  <span className={
                    evt.decision === 'Triggered' ? 'tf-badge tf-badge-green' :
                    evt.decision === 'Below Threshold' ? 'tf-badge tf-badge-orange' :
                    evt.decision === 'No Consensus' ? 'tf-badge tf-badge-red' :
                    'tf-badge tf-badge-blue'
                  }>
                    {evt.decision}
                  </span>
                </td>
                <td style={{ color: evt.settlement > 0 ? 'var(--color-tf-green)' : 'var(--color-tf-text-dim)', fontWeight: 500 }}>
                  ₹{evt.settlement.toLocaleString()}
                </td>
                <td>
                  <span className={
                    evt.status === 'Completed' ? 'tf-badge tf-badge-green' :
                    evt.status === 'Duplicate' ? 'tf-badge tf-badge-orange' :
                    'tf-badge tf-badge-red'
                  }>
                    {evt.status}
                  </span>
                </td>
                <td>
                  <Link href={`/events/${evt.id}`} className="tf-btn tf-btn-outline" style={{ padding: '4px 10px', fontSize: '11px', textDecoration: 'none' }}>
                    <Eye size={12} /> View Evidence
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AppLayout>
  );
}
