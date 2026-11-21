# Ye et al. (2025) layout reconstruction

Benchmark article: Jiaxing Ye, Xiong Yao, Xing Shi, and Feng Yang, “Global vs. local heat patches: Toward a more comprehensive perspective on managing urban overheating—A Shanghai case study,” *Sustainable Cities and Society* 129 (2025), 106503. DOI: `10.1016/j.scs.2025.106503`.

Use this as an optional layout preset. Reproduce spatial organization and visual grammar, not the article's data, numerical results, maps, satellite crops, icons, or wording.

## Source diagnosis

The frequently shared tall screenshot is a montage, not one article figure. It combines the article header with Fig. 3 (workflow), Fig. 12 (conceptual synthesis), Fig. 11 (LHP evidence plate), and Fig. 10 (GHP evidence plate). Reconstruct these source figures separately before assembling any montage.

The full Elsevier XML confirms this analytical production pipeline:

- **GIS/raster analysis:** four Landsat 8 OLI Level 2 surface-temperature scenes, 1.5×IQR outlier treatment, summer averaging, and 100 m resampling in ArcGIS Pro and ENVI 5.6.2;
- **LCZ classification:** WUDAPT Random Forest classification, retaining 16 LCZ types on the same 100 m grid;
- **heat-patch extraction:** GHP thresholding at LST >50 °C; LHP extraction from Gaussian-smoothed 2 °C contours through a Local Contour Tree implemented with Python `networkx`, followed by a 45.5 °C minimum filter;
- **adjacent context:** 300 m and 600 m patch buffers, with 600 m used for the main ranking, classification, and clustering figures;
- **Python modeling:** `xgboost` and `shap`, using patch-level LCZ proportions, 70/30 train-test splitting, grid search, 10-fold cross-validation, beeswarm plots, and force plots;
- **clustering:** K-means on mean patch-level SHAP vectors, k=4 chosen with the elbow method and Davies–Bouldin index, with the nearest-to-centroid patch used as the representative sample;
- **vector composition:** workflow frames, conceptual curves, node diagrams, arrows, rounded masks, striped fields, legends, and final cross-panel alignment;
- **source imagery:** satellite or remote-sensing crops for representative samples.

ArcGIS Pro, ENVI 5.6.2, WUDAPT, `networkx`, `xgboost`, and `shap` are author-confirmed. The exact final compositor and plotting backend are not stated; Illustrator/PowerPoint/Draw.io/SVG and Matplotlib remain production-route inferences.

## Shared visual system

- Primary structure: dark navy-black around `#17264F` to `#111111`.
- Thesis accent: rose/deep pink around `#CC3E69` to `#E590AA`.
- Scope fields: very pale pink with low opacity.
- Global/local comparison: rose for GHPs and teal for LHPs.
- Auxiliary data color: LCZ categorical colors remain inside maps and legends.
- Canvas: pure white, with large unframed gutters.
- Type: bold sans-serif for titles; regular sans-serif for explanations.
- Repeated motif: rounded rectangles for process, circles for integration and samples, dashed boundaries for analytical scope.

## Per-figure production audit

### Graphical abstract — 2103 × 886, aspect 2.374

**Observed layout.** A horizontal pipeline with four macro-zones: heat-patch distinction, buffer/LCZ operations, paired mapping, and ranking/clustering. A pale rose ribbon crosses the middle and visually binds all stages. Grey rounded cards float above it.

**Likely production.** Export simplified GHP/LHP maps and cluster maps from GIS; export a cropped SHAP summary from Python; draw buffer icons and the outer composition in a vector editor.

**Reconstruction.** Use a 12-column canvas. Allocate approximately 14%, 22%, 41%, and 17% to the four zones, leaving narrow gutters. Preserve two repeated horizontal lanes for global and local analysis. Use one large red arrow between mapping and outcomes.

### Fig. 1 — 3000 × 632, aspect 4.747

**Observed layout.** Two conceptual temperature profiles on one very wide canvas. Black Bézier ridgelines receive a vertical white-to-rose gradient fill and yellow peak edge. Dashed rectangles identify global-threshold versus local-relative peaks.

