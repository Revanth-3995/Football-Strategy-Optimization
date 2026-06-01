import React, { useContext } from 'react';
import { AnalyticsContext } from '../App';
import MatchSelector from '../components/MatchSelector';
import StatCard from '../components/StatCard';

const Dashboard = () => {
  const { trainResult, error } = useContext(AnalyticsContext);

  const getBorderColor = (insightType) => {
    if (insightType === "Best Pressing Zone") return "border-[var(--success)]";
    if (insightType === "Time Management") return "border-[var(--accent-warm)]";
    if (insightType === "Counterpress Effectiveness") return "border-blue-500";
    if (insightType === "Wide Pressing Inefficiency") return "border-purple-500";
    return "border-[var(--border)]";
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <header className="mb-8">
        <h1 className="text-3xl font-bold font-barlow text-white tracking-wide">Football Strategy Optimizer</h1>
        <p className="text-[var(--text-muted)] mt-1">Spatial Event Data Analytics</p>
      </header>

      <MatchSelector />

      {error && (
        <div className="bg-[var(--danger)]/10 border border-[var(--danger)] text-[var(--danger)] px-4 py-3 rounded-lg mb-8">
          {error}
        </div>
      )}

      {trainResult && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard
              title="Model Accuracy"
              value={`${(trainResult.metrics.accuracy * 100).toFixed(1)}%`}
            />
            <StatCard
              title="Total Pressures"
              value={trainResult.metrics.n_samples}
              subtitle="Events analyzed"
            />
            <StatCard
              title="Best Zone"
              value={
                trainResult.insights.find(i => i.insight === "Best Pressing Zone")?.finding.split(' ')[0] || "N/A"
              }
            />
            <StatCard
              title="Counterpress Mult."
              value={
                trainResult.insights.find(i => i.insight === "Counterpress Effectiveness")?.finding.match(/[\d.]+x/)?.[0] || "N/A"
              }
            />
          </div>

          <div className="mb-8">
            <h2 className="text-xl font-bold font-barlow text-white mb-4">Quick Insights</h2>
            <div className="flex overflow-x-auto space-x-6 pb-4">
              {trainResult.insights.map((insight, idx) => (
                <div
                  key={idx}
                  className={`min-w-[300px] flex-shrink-0 bg-[var(--bg-card)] border border-[var(--border)] border-l-4 ${getBorderColor(insight.insight)} rounded-xl p-5`}
                >
                  <div className="flex items-center space-x-2 mb-3">
                    <svg className="w-5 h-5 text-[var(--text-muted)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <h3 className="font-semibold text-white">{insight.insight}</h3>
                  </div>
                  <p className="text-sm text-[var(--text-primary)] mb-3">{insight.finding}</p>
                  <p className="text-xs text-[var(--text-muted)] italic">{insight.action}</p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;
