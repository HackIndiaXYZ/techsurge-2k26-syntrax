import { WeatherSource, PollResponse } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  async getProvidersHealth(): Promise<WeatherSource[]> {
    const res = await fetch(`${API_BASE}/weather/sources`, {
      cache: 'no-store',
    });
    if (!res.ok) throw new Error('Failed to fetch providers health');
    return res.json();
  },

  async triggerWeatherPoll(): Promise<PollResponse> {
    const res = await fetch(`${API_BASE}/weather/poll`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to trigger poll');
    return res.json();
  },

  // Other endpoints can be added here
};

