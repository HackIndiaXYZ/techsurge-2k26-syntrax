export interface WeatherSource {
  name: string;
  status: 'ONLINE' | 'OFFLINE' | 'DEGRADED' | 'UNKNOWN';
  latency_ms: number;
}

export interface PollResponse {
  status: str;
  message: str;
}

