import React, { createContext, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Visualizations from './pages/Visualizations';
import MLModel from './pages/MLModel';
import TacticalInsights from './pages/TacticalInsights';

export const AnalyticsContext = createContext();

function App() {
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [selectedTeam, setSelectedTeam] = useState("");
  const [trainResult, setTrainResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const contextValue = {
    selectedMatch, setSelectedMatch,
    selectedTeam, setSelectedTeam,
    trainResult, setTrainResult,
    isLoading, setIsLoading,
    error, setError
  };

  return (
    <AnalyticsContext.Provider value={contextValue}>
      <Router>
        <div className="flex h-screen bg-[var(--bg-primary)]">
          <Sidebar />
          <div className="flex-1 overflow-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/visualizations" element={<Visualizations />} />
              <Route path="/ml-model" element={<MLModel />} />
              <Route path="/tactical-insights" element={<TacticalInsights />} />
            </Routes>
          </div>
        </div>
      </Router>
    </AnalyticsContext.Provider>
  );
}

export default App;
