import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const FeatureImportanceBar = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-[var(--text-muted)] border-2 border-dashed border-[var(--border)] rounded-lg">
        Run analysis to generate chart
      </div>
    );
  }

  // Sort ascending for vertical bar chart so biggest is at top (Recharts renders bottom to top usually)
  const chartData = useMemo(() => {
    return [...data].sort((a, b) => a.importance - b.importance);
  }, [data]);

  return (
    <div className="h-[400px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
        >
          <defs>
            <linearGradient id="colorGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#00e5a0" stopOpacity={0.8} />
              <stop offset="100%" stopColor="#0ea5e9" stopOpacity={0.8} />
            </linearGradient>
          </defs>
          <XAxis type="number" hide />
          <YAxis
            type="category"
            dataKey="feature"
            axisLine={false}
            tickLine={false}
            tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
            width={100}
          />
          <Tooltip
            cursor={{ fill: 'var(--bg-elevated)' }}
            contentStyle={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: '8px', color: 'white' }}
            itemStyle={{ color: 'var(--accent)' }}
          />
          <Bar dataKey="importance" animationDuration={800} radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill="url(#colorGradient)" />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default FeatureImportanceBar;
