from __future__ import annotations

import argparse
import ast
import json
import math
import re
from datetime import datetime
from io import BytesIO
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager
from matplotlib.patches import Patch
from PIL import Image, ImageDraw, ImageFont
from shapely.ops import unary_union


BACKGROUND = "#f8f7f1"
PANEL = "#fffdf7"
INK = "#263238"
MUTED = "#64706f"
GRID = "#d8d6cc"
BOUNDARY = "#ffffff"
BASEMAP_TILE_URL = "https://{subdomain}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png"
BASEMAP_WEB_MERCATOR_HALF = 20037508.342789244
BASEMAP_TILE_SIZE = 256
BASEMAP_TILE_CACHE: dict[str, Image.Image] = {}

GROUP_STYLE = {
    "居住用地": {"color": "#F2C36B", "keywords": ["residential", "housing", "居住", "住宅", "居民"]},
    "工业与生产用地": {"color": "#A98274", "keywords": ["industrial", "works", "warehouse", "logistics", "工业", "仓储", "物流", "生产"]},
    "商服与公共设施用地": {"color": "#D96C64", "keywords": ["commercial", "retail", "institutional", "office", "school", "hospital", "商业", "商服", "公共", "教育", "医疗", "文化", "体育"]},
    "绿地与开敞空间": {"color": "#6FA869", "keywords": ["park", "grass", "green", "forest", "garden", "village_green", "公园", "绿地", "林地", "草地", "开敞"]},
    "水体与游憩设施": {"color": "#6BAED6", "keywords": ["water", "river", "lake", "theme_park", "water_park", "water_hazard", "河", "湖", "水", "游憩"]},
    "待开发/建设中用地": {"color": "#B7B8B2", "keywords": ["brownfield", "greenfield", "construction", "vacant", "棕地", "待开发", "建设中"]},
    "农业设施/园艺用地": {"color": "#C6CF76", "keywords": ["farmland", "farm", "orchard", "greenhouse", "horticulture", "agriculture", "农业", "农田", "耕地", "园艺"]},
    "交通及附属设施": {"color": "#8C9AA8", "keywords": ["garage", "parking", "transport", "road", "railway", "停车", "交通", "道路", "铁路"]},
    "其他": {"color": "#D6D0C2", "keywords": []},
}

CLASS_LABELS = {
    "residential": "居住用地",
    "industrial": "工业用地",
    "commercial": "商业用地",
    "retail": "零售商业",
    "park": "公园绿地",
    "grass": "草地/开敞绿地",
    "brownfield": "棕地/再开发",
    "greenfield": "绿地待建",
    "theme_park": "主题公园",
    "green": "绿地",
    "works": "生产设施",
    "greenhouse_horticulture": "温室园艺",
    "garages": "停车库/附属设施",
    "water_hazard": "水体/障碍水面",
    "water_park": "水上游憩",
    "lateral_water_hazard": "带状水面",
    "institutional": "公共机构",
    "village_green": "社区绿地",
}

CLASS_FIELD_CANDIDATES = [
    "class",
    "landuse",
    "subtype",
    "fclass",
    "type",
    "category",
    "用地类型",
    "用地性质",
    "地类",
    "类型",
    "类别",
]
COLOR_FIELD_CANDIDATES = ["LandColor", "color", "fill", "Color", "颜色", "色彩"]
ADMIN_NAME_FIELD_CANDIDATES = ["地名", "县级", "市级", "省级", "name", "NAME_3", "NAME_2", "NAME_1", "乡"]
ADMIN_PARENT_FIELD_CANDIDATES = ["地级", "市级", "地级市", "市", "NAME_2", "NAME_1"]


def configure_fonts() -> str:
    candidates = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Source Han Sans SC", "Arial Unicode MS", "DejaVu Sans"]
    available = {font.name for font in font_manager.fontManager.ttflist}
    selected = next((name for name in candidates if name in available), "DejaVu Sans")
    plt.rcParams["font.family"] = selected
    plt.rcParams["axes.unicode_minus"] = False
    return selected


def ensure_dirs(out_dir: Path) -> dict[str, Path]:
    paths = {"root": out_dir, "maps": out_dir / "maps", "charts": out_dir / "charts", "tables": out_dir / "tables"}
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def nonempty_ratio(series: pd.Series) -> float:
    values = series.dropna().astype(str).str.strip()
    return float((values != "").mean()) if len(series) else 0.0


def choose_field(gdf: gpd.GeoDataFrame, explicit: str | None, candidates: list[str]) -> str | None:
    if explicit:
        if explicit not in gdf.columns:
            raise ValueError(f"field not found: {explicit}")
        return explicit
    lower_lookup = {str(col).lower(): col for col in gdf.columns}
    for candidate in candidates:
        if candidate in gdf.columns and nonempty_ratio(gdf[candidate]) > 0:
            return candidate
        if candidate.lower() in lower_lookup and nonempty_ratio(gdf[lower_lookup[candidate.lower()]]) > 0:
            return lower_lookup[candidate.lower()]
    scored = []
    for col in gdf.columns:
        if col == gdf.geometry.name:
            continue
        unique_count = gdf[col].nunique(dropna=True)
        if 1 < unique_count <= 80 and nonempty_ratio(gdf[col]) > 0.3:
            scored.append((unique_count, str(col)))
    return sorted(scored)[0][1] if scored else None


def parse_source_tags(value: object) -> str | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    parsed = value
    if isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
        except Exception:
            text = value.strip()
            return text or None
    if isinstance(parsed, list):
        tag_dict = {}
        for item in parsed:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                tag_dict[str(item[0]).lower()] = str(item[1])
            elif isinstance(item, dict):
                tag_dict.update({str(k).lower(): str(v) for k, v in item.items()})
        for key in ["landuse", "leisure", "amenity", "natural", "tourism", "building"]:
            if key in tag_dict:
                return tag_dict[key]
    if isinstance(parsed, dict):
        for key in ["landuse", "leisure", "amenity", "natural", "tourism", "building"]:
            if key in parsed:
                return str(parsed[key])
    return None


def normalize_class(value: object) -> str:
    text = str(value or "").strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return "unclassified"
    return re.sub(r"\s+", "_", text)


def infer_classes(gdf: gpd.GeoDataFrame, class_field: str | None) -> pd.Series:
    if class_field:
        values = gdf[class_field].map(normalize_class)
    elif "source_tags" in gdf.columns:
        values = gdf["source_tags"].map(parse_source_tags).map(normalize_class)
    else:
        values = pd.Series(["unclassified"] * len(gdf), index=gdf.index)
    if (values == "unclassified").mean() > 0.75 and "source_tags" in gdf.columns:
        parsed = gdf["source_tags"].map(parse_source_tags).map(normalize_class)
        values = values.mask(values == "unclassified", parsed)
    return values.fillna("unclassified")


def label_for_class(class_name: str) -> str:
    return CLASS_LABELS.get(class_name, class_name)


