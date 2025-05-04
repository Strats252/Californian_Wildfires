# --------------------------------------------------
# Import Required Libraries
# --------------------------------------------------
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import rasterio
from rasterio.transform import from_bounds
from IPython.display import Image as IPImage, display

# --------------------------------------------------
# Load Landsat 8 OLI Image (Georeferenced)
# --------------------------------------------------
landsat_rgb_path = "C:/Users/danie/Data/Comp.tif"  # Update as needed

with rasterio.open(landsat_rgb_path) as src:
    count = src.count
    if count >= 4:
        landsat_rgb = src.read([4, 3, 2])  # Red, Green, Blue
    else:
        raise ValueError(f"Error: Landsat image has only {count} bands — need at least 4 (for R, G, B).")
    landsat_rgb = np.transpose(landsat_rgb, (1, 2, 0))
    landsat_crs = src.crs

# --------------------------------------------------
# Stretch Landsat data to 0–255 and Apply Gamma Correction
# --------------------------------------------------
def normalize(array, gamma=1.2):
    array_min, array_max = np.percentile(array, (2, 98))
    scaled = np.clip((array - array_min) / (array_max - array_min), 0, 1)
    scaled = scaled ** (1 / gamma)
    return (scaled * 255).astype(np.uint8)

landsat_rgb = np.dstack([normalize(landsat_rgb[:, :, i]) for i in range(3)])

# --------------------------------------------------
# Mask Black Background (Make Transparent)
# --------------------------------------------------
black_mask = np.all(landsat_rgb <= 5, axis=2)
alpha_channel = np.where(black_mask, 0, 255).astype(np.uint8)
landsat_rgba = np.dstack((landsat_rgb, alpha_channel))

# --------------------------------------------------
# Load Spatial Data
# --------------------------------------------------
counties_path = "Base_Data/California_County_Boundaries.shp"
BUA_path = "Base_Data/Urban_Area.shp"
highway_path = "Base_Data/State_Highway.shp"
fires_path = "Base_Data/fires_50000.shp"

gdf_counties = gpd.read_file(counties_path)
gdf_BUA = gpd.read_file(BUA_path)
gdf_highway = gpd.read_file(highway_path)
gdf_fires = gpd.read_file(fires_path)

# --------------------------------------------------
# Reproject All Layers to WGS84
# --------------------------------------------------
wgs84_crs = "EPSG:4326"

gdf_counties = gdf_counties.to_crs(wgs84_crs)
gdf_BUA = gdf_BUA.to_crs(wgs84_crs)
gdf_highway = gdf_highway.to_crs(wgs84_crs)
gdf_fires = gdf_fires.to_crs(wgs84_crs)

# --------------------------------------------------
# Define Geographic Extent
# --------------------------------------------------
xmin, ymin = -125.0, 36.0
xmax, ymax = -119.0, 41.0

# --------------------------------------------------
# Create Map Plot (No Marginalia)
# --------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 10))
ax.set_facecolor('none')

# Plot counties
gdf_counties.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=0.5)

# Plot Landsat imagery with alpha
ax.imshow(
    landsat_rgba,
    extent=(float(xmin), float(xmax), float(ymin), float(ymax)),
    origin='upper'
)

# Plot additional data layers
gdf_BUA.plot(ax=ax, color='grey', alpha=0.5)
gdf_highway.plot(ax=ax, color='green', linewidth=1.0)
gdf_fires.plot(
    ax=ax,
    column='GIS_ACRES',
    cmap='OrRd',
    legend=False,
    edgecolor='black',
    linewidth=0.5
)

# Set visible area
ax.set_xlim([xmin, xmax])
ax.set_ylim([ymin, ymax])

# --------------------------------------------------
# Remove All Marginalia
# --------------------------------------------------
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlabel("")
ax.set_ylabel("")
plt.title("")  # No title
plt.tight_layout(pad=0)

# --------------------------------------------------
# Export Clean PNG with Transparency
# --------------------------------------------------
temp_image_path = "California_Wildfires_Landsat_without_marginalia.png"
fig.savefig(temp_image_path, dpi=300, bbox_inches='tight', pad_inches=0, transparent=True)
display(IPImage(filename=temp_image_path))
plt.close(fig)

# --------------------------------------------------
# Convert PNG to GeoTIFF with Georeferencing
# --------------------------------------------------
img = Image.open(temp_image_path).convert("RGBA")
img_arr = np.array(img)
height, width = img_arr.shape[:2]
transform = from_bounds(xmin, ymin, xmax, ymax, width, height)

with rasterio.open(
        "california_wildfires_landsat_map.tif", "w",
        driver="GTiff",
        height=height,
        width=width,
        count=4,
        dtype=img_arr.dtype,
        crs=wgs84_crs,
        transform=transform
) as dst:
    for i in range(4):
        dst.write(img_arr[:, :, i], i + 1)

print("GeoTIFF saved as 'california_wildfires_landsat_map.tif'")
