from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from facility_registry import REQUIRED_SCHEMA


def export_outputs(df: pd.DataFrame, csv_path: str | Path, gpkg_path: str | Path, layer_name: str, crs: str) -> None:
    csv_path = Path(csv_path)
    gpkg_path = Path(gpkg_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    gpkg_path.parent.mkdir(parents=True, exist_ok=True)

    output = df[REQUIRED_SCHEMA].copy()
    output.to_csv(csv_path, index=False)

    geometry = [Point(xy) if pd.notna(xy[0]) and pd.notna(xy[1]) else None for xy in zip(output["lon"], output["lat"])]
    gdf = gpd.GeoDataFrame(output, geometry=geometry, crs=crs)
    gdf.to_file(gpkg_path, layer=layer_name, driver="GPKG")
