import React, { useContext } from 'react';
import { AnalyticsContext } from '../App';
import InsightsTable from '../components/InsightsTable';

const TacticalInsights = () => {
  const { trainResult } = useContext(AnalyticsContext);

  const insights = trainResult?.insights || [];

  // Find the most critical insight (e.g., the one about Counterpress or Best Zone)
  const keyInsight = insights.find(i => i.insight === "Counterpress Effectiveness") || insights[0];

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <header className="mb-8">
        <h1 className="text-3xl font-bold font-barlow text-white tracking-wide">Tactical Insights</h1>
        <p className="text-[var(--text-muted)] mt-1">Actionable recommendations derived from model predictions</p>
      </header>

      <div className="mb-8">
        <InsightsTable insights={insights} />
      </div>

      {keyInsight && (
        <div className="bg-[var(--bg-card)] border border-[var(--border)] border-l-4 border-l-[var(--accent)] rounded-xl p-6">
          <h2 className="text-sm font-bold text-[var(--accent)] uppercase tracking-wider mb-2">Key Finding</h2>
          <div className="text-xl text-white mb-2">{keyInsight.finding}</div>
          <div className="text-md text-[var(--text-muted)] italic">Recommendation: {keyInsight.action}</div>
        </div>
      )}
    </div>
  );
};

export default TacticalInsights;
