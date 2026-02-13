from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import logging
from pathlib import Path

import pandas as pd

from facility_registry.dedupe import deduplicate
from facility_registry.io import load_config
from facility_registry.normalize import normalize_dataframe

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")


def main() -> None:
    cfg = load_config()
    raw = pd.read_csv("data/raw/facilities_raw.csv")
    cleaned, out_of_range_fixes = normalize_dataframe(raw)
    cleaned["raw_lat"] = cleaned["lat"]
    cleaned["raw_lon"] = cleaned["lon"]
    deduped = deduplicate(cleaned, cfg["dedupe_thresholds"])
    deduped["_out_of_range_fixes"] = out_of_range_fixes

    Path("data/interim").mkdir(parents=True, exist_ok=True)
    deduped.to_csv("data/interim/cleaned_facilities.csv", index=False)
    logging.info("Wrote cleaned dataset to data/interim/cleaned_facilities.csv")


if __name__ == "__main__":
    main()
