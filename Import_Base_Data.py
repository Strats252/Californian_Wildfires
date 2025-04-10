import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Load shapefiles
counties_path = "Base_Data/California_County_Boundaries_and_Identifiers.shp"
BUA_path = "Base_Data/2020_Adjusted_Urban_Area.shp"
highway_path = "Base_Data/Interstate_Road.shp"

gdf_counties = gpd.read_file(counties_path)
gdf_BUA = gpd.read_file(BUA_path)
gdf_highway = gpd.read_file(highway_path)

# Make sure all GeoDataFrames use the same CRS
target_crs = gdf_counties.crs
if gdf_BUA.crs != target_crs:
    gdf_BUA = gdf_BUA.to_crs(target_crs)
if gdf_highway.crs != target_crs:
    gdf_highway = gdf_highway.to_crs(target_crs)

# Plot all shapefiles
fig, ax = plt.subplots(figsize=(12, 10))

gdf_counties.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=0.5)
gdf_BUA.plot(ax=ax, color='grey', alpha=0.5)
gdf_highway.plot(ax=ax, color='green', linewidth=1.0)

# Manually add legend patches
legend_elements = [
    mpatches.Patch(edgecolor='black', facecolor='none', label='Counties'),
    mpatches.Patch(color='grey', alpha=0.5, label='Urban Area'),
    mpatches.Patch(color='green', label='Highway'),
]

plt.legend(handles=legend_elements)

plt.title("California Wildfires")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.show()
