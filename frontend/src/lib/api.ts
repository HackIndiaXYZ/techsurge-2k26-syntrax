// =============================================================================
// TerraFlux API Client — Typed functions for all backend endpoints
// =============================================================================
import {
  WeatherSource,
  PollResponse,
  HealthResponse,
  SimulationRequest,
  SimulationResponse,
  PolicyResponse,
  WalletResponse,
  PayoutResponse,
  AuditListResponse,
  ApiError,
} from './types';

import { createClient } from './supabase';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const getAuthHeader = async () => {
  const supabase = createClient();
  const { data: { session } } = await supabase.auth.getSession();
  if (session?.access_token) {
    return { Authorization: `Bearer ${session.access_token}` };
  }
  return {};
};

/**
 * Generic fetch wrapper with typed error handling.
 * Throws ApiError for non-2xx responses, or a generic Error for network failures.
 */
async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  let res: Response;
  try {
    const authHeader = await getAuthHeader();
    res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...authHeader,
        ...options?.headers,
      },
    });
  } catch (err) {
    throw new Error(
      `Network error: Unable to reach backend at ${API_BASE}. ` +
      `Is the backend running? (${err instanceof Error ? err.message : String(err)})`
    );
  }

  if (!res.ok) {
    let detail = null;
    try {
      detail = await res.json();
    } catch {
      // Response may not be JSON
    }
    throw new ApiError(res.status, detail, `API ${res.status}: ${path}`);
  }

  return res.json() as Promise<T>;
}

export const api = {
  // ── Health ──────────────────────────────────────────────────────────────
  async getHealth(): Promise<HealthResponse> {
    return apiFetch<HealthResponse>('/health', { cache: 'no-store' });
  },

  // ── Weather ─────────────────────────────────────────────────────────────
  async getProvidersHealth(): Promise<WeatherSource[]> {
    return apiFetch<WeatherSource[]>('/weather/sources', { cache: 'no-store' });
  },

  async triggerWeatherPoll(): Promise<PollResponse> {
    return apiFetch<PollResponse>('/weather/poll', { method: 'POST' });
  },

  // ── Simulation ──────────────────────────────────────────────────────────
  async runSimulation(request: SimulationRequest): Promise<SimulationResponse> {
    return apiFetch<SimulationResponse>('/simulations', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  // ── Policy ──────────────────────────────────────────────────────────────
  async getPolicy(policyId: string): Promise<PolicyResponse> {
    return apiFetch<PolicyResponse>(`/policies/${encodeURIComponent(policyId)}`, {
      cache: 'no-store',
    });
  },

  // ── Wallet ──────────────────────────────────────────────────────────────
  async getWallet(walletId: string): Promise<WalletResponse> {
    return apiFetch<WalletResponse>(`/wallets/${encodeURIComponent(walletId)}`, {
      cache: 'no-store',
    });
  },

  // ── Payout ──────────────────────────────────────────────────────────────
  async getPayout(payoutId: string): Promise<PayoutResponse> {
    return apiFetch<PayoutResponse>(`/payouts/${encodeURIComponent(payoutId)}`, {
      cache: 'no-store',
    });
  },

  // ── Audit ───────────────────────────────────────────────────────────────
  async getAuditEvents(policyId: string, limit: number = 50): Promise<AuditListResponse> {
    return apiFetch<AuditListResponse>(
      `/policies/${encodeURIComponent(policyId)}/audit?limit=${limit}`,
      { cache: 'no-store' }
    );
  },
};
