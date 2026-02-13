from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import logging

import pandas as pd

from facility_registry.io import load_config
from facility_registry.mapping import make_static_map

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")


def main() -> None:
    cfg = load_config()
    df = pd.read_csv("data/processed/facilities_master.csv")
    map_cfg = cfg["map"]
    make_static_map(
        df,
        map_cfg["output_path"],
        map_cfg["title"],
        tuple(map_cfg["page_size"]),
        map_cfg["footer_note"],
    )
    logging.info("Generated static map PDF")


if __name__ == "__main__":
    main()