def group_for_class(class_name: str) -> str:
    return group_match_for_class(class_name)[0]


def group_match_for_class(class_name: str) -> tuple[str, str]:
    text = class_name.lower()
    matches: list[tuple[int, int, str, str]] = []
    for group, spec in GROUP_STYLE.items():
        if group == "其他":
            continue
        for keyword in spec["keywords"]:
            if keyword.lower() in text:
                exact_rank = 0 if text == keyword.lower() else 1
                matches.append((exact_rank, -len(keyword), group, keyword))
    if matches:
        exact_rank, _, group, keyword = sorted(matches)[0]
        return group, f"关键词匹配：{keyword}" + ("（精确值）" if exact_rank == 0 else "")
    return "其他", "未匹配默认归入：其他"


def infer_utm_crs(gdf: gpd.GeoDataFrame) -> str:
    wgs = gdf.to_crs(4326)
    minx, miny, maxx, maxy = wgs.total_bounds
    lon = (minx + maxx) / 2
    lat = (miny + maxy) / 2
    zone = int((lon + 180) // 6) + 1
    epsg = 32600 + zone if lat >= 0 else 32700 + zone
    return f"EPSG:{epsg}"


def normalize_admin_text(value: object) -> str:
    return re.sub(r"\s+", "", str(value or "")).strip()


def parse_admin_names(values: list[str] | None) -> list[str]:
    names: list[str] = []
    for value in values or []:
        names.extend(item.strip() for item in re.split(r"[,，;；]", value) if item.strip())
    return list(dict.fromkeys(names))


def read_admin_context(
    admin_path: Path,
    admin_names: list[str],
    name_field: str | None,
    parent_field: str | None,
    parent_value: str | None,
    target_crs: object,
) -> dict:
    admin = gpd.read_file(admin_path)
    if admin.crs is None:
        admin = admin.set_crs(4326)
    admin = admin.loc[admin.geometry.notna() & ~admin.geometry.is_empty].copy()
    if admin.empty:
        raise ValueError("admin boundary contains no non-empty geometry")
    chosen_name_field = choose_field(admin, name_field, ADMIN_NAME_FIELD_CANDIDATES)
    if not chosen_name_field:
        raise ValueError("could not identify an administrative name field")
    names = parse_admin_names(admin_names)
    if not names:
        raise ValueError("--admin-name is required when --admin-boundary is provided")
    wanted = {normalize_admin_text(name) for name in names}
    name_values = admin[chosen_name_field].map(normalize_admin_text)
    selected_mask = name_values.isin(wanted)
    if not selected_mask.any():
        selected_mask = name_values.map(lambda value: any(value.startswith(name) for name in wanted))

    chosen_parent_field = None
    if parent_value:
        chosen_parent_field = choose_field(admin, parent_field, ADMIN_PARENT_FIELD_CANDIDATES)
        if not chosen_parent_field:
            raise ValueError("could not identify the administrative parent field")
        selected_mask &= admin[chosen_parent_field].map(normalize_admin_text) == normalize_admin_text(parent_value)
    selected = admin.loc[selected_mask].copy()
    if selected.empty:
        parent_note = f" under {parent_value}" if parent_value else ""
        raise ValueError(f"no administrative features matched {names}{parent_note}")
    try:
        selected["geometry"] = selected.geometry.make_valid()
    except AttributeError:
        pass
    selected_plot = selected.to_crs(target_crs)
    selection_geometry = unary_union(selected_plot.geometry)
    if selection_geometry.is_empty:
        raise ValueError("selected administrative boundary is empty")
    return {
        "path": str(admin_path),
        "source_crs": str(admin.crs),
        "name_field": chosen_name_field,
        "parent_field": chosen_parent_field,
        "parent_value": parent_value or "",
        "requested_names": names,
        "selected_names": [str(value) for value in selected[chosen_name_field].tolist()],
        "selected_count": int(len(selected)),
        "selected_admin": selected,
        "selection_geometry": selection_geometry,
    }


def read_landuse(
    input_path: Path,
    class_field: str | None,
    color_field: str | None,
    area_crs: str | None,
    admin_boundary: Path | None = None,
    admin_names: list[str] | None = None,
    admin_name_field: str | None = None,
    admin_parent_field: str | None = None,
    admin_parent: str | None = None,
) -> tuple[gpd.GeoDataFrame, str | None, str | None, str, dict | None]:
    gdf = gpd.read_file(input_path)
    if gdf.crs is None:
        gdf = gdf.set_crs(4326)
    gdf = gdf.loc[gdf.geometry.notna() & ~gdf.geometry.is_empty].copy()
    if gdf.empty:
        raise ValueError("input layer contains no non-empty geometry")
    input_feature_count = int(len(gdf))
    chosen_class = choose_field(gdf, class_field, CLASS_FIELD_CANDIDATES)
    chosen_color = choose_field(gdf, color_field, COLOR_FIELD_CANDIDATES)
    chosen_area_crs = area_crs or infer_utm_crs(gdf)
    admin_context = None
    if admin_boundary:
        admin_context = read_admin_context(
            admin_boundary,
            admin_names or [],
            admin_name_field,
            admin_parent_field,
            admin_parent,
            gdf.crs,
        )
        clip_mask = gpd.GeoDataFrame({"geometry": [admin_context["selection_geometry"]]}, crs=gdf.crs)
        gdf = gpd.clip(gdf, clip_mask)
        gdf = gdf.loc[gdf.geometry.notna() & ~gdf.geometry.is_empty].copy()
        if gdf.empty:
            raise ValueError("administrative selection does not intersect the land-use layer")
        admin_context["input_feature_count"] = input_feature_count
        admin_context["clipped_feature_count"] = int(len(gdf))
    gdf["class_norm"] = infer_classes(gdf, chosen_class)
    gdf["class_label"] = gdf["class_norm"].map(label_for_class)
    class_mapping = {name: group_match_for_class(name) for name in gdf["class_norm"].unique()}
    gdf["landuse_group"] = gdf["class_norm"].map(lambda value: class_mapping[value][0])
    gdf["mapping_rule"] = gdf["class_norm"].map(lambda value: class_mapping[value][1])
    area_gdf = gdf.to_crs(chosen_area_crs)
    gdf["area_m2"] = area_gdf.geometry.area
    gdf["area_ha"] = gdf["area_m2"] / 10000.0
    gdf["area_km2"] = gdf["area_m2"] / 1_000_000.0
    return gdf, chosen_class, chosen_color, chosen_area_crs, admin_context


def summarize(gdf: gpd.GeoDataFrame, paths: dict[str, Path], color_field: str | None) -> tuple[pd.DataFrame, pd.DataFrame]:
    total_area = float(gdf["area_ha"].sum())
    class_summary = (
        gdf.groupby(["class_norm", "class_label", "landuse_group"], dropna=False)
        .agg(
            feature_count=("class_norm", "size"),
            area_ha=("area_ha", "sum"),
            area_km2=("area_km2", "sum"),
            mapping_rule=("mapping_rule", "first"),
        )
        .reset_index()
        .sort_values("area_ha", ascending=False)
    )
    class_summary["area_pct"] = class_summary["area_ha"] / total_area * 100
    if color_field:
        class_summary["source_color"] = class_summary["class_norm"].map(gdf.groupby("class_norm")[color_field].first().to_dict()).fillna("")
    else:
        class_summary["source_color"] = ""
    group_summary = (
        gdf.groupby("landuse_group", dropna=False)
        .agg(feature_count=("landuse_group", "size"), area_ha=("area_ha", "sum"), area_km2=("area_km2", "sum"))
        .reset_index()
    )
    group_summary["area_pct"] = group_summary["area_ha"] / total_area * 100
    group_summary["color"] = group_summary["landuse_group"].map(lambda group: GROUP_STYLE[group]["color"])
    group_summary["order"] = group_summary["landuse_group"].map(lambda group: list(GROUP_STYLE).index(group))
    group_summary = group_summary.sort_values(["area_ha", "order"], ascending=[False, True]).drop(columns=["order"])
    class_summary.to_csv(paths["tables"] / "landuse_class_summary.csv", index=False, encoding="utf-8-sig")
    class_summary[["class_norm", "class_label", "landuse_group", "mapping_rule", "feature_count", "area_ha", "area_pct"]].to_csv(
        paths["tables"] / "landuse_class_to_group_mapping.csv", index=False, encoding="utf-8-sig"
    )
    group_summary.to_csv(paths["tables"] / "landuse_group_summary.csv", index=False, encoding="utf-8-sig")
    return class_summary, group_summary


def map_extent(gdf: gpd.GeoDataFrame, pad_ratio: float = 0.035) -> tuple[float, float, float, float]:
    minx, miny, maxx, maxy = gdf.total_bounds
    dx = max(maxx - minx, 1)
    dy = max(maxy - miny, 1)
    return minx - dx * pad_ratio, maxx + dx * pad_ratio, miny - dy * pad_ratio, maxy + dy * pad_ratio


def nice_scale_length(width_m: float) -> int:
    target = max(width_m / 5.0, 1)
    candidates = [500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]
    usable = [value for value in candidates if value <= target]
    return usable[-1] if usable else candidates[0]


def add_scale_bar(ax) -> None:
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    length = nice_scale_length(x1 - x0)
    x = x0 + (x1 - x0) * 0.06
    y = y0 + (y1 - y0) * 0.065
    tick = (y1 - y0) * 0.012
    ax.plot([x, x + length], [y, y], color=INK, linewidth=2.4, solid_capstyle="butt", zorder=20)
    ax.plot([x, x], [y - tick, y + tick], color=INK, linewidth=1.2, zorder=20)
    ax.plot([x + length, x + length], [y - tick, y + tick], color=INK, linewidth=1.2, zorder=20)
    label = f"{int(length / 1000)} km" if length >= 1000 else f"{length} m"
    ax.text(x + length / 2, y + tick * 1.8, label, ha="center", va="bottom", fontsize=9, color=INK, zorder=21)


def add_north_arrow(ax) -> None:
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    x = x1 - (x1 - x0) * 0.07
    y = y1 - (y1 - y0) * 0.13
    size = (y1 - y0) * 0.065
    ax.annotate("", xy=(x, y + size), xytext=(x, y - size * 0.25), arrowprops=dict(arrowstyle="-|>", color=INK, linewidth=1.8), zorder=21)
    ax.text(x, y + size * 1.14, "N", ha="center", va="bottom", fontsize=11, fontweight="bold", color=INK, zorder=21)


def setup_map_axis(ax, title: str, subtitle: str) -> None:
    ax.set_facecolor(BACKGROUND)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color("#d2d0c8")
        spine.set_linewidth(0.8)
    ax.set_title(title, loc="left", fontsize=21, fontweight="bold", color=INK, pad=16)
    ax.text(0.0, 1.0, subtitle, transform=ax.transAxes, ha="left", va="bottom", fontsize=9.5, color=MUTED)


def prepare_plot_gdf(gdf: gpd.GeoDataFrame, map_crs: str) -> gpd.GeoDataFrame:
    plot_gdf = gdf.to_crs(map_crs).copy()
    plot_gdf["geometry"] = plot_gdf.geometry.simplify(20, preserve_topology=True)
    return plot_gdf.loc[plot_gdf.geometry.notna() & ~plot_gdf.geometry.is_empty].copy()


def prepare_admin_plot(admin_context: dict | None, map_crs: str) -> gpd.GeoDataFrame | None:
    if not admin_context:
        return None
    admin_plot = admin_context["selected_admin"].to_crs(map_crs).copy()
    admin_plot["geometry"] = admin_plot.geometry.simplify(12, preserve_topology=True)
    return admin_plot.loc[admin_plot.geometry.notna() & ~admin_plot.geometry.is_empty].copy()


def map_extent_for(plot_gdf: gpd.GeoDataFrame, admin_plot_gdf: gpd.GeoDataFrame | None) -> tuple[float, float, float, float]:
    extent_source = admin_plot_gdf if admin_plot_gdf is not None and len(admin_plot_gdf) else plot_gdf
    return map_extent(extent_source, pad_ratio=0.025)


def _web_mercator_tile_xy(x: float, y: float, zoom: int) -> tuple[int, int]:
    n = 2**zoom
    x_tile = int((x + BASEMAP_WEB_MERCATOR_HALF) / (2 * BASEMAP_WEB_MERCATOR_HALF) * n)
    y_tile = int((1 - math.asinh(y / BASEMAP_WEB_MERCATOR_HALF) / math.pi) / 2 * n)
    return max(0, min(n - 1, x_tile)), max(0, min(n - 1, y_tile))


def _web_mercator_tile_y_edge(tile_y: int, zoom: int) -> float:
    """Convert a slippy-map tile row edge back to Web Mercator metres."""
    n = 2**zoom
    normalized = 1 - 2 * tile_y / n
    return BASEMAP_WEB_MERCATOR_HALF * math.sinh(math.pi * normalized)


def _choose_basemap_zoom(width_m: float, height_m: float) -> int:
    target_width = max(width_m, height_m, 1.0)
    world_width = 2 * BASEMAP_WEB_MERCATOR_HALF
    zoom = round(math.log2(world_width * 5 / target_width))
    return max(6, min(15, zoom))


def add_light_basemap(ax, map_crs: str, basemap_mode: str, basemap_alpha: float) -> dict:
    """Add a pale, label-free Carto tile layer and report a recoverable status."""
    info = {
        "requested": basemap_mode,
        "provider": "CartoDB Positron No Labels",
        "tile_url": BASEMAP_TILE_URL,
        "alpha": float(basemap_alpha),
        "status": "disabled" if basemap_mode == "none" else "not_run",
        "zoom": None,
        "tiles_fetched": 0,
        "tiles_missing": 0,
    }
    if basemap_mode == "none":
        return info
    if basemap_mode != "carto-light-nolabels":
        info["status"] = "fallback_no_basemap"
        info["error"] = f"unsupported basemap mode: {basemap_mode}"
        return info
    try:
        import numpy as np
        import requests
        from pyproj import Transformer
        from rasterio.transform import from_bounds
        from rasterio.warp import Resampling, calculate_default_transform, reproject

        minx, maxx = ax.get_xlim()
        miny, maxy = ax.get_ylim()
        transformer = Transformer.from_crs(map_crs, "EPSG:3857", always_xy=True)
        corners = [
            transformer.transform(minx, miny),
            transformer.transform(minx, maxy),
            transformer.transform(maxx, miny),
            transformer.transform(maxx, maxy),
        ]
        web_minx = max(-BASEMAP_WEB_MERCATOR_HALF, min(point[0] for point in corners))
        web_maxx = min(BASEMAP_WEB_MERCATOR_HALF, max(point[0] for point in corners))
        web_miny = max(-BASEMAP_WEB_MERCATOR_HALF, min(point[1] for point in corners))
        web_maxy = min(BASEMAP_WEB_MERCATOR_HALF, max(point[1] for point in corners))
        if web_minx >= web_maxx or web_miny >= web_maxy:
            raise ValueError("map extent does not overlap Web Mercator bounds")

        zoom = _choose_basemap_zoom(web_maxx - web_minx, web_maxy - web_miny)
        info["zoom"] = zoom
        left_tile, top_tile = _web_mercator_tile_xy(web_minx, web_maxy, zoom)
        right_tile, bottom_tile = _web_mercator_tile_xy(web_maxx, web_miny, zoom)
        columns = right_tile - left_tile + 1
        rows = bottom_tile - top_tile + 1
        mosaic = Image.new("RGB", (columns * BASEMAP_TILE_SIZE, rows * BASEMAP_TILE_SIZE), "#f5f5f2")
        session = requests.Session()
        session.headers.update({"User-Agent": "urban-landuse-mapping/1.0"})
        missing = 0
        available = 0
        for row_idx, tile_y in enumerate(range(top_tile, bottom_tile + 1)):
            for col_idx, tile_x in enumerate(range(left_tile, right_tile + 1)):
                subdomain = "abcd"[(tile_x + tile_y) % 4]
                tile_url = BASEMAP_TILE_URL.format(subdomain=subdomain, z=zoom, x=tile_x, y=tile_y)
                tile = BASEMAP_TILE_CACHE.get(tile_url)
                if tile is None:
                    try:
                        response = session.get(tile_url, timeout=10)
                        response.raise_for_status()
                        tile = Image.open(BytesIO(response.content)).convert("RGB")
                        BASEMAP_TILE_CACHE[tile_url] = tile
                        info["tiles_fetched"] += 1
                    except Exception:
                        missing += 1
                        continue
                mosaic.paste(tile, (col_idx * BASEMAP_TILE_SIZE, row_idx * BASEMAP_TILE_SIZE))
                available += 1
        info["tiles_missing"] = missing
        if available == 0:
            raise RuntimeError("no Carto basemap tiles could be downloaded")

        src = np.asarray(mosaic, dtype=np.uint8).transpose(2, 0, 1)
        src_minx = (left_tile / 2**zoom * 2 - 1) * BASEMAP_WEB_MERCATOR_HALF
        src_miny = _web_mercator_tile_y_edge(bottom_tile + 1, zoom)
        src_maxx = ((right_tile + 1) / 2**zoom * 2 - 1) * BASEMAP_WEB_MERCATOR_HALF
        src_maxy = _web_mercator_tile_y_edge(top_tile, zoom)
        src_transform = from_bounds(
            src_minx,
            src_miny,
            src_maxx,
            src_maxy,
            mosaic.width,
            mosaic.height,
        )
        dst_transform, dst_width, dst_height = calculate_default_transform(
            "EPSG:3857",
            map_crs,
            mosaic.width,
            mosaic.height,
            src_minx,
            src_miny,
            src_maxx,
            src_maxy,
        )
        dst = np.zeros((3, dst_height, dst_width), dtype=np.uint8)
        reproject(
            source=src,
            destination=dst,
            src_transform=src_transform,
            src_crs="EPSG:3857",
            dst_transform=dst_transform,
            dst_crs=map_crs,
            resampling=Resampling.bilinear,
        )
        left = dst_transform.c
        top = dst_transform.f
        right = left + dst_transform.a * dst_width
        bottom = top + dst_transform.e * dst_height
        ax.imshow(
            dst.transpose(1, 2, 0),
            extent=(left, right, bottom, top),
            origin="upper",
            interpolation="bilinear",
            alpha=basemap_alpha,
            zorder=1.05,
        )
        info["status"] = "added" if missing == 0 else "added_partial"
        return info
    except Exception as exc:
        info["status"] = "fallback_no_basemap"
        info["error"] = f"{type(exc).__name__}: {exc}"
        return info


def draw_admin_context(
    ax,
    admin_plot_gdf: gpd.GeoDataFrame | None,
    admin_name_field: str | None,
    fill_alpha: float = 0.22,
) -> None:
    if admin_plot_gdf is None or admin_plot_gdf.empty:
        return
    admin_plot_gdf.plot(ax=ax, facecolor="#efeee8", edgecolor="none", alpha=fill_alpha, zorder=1.15)
    admin_plot_gdf.boundary.plot(ax=ax, color="#60655f", linewidth=1.0, zorder=1.35)
    ax.text(
        0.012,
        0.982,
        "浅灰范围：选定行政区；底图仅作位置参照，未覆盖用地不计入面积统计",
        transform=ax.transAxes,
        fontsize=7.6,
        color=MUTED,
        ha="left",
        va="top",
        zorder=13,
        bbox=dict(facecolor="#f8f7f1", edgecolor="none", alpha=0.78, pad=2.2),
    )
    for _, row in admin_plot_gdf.iterrows():
        point = row.geometry.representative_point()
        label = str(row[admin_name_field]) if admin_name_field and admin_name_field in row else ""
        if label:
            ax.text(
                point.x,
                point.y,
                label,
                fontsize=8.5,
                color="#4c514c",
                ha="center",
                va="center",
                zorder=12,
                bbox=dict(facecolor="#f8f7f1", edgecolor="none", alpha=0.72, pad=1.6),
            )


def draw_group_map(
    plot_gdf: gpd.GeoDataFrame,
    group_summary: pd.DataFrame,
    output_path: Path,
    title: str,
    subtitle: str,
    source_note: str,
    admin_plot_gdf: gpd.GeoDataFrame | None = None,
    admin_name_field: str | None = None,
    basemap_mode: str = "carto-light-nolabels",
    basemap_alpha: float = 0.38,
) -> dict:
    fig = plt.figure(figsize=(13.2, 9.2), facecolor=BACKGROUND)
    grid = fig.add_gridspec(1, 5, width_ratios=[1, 1, 1, 1, 1.15], wspace=0.02)
    ax = fig.add_subplot(grid[0, :4])
    side = fig.add_subplot(grid[0, 4])
    setup_map_axis(ax, title, subtitle)
    minx, maxx, miny, maxy = map_extent_for(plot_gdf, admin_plot_gdf)
    for group in list(GROUP_STYLE):
        layer = plot_gdf.loc[plot_gdf["landuse_group"] == group]
        if len(layer):
            layer.plot(ax=ax, color=GROUP_STYLE[group]["color"], edgecolor=BOUNDARY, linewidth=0.04, alpha=0.96, zorder=2)
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    basemap_info = add_light_basemap(ax, str(plot_gdf.crs), basemap_mode, basemap_alpha)
    draw_admin_context(ax, admin_plot_gdf, admin_name_field)
    add_scale_bar(ax)
    add_north_arrow(ax)
    ax.text(0.01, 0.012, source_note, transform=ax.transAxes, fontsize=8.5, color=MUTED, ha="left", va="bottom", bbox=dict(facecolor=BACKGROUND, edgecolor="none", alpha=0.72, pad=3))
    side.set_facecolor(PANEL)
    side.axis("off")
    side.text(0.0, 0.98, "图例与结构", transform=side.transAxes, fontsize=15, fontweight="bold", color=INK, va="top")
    y = 0.91
    for _, row in group_summary.sort_values("area_ha", ascending=False).iterrows():
        group = row["landuse_group"]
        side.add_patch(plt.Rectangle((0.0, y - 0.018), 0.07, 0.024, transform=side.transAxes, color=GROUP_STYLE[group]["color"], ec="#ffffff", lw=0.5))
        side.text(0.09, y, group, transform=side.transAxes, fontsize=9.3, color=INK, va="center")
        side.text(0.98, y, f"{row['area_pct']:.1f}%", transform=side.transAxes, fontsize=9.0, color=MUTED, va="center", ha="right")
        y -= 0.055
    total = float(group_summary["area_ha"].sum())
    side.plot([0, 1], [y - 0.015, y - 0.015], transform=side.transAxes, color=GRID, lw=0.8)
    side.text(0.0, y - 0.07, "统计口径", transform=side.transAxes, fontsize=12, fontweight="bold", color=INK)
    side.text(0.0, y - 0.135, f"斑块数：{len(plot_gdf):,}\n总面积：{total:,.1f} ha\n面积换算：1 ha = 10,000 m²\n小类保留在 CSV 表。", transform=side.transAxes, fontsize=9.2, color=MUTED, va="top", linespacing=1.45)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor=BACKGROUND)
    plt.close(fig)
    return basemap_info


