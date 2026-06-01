import React from 'react';

const ChartViewer = ({ title, description, imageUrl }) => {
  return (
    <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-6 flex flex-col h-full">
      <div className="mb-4 flex justify-between items-start">
        <div>
          <h3 className="text-xl font-bold font-barlow text-white">{title}</h3>
          <p className="text-sm text-[var(--text-muted)] mt-1">{description}</p>
        </div>
        {imageUrl && (
          <a
            href={imageUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs bg-[var(--bg-elevated)] border border-[var(--border)] px-3 py-1.5 rounded hover:bg-[var(--border)] transition-colors text-white whitespace-nowrap"
          >
            Download PNG
          </a>
        )}
      </div>

      <div className="flex-1 flex items-center justify-center bg-[var(--bg-elevated)] rounded-lg border border-[var(--border)] overflow-hidden min-h-[300px]">
        {imageUrl ? (
          <img src={imageUrl} alt={title} className="max-w-full max-h-full object-contain" />
        ) : (
          <div className="border-2 border-dashed border-[var(--border)] rounded-lg w-full h-full flex items-center justify-center m-4 text-[var(--text-muted)]">
            Run analysis to generate
          </div>
        )}
      </div>
    </div>
  );
};

export default ChartViewer;
