import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error
import warnings

warnings.filterwarnings("ignore")

print("--- Component 2: XGBoost Production Forecasting ---")
print("1. Generating Synthetic Chronological Mining Logs...")

# Simulate 150 weeks of historical data for a single mine (e.g., Kandri)
np.random.seed(42)
weeks = np.arange(150)

# Base production
base_prod = 3000

# Features
# 1. Autoregressive lags (simulated as slight random walks around base)
lag_1 = base_prod + np.random.normal(0, 100, 150)
lag_4 = base_prod + np.random.normal(0, 150, 150)
lag_12 = base_prod + np.random.normal(0, 200, 150)

# 2. Meteorological Disruptions (Rainfall in mm)
# Spikes during monsoon (weeks 20-30, 72-82, 124-134)
rainfall = np.random.exponential(10, 150)
for w in range(150):
    if (20 <= w <= 30) or (72 <= w <= 82) or (124 <= w <= 134):
        rainfall[w] += np.random.uniform(50, 150)

# 3. Fleet Operational Health (0.0 to 1.0)
fleet_health = np.random.uniform(0.85, 0.99, 150)
# Introduce occasional massive breakdowns
fleet_health[45] = 0.40
fleet_health[95] = 0.50

# Target (Actual Production)
# Heavily influenced by rainfall and fleet health
production = base_prod + (lag_1 * 0.1) - (rainfall * 12) + ((fleet_health - 0.9) * 5000)
# Add some noise
production += np.random.normal(0, 50, 150)
# Ensure no negative production
production = np.clip(production, 0, None)

df = pd.DataFrame({
    'week': weeks,
    'lag_1': lag_1,
    'lag_4': lag_4,
    'lag_12': lag_12,
    'rainfall': rainfall,
    'fleet_health': fleet_health,
    'production': production
})

print("2. Performing Strict Chronological Train/Test Split...")
# CRITICAL: We cannot randomly shuffle time-series data. 
# We train on the first 120 weeks and test on the final 30 weeks.
train_df = df.iloc[:120]
test_df = df.iloc[120:]

features = ['lag_1', 'lag_4', 'lag_12', 'rainfall', 'fleet_health']
X_train = train_df[features]
y_train = train_df['production']
X_test = test_df[features]
y_test = test_df['production']

print("3. Training XGBoost Regressor...")
model = XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
model.fit(X_train, y_train)

print("4. Evaluating Forecast Accuracy on Unseen Future Data...")
preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)

print(f"\n--- VALIDATION RESULTS ---")
print(f"Mean Absolute Error (MAE): {mae:.2f} Tonnes")
print("--------------------------\n")

print("5. Rendering Forecast Chart...")
plt.figure(figsize=(12, 6))
plt.plot(train_df['week'], train_df['production'], label='Historical (Train)', color='#94a3b8')
plt.plot(test_df['week'], test_df['production'], label='Actual (Test)', color='#10b981', linewidth=2)
plt.plot(test_df['week'], preds, label='XGBoost Forecast', color='#ef4444', linestyle='--', linewidth=2)

# Highlight monsoon impact on test data
plt.axvspan(124, 134, color='#3b82f6', alpha=0.1, label='Monsoon Season')

plt.title("Component 2: XGBoost Production Forecasting (Kandri Mine)")
plt.xlabel("Operational Week")
plt.ylabel("Manganese Production (Tonnes)")
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
output_path = "component2_forecast.png"
plt.savefig(output_path, dpi=300)
print(f"Chart saved successfully to {output_path}")