def raw_palette(classes: list[str]) -> dict[str, str]:
    cmap = plt.get_cmap("tab20")
    return {name: matplotlib.colors.to_hex(cmap(i % 20)) for i, name in enumerate(classes)}


def draw_raw_class_map(
    plot_gdf: gpd.GeoDataFrame,
    class_summary: pd.DataFrame,
    output_path: Path,
    source_note: str,
    admin_plot_gdf: gpd.GeoDataFrame | None = None,
    admin_name_field: str | None = None,
    basemap_mode: str = "carto-light-nolabels",
    basemap_alpha: float = 0.38,
) -> dict:
    colors = raw_palette(class_summary["class_norm"].tolist())
    fig = plt.figure(figsize=(13.2, 9.2), facecolor=BACKGROUND)
    grid = fig.add_gridspec(1, 5, width_ratios=[1, 1, 1, 1, 1.25], wspace=0.02)
    ax = fig.add_subplot(grid[0, :4])
    side = fig.add_subplot(grid[0, 4])
    setup_map_axis(ax, "用地现状图：原始分类", "按原始分类字段渲染，用于核对精细类别分布")
    minx, maxx, miny, maxy = map_extent_for(plot_gdf, admin_plot_gdf)
    for class_name in class_summary["class_norm"]:
        layer = plot_gdf.loc[plot_gdf["class_norm"] == class_name]
        if len(layer):
            layer.plot(ax=ax, color=colors[class_name], edgecolor=BOUNDARY, linewidth=0.035, alpha=0.93, zorder=2)
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    basemap_info = add_light_basemap(ax, str(plot_gdf.crs), basemap_mode, basemap_alpha)
    draw_admin_context(ax, admin_plot_gdf, admin_name_field)
    add_scale_bar(ax)
    add_north_arrow(ax)
    ax.text(0.01, 0.012, source_note, transform=ax.transAxes, fontsize=8.5, color=MUTED, ha="left", va="bottom", bbox=dict(facecolor=BACKGROUND, edgecolor="none", alpha=0.72, pad=3))
    side.set_facecolor(PANEL)
    side.axis("off")
    side.text(0.0, 0.98, "原始分类图例", transform=side.transAxes, fontsize=14, fontweight="bold", color=INK, va="top")
    y = 0.93
    for _, row in class_summary.iterrows():
        name = row["class_norm"]
        side.add_patch(plt.Rectangle((0.0, y - 0.015), 0.055, 0.02, transform=side.transAxes, color=colors[name], ec="#ffffff", lw=0.4))
        side.text(0.075, y, str(row["class_label"])[:18], transform=side.transAxes, fontsize=8.1, color=INK, va="center")
        side.text(0.99, y, f"{row['area_pct']:.1f}%", transform=side.transAxes, fontsize=7.8, color=MUTED, va="center", ha="right")
        y -= 0.043
        if y < 0.05:
            break
    fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor=BACKGROUND)
    plt.close(fig)
    return basemap_info


