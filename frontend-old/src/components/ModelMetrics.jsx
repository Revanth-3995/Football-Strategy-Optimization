import React from 'react';

const MetricRing = ({ label, value }) => {
  // SVG circle calculation
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const safeValue = value || 0;
  const strokeDashoffset = circumference - (safeValue / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-24 h-24 flex items-center justify-center">
        {/* Background Ring */}
        <svg className="absolute w-full h-full transform -rotate-90">
          <circle
            cx="48"
            cy="48"
            r={radius}
            stroke="var(--bg-elevated)"
            strokeWidth="8"
            fill="none"
          />
          {/* Progress Ring */}
          <circle
            cx="48"
            cy="48"
            r={radius}
            stroke="var(--accent)"
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            style={{
              strokeDasharray: circumference,
              strokeDashoffset: strokeDashoffset,
              transition: 'stroke-dashoffset 1s ease-in-out',
            }}
          />
        </svg>
        <span className="text-xl font-bold font-barlow text-white">{Math.round(safeValue)}%</span>
      </div>
      <span className="mt-3 text-sm font-semibold text-[var(--text-muted)] uppercase tracking-wider">{label}</span>
    </div>
  );
};

const ModelMetrics = ({ metrics }) => {
  if (!metrics) {
    return (
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-8 text-center text-[var(--text-muted)]">
        Run analysis to see model metrics.
      </div>
    );
  }

  return (
    <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-6">
      <h3 className="text-lg font-bold font-barlow text-white mb-6">Model Performance Metrics</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <MetricRing label="Accuracy" value={metrics.accuracy * 100} />
        <MetricRing label="Precision" value={metrics.precision * 100} />
        <MetricRing label="Recall" value={metrics.recall * 100} />
        <MetricRing label="F1 Score" value={metrics.f1 * 100} />
      </div>
      <div className="mt-6 text-xs text-[var(--text-muted)] text-center">
        Based on {metrics.n_samples} pressing events analyzed using Random Forest
      </div>
    </div>
  );
};

export default ModelMetrics;
