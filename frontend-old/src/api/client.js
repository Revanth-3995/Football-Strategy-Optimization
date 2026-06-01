import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: BASE_URL });

export const getCompetitions = () => api.get('/api/competitions');
export const getMatches = (competitionId, seasonId) =>
  api.get(`/api/matches?competition_id=${competitionId}&season_id=${seasonId}`);
export const trainModel = (matchId, team) =>
  api.post('/api/train', { match_id: matchId, team });
export const predictPress = (data) => api.post('/api/predict', data);
export const getPlayers = (matchId, team) =>
  api.get(`/api/players?match_id=${matchId}&team=${team}`);
export const getModelHistory = (matchId) =>
  api.get(`/api/model-history?match_id=${matchId}`);
