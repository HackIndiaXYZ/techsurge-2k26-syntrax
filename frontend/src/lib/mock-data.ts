// TerraFlux Mock Data - Centralized demo state
// All values represent pre-computed backend results

export type DemoScenario = 'normal' | 'corrupted' | 'no_consensus' | 'duplicate';

export interface WeatherSource {
  id: string;
  name: string;
  fullName: string;
  rainfall: number;
  status: 'valid' | 'outlier';
  temperature: number;
  humidity: number;
  wind: number;
}

export interface ConsensusResult {
  achieved: boolean;
  trustedRainfall: number;
  agreeSources: number;
  totalSources: number;
  tolerance: number;
}

export interface PolicyEvaluation {
  triggered: boolean;
  rainfall: number;
  threshold: number;
  thresholdUnit: string;
  payoutAmountPaise: number;
}

export interface EventRecord {
  id: string;
  time: string;
  date: string;
  rainfall: number;
  decision: 'Triggered' | 'Below Threshold' | 'No Consensus' | 'Duplicate';
  settlement: number;
  status: 'Completed' | 'No Payout' | 'Not Eligible' | 'Duplicate';
}

export interface WalletTransaction {
  date: string;
  eventId: string;
  description: string;
  amount: number;
  balance: number;
  status: 'Completed' | 'No Payout' | 'Not Eligible' | 'Duplicate';
}

export const scenarioData: Record<DemoScenario, {
  sources: WeatherSource[];
  consensus: ConsensusResult;
  evaluation: PolicyEvaluation;
}> = {
  normal: {
    sources: [
      { id: 'A', name: 'Source A (IMD)', fullName: 'India Meteorological Department', rainfall: 110.0, status: 'valid', temperature: 26.4, humidity: 78, wind: 12 },
      { id: 'B', name: 'Source B (OpenWeather)', fullName: 'OpenWeather API', rainfall: 108.0, status: 'valid', temperature: 26.1, humidity: 80, wind: 10 },
      { id: 'C', name: 'Source C (Community)', fullName: 'Community Weather Network', rainfall: 111.0, status: 'valid', temperature: 27.8, humidity: 82, wind: 8 },
    ],
    consensus: { achieved: true, trustedRainfall: 109.7, agreeSources: 3, totalSources: 3, tolerance: 5 },
    evaluation: { triggered: true, rainfall: 109.7, threshold: 100, thresholdUnit: '≥ 100 mm / 60 min', payoutAmountPaise: 1000000 },
  },
  corrupted: {
    sources: [
      { id: 'A', name: 'Source A (IMD)', fullName: 'India Meteorological Department', rainfall: 103.0, status: 'valid', temperature: 26.4, humidity: 78, wind: 12 },
      { id: 'B', name: 'Source B (OpenWeather)', fullName: 'OpenWeather API', rainfall: 101.0, status: 'valid', temperature: 26.1, humidity: 80, wind: 10 },
      { id: 'C', name: 'Source C (Community)', fullName: 'Community Weather Network', rainfall: 7.0, status: 'outlier', temperature: 27.8, humidity: 82, wind: 8 },
    ],
    consensus: { achieved: true, trustedRainfall: 102.0, agreeSources: 2, totalSources: 3, tolerance: 5 },
    evaluation: { triggered: true, rainfall: 102.0, threshold: 100, thresholdUnit: '≥ 100 mm / 60 min', payoutAmountPaise: 1000000 },
  },
  no_consensus: {
    sources: [
      { id: 'A', name: 'Source A (IMD)', fullName: 'India Meteorological Department', rainfall: 120.0, status: 'outlier', temperature: 26.4, humidity: 78, wind: 12 },
      { id: 'B', name: 'Source B (OpenWeather)', fullName: 'OpenWeather API', rainfall: 50.0, status: 'outlier', temperature: 26.1, humidity: 80, wind: 10 },
      { id: 'C', name: 'Source C (Community)', fullName: 'Community Weather Network', rainfall: 5.0, status: 'outlier', temperature: 27.8, humidity: 82, wind: 8 },
    ],
    consensus: { achieved: false, trustedRainfall: 0, agreeSources: 0, totalSources: 3, tolerance: 5 },
    evaluation: { triggered: false, rainfall: 0, threshold: 100, thresholdUnit: '≥ 100 mm / 60 min', payoutAmountPaise: 0 },
  },
  duplicate: {
    sources: [
      { id: 'A', name: 'Source A (IMD)', fullName: 'India Meteorological Department', rainfall: 103.0, status: 'valid', temperature: 26.4, humidity: 78, wind: 12 },
      { id: 'B', name: 'Source B (OpenWeather)', fullName: 'OpenWeather API', rainfall: 101.0, status: 'valid', temperature: 26.1, humidity: 80, wind: 10 },
      { id: 'C', name: 'Source C (Community)', fullName: 'Community Weather Network', rainfall: 7.0, status: 'outlier', temperature: 27.8, humidity: 82, wind: 8 },
    ],
    consensus: { achieved: true, trustedRainfall: 102.0, agreeSources: 2, totalSources: 3, tolerance: 5 },
    evaluation: { triggered: true, rainfall: 102.0, threshold: 100, thresholdUnit: '≥ 100 mm / 60 min', payoutAmountPaise: 1000000 },
  },
};

