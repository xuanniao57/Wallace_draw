# Composition grammar

## Visual hierarchy

Use a white or near-white canvas. Build hierarchy in this order:

1. outer step or phase;
2. dominant evidence image;
3. short label or formula;
4. connector;
5. optional supporting icon.

The dominant evidence should occupy more area than explanatory text. A reader should identify the research object, method, and outcome before reading the caption.

## Panels

- Group only stages the reader needs to distinguish; a single transformation can occupy a single field.
- Place the step title directly at the upper-left of each panel.
- Use one thin neutral border or whitespace separation; do not place every internal item in another card.
- Align image edges and baselines across adjacent panels.
- Keep comparable charts at identical plot dimensions and scales.

## Text

- Use a neutral sans-serif family such as Arial, Helvetica, Source Sans, or the manuscript's approved font.
- Use sentence case for descriptions and consistent title case for step headings.
- Keep internal labels short; move detailed explanation to the caption.
- Avoid light-grey explanatory sentences, rotated labels, and text embedded at unreadable raster resolution.
- Set the figure at its actual manuscript width. Follow the project or venue typography; increase small labels and remove detail until the printed figure is readable.

## Connectors

- Use straight or orthogonal arrows for ordered stages.
- Route arrows through gutters, not across maps or charts.
- Use a restrained curve for a meaningful branch, feedback loop, or merge.
- Show branch alternatives in parallel and rejoin them at a visible comparison or decision node.
- Avoid crossing connectors. If two edges must cross, revise the layout before adding bridges or decoration.

## Color

- For the black--red house style, use a white canvas, near-black text and one red family for emphasis. A practical starting set is `#111111` (ink), `#B5122B` (deep red), `#D92E4E` (active red), `#F8DDE3` (pale red field), `#D9D9D9` (neutral rule), and `#FFFFFF` (canvas).
- Use black for titles, body labels, axes, ordinary arrows, boundaries, and the main reading order. Use red for the paper's thesis: focal nodes, selected states, comparison bridges, heat/intensity, or the final decision layer. Use pale red as an area field, not as a default card background.
- As a heuristic, let white/neutral space dominate, keep black as the structural layer, and limit saturated red to a small fraction of the canvas. If everything is red, nothing is focal.
- Reserve auxiliary color for information that cannot be encoded honestly in black/red alone: multi-class maps, signed diverging values, categorical clusters, or source imagery. Keep those colors muted and inside the empirical inset; retain black/red for the surrounding narrative shell.
- Reuse every semantic color consistently across panels. Never assign red to unrelated meanings in the same figure.
- Do not use rainbow palettes, gradients for decoration, shadows, bevels, or 3D chart effects.
- Verify that hierarchy and grouping still work in greyscale; color should reinforce structure rather than repair it.

## Black--red connector grammar

- Solid black arrow: primary sequence or direct dependency.
- Thin black rule: grouping, alignment, or measurement reference.
- Solid red arrow: thesis-bearing transition, selection, or synthesis.
- Dotted red curve: long-range comparison, feedback, or global--local correspondence.
- Pale red halo or field: shared analytical scope around several nodes.

Do not mix these meanings casually. Prefer rewriting the layout over adding more line styles.

## Reusable patterns

### Linear evidence pipeline

`data/context -> analysis -> validation -> spatial/result interpretation`

Use when the scientific procedure is mostly sequential.

### Multimodal convergence

Place two or three evidence streams vertically, merge them into a shared construct or model, then show one validated result.

### Branch and compare

Show alternative datasets, scales, models, or hypotheses in parallel. Join them at a comparison node whose evidence is visible. Use this for methodological choices, not decoration.

### Human--AI research loop

Place human dialogue/checkpoints as a control surface beside or above the executable workflow. Show only observable decisions and artifacts; do not expose fabricated private chain-of-thought.

### Spatial validation loop

Place the global model/result beside a residual or local map, then route failure or sensitivity back to method selection. Make the changed scale or parameter explicit.

## Cities-style cleanliness test

Before export, ask:

- Could a real image, map, chart, icon, or formula replace this text?
- Is this border necessary for grouping, or is it visual clutter?
- Does each panel contain one dominant scientific idea?
- Are arrows explaining causality or workflow, or merely connecting boxes?
- Would the figure still work if every grey explanatory sentence were deleted?

If the last answer is no, improve the evidence and visual hierarchy rather than adding more prose.