def draw_donut_chart(group_summary: pd.DataFrame, output_path: Path) -> None:
    data = group_summary.sort_values("area_ha", ascending=False)
    fig, ax = plt.subplots(figsize=(8.2, 7.2), facecolor=BACKGROUND)
    wedges, _ = ax.pie(data["area_ha"], startangle=90, colors=[GROUP_STYLE[g]["color"] for g in data["landuse_group"]], counterclock=False, wedgeprops=dict(width=0.38, edgecolor=BACKGROUND, linewidth=1.2))
    total = float(data["area_ha"].sum())
    ax.text(0, 0.04, f"{total:,.0f}", ha="center", va="center", fontsize=22, fontweight="bold", color=INK)
    ax.text(0, -0.15, "ha", ha="center", va="center", fontsize=11, color=MUTED)
    ax.set_title("用地结构饼状图（按面积）", loc="left", fontsize=19, fontweight="bold", color=INK, pad=16)
    labels = [f"{r.landuse_group}  {r.area_ha:,.0f} ha  ({r.area_pct:.1f}%)" for r in data.itertuples(index=False)]
    ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False, fontsize=9)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor=BACKGROUND)
    plt.close(fig)


def draw_bar_chart(class_summary: pd.DataFrame, output_path: Path) -> None:
    top = class_summary.head(12).copy()
    if len(class_summary) > 12:
        other = class_summary.iloc[12:]
        top = pd.concat([top, pd.DataFrame([{"class_norm": "other_minor", "class_label": "其他小类合计", "landuse_group": "其他", "feature_count": int(other["feature_count"].sum()), "area_ha": float(other["area_ha"].sum()), "area_km2": float(other["area_km2"].sum()), "area_pct": float(other["area_pct"].sum())}])], ignore_index=True)
    top = top.sort_values("area_ha", ascending=True)
    fig, ax = plt.subplots(figsize=(9.4, 7.4), facecolor=BACKGROUND)
    colors = [GROUP_STYLE.get(g, GROUP_STYLE["其他"])["color"] for g in top["landuse_group"]]
    bars = ax.barh(top["class_label"], top["area_ha"], color=colors, edgecolor="#ffffff", linewidth=0.6)
    ax.set_title("原始用地小类面积排序", loc="left", fontsize=19, fontweight="bold", color=INK, pad=14)
    ax.set_xlabel("面积（公顷）", fontsize=10, color=INK)
    ax.tick_params(axis="x", labelsize=8.5, colors=MUTED)
    ax.tick_params(axis="y", labelsize=9.0, colors=INK)
    ax.grid(axis="x", color=GRID, linewidth=0.7, alpha=0.7)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    xmax = max(top["area_ha"]) * 1.16
    ax.set_xlim(0, xmax)
    for bar, pct in zip(bars, top["area_pct"]):
        ax.text(bar.get_width() + xmax * 0.012, bar.get_y() + bar.get_height() / 2, f"{pct:.1f}%", va="center", fontsize=8.4, color=MUTED)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor=BACKGROUND)
    plt.close(fig)