export const recentEvents: EventRecord[] = [
  { id: 'EVT-1042', time: '10:24:12', date: '18 Sep 2026, 10:24', rainfall: 102.0, decision: 'Triggered', settlement: 10000, status: 'Completed' },
  { id: 'EVT-1041', time: '08:15:33', date: '16 Sep 2026, 14:12', rainfall: 72.4, decision: 'Below Threshold', settlement: 0, status: 'No Payout' },
  { id: 'EVT-1040', time: '06:42:18', date: '14 Sep 2026, 09:33', rainfall: 118.6, decision: 'Triggered', settlement: 10000, status: 'Completed' },
  { id: 'EVT-1039', time: '02:31:09', date: '12 Sep 2026, 11:18', rainfall: 65.2, decision: 'No Consensus', settlement: 0, status: 'Not Eligible' },
  { id: 'EVT-1038', time: '00:14:55', date: '10 Sep 2026, 16:05', rainfall: 101.3, decision: 'Triggered', settlement: 10000, status: 'Completed' },
];

export const walletTransactions: WalletTransaction[] = [
  { date: '18 Sep 2026, 10:24', eventId: 'EVT-1042', description: 'Climate Event Settlement', amount: 10000, balance: 10000, status: 'Completed' },
  { date: '16 Sep 2026, 14:12', eventId: 'EVT-1041', description: 'Below threshold (no payout)', amount: 0, balance: 0, status: 'No Payout' },
  { date: '14 Sep 2026, 09:33', eventId: 'EVT-1040', description: 'No consensus (3 sources)', amount: 0, balance: 0, status: 'Not Eligible' },
  { date: '12 Sep 2026, 11:18', eventId: 'EVT-1039', description: 'Duplicate settlement attempt', amount: 10000, balance: 10000, status: 'Duplicate' },
  { date: '10 Sep 2026, 16:05', eventId: 'EVT-1038', description: 'Climate Event Settlement', amount: 10000, balance: 10000, status: 'Completed' },
];

export const policies = [
  { id: 'SYN-F03-001', name: 'Rainfall Index Protection', region: 'Tamil Nadu (TN)', trigger: '≥ 100 mm / 60 min', payout: '₹10,000', status: 'Active' as const, period: 'Aug 2026 - Dec 2026', type: 'Rainfall Index' },
  { id: 'SYN-MH-002', name: 'Heavy Rain Protection', region: 'Maharashtra (MH)', trigger: '≥ 120 mm / 60 min', payout: '₹15,000', status: 'Active' as const, period: 'Jul 2026 - Nov 2026', type: 'Rainfall Index' },
  { id: 'SYN-KA-003', name: 'Monsoon Shield', region: 'Karnataka (KA)', trigger: '≥ 100 mm / 60 min', payout: '₹10,000', status: 'Expiring Soon' as const, period: 'Jun 2026 - Sep 2026', type: 'Rainfall Index' },
  { id: 'SYN-GJ-004', name: 'Flood Relief Cover', region: 'Gujarat (GJ)', trigger: '≥ 150 mm / 60 min', payout: '₹20,000', status: 'Inactive' as const, period: 'Jan 2026 - May 2026', type: 'Rainfall Index' },
];

export const systemHealth = [
  { name: 'Weather Source A (IMD)', status: 'Online', icon: 'cloud' },
  { name: 'Weather Source B (OpenWeather)', status: 'Online', icon: 'cloud' },
  { name: 'Weather Source C (Community)', status: 'Online', icon: 'cloud' },
  { name: 'Consensus Engine', status: 'Ready', icon: 'cpu' },
  { name: 'Policy Evaluation Engine', status: 'Ready', icon: 'shield' },
  { name: 'Settlement Engine', status: 'Ready', icon: 'zap' },
  { name: 'Synthetic Wallet', status: 'Ready', icon: 'wallet' },
  { name: 'AI Explanation Service', status: 'Ready', icon: 'brain' },
];

export const eventTimeline = [
  { time: '10:24:00', title: 'Telemetry Received', description: 'Weather data received from 3 sources', status: 'complete' as const },
  { time: '10:24:02', title: 'Source Validation', description: 'Sources A and B validated. Source C flagged as outlier.', status: 'warning' as const },
  { time: '10:24:03', title: 'Consensus Achieved', description: '2/3 sources agree. Trusted rainfall: 102.0 mm', status: 'complete' as const },
  { time: '10:24:04', title: 'Trigger Evaluated', description: '102.0 mm ≥ 100 mm threshold — Trigger satisfied', status: 'complete' as const },
  { time: '10:24:05', title: 'Payout Created', description: 'Simulated settlement of ₹10,000 authorized', status: 'complete' as const },
  { time: '10:24:06', title: 'Settlement Completed', description: 'Funds credited to synthetic wallet WLT-001', status: 'complete' as const },
  { time: '10:24:07', title: 'Audit Record Created', description: 'Immutable audit trail generated for EVT-1042', status: 'complete' as const },
];
