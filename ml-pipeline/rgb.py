import rasterio
import numpy as np
import matplotlib.pyplot as plt

# 1. Open the raw band files
# We pass the exact filenames shown in your folder
blue_file = rasterio.open('T44QMK_20251228T051231_B02_10m.jp2')
green_file = rasterio.open('T44QMK_20251228T051231_B03_10m.jp2')
red_file = rasterio.open('T44QMK_20251228T051231_B04_10m.jp2')

# 2. Extract the grid of pixel numbers into NumPy arrays
# read(1) extracts Band 1 from each file as a 2D matrix
blue = blue_file.read(1)
green = green_file.read(1)
red = red_file.read(1)

# 3. Radiometric Scaling (The Physics)
# Sentinel-2 stores reflectance scaled by 10,000 to save file space.
# Dividing by 10000.0 restores real surface reflectance decimals (0.0 to 1.0).
blue = blue / 10000.0
green = green / 10000.0
red = red / 10000.0

# 4. Stack into an RGB Image
# Computer screens show color images by layering Red, Green, and Blue channels.
# np.dstack stacks these three 2D matrices into one 3D matrix (height, width, 3).
rgb = np.dstack((red, green, blue))

# 5. Contrast Enhancement & Clipping
# Raw reflectance can look dark on screen. Multiplying by 3.5 brightens it,
# and np.clip ensures values stay strictly between 0.0 (black) and 1.0 (white).
rgb = np.clip(rgb * 3.5, 0, 1)

# 6. Render the Satellite Image
plt.figure(figsize=(10, 10))
plt.imshow(rgb)
plt.title("Sentinel-2 True Color Composite (Balaghat)")
plt.axis('off')  # Hides pixel coordinate numbers on the edges
plt.show()