#!/usr/bin/env python3
"""Inventory candidate assets for a hybrid scientific figure."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


RASTER_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tiff", ".bmp"}
OTHER_EXTENSIONS = {".svg", ".pdf", ".drawio"}


def raster_size(path: Path) -> tuple[int | None, int | None, str]:
    try:
        from PIL import Image

        with Image.open(path) as image:
            return int(image.width), int(image.height), "read"
    except Exception as exc:  # asset inventory must continue if one file is damaged
        return None, None, f"unreadable: {type(exc).__name__}"


def svg_size(path: Path) -> tuple[float | None, float | None, str]:
    try:
        head = path.read_text(encoding="utf-8", errors="ignore")[:10000]
        width_match = re.search(r'\bwidth=["\']([0-9.]+)', head)
        height_match = re.search(r'\bheight=["\']([0-9.]+)', head)
        if width_match and height_match:
            return float(width_match.group(1)), float(height_match.group(1)), "read"
        viewbox = re.search(r'\bviewBox=["\']([^"\']+)["\']', head)
        if viewbox:
            numbers = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", viewbox.group(1))
            if len(numbers) == 4:
                return float(numbers[2]), float(numbers[3]), "viewBox"
        return None, None, "size-not-declared"
    except Exception as exc:
        return None, None, f"unreadable: {type(exc).__name__}"


def inspect(path: Path, root: Path) -> dict[str, object]:
    suffix = path.suffix.lower()
    width: float | int | None = None
    height: float | int | None = None
    status = "not-applicable"
    if suffix in RASTER_EXTENSIONS:
        width, height, status = raster_size(path)
    elif suffix == ".svg":
        width, height, status = svg_size(path)
    aspect = round(float(width) / float(height), 4) if width and height else None
    return {
        "path": path.relative_to(root).as_posix(),
        "extension": suffix,
        "bytes": path.stat().st_size,
        "width": width,
        "height": height,
        "aspect_ratio": aspect,
        "dimension_status": status,
        "scientific_role": "TODO",
        "source_or_script": "TODO",
        "empirical_or_conceptual": "TODO",
        "crop_or_filter": "TODO",
        "publication_permission": "TODO",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Directory containing candidate figure assets")
    parser.add_argument("--out", type=Path, help="Write JSON inventory to this path; otherwise print it")
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        raise SystemExit(f"Not a directory: {root}")

    allowed = RASTER_EXTENSIONS | OTHER_EXTENSIONS
    assets = [inspect(path, root) for path in sorted(root.rglob("*")) if path.is_file() and path.suffix.lower() in allowed]
    payload = {"root": str(root), "asset_count": len(assets), "assets": assets}
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote {len(assets)} assets to {args.out.resolve()}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
