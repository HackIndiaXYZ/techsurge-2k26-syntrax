'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';
import { DemoScenario } from '@/lib/mock-data';

interface AppContextType {
  scenario: DemoScenario;
  setScenario: (s: DemoScenario) => void;
  isAuthenticated: boolean;
  setIsAuthenticated: (v: boolean) => void;
  isDarkMode: boolean;
  setIsDarkMode: (v: boolean) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [scenario, setScenario] = useState<DemoScenario>('corrupted');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);

  return (
    <AppContext.Provider value={{ scenario, setScenario, isAuthenticated, setIsAuthenticated, isDarkMode, setIsDarkMode }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within AppProvider');
  return context;
}
