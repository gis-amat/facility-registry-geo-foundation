from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import logging

import pandas as pd

from facility_registry.qa import generate_qa

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")


def main() -> None:
    raw = pd.read_csv("data/raw/facilities_raw.csv")
    df = pd.read_csv("data/interim/cleaned_facilities.csv")
    out_of_range_fixes = int(df.get("_out_of_range_fixes", pd.Series([0])).iloc[0])
    generate_qa(raw, df, out_of_range_fixes, "reports/qa")
    logging.info("Generated QA outputs")


if __name__ == "__main__":
    main()