**Likely production.** SVG/Illustrator path drawing or Matplotlib curves followed by vector annotation.

**Reconstruction.** Generate two smooth multi-peak curves, close each to a baseline, apply a vertical gradient, and overlay dashed selection rectangles. Keep labels outside the curve whenever possible. The source depends on shape comparison, not axes.

### Fig. 2 — 3500 × 1663, aspect 2.105

**Observed layout.** A two-map locator plate: China on the left, Shanghai on the right. Both maps have coordinate ticks; the Shanghai panel overlays a pale basemap, urban-space fill, river, administrative boundaries, urban core, and new-town boundaries.

**Likely production.** GIS layout with two map frames, scale bars, north arrows, and a manually positioned legend.

**Reconstruction.** Preserve the left/right width ratio near 42:58. Keep both map frames equal in height. Use grey national context, red study-location mark, pale basemap, and black hierarchical boundaries.

### Fig. 3 — 3333 × 4174, aspect 0.798

**Observed layout.** A tall workflow with a narrow numbered spine on the right. Three broad rounded containers hold data/identification, modeling/ranking, and clustering. Two translucent rose lanes run vertically through the central analysis. Blue blocks represent LCZ/context; rose blocks represent temperature/heat-patch operations. Pale red feedback connectors return from later analyses to earlier classification steps.

**Likely production.** Outer geometry in Illustrator/PowerPoint/Draw.io; small maps and charts exported from GIS/Python and clipped into rectangles or circles.

**Reconstruction.** Use a portrait canvas. Reserve about 84% for the workflow and 12% for the numbered spine. First build the three major rounded rectangles, then the two translucent vertical lanes, then dashed subgroups, then circular evidence windows. The bottom comparison loop must be centered on the two lanes, not on the whole canvas.

### Fig. 4 — 1667 × 3618, aspect 0.461

**Observed layout.** A vertical algorithm explainer. The upper panel shows three node-simplification scenarios; the lower panel pairs initial and simplified tree structures with corresponding filled-contour diagrams.

**Likely production.** Vector nodes and connectors plus manually drawn or programmatically generated contours.

**Reconstruction.** Use navy filled nodes, rose outlined successor nodes, grey transformation arrows, and rounded outer frames. Maintain exact before/after columns and align each tree with its contour field beneath it.

### Fig. 5 — 3333 × 2275, aspect 1.465

**Observed layout.** Two dominant maps: continuous LST raster and categorical LCZ map. Three threshold-map thumbnails sit under the LST panel, while a large categorical legend occupies the lower-right quadrant.

**Likely production.** Raster and vector GIS layers, with final assembly in a GIS layout or vector editor.

**Reconstruction.** Keep the two main maps equal in visual area and share identical outlines/boundaries. Use a vertical temperature colorbar near the top gap. Place the three threshold thumbnails on a common baseline and equal size.

### Fig. 6 — 3333 × 1098, aspect 3.036

**Observed layout.** Three equal maps for GHPs, LHPs, and overlap. Rose and teal encode the two patch families; the third panel overlays both.

**Likely production.** GIS spatial overlay with common extent and transparent layer export.

**Reconstruction.** Lock map extent, aspect ratio, boundary hierarchy, and label baselines across all panels. The overlap panel must be a literal overlay of the first two outputs, not a separately generalized map.

### Fig. 7 — 3333 × 1396, aspect 2.388

**Observed layout.** Two equal dominant-LCZ maps plus a right-side legend. Large areas of white space make the categorical patches readable.

**Likely production.** GIS dissolve/classification by dominant LCZ type.

**Reconstruction.** Use the same category palette and map extent in both panels. Reserve a separate legend column rather than shrinking the maps to place legends inside them.

### Fig. 8 — 3333 × 3656, aspect 0.912

**Observed layout.** A 2 × 2 matrix of SHAP beeswarms. Pale rose horizontal bars encode mean absolute SHAP behind the point distributions; blue-to-pink point color encodes feature value. Each panel has an upper bar scale and lower signed SHAP axis.

**Likely production.** Python SHAP plus Matplotlib customization. The background importance bars likely require a second aligned x-axis or custom artists.

