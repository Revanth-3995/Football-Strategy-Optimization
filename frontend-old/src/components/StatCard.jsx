import React from 'react';

const StatCard = ({ title, value, subtitle }) => {
  return (
    <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-6 flex flex-col justify-center">
      <h3 className="text-sm font-semibold text-[var(--text-muted)] uppercase tracking-wider">{title}</h3>
      <div className="mt-2 text-[3rem] leading-none font-barlow font-bold text-white">
        {value}
      </div>
      {subtitle && (
        <p className="mt-2 text-sm text-[var(--text-muted)]">{subtitle}</p>
      )}
    </div>
  );
};

export default StatCard;
