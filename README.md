# Logistics Facility Registry v1

A reproducible geospatial data engineering project that turns messy logistics facility records into a clean registry ready for portfolio decisions such as coverage analysis and network rationalization.

## What this repository demonstrates
- Deterministic synthetic data generation with realistic data quality issues.
- Cleaning and normalization of names, addresses, countries, and coordinates.
- Fuzzy duplicate grouping with canonical record selection.
- Optional geocoding workflow with cache-first offline behavior.
- QA/QC reporting for completeness, duplicates, and geographic checks.
- Export to analytical deliverables (CSV + GeoPackage).
- Static PDF map export using Natural Earth polygons, no web basemap.

## Synthetic data statement
All data in this repository is synthetic and generated for demonstration only.

## Outputs
Running the pipeline produces:
- `data/processed/facilities_master.csv`
- `data/processed/facilities_master.gpkg` (layer: `facilities_master`)
- `reports/qa/qa_report.md`
- `reports/qa/qa_summary.csv`
- `reports/maps/facilities_overview.pdf`

## Final schema
| Column | Meaning |
|---|---|
| facility_id | Stable deterministic ID from normalized name+address+country |
| facility_name | Facility name |
| facility_type | One of warehouse, cross-dock, parcel hub, port, airport, rail terminal |
| operator | Synthetic operator name |
| street | Street component |
| city | City component |
| state_region | State/region component |
| postal_code | Postal code |
| country_iso2 | ISO-3166 alpha-2 country code |
| address_full | Normalized single-line address |
| lat | Latitude WGS84 |
| lon | Longitude WGS84 |
| has_valid_coords | Coordinate validity flag |
| duplicate_group_id | Duplicate cluster ID or blank |
| is_canonical_record | Canonical record within duplicate group |
| geocode_method | raw_coords, cached_geocode, online_geocode, none |
| geocode_confidence | Deterministic confidence proxy 0..1 |
| source | Source label |
| updated_at | ISO date stamp |

## Reproducibility
Install dependencies and run end-to-end:

```bash
make setup
make build
```

Useful targets:
- `make qa`
- `make map`
- `make test`

Scripts can also run directly from repo root, e.g. `python scripts/01_clean_normalize.py`.

## License
MIT. See `LICENSE`.
