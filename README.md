### 6.1 Project Overview
A full-stack Football Strategy Optimization web application that loads StatsBomb open event data via Python backend, runs a Random Forest ML pipeline to predict pressing success, generates spatial visualizations, and serves them through a REST API to a polished, coach-ready React dashboard. It uses StatsBomb free open data only.

### 6.2 Architecture Diagram (ASCII)
```
┌─────────────────────────────────────────────────────────┐
│  Browser (React + Vite, port 3000)                      │
│  Dashboard | Visualizations | ML Model | Insights        │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP (Axios)
                   ▼
┌─────────────────────────────────────────────────────────┐
│  FastAPI Backend (port 8000)                            │
│  /api/competitions  /api/matches  /api/train            │
│  /api/predict       /api/players  /api/model-history    │
│  /charts/* (static file serving)                       │
├────────────┬──────────────┬───────────────┬────────────┤
│ data_loader│ feature_eng. │ model.py      │ visualize  │
│ statsbombpy│ pandas/numpy │ scikit-learn  │ mplsoccer  │
└────────────┴──────────────┴───────────────┴────────────┘
                   │                │
         ┌─────────▼──────┐ ┌──────▼──────────┐
         │  SQLite DB     │ │  File System    │
         │  data/         │ │  outputs/charts │
         │  analytics.db  │ │  data/cache/    │
         └────────────────┘ └─────────────────┘
                   │
         ┌─────────▼──────────────┐
         │  StatsBomb Open Data   │
         │  (GitHub / API)        │
         └────────────────────────┘
```

### 6.3 Prerequisites
```
Python 3.11+
Node.js 20+
Git
```

### 6.4 Installation & Setup
```bash
# 1. Clone the repo
git clone <repo-url>
cd football-analytics

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Environment
cp .env.example .env           # Edit if needed (defaults work out of the box)

# 4. Frontend setup
cd ../frontend
npm install

# 5. Create required directories
mkdir -p ../data/cache ../outputs/charts
```

### 6.5 Running the Application

**Terminal 1 — Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```
Backend will be available at `http://localhost:8000`
API docs: `http://localhost:8000/docs` (auto-generated Swagger UI)

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```
App will be available at `http://localhost:3000`

### 6.6 First Use Walkthrough

```
1. Open http://localhost:3000
2. In the Match Selector, the default competition (UEFA Euro 2020) is pre-selected
3. Select a match (e.g., "Italy vs Turkey")
4. Enter team name (e.g., "Italy") — it auto-fills from home team
5. Click "Run Full Analysis"
   → Wait 15–60 seconds (first run downloads data; subsequent runs use cache)
6. Navigate to each tab to explore results
7. Go to ML Model → Live Predictor and test different press locations
```

### 6.7 Running Tests

```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# Frontend tests (if Jest/Vitest configured)
cd frontend
npm test
```

### 6.8 Project Structure Reference
```
football-analytics/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── data_loader.py           # StatsBomb data loading logic
│   ├── feature_engineering.py  # Feature extraction from events
│   ├── model.py                 # Random Forest training & inference
│   ├── visualizations.py        # All 5 chart generators (mplsoccer)
│   ├── database.py              # SQLite setup and queries
│   ├── schemas.py               # Pydantic response models
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── api/
│   │   │   └── client.js        # Axios API wrapper
│   │   ├── components/
│   │   │   ├── Sidebar.jsx
│   │   │   ├── MatchSelector.jsx
│   │   │   ├── StatCard.jsx
│   │   │   ├── ChartViewer.jsx
│   │   │   ├── InsightsTable.jsx
│   │   │   ├── FeatureImportanceBar.jsx
│   │   │   ├── ModelMetrics.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Visualizations.jsx
│   │   │   ├── MLModel.jsx
│   │   │   └── TacticalInsights.jsx
│   │   └── styles/
│   │       └── globals.css
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── data/
│   └── cache/                   # Auto-created; stores downloaded StatsBomb JSON
├── outputs/
│   └── charts/                  # Auto-created; stores generated PNG charts
├── README.md
└── .gitignore
```

### 6.9 Extending the Project
- Add more matches: pass any valid match_id to POST /api/train
- Compare teams: call the API twice with different `team` values
- Season analysis: loop over all match_ids in a season, aggregate metrics
- New visualizations: add a new function to `visualizations.py` and a new endpoint

### 6.10 Known Limitations
- First data load for a new match takes 10–60 seconds (network dependent)
- Model trained on a single match has limited generalizability — use multiple matches for production
- StatsBomb data is event-level; tracking data (player positions every frame) would improve the model

### 6.11 Data Source
StatsBomb Open Data: https://github.com/statsbomb/open-data
License: Free for educational and non-commercial use
