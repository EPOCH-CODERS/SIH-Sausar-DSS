import rasterio
from rasterio.enums import Resampling
from rasterio.warp import transform as warp_transform
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
import warnings

warnings.filterwarnings("ignore")
print("1. Loading Satellite Data...")

# Open Files
b2_file = rasterio.open('T44QMK_20251228T051231_B02_10m.jp2')
b3_file = rasterio.open('T44QMK_20251228T051231_B03_10m.jp2')
b4_file = rasterio.open('T44QMK_20251228T051231_B04_10m.jp2')
b8_file = rasterio.open('T44QMK_20251228T051231_B08_10m.jp2')
b11_file = rasterio.open('T44QMK_20251228T051231_B11_20m.jp2')
b12_file = rasterio.open('T44QMK_20251228T051231_B12_20m.jp2')

b2 = (b2_file.read(1) / 10000.0).astype(np.float32)
b3 = (b3_file.read(1) / 10000.0).astype(np.float32)
b4 = (b4_file.read(1) / 10000.0).astype(np.float32)
b8 = (b8_file.read(1) / 10000.0).astype(np.float32)

target_shape = (b4.shape[0], b4.shape[1])
b11 = (b11_file.read(1, out_shape=target_shape, resampling=Resampling.bilinear) / 10000.0).astype(np.float32)
b12 = (b12_file.read(1, out_shape=target_shape, resampling=Resampling.bilinear) / 10000.0).astype(np.float32)

print("2. Computing Spectral Indices...")
ferric_iron = np.where(b2 == 0, 0, b4 / b2).astype(np.float32)
hydroxyl = np.where(b12 == 0, 0, b11 / b12).astype(np.float32)
ferrous_iron = np.where((b8 == 0) | (b4 == 0), 0, (b12 / b8) + (b3 / b4)).astype(np.float32)

ndvi = np.where((b8 + b4) == 0, 0, (b8 - b4) / (b8 + b4)).astype(np.float32)
laterite = np.where(b3 == 0, 0, b4 / b3).astype(np.float32)

features = np.dstack((ferric_iron, hydroxyl, ferrous_iron, ndvi, laterite))
h, w, c = features.shape

print("3. Flattening Data...")
X_full = features.reshape(h * w, c)
X_full = np.nan_to_num(X_full, copy=False, nan=0.0, posinf=0.0, neginf=0.0)

print("4. Extracting Mine Coordinates...")
mine_names = ['Balaghat', 'Ukwa', 'Tirodi']
lats = [22.05, 22.08, 22.12]
lons = [80.71, 80.68, 80.74]
xs, ys = warp_transform('EPSG:4326', b4_file.crs, lons, lats)

# Store indices separately for each mine
mine_indices = {}
for name, x, y in zip(mine_names, xs, ys):
    row, col = b4_file.index(x, y)
    indices = []
    for dr in range(-50, 50):
        for dc in range(-50, 50):
            idx = (row + dr) * w + (col + dc)
            if 0 <= idx < h * w:
                indices.append(idx)
    mine_indices[name] = indices

# --- UPGRADE 3: MINE-GROUPED LOOCV ---
print("\n--- SIH DEFENSE: SPATIAL CROSS-VALIDATION ---")
for holdout_mine in mine_names:
    # 1. Isolate the holdout mine for testing
    test_pos = mine_indices[holdout_mine]
    
    # 2. Combine the other mines for training
    train_pos = []
    for m in mine_names:
        if m != holdout_mine:
            train_pos.extend(mine_indices[m])
            
    # 3. Get balanced negative background pixels
    train_neg = np.random.choice(h * w, len(train_pos), replace=False)
    
    # 4. Build CV training arrays
    X_cv_train = X_full[np.concatenate([train_pos, train_neg])]
    y_cv_train = np.concatenate([np.ones(len(train_pos)), np.zeros(len(train_neg))])
    
    # 5. Train a temporary CV model (using 100 trees for speed)
    rf_cv = RandomForestClassifier(n_estimators=100, max_features='sqrt', min_samples_leaf=10, class_weight='balanced', random_state=42, n_jobs=-1)
    rf_cv.fit(X_cv_train, y_cv_train)
    
    # 6. Test on the completely unseen holdout mine
    X_cv_test = X_full[test_pos]
    test_probs = rf_cv.predict_proba(X_cv_test)[:, 1]
    avg_prob = np.mean(test_probs)
    
    print(f"Hidden Mine: {holdout_mine.ljust(10)} | AI Predicted Prospectivity: {avg_prob:.2f} (Target > 0.50)")
print("---------------------------------------------\n")

print("5. Training Final Production Model...")
# Gather all positive indices for the final map
positive_indices = []
for m in mine_names:
    positive_indices.extend(mine_indices[m])

num_positives = len(positive_indices)
negative_indices = np.random.choice(h * w, num_positives, replace=False)

train_indices = np.concatenate([positive_indices, negative_indices])
X_train = X_full[train_indices]
y_train = np.concatenate([np.ones(num_positives), np.zeros(num_positives)])

rf = RandomForestClassifier(n_estimators=200, max_features='sqrt', min_samples_leaf=10, class_weight='balanced', random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)

print("\n--- FINAL FEATURE IMPORTANCE ---")
feature_names = ['Ferric Iron', 'Hydroxyl', 'Ferrous Iron', 'NDVI', 'Laterite']
for name, importance in zip(feature_names, rf.feature_importances_):
    print(f"{name}: {importance:.3f}")
print("--------------------------------\n")

print("6. Predicting Prospectivity Map (Chunking)...")
chunk_size = 5000000
probabilities = np.zeros(X_full.shape[0], dtype=np.float32)

for i in range(0, X_full.shape[0], chunk_size):
    end = min(i + chunk_size, X_full.shape[0])
    probabilities[i:end] = rf.predict_proba(X_full[i:end])[:, 1]
    print(f"   -> Processed pixels {i} to {end}...")

prospectivity_map = probabilities.reshape(h, w)

print("7. Rendering Final Map...")
small_map = prospectivity_map[::10, ::10]

plt.figure(figsize=(10, 8))
plt.imshow(small_map, cmap='viridis')
plt.colorbar(label='Probability of Manganese Pathfinders')
plt.title("Component 1: True Mineral Prospectivity Map (Tuned 5-Factor)")
plt.axis('off')
plt.show()
plt.savefig("component1_prospectivity_map.png", dpi=300, bbox_inches='tight')