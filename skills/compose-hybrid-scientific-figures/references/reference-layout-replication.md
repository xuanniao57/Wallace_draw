# Reference-layout replication

Use this mode when the user values faithful composition more than reuse of the reference's underlying data. Reproduce the visual grammar and geometry; do not present substituted data as the source article's result.

## 1. Acquire source evidence

Obtain the highest-resolution lawful source available: publisher figure image, author manuscript, PDF page render, or user-provided image. Record the source URL, DOI or citation, pixel dimensions, access status, and whether the asset is a graphical abstract, article figure, or a montage assembled outside the paper.

Do not infer a single canvas from a screenshot until checking whether it contains several independent source figures. Split a montage into its original figures before measuring layout.

## 2. Inventory every figure

For each source figure, record:

- canvas width, height, and aspect ratio;
- panel labels and reading order;
- normalized bounds `(x / width, y / height, w / width, h / height)` for every macro-panel;
- grid, gutter, outer margin, repeated row/column dimensions, and alignment anchors;
- type hierarchy, line weights, corner radii, dash patterns, arrowheads, and color roles;
- which components are generated from data and which are manually composed;
- the likely native producer for each component, stated as an inference unless confirmed by the authors.

Use a table or JSON layout manifest. Keep observations separate from inferred production tools.

## 3. Reconstruct in layers

Build in this order:

1. exact canvas and outer margins;
2. macro-panel rectangles, circles, ribbons, or scope fields;
3. repeated grid and alignment anchors;
4. placeholder boxes named by scientific role;
5. titles, labels, legends, and panel letters;
6. primary connectors, then comparison or feedback connectors;
7. local maps, charts, images, and icons;
8. final accent color, masks, clipped patterns, and minor decoration.

Do not begin with final maps or charts. A reference match is first a geometry problem.

## 4. Substitute data honestly

When original data are unavailable:

- preserve slot aspect ratio, map extent shape, chart family, number of rows, legend position, and visual density;
- use local or synthetic data that exercise the same layout constraints;
- label the output as a layout reconstruction with substitute data;
- do not copy numerical values, article findings, satellite crops, or branded assets into a new scientific claim;
- regenerate maps and charts in their native tools, then place them as evidence assets.

For exact layout testing, placeholder content should resemble the source's visual mass: sparse map for sparse map, dense beeswarm for dense beeswarm, four diagnostic strips for four diagnostic strips.

## 5. Match typography and geometry

- Preserve the source aspect ratio exactly unless the user requests a new format.
- Keep macro-panel bounds within about 1% of canvas width/height and repeated slots within about 0.5% when the reference is high resolution.
- Match type hierarchy and relative size before matching the exact font. Use Arial/Helvetica when the original family is unknown.
- Match visual weight: border thickness, dash length, arrowhead size, and corner radius as proportions of canvas width.
- Use clipping paths for rounded striped fields, circular thumbnails, and map masks. Do not fake them with raster screenshots if editable SVG geometry is practical.

## 6. Overlay QA

Export the reconstruction at the reference pixel size. Compare three views:

1. side-by-side at equal size;
2. 50% opacity overlay with the reference;
3. greyscale thumbnail.

Inspect in this order:

- canvas ratio and crop;
- macro-panel positions and dimensions;
- alignment baselines and gutters;
- center of visual mass;
- type hierarchy and line weight;
- connector topology;
- color distribution;
- local content detail.

Fix geometry before style. Do not hide misalignment with shadows, gradients, or extra labels.

## 7. Deliverables

Return the editable master, a review PNG at the reference dimensions, and a layout manifest containing source citation, canvas, normalized bounds, asset-slot mapping, and substituted-data disclosure. Keep the original source image separate from the deliverable.
