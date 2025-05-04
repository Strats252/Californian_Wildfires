# --------------------------------------------------
# Import
# --------------------------------------------------
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from PIL import Image
import rasterio
from rasterio.transform import from_bounds
from IPython.display import Image as IPImage, display

# --------------------------------------------------
# Load Landsat 8 OLI Image (Georeferenced)
# --------------------------------------------------
landsat_rgb_path = "C:/Users/danie/Data/Comp.tif" # change this to where you have saved your composite image from the downloaded imagery from USGS.

# Open the Landsat RGB image
with rasterio.open(landsat_rgb_path) as src:
    count = src.count
    if count >= 4:
        landsat_rgb = src.read([4, 3, 2])  # Red, Green, Blue bands
    else:
        raise ValueError(f"Error: Landsat image has only {count} bands — need at least 4 (for R, G, B).")

    landsat_rgb = np.transpose(landsat_rgb, (1, 2, 0))  # (rows, cols, bands)
    landsat_extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
    landsat_crs = src.crs

# --------------------------------------------------
# Stretch Landsat data to 0–255 and Apply Gamma Correction
# --------------------------------------------------
def normalize(array, gamma=1.2):
    array_min, array_max = np.percentile(array, (2, 98))
    scaled = np.clip((array - array_min) / (array_max - array_min), 0, 1)
    scaled = scaled ** (1/gamma)  # Brighten
    return (scaled * 255).astype(np.uint8)

landsat_rgb = np.dstack([normalize(landsat_rgb[:, :, i]) for i in range(3)])

# --------------------------------------------------
# Mask Black Background (Make Transparent) without this there will a black background to the imagery
# --------------------------------------------------
# Create an alpha channel: where all RGB values are near 0, make it transparent
black_mask = np.all(landsat_rgb <= 5, axis=2)  # Tolerance of 5
alpha_channel = np.where(black_mask, 0, 255).astype(np.uint8)

# Add alpha to Landsat (ensure it has an alpha channel)
landsat_rgba = np.dstack((landsat_rgb, alpha_channel))

# --------------------------------------------------
# Load Spatial Data (Shapefiles)
# --------------------------------------------------
counties_path = "Base_Data/California_County_Boundaries.shp" #If using data stored locally import full file path including drive letter.
BUA_path = "Base_Data/Urban_Area.shp" #If using data stored locally import full file path including drive letter.
highway_path = "Base_Data/State_Highway.shp" #If using data stored locally import full file path including drive letter.
fires_path = "Base_Data/fires_50000.shp" #If using data stored locally import full file path including drive letter.

gdf_counties = gpd.read_file(counties_path)
gdf_BUA = gpd.read_file(BUA_path)
gdf_highway = gpd.read_file(highway_path)
gdf_fires = gpd.read_file(fires_path)

# --------------------------------------------------
# Reproject All Layers to WGS84 (EPSG:4326)
# --------------------------------------------------
wgs84_crs = "EPSG:4326"  # WGS84 for lat/lon

gdf_counties = gdf_counties.to_crs(wgs84_crs)
gdf_BUA = gdf_BUA.to_crs(wgs84_crs)
gdf_highway = gdf_highway.to_crs(wgs84_crs)
gdf_fires = gdf_fires.to_crs(wgs84_crs)

# --------------------------------------------------
# Define the Geographic Extent (Latitude/Longitude)
# --------------------------------------------------
xmin, ymin = -125.0, 36.0  # (Longitude, Latitude) - Adjust as per your region should you wish to move AOI
xmax, ymax = -119.0, 41.0  # (Longitude, Latitude) - Adjust as per your region should you wish to move AOI

# --------------------------------------------------
# Create the Map Plot, order can be amended depending on display preferences
# --------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 10))
ax.set_facecolor('none')

# 1. Plot counties first
gdf_counties.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=0.5)

# 2. Plot Landsat RGB (with alpha channel for transparency) above counties
ax.imshow(
    landsat_rgba,  # Use RGBA to include the transparency - A is the ALPHA without this the black still draws
    extent=(float(xmin), float(xmax), float(ymin), float(ymax)),
    origin='upper'
)

# 3. Plot the other layers (BUA, highways, fires) above Landsat to ensure correct layer hierarchy
gdf_BUA.plot(ax=ax, color='grey', alpha=0.5)
gdf_highway.plot(ax=ax, color='green', linewidth=1.0)
gdf_fires.plot(
    ax=ax,
    column='GIS_ACRES', #This column is found within the attributes of the data
    cmap='OrRd',
    legend=True,
    edgecolor='black',
    linewidth=0.5
)

# Set visible area
ax.set_xlim([xmin, xmax])  # Longitude range
ax.set_ylim([ymin, ymax])  # Latitude range

# --------------------------------------------------
# Add County Labels
# --------------------------------------------------
label_column = 'CDT_NAME_S' #This column is found within the attributes of the data
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
# Add Custom Legend
# --------------------------------------------------
legend_elements = [
    mpatches.Patch(edgecolor='black', facecolor='none', label='Counties'), # Ensure that this matches colour plots found at line 81 onwards
    mpatches.Patch(facecolor='grey', alpha=0.5, label='Urban Area'), # Ensure that this matches colour plots found at line 81 onwards
    mpatches.Patch(facecolor='green', label='Highway'), # Ensure that this matches colour plots found at line 81 onwards
    mpatches.Patch(facecolor='white', edgecolor='black', label='Fires (by acres)') # Ensure that this matches colour plots found at line 81 onwards
]
ax.legend(handles=legend_elements, loc='lower left', bbox_to_anchor=(0, 0)) #This is location of where the legend will be lcocated

# Map title and axis labels
plt.title("California Wildfires with Landsat Background (WGS84)", fontsize=16) #Change the name of the map
plt.xlabel("Longitude") #X axis label name
plt.ylabel("Latitude") #Y axis label name
plt.tight_layout()

# --------------------------------------------------
# Export Plot as PNG Image
# --------------------------------------------------
temp_image_path = "California_Wildfires_Landsat.png"
fig.savefig(temp_image_path, dpi=300, bbox_inches='tight')
display(IPImage(filename=temp_image_path))
plt.close(fig)

# --------------------------------------------------
# Convert PNG to GeoTIFF with Georeferencing
# --------------------------------------------------
img = Image.open(temp_image_path).convert("RGBA")  # Use RGBA for transparency
img_arr = np.array(img)
height, width = img_arr.shape[:2]
transform = from_bounds(xmin, ymin, xmax, ymax, width, height)

with rasterio.open(
        "california_wildfires_landsat_map.tif", "w",
        driver="GTiff",
        height=height,
        width=width,
        count=4,  # 4 channels: RGBA
        dtype=img_arr.dtype,
        crs=wgs84_crs,
        transform=transform
) as dst:
    for i in range(4):  # Write 4 channels (RGBA) Alpha taken into account to ensure that mask works
        dst.write(img_arr[:, :, i], i + 1)

print("GeoTIFF saved as 'california_wildfires_landsat_map.tif'")
