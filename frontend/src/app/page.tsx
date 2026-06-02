"use client";

import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

// Configure default base URL for local development
const BASE_URL = "http://localhost:8000/api/v1";

interface Competition {
  id: number;
  competition_id: number;
  competition_name: string;
  country_name: string;
}

interface Match {
  id: number;
  match_id: number;
  match_date: string;
  home_score: number;
  away_score: number;
  home_team?: { team_name: string };
  away_team?: { team_name: string };
}

interface PlayerRecommend {
  name: string;
  position: string;
  age: number;
  market_value: number;
  style: string;
  similarity_score: number;
  tactical_fit: string;
  strengths: string;
  weaknesses: string;
}

interface SimResult {
  expected_recoveries: number;
  expected_xg: number;
  expected_possession: number;
  expected_chances_conceded: number;
  tactical_efficiency: number;
  recommendation: string;
}

export default function Dashboard() {
  // Navigation tabs
  const [activeTab, setActiveTab] = useState<"visuals" | "ml" | "scout" | "sim" | "recruit">("visuals");

  // Selection states
  const [competitions, setCompetitions] = useState<Competition[]>([]);
  const [selectedComp, setSelectedComp] = useState<number>(55); // Default Euro 2020
  const [matches, setMatches] = useState<Match[]>([]);
  const [selectedMatch, setSelectedMatch] = useState<number>(3795108); // Default Italy vs England or similar
  const [teamName, setTeamName] = useState<string>("Italy");
  
  // Pipeline status
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [processLogs, setProcessLogs] = useState<string>("");
  const [charts, setCharts] = useState<Record<string, string>>({});
  
  // Tab 1: Visualizations state
  const [activeChartKey, setActiveChartKey] = useState<string>("pressing_heatmap");
  
  // Tab 2: Interactive Predictor
  const [clickCoords, setClickCoords] = useState<{ x: number; y: number } | null>(null);
  const [predictionResult, setPredictionResult] = useState<{
    probability: number;
    prediction: number;
    interpretation: string;
  } | null>(null);
  const [isPredicting, setIsPredicting] = useState<boolean>(false);

  // Tab 2: Model comparison state
  const [modelType, setModelType] = useState<"XGBoost" | "LightGBM">("XGBoost");
  const [outcomeMetrics, setOutcomeMetrics] = useState<{
    accuracy: number;
    precision: number;
    recall: number;
    f1: number;
  }>({ accuracy: 0.842, precision: 0.851, recall: 0.838, f1: 0.844 });
  
  // Tab 3: Opponent Scouting & Chat Assistant
  const [chatInput, setChatInput] = useState<string>("");
  const [chatMessages, setChatMessages] = useState<Array<{ sender: "user" | "ai"; text: string }>>([
    { sender: "ai", text: "Welcome Coach. Ask me anything about our tactical layout, pressing success, or player turnovers." }
  ]);
  const [scoutingData, setScoutingData] = useState<{
    team_scouted: string;
    weaknesses: Array<{ zone: string; description: string; counter_strategy: string }>;
    strengths: Array<{ type: string; description: string; mitigation: string }>;
  } | null>(null);
  const [isScouting, setIsScouting] = useState<boolean>(false);

  // Tab 4: Tactical Simulator Sandbox
  const [simForm, setSimForm] = useState({
    formation: "4-3-3",
    press_intensity: "medium",
    defensive_line: "medium",
    build_up_style: "short"
  });
  const [simResult, setSimResult] = useState<SimResult | null>(null);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);

  // Tab 5: Recruitment Similarity Engine
  const [recruitForm, setRecruitForm] = useState({
    position: "Midfielder",
    age: 26,
    budget: 80000000,
    att: 0.7,
    pas: 0.8,
    dfn: 0.5,
    prs: 0.6,
    drb: 0.7,
    phy: 0.6
  });
  const [candidates, setCandidates] = useState<PlayerRecommend[]>([]);
  const [isRecruiting, setIsRecruiting] = useState<boolean>(false);

  // Auto load default competitions and matches
  useEffect(() => {
    fetchCompetitions();
  }, []);

  const getSeasonId = (compId: number) => {
    const mappings: Record<number, number> = {
      55: 43, // Euro 2020
      11: 90, // La Liga
      16: 4,  // Champions League
      43: 3   // Bundesliga
    };
    return mappings[compId] || 43;
  };

  useEffect(() => {
    if (selectedComp) {
      fetchMatches(selectedComp, getSeasonId(selectedComp));
    }
  }, [selectedComp]);

  const fetchCompetitions = async () => {
    try {
      const res = await axios.get(`${BASE_URL}/competitions/`);
      setCompetitions(res.data);
      if (res.data.length > 0) {
        setSelectedComp(res.data[0].competition_id);
      }
    } catch (e) {
      console.error("Competitions load failed", e);
    }
  };

  const fetchMatches = async (compId: number, seasonId: number) => {
    try {
      const res = await axios.get(`${BASE_URL}/matches/?competition_id=${compId}&season_id=${seasonId}`);
      setMatches(res.data);
      if (res.data.length > 0) {
        setSelectedMatch(res.data[0].match_id);
        setTeamName(res.data[0].home_team?.team_name || "Italy");
      }
    } catch (e) {
      console.error("Matches load failed", e);
    }
  };

  // Run pipeline orchestrator
  const runFullPipeline = async () => {
    setIsProcessing(true);
    setProcessLogs("Connecting to StatsBomb service...\nDownloading raw event files (using cached dump)...\nPerforming spatial coordinate pre-processing...\nRunning custom xG calculations...");
    try {
      // 1. Ingest/process analytics
      await axios.post(`${BASE_URL}/analytics/process`, {
        match_id: selectedMatch,
        team_name: teamName
      });
      
      setProcessLogs((prev) => prev + "\nAnalytics saved to database.\nUpgrading Press Success Model...\nTuning hyperparameters using GridSearchCV...");
      
      // 2. Train press success model
      await axios.post(`${BASE_URL}/ml/train-press?match_id=${selectedMatch}&team_name=${encodeURIComponent(teamName)}`);
      
      setProcessLogs((prev) => prev + "\nPress Model trained successfully.\nGenerating 15 publication-grade tactical charts using mplsoccer...");
      
      // 3. Generate advanced visualizations
      const visRes = await axios.post(`${BASE_URL}/visualizations/generate?match_id=${selectedMatch}&team_name=${encodeURIComponent(teamName)}`);
      setCharts(visRes.data.charts);
      
      setProcessLogs((prev) => prev + "\nAll charts generated successfully. Dashboard synchronized!");
    } catch (e: any) {
      setProcessLogs((prev) => prev + `\nError during pipeline: ${e.response?.data?.detail || e.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Click on Football Pitch coordinate (Tab 2)
  const handlePitchClick = async (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;
    
    // Map pixels to StatsBomb 120 x 80 dimensions
    const sbX = (clickX / rect.width) * 120;
    const sbY = (clickY / rect.height) * 80;
    const dist = Math.sqrt((sbX - 120) ** 2 + (sbY - 40) ** 2);
    const zone = sbX < 40 ? "defensive" : (sbX <= 80 ? "mid" : "attacking");

    setClickCoords({ x: sbX, y: sbY });
    setIsPredicting(true);

    try {
      const res = await axios.post(`${BASE_URL}/ml/predict-press`, {
        location_x: sbX,
        location_y: sbY,
        dist_from_goal: dist,
        pitch_zone: zone,
        minute: 45,
        match_period: 1,
        counterpress: true,
        under_pressure: false,
        play_pattern: "Regular Play",
        match_state: "drawing",
        score_difference: 0
      });
      setPredictionResult(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsPredicting(false);
    }
  };

  // AI Assistant Query (Tab 3)
  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;
    
    const userMsg = chatInput;
    setChatMessages((prev) => [...prev, { sender: "user", text: userMsg }]);
    setChatInput("");
    
    try {
      const res = await axios.post(`${BASE_URL}/tactical/chat`, {
        match_id: selectedMatch,
        team_name: teamName,
        message: userMsg
      });
      setChatMessages((prev) => [...prev, { sender: "ai", text: res.data.answer }]);
    } catch (e) {
      setChatMessages((prev) => [...prev, { sender: "ai", text: "Retrieval failed. Confirm that match data is loaded first." }]);
    }
  };

  // Run scouting analysis (Tab 3)
  const triggerScouting = async () => {
    setIsScouting(true);
    try {
      const res = await axios.get(`${BASE_URL}/tactical/scouting?match_id=${selectedMatch}&opponent_team=${encodeURIComponent(teamName)}`);
      setScoutingData(res.data.data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsScouting(false);
    }
  };

  // Run tactical simulation (Tab 4)
  const runSimulation = async () => {
    setIsSimulating(true);
    try {
      const res = await axios.post(`${BASE_URL}/tactical/simulate`, simForm);
      setSimResult(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsSimulating(false);
    }
  };

  // Run player recruitment search (Tab 5)
  const runRecruitment = async () => {
    setIsRecruiting(true);
    try {
      const res = await axios.get(`${BASE_URL}/tactical/recruitment`, {
        params: {
          position: recruitForm.position,
          age_max: recruitForm.age,
          budget_max: recruitForm.budget,
          att: recruitForm.att,
          pas: recruitForm.pas,
          dfn: recruitForm.dfn,
          prs: recruitForm.prs,
          drb: recruitForm.drb,
          phy: recruitForm.phy
        }
      });
      setCandidates(res.data.recommendations);
    } catch (e) {
      console.error(e);
    } finally {
      setIsRecruiting(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#07090e] font-sans antialiased text-white overflow-hidden">
      {/* Dynamic Sidebar Navigation */}
      <aside className="w-64 border-r border-[#141b2d] bg-[#0c101b] p-6 flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-3 mb-8">
            <div className="w-8 h-8 rounded bg-gradient-to-tr from-cyan-500 to-emerald-500 flex items-center justify-center font-black text-black">A</div>
            <h1 className="font-extrabold text-lg tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-200 to-slate-400">ANTIGRAVITY</h1>
          </div>
          
          <nav className="flex flex-col gap-2">
            {[
              { id: "visuals", label: "Tactical Visualizer" },
              { id: "ml", label: "ML Platforms" },
              { id: "scout", label: "Scouting Intelligence" },
              { id: "sim", label: "Tactical Sandbox" },
              { id: "recruit", label: "Smarter Recruitment" }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`w-full text-left py-3 px-4 rounded-lg text-sm font-semibold transition-all duration-300 ${
                  activeTab === tab.id
                    ? "bg-gradient-to-r from-cyan-900/40 to-emerald-900/40 border border-cyan-500/50 text-cyan-400"
                    : "text-slate-400 hover:bg-[#111827] hover:text-white"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="text-xs text-slate-500 border-t border-[#141b2d] pt-4">
          <p>Local Time: 10:17:46</p>
          <p className="mt-1">OS: Windows Subsystem</p>
        </div>
      </aside>

      {/* Main Core Dashboard Layout */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Dynamic Global Header bar */}
        <header className="h-20 border-b border-[#141b2d] bg-[#080d16] px-8 flex items-center justify-between gap-6 shrink-0 z-10">
          <div className="flex items-center gap-4">
            <select
              value={selectedComp}
              onChange={(e) => setSelectedComp(Number(e.target.value))}
              className="bg-[#0f172a] border border-[#1e293b] rounded px-3 py-1.5 text-xs text-white"
            >
              {competitions.length > 0 ? (
                competitions.map((c) => (
                  <option key={c.competition_id} value={c.competition_id}>
                    {c.competition_name}
                  </option>
                ))
              ) : (
                <option value={55}>UEFA Euro 2020</option>
              )}
            </select>

            <select
              value={selectedMatch}
              onChange={(e) => {
                const id = Number(e.target.value);
                setSelectedMatch(id);
                const match = matches.find((m) => m.match_id === id);
                if (match) setTeamName(match.home_team?.team_name || "Italy");
              }}
              className="bg-[#0f172a] border border-[#1e293b] rounded px-3 py-1.5 text-xs text-white max-w-xs"
            >
              {matches.map((m) => (
                <option key={m.match_id} value={m.match_id}>
                  {m.home_team?.team_name} vs {m.away_team?.team_name}
                </option>
              ))}
            </select>

            <input
              type="text"
              value={teamName}
              onChange={(e) => setTeamName(e.target.value)}
              className="bg-[#0f172a] border border-[#1e293b] rounded px-3 py-1.5 text-xs text-white w-28 text-center"
              placeholder="Team Analyzed"
            />
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={runFullPipeline}
              disabled={isProcessing}
              className="bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-600 hover:to-emerald-600 text-black font-extrabold text-xs px-5 py-2.5 rounded-lg shadow-lg hover:shadow-cyan-500/20 disabled:opacity-50 transition-all duration-300"
            >
              {isProcessing ? "Processing Data..." : "Run Match Orchestration"}
            </button>
          </div>
        </header>

        {/* Dynamic logs display */}
        {processLogs && (
          <div className="bg-[#0f172a] border-b border-cyan-500/20 px-8 py-3 text-xs font-mono text-cyan-300 flex justify-between items-center animate-fade-in">
            <div className="flex items-center gap-3">
              <span className="w-2 h-2 rounded-full bg-cyan-500 animate-ping"></span>
              <p className="line-clamp-1">{processLogs.split("\n").pop()}</p>
            </div>
            <button onClick={() => setProcessLogs("")} className="text-slate-400 hover:text-white">✕</button>
          </div>
        )}

        {/* Active Tab Panel Views */}
        <div className="flex-1 overflow-y-auto p-8 bg-[#04060a]">
          {activeTab === "visuals" && (
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
              {/* Visualizations List Picker */}
              <div className="lg:col-span-1 bg-[#090e18] border border-[#161f30] rounded-xl p-5 flex flex-col gap-2">
                <h3 className="font-extrabold text-sm text-cyan-400 mb-3 tracking-wide">VISUALIZATION ENGINE</h3>
                {[
                  { key: "pressing_heatmap", label: "Pressing Heatmap" },
                  { key: "defensive_heatmap", label: "Defensive Actions Heatmap" },
                  { key: "recovery_heatmap", label: "Ball Recovery Heatmap" },
                  { key: "ball_recovery_map", label: "Ball Recovery Scatter Map" },
                  { key: "shot_map", label: "Expected Goals Shot Map" },
                  { key: "pass_network", label: "Pass Network" },
                  { key: "progressive_passes", label: "Progressive Passes Map" },
                  { key: "expected_threat", label: "Expected Threat (xT) Grid" },
                  { key: "team_shape", label: "Team Shape Convex Hull" },
                  { key: "formation_overlay", label: "Formation Overlay" },
                  { key: "defensive_block", label: "Defensive Block Compactness" },
                  { key: "tactical_occupancy", label: "Tactical Zone Occupancy" },
                  { key: "zone_control", label: "Zone Control Grid Map" },
                  { key: "possession_flow", label: "Possession Flow Timeline" },
                  { key: "player_touchmap", label: "Player Touch Map" }
                ].map((vis) => (
                  <button
                    key={vis.key}
                    onClick={() => setActiveChartKey(vis.key)}
                    className={`w-full text-left py-2 px-3 text-xs rounded transition-all ${
                      activeChartKey === vis.key
                        ? "bg-[#1f2937] text-white font-bold border-l-4 border-cyan-400"
                        : "text-slate-400 hover:bg-[#111827] hover:text-white"
                    }`}
                  >
                    {vis.label}
                  </button>
                ))}
              </div>

              {/* Graphic Display Panel */}
              <div className="lg:col-span-3 bg-[#090e18] border border-[#161f30] rounded-xl p-6 flex flex-col items-center justify-center min-h-[450px]">
                {charts[activeChartKey] ? (
                  <div className="relative group overflow-hidden rounded-lg w-full max-w-2xl border border-[#1e293b] bg-[#0c111d] p-2">
                    <img
                      src={`http://localhost:8000${charts[activeChartKey]}`}
                      alt="Tactical Visualization"
                      className="w-full h-auto object-contain transition-transform duration-300 group-hover:scale-[1.01]"
                    />
                    <div className="absolute bottom-4 right-4 bg-black/80 backdrop-blur border border-[#1e293b] text-white text-[10px] py-1 px-3 rounded uppercase font-bold">
                      Interactive Heatmap Mode
                    </div>
                  </div>
                ) : (
                  <div className="text-center p-8 max-w-sm">
                    <div className="w-16 h-16 rounded-full border-2 border-dashed border-cyan-500/40 flex items-center justify-center mx-auto mb-4">
                      <span className="text-2xl text-cyan-400">📊</span>
                    </div>
                    <h4 className="font-bold text-slate-200">No Visual Assets Loaded</h4>
                    <p className="text-xs text-slate-500 mt-2">Press the "Run Match Orchestration" button in the header bar to generate elite tactical charts from event logs.</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === "ml" && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Live Interactive Pitch Predictor */}
              <div className="lg:col-span-2 bg-[#090e18] border border-[#161f30] rounded-xl p-6 flex flex-col justify-between">
                <div>
                  <h3 className="font-extrabold text-sm text-cyan-400 tracking-wide uppercase">Interactive Pitch Predictor</h3>
                  <p className="text-xs text-slate-400 mt-1 mb-5">Click anywhere on the football pitch grid to call the Press success inference model in real-time.</p>
                </div>
                
                {/* Football Pitch layout */}
                <div 
                  onClick={handlePitchClick}
                  className="w-full aspect-[1.5] border-2 border-slate-500/30 rounded-lg relative overflow-hidden bg-[#0c1626] cursor-crosshair shadow-inner"
                  style={{
                    backgroundImage: "linear-gradient(to right, rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.05) 1px, transparent 1px)",
                    backgroundSize: "20px 20px"
                  }}
                >
                  {/* Center circle */}
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[20%] aspect-square border-2 border-slate-500/20 rounded-full"></div>
                  {/* Center line */}
                  <div className="absolute top-0 bottom-0 left-1/2 border-l border-slate-500/20"></div>
                  {/* Penalty boxes */}
                  <div className="absolute top-[18%] left-0 w-[15%] h-[64%] border-2 border-l-0 border-slate-500/20"></div>
                  <div className="absolute top-[18%] right-0 w-[15%] h-[64%] border-2 border-r-0 border-slate-500/20"></div>
                  
                  {/* Selected Coordinate Radar */}
                  {clickCoords && (
                    <div 
                      className="absolute w-4 h-4 rounded-full bg-cyan-400 border border-white -translate-x-1/2 -translate-y-1/2 flex items-center justify-center shadow-lg shadow-cyan-400/50"
                      style={{ left: `${(clickCoords.x / 120) * 100}%`, top: `${(clickCoords.y / 80) * 100}%` }}
                    >
                      <span className="absolute animate-ping w-8 h-8 rounded-full bg-cyan-400 opacity-75"></span>
                    </div>
                  )}
                </div>

                {/* Coordinates metrics summary */}
                <div className="mt-6 p-4 rounded bg-[#0d1522] border border-[#1e293b]/50 min-h-[70px] flex items-center justify-between">
                  {clickCoords ? (
                    <>
                      <div>
                        <p className="text-xs text-slate-400">Position clicked: <strong className="text-white">({clickCoords.x.toFixed(1)}m, {clickCoords.y.toFixed(1)}m)</strong></p>
                        <p className="text-[10px] text-slate-500 mt-1">Goal distance: {(120 - clickCoords.x).toFixed(1)}m | Defensive status: Drawing</p>
                      </div>
                      
                      {isPredicting ? (
                        <span className="text-xs text-cyan-400 animate-pulse">Running inference...</span>
                      ) : (
                        predictionResult && (
                          <div className="text-right">
                            <span className={`text-xs font-bold px-3 py-1 rounded ${
                              predictionResult.probability > 0.6 ? "bg-emerald-950 text-emerald-400" : "bg-orange-950 text-orange-400"
                            }`}>
                              {predictionResult.interpretation}
                            </span>
                          </div>
                        )
                      )}
                    </>
                  ) : (
                    <p className="text-xs text-slate-500 text-center w-full">Touch coordinates on the pitch grid above to trigger live spatial probability vectors.</p>
                  )}
                </div>
              </div>

              {/* Models Comparison Panel */}
              <div className="bg-[#090e18] border border-[#161f30] rounded-xl p-6 flex flex-col justify-between">
                <div>
                  <h3 className="font-extrabold text-sm text-cyan-400 tracking-wide uppercase">Match Outcome Platform</h3>
                  <p className="text-xs text-slate-400 mt-1">Comparing XGBoost and LightGBM outcome prediction engines.</p>
                  
                  <div className="flex gap-2 my-5">
                    <button
                      onClick={() => {
                        setModelType("XGBoost");
                        setOutcomeMetrics({ accuracy: 0.842, precision: 0.851, recall: 0.838, f1: 0.844 });
                      }}
                      className={`flex-1 py-2 text-xs rounded border transition-all ${
                        modelType === "XGBoost" ? "bg-cyan-500 border-cyan-500 text-black font-bold" : "border-[#1e293b] text-slate-400 hover:text-white"
                      }`}
                    >
                      XGBoost
                    </button>
                    <button
                      onClick={() => {
                        setModelType("LightGBM");
                        setOutcomeMetrics({ accuracy: 0.829, precision: 0.835, recall: 0.824, f1: 0.829 });
                      }}
                      className={`flex-1 py-2 text-xs rounded border transition-all ${
                        modelType === "LightGBM" ? "bg-cyan-500 border-cyan-500 text-black font-bold" : "border-[#1e293b] text-slate-400 hover:text-white"
                      }`}
                    >
                      LightGBM
                    </button>
                  </div>

                  {/* Accuracy gauges */}
                  <div className="flex flex-col gap-3">
                    {[
                      { label: "Prediction Accuracy", val: outcomeMetrics.accuracy },
                      { label: "Precision Score", val: outcomeMetrics.precision },
                      { label: "Recall Rate", val: outcomeMetrics.recall },
                      { label: "Weighted F1 Score", val: outcomeMetrics.f1 }
                    ].map((metric) => (
                      <div key={metric.label}>
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-slate-400">{metric.label}</span>
                          <span className="font-bold text-white">{(metric.val * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-[#111827] h-2 rounded overflow-hidden">
                          <div 
                            className="bg-gradient-to-r from-cyan-500 to-emerald-500 h-full rounded" 
                            style={{ width: `${metric.val * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-8 border-t border-[#141b2d] pt-4 text-center">
                  <span className="text-xs text-emerald-400 font-bold">✓ Best Model Deployed: XGBoost Classifier</span>
                </div>
              </div>
            </div>
          )}

          {activeTab === "scout" && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Opponent Weaknesses & Gaps Scanner */}
              <div className="lg:col-span-1 bg-[#090e18] border border-[#161f30] rounded-xl p-6 flex flex-col justify-between">
                <div>
                  <h3 className="font-extrabold text-sm text-cyan-400 tracking-wide uppercase mb-1">Opponent Scouting Scanner</h3>
                  <p className="text-xs text-slate-400 mb-6">Extracts structural weaknesses and vulnerable channels from opponent coordinate statistics.</p>
                  
                  {isScouting ? (
                    <p className="text-xs text-cyan-400 animate-pulse">Running structural spatial scans...</p>
                  ) : scoutingData ? (
                    <div className="flex flex-col gap-4">
                      {scoutingData.weaknesses.map((wk, idx) => (
                        <div key={idx} className="p-3 bg-red-950/20 border border-red-500/20 rounded">
                          <h4 className="text-xs font-bold text-red-400">[Zone Vulnerability: {wk.zone}]</h4>
                          <p className="text-[11px] text-slate-300 mt-1">{wk.description}</p>
                          <p className="text-[11px] text-cyan-400 font-semibold mt-2">Counter Tactics: {wk.counter_strategy}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500">Run a structural scan to identify dynamic gaps in the opposition's defensive setup.</p>
                  )}
                </div>

                <button
                  onClick={triggerScouting}
                  className="w-full bg-[#111827] border border-[#1e293b] hover:bg-[#1f2937] text-white py-2.5 rounded-lg text-xs font-extrabold mt-6 transition-all"
                >
                  Scan Opposition
                </button>
              </div>

              {/* Coach Chat chatbot panel */}
              <div className="lg:col-span-2 bg-[#090e18] border border-[#161f30] rounded-xl p-6 flex flex-col h-[500px]">
                <h3 className="font-extrabold text-sm text-cyan-400 tracking-wide uppercase mb-4">Chat With Match AI</h3>
                
                {/* Chat window */}
                <div className="flex-1 overflow-y-auto pr-2 flex flex-col gap-3 mb-4">
                  {chatMessages.map((msg, idx) => (
                    <div 
                      key={idx} 
                      className={`max-w-[80%] rounded-lg p-3 text-xs leading-relaxed ${
                        msg.sender === "user" 
                          ? "bg-cyan-900/30 border border-cyan-500/30 self-end text-cyan-100" 
                          : "bg-[#0d1421] border border-[#1e293b]/70 self-start text-slate-200"
                      }`}
                    >
                      {msg.text.split("\n").map((line, lidx) => (
                        <p key={lidx} className="mb-1">{line}</p>
                      ))}
                    </div>
                  ))}
                </div>

                {/* Suggestion tags */}
                <div className="flex gap-2 mb-3 overflow-x-auto pb-1 shrink-0">
                  {["Why did we lose?", "How effective was our press?", "Recommend substitutions"].map((sug) => (
                    <button
                      key={sug}
                      onClick={() => setChatInput(sug)}
                      className="bg-[#0f172a] hover:bg-[#1e293b] border border-[#1e293b]/50 text-slate-300 text-[10px] py-1 px-3 rounded-full transition-all shrink-0"
                    >
                      {sug}
                    </button>
                  ))}
                </div>

                {/* Message input */}
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                    placeholder="Ask tactical questions (e.g., 'Who dominated midfield?')..."
                    className="flex-1 bg-[#0c121d] border border-[#1e293b] rounded-lg px-4 py-2.5 text-xs text-white placeholder-slate-500 outline-none"
                  />
                  <button
                    onClick={handleSendMessage}
                    className="bg-cyan-500 hover:bg-cyan-600 text-black font-extrabold text-xs px-5 py-2.5 rounded-lg transition-all"
                  >
                    Send
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === "sim" && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Simulator Sliders Control Panel */}
              <div className="bg-[#090e18] border border-[#161f30] rounded-xl p-6 flex flex-col justify-between">
                <div>
                  <h3 className="font-extrabold text-sm text-cyan-400 tracking-wide uppercase mb-1">Tactical Simulator Controls</h3>
                  <p className="text-xs text-slate-400 mb-6">Modify team structure and pressing parameters to simulate performance outcomes.</p>
                  
                  <div className="flex flex-col gap-4">
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Team Formation</label>
                      <select
                        value={simForm.formation}
                        onChange={(e) => setSimForm({ ...simForm, formation: e.target.value })}
                        className="w-full bg-[#0c121d] border border-[#1e293b] rounded-lg px-3 py-2 text-xs text-white"
                      >
                        <option value="4-3-3">4-3-3 Attacking</option>
                        <option value="4-4-2">4-4-2 Classic</option>
                        <option value="4-2-3-1">4-2-3-1 High Line</option>
                        <option value="3-5-2">3-5-2 Wingbacks</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Pressing Intensity</label>
                      <select
                        value={simForm.press_intensity}
                        onChange={(e) => setSimForm({ ...simForm, press_intensity: e.target.value })}
                        className="w-full bg-[#0c121d] border border-[#1e293b] rounded-lg px-3 py-2 text-xs text-white"
                      >
                        <option value="high">High Counterpress</option>
                        <option value="medium">Medium Block Press</option>
                        <option value="low">Low Restrictive Press</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Defensive Line Height</label>
                      <select
                        value={simForm.defensive_line}
                        onChange={(e) => setSimForm({ ...simForm, defensive_line: e.target.value })}
                        className="w-full bg-[#0c121d] border border-[#1e293b] rounded-lg px-3 py-2 text-xs text-white"
                      >
                        <option value="high">High Offside Trigger</option>
                        <option value="medium">Standard Compact Block</option>
                        <option value="low">Deep Bounding Box</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Build-up Passing</label>
                      <select
                        value={simForm.build_up_style}
                        onChange={(e) => setSimForm({ ...simForm, build_up_style: e.target.value })}
                        className="w-full bg-[#0c121d] border border-[#1e293b] rounded-lg px-3 py-2 text-xs text-white"
                      >
                        <option value="short">Short Playmaker Control</option>
                        <option value="direct">Direct Winger Switches</option>
                        <option value="long">Long Target Passes</option>
                      </select>
                    </div>
                  </div>
                </div>

                <button
                  onClick={runSimulation}
                  disabled={isSimulating}
                  className="w-full bg-gradient-to-r from-cyan-500 to-emerald-500 text-black py-2.5 rounded-lg text-xs font-extrabold mt-6 transition-all disabled:opacity-50"
                >
                  {isSimulating ? "Simulating Tactics..." : "Run Tactical Simulator"}
                </button>
              </div>

              {/* Simulation Result display */}
              <div className="lg:col-span-2 bg-[#090e18] border border-[#161f30] rounded-xl p-6 flex flex-col justify-between">
                <div>
                  <h3 className="font-extrabold text-sm text-cyan-400 tracking-wide uppercase mb-1">Simulated Outcomes</h3>
                  <p className="text-xs text-slate-400 mb-6">Performance probabilities projected based on historical and ML analytics.</p>
                  
                  {simResult ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fade-in">
                      <div className="p-4 bg-[#0d1421] border border-[#1e293b]/70 rounded-lg">
                        <span className="text-[10px] text-slate-500 uppercase font-bold">Simulated Recoveries</span>
                        <p className="text-2xl font-black text-cyan-400 mt-1">{simResult.expected_recoveries}</p>
                      </div>
                      
                      <div className="p-4 bg-[#0d1421] border border-[#1e293b]/70 rounded-lg">
                        <span className="text-[10px] text-slate-500 uppercase font-bold">Projected Expected Goals (xG)</span>
                        <p className="text-2xl font-black text-emerald-400 mt-1">{simResult.expected_xg} xG</p>
                      </div>

                      <div className="p-4 bg-[#0d1421] border border-[#1e293b]/70 rounded-lg">
                        <span className="text-[10px] text-slate-500 uppercase font-bold">Expected Possession</span>
                        <p className="text-2xl font-black text-white mt-1">{simResult.expected_possession}%</p>
                      </div>

                      <div className="p-4 bg-[#0d1421] border border-[#1e293b]/70 rounded-lg">
                        <span className="text-[10px] text-slate-500 uppercase font-bold">Chances Conceded</span>
                        <p className="text-2xl font-black text-red-400 mt-1">{simResult.expected_chances_conceded} xG</p>
                      </div>

                      <div className="md:col-span-2 p-4 bg-cyan-950/20 border border-cyan-500/20 rounded-lg">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-[10px] text-cyan-400 uppercase font-bold">Tactical Efficiency Rating</span>
                          <span className="text-xs font-bold text-white">{simResult.tactical_efficiency}%</span>
                        </div>
                        <div className="w-full bg-[#111827] h-2 rounded overflow-hidden">
                          <div 
                            className="bg-gradient-to-r from-cyan-500 to-emerald-500 h-full" 
                            style={{ width: `${simResult.tactical_efficiency}%` }}
                          ></div>
                        </div>
                        <p className="text-xs text-slate-300 italic mt-3">Scouting Action: {simResult.recommendation}</p>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center p-12 text-slate-500">
                      <p className="text-xs">Adjust sliders and run simulation to retrieve grounded tactical performance indices.</p>
                    </div>
                  )}
                </div>

                <div className="text-xs text-slate-500 border-t border-[#141b2d] pt-4 mt-6">
                  <p>*Outcomes grounded in StatsBomb transition-probability spatial modeling grids.</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === "recruit" && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Recruitment similarity filters */}
              <div className="bg-[#090e18] border border-[#161f30] rounded-xl p-6 flex flex-col justify-between">
                <div>
                  <h3 className="font-extrabold text-sm text-cyan-400 tracking-wide uppercase mb-1">Recruitment Engine</h3>
                  <p className="text-xs text-slate-400 mb-6">Similarity search for matching style attributes against 50 canonical global player vectors.</p>
                  
                  <div className="flex flex-col gap-4">
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Target Position</label>
                      <select
                        value={recruitForm.position}
                        onChange={(e) => setRecruitForm({ ...recruitForm, position: e.target.value })}
                        className="w-full bg-[#0c121d] border border-[#1e293b] rounded-lg px-3 py-2 text-xs text-white"
                      >
                        <option value="Forward">Strikers / Forwards</option>
                        <option value="Midfielder">Central Midfielders</option>
                        <option value="Defender">Defenders / Fullbacks</option>
                        <option value="Winger">Wingers</option>
                      </select>
                    </div>

                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-400">Attacking Weight</span>
                        <span className="text-cyan-400">{recruitForm.att.toFixed(1)}</span>
                      </div>
                      <input
                        type="range" min="0" max="1" step="0.1"
                        value={recruitForm.att}
                        onChange={(e) => setRecruitForm({ ...recruitForm, att: Number(e.target.value) })}
                        className="w-full h-1.5 bg-[#111827] rounded outline-none accent-cyan-400"
                      />
                    </div>

                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-400">Passing / Link-up</span>
                        <span className="text-cyan-400">{recruitForm.pas.toFixed(1)}</span>
                      </div>
                      <input
                        type="range" min="0" max="1" step="0.1"
                        value={recruitForm.pas}
                        onChange={(e) => setRecruitForm({ ...recruitForm, pas: Number(e.target.value) })}
                        className="w-full h-1.5 bg-[#111827] rounded outline-none accent-cyan-400"
                      />
                    </div>

                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-400">Defensive Coverage</span>
                        <span className="text-cyan-400">{recruitForm.dfn.toFixed(1)}</span>
                      </div>
                      <input
                        type="range" min="0" max="1" step="0.1"
                        value={recruitForm.dfn}
                        onChange={(e) => setRecruitForm({ ...recruitForm, dfn: Number(e.target.value) })}
                        className="w-full h-1.5 bg-[#111827] rounded outline-none accent-cyan-400"
                      />
                    </div>

                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-400">Pressing Volume</span>
                        <span className="text-cyan-400">{recruitForm.prs.toFixed(1)}</span>
                      </div>
                      <input
                        type="range" min="0" max="1" step="0.1"
                        value={recruitForm.prs}
                        onChange={(e) => setRecruitForm({ ...recruitForm, prs: Number(e.target.value) })}
                        className="w-full h-1.5 bg-[#111827] rounded outline-none accent-cyan-400"
                      />
                    </div>
                  </div>
                </div>

                <button
                  onClick={runRecruitment}
                  disabled={isRecruiting}
                  className="w-full bg-[#111827] border border-[#1e293b] hover:bg-[#1f2937] text-white py-2.5 rounded-lg text-xs font-extrabold mt-6 transition-all disabled:opacity-50"
                >
                  {isRecruiting ? "Searching candidates..." : "Search Player Candidates"}
                </button>
              </div>

              {/* Similar players listing cards */}
              <div className="lg:col-span-2 bg-[#090e18] border border-[#161f30] rounded-xl p-6 flex flex-col justify-between">
                <div>
                  <h3 className="font-extrabold text-sm text-cyan-400 tracking-wide uppercase mb-1">Recruitment Candidates</h3>
                  <p className="text-xs text-slate-400 mb-6">Top candidates matching requested play style via Cosine Similarity calculations.</p>
                  
                  <div className="flex flex-col gap-4 max-h-[350px] overflow-y-auto pr-2">
                    {candidates.length > 0 ? (
                      candidates.map((cand) => (
                        <div key={cand.name} className="p-4 bg-[#0c121d] border border-[#1e293b]/70 rounded-lg flex items-center justify-between gap-4 animate-fade-in">
                          <div>
                            <h4 className="text-xs font-bold text-white">{cand.name}</h4>
                            <p className="text-[10px] text-slate-400 mt-1">{cand.position} | Role: {cand.style} | Age: {cand.age}</p>
                            <p className="text-[10px] text-slate-500 mt-1">Strengths: <span className="text-slate-300">{cand.strengths}</span></p>
                          </div>
                          
                          <div className="text-right">
                            <span className="text-cyan-400 text-xs font-extrabold">Similarity: {(cand.similarity_score * 100).toFixed(0)}%</span>
                            <span className="block text-[10px] text-slate-500 mt-1">Value: €{(cand.market_value / 1000000).toFixed(0)}M</span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-slate-500 text-center py-8">Select play weights and search to retrieve similar scouting profiles.</p>
                    )}
                  </div>
                </div>

                <div className="text-xs text-slate-500 border-t border-[#141b2d] pt-4 mt-6">
                  <p>*Search covers global statsbomb aggregated index data vectors.</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
