import rasterio
from rasterio.enums import Resampling  # NEW: The resizing tool
import numpy as np
import matplotlib.pyplot as plt
import warnings

# Ignore divide-by-zero warnings in the terminal so it stays clean
warnings.filterwarnings("ignore")

# 1. OPEN FILES
b2_file = rasterio.open('T44QMK_20251228T051231_B02_10m.jp2')
b4_file = rasterio.open('T44QMK_20251228T051231_B04_10m.jp2')
b11_file = rasterio.open('T44QMK_20251228T051231_B11_20m.jp2')
b12_file = rasterio.open('T44QMK_20251228T051231_B12_20m.jp2')

# 2. READ & SCALE 10m BANDS (Like Day 1)
b2 = b2_file.read(1) / 10000.0
b4 = b4_file.read(1) / 10000.0

# 3. READ, RESAMPLE & SCALE 20m BANDS
# Look closely at how I force b11 to match b4's shape. 
b11 = b11_file.read(
    1,
    out_shape=(b4.shape[0], b4.shape[1]),
    resampling=Resampling.bilinear
) / 10000.0

# YOUR TURN: Do the exact same thing for b12, forcing it to match b4's shape.
b12 = b12_file.read(
    1,
    out_shape=(b4.shape[0], b4.shape[1]),
    resampling=Resampling.bilinear
) / 10000.0


# 4. COMPUTE SPECTRAL INDICES
# Ferric Iron (Fe3+) = Band 4 / Band 2
# We use np.where(condition, if_true, if_false) to avoid dividing by zero.
ferric_iron = np.where(b2 == 0, np.nan, b4 / b2)

# YOUR TURN: Hydroxyl Alteration = Band 11 / Band 12
# Use the same np.where logic. If b12 is 0, return np.nan, otherwise do b11 / b12.
hydroxyl = np.where(b12== 0, np.nan, b11/b12)


# 5. VISUALIZE THE MINERAL MAP (Showing Hydroxyl)
plt.figure(figsize=(10, 8))
# We use a 'hot' color map: black/red means low concentration, yellow/white means high.
plt.imshow(hydroxyl, cmap='hot', vmin=0.5, vmax=1.5)
plt.colorbar(label='Hydroxyl Index Value')
plt.title("Hydroxyl Alteration Map (Manganese Pathfinder)")
plt.axis('off')
plt.show()