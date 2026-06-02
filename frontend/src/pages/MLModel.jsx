import React, { useContext, useState } from 'react';
import { AnalyticsContext } from '../App';
import ModelMetrics from '../components/ModelMetrics';
import FeatureImportanceBar from '../components/FeatureImportanceBar';
import { predictPress } from '../api/client';

const MLModel = () => {
  const { trainResult } = useContext(AnalyticsContext);

  // Predictor state
  const [predForm, setPredForm] = useState({
    location_x: 60,
    location_y: 40,
    minute: 45,
    match_period: 1,
    counterpress: false,
    under_pressure: false,
    play_pattern: "Regular Play"
  });
  const [prediction, setPrediction] = useState(null);
  const [isPredicting, setIsPredicting] = useState(false);

  const handlePredict = async () => {
    setIsPredicting(true);
    try {
      const res = await predictPress(predForm);
      setPrediction(res.data);
    } catch (err) {
      console.error(err);
      alert("Failed to predict. Has the model been trained?");
    } finally {
      setIsPredicting(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <header className="mb-8">
        <h1 className="text-3xl font-bold font-barlow text-white tracking-wide">Machine Learning Pipeline</h1>
        <p className="text-[var(--text-muted)] mt-1">Random Forest Classifier for Pressing Success</p>
      </header>

      <div className="mb-8">
        <ModelMetrics metrics={trainResult?.metrics} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-6">
          <h2 className="text-xl font-bold font-barlow text-white mb-6">Interactive Feature Importance</h2>
          <FeatureImportanceBar data={trainResult?.feature_importance} />
        </div>

        <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-6">
          <h2 className="text-xl font-bold font-barlow text-white mb-6">Live Press Predictor</h2>

          <div className="space-y-4">
            <div>
              <label className="flex justify-between text-sm text-[var(--text-muted)] mb-1">
                <span>Location X (Length)</span>
                <span>{predForm.location_x}</span>
              </label>
              <input
                type="range" min="0" max="120"
                className="w-full accent-[var(--accent)]"
                value={predForm.location_x}
                onChange={e => setPredForm({...predForm, location_x: parseInt(e.target.value)})}
              />
            </div>

            <div>
              <label className="flex justify-between text-sm text-[var(--text-muted)] mb-1">
                <span>Location Y (Width)</span>
                <span>{predForm.location_y}</span>
              </label>
              <input
                type="range" min="0" max="80"
                className="w-full accent-[var(--accent)]"
                value={predForm.location_y}
                onChange={e => setPredForm({...predForm, location_y: parseInt(e.target.value)})}
              />
            </div>

            {/* Mini Pitch visualization */}
            <div className="w-full aspect-[120/80] bg-[#2a3c24] border-2 border-white relative rounded overflow-hidden opacity-80 my-4 max-w-[300px] mx-auto">
              <div className="absolute top-0 bottom-0 left-1/2 w-0.5 bg-white opacity-50"></div>
              <div className="absolute top-1/2 left-1/2 w-12 h-12 border-2 border-white rounded-full -translate-x-1/2 -translate-y-1/2 opacity-50"></div>
              {/* Point */}
              <div
                className="absolute w-3 h-3 bg-[var(--accent)] rounded-full border border-black shadow-[0_0_8px_rgba(0,229,160,0.8)] -translate-x-1.5 -translate-y-1.5 transition-all duration-100"
                style={{
                  left: `${(predForm.location_x / 120) * 100}%`,
                  top: `${100 - (predForm.location_y / 80) * 100}%`
                }}
              ></div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-[var(--text-muted)] mb-1">Minute</label>
                <input
                  type="number" min="0" max="120"
                  className="w-full bg-[var(--bg-elevated)] border border-[var(--border)] rounded p-2 text-white"
                  value={predForm.minute}
                  onChange={e => setPredForm({...predForm, minute: parseInt(e.target.value)})}
                />
              </div>
              <div>
                <label className="block text-sm text-[var(--text-muted)] mb-1">Period</label>
                <select
                  className="w-full bg-[var(--bg-elevated)] border border-[var(--border)] rounded p-2 text-white"
                  value={predForm.match_period}
                  onChange={e => setPredForm({...predForm, match_period: parseInt(e.target.value)})}
                >
                  <option value={1}>1st Half</option>
                  <option value={2}>2nd Half</option>
                  <option value={3}>Extra Time 1</option>
                  <option value={4}>Extra Time 2</option>
                </select>
              </div>
            </div>

            <div className="flex items-center space-x-6 pt-2">
              <label className="flex items-center space-x-2 text-white cursor-pointer">
                <input
                  type="checkbox"
                  className="w-4 h-4 accent-[var(--accent)]"
                  checked={predForm.counterpress}
                  onChange={e => setPredForm({...predForm, counterpress: e.target.checked})}
                />
                <span>Counterpress</span>
              </label>
              <label className="flex items-center space-x-2 text-white cursor-pointer">
                <input
                  type="checkbox"
                  className="w-4 h-4 accent-[var(--accent)]"
                  checked={predForm.under_pressure}
                  onChange={e => setPredForm({...predForm, under_pressure: e.target.checked})}
                />
                <span>Under Pressure</span>
              </label>
            </div>

            <div className="pt-2">
              <label className="block text-sm text-[var(--text-muted)] mb-1">Play Pattern</label>
              <select
                className="w-full bg-[var(--bg-elevated)] border border-[var(--border)] rounded p-2 text-white"
                value={predForm.play_pattern}
                onChange={e => setPredForm({...predForm, play_pattern: e.target.value})}
              >
                <option value="Regular Play">Regular Play</option>
                <option value="From Throw In">From Throw In</option>
                <option value="From Free Kick">From Free Kick</option>
                <option value="From Goal Kick">From Goal Kick</option>
                <option value="From Corner">From Corner</option>
                <option value="From Keeper">From Keeper</option>
                <option value="From Counter">From Counter</option>
              </select>
            </div>

            <button
              className="w-full mt-4 py-3 bg-[var(--bg-elevated)] hover:bg-[var(--border)] border border-[var(--border)] rounded-lg text-white font-bold transition-colors"
              onClick={handlePredict}
              disabled={isPredicting}
            >
              {isPredicting ? 'Predicting...' : 'Predict Press Success'}
            </button>

            {prediction && (
              <div className="mt-4 p-4 rounded-lg bg-[var(--bg-elevated)] flex flex-col items-center border border-[var(--border)]">
                <div className="text-4xl font-barlow font-bold text-white mb-2">
                  {(prediction.probability * 100).toFixed(1)}%
                </div>
                <div className={`px-3 py-1 rounded text-xs font-bold ${prediction.probability > 0.5 ? 'bg-[var(--success)]/20 text-[var(--success)]' : 'bg-[var(--danger)]/20 text-[var(--danger)]'}`}>
                  {prediction.probability > 0.5 ? 'HIGH CHANCE' : 'LOW CHANCE'}
                </div>
                <div className="text-sm text-[var(--text-muted)] mt-2">
                  {prediction.interpretation}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MLModel;
