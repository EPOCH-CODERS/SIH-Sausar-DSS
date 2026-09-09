from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBRegressor
import pulp

app = FastAPI(title="MOIL DSS API - FULL LIVE ML INTEGRATION")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# MINES METADATA
# ---------------------------------------------------------
MINES_META = [
    {"name": "Kandri", "lat": 21.42, "lon": 79.32, "type": "Underground", "high_grade": True},
    {"name": "Munsar", "lat": 21.40, "lon": 79.28, "type": "Underground", "high_grade": False},
    {"name": "Beldongri", "lat": 21.38, "lon": 79.29, "type": "Underground", "high_grade": False},
    {"name": "Gumgaon", "lat": 21.37, "lon": 78.98, "type": "Underground", "high_grade": False},
    {"name": "Dongri Buzurg", "lat": 21.53, "lon": 79.68, "type": "Opencast", "high_grade": False},
    {"name": "Chikla", "lat": 21.55, "lon": 79.73, "type": "Underground", "high_grade": False},
    {"name": "Balaghat", "lat": 21.82, "lon": 80.18, "type": "Underground", "high_grade": True},
    {"name": "Ukwa", "lat": 21.97, "lon": 80.47, "type": "Underground", "high_grade": False},
    {"name": "Tirodi", "lat": 21.68, "lon": 79.95, "type": "Opencast", "high_grade": False},
    {"name": "Sitapatore / Sukli", "lat": 21.65, "lon": 79.92, "type": "Opencast", "high_grade": False}
]

# ---------------------------------------------------------
# COMPONENT 1: RANDOM FOREST INITIALIZATION
# ---------------------------------------------------------
print("Initializing Random Forest (Component 1)...")
np.random.seed(42)
X_train_rf = np.random.rand(1000, 5)
y_train_rf = np.random.choice([0, 1], size=1000)
rf_model = RandomForestClassifier(n_estimators=50, max_features='sqrt', random_state=42, n_jobs=-1)
rf_model.fit(X_train_rf, y_train_rf)

# ---------------------------------------------------------
# COMPONENT 2: XGBOOST INITIALIZATION (SYNTHETIC DATA)
# ---------------------------------------------------------
print("Initializing XGBoost Regressor (Component 2)...")
# Generate synthetic chronological data for training (104 weeks = 2 years)
xgb_models = {}
for mine in MINES_META:
    # Features: lag_1, lag_4, lag_12, rainfall_mm, fleet_availability_pct
    X_train_xgb = np.random.rand(104, 5) 
    # Target: Production in tonnes
    y_train_xgb = 2000 + (X_train_xgb[:, 0] * 500) - (X_train_xgb[:, 3] * 800) + (X_train_xgb[:, 4] * 1000) + np.random.normal(0, 100, 104)
    
    model = XGBRegressor(n_estimators=50, max_depth=4, learning_rate=0.1, random_state=42)
    model.fit(X_train_xgb, y_train_xgb)
    xgb_models[mine["name"]] = model


@app.get("/")
def read_root():
    return {"message": "MOIL DSS API is running with Full Live ML Integration"}

# Component 1 Endpoint
@app.get("/api/prospectivity")
def get_prospectivity():
    live_results = []
    for mine in MINES_META:
        mine_pixel_signature = np.random.rand(1, 5)
        probability = rf_model.predict_proba(mine_pixel_signature)[0][1]
        
        if probability > 0.6: band = "High"
        elif probability > 0.4: band = "Medium"
        else: band = "Low"
            
        result = mine.copy()
        result["band"] = band
        result["probability"] = round(probability, 3)
        live_results.append(result)
    return {"mines": live_results}

# Component 2 Endpoint
@app.get("/api/forecast")
def get_forecast():
    weeks = [f"Week {i}" for i in range(1, 13)]
    mines_data = []
    
    for mine in MINES_META:
        model = xgb_models[mine["name"]]
        target_prod = 2500 if not mine["high_grade"] else 3500
        
        # Simulate future 12 weeks of inputs (some with high rainfall/low fleet to trigger shortfalls)
        X_future = np.random.rand(12, 5)
        # Introduce a harsh monsoon / breakdown for week 4 and 8
        X_future[3, 3] = 0.95 # High rainfall
        X_future[3, 4] = 0.40 # Low fleet uptime
        X_future[7, 4] = 0.30 # Major breakdown
        
        forecasts_arr = model.predict(X_future)
        
        forecasts = []
        for i, w in enumerate(weeks):
            forecasts.append({
                "week": w, 
                "forecast": max(0, int(forecasts_arr[i])), 
                "target": target_prod
            })
        mines_data.append({"mine": mine["name"], "data": forecasts})
    
    return {"forecasts": mines_data}

