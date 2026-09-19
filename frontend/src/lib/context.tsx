'use client';

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { api } from '@/lib/api';
import {
  SimulationResponse,
  SimulationRequest,
  SimulationScenario,
} from '@/lib/types';

// ── Demo scenario selection (for the UI scenario buttons) ────────────────────
export type DemoScenario = 'normal' | 'corrupted' | 'no_consensus' | 'duplicate';

// ── Known IDs from actual database ───────────────────────────────────────────
export const DEMO_POLICY_ID = 'e5000000-0000-0000-0000-000000000001';
export const DEMO_WALLET_ID = 'f6000000-0000-0000-0000-000000000001';
export const DEMO_REGION_ID = 'b2000000-0000-0000-0000-000000000001';
export const DEMO_SOURCE_IDS = [
  'c3000000-0000-0000-0000-000000000001', // openmeteo
  'c3000000-0000-0000-0000-000000000002', // accuweather
  'c3000000-0000-0000-0000-000000000003', // imd
];

// ── Observation values for each demo scenario ────────────────────────────────
const SCENARIO_OBSERVATIONS: Record<DemoScenario, { values: number[]; backendScenario: SimulationScenario }> = {
  normal:       { values: [110, 108, 111], backendScenario: 'NORMAL' },
  corrupted:    { values: [110, 108, 7],   backendScenario: 'CORRUPTED_SOURCE' },
  no_consensus: { values: [120, 50, 5],    backendScenario: 'NO_CONSENSUS' },
  duplicate:    { values: [110, 108, 7],   backendScenario: 'DUPLICATE_REPLAY' },
};

interface AppContextType {
  // Demo scenario selection
  scenario: DemoScenario;
  setScenario: (s: DemoScenario) => void;

  // Backend simulation results
  simulationResult: SimulationResponse | null;
  simulationLoading: boolean;
  simulationError: string | null;
  runSimulation: (scenario: DemoScenario) => Promise<SimulationResponse | null>;

  // Auth & theme (preserved from original)
  isAuthenticated: boolean;
  setIsAuthenticated: (v: boolean) => void;
  isDarkMode: boolean;
  setIsDarkMode: (v: boolean) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [scenario, setScenario] = useState<DemoScenario>('normal');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);

  const [simulationResult, setSimulationResult] = useState<SimulationResponse | null>(null);
  const [simulationLoading, setSimulationLoading] = useState(false);
  const [simulationError, setSimulationError] = useState<string | null>(null);

  const runSimulation = useCallback(async (selectedScenario: DemoScenario): Promise<SimulationResponse | null> => {
    setSimulationLoading(true);
    setSimulationError(null);

    const config = SCENARIO_OBSERVATIONS[selectedScenario];

    const request: SimulationRequest = {
      scenario: config.backendScenario,
      policy_id: DEMO_POLICY_ID,
      region_id: DEMO_REGION_ID,
      observations: config.values.map((value, i) => ({
        source_id: DEMO_SOURCE_IDS[i],
        value,
      })),
      observed_at: new Date().toISOString(),
    };

    try {
      const result = await api.runSimulation(request);
      setSimulationResult(result);
      setScenario(selectedScenario);
      return result;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown simulation error';
      setSimulationError(message);
      return null;
    } finally {
      setSimulationLoading(false);
    }
  }, []);

  return (
    <AppContext.Provider value={{
      scenario, setScenario,
      simulationResult, simulationLoading, simulationError, runSimulation,
      isAuthenticated, setIsAuthenticated,
      isDarkMode, setIsDarkMode,
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within AppProvider');
  return context;
}
