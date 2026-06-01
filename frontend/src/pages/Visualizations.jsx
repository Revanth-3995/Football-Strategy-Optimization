import React, { useContext } from 'react';
import { AnalyticsContext } from '../App';
import ChartViewer from '../components/ChartViewer';

const Visualizations = () => {
  const { trainResult } = useContext(AnalyticsContext);

  const chartsConfig = [
    { id: 'pressing_heatmap', title: 'Pressing Heatmap', desc: 'Spatial distribution of all pressing actions.' },
    { id: 'defensive_heatmap', title: 'Defensive Heatmap', desc: 'Tackles, interceptions, and clearances.' },
    { id: 'pass_network', title: 'Pass Network', desc: 'Average passing positions and combinations.' },
    { id: 'shot_map', title: 'Shot Map', desc: 'Shot locations sized by expected goals (xG).' },
    { id: 'player_touchmap', title: 'Player Touch Map', desc: 'Activity map for the player with most touches.' },
    { id: 'feature_importance', title: 'Feature Importance', desc: 'Top drivers of pressing success (static).' },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <header className="mb-8">
        <h1 className="text-3xl font-bold font-barlow text-white tracking-wide">Spatial Visualizations</h1>
        <p className="text-[var(--text-muted)] mt-1">Generated using mplsoccer based on StatsBomb event data</p>
      </header>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        {chartsConfig.map(config => (
          <ChartViewer
            key={config.id}
            title={config.title}
            description={config.desc}
            imageUrl={trainResult?.charts?.[config.id]}
          />
        ))}
      </div>
    </div>
  );
};

export default Visualizations;