def draw_dashboard(
    plot_gdf: gpd.GeoDataFrame,
    group_summary: pd.DataFrame,
    class_summary: pd.DataFrame,
    output_path: Path,
    title: str,
    source_note: str,
    admin_plot_gdf: gpd.GeoDataFrame | None = None,
    admin_name_field: str | None = None,
    basemap_mode: str = "carto-light-nolabels",
    basemap_alpha: float = 0.38,
) -> dict:
    fig = plt.figure(figsize=(16, 10), facecolor=BACKGROUND)
    grid = fig.add_gridspec(2, 3, width_ratios=[1.25, 1.25, 1], height_ratios=[1, 1], wspace=0.18, hspace=0.18)
    ax_map = fig.add_subplot(grid[:, :2])
    ax_donut = fig.add_subplot(grid[0, 2])
    ax_bar = fig.add_subplot(grid[1, 2])
    setup_map_axis(ax_map, title, "行政区裁剪后的报告总图；右侧为结构占比和原始小类面积")
    minx, maxx, miny, maxy = map_extent_for(plot_gdf, admin_plot_gdf)
    for group in list(GROUP_STYLE):
        layer = plot_gdf.loc[plot_gdf["landuse_group"] == group]
        if len(layer):
            layer.plot(ax=ax_map, color=GROUP_STYLE[group]["color"], edgecolor=BOUNDARY, linewidth=0.035, alpha=0.96, zorder=2)
    ax_map.set_xlim(minx, maxx)
    ax_map.set_ylim(miny, maxy)
    basemap_info = add_light_basemap(ax_map, str(plot_gdf.crs), basemap_mode, basemap_alpha)
    draw_admin_context(ax_map, admin_plot_gdf, admin_name_field)
    add_scale_bar(ax_map)
    add_north_arrow(ax_map)
    ax_map.legend(handles=[Patch(facecolor=GROUP_STYLE[g]["color"], edgecolor="#ffffff", label=g) for g in group_summary["landuse_group"]], loc="lower right", frameon=True, facecolor=BACKGROUND, edgecolor="none", fontsize=8.5)
    data = group_summary.sort_values("area_ha", ascending=False)
    wedges, _ = ax_donut.pie(data["area_ha"], startangle=90, colors=[GROUP_STYLE[g]["color"] for g in data["landuse_group"]], counterclock=False, wedgeprops=dict(width=0.40, edgecolor=BACKGROUND, linewidth=1.0))
    ax_donut.set_title("用地结构", loc="left", fontsize=13.5, fontweight="bold", color=INK)
    ax_donut.text(0, 0, f"{data['area_ha'].sum():,.0f} ha", ha="center", va="center", fontsize=11, fontweight="bold", color=INK)
    ax_donut.legend(wedges, [f"{r.landuse_group}  {r.area_pct:.1f}%" for r in data.itertuples(index=False)], loc="lower center", bbox_to_anchor=(0.5, -0.18), frameon=False, fontsize=7.2, ncol=1)
    top = class_summary.head(8).sort_values("area_ha", ascending=True)
    ax_bar.barh(top["class_label"], top["area_ha"], color=[GROUP_STYLE[g]["color"] for g in top["landuse_group"]], edgecolor="#ffffff", linewidth=0.5)
    ax_bar.set_title("原始小类面积 Top 8", loc="left", fontsize=13.5, fontweight="bold", color=INK)
    ax_bar.set_xlabel("ha", fontsize=8.5, color=MUTED)
    ax_bar.tick_params(axis="both", labelsize=7.8, colors=MUTED)
    ax_bar.grid(axis="x", color=GRID, linewidth=0.6, alpha=0.7)
    ax_bar.spines["top"].set_visible(False)
    ax_bar.spines["right"].set_visible(False)
    ax_bar.spines["left"].set_visible(False)
    ax_bar.spines["bottom"].set_color(GRID)
    fig.text(0.012, 0.018, source_note, fontsize=8.5, color=MUTED)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor=BACKGROUND)
    plt.close(fig)
    return basemap_info


