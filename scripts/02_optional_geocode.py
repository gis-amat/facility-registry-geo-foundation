from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import logging
import os

import pandas as pd

from facility_registry.geocode import apply_geocoding
from facility_registry.io import load_config

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")


def main() -> None:
    cfg = load_config()
    online_env = os.getenv("ENABLE_ONLINE_GEOCODE", "false").lower() in {"1", "true", "yes"}
    online_enabled = bool(cfg.get("online_geocode_enabled", False) and online_env)

    df = pd.read_csv("data/interim/cleaned_facilities.csv")
    out = apply_geocoding(df, "caches/geocoding_cache.csv", online_enabled=online_enabled)
    out.to_csv("data/interim/cleaned_facilities.csv", index=False)
    logging.info("Applied geocoding with online_enabled=%s", online_enabled)


if __name__ == "__main__":
    main()
