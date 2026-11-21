"""Compare two measurements on matched units, optionally showing a map of changes."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("csv", type=Path)
    for opt in ("id", "before", "after", "unit", "out"):
        p.add_argument("--" + opt, required=True)
    p.add_argument("--change-unit", help="Unit for differences, e.g. percentage points")
    p.add_argument("--labels", nargs=2, metavar=("A", "B"))
    p.add_argument("--geo", help="Polygon layer with one geometry per unit")
    p.add_argument("--geo-id", help="Geometry join column, defaults to --id")
    p.add_argument("--crs", help="Projected display CRS for the study area")
    p.add_argument("--intensive", action="store_true",
                   help="Values are comparable rates, shares or intensities suitable for polygon fills")
    return p.parse_args()


def main():
    a = parse_args()
    df = pd.read_csv(a.csv, dtype={a.id: "string"}, keep_default_na=False)
    if df.empty or not df[a.id].is_unique or df[a.id].str.strip().eq("").any():
        raise ValueError("Expected a nonempty table with unique nonblank IDs")
    before = pd.to_numeric(df[a.before], errors="raise")
    after = pd.to_numeric(df[a.after], errors="raise")
    values = np.column_stack((before, after))
    if not np.isfinite(values).all():
        raise ValueError("Resolve missing or non-finite pairs, and report exclusions")
    change = after - before
    delta_unit = a.change_unit or a.unit
    names = a.labels or [a.before, a.after]
    plt.rcParams.update({"svg.fonttype": "none", "pdf.fonttype": 42,
                         "font.sans-serif": ["Arial", "Microsoft YaHei", "Noto Sans CJK SC", "DejaVu Sans"],
                         "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    geo = None
    if a.geo:
        import geopandas as gpd
        if not a.intensive:
            raise ValueError("Map fills require comparable intensive values. Use the chart-only mode for totals.")
        geo = gpd.read_file(a.geo)
        key = a.geo_id or a.id
        geo[key] = geo[key].astype("string")
        if geo.crs is None or geo.geometry.is_empty.any() or geo.geometry.isna().any():
            raise ValueError("All map units need a geometry and a defined CRS")
        if not geo.geom_type.isin(["Polygon", "MultiPolygon"]).all():
            raise ValueError("Expected polygon geometries")
        if not geo[key].is_unique or set(geo[key]) != set(df[a.id]):
            raise ValueError("Map and table need exactly the same unique IDs (preserve leading zeros)")
        if a.crs:
            geo = geo.to_crs(a.crs)
        if not geo.crs.is_projected:
            raise ValueError("Supply --crs with a projected display CRS appropriate to the study area")
        geo = geo.set_index(key).loc[df[a.id]].copy()
        geo["paired_change"] = change.to_numpy()
    if geo is not None:
        fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.6), layout="constrained",
                                 gridspec_kw={"width_ratios": [1.25, 1, 1]})
        m = axes[0]
        limit = float(change.abs().max())
        if limit:
            geo.plot(column="paired_change", ax=m, cmap="BrBG",
                     norm=TwoSlopeNorm(0, -limit, limit), linewidth=.45, edgecolor="#777777",
                     legend=True, legend_kwds={"orientation":"horizontal","shrink":.8,"label":delta_unit})
        else:
            geo.plot(ax=m, color="#ededed", linewidth=.45, edgecolor="#777777")
            m.text(.5, -.04, "All changes = 0 " + delta_unit, ha="center", transform=m.transAxes)
        m.set_title(f"{names[1]} − {names[0]} ({delta_unit})")
        m.set_axis_off()
    else:
        fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.5), layout="constrained")
    scatter, distribution = axes[-2:]
    lo, hi = np.min(values), np.max(values)
    padding = .06 * (hi - lo) if hi > lo else max(abs(lo)*.02, 1)
    bounds = (lo - padding, hi + padding)
    scatter.plot(bounds, bounds, ls="--", lw=.9, color="#7d8a85", zorder=0)
    scatter.scatter(before, after, s=18, color="#236457", alpha=.72)
    scatter.set(xlim=bounds, ylim=bounds, aspect="equal", xlabel=f"{names[0]} ({a.unit})",
                ylabel=f"{names[1]} ({a.unit})", title=f"Matched observations  ·  n = {len(df)}")
    scatter.xaxis.set_major_locator(MaxNLocator(5))
    scatter.yaxis.set_major_locator(MaxNLocator(5))
    ordered = np.sort(change)
    probability = np.arange(1, len(df)+1)/len(df)
    distribution.axvline(0, color="#7d8a85", ls="--", lw=.9)
    # Draw the right-continuous empirical CDF through both endpoints.
    margin = max(float(np.ptp(ordered)), abs(float(ordered[-1]))*.02, 1e-9)*.06
    left, right = min(float(ordered[0]),0)-margin, max(float(ordered[-1]),0)+margin
    distribution.step(np.r_[left,ordered,right], np.r_[0,probability,1], where="post",
                      color="#236457", lw=1.7)
    distribution.set(xlim=(left,right), ylim=(-.02,1.02), xlabel=f"{names[1]} − {names[0]} ({delta_unit})",
                     ylabel="Cumulative share", title="Distribution of paired changes")
    output = Path(a.out)
    output.mkdir(parents=True, exist_ok=True)
    for ext in ("svg","pdf","png"):
        fig.savefig(output / f"paired-change.{ext}", dpi=320)
    plt.close(fig)
    print(f"Rendered {len(df)} complete pairs" + (f", display CRS {geo.crs}" if geo is not None else ""))


if __name__ == "__main__":
    main()
