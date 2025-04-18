import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Load shapefiles
counties_path = "Base_Data/California_County_Boundaries_and_Identifiers_pro.shp"
BUA_path = "Base_Data/2020_Adjusted_Urban_Area.shp"
highway_path = "Base_Data/Interstate_Road.shp"
fires_path = "Base_Data/fires_50000.shp"

gdf_counties = gpd.read_file(counties_path)
gdf_BUA = gpd.read_file(BUA_path)
gdf_highway = gpd.read_file(highway_path)
gdf_fires = gpd.read_file(fires_path)

# Make sure all GeoDataFrames use the same CRS
target_crs = gdf_counties.crs
if gdf_BUA.crs != target_crs:
    gdf_BUA = gdf_BUA.to_crs(target_crs)
if gdf_highway.crs != target_crs:
    gdf_highway = gdf_highway.to_crs(target_crs)
if gdf_fires.crs != target_crs:
    gdf_fires = gdf_fires.to_crs(target_crs)

# Plot all shapefiles
fig, ax = plt.subplots(figsize=(12, 10))
ax.set_facecolor('lightblue') # This set the background colour to the map face

gdf_counties.plot(ax=ax, edgecolor='black', facecolor='grey', linewidth=0.5)
gdf_BUA.plot(ax=ax, color='grey', alpha=0.5)
gdf_highway.plot(ax=ax, color='green', linewidth=1.0)
gdf_fires.plot(ax=ax, edgecolor='black', facecolor='red', linewidth=0.5)

# Set display extent
xmin, xmax = -124.48146, -119.87385
ymin, ymax = 36.020764, 40.248248
ax.set_xlim([xmin, xmax])
ax.set_ylim([ymin, ymax])

# Create County Labels (within extent)
label_column = 'CDT_NAME_S'  # Adjust if needed
for idx, row in gdf_counties.iterrows():
    centroid = row.geometry.centroid
    if xmin <= centroid.x <= xmax and ymin <= centroid.y <= ymax:
        ax.text(
            centroid.x, centroid.y, str(row[label_column]),
            fontsize=8, ha='center', color='black', fontweight='bold'
        )

# Manually add legend patches
legend_elements = [
    mpatches.Patch(edgecolor='black', facecolor='none', label='Counties'),
    mpatches.Patch(color='grey', alpha=0.5, label='Urban Area'),
    mpatches.Patch(color='green', label='Highway'),
    mpatches.Patch(edgecolor='red', facecolor='red', label='Fires'),
]

plt.legend(handles=legend_elements)
plt.title("California Wildfires")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.tight_layout()
plt.show()
