---
name: urban-landuse-mapping
description: Build reusable planning-report land-use current-status maps, land-use structure pie/donut charts, class area ranking charts, audit tables, and artifact manifests from polygon GeoJSON/GPKG/Shapefile data. Use when the task mentions 用地现状图, land-use mapping, land-use structure analysis, planning report figures, OSM landuse polygons, or GIS polygon thematic cartography.
---

# Urban Land-Use Mapping

Use this skill to turn polygon land-use data into a repeatable planning-cartography package, not a one-off figure.

## Default Path

Run the bundled pure-Python renderer first:

```powershell
python "<skill_dir>\scripts\render_landuse_package.py" --input "<landuse.geojson>" --out-dir "<output_dir>" --study-area "杭州" --title "杭州市用地现状图" --basemap carto-light-nolabels --basemap-alpha 0.38
```

The script uses GeoPandas/Shapely/pyproj/Matplotlib/Pillow. QGIS is optional, not required.

Use QGIS only when the deliverable needs QGIS Processing algorithms, a `.qgz/.qgs` workbench, desktop cartographic inspection, or the Python repair path fails on invalid geometries.

For a report map, select a meaningful administrative study area instead of rendering a whole prefecture by default:

```powershell
python "<skill_dir>\scripts\render_landuse_package.py" `
  --input "<landuse.geojson>" `
  --out-dir "<output_dir>" `
  --admin-boundary "<county_boundary.shp>" `
  --admin-name "上城区,拱墅区,西湖区,滨江区" `
  --admin-parent-field "地级" `
  --admin-parent "杭州市" `
   --study-area "杭州主城区" `
  --title "杭州主城区用地现状图" `
  --basemap carto-light-nolabels `
  --basemap-alpha 0.38
```

Repeat `--admin-name` or pass comma-separated names. The renderer reprojects the boundary to the land-use CRS, clips polygons to the selected boundary, then recomputes area in the requested or inferred metric CRS.

## Workflow

1. Treat the user-provided spatial file as the data contract. Do not silently swap in sibling data.
2. Inspect CRS, geometry types, feature count, candidate classification fields, and any source color field.
3. Choose the class field automatically when possible, preferring `class`, `landuse`, `subtype`, Chinese land-use fields, then parsed `source_tags`.
4. If an administrative layer is available, select the requested districts/counties and clip the land-use polygons before plotting or summarizing. Keep the selected boundary layer and selection metadata in the output package.
5. Compute area in a local UTM metric CRS inferred from the data centroid. Do not report final planning areas from EPSG:3857.
6. Preserve both levels of classification:
   - raw class table and raw-class diagnostic map for audit;
   - grouped planning classes for report map and structure charts.
7. Make the raw-to-report transformation explicit. Include the original field value, Chinese label, report group, matching rule, feature count, area, and share in both CSV and a readable mapping figure.
8. Produce a complete package: map(s), structure chart, area ranking chart, raw-to-group mapping figure, grouped/raw CSV tables, selected boundary/plot layers, README, and `artifact_manifest.json`.
9. Run a visual/QC pass: meaningful administrative extent, title hierarchy, district labels, legend, scale bar, north arrow, source note, CRS note, readable labels, consistent colors, no overcrowded pie labels, and no missing output paths.

## Graphic shell and color discipline

Use a white, black, and red narrative shell unless the user supplies another house style:

- white canvas; near-black titles, labels, administrative outlines, axes, scale bar, and north arrow;
- deep red for the study focus, selected boundary, representative locations, comparison annotation, or main planning takeaway;
- pale red only as a low-opacity focus field or highlight, never as a blanket background for every panel;
- solid black connectors for sequence and ordinary relations; dotted red connectors only for comparison, feedback, or cross-scale correspondence.

Do not force categorical land-use classes into indistinguishable red shades. The thematic layer may use muted class colors when categories must remain separable; keep those colors inside the map, legend, and directly linked charts. For binary or ordered intensity data, prefer neutral-to-red ramps. For signed deviations around a meaningful zero, use a restrained colorblind-safe diverging scale and explain its midpoint. The overall page should still read as a black structural skeleton with a red focal argument.

When composing several outputs into one publication figure, use repeated map dimensions, aligned legends and diagnostic strips, and identical sample-thumbnail geometry. Put workflow/provenance on the left or top, the main spatial evidence at the visual center, and representative local crops along the bottom or outer edge.

For reference-layout replication, export additional composite-ready map assets when needed:

- identical pixel dimensions and geographic extent across comparison maps;
- transparent or white background without standalone title, caption, or duplicated legend;
- fixed boundary line weights and one shared legend supplied as a separate asset;
- separate patch, buffer, overlap, cluster, and representative-location layers so the outer compositor can control emphasis;
- small locator maps and local crops at the exact aspect ratios required by the target slots.

Never resize comparison maps independently to fill their boxes. Letterbox or revise the crop while preserving common extent and scale.

## Basemap

For report maps, use the optional `carto-light-nolabels` mode by default. It adds a pale CartoDB Positron No Labels tile layer beneath the land-use polygons and translucent administrative boundary fill. The basemap is positional context only: it does not enter clipping, area calculation, classification, or chart statistics. Keep the default opacity around `0.38` so the thematic colors remain primary.

The renderer fetches tiles directly with the existing Python GIS/runtime dependencies and reprojects them to the local map CRS. If tile access or optional raster dependencies fail, the renderer must still finish the package, record `fallback_no_basemap` in `artifact_manifest.json`, and explain the reason. Use `--basemap none` when an offline or source-free figure is required. The manifest and README record the provider, tile URL, opacity, zoom, tile counts, and per-map render status.

## Outputs

Expected files:

- `maps/01_landuse_current_map.png`
- `maps/02_landuse_raw_class_map.png`
- `charts/03_landuse_structure_donut.png`
- `charts/04_landuse_class_area_bar.png`
- `charts/05_landuse_figure_group.png`
- `charts/06_raw_to_report_group_mapping.png`
- `tables/landuse_group_summary.csv`
- `tables/landuse_class_summary.csv`
- `tables/landuse_class_to_group_mapping.csv`
- `tables/landuse_plot_layer.gpkg`
- `tables/selected_admin_boundary.gpkg` when administrative selection is used
- `artifact_manifest.json`
- `README.md`

## Classification

Use the defaults in `references/classification.md`. The source `class`/`landuse` value is not silently replaced: preserve it as the raw class, apply the transparent keyword mapping, and record the matched keyword in `mapping_rule`. Override the mapping only when the dataset has a known local planning codebook or the user supplies one.

If raw classes exceed about 8 categories, use grouped classes for the formal map and chart, and keep raw classes in the diagnostic map/table.

## Claim Boundary

These outputs support descriptive claims about mapped land-use composition and distribution. They do not support causal, policy-effect, compliance, people-specific, or temporal-change claims without additional verified evidence.
