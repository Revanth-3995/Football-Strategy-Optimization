import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar = () => {
  const links = [
    { to: '/', label: 'Dashboard' },
    { to: '/visualizations', label: 'Visualizations' },
    { to: '/ml-model', label: 'ML Model' },
    { to: '/tactical-insights', label: 'Tactical Insights' }
  ];

  return (
    <div className="w-[240px] bg-[var(--bg-card)] border-r border-[var(--border)] h-full flex flex-col justify-between">
      <div>
        <div className="p-6 flex items-center space-x-3">
          <svg className="w-8 h-8 text-[var(--accent)]" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z" />
          </svg>
          <span className="text-xl font-bold font-barlow tracking-wider text-white">FootballIQ</span>
        </div>
        <nav className="mt-4 flex flex-col space-y-1">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `px-6 py-3 font-semibold transition-colors duration-200 ${
                  isActive
                    ? 'border-l-2 border-[var(--accent)] bg-[var(--bg-elevated)] text-[var(--accent)]'
                    : 'text-[var(--text-muted)] hover:text-white hover:bg-[var(--bg-elevated)]'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>
      <div className="p-6 text-xs text-[var(--text-muted)]">
        Data: StatsBomb Open Data
      </div>
    </div>
  );
};

export default Sidebar;