# Component 3 Endpoints
class ReallocationRequest(BaseModel):
    action: str
    transfer_id: str

@app.get("/api/decision/tier1")
def get_tier1_reallocation():
    print("Running PuLP ILP Optimizer (Component 3 Tier 1)...")
    # Simulate a scenario where 3 fleets are available to transfer
    fleets = [
        {"id": "F1", "equipment": "100T Dumper", "type": "Opencast", "from": "Dongri Buzurg"},
        {"id": "F2", "equipment": "LHD Loader", "type": "Underground", "from": "Munsar"},
        {"id": "F3", "equipment": "Surface Shovel", "type": "Opencast", "from": "Tirodi"}
    ]
    
    # Candidate destinations needing equipment
    destinations = [m for m in MINES_META if m["name"] not in ["Dongri Buzurg", "Munsar", "Tirodi"]]
    
    # Define PuLP Problem
    prob = pulp.LpProblem("Maximize_Ore_Recovery", pulp.LpMaximize)
    
    # Decision Variables: X[f, d] = 1 if fleet f transfers to destination d
    transfer_vars = {}
    for f in fleets:
        for d in destinations:
            transfer_vars[(f["id"], d["name"])] = pulp.LpVariable(f"transfer_{f['id']}_{d['name'].replace(' ', '')}", cat="Binary")
            
    # Objective Function: Sum of (Expected_Ore * Grade_Multiplier)
    # High grade gets 1.5x multiplier. Standard gets 1.0x.
    objective = []
    for f in fleets:
        for d in destinations:
            multiplier = 1.5 if d["high_grade"] else 1.0
            expected_ore = random.randint(500, 1500)
            objective.append(expected_ore * multiplier * transfer_vars[(f["id"], d["name"])])
    
    prob += pulp.lpSum(objective)
    
    # Constraints
    # 1. A fleet can only go to one destination
    for f in fleets:
        prob += pulp.lpSum([transfer_vars[(f["id"], d["name"])] for d in destinations]) <= 1
        
    # 2. HARD DOMAIN CONSTRAINT: Underground equipment CANNOT go to Opencast, and vice versa.
    for f in fleets:
        for d in destinations:
            if f["type"] != d["type"]:
                prob += transfer_vars[(f["id"], d["name"])] == 0 # Must be strictly zero
                
    # Solve
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    # Extract results
    approved_transfers = []
    for f in fleets:
        for d in destinations:
            if pulp.value(transfer_vars[(f["id"], d["name"])]) == 1.0:
                approved_transfers.append({
                    "id": f"T-{f['id']}-{d['name']}",
                    "from": f["from"],
                    "to": d["name"],
                    "equipment": f["equipment"],
                    "type": f["type"],
                    "grade_multiplier": 1.5 if d["high_grade"] else 1.0,
                    "status": "Pending"
                })
                
    return {"transfers": approved_transfers}

@app.get("/api/decision/tier2")
def get_tier2_exploration():
    # Strategic Exploration Ranking based on Heuristic
    # Priority_Score = Band_Score / (Distance_to_Nearest_MOIL_Mine_km + 1)
    
    candidates = [
        {"id": "E1", "name": "Sausar Zone Alpha", "band": "High", "distance_km": 2.1},
        {"id": "E2", "name": "Sausar Zone Beta", "band": "High", "distance_km": 15.4},
        {"id": "E3", "name": "Sausar Zone Gamma", "band": "Medium", "distance_km": 1.2},
        {"id": "E4", "name": "Sausar Zone Delta", "band": "Low", "distance_km": 0.5}
    ]
    
    def band_score(band):
        if band == "High": return 100
        if band == "Medium": return 50
        return 10
        
    for c in candidates:
        c["priority_score"] = round(band_score(c["band"]) / (c["distance_km"] + 1), 2)
        c["status"] = "Pending"
        
    # Sort descending by priority score
    candidates.sort(key=lambda x: x["priority_score"], reverse=True)
    
    return {"targets": candidates}

@app.post("/api/decision/action")
def perform_action(req: ReallocationRequest):
    return {"status": "success", "message": f"Transfer {req.transfer_id} {req.action}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
