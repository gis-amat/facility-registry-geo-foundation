from __future__ import annotations

from collections import defaultdict

import pandas as pd
from rapidfuzz import fuzz


def _completeness_score(row: pd.Series) -> int:
    cols = ["street", "city", "state_region", "postal_code", "country_iso2", "operator"]
    return sum(1 for col in cols if str(row.get(col, "")).strip() != "")


def deduplicate(df: pd.DataFrame, thresholds: dict[str, float]) -> pd.DataFrame:
    df = df.copy()
    parent = list(range(len(df)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    group_cols = ["country_iso2", "city"]
    grouped = df.groupby(group_cols, dropna=False).groups

    for _, idx in grouped.items():
        indices = list(idx)
        for i, ai in enumerate(indices):
            for bi in indices[i + 1 :]:
                a = df.loc[ai]
                b = df.loc[bi]
                n_score = fuzz.token_sort_ratio(str(a["facility_name"]), str(b["facility_name"]))
                ad_score = fuzz.token_sort_ratio(str(a["address_full"]), str(b["address_full"]))
                combined = (n_score + ad_score) / 2
                if (
                    n_score >= thresholds["name_similarity"]
                    and ad_score >= thresholds["address_similarity"]
                    and combined >= thresholds["combined_similarity"]
                ):
                    union(ai, bi)

    groups: dict[int, list[int]] = defaultdict(list)
    for i in range(len(df)):
        groups[find(i)].append(i)

    df["duplicate_group_id"] = ""
    df["is_canonical_record"] = True
    gid = 1
    for members in groups.values():
        if len(members) <= 1:
            continue
        label = f"DG-{gid:04d}"
        gid += 1
        subset = df.loc[members].copy()
        subset["completeness"] = subset.apply(_completeness_score, axis=1)
        subset = subset.sort_values(
            by=["completeness", "has_valid_coords", "facility_id"],
            ascending=[False, False, True],
        )
        canonical_idx = subset.index[0]
        df.loc[members, "duplicate_group_id"] = label
        df.loc[members, "is_canonical_record"] = False
        df.loc[canonical_idx, "is_canonical_record"] = True

    return df
