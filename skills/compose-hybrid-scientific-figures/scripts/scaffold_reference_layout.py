#!/usr/bin/env python3
"""Create editable SVG scaffolds for evidence-led scientific figure layouts.

The presets encode panel geometry only. Placeholder labels and optional local
assets must not be interpreted as scientific results.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr


INK = "#17264F"
BLACK = "#111111"
RED = "#CC3E69"
ACTIVE_RED = "#E6557E"
PALE_RED = "#F6DCE4"
LIGHT_RED = "#E9A1B5"
TEAL = "#35B7B1"
GREY = "#E7E7E7"
MID_GREY = "#A9A9A9"
WHITE = "#FFFFFF"


class Figure:
    def __init__(self, width: int, height: int, preset: str, assets: dict[str, Path]):
        self.width = width
        self.height = height
        self.preset = preset
        self.assets = assets
        self.body: list[str] = []
        self.slots: list[dict[str, object]] = []

    def add(self, svg: str) -> None:
        self.body.append(svg)

    def rect(self, x, y, w, h, *, fill=WHITE, stroke="none", sw=0, rx=0, dash=None, opacity=1.0):
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{sw}"{dash_attr}/>'
        )

    def circle(self, cx, cy, r, *, fill=WHITE, stroke=INK, sw=3, dash=None, opacity=1.0):
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" fill-opacity="{opacity}" '
            f'stroke="{stroke}" stroke-width="{sw}"{dash_attr}/>'
        )

    def line(self, x1, y1, x2, y2, *, stroke=INK, sw=4, dash=None, marker=True):
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        marker_attr = ' marker-end="url(#arrow-ink)"' if marker and stroke == INK else ''
        if marker and stroke in {RED, ACTIVE_RED}:
            marker_attr = ' marker-end="url(#arrow-red)"'
        self.add(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{sw}"{dash_attr}{marker_attr}/>'
        )

    def path(self, d, *, fill="none", stroke=INK, sw=4, dash=None, opacity=1.0, marker=False):
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        marker_attr = ''
        if marker:
            marker_attr = ' marker-end="url(#arrow-red)"' if stroke in {RED, ACTIVE_RED} else ' marker-end="url(#arrow-ink)"'
        self.add(
            f'<path d={quoteattr(d)} fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" '
            f'stroke-width="{sw}"{dash_attr}{marker_attr}/>'
        )

    def text(self, x, y, value, *, size=26, weight=400, fill=BLACK, anchor="middle", italic=False):
        style = "italic" if italic else "normal"
        self.add(
            f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Arial, Helvetica, sans-serif" '
            f'font-size="{size}" font-weight="{weight}" font-style="{style}" fill="{fill}">{escape(str(value))}</text>'
        )

    def multiline(self, x, y, lines, *, size=24, weight=400, fill=BLACK, anchor="middle", gap=1.18):
        self.add(
            f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Arial, Helvetica, sans-serif" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}">'
            + "".join(
                f'<tspan x="{x}" dy="{0 if i == 0 else size * gap}">{escape(str(line))}</tspan>'
                for i, line in enumerate(lines)
            )
            + '</text>'
        )

    def slot(self, name, x, y, w, h, *, shape="rect", rx=20, label=None, fit="contain"):
        self.slots.append(
            {
                "name": name,
                "bounds_px": [x, y, w, h],
                "bounds_normalized": [
                    round(x / self.width, 6),
                    round(y / self.height, 6),
                    round(w / self.width, 6),
                    round(h / self.height, 6),
                ],
                "asset": str(self.assets[name]) if name in self.assets else None,
            }
        )
        asset = self.assets.get(name)
        clip_id = f"clip-{escape(name).replace(' ', '-') }"
        if shape == "circle":
            cx, cy, r = x + w / 2, y + h / 2, min(w, h) / 2
            self.add(f'<clipPath id="{clip_id}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>')
        else:
            self.add(f'<clipPath id="{clip_id}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/></clipPath>')

        if asset:
            mime = mimetypes.guess_type(asset.name)[0] or "application/octet-stream"
            data = base64.b64encode(asset.read_bytes()).decode("ascii")
            preserve = "xMidYMid slice" if fit == "cover" else "xMidYMid meet"
            self.add(
                f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="{preserve}" '
                f'clip-path="url(#{clip_id})" href="data:{mime};base64,{data}"/>'
            )
        else:
            if shape == "circle":
                self.circle(x + w / 2, y + h / 2, min(w, h) / 2, fill="#FAFAFA", stroke=MID_GREY, sw=2, dash="10 8")
            else:
                self.rect(x, y, w, h, fill="#FAFAFA", stroke=MID_GREY, sw=2, rx=rx, dash="10 8")
            self.text(x + w / 2, y + h / 2 + 8, label or name, size=min(26, max(14, w / 18)), weight=700, fill="#666666")

    def render(self) -> str:
        defs = f"""
