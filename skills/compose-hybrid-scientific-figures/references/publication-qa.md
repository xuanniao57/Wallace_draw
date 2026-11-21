# Publication QA

## Scientific integrity

- Confirm that every empirical image comes from the stated data, script, model, or interface state.
- Preserve axes, units, legends, uncertainty, sample definitions, and comparison baselines needed for interpretation.
- Confirm that maps retain correct aspect ratio, projection context, scale indication, colorbar, and spatial unit.
- Label conceptual or AI-generated illustrations so they cannot be mistaken for observations.
- Do not imply causality, coverage, accuracy, or model validity beyond the underlying analysis.

## Visual inspection

- Read the figure at the target manuscript width, not only when zoomed in.
- Check that panel sequence is obvious within three seconds.
- Check that step titles, branch/merge points, and main result are readable.
- Check image aspect ratios, sharpness, crop boundaries, whitespace, and alignment.
- Check that arrows connect exact targets and do not cover evidence.
- Remove repeated legends, decorative frames, tiny notes, and low-contrast text.
- In a black--red figure, confirm that the black skeleton remains readable without color and that red has one stable thesis-bearing role.
- Confirm that pale red fields do not reduce text contrast and that auxiliary hues remain confined to empirical insets with legends.
- Inspect a greyscale preview; grouping, sequence, and selected states must not depend on hue alone.

## Reference-layout QA

When reproducing a supplied figure layout:

- verify the source is one figure rather than a montage of several figures;
- export at the source pixel dimensions and preserve its exact aspect ratio;
- compare macro-panel bounds, outer margins, repeated row/column sizes, and alignment anchors before comparing colors;
- inspect a 50% opacity overlay and fix any panel edge displaced by more than about 1% of canvas width or height;
- confirm the number, order, and aspect ratio of substitute maps, charts, and imagery slots match the reference;
- disclose that local or synthetic data replaced the source article's evidence;
- keep the source image separate from the editable master and final deliverable.

## Export

- Retain an editable master.
- Prefer SVG or PDF for vector text, arrows, icons, and formulas.
- Use PNG for raster-heavy composites and screenshots; export at 2x--3x the final display resolution.
- Preserve embedded source metadata where the format supports it.
- Name exports deterministically, for example `figure_overview_v03.drawio`, `.svg`, and `.png`.

## Delivery check

- Editable source opens successfully.
- SVG/PDF renders without missing fonts or clipped elements.
- PNG matches the master.
- Caption terminology matches the manuscript.
- The project contains the scripts or source files required to regenerate empirical subfigures.
