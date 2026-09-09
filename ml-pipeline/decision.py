import pulp
import pandas as pd

print("==================================================")
print("Component 3: Two-Tiered Decision Engine")
print("==================================================\n")

# ---------------------------------------------------------
# TIER 1: IMMEDIATE FLEET REALLOCATION (DAYS TO WEEKS)
# ---------------------------------------------------------
print("--- TIER 1: PuLP ILP Fleet Optimizer ---")
print("Objective: Maximize Recovered Ore * Grade Multiplier - Transfer Costs")
print("Hard Constraint: Underground equipment CANNOT enter Opencast pits, and vice versa.\n")

# 1. Define the Available Fleets needing reallocation
fleets = [
    {"id": "F1", "equipment": "100T Dumper", "type": "Opencast", "current_loc": "Dongri Buzurg"},
    {"id": "F2", "equipment": "LHD Loader", "type": "Underground", "current_loc": "Munsar"},
    {"id": "F3", "equipment": "Surface Shovel", "type": "Opencast", "current_loc": "Sitapatore"}
]

# 2. Define Candidate Destinations
destinations = [
    {"name": "Kandri", "type": "Underground", "high_grade": True, "expected_ore": 1200, "transfer_cost": 200},
    {"name": "Balaghat", "type": "Underground", "high_grade": True, "expected_ore": 1500, "transfer_cost": 500},
    {"name": "Tirodi", "type": "Opencast", "high_grade": False, "expected_ore": 900, "transfer_cost": 100},
    {"name": "Beldongri", "type": "Underground", "high_grade": False, "expected_ore": 800, "transfer_cost": 150}
]

# Initialize Problem
prob = pulp.LpProblem("Maximize_MOIL_Ore_Recovery", pulp.LpMaximize)

# Decision Variables: X[f, d] = 1 if fleet f transfers to destination d
transfer_vars = {}
for f in fleets:
    for d in destinations:
        transfer_vars[(f["id"], d["name"])] = pulp.LpVariable(
            f"transfer_{f['id']}_to_{d['name']}", cat="Binary"
        )

# Objective Function
objective = []
for f in fleets:
    for d in destinations:
        # 1.5x Grade multiplier for High-Grade Mn deposits
        multiplier = 1.5 if d["high_grade"] else 1.0
        economic_value = (d["expected_ore"] * multiplier) - d["transfer_cost"]
        objective.append(economic_value * transfer_vars[(f["id"], d["name"])])

prob += pulp.lpSum(objective)

# Constraint 1: A fleet can only go to a maximum of 1 destination
for f in fleets:
    prob += pulp.lpSum([transfer_vars[(f["id"], d["name"])] for d in destinations]) <= 1

# Constraint 2: PHYSICAL BOUNDARY (Underground vs Opencast)
# "Underground machinery (LHDs/winches) and surface fleet (dumpers/shovels) are completely incompatible."
for f in fleets:
    for d in destinations:
        if f["type"] != d["type"]:
            prob += transfer_vars[(f["id"], d["name"])] == 0 # Must be exactly 0

print("Solving ILP...")
prob.solve(pulp.PULP_CBC_CMD(msg=0))

print(f"Status: {pulp.LpStatus[prob.status]}\n")
print("OPTIMAL ALLOCATIONS:")
df_results = []
for f in fleets:
    allocated = False
    for d in destinations:
        if pulp.value(transfer_vars[(f["id"], d["name"])]) == 1.0:
            df_results.append({
                "Fleet ID": f["id"],
                "Equipment": f["equipment"],
                "Type": f["type"],
                "Transferred To": d["name"],
                "Destination Type": d["type"],
                "Grade Multiplier": "1.5x" if d["high_grade"] else "1.0x"
            })
            allocated = True
    if not allocated:
        df_results.append({
            "Fleet ID": f["id"],
            "Equipment": f["equipment"],
            "Type": f["type"],
            "Transferred To": "IDLE (No compatible/profitable destination)",
            "Destination Type": "-",
            "Grade Multiplier": "-"
        })

print(pd.DataFrame(df_results).to_string(index=False))
print("\nNotice how the LHD Loader (Underground) is mathematically prevented from entering Tirodi (Opencast).")


# ---------------------------------------------------------
# TIER 2: STRATEGIC EXPLORATION RANKING (MONTHS TO YEARS)
# ---------------------------------------------------------
print("\n--- TIER 2: Strategic Exploration Ranking ---")
print("Formula: Priority_Score = Band_Score / (Distance_to_Nearest_MOIL_Mine_km + 1)")

# Exploration Candidates (from Component 1 output)
candidates = [
    {"name": "Sausar Zone Alpha", "band": "High", "distance_km": 2.1},
    {"name": "Sausar Zone Beta", "band": "High", "distance_km": 15.4},
    {"name": "Sausar Zone Gamma", "band": "Medium", "distance_km": 1.2},
    {"name": "Sausar Zone Delta", "band": "Low", "distance_km": 0.5}
]

def get_band_score(band):
    if band == "High": return 100
    if band == "Medium": return 50
    return 10

for c in candidates:
    c["Priority Score"] = round(get_band_score(c["band"]) / (c["distance_km"] + 1), 2)

# Sort by priority score
candidates.sort(key=lambda x: x["Priority Score"], reverse=True)

df_tier2 = pd.DataFrame(candidates)
print("\nRANKED EXPLORATION TARGETS:")
print(df_tier2.to_string(index=False))
