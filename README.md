# Antigravity Football Intelligence Platform (Phases 1-13)

Welcome to the **Antigravity Football Intelligence Platform** — a premium, publication-grade analytics and strategy optimization suite designed for professional managers, scouts, and performance analysts. 

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
│  Self-Healing Loaders | ML Services | Analytics Engines  │
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
1. **Self-Healing Ingestion Pipeline**: Auto-detects database emptiness on startup. If SQLite lacks entries, the backend directly calls StatsBomb's API to fetch, process, and synchronize matches and competition categories dynamically.
2. **Analytics & Metrics Calculator**: Reads event logs, parses spatial attributes, and computes complex metrics (xG, xT, tilt) in a vector-grounded pipeline.
3. **Advanced Visualization Generator**: Integrates `mplsoccer` and `matplotlib` to render 15 detailed tactical maps, saving them as static, cached PNG files served instantly to the client.
4. **Machine Learning & Inference Pipeline**: Handles tuned training grids, calculates performance scores for outcome predictors (XGBoost vs LightGBM), and runs instant real-time coordinates predictions.

---

## 2. Deep Dive: The 15 Visualizations (Explained in Layman's Terms)

Every visualization is compiled from exact StatsBomb event coordinates to tell a detailed tactical story:

1. **Pressing Heatmap**: A smooth, glowing map showing where your players applied intense defensive pressure. Highly concentrated red/orange zones tell you where your team successfully disrupted opponent possession.
2. **Defensive Heatmap**: Maps the concentration of tackles, blocks, interceptions, and clearances. It highlights your team's primary active defensive shielding zone.
3. **Recovery Heatmap**: Shows the density of ball recoveries. It pinpoints exactly where your team wins second balls or cleans up turnovers.
4. **Shot Map**: Maps every shot taken in the attacking half. Circles are sized based on shot quality (**Expected Goals - xG**) and color-coded/star-shaped to indicate goals vs misses.
5. **Pass Network**: Draws nodes for players at their average coordinate positions, sized by total passes attempted. Lines are drawn between players who passed to each other, with thickness representing pass frequency.
6. **Player Touch Map**: Select any player to see a scatter plot of every event they participated in, overlayed with a custom density contour showing where they spent their time on the pitch.
7. **Zone Control Map**: Divides the pitch into 30 tactical zones (a 6x5 grid). It computes which team had more actions in each cell, coloring zones red for home dominance and blue for away.
8. **Ball Recovery Map**: A clean scatter mapping showing the exact location of recoveries, helping scouts see if you recover balls high up the pitch or deep in your box.
9. **Possession Flow Map**: A time-series momentum graph representing game state dominance. It showcases which team had territorial control and threat generation minute-by-minute.
10. **Progressive Pass Map**: Draws vectors for passes that moved the ball at least 25% closer to the opponent's goal, indicating verticality and direct penetration channels.
11. **Expected Threat (xT) Map**: A 12x8 spatial grid overlay showing where passes and carries generated the highest expected threat, highlighting attacking corridors.
12. **Team Shape Convex Hull**: Draws a polygon connecting the average positions of your outfield players. This highlights team compactness, vertical stretching, and overall tactical width.
13. **Formation Overlay**: Places player position nodes based on average event coordinates to reconstruct the active shape (e.g. 4-3-3, 4-2-3-1) dynamically.
14. **Defensive Block Compactness**: Draws a dashed bounding box around the core 70% of your defensive events, indicating whether your block is deep, high, compact, or stretched.
15. **Tactical Zone Occupancy**: Divides the pitch into 18 standardized zones and prints the percentage of total team actions occurring in each zone, showcasing tactical asymmetry.

---

## 3. The Machine Learning Subsystems

### 3.1 Press Success Predictor (Random Forest Classifier)
* **What it does**: Predicts the probability (0% to 100%) that pressing an opponent at a specific `(x, y)` coordinate will win back the ball within 5 seconds.
* **Why we built it**: Helps coaches optimize counterpress triggers. It dynamically learns spatial success patterns by analyzing game state, distance from goal, play patterns, and defensive pressure parameters.

