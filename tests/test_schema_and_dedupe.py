from __future__ import annotations

from pathlib import Path

import pandas as pd

from facility_registry import ALLOWED_FACILITY_TYPES, REQUIRED_SCHEMA


def _load_dataset() -> pd.DataFrame:
    path = Path("data/processed/facilities_master.csv")
    if not path.exists():
        return pd.read_csv("data/interim/cleaned_facilities.csv")
    return pd.read_csv(path)


def test_schema_columns_exact_order() -> None:
    path = Path("data/processed/facilities_master.csv")
    if path.exists():
        df = pd.read_csv(path)
        assert list(df.columns) == REQUIRED_SCHEMA


def test_facility_type_allowed() -> None:
    df = _load_dataset()
    values = set(df["facility_type"].dropna().astype(str).str.lower().unique())
    assert values.issubset(ALLOWED_FACILITY_TYPES)


def test_duplicate_groups_have_one_canonical() -> None:
    df = _load_dataset()
    groups = df[df["duplicate_group_id"].fillna("") != ""].groupby("duplicate_group_id")
    for _, g in groups:
        assert int(g["is_canonical_record"].sum()) == 1


def test_country_iso2_length_for_canonical() -> None:
    df = _load_dataset()
    canonical = df[df["is_canonical_record"]]
    assert canonical["country_iso2"].fillna("").str.len().eq(2).all()


def test_valid_coord_ranges() -> None:
    df = _load_dataset()
    valid = df[df["has_valid_coords"]]
    assert valid["lat"].between(-90, 90).all()
    assert valid["lon"].between(-180, 180).all()
