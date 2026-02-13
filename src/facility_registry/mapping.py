from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


def make_static_map(df: pd.DataFrame, output_path: str | Path, title: str, page_size: tuple[float, float], footer_note: str) -> None:
    canonical = df[df["is_canonical_record"] & df["has_valid_coords"]].copy()
    geometry = gpd.points_from_xy(canonical["lon"], canonical["lat"])
    gdf = gpd.GeoDataFrame(canonical, geometry=geometry, crs="EPSG:4326")

    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

    fig, ax = plt.subplots(figsize=page_size)
    world.plot(ax=ax, color="#f0f0f0", edgecolor="#999999", linewidth=0.4)

    marker_map = {
        "warehouse": "o",
        "cross-dock": "s",
        "parcel hub": "^",
        "port": "P",
        "airport": "X",
        "rail terminal": "D",
    }

    for ftype, marker in marker_map.items():
        subset = gdf[gdf["facility_type"] == ftype]
        if not subset.empty:
            subset.plot(
                ax=ax,
                markersize=20 + subset["geocode_confidence"].fillna(0) * 20,
                marker=marker,
                label=ftype,
                alpha=0.8,
            )

    ax.set_title(title)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(loc="lower left", fontsize=8, frameon=True)
    fig.text(0.01, 0.01, footer_note, fontsize=8)
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 85)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, format="pdf")
    plt.close(fig)
