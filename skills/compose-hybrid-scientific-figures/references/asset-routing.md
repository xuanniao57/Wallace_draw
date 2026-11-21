# Asset and tool routing

Choose the medium that preserves the strongest evidence.

| Scientific content | Preferred producer | Role in the composite |
|---|---|---|
| Study area, spatial distribution, coefficients, residuals | GIS, GeoPandas, deck.gl/MapLibre, spatial frontend | Empirical spatial evidence |
| Distributions, correlations, uncertainty, model comparison | Notebook, Vega-Lite/Altair, statistical plotting library | Empirical quantitative evidence |
| Street view, satellite image, field photo, sensor view | Original imagery or reproducible crop | Observational context |
| Model architecture or data transformation | Draw.io/SVG primitives plus compact formula | Method explanation |
| Abstract construct with no direct measurement | Simple icon set or restrained AI illustration | Supporting explanation only |
| Branch, merge, feedback, checkpoint, provenance | Draw.io/Figma/SVG connector geometry | Process logic |
| Software interaction or Agent state | Tightly cropped real screenshot | Interface evidence |

## Selection rules

1. If an empirical result exists, use it instead of an illustrative substitute.
2. If a relation is quantitative, encode it as position, length, color, or shape in a chart rather than prose.
3. If geography changes the interpretation, show a map rather than a non-spatial summary alone.
4. If a screenshot contains many controls, crop to the decision state and enlarge the relevant labels.
5. If a construct cannot be observed directly, use one small illustration and label it as conceptual.
6. If an image cannot be reproduced or shared, use an explicit placeholder in the editable master and document the required source; do not fabricate evidence.

## Evidence manifest fields

Record at least:

- `asset_id`
- `source_file`
- `producer`
- `scientific_role`
- `empirical_or_conceptual`
- `crop_or_filter`
- `units_or_scale`
- `reproduction_source`
- `publication_permission`

Keep the manifest with the project, not inside the global skill.