def draw_mapping_chart(class_summary: pd.DataFrame, output_path: Path) -> None:
    """Make the raw-class to report-group transformation visible in the report package."""
    data = class_summary.sort_values(["landuse_group", "area_ha"], ascending=[True, False]).copy()
    height = max(6.6, 1.35 + len(data) * 0.38)
    fig, ax = plt.subplots(figsize=(13.5, height), facecolor=BACKGROUND)
    ax.axis("off")
    ax.set_title("原始用地分类到报告大类的归并说明", loc="left", fontsize=19, fontweight="bold", color=INK, pad=18)
    ax.text(
        0.0,
        1.005,
        "原始字段值保留在左侧；报告大类依据默认关键词规则归并，面积按行政区裁剪后的几何重新计算。",
        transform=ax.transAxes,
        fontsize=9.5,
        color=MUTED,
        va="bottom",
    )
    table_data = [["原始字段值", "原始分类说明", "报告大类", "归并依据", "斑块数", "面积（公顷）", "占比"]]
    for row in data.itertuples(index=False):
        table_data.append(
            [
                str(row.class_norm),
                str(row.class_label),
                str(row.landuse_group),
                str(row.mapping_rule),
                f"{int(row.feature_count):,}",
                f"{row.area_ha:,.1f}",
                f"{row.area_pct:.1f}%",
            ]
        )
    table = ax.table(
        cellText=table_data,
        colWidths=[0.16, 0.16, 0.19, 0.23, 0.09, 0.11, 0.07],
        cellLoc="left",
        bbox=[0.0, 0.02, 1.0, 0.91],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8.6)
    for (row_idx, col_idx), cell in table.get_celld().items():
        cell.set_edgecolor("#dedbd0")
        cell.set_linewidth(0.55)
        cell.PAD = 0.018
        if row_idx == 0:
            cell.set_facecolor("#d9ddd4")
            cell.set_text_props(color=INK, weight="bold")
        else:
            cell.set_facecolor("#fffdf7" if row_idx % 2 else "#f2f1eb")
            cell.set_text_props(color=INK)
            if col_idx == 2:
                group = str(data.iloc[row_idx - 1]["landuse_group"])
                cell.set_facecolor(GROUP_STYLE.get(group, GROUP_STYLE["其他"])["color"])
    fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor=BACKGROUND)
    plt.close(fig)


