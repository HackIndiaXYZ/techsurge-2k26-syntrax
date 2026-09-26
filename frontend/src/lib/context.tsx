'use client';

import React, { createContext, useContext, useState, useCallback, ReactNode, useEffect } from 'react';
import { api } from '@/lib/api';
import { createClient } from '@/lib/supabase';
import {
  SimulationResponse,
  SimulationRequest,
  SimulationScenario,
  IdentityResponse,
} from '@/lib/types';

// ── Demo scenario selection (for the UI scenario buttons) ────────────────────
export type DemoScenario = 'normal' | 'corrupted' | 'no_consensus' | 'duplicate';

// ── Known IDs from actual database ───────────────────────────────────────────
export const DEMO_REGION_ID = '00000000-0000-0000-0000-000000000001';
export const DEMO_SOURCE_IDS = [
  '00000000-0000-0000-0000-000000000010', // openmeteo
  '00000000-0000-0000-0000-000000000011', // accuweather
  '00000000-0000-0000-0000-000000000012', // imd
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

  // Identity
  identity: IdentityResponse | null;
  identityLoading: boolean;
  reloadIdentity: () => Promise<void>;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [scenario, setScenario] = useState<DemoScenario>('normal');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);

  useEffect(() => {
    const supabase = createClient();
    supabase.auth.getSession().then(({ data: { session } }) => {
      setIsAuthenticated(!!session);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      setIsAuthenticated(!!session);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const [identity, setIdentity] = useState<IdentityResponse | null>(null);
  const [identityLoading, setIdentityLoading] = useState(false);

  const [simulationResult, setSimulationResult] = useState<SimulationResponse | null>(null);
  const [simulationLoading, setSimulationLoading] = useState(false);
  const [simulationError, setSimulationError] = useState<string | null>(null);

  const reloadIdentity = useCallback(async () => {
    try {
      setIdentityLoading(true);
      const res = await api.getMe();
      setIdentity(res);
    } catch (err) {
      console.error("Failed to load identity:", err);
      setIdentity(null);
    } finally {
      setIdentityLoading(false);
    }
  }, []);

  // Fetch identity if authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      reloadIdentity();
    } else {
      setIdentity(null);
    }
  }, [isAuthenticated, reloadIdentity]);

  const runSimulation = useCallback(async (selectedScenario: DemoScenario): Promise<SimulationResponse | null> => {
    setSimulationLoading(true);
    setSimulationError(null);

    const config = SCENARIO_OBSERVATIONS[selectedScenario];
    const policyId = identity?.policies?.[0]?.policy_id;
    
    if (!policyId) {
      setSimulationError("No active policy found. Please create a policy first.");
      setSimulationLoading(false);
      return null;
    }

    const request: SimulationRequest = {
      scenario: config.backendScenario,
      policy_id: policyId,
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
  }, [identity]);

  return (
    <AppContext.Provider value={{
      scenario, setScenario,
      simulationResult, simulationLoading, simulationError, runSimulation,
      isAuthenticated, setIsAuthenticated,
      isDarkMode, setIsDarkMode,
      identity, identityLoading, reloadIdentity,
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
