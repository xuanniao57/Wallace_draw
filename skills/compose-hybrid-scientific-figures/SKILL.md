---
name: compose-hybrid-scientific-figures
description: Compose, revise, or layout-match publication-ready scientific framework and workflow figures from GIS maps, charts, model diagnostics, imagery, and vector explanation. Use for evidence-led overview figures, editable multi-panel compositions, or exact reference-layout replication with substitute local data.
---

# Compose Hybrid Scientific Figures

Build a visual scientific argument, not a decorated flowchart. Let real analytical evidence explain the research; use vector layout only to organize it.

## Core contract

- Preserve scientific meaning, provenance, units, scales, and uncertainty.
- Prefer real maps, charts, model diagnostics, source imagery, equations, and implemented interface states over prose.
- Use AI illustration only for abstract constructs without a direct empirical representation. Never replace measured evidence with invented imagery.
- Use Draw.io, Figma, or SVG for outer panels, short step titles, arrows, icons, branch/merge logic, and alignment.
- Keep text directly on the canvas when possible. Avoid nested cards, pills, shaded explanation boxes, and micro-text.
- For an approved black--red project or when a single focal selection carries the thesis, use a white canvas, near-black typography and structural lines, one deep red accent, and pale red tints for focal regions. Red carries the scientific thesis or selected comparison; it is not a general decoration color.
- Keep auxiliary hues local to empirical graphics that need categorical, divergent, or image-native color. Mute them, explain them in a legend, and prevent them from competing with the surrounding narrative layer.
- Deliver an editable master plus publication exports. Do not flatten the entire figure into a screenshot.

## Workflow

### 1. Fix the visual argument

Write one sentence that states what the reader should understand after seeing the figure. For an original framework, read [original-framework.md](references/original-framework.md). Choose a layout from the actual dependencies, decisions or spatial relationships. For a purely quantitative results plate, use design-spatial-data-figures and start with a plot of the observations.

Choose the final use before composing:

- single-column manuscript;
- double-column/full-page manuscript;
- 16:9 presentation;
- interactive frontend overview.

### 2. Inventory evidence

Inspect every candidate asset before drawing. Record its source, role, crop, resolution, and whether it is empirical, explanatory, or interface evidence.

Run `scripts/inventory_figure_assets.py <asset-directory> --out <inventory.json>` when a directory contains many candidate files. Read `references/asset-routing.md` to decide which medium should carry each scientific statement.

Do not compose until the following are known:

- research object and study context;
- input data and constructs;
- analytical transformation;
- validation or comparison;
- final finding, decision, or bounded claim.

### 3. Build an evidence-led storyboard

For new or substantially redesigned conceptual frameworks and mixed method illustrations, generate an image-model mockup before vector assembly. Use the available built-in image-generation tool; retain its prompt and output. Inspect the mockup, then identify which illustrations to crop, which elements to rebuild as editable vectors, and which evidence slots require real maps, code, tables or charts. Do not replace this step with a text-only storyboard unless the user asks to skip image generation. Small label corrections to an approved figure do not need a new mockup.

Make relationships visible through concrete objects and actions. For review/provenance figures, show selected tree nodes, attached evidence, highlighted discrepancies and review records connected to their targets. Do not turn the final panel into paragraph boxes. Generated analytical plots and interface states are layout placeholders, never empirical evidence; replace them with sourced material during assembly.

Give each visual a short title and a specific object to follow. Draw only the real incoming, outgoing or feedback relations; sources, endpoints, branches and merges have different degrees. When two results are compared directly, aligned positions can carry the relationship without arrows.

Read `references/composition-grammar.md` for layout, typography, panel, connector, and color rules. Use the pattern that matches the research claim. When the user requests black/red styling or the chosen reference uses this system, also read `references/black-red-evidence-language.md` and adapt its grammar without copying article-specific content.

