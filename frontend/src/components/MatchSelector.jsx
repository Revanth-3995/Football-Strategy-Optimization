import React, { useState, useEffect, useContext } from 'react';
import { getCompetitions, getMatches, trainModel } from '../api/client';
import { AnalyticsContext } from '../App';
import LoadingSpinner from './LoadingSpinner';

const MatchSelector = () => {
  const {
    setSelectedMatch,
    selectedTeam,
    setSelectedTeam,
    setTrainResult,
    isLoading,
    setIsLoading,
    setError
  } = useContext(AnalyticsContext);

  const [competitions, setCompetitions] = useState([]);
  const [selectedComp, setSelectedComp] = useState("55_43"); // Default Euro 2020 (id=55, season=43)
  const [matches, setMatches] = useState([]);
  const [localMatchId, setLocalMatchId] = useState("");

  // Load competitions
  useEffect(() => {
    getCompetitions().then(res => {
      setCompetitions(res.data);
    }).catch(err => console.error(err));
  }, []);

  // Load matches when competition changes
  useEffect(() => {
    if (selectedComp) {
      const [compId, seasonId] = selectedComp.split('_');
      getMatches(compId, seasonId).then(res => {
        setMatches(res.data);
        if (res.data.length > 0) {
          setLocalMatchId(res.data[0].match_id.toString());
          setSelectedTeam(res.data[0].home_team);
        }
      }).catch(err => console.error(err));
    }
  }, [selectedComp]);

  // Update selected team when match changes
  useEffect(() => {
    const match = matches.find(m => m.match_id.toString() === localMatchId);
    if (match) {
      setSelectedTeam(match.home_team);
    }
  }, [localMatchId, matches, setSelectedTeam]);

  const handleRunAnalysis = async () => {
    if (!localMatchId || !selectedTeam) return;

    setIsLoading(true);
    setError(null);
    const match = matches.find(m => m.match_id.toString() === localMatchId);
    setSelectedMatch(match);

    try {
      const res = await trainModel(parseInt(localMatchId), selectedTeam);
      setTrainResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to run analysis");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-6 mb-8">
      <div className="flex flex-col md:flex-row gap-4 items-end">
        <div className="flex-1 w-full">
          <label className="block text-sm font-semibold text-[var(--text-muted)] mb-2">Competition & Season</label>
          <select
            className="w-full bg-[var(--bg-elevated)] border border-[var(--border)] text-white text-sm rounded-lg p-2.5 focus:ring-[var(--accent)] focus:border-[var(--accent)]"
            value={selectedComp}
            onChange={(e) => setSelectedComp(e.target.value)}
          >
            {competitions.map(c => (
              <option key={`${c.competition_id}_${c.season_id}`} value={`${c.competition_id}_${c.season_id}`}>
                {c.competition_name} — {c.season_name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex-2 w-full md:w-[40%]">
          <label className="block text-sm font-semibold text-[var(--text-muted)] mb-2">Match</label>
          <select
            className="w-full bg-[var(--bg-elevated)] border border-[var(--border)] text-white text-sm rounded-lg p-2.5 focus:ring-[var(--accent)] focus:border-[var(--accent)]"
            value={localMatchId}
            onChange={(e) => setLocalMatchId(e.target.value)}
          >
            {matches.map(m => (
              <option key={m.match_id} value={m.match_id}>
                {m.home_team} vs {m.away_team} ({m.match_id})
              </option>
            ))}
          </select>
        </div>

        <div className="flex-1 w-full">
          <label className="block text-sm font-semibold text-[var(--text-muted)] mb-2">Team</label>
          <input
            type="text"
            className="w-full bg-[var(--bg-elevated)] border border-[var(--border)] text-white text-sm rounded-lg p-2.5 focus:ring-[var(--accent)] focus:border-[var(--accent)]"
            value={selectedTeam}
            onChange={(e) => setSelectedTeam(e.target.value)}
          />
        </div>

        <button
          onClick={handleRunAnalysis}
          disabled={isLoading || !localMatchId}
          className="w-full md:w-auto px-6 py-2.5 bg-[var(--accent)] text-[#0a0e1a] font-bold rounded-lg hover:bg-[#00c58a] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center h-[42px]"
        >
          {isLoading ? <LoadingSpinner size="small" /> : "Run Full Analysis"}
        </button>
      </div>
    </div>
  );
};

export default MatchSelector;
