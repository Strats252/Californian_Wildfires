import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from PIL import Image
import rasterio
from rasterio.transform import from_bounds

# ------------------------------
# Load Shapefiles
# ------------------------------
counties_path = "Base_Data/California_County_Boundaries_and_Identifiers_pro.shp"
BUA_path = "Base_Data/2020_Adjusted_Urban_Area.shp"
highway_path = "Base_Data/Interstate_Road.shp"
fires_path = "Base_Data/fires_50000.shp"

gdf_counties = gpd.read_file(counties_path)
gdf_BUA = gpd.read_file(BUA_path)
gdf_highway = gpd.read_file(highway_path)
gdf_fires = gpd.read_file(fires_path)

# ------------------------------
# Ensure all layers use the same CRS
# ------------------------------
target_crs = gdf_counties.crs
gdf_BUA = gdf_BUA.to_crs(target_crs)
gdf_highway = gdf_highway.to_crs(target_crs)
gdf_fires = gdf_fires.to_crs(target_crs)

# ------------------------------
# Set Map Extent
# ------------------------------
xmin, xmax = -124.48146, -119.87385
ymin, ymax = 36.020764, 40.248248

# ------------------------------
# Create Plot
# ------------------------------
fig, ax = plt.subplots(figsize=(12, 10))
ax.set_facecolor('lightblue')  # Set background color

# Plot Layers
gdf_counties.plot(ax=ax, edgecolor='black', facecolor='grey', linewidth=0.5)
gdf_BUA.plot(ax=ax, color='grey', alpha=0.5)
gdf_highway.plot(ax=ax, color='green', linewidth=1.0)
gdf_fires.plot(
    ax=ax,
    column='GIS_ACRES',
    cmap='OrRd',
    legend=True,
    edgecolor='black',
    linewidth=0.5
)

# Set extent
ax.set_xlim([xmin, xmax])
ax.set_ylim([ymin, ymax])

# Add County Labels (within extent)
label_column = 'CDT_NAME_S'
for idx, row in gdf_counties.iterrows():
    centroid = row.geometry.centroid
    if xmin <= centroid.x <= xmax and ymin <= centroid.y <= ymax:
        ax.text(
            centroid.x, centroid.y, str(row[label_column]),
            fontsize=8, ha='center', color='black', fontweight='bold'
        )

# Manual legend
legend_elements = [
    mpatches.Patch(edgecolor='black', facecolor='grey', label='Counties'),
    mpatches.Patch(facecolor='grey', alpha=0.5, label='Urban Area'),
    mpatches.Patch(facecolor='green', label='Highway'),
    mpatches.Patch(facecolor='white', edgecolor='black', label='Fires (by acres)')
]
plt.legend(handles=legend_elements, loc='lower left', bbox_to_anchor=(0, 0))

# Titles and layout
plt.title("California Wildfires")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.tight_layout()

# ------------------------------
# Export to temporary image (PNG)
# ------------------------------
temp_image_path = "temp_image.png"
fig.savefig(temp_image_path, dpi=300, bbox_inches='tight')
plt.close(fig)

# ------------------------------
# Export as GeoTIFF
# ------------------------------
img = Image.open(temp_image_path).convert("RGB")
img_arr = np.array(img)

# Calculate transform from extent and image size
height, width = img_arr.shape[0], img_arr.shape[1]
transform = from_bounds(xmin, ymin, xmax, ymax, width, height)

# Save as GeoTIFF
with rasterio.open(
    "california_wildfires_map.tif",
    "w",
    driver="GTiff",
    height=height,
    width=width,
    count=3,
    dtype=img_arr.dtype,
    crs=target_crs,
    transform=transform
) as dst:
    for i in range(3):  # RGB channels
        dst.write(img_arr[:, :, i], i + 1)

print("✅ GeoTIFF saved as 'california_wildfires_map.tif'")