<defs>
  <marker id="arrow-ink" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 Z" fill="{INK}"/></marker>
  <marker id="arrow-red" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 Z" fill="{RED}"/></marker>
  <pattern id="rose-stripes" width="12" height="12" patternUnits="userSpaceOnUse"><rect width="12" height="12" fill="white"/><rect y="0" width="12" height="4" fill="{PALE_RED}"/></pattern>
  <linearGradient id="rose-fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ACTIVE_RED}" stop-opacity="0.56"/><stop offset="1" stop-color="{PALE_RED}" stop-opacity="0.12"/></linearGradient>
</defs>
"""
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}">\n{defs}'
            + "\n".join(self.body)
            + "\n</svg>\n"
        )


def graphical_abstract(assets: dict[str, Path]) -> Figure:
    f = Figure(2103, 886, "graphical-abstract", assets)
    f.rect(0, 0, f.width, f.height, fill=WHITE)
    f.rect(70, 330, 1880, 220, fill=PALE_RED, opacity=0.75)

    f.rect(34, 70, 245, 340, fill=LIGHT_RED, stroke=RED, sw=5, rx=28)
    f.rect(34, 475, 245, 340, fill=LIGHT_RED, stroke=RED, sw=5, rx=28)
    f.multiline(157, 190, ["Global", "Heat", "Patch"], size=31, weight=700)
    f.multiline(157, 595, ["Local", "Heat", "Patch"], size=31, weight=700)

    f.rect(326, 28, 470, 810, fill="#F3F3F3", stroke="#D3D3D3", sw=2, rx=32)
    f.multiline(450, 65, ["adjacent", "buffer zones"], size=25, weight=700)
    f.multiline(660, 65, ["LCZ", "compositions"], size=25, weight=700)
    for row, y in enumerate((140, 510)):
        f.slot(f"buffer_{row+1}", 370, y, 160, 250, label="buffer sequence")
        f.slot(f"composition_{row+1}", 575, y, 170, 250, label="LCZ sequence")

    for row, y in enumerate((70, 460)):
        f.rect(815, y, 720, 340, fill="#F3F3F3", stroke="#D3D3D3", sw=2, rx=34)
        f.text(1175, y + 54, "Mapping", size=35, weight=700)
        f.slot(f"patch_map_{row+1}", 850, y + 75, 310, 210, label="heat-patch map")
        f.slot(f"lcz_map_{row+1}", 1190, y + 75, 310, 210, label="adjacent LCZ map")
    f.line(1560, 440, 1660, 440, stroke=RED, sw=12)

    f.rect(1690, 28, 360, 810, fill="#F3F3F3", stroke="#D3D3D3", sw=2, rx=32)
    f.text(1870, 82, "Ranking", size=35, weight=700)
    f.slot("ranking", 1740, 100, 260, 250, label="SHAP ranking")
    f.text(1870, 415, "Clustering", size=35, weight=700)
    f.slot("cluster_map_1", 1740, 445, 260, 160, label="GHP clusters")
    f.slot("cluster_map_2", 1740, 635, 260, 160, label="LHP clusters")
    return f


def workflow(assets: dict[str, Path]) -> Figure:
    f = Figure(1600, 2000, "workflow", assets)
    f.rect(0, 0, f.width, f.height, fill=WHITE)
    f.rect(470, 120, 250, 1720, fill=PALE_RED, opacity=0.6, rx=100)
    f.rect(800, 120, 250, 1720, fill=PALE_RED, opacity=0.6, rx=100)

    major = [(70, 35, 1250, 900), (70, 960, 1250, 500), (70, 1485, 1250, 380)]
    for x, y, w, h in major:
        f.rect(x, y, w, h, fill=WHITE, stroke=INK, sw=3, rx=24)

    f.rect(150, 70, 270, 95, fill="#AFC2E7", rx=18)
    f.rect(450, 70, 610, 95, fill=LIGHT_RED, rx=18)
    f.multiline(285, 105, ["Local Climate", "Zone"], size=25, weight=700)
    f.text(755, 130, "Land Surface Temperature", size=30, weight=700)

    f.rect(320, 215, 830, 310, fill=WHITE, stroke=INK, sw=2, rx=20, dash="12 8")
    f.slot("global_identification", 380, 255, 330, 220, label="Global Heat Patch")
    f.slot("local_identification", 760, 255, 330, 220, label="Local Heat Patch")

    f.rect(150, 555, 1000, 260, fill=WHITE, stroke=INK, sw=2, rx=20, dash="12 8")
    f.slot("lcz_composition", 190, 590, 260, 185, label="LCZ composition")
    f.slot("buffer_sequence", 500, 590, 610, 185, label="300 m → 600 m buffers")
    f.rect(150, 835, 1000, 95, fill="#AFC2E7", rx=18)
    f.text(650, 895, "Classify heat patches by dominant LCZ type", size=27, weight=600)

    rows = [(995, "RANKING", "model", "ranking"), (1205, "CLASSIFICATION", "classification", "bars")]
    for y, title, left, right in rows:
        f.rect(150, y, 1000, 175, fill=GREY, rx=85)
        f.slot(left, 165, y + 10, 155, 155, shape="circle", label=left)
        f.text(650, y + 55, title, size=28, weight=700)
        f.slot(right, 970, y + 12, 155, 150, shape="circle", label=right)
    f.rect(150, 1525, 1000, 280, fill=GREY, rx=90)
    f.slot("clustering_method", 165, 1580, 155, 155, shape="circle", label="K-Means")
    f.text(650, 1605, "CLUSTERING", size=30, weight=700)
    f.slot("cluster_result", 955, 1560, 170, 170, shape="circle", label="cluster map")

    spine_x = 1420
    f.line(spine_x, 120, spine_x, 1810, stroke=INK, sw=3, marker=False)
    for n, y, label_lines in [(1, 115, ["Data", "Acquisition"]), (2, 570, ["Identification"]), (3, 1080, ["Modeling", "& Ranking"]), (4, 1650, ["Clustering"])]:
        f.circle(spine_x, y + 40, 9, fill=WHITE, stroke=INK, sw=3)
        f.text(1325, y + 55, n, size=62, weight=700, fill=INK)
        f.multiline(1500, y + 30, label_lines, size=20, weight=700, fill=INK)
    f.path("M 430 1880 C 590 2010 870 2010 1040 1880", stroke=RED, sw=5, marker=True)
    f.text(740, 1950, "Comparison", size=26, weight=700, fill=RED)
    return f


def cluster_evidence(assets: dict[str, Path]) -> Figure:
    f = Figure(1600, 1450, "cluster-evidence", assets)
    f.rect(0, 0, f.width, f.height, fill=WHITE)
    f.rect(25, 25, 760, 1010, fill="url(#rose-stripes)", rx=70)
    f.text(405, 80, "(a)", size=30, weight=700)
    f.slot("cluster_map", 80, 110, 650, 760, label="cluster map")
    f.rect(80, 885, 650, 110, fill=WHITE, stroke="none", rx=10, opacity=0.9)
    f.text(405, 950, "cluster legend and representative samples", size=22, weight=600)

    f.text(1190, 80, "(b)", size=30, weight=700)
    for i, y in enumerate((105, 310, 515, 720), 1):
        f.slot(f"diagnostic_{i}", 840, y, 710, 155, label=f"SHAP diagnostic {i}")

    f.text(800, 1100, "(c)", size=30, weight=700)
    card_w = 355
    for i in range(4):
        x = 45 + i * 390
        f.slot(f"composition_patch_{i+1}", x + 125, 1115, 105, 80, label=f"LCZ {i+1}")
        f.slot(f"sample_image_{i+1}", x, 1210, card_w, 190, label=f"sample s{i+1}", fit="cover")
        f.circle(x + 22, 1228, 28, fill=WHITE, stroke=LIGHT_RED, sw=5)
        f.text(x + 22, 1237, f"s{i+1}", size=21, weight=700)
    f.line(1270, 1415, 1550, 1415, stroke=BLACK, sw=5, marker=False)
    f.text(1410, 1440, "scale", size=18, weight=400)
    return f


def conceptual_synthesis(assets: dict[str, Path]) -> Figure:
    f = Figure(1600, 1600, "conceptual-synthesis", assets)
    f.rect(0, 0, f.width, f.height, fill=WHITE)
    f.path("M 480 620 C 510 410 910 350 1040 620 L 1250 1280 C 1030 1510 500 1510 290 1280 Z", fill="url(#rose-fade)", stroke=RED, sw=6, dash="16 10", opacity=0.95)

    f.rect(430, 40, 570, 570, fill=WHITE, stroke=BLACK, sw=3, rx=40, dash="12 8")
    for x, y, label in [(555, 170, "Exposure"), (715, 100, "Sensitivity"), (875, 170, "Adaptive\nCapacity")]:
        f.slot(f"hhr_{label.split()[0].lower()}", x - 60, y - 60, 120, 120, shape="circle", label=label)
    f.text(715, 275, "HHR assessment", size=30, weight=700)
    f.slot("hgz", 625, 330, 180, 180, shape="circle", label="HGZs")
    f.slot("ghp", 500, 470, 180, 180, shape="circle", label="GHPs")
    f.slot("lhp", 750, 470, 180, 180, shape="circle", label="LHPs")
    f.text(715, 575, "+", size=58, weight=700, fill=RED)

    f.multiline(180, 480, ["Two", "perspectives for", "addressing HPs"], size=30, weight=700, fill=RED)
    f.slot("global_perspective", 250, 690, 190, 190, shape="circle", label="GHP perspective")
    f.slot("local_perspective", 250, 930, 190, 190, shape="circle", label="LHP perspective")

    f.slot("temporal_stack", 1070, 750, 200, 200, shape="circle", label="temporal variation")
    for i, (y, label) in enumerate([(640, "patch coverage"), (850, "patch intensity"), (1060, "pattern analysis")], 1):
        f.slot(f"variation_{i}", 1320, y, 150, 150, shape="circle", label=label)
    f.line(1260, 850, 1320, 715, stroke=INK, sw=5)
    f.line(1260, 850, 1320, 925, stroke=INK, sw=5)
    f.line(1260, 850, 1320, 1135, stroke=INK, sw=5)

    f.slot("cluster_typology", 500, 1270, 210, 210, shape="circle", label="cluster typology")
    f.slot("polycentricity", 760, 1270, 210, 210, shape="circle", label="polycentric structure")
    f.multiline(1320, 1240, ["Clustering of HPs", "tailored mitigation"], size=28, weight=700, fill=RED)

    f.multiline(1280, 120, ["Heat Governance Zones", "// HGZs //"], size=34, weight=700, fill=RED)
    f.multiline(1320, 410, ["Spatiotemporal", "variations of HGZs"], size=32, weight=700, fill=RED)
    return f


BUILDERS = {
    "graphical-abstract": graphical_abstract,
    "workflow": workflow,
    "cluster-evidence": cluster_evidence,
    "conceptual-synthesis": conceptual_synthesis,
}


def parse_assets(values: list[str]) -> dict[str, Path]:
    assets: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Invalid --asset value {value!r}; expected slot=path")
        slot, raw_path = value.split("=", 1)
        path = Path(raw_path).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Asset for slot {slot!r} does not exist: {path}")
        assets[slot] = path
    return assets


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", required=True, choices=sorted(BUILDERS))
    parser.add_argument("--out", required=True, help="Output SVG path")
    parser.add_argument("--asset", action="append", default=[], help="Replace a slot with an image: slot=path")
    parser.add_argument("--manifest", help="Optional layout manifest JSON; defaults beside the SVG")
    args = parser.parse_args()

    assets = parse_assets(args.asset)
    figure = BUILDERS[args.preset](assets)
    out = Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(figure.render(), encoding="utf-8")

    manifest = Path(args.manifest).expanduser().resolve() if args.manifest else out.with_suffix(".layout.json")
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps(
            {
                "preset": figure.preset,
                "canvas_px": [figure.width, figure.height],
                "aspect_ratio": round(figure.width / figure.height, 6),
                "slots": figure.slots,
                "disclosure": "Layout scaffold only; placeholder or substitute assets are not source-article evidence.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(out)
    print(manifest)


if __name__ == "__main__":
    main()