When the user asks to reproduce a reference figure's layout closely, switch to **reference-replication mode** and read `references/reference-layout-replication.md`. For the Ye et al. (2025) heat-patch visual system, also read `references/ye-2025-layout-reconstruction.md`. Match layout, spacing, hierarchy, and geometry; replace scientific content with the user's or clearly labeled local placeholder data.

### 4. Prepare assets in their native tools

- Generate maps in GIS, deck.gl/MapLibre, GeoPandas, or the project's spatial renderer.
- Generate statistical and model figures from the underlying data in a notebook or declared chart grammar.
- Render formulas as vector math when possible.
- Crop software screenshots to the exact state that supports the argument.
- Generate icons or small illustrations only after empirical assets and available whitespace are known.
- Reuse suitable human/Agent illustrations by cropping them from a user-approved generated reference and embedding them as image assets. Do not replace a good illustration with crude vector primitives merely to make every element vector. Record the original image and crop bounds; keep outer text, connectors and panels editable. These assets are conceptual, never empirical evidence.
- For an approved mockup-to-vector conversion, explicitly inventory the small illustrations the user values (for example human and Agent avatars). Keep them as separate embedded assets in the editable master; do not silently drop them during simplification. A hybrid vector figure may contain raster illustrations. Check those assets against the approved mockup at final-size QA, including crop cleanliness and legibility. Crop only the conceptual illustration, not generated numerical results or a fabricated interface state; use real outputs for those.
- When showing a research tree, preserve visible parent--child edges and branch points; a crop containing only sibling cards does not communicate a tree. Translate display text separately from the source state, label translated/replayed views, and retain original identifiers, statuses and artifact bindings.

Retain the original source or script for every empirical image. Do not redraw a real result as a decorative placeholder.

### 5. Compose the editable master

Set the relative sizes and reading order of the main objects first. Use a frame only where grouping would otherwise be ambiguous. Place evidence and direct labels, then connect the actual transformations and decisions.

If a live Draw.io workflow is available, also use the `recreate-scientific-figure-in-drawio` skill and construct editable geometry on the visible canvas. Otherwise compose an editable `.drawio`, SVG, or Figma master while preserving text and connectors as vector elements.

Route arrows through whitespace or gutters. Pin connector entry and exit points. Use curved connectors only when they clarify a branch, return, or merge; never use them to hide poor alignment.

For a rapid layout-first scaffold, run:

```powershell
python "<skill_dir>\scripts\scaffold_reference_layout.py" --preset cluster-evidence --out "<output.svg>"
```

Available presets are `graphical-abstract`, `workflow`, `cluster-evidence`, and `conceptual-synthesis`. Use repeated `--asset slot=path` arguments to replace placeholders while preserving the measured geometry. Treat the scaffold as an editable starting point, not as scientific evidence.

### 6. Reduce before decorating

Perform a deletion pass:

- remove any sentence already expressed by a map, chart, formula, or icon;
- remove repeated legends and repeated method names;
- remove boxes that serve only as backgrounds;
- replace paragraph callouts with a label of one to six words;
- enlarge the remaining scientific evidence.

The result should remain understandable without grey micro-annotations.

### 7. Validate at delivery size

Read and apply `references/publication-qa.md`. Export a review PNG at approximately 2000--3000 px width and inspect it both full-size and at the manuscript's actual display width.

Require:

- readable step titles and major labels;
- undistorted maps and charts;
- visible units, legends, scale bars, and uncertainty where scientifically necessary;
- unambiguous arrow direction and panel order;
- no overlap, clipping, tiny text, or unexplained decorative imagery;
- an editable master plus PNG and SVG/PDF exports when supported.

## Delivery

Return:

- editable master (`.drawio`, Figma file, or structured SVG);
- review PNG;
- publication SVG or PDF;
- asset inventory or source manifest when the figure embeds empirical results;
- a short note identifying intentionally rasterized components.

Keep project-specific scripts, data paths, and case details outside this global skill. Store those in the project and cite this skill as the governing workflow.
