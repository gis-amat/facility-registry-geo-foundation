from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def apply_geocoding(
    df: pd.DataFrame,
    cache_path: str | Path,
    online_enabled: bool = False,
) -> pd.DataFrame:
    df = df.copy()
    cache = pd.read_csv(cache_path)
    cache["cache_key"] = (
        cache["address_full"].fillna("").str.lower().str.strip()
        + "|"
        + cache["country_iso2"].fillna("").str.upper().str.strip()
    )
    cache_map = cache.set_index("cache_key")

    df["geocode_method"] = "none"
    df["geocode_confidence"] = 0.0

    raw_mask = df["has_valid_coords"]
    df.loc[raw_mask, "geocode_method"] = "raw_coords"
    df.loc[raw_mask, "geocode_confidence"] = 0.90

    missing = ~df["has_valid_coords"]
    keys = df["address_full"].fillna("").str.lower().str.strip() + "|" + df["country_iso2"].fillna("").str.upper().str.strip()

    for idx in df[missing].index:
        key = keys.loc[idx]
        if key in cache_map.index:
            c = cache_map.loc[key]
            df.at[idx, "lat"] = float(c["lat"])
            df.at[idx, "lon"] = float(c["lon"])
            df.at[idx, "has_valid_coords"] = True
            df.at[idx, "geocode_method"] = "cached_geocode"
            df.at[idx, "geocode_confidence"] = float(c["geocode_confidence"])
        elif online_enabled:
            df.at[idx, "geocode_method"] = "online_geocode"
            df.at[idx, "geocode_confidence"] = 0.80

    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    invalid = df["lat"].abs().gt(90) | df["lon"].abs().gt(180)
    df.loc[invalid, ["lat", "lon"]] = np.nan
    df["has_valid_coords"] = df["lat"].notna() & df["lon"].notna()
    return df
