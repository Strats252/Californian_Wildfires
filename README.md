<h1 align="center"> CALIFORNIA WILDFIRE VISUALISATION MAP</h1>
<p align="center">
  <strong>Overlay wildfires, highways, urban areas, and counties on Landsat 8 imagery.</strong><br>
  This will generate a publication-ready, georeferenced maps in PNG and GeoTIFF formats
</p>

---

##  INTRODUCTION

This Python script overlays California wildfire data on top of Landsat 8 satellite imagery, including key vector layers like counties, urban areas, and highways. The final output is both a high-resolution PNG map and a **GeoTIFF** image, georeferenced and ready for GIS or remote sensing applications. The workflow for this script process can be seen below here with highlights the main steps to achieve the desired output:

<p align="center">
  <img width="477" alt="image" src="https://github.com/user-attachments/assets/fc46c7de-d2d9-47e1-9798-271dcedb1b3b" />
</p>

---

## PROJECT STRUCTURE

├── Base_Data/ │  California_County_Boundaries.shp │ Urban_Area.shp │ State_Highway.shp │ fires_50000.shp | Comp.tif # Landsat 8 RGB composite | wildfire_map_script.py |

2 additonal files are generated once the script has been run. 

# Main Python script 

---

## REQUIREMENTS

Install the required Python libraries before running the script:

```bash
pip install geopandas rasterio matplotlib numpy pillow
```
---

## USAGE (Some steps are carried out in ArcPRO such as step 2 and 3)

  1.  Download and prepare Landsat 8 data

  2.  Create an RGB composite using Band 4 (Red), Band 3 (Green), Band 2 (Blue)

  3.  Save as Comp.tif

  4.  Prepare shapefiles

  5.  Ensure the following files are available in Base_Data/:

      California county boundaries

      Urban areas

      State highways

      Wildfire data with GIS_ACRES field

**Run the script**

```bash
python wildfire_map_script.py
```

This will generate:

  1.  California_Wildfires_Landsat.png

  2.  california_wildfires_landsat_map.tif (georeferenced which can then be brought into other applications such are ArcPRO and subsequently published to Portal

---

# INCLUDED LAYERS

| Layer            | Description                        | Style                          |
|------------------|------------------------------------|--------------------------------|
| Landsat Imagery  | RGB composite (Bands 4,3,2)         | True color + transparency      |
| County Boundaries| County outlines                    | Black border, no fill          |
| Urban Areas      | Developed regions                  | Semi-transparent gray          |
| State Highways   | Roads and routes                   | Solid green line               |
| Wildfires        | Fire polygons by acreage           | Orange-red gradient (OrRd)     |

---

# MAP COORDINATE SYSTEM
All spatial layers are reprojected to:

  + EPSG:4326 — WGS84 (Latitude/Longitude)

You can modify the Area of Interest in the script by adjusting:

```bash
xmin, ymin = -125.0, 36.0  # Lower-left (Longitude, Latitude)
xmax, ymax = -119.0, 41.0  # Upper-right (Longitude, Latitude)
```

---

## OUTPUT FILES

| File                                 | Format   | Description                                      |
|--------------------------------------|----------|--------------------------------------------------|
| `California_Wildfires_Landsat.png`   | PNG      | Final map with all overlays                     |
| `california_wildfires_landsat_map.tif`| GeoTIFF | Georeferenced raster with RGBA channels         |

These can be used for reports, analysis, or imported into GIS software.

---

## NOTES

- The Landsat image must have at least 4 bands to allow extraction of R, G, B channels.
- The wildfire shapefile should include a column named `GIS_ACRES` for coloring by size.
- The map uses a manual alpha mask to remove black background from the satellite image.
- Custom labels for counties are added using centroid positioning.

---

## LICENSE

This project is available under the [MIT License](LICENSE). This is license that allows users freedom to use, share and modify.

---
## KNOWN ERRORS AND ISSUES

It is known that the Tif output changes the symbology of the fires and presents itself different to the .Png file. This is something that hasn't been able to be corrected. 

---

## BRANCHES

A branch has been created to remove the marginalia from the outputs should the user wish to remove it for a better display in GIS software.

---

## TROUBLESHOOTING

Please use the document attached in the repository https://github.com/Strats252/Californian_Wildfires/blob/main/Wildfire%20Proximity%20to%20Populated%20Areas%20and%20Infrastructure%20in%20California-Daniel%20Stratford%20B00992246.pdf  to answer potential errors that may be faced.

---

## AUTHOR

Developed by **Daniel Stratford**  
Student number: B00992246
This program has been created for academic purposes only.

For questions or issues please contact stratford-d1@ulster.ac.uk 
