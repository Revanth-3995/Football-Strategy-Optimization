# Football Strategy Optimization using Spatial Event Data Analytics & Machine Learning (Phases 1-13)

Welcome to the **Football Strategy Optimization Platform** — a premium, publication-grade analytics and strategy optimization suite designed for professional managers, scouts, and performance analysts. 

This platform processes raw event-level data from StatsBomb, computes advanced tactical metrics, trains machine learning models, generates spatial visual assets, and exposes them through a high-performance REST API to an Opta/StatsBomb-inspired dark-mode SaaS dashboard.

---

## 1. System Architecture & Core Pipelines

The platform is designed around a fully decoupled, self-healing, and highly resilient three-tier architecture:

```
┌──────────────────────────────────────────────────────────┐
│              NEXT.JS 16 SAAS VISUAL DASHBOARD            │
│  Interactive Pitch Grid | AI Chatbot | Sliders | D3      │
└────────────────────────────┬─────────────────────────────┘
                             │ HTTP / JSON
                             ▼
┌──────────────────────────────────────────────────────────┐
│              FASTAPI REST BACKEND SERVER                 │
│  Self-Healing Ingestion | ML Services | Analytics Engine │
├───────────────┬───────────────────┬──────────────────────┤
│  Ingestion    │   Visualization   │    ML Platform       │
│  statsbombpy  │  mplsoccer/pyplot │  Scikit-Learn/XGB    │
└───────┬───────┴─────────┬─────────┴──────────┬───────────┘
        │                 │                    │
        ▼                 ▼                    ▼
┌───────────────┐ ┌───────────────┐ ┌──────────────────────┐
│  SQLite DB    │ │  File System  │ │   Resilient Cache    │
│  football_    │ │  statically   │ │   MemoryRedis /      │
│  analytics.db │ │  served charts│ │   Redis Server       │
└───────────────┘ └───────────────┘ └──────────────────────┘
```

### The Core Pipelines:
1. **Dynamic Open-Data Ingestion Ingestion Pipeline**: Auto-detects database structure on startup. It is pre-seeded with **24 world-class competitions** (including the **FIFA World Cup 2022 & 2018**, **UEFA Champions League**, **Premier League (EPL)**, **La Liga**, and **Euro 2020**). If a competition's matches or event-level data are selected, the pipeline dynamically communicates with StatsBomb's API, ingests the data on the fly, populates the SQLite database, and caches event logs.
2. **Analytics & Metrics Calculator**: Reads event logs, parses spatial attributes, and computes complex metrics (xG, xT, field tilt, press resistance, transition speed) in a vectorized pipeline.
3. **Advanced Visualization Generator**: Integrates `mplsoccer` and `matplotlib` to render 15 detailed tactical maps, saving them as static, cached PNG files served instantly to the client.
4. **Machine Learning & Inference Pipeline**: Handles tuned training grids, calculates performance scores for outcome predictors (XGBoost vs LightGBM), and runs instant real-time coordinate-based predictions.

---

## 2. Deep Dive: The 15 Visualizations (With Superstar Naming Formatter)

Every visualization is compiled from exact StatsBomb event coordinates. To ensure absolute publication-grade visual quality, we have integrated a **Superstar Player Naming Formatter** that automatically formats complex StatsBomb full names (e.g. converting `"Lionel Andrés Messi Cuccittini"` into `"Messi"`, `"Cristiano Ronaldo dos Santos Aveiro"` into `"C. Ronaldo"`, `"Kevin De Bruyne"` into `"De Bruyne"`, and ignoring suffix terms like `"Júnior"` or `"Senior"`):

1. **Pressing Heatmap**: A smooth, glowing map showing where your players applied intense defensive pressure. Concentrated red/orange zones show where your team successfully disrupted opponent possession.
2. **Defensive Action Heatmap**: Maps the concentration of tackles, blocks, interceptions, and clearances. It highlights your team's primary active defensive shielding zone.
3. **Recovery Heatmap**: Shows the density of ball recoveries. It pinpoints exactly where your team wins second balls or cleans up turnovers.
4. **Shot Map**: Maps every shot taken in the attacking half. Circles are sized based on shot quality (**Expected Goals - xG**) and color-coded/star-shaped to indicate goals vs misses.
5. **Pass Network**: Draws nodes for players at their average coordinate positions, sized by total passes attempted. Lines represent pass frequency between teammates. *Uses the Superstar Naming Formatter.*
6. **Player Touch Map**: Select any player to see a scatter plot of every event they participated in, overlayed with a custom density contour showing where they spent their time on the pitch.
7. **Zone Control Map**: Divides the pitch into 30 tactical zones (a 6x5 grid). It computes which team had more actions in each cell, coloring zones red for home dominance and blue for away.
8. **Ball Recovery Map**: A clean scatter mapping showing the exact location of recoveries, helping scouts see if you recover balls high up the pitch or deep in your box.
9. **Possession Flow Map**: A time-series momentum graph representing game state dominance, showcasing territorial control and threat generation minute-by-minute.
10. **Progressive Pass Map**: Draws vectors for passes that moved the ball at least 25% closer to the opponent's goal, indicating verticality and direct penetration channels.
11. **Expected Threat (xT) Map**: A 12x8 spatial grid overlay showing where passes and carries generated the highest expected threat, highlighting attacking corridors.
12. **Team Shape Convex Hull**: Draws a polygon connecting the average positions of your outfield players. This highlights team compactness, vertical stretching, and tactical width. *Uses the Superstar Naming Formatter.*
13. **Formation Overlay**: Places player position nodes based on average event coordinates to reconstruct the active shape (e.g. 4-3-3, 4-2-3-1) dynamically. *Uses the Superstar Naming Formatter.*
14. **Defensive Block Compactness**: Draws a dashed bounding box around the core 70% of your defensive events, indicating whether your block is deep, high, compact, or stretched.
15. **Tactical Zone Occupancy**: Divides the pitch into 18 standardized zones and prints the percentage of total team actions occurring in each zone, showcasing tactical asymmetry.

