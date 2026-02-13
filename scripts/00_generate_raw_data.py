from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from facility_registry.io import load_config

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")


def main() -> None:
    cfg = load_config()
    rng = np.random.default_rng(cfg["random_seed"])

    countries = [
        ("United States", "US", ["California", "Texas", "Illinois"], ["Los Verdes", "Northgate", "Mason"]),
        ("Deutschland", "DE", ["Bavaria", "Hesse", "Saxony"], ["Rheinhafen", "Nordstadt", "Kalten"]),
        ("United Kingdom", "GB", ["England", "Scotland", "Wales"], ["Avonford", "Dunmere", "Carden"]),
        ("Brazil", "BR", ["Sao Paulo", "Rio Grande do Sul", "Bahia"], ["Porto Claro", "Nova Leste", "Sertao Azul"]),
        ("Japan", "JP", ["Kansai", "Kanto", "Chubu"], ["Aokawa", "Midori", "Hinode"]),
        ("South Africa", "ZA", ["Gauteng", "Western Cape", "KwaZulu-Natal"], ["New Umber", "Cape Meridian", "Zulu Point"]),
        ("Australia", "AU", ["New South Wales", "Victoria", "Queensland"], ["Redgum", "Bluehaven", "Coral Reach"]),
        ("Mexico", "MX", ["Jalisco", "Nuevo Leon", "Puebla"], ["Valle Luna", "Monte Rio", "Piedra Alta"]),
    ]
    facility_types = ["warehouse", "cross-dock", "parcel hub", "port", "airport", "rail terminal"]
    operators = ["Asteron Logistics", "Nimbus Freight", "Kiteway Cargo", "Granite Loop Transport"]
    streets = ["Axis", "Harbor", "Summit", "Transit", "Vector", "Delta", "Foundry", "Canal"]

    records: list[dict[str, object]] = []
    for i in range(230):
        country_name, _, states, cities = countries[i % len(countries)]
        city = rng.choice(cities)
        state = rng.choice(states)
        ftype = rng.choice(facility_types)
        operator = rng.choice(operators)
        street_num = int(rng.integers(10, 9999))
        street_name = f"{street_num} {rng.choice(streets)} Rd"
        postal = str(int(rng.integers(10000, 99999)))
        lat = float(rng.uniform(-35, 55))
        lon = float(rng.uniform(-125, 145))

        if rng.random() < 0.10:
            lat_val = ""
            lon_val = ""
        elif rng.random() < 0.12:
            lat_val = f"{lat:.4f}".replace(".", ",")
            lon_val = f"{lon:.4f}".replace(".", ",")
        elif rng.random() < 0.06:
            lat_val = f"{lon:.4f}"
            lon_val = f"{lat:.4f}"
        else:
            lat_val = f"{lat:.5f}"
            lon_val = f"{lon:.5f}"

        country_variant = rng.choice(
            [country_name, country_name.upper(), country_name.lower(), {"United States": "USA", "Deutschland": "Germany", "United Kingdom": "UK", "Brazil": "Brasil", "Japan": "Nippon", "Mexico": "MX", "South Africa": "ZA", "Australia": "AU"}.get(country_name, country_name)]
        )

        rec = {
            rng.choice(["FacilityName", "facility_name", "Name"]): f"{city} {ftype.title()} {i % 40}",
            rng.choice(["FacilityType", "facility_type"]): ftype,
            "Operator": operator,
            rng.choice(["street", "Street_Address", "Address"]): f" {street_name} ",
            "City": f" {city} ",
            rng.choice(["State", "state_region", "Region"]): state,
            rng.choice(["postal_code", "Postal", "ZIP"]): postal,
            rng.choice(["Country", "country_name", "COUNTRY"]): country_variant,
            rng.choice(["lat", "Latitude"]): lat_val,
            rng.choice(["lon", "Lng", "Longitude"]): lon_val,
            "source": "synthetic_v1",
        }
        records.append(rec)

    df = pd.DataFrame(records)
    df = df.reindex(sorted(df.columns), axis=1)

    dup_idx = rng.choice(df.index, size=20, replace=False)
    dupes = df.loc[dup_idx].copy()
    near_dupes = df.loc[rng.choice(df.index, size=10, replace=False)].copy()
    if "City" in near_dupes.columns:
        near_dupes["City"] = near_dupes["City"].astype(str).str.strip() + "  "
    if "FacilityName" in near_dupes.columns:
        near_dupes["FacilityName"] = near_dupes["FacilityName"].astype(str).str.replace(" ", "-", regex=False)

    out = pd.concat([df, dupes, near_dupes], ignore_index=True)
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    out.to_csv("data/raw/facilities_raw.csv", index=False)
    logging.info("Generated raw dataset with %s rows", len(out))


if __name__ == "__main__":
    main()