def make_contact_sheet(image_paths: list[Path], output_path: Path) -> None:
    tile_w, tile_h = 760, 560
    label_h = 42
    cols = 2
    rows = math.ceil(len(image_paths) / cols)
    sheet = Image.new("RGB", (cols * tile_w, rows * (tile_h + label_h)), BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("msyh.ttc", 20)
    except Exception:
        font = ImageFont.load_default()
    for idx, path in enumerate(image_paths):
        image = Image.open(path).convert("RGB")
        image.thumbnail((tile_w - 36, tile_h - 32), Image.Resampling.LANCZOS)
        col = idx % cols
        row = idx // cols
        x = col * tile_w + (tile_w - image.width) // 2
        y = row * (tile_h + label_h) + 18
        sheet.paste(image, (x, y))
        draw.text((col * tile_w + 22, row * (tile_h + label_h) + tile_h + 2), f"{idx + 1}. {path.name}", fill=INK, font=font)
    sheet.save(output_path, quality=95)


def write_readme(paths: dict[str, Path], manifest: dict, group_summary: pd.DataFrame, class_summary: pd.DataFrame) -> None:
    top_groups = "\n".join(f"- {r.landuse_group}: {r.area_ha:,.1f} ha ({r.area_pct:.1f}%)" for r in group_summary.sort_values("area_ha", ascending=False).itertuples(index=False))
    top_classes = "\n".join(f"- {r.class_label} (`{r.class_norm}`): {r.area_ha:,.1f} ha ({r.area_pct:.1f}%)" for r in class_summary.head(10).itertuples(index=False))
    text = f"""# Land-Use Mapping Outputs

Generated at: {manifest["created_at"]}

## Deliverables

- `maps/01_landuse_current_map.png`: current land-use map by aggregate group.
- `maps/02_landuse_raw_class_map.png`: raw-class diagnostic map.
- `charts/03_landuse_structure_donut.png`: land-use structure pie/donut chart.
- `charts/04_landuse_class_area_bar.png`: raw class area ranking.
- `charts/05_landuse_figure_group.png`: report-ready map + chart group.
- `charts/06_raw_to_report_group_mapping.png`: raw class to report group mapping explanation.
- `maps/00_contact_sheet.png`: quick visual index.
- `tables/landuse_group_summary.csv`: grouped area table.
- `tables/landuse_class_summary.csv`: raw class area table.
- `tables/landuse_class_to_group_mapping.csv`: explicit raw-to-group mapping audit table.
- `tables/landuse_plot_layer.gpkg`: rendered plot layer.

## Area Method

Source CRS: `{manifest["source_crs"]}`. Area and map rendering CRS: `{manifest["area_crs"]}`. Total mapped area: `{manifest["total_area_ha"]:,.1f}` ha.

## Administrative Selection

{manifest.get("admin_selection_note", "未使用行政区边界裁剪；地图范围来自输入数据。")}

## Basemap

{manifest.get("basemap_note", "未启用底图。")}

## Raw To Report Group Method

The source classification field is `{manifest.get("class_field") or "inferred source_tags"}`. Each raw value is kept in the raw-class table and diagnostic map. The report group is assigned by the first matching keyword in `references/classification.md`; unmatched values go to `其他`. This is a transparent descriptive aggregation, not an official planning code conversion. Replace the default mapping when an official local codebook is available.

## Group Summary

{top_groups}

## Top Raw Classes

{top_classes}
"""
    (paths["root"] / "README.md").write_text(text, encoding="utf-8")


def render(args: argparse.Namespace) -> dict:
    font = configure_fonts()
    paths = ensure_dirs(Path(args.out_dir))
    admin_boundary = Path(args.admin_boundary) if args.admin_boundary else None
    admin_names = parse_admin_names(args.admin_name)
    gdf, class_field, color_field, area_crs, admin_context = read_landuse(
        Path(args.input),
        args.class_field,
        args.color_field,
        args.area_crs,
        admin_boundary=admin_boundary,
        admin_names=admin_names,
        admin_name_field=args.admin_name_field,
        admin_parent_field=args.admin_parent_field,
        admin_parent=args.admin_parent,
    )
    class_summary, group_summary = summarize(gdf, paths, color_field)
    plot_gdf = prepare_plot_gdf(gdf, area_crs)
    admin_plot_gdf = prepare_admin_plot(admin_context, area_crs)
    plot_layer = paths["tables"] / "landuse_plot_layer.gpkg"
    plot_gdf.to_file(plot_layer, layer="landuse_groups", driver="GPKG")
    admin_layer = None
    if admin_plot_gdf is not None:
        admin_layer = paths["tables"] / "selected_admin_boundary.gpkg"
        admin_plot_gdf.to_file(admin_layer, layer="selected_admin", driver="GPKG")
    title = args.title or f"{args.study_area or Path(args.input).stem}用地现状图"
    admin_label = ""
    if admin_context:
        admin_label = "行政区：" + "、".join(admin_context["selected_names"])
    source_note = f"数据：{Path(args.input).name} | {admin_label or '未使用行政区裁剪'} | 面积/制图坐标系：{area_crs}"
    outputs = {
        "current_map": paths["maps"] / "01_landuse_current_map.png",
        "raw_class_map": paths["maps"] / "02_landuse_raw_class_map.png",
        "structure_donut": paths["charts"] / "03_landuse_structure_donut.png",
        "class_area_bar": paths["charts"] / "04_landuse_class_area_bar.png",
        "figure_group": paths["charts"] / "05_landuse_figure_group.png",
        "raw_to_report_mapping": paths["charts"] / "06_raw_to_report_group_mapping.png",
    }
    map_subtitle = "按规划报告用地大类归并渲染"
    if admin_label:
        map_subtitle += f" | {admin_label}"
    basemap_runs = []
    basemap_runs.append(draw_group_map(
        plot_gdf,
        group_summary,
        outputs["current_map"],
        title,
        map_subtitle,
        source_note,
        admin_plot_gdf,
        admin_context["name_field"] if admin_context else None,
        args.basemap,
        args.basemap_alpha,
    ))
    basemap_runs.append(draw_raw_class_map(
        plot_gdf,
        class_summary,
        outputs["raw_class_map"],
        source_note,
        admin_plot_gdf,
        admin_context["name_field"] if admin_context else None,
        args.basemap,
        args.basemap_alpha,
    ))
    draw_donut_chart(group_summary, outputs["structure_donut"])
    draw_bar_chart(class_summary, outputs["class_area_bar"])
    basemap_runs.append(draw_dashboard(
        plot_gdf,
        group_summary,
        class_summary,
        outputs["figure_group"],
        title.replace("图", "与结构分析"),
        source_note,
        admin_plot_gdf,
        admin_context["name_field"] if admin_context else None,
        args.basemap,
        args.basemap_alpha,
    ))
    draw_mapping_chart(class_summary, outputs["raw_to_report_mapping"])
    contact_sheet = paths["maps"] / "00_contact_sheet.png"
    make_contact_sheet(list(outputs.values()), contact_sheet)
    admin_selection_note = "未使用行政区边界裁剪；地图范围来自输入数据。"
    if admin_context:
        admin_selection_note = (
            f"使用 `{admin_context['path']}` 的 `{admin_context['name_field']}` 字段选择 "
            f"{', '.join(admin_context['selected_names'])}，父级条件为 "
            f"{admin_context['parent_value'] or '未指定'}；输入斑块 {admin_context.get('input_feature_count', len(gdf)):,} 个，"
            f"裁剪后保留 {admin_context.get('clipped_feature_count', len(gdf)):,} 个。"
        )
    basemap_status = "、".join(sorted({str(item.get("status")) for item in basemap_runs}))
    if args.basemap == "none":
        basemap_note = "未启用底图（`--basemap none`）。"
    else:
        basemap_note = (
            f"请求使用 CartoDB Positron No Labels 无文字浅色底图，透明度 {args.basemap_alpha:.2f}；"
            f"三张地图渲染状态：{basemap_status or '未记录'}。底图仅作位置参照，不参与面积统计。"
        )
    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "input_path": str(Path(args.input)),
        "output_dir": str(paths["root"]),
        "source_crs": str(gdf.crs),
        "area_crs": area_crs,
        "basemap": {
            "requested": args.basemap,
            "provider": "CartoDB Positron No Labels",
            "tile_url": BASEMAP_TILE_URL,
            "alpha": float(args.basemap_alpha),
            "render_runs": basemap_runs,
        },
        "bbox_wgs84": [float(v) for v in gdf.to_crs(4326).total_bounds],
        "bbox_area_crs": [float(v) for v in plot_gdf.total_bounds],
        "class_field": class_field,
        "color_field": color_field,
        "font": font,
        "feature_count": int(len(gdf)),
        "input_feature_count": int(admin_context.get("input_feature_count", len(gdf))) if admin_context else int(len(gdf)),
        "geometry_types": {str(k): int(v) for k, v in gdf.geom_type.value_counts().to_dict().items()},
        "total_area_ha": float(gdf["area_ha"].sum()),
        "total_area_km2": float(gdf["area_km2"].sum()),
        "raw_class_count": int(gdf["class_norm"].nunique()),
        "group_count": int(gdf["landuse_group"].nunique()),
        "outputs": {k: str(v) for k, v in outputs.items()},
        "contact_sheet": str(contact_sheet),
        "tables": {
            "group_summary": str(paths["tables"] / "landuse_group_summary.csv"),
            "class_summary": str(paths["tables"] / "landuse_class_summary.csv"),
            "class_to_group_mapping": str(paths["tables"] / "landuse_class_to_group_mapping.csv"),
            "plot_layer": str(plot_layer),
        },
        "admin_selection": {
            "enabled": bool(admin_context),
            "boundary_path": admin_context["path"] if admin_context else "",
            "source_crs": admin_context["source_crs"] if admin_context else "",
            "name_field": admin_context["name_field"] if admin_context else "",
            "parent_field": admin_context["parent_field"] if admin_context else "",
            "parent_value": admin_context["parent_value"] if admin_context else "",
            "requested_names": admin_context["requested_names"] if admin_context else [],
            "selected_names": admin_context["selected_names"] if admin_context else [],
            "selected_count": admin_context["selected_count"] if admin_context else 0,
            "boundary_layer": str(admin_layer) if admin_layer else "",
        },
        "admin_selection_note": admin_selection_note,
        "basemap_note": basemap_note,
        "quality_notes": [
            "Area is computed after reprojection to a local UTM metric CRS.",
            "When an administrative boundary is supplied, land-use polygons are clipped before area summaries and maps are produced.",
            "Current map uses aggregate classes for legibility; raw class map and raw-to-report mapping table are provided for audit.",
            "Maps include title, legend, scale bar, north arrow, source note, and CRS note.",
            "Maps optionally use a pale, label-free CartoDB basemap beneath land-use and administrative layers; failures fall back without blocking the package.",
            "Report groups are a transparent keyword-based descriptive aggregation and should be replaced by an official codebook when available.",
        ],
    }
    (paths["root"] / "artifact_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readme(paths, manifest, group_summary, class_summary)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a reusable planning land-use map and chart package.")
    parser.add_argument("--input", required=True, help="Input polygon spatial file: GeoJSON/GPKG/Shapefile/etc.")
    parser.add_argument("--out-dir", required=True, help="Output directory.")
    parser.add_argument("--study-area", default="", help="Study area name for titles.")
    parser.add_argument("--title", default="", help="Explicit map title.")
    parser.add_argument("--class-field", default=None, help="Classification field override.")
    parser.add_argument("--color-field", default=None, help="Source color field override.")
    parser.add_argument("--area-crs", default=None, help="Area/map CRS override, e.g. EPSG:32651.")
    parser.add_argument("--admin-boundary", default=None, help="Optional administrative boundary layer used to select and clip the study area.")
    parser.add_argument("--admin-name", action="append", default=[], help="Administrative name to select; repeat the option or provide comma-separated names.")
    parser.add_argument("--admin-name-field", default=None, help="Administrative name field override, e.g. 地名 or NAME_3.")
    parser.add_argument("--admin-parent-field", default=None, help="Parent administrative field override, e.g. 地级.")
    parser.add_argument("--admin-parent", default=None, help="Parent administrative value used to disambiguate names, e.g. 杭州市.")
    parser.add_argument("--basemap", choices=["carto-light-nolabels", "none"], default="carto-light-nolabels", help="Optional pale label-free basemap beneath report maps.")
    parser.add_argument("--basemap-alpha", type=float, default=0.38, help="Basemap opacity, recommended 0.25-0.45 for report figures.")
    args = parser.parse_args()
    manifest = render(args)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
