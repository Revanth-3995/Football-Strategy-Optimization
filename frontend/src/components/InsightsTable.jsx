import React from 'react';

const InsightsTable = ({ insights }) => {
  if (!insights || insights.length === 0) {
    return (
      <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-8 text-center text-[var(--text-muted)]">
        No insights available. Run analysis first.
      </div>
    );
  }

  // Define colors based on insight type to mimic the styling rules
  const getBorderColor = (insight) => {
    if (insight.includes('Zone')) return 'border-[var(--success)]';
    if (insight.includes('Time')) return 'border-[var(--accent-warm)]';
    if (insight.includes('Effectiveness') || insight.includes('Inefficiency')) return 'border-blue-500';
    return 'border-[var(--border)]';
  };

  const parseFindingText = (text) => {
    // Basic regex to wrap percentages/numbers in accent color
    const parts = text.split(/(\d+(?:\.\d+)?%?x?)/);
    return parts.map((part, i) => {
      if (/^\d+(?:\.\d+)?%?x?$/.test(part)) {
        return <span key={i} className="text-[var(--accent)] font-bold">{part}</span>;
      }
      return part;
    });
  };

  return (
    <div className="overflow-hidden rounded-xl border border-[var(--border)]">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="bg-[var(--bg-elevated)] border-b border-[var(--border)]">
            <th className="p-4 font-semibold text-white">Insight</th>
            <th className="p-4 font-semibold text-white">Finding</th>
            <th className="p-4 font-semibold text-white">Recommended Action</th>
          </tr>
        </thead>
        <tbody className="bg-[var(--bg-card)]">
          {insights.map((item, i) => (
            <tr
              key={i}
              className={`border-b border-[var(--border)] last:border-0 hover:bg-[var(--bg-elevated)] transition-colors ${i % 2 === 0 ? 'bg-[var(--bg-card)]' : 'bg-[var(--bg-elevated)]'}`}
            >
              <td className={`p-4 border-l-4 ${getBorderColor(item.insight)} font-medium text-white`}>
                {item.insight}
              </td>
              <td className="p-4 font-mono-num text-sm text-[var(--text-primary)]">
                {parseFindingText(item.finding)}
              </td>
              <td className="p-4 italic text-[var(--text-muted)] text-sm">
                {item.action}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default InsightsTable;
