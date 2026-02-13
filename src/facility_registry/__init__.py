"""Facility registry pipeline package."""

REQUIRED_SCHEMA = [
    "facility_id",
    "facility_name",
    "facility_type",
    "operator",
    "street",
    "city",
    "state_region",
    "postal_code",
    "country_iso2",
    "address_full",
    "lat",
    "lon",
    "has_valid_coords",
    "duplicate_group_id",
    "is_canonical_record",
    "geocode_method",
    "geocode_confidence",
    "source",
    "updated_at",
]

ALLOWED_FACILITY_TYPES = {
    "warehouse",
    "cross-dock",
    "parcel hub",
    "port",
    "airport",
    "rail terminal",
}
