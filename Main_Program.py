# --------------------------------------------------
# Import Required Libraries
# --------------------------------------------------
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from PIL import Image
import rasterio
from rasterio.transform import from_bounds

# --------------------------------------------------
# Load Spatial Data (Shapefiles)
# --------------------------------------------------
# Paths to your shapefiles
counties_path = "Base_Data/California_County_Boundaries_and_Identifiers_pro.shp"
BUA_path = "Base_Data/2020_Adjusted_Urban_Area.shp"
highway_path = "Base_Data/Interstate_Road.shp"
fires_path = "Base_Data/fires_50000.shp"

# Load shapefiles into GeoDataFrames
gdf_counties = gpd.read_file(counties_path)
gdf_BUA = gpd.read_file(BUA_path)
gdf_highway = gpd.read_file(highway_path)
gdf_fires = gpd.read_file(fires_path)

# --------------------------------------------------
# Reproject All Layers to the Same Coordinate System
# --------------------------------------------------
target_crs = gdf_counties.crs  # Use the counties CRS as the reference
gdf_BUA = gdf_BUA.to_crs(target_crs)
gdf_highway = gdf_highway.to_crs(target_crs)
gdf_fires = gdf_fires.to_crs(target_crs)

# --------------------------------------------------
# Define the Geographic Extent of the printed map
# --------------------------------------------------
# This focuses the map on a region in Northern California
xmin, xmax = -124.48146, -119.87385
ymin, ymax = 36.020764, 40.248248

# --------------------------------------------------
# Create the Map Plot
# --------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 10))
ax.set_facecolor('lightblue')  # Background for oceans/sky

# Plot the different spatial layers
gdf_counties.plot(ax=ax, edgecolor='black', facecolor='grey', linewidth=0.5)
gdf_BUA.plot(ax=ax, color='grey', alpha=0.5)
gdf_highway.plot(ax=ax, color='green', linewidth=1.0)
gdf_fires.plot(
    ax=ax,
    column='GIS_ACRES',         # Color fires by acreage
    cmap='OrRd',                # Orange-Red color map
    legend=True,                # Show legend for fire sizes
    edgecolor='black',
    linewidth=0.5
)

# Set visible area on the map
ax.set_xlim([xmin, xmax])
ax.set_ylim([ymin, ymax])

# --------------------------------------------------
# Add County Labels (inside the defined extent)
# --------------------------------------------------
label_column = 'CDT_NAME_S'  # County name column
for _, row in gdf_counties.iterrows():
    centroid = row.geometry.centroid
    if xmin <= centroid.x <= xmax and ymin <= centroid.y <= ymax:
        ax.text(
            centroid.x, centroid.y,
            str(row[label_column]),
            fontsize=8, ha='center',
            color='black', fontweight='bold'
        )

# --------------------------------------------------
# Add a Custom Legend
# --------------------------------------------------
legend_elements = [
    mpatches.Patch(edgecolor='black', facecolor='grey', label='Counties'),
    mpatches.Patch(facecolor='grey', alpha=0.5, label='Urban Area'),
    mpatches.Patch(facecolor='green', label='Highway'),
    mpatches.Patch(facecolor='white', edgecolor='black', label='Fires (by acres)')
]
plt.legend(handles=legend_elements, loc='lower left', bbox_to_anchor=(0, 0))

# Map title and axis labels
plt.title("California Wildfires", fontsize=16)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.tight_layout()

# --------------------------------------------------
# Export Plot as Temporary PNG Image
# --------------------------------------------------
temp_image_path = "temp_image.png"
fig.savefig(temp_image_path, dpi=300, bbox_inches='tight')
plt.close(fig)  # Close the plot to free memory

# --------------------------------------------------
# Convert PNG to GeoTIFF with Georeferencing
# --------------------------------------------------
# Open image and convert to numpy array
img = Image.open(temp_image_path).convert("RGB")
img_arr = np.array(img)

# Create geospatial transform from bounds and image size
height, width = img_arr.shape[:2]
transform = from_bounds(xmin, ymin, xmax, ymax, width, height)

# Save as a 3-band (RGB) GeoTIFF
with rasterio.open(
    "california_wildfires_map.tif", "w",
    driver="GTiff",
    height=height,
    width=width,
    count=3,
    dtype=img_arr.dtype,
    crs=target_crs,
    transform=transform
) as dst:
    for i in range(3):
        dst.write(img_arr[:, :, i], i + 1)  # Write R, G, B bands

print("✅ GeoTIFF saved as 'california_wildfires_map.tif'")