### 3.2 Match Outcome Predictor (XGBoost vs LightGBM)
* **What it does**: Analyzes aggregated match statistics (xG differences, possession shares, progressive pass counts, press success rates) to predict whether the game will result in a Win, Loss, or Draw.
* **Why we built it**: Deploys the best classifier by evaluating and comparing accuracy, precision, recall, and F1 scores in real-time.

### 3.3 Formation Detection Engine (Shape-Matching & Clustering)
* **What it does**: Identifies the team's true formation (e.g., 4-3-3, 3-5-2, 4-2-3-1) dynamically based on active player average coordinates.
* **How it works**: Groups outfield players into Defense, Midfield, and Attack categories, refines layout counts using mathematical scaling, and matches them to canon formation geometries, returning a confidence rating.

### 3.4 Player Role Detection (Event-Profile Cosine Similarity)
* **What it does**: Classifies a player's tactical role (e.g. *Deep Lying Playmaker*, *Wing Back*, *False Nine*, *Poacher*) instead of generic positions.
* **How it works**: Compiles a high-dimensional vector of action rates (shots, progressive passes, crosses, tackles, recoveries) and computes its cosine similarity against 11 predefined play style prototypes.

### 3.5 Player Style Clustering (K-Means)
* **What it does**: Groups squad players into 3 distinct style clusters based on their actions, projecting them onto a 2D map.

---

## 4. Advanced Analytics & Metrics (Layman's Terms)

We computed custom tactical metrics to provide Opta-grade intelligence:
* **Expected Goals (xG)**: The mathematical probability (0.0 to 1.0) that a shot results in a goal. We calculate this using a custom logistic regression based on shot distance and angle to the goal center.
* **Expected Threat (xT)**: Assigns a threat value to zones on the pitch. Passes that move the ball from low-value zones (e.g., your defensive half) to high-value zones (e.g., edge of the box) accumulate positive xT.
* **Field Tilt**: Measures territorial dominance. It calculates your team's share of total passes completed in the attacking third. If you have 60% Field Tilt, you are pinning the opponent back.
* **Press Resistance**: The percentage of passes completed successfully while under intense opponent pressure.
* **Counterpress Efficiency**: The percentage of times your team successfully recovered the ball within 5 seconds of applying defensive pressure.
* **Transition Speed**: The progression velocity of the ball (meters/second) during vertical counter-attacks.

---

## 5. Engineering Implementation Choices (Why We Did It)

1. **SQLite Database Fallback**: We swapped PostgreSQL for a structured SQLite file locally. This ensures **zero-configuration setup**—meaning coaches can deploy the dashboard instantly on laptops without setting up external database services.
2. **Resilient Mock Redis Caching**: Redis is a standard backend requirement, but if Redis is offline, standard endpoints normally crash. I built a `MemoryRedis` class that handles timeouts and falls back to an in-memory dictionary.
3. **Hybrid Visual Rendering**: Matplotlib + `mplsoccer` compile beautiful, publication-grade PNG images on the backend. Meanwhile, the frontend uses an interactive SVG grid. This delivers the best of both worlds: highly responsive coordinate click-to-predict triggers on the web, and high-resolution, static tactical graphics ready for print.
4. **Self-Healing API Loaders**: If a database query for matches or competitions returns an empty list, the endpoints automatically fetch the data from StatsBomb on demand, keeping your local database synchronized.
5. **Typescript Type Safety**: I verified the Next.js app with `npx tsc --noEmit` and ensured **zero compilation errors**, guaranteeing bulletproof type-safety.

---

## 6. How to Run the Platform

### Prerequisites:
* Python 3.11+
* Node.js 20+

### Step 1: Start the Backend Server
```bash
# 1. Navigate to the backend folder
cd backend

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Run the FastAPI development server
python -m uvicorn main:app --reload --port 8000
```
The API documentation will be available at `http://localhost:8000/docs`.

### Step 2: Start the Frontend Next.js App
Open a **new terminal tab/window**:
```bash
# 1. Navigate to the frontend folder
cd frontend

# 2. Start Next.js development server
npm run dev
```
Open `http://localhost:3000` in your web browser.

---

## 7. Verification & Tests
Verify backend mathematical calculations and engines by running:
```bash
backend\venv\Scripts\python -m pytest backend/tests/ -v
```
All 8 analytical, metrics, and API test cases will pass successfully!