**Reconstruction.** Build each panel from one common function. Sort features independently if required, but keep plot width, row height, zero line, title offset, and colorbar dimensions identical. Draw bars first, beeswarm second, zero line third, labels last.

### Fig. 9 — 3333 × 3980, aspect 0.837

**Observed layout.** Mirrored GHP/LHP columns under navy header bands. Six repeated rows each pair a small locator map with a grouped bar chart. A schematic concentric-circle legend anchors the bottom.

**Likely production.** Matplotlib GridSpec or similar repeated programmatic layout, possibly assembled afterward in a vector editor.

**Reconstruction.** Use a strict grid: two super-columns; within each, a narrow map column and a wider chart column. Fix identical row heights. Align all axes and category labels. Build the bottom legend as its own full-width row.

### Fig. 10 — 3333 × 3021, aspect 1.103

**Observed layout.** GHP cluster evidence plate. Panel (a), a cluster map, fills the upper-left inside a clipped pale-pink striped rounded rectangle. Panel (b) stacks four SHAP force/decision strips in the upper-right. Panel (c) spans the bottom with four equal satellite-image cards; each card has a small LCZ-composition patch above it and a circular sample label.

**Likely production.** Cluster map from GIS/Python; SHAP force plots from Python; satellite crops from GIS or remote-sensing imagery; final assembly and rounded striped mask in Illustrator/PowerPoint.

**Reconstruction.** Use a near-square canvas. Allocate roughly 50% width to the map and 50% to diagnostics. Reserve the bottom 24–28% for four equal sample cards. Align each sample marker on the map with its corresponding diagnostic strip and bottom card by label, not by color alone.

### Fig. 11 — 3333 × 3054, aspect 1.091

**Observed layout.** LHP counterpart to Fig. 10 with the same geometry, four cluster colors, four force plots, and four satellite samples.

**Likely production.** Same pipeline and template as Fig. 10.

**Reconstruction.** Treat Fig. 10 and Fig. 11 as a locked template pair. Do not independently resize or move panels. This repeated geometry is what makes global/local comparison credible.

### Fig. 12 — 3333 × 3346, aspect 0.996

**Observed layout.** Near-square conceptual synthesis. The upper center contains HHR factors feeding a triangular GHP/LHP/HGZ construct. A large pale-rose sector occupies the middle. Circular evidence modules orbit its perimeter: GHP fragmentation, LHP network disruption, temporal variation, patch coverage/intensity/pattern, cluster typology, and polycentric structure. Red headings and black one-line explanations sit outside the geometry.

**Likely production.** Vector-editor composition using circles, arcs, dotted strokes, icons, pixel motifs, and translucent rose shapes.

**Reconstruction.** Establish the large red sector and central axis first. Place the upper triangle, left pair, right temporal stack, and bottom pair on a common circular rhythm. Use navy for risk-assessment structure and rose for the heat-governance thesis. Keep narrative callouts outside the central field.

### Fig. 13 — 3333 × 2861, aspect 1.165

**Observed layout.** Two dashed rounded row containers. Each row shows a source heat-patch map, a centered “expand 600 m” arrow, and an adjacent-buffer map. The categorical legend occupies a narrow right column.

**Likely production.** GIS buffer operation and LCZ intersection, followed by vector assembly.

**Reconstruction.** Lock two identical row templates. Use equal source and result map slots, one centered operation arrow, and a shared legend. Rounded dashed row borders indicate analytical scope, not decoration.

## Four reusable presets

### `graphical-abstract`

Horizontal evidence pipeline: global/local lanes → buffer/composition → paired maps → ranking/clustering.

### `workflow`

Portrait numbered pipeline: inputs → identification → modeling/ranking → clustering, with two translucent comparison lanes.

### `cluster-evidence`

Near-square evidence plate: cluster map + four diagnostic strips + four representative imagery cards.

### `conceptual-synthesis`

Near-square radial synthesis: upper assessment triangle + central scope field + orbiting evidence modules + external narrative callouts.

Use `scripts/scaffold_reference_layout.py` to generate editable SVG geometry for these presets. Replace placeholder slots with regenerated local evidence, then perform overlay QA against the chosen source figure.