---

## 3. The Machine Learning Subsystems

### 3.1 Press Success Predictor (Random Forest Classifier)
* **What it does**: Predicts the probability (0% to 100%) that pressing an opponent at a specific `(x, y)` coordinate will win back the ball within 5 seconds.
* **How it works**: When you click **"Run Match Orchestration"**, the model dynamically trains a **Random Forest Classifier** using scikit-learn. It processes spatial attributes, splits data, performs **GridSearchCV hyperparameter tuning** (cross-validating `n_estimators`, `max_depth`, and `min_samples_split`), and saves the serialized model weights to `ml_models/press_success.pkl`.
* **Inference**: Click anywhere on the dashboard's Pitch Grid to make real-time predictions. The backend loads the saved weights from disk and calculates the probability instantly.

### 3.2 Match Outcome Predictor (XGBoost vs LightGBM)
* **What it does**: Analyzes aggregated match statistics (xG differences, possession shares, progressive pass counts, press success rates) to predict whether the game will result in a Win, Loss, or Draw.
* **How it works**: Fits both an **XGBoost Classifier** and a **LightGBM Classifier** in parallel, evaluates their F1-scores, and deploys the champion model to `ml_models/outcome_predictor.pkl`.

### 3.3 Formation Detection Engine (Shape-Matching & Clustering)
* **What it does**: Identifies the team's true formation (e.g., 4-3-3, 3-5-2, 4-2-3-1) dynamically based on active player average coordinates.

### 3.4 Player Role Detection (Event-Profile Cosine Similarity)
* **What it does**: Classifies a player's tactical role (e.g. *Deep Lying Playmaker*, *Wing Back*, *False Nine*, *Poacher*) instead of generic positions.

### 3.5 Player Style Clustering (K-Means)
* **What it does**: Groups squad players into 3 distinct style clusters based on their actions, projecting them onto a 2D map.

---

## 4. Upgraded Smarter Recruitment Similarity Engine

The **Smarter Recruitment Engine** allows scouts to identify players based on their style weight similarities using Cosine Similarity math. It features:
* **Rich 25-Player Database**: High-fidelity data representing elite global stars (e.g. Jude Bellingham, Pedri, Erling Haaland, Kylian Mbappe, Declan Rice, Luka Modric, Bukayo Saka, Phil Foden, Vinicius Jr, Virgil van Dijk, Trent Alexander-Arnold, Ruben Dias, etc.) with precise playstyle vectors.
* **Interactive UI Controls**: Sliders in the Next.js sidebar for complete control over search parameters:
  * **Attacking Weight**
  * **Passing / Link-up Weight**
  * **Defensive Coverage Weight**
  * **Pressing Volume Weight**
  * **Dribbling Weight** *(New!)*
  * **Physical Weight** *(New!)*
  * **Max Age Limit** *(New!)*
  * **Max Budget Cap** *(New!)*

---

## 5. Advanced Analytics & Metrics (Opta-grade)

* **Expected Goals (xG)**: The mathematical probability (0.0 to 1.0) that a shot results in a goal.
* **Expected Threat (xT)**: Assigns threat values to zones on the pitch, measuring threat generated by passes/carries.
* **Field Tilt**: Measures territorial dominance by calculating the team's share of total passes in the attacking third.
* **Press Resistance**: The percentage of passes completed successfully while under intense opponent pressure.
* **Counterpress Efficiency**: The percentage of times your team successfully recovered the ball within 5 seconds of applying defensive pressure.

---

## 6. How to Run the Platform

> [!IMPORTANT]
> **PowerShell Prompt Warning:** When copying commands, do **NOT** copy any leading `>>` or `(venv)` symbols. These are terminal prompts, not part of the commands, and will cause syntax errors.

### Prerequisites:
* Python 3.11+ (We recommend running inside the pre-configured virtual environment)
* Node.js 20+

### Step 1: Start the Backend REST API Server

Open a terminal at the project root directory (`Football-Strategy-Optimization`):

```powershell
# Windows (Direct execution utilizing the virtual environment - Recommended):
.\backend\venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000

# Alternative (Activating the virtual environment first):
# 1. Activate venv
.\backend\venv\Scripts\Activate.ps1
# 2. Run uvicorn
python -m uvicorn backend.main:app --reload --port 8000
```

*The API documentation will be available at `http://localhost:8000/docs` and server health check at `http://localhost:8000/health`.*

### Step 2: Start the Frontend Next.js Dashboard

Open a **new terminal tab or window** at the frontend folder (`Football-Strategy-Optimization/frontend`):

```bash
# 1. Install dependencies (if running for the first time)
npm install

# 2. Start Next.js development server
npm run dev
```

Open `http://localhost:3000` in your web browser.

---

## 7. Verification & Tests

To verify backend mathematical calculations, pipeline engines, and model training routines, run:

```powershell
# Windows:
.\backend\venv\Scripts\python.exe -m pytest backend/tests/ -v
```

All 8 analytical, metrics, and API test cases will pass successfully!
