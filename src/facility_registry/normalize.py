from __future__ import annotations

import hashlib
import re
from typing import Any

import numpy as np
import pandas as pd
import pycountry

COUNTRY_ALIASES = {
    "united states": "US",
    "usa": "US",
    "u.s.": "US",
    "us": "US",
    "deutschland": "DE",
    "germany": "DE",
    "federal republic of germany": "DE",
    "uk": "GB",
    "u.k.": "GB",
    "united kingdom": "GB",
    "great britain": "GB",
    "england": "GB",
    "espana": "ES",
    "spain": "ES",
    "brasil": "BR",
    "brazil": "BR",
    "nippon": "JP",
    "japan": "JP",
    "mexico": "MX",
    "canada": "CA",
    "south africa": "ZA",
    "australia": "AU",
    "france": "FR",
}

RAW_TO_STANDARD = {
    "facilityname": "facility_name",
    "facility_name": "facility_name",
    "name": "facility_name",
    "facility_type": "facility_type",
    "facilitytype": "facility_type",
    "operator": "operator",
    "street": "street",
    "street_address": "street",
    "address": "street",
    "city": "city",
    "state": "state_region",
    "state_region": "state_region",
    "region": "state_region",
    "postal_code": "postal_code",
    "postal": "postal_code",
    "zip": "postal_code",
    "country": "country",
    "country_name": "country",
    "lat": "lat",
    "latitude": "lat",
    "lon": "lon",
    "lng": "lon",
    "longitude": "lon",
    "source": "source",
}


def _canonical_col(name: str) -> str:
    token = re.sub(r"[^a-z0-9]+", "", name.strip().lower())
    return RAW_TO_STANDARD.get(token, name.strip().lower())


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {col: _canonical_col(col) for col in df.columns}
    df = df.rename(columns=renamed)
    cols = [
        "facility_name",
        "facility_type",
        "operator",
        "street",
        "city",
        "state_region",
        "postal_code",
        "country",
        "lat",
        "lon",
        "source",
    ]
    for col in cols:
        if col not in df.columns:
            df[col] = np.nan
    return df[cols].copy()


def clean_text(value: Any, lower: bool = False) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[|;]+", "", text)
    return text.lower() if lower else text


def normalize_country(country_raw: Any) -> str:
    token = clean_text(country_raw, lower=True)
    if not token:
        return ""
    if token in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[token]
    if len(token) == 2 and token.upper().isalpha():
        return token.upper()
    try:
        return pycountry.countries.lookup(token).alpha_2
    except LookupError:
        return ""


def parse_coordinate(value: Any) -> float:
    if pd.isna(value):
        return np.nan
    token = clean_text(value)
    if token == "":
        return np.nan
    token = token.replace(",", ".")
    token = re.sub(r"[^0-9.\-]", "", token)
    try:
        return float(token)
    except ValueError:
        return np.nan


def fix_coordinates(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    lat = df["lat"].apply(parse_coordinate)
    lon = df["lon"].apply(parse_coordinate)
    out_of_range_fixes = 0

    swap_mask = lat.abs().gt(90) & lon.abs().le(90)
    if swap_mask.any():
        lat2 = lat.copy()
        lat.loc[swap_mask] = lon[swap_mask]
        lon.loc[swap_mask] = lat2[swap_mask]

    invalid = lat.abs().gt(90) | lon.abs().gt(180)
    out_of_range_fixes = int(invalid.sum())
    lat.loc[invalid] = np.nan
    lon.loc[invalid] = np.nan

    df["lat"] = lat
    df["lon"] = lon
    df["has_valid_coords"] = df["lat"].notna() & df["lon"].notna()
    return df, out_of_range_fixes


def build_address_full(df: pd.DataFrame) -> pd.Series:
    parts = ["street", "city", "state_region", "postal_code", "country_iso2"]
    return df[parts].fillna("").apply(
        lambda row: ", ".join([clean_text(v) for v in row if clean_text(v)]), axis=1
    )


def make_facility_id(name: str, address: str, country_iso2: str) -> str:
    base = f"{clean_text(name, lower=True)}|{clean_text(address, lower=True)}|{country_iso2}"
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:8].upper()
    return f"FAC-{digest}"


def normalize_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    df = standardize_columns(df)
    for col in ["facility_name", "facility_type", "operator", "street", "city", "state_region", "postal_code", "source"]:
        df[col] = df[col].apply(clean_text)

    df["facility_type"] = df["facility_type"].str.lower()
    df["country_iso2"] = df["country"].apply(normalize_country)
    df, out_of_range_fixes = fix_coordinates(df)
    df["address_full"] = build_address_full(df)
    df["facility_id"] = df.apply(
        lambda r: make_facility_id(r["facility_name"], r["address_full"], r["country_iso2"]), axis=1
    )
    df["source"] = df["source"].replace("", "synthetic_v1")
    return df.drop(columns=["country"]), out_of_range_fixes
