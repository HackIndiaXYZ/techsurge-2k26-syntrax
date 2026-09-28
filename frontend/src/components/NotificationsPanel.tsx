'use client';

import { useEffect, useState, useCallback } from 'react';
import { api } from '@/lib/api';
import { NotificationResponse } from '@/lib/types';
import { Bell, CheckCircle, Clock, Loader2, AlertTriangle } from 'lucide-react';

interface NotificationsPanelProps {
  /** Trigger re-fetch when this value changes (e.g., after a simulation) */
  refreshKey?: number;
}

export default function NotificationsPanel({ refreshKey }: NotificationsPanelProps) {
  const [notifications, setNotifications] = useState<NotificationResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [acknowledging, setAcknowledging] = useState<string | null>(null);

  const fetchNotifications = useCallback(async () => {
    try {
      setError(null);
      const data = await api.getNotifications();
      setNotifications(data.notifications);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load notifications');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications, refreshKey]);

  const handleAcknowledge = async (notificationId: string) => {
    setAcknowledging(notificationId);
    try {
      const result = await api.acknowledgeNotification(notificationId);
      // Update local state
      setNotifications(prev =>
        prev.map(n =>
          n.notification_id === notificationId
            ? { ...n, status: result.status as 'ACKNOWLEDGED', acknowledged_at: result.acknowledged_at }
            : n
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to acknowledge');
    } finally {
      setAcknowledging(null);
    }
  };

  const unreadCount = notifications.filter(n => n.status === 'UNREAD').length;

  if (loading) {
    return (
      <div className="tf-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <Bell size={16} color="var(--color-tf-green)" />
          <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#fff' }}>Notifications</h3>
        </div>
        <div style={{ padding: '24px', textAlign: 'center' }}>
          <Loader2 size={16} color="var(--color-tf-green)" style={{ animation: 'spin 1s linear infinite' }} />
        </div>
      </div>
    );
  }

  return (
    <div className="tf-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Bell size={16} color="var(--color-tf-green)" />
          <h3 style={{ fontSize: '14px', fontWeight: 600, color: '#fff' }}>Notifications</h3>
          {unreadCount > 0 && (
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              minWidth: '20px',
              height: '20px',
              borderRadius: '10px',
              backgroundColor: 'var(--color-tf-green)',
              color: '#0a0e14',
              fontSize: '11px',
              fontWeight: 700,
              padding: '0 6px',
            }}>
              {unreadCount}
            </span>
          )}
        </div>
        <span style={{ fontSize: '11px', color: 'var(--color-tf-text-dim)' }}>
          {total} total
        </span>
      </div>

      {error && (
        <div style={{
          padding: '8px 12px',
          marginBottom: '8px',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '6px',
          fontSize: '11px',
          color: '#ef4444',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
        }}>
          <AlertTriangle size={12} />
          {error}
        </div>
      )}

      {notifications.length === 0 ? (
        <div style={{
          padding: '32px 16px',
          textAlign: 'center',
          color: 'var(--color-tf-text-dim)',
          fontSize: '12px',
        }}>
          <Bell size={24} color="var(--color-tf-text-dim)" style={{ marginBottom: '8px', opacity: 0.5 }} />
          <div>No notifications yet.</div>
          <div style={{ marginTop: '4px', fontSize: '11px' }}>
            Settlement notifications will appear here after a successful payout.
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {notifications.map(n => (
            <div
              key={n.notification_id}
              style={{
                padding: '12px 14px',
                borderRadius: '8px',
                backgroundColor: n.status === 'UNREAD'
                  ? 'rgba(16, 185, 129, 0.06)'
                  : 'rgba(255, 255, 255, 0.02)',
                border: n.status === 'UNREAD'
                  ? '1px solid rgba(16, 185, 129, 0.2)'
                  : '1px solid var(--color-tf-border)',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  {n.status === 'UNREAD' ? (
                    <div style={{
                      width: '8px', height: '8px', borderRadius: '50%',
                      backgroundColor: 'var(--color-tf-green)',
                      flexShrink: 0,
                    }} />
                  ) : (
                    <CheckCircle size={14} color="var(--color-tf-text-dim)" />
                  )}
                  <span style={{
                    fontSize: '13px',
                    fontWeight: 600,
                    color: n.status === 'UNREAD' ? '#fff' : 'var(--color-tf-text-muted)',
                  }}>
                    {n.title}
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '10px', color: 'var(--color-tf-text-dim)' }}>
                  <Clock size={10} />
                  {new Date(n.created_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>

              <div style={{
                fontSize: '12px',
                color: 'var(--color-tf-text-muted)',
                lineHeight: '1.5',
                marginBottom: '8px',
                paddingLeft: '14px',
              }}>
                {n.message}
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingLeft: '14px' }}>
                {n.status === 'UNREAD' ? (
                  <button
                    onClick={() => handleAcknowledge(n.notification_id)}
                    disabled={acknowledging === n.notification_id}
                    style={{
                      padding: '5px 14px',
                      borderRadius: '6px',
                      backgroundColor: 'var(--color-tf-green)',
                      color: '#0a0e14',
                      border: 'none',
                      fontSize: '11px',
                      fontWeight: 600,
                      cursor: acknowledging === n.notification_id ? 'wait' : 'pointer',
                      opacity: acknowledging === n.notification_id ? 0.7 : 1,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      transition: 'opacity 0.2s ease',
                    }}
                  >
                    {acknowledging === n.notification_id ? (
                      <>
                        <Loader2 size={11} style={{ animation: 'spin 1s linear infinite' }} />
                        Acknowledging...
                      </>
                    ) : (
                      <>
                        <CheckCircle size={11} />
                        Acknowledge
                      </>
                    )}
                  </button>
                ) : (
                  <span style={{
                    fontSize: '10px',
                    color: 'var(--color-tf-text-dim)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}>
                    <CheckCircle size={10} color="var(--color-tf-green)" />
                    Acknowledged {n.acknowledged_at ? new Date(n.acknowledged_at).toLocaleString('en-IN') : ''}
                  </span>
                )}

                <span className="tf-badge tf-badge-green" style={{ fontSize: '9px' }}>
                  {n.event_type}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
