from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import logging
from datetime import date

import pandas as pd

from facility_registry import REQUIRED_SCHEMA
from facility_registry.export import export_outputs
from facility_registry.io import load_config

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")


def main() -> None:
    cfg = load_config()
    df = pd.read_csv("data/interim/cleaned_facilities.csv")
    df["updated_at"] = date.today().isoformat()

    missing = [c for c in REQUIRED_SCHEMA if c not in df.columns]
    for col in missing:
        if col in {"duplicate_group_id"}:
            df[col] = ""
        elif col in {"is_canonical_record", "has_valid_coords"}:
            df[col] = False
        elif col in {"geocode_confidence", "lat", "lon"}:
            df[col] = 0.0
        else:
            df[col] = ""

    export_outputs(
        df,
        "data/processed/facilities_master.csv",
        "data/processed/facilities_master.gpkg",
        layer_name=cfg["gpkg_layer_name"],
        crs=cfg["crs_output"],
    )
    logging.info("Exported processed CSV and GPKG")


if __name__ == "__main__":
    main()
