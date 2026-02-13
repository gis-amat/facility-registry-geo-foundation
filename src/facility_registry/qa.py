from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from facility_registry import ALLOWED_FACILITY_TYPES


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1 = np.radians(lat1)
    p2 = np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlambda / 2) ** 2
    return 2 * r * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def generate_qa(raw_df: pd.DataFrame, df: pd.DataFrame, out_of_range_fixes: int, out_dir: str | Path) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    canonical = df[df["is_canonical_record"]]
    summary_rows: list[dict[str, object]] = []
    summary_rows.append({"metric": "raw_rows", "value": len(raw_df)})
    summary_rows.append({"metric": "total_rows_processed", "value": len(df)})
    summary_rows.append({"metric": "canonical_rows", "value": len(canonical)})
    summary_rows.append({"metric": "pct_valid_coords", "value": round(df["has_valid_coords"].mean() * 100, 2)})
    summary_rows.append({"metric": "out_of_range_fixes", "value": out_of_range_fixes})

    dup_sizes = df[df["duplicate_group_id"] != ""].groupby("duplicate_group_id").size()
    summary_rows.append({"metric": "duplicate_groups", "value": int(len(dup_sizes))})

    missing = df.isna().sum()
    missing_pct = (df.isna().mean() * 100).round(2)
    for col in df.columns:
        summary_rows.append({"metric": f"missing_{col}", "value": int(missing[col]), "pct": float(missing_pct[col])})

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(out_dir / "qa_summary.csv", index=False)

    country_counts = canonical["country_iso2"].value_counts()
    top_countries = country_counts.head(10)
    other_count = int(country_counts.iloc[10:].sum())

    valid_types = set(df["facility_type"].dropna().unique())
    invalid_types = sorted(valid_types - ALLOWED_FACILITY_TYPES)

    raw_compare = df[(df["geocode_method"].isin(["cached_geocode", "online_geocode"])) & df["has_valid_coords"]]
    precision_text = "not applicable with offline cache only"
    if not raw_compare.empty and {"raw_lat", "raw_lon"}.issubset(df.columns):
        subset = raw_compare.dropna(subset=["raw_lat", "raw_lon", "lat", "lon"]).copy()
        if not subset.empty:
            subset["distance_km"] = haversine_km(subset["raw_lat"], subset["raw_lon"], subset["lat"], subset["lon"])
            precision_text = (
                f"mean={subset['distance_km'].mean():.2f} km, "
                f"median={subset['distance_km'].median():.2f} km, "
                f"p95={subset['distance_km'].quantile(0.95):.2f} km"
            )

    md = [
        "# QA/QC Report - Logistics Facility Registry v1",
        "",
        "## Row Counts",
        f"- Raw rows: {len(raw_df)}",
        f"- Processed rows: {len(df)}",
        f"- Canonical rows: {len(canonical)}",
        "",
        "## Missingness",
    ]
    for col in df.columns:
        md.append(f"- {col}: {int(missing[col])} ({missing_pct[col]:.2f}%)")

    md.extend([
        "",
        "## Duplicates",
        f"- Duplicate groups: {len(dup_sizes)}",
    ])
    if len(dup_sizes) > 0:
        md.append(f"- Group size min/median/max: {int(dup_sizes.min())}/{float(dup_sizes.median()):.1f}/{int(dup_sizes.max())}")
        md.append("- Top 10 largest groups:")
        for gid, size in dup_sizes.sort_values(ascending=False).head(10).items():
            md.append(f"  - {gid}: {int(size)}")

    md.extend([
        "",
        "## Country Coverage (canonical)",
    ])
    for country, count in top_countries.items():
        md.append(f"- {country}: {int(count)}")
    if other_count > 0:
        md.append(f"- Others: {other_count}")

    md.extend([
        "",
        "## Coordinate Validity",
        f"- Valid coordinates: {df['has_valid_coords'].mean() * 100:.2f}%",
        f"- Missing coordinates: {(~df['has_valid_coords']).mean() * 100:.2f}%",
        f"- Out-of-range fixes applied: {out_of_range_fixes}",
        "",
        "## Geocode Precision Proxy",
        f"- {precision_text}",
        "",
        "## Sanity Checks",
        f"- Lat/Lon range check passed: {bool((df['lat'].dropna().between(-90, 90) & df['lon'].dropna().between(-180, 180)).all())}",
        f"- Canonical with non-empty country_iso2: {bool((canonical['country_iso2'].str.len() == 2).all())}",
        f"- Facility type restricted to allowed set: {len(invalid_types) == 0}",
        "",
        "## Data Limitations",
        "- Data is synthetic and intended for portfolio demonstration only.",
        "- Geocoding confidence is heuristic and not survey-grade.",
        "- Duplicate detection uses fuzzy heuristics and may under/over-cluster edge cases.",
    ])

    (out_dir / "qa_report.md").write_text("\n".join(md), encoding="utf-8")
