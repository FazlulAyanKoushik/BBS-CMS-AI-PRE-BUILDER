"""Parse a Japanese business CSV into a normalized JSON business profile."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import pandas as pd

from app.constants import HEADER_TO_KEY, SENSITIVE_KEYS

ENCODINGS = ["utf-8-sig", "utf-8", "cp932", "shift_jis", "latin-1"]


def read_csv_bytes(data: bytes) -> pd.DataFrame:
    """Read CSV bytes, auto-detecting the encoding (UTF-8 / Shift-JIS etc.)."""
    for enc in ENCODINGS:
        try:
            return pd.read_csv(io.BytesIO(data), encoding=enc, dtype=str)
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue
    raise ValueError("Could not decode CSV with any supported encoding")


def _clean(value: Any) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip()
    return text or None


def normalize_row(row: pd.Series) -> dict[str, Any]:
    """Map a CSV row (by Japanese header) to normalized English keys."""
    profile: dict[str, Any] = {}
    unmapped: list[str] = []
    for header in row.index:
        value = _clean(row[header])
        if value is None:
            continue
        key = HEADER_TO_KEY.get(header)
        if key is None:
            unmapped.append(header)
            continue
        profile[key] = value
    if unmapped:
        profile["_unmapped_columns"] = unmapped
    return profile


def build_profile(data: bytes, row_index: int = 0, include_raw: bool = True) -> dict[str, Any]:
    """Build a single business profile from CSV bytes.

    Args:
        data: raw CSV file bytes.
        row_index: which data row to use (headers are row 0).
        include_raw: include the full normalized row (minus secrets) as raw_profile.

    A header-only CSV (template with no data rows) is treated as a single empty
    row so the pipeline still runs and produces a generic spec.
    """
    df = read_csv_bytes(data)
    if len(df.columns) == 0:
        raise ValueError("CSV contains no columns")

    if len(df) == 0:
        profile: dict[str, Any] = {"store_name": None, "documented_columns_count": len(df.columns)}
        if include_raw:
            profile["raw_profile"] = {}
        return profile

    # Locate the requested row across the first non-NaN index, ignore empty trailing rows.
    row_idx = row_index
    if row_idx >= len(df):
        raise IndexError(f"CSV has only {len(df)} data rows (requested row {row_index})")

    row = df.iloc[row_idx]
    normalized = normalize_row(row)

    profile = {
        "store_name": normalized.get("store_name"),
        "business_type": normalized.get("business_type"),
        "phone": normalized.get("phone"),
        "website_url": normalized.get("website_url"),
        "address": " ".join(
            part
            for part in [
                normalized.get("address_prefecture") or "",
                normalized.get("address_city") or "",
                normalized.get("address_town") or "",
                normalized.get("address_street") or "",
                normalized.get("address_building") or "",
            ]
            if part
        )
        or None,
        "keywords": [
            k
            for k in [
                normalized.get("keyword_category"),
                normalized.get("keyword_service"),
                normalized.get("main_industry_service"),
                *[normalized.get(f"sub_industry_service_{i}") for i in range(1, 5)],
                normalized.get("keyword_prefecture"),
                normalized.get("keyword_city"),
                normalized.get("keyword_area_1"),
                normalized.get("keyword_area_2"),
                normalized.get("keyword_area_3"),
            ]
            if k
        ],
        "services": [
            s
            for s in [
                normalized.get("main_industry_service"),
                *[normalized.get(f"sub_industry_service_{i}") for i in range(1, 5)],
            ]
            if s
        ],
        "region": {
            "prefecture": normalized.get("keyword_prefecture") or normalized.get("address_prefecture"),
            "city": normalized.get("keyword_city") or normalized.get("address_city"),
            "areas": [a for a in [normalized.get(f"keyword_area_{i}") for i in range(1, 4)] if a],
            "language_selection": normalized.get("language_selection"),
        },
        "business_hours": normalized.get("business_hours"),
        "opening_date": normalized.get("opening_date"),
        "employees": normalized.get("employees"),
        "attributes": {
            f"attribute_{i}": normalized.get(f"attribute_{i}")
            for i in range(1, 12)
            if normalized.get(f"attribute_{i}")
        },
    }

    profile = {k: v for k, v in profile.items() if v not in (None, [], {}, "")}

    if include_raw:
        raw = {k: (None if k in SENSITIVE_KEYS else v) for k, v in normalized.items()}
        profile["raw_profile"] = raw

    return profile


def build_profiles_from_file(path: str | Path, include_raw: bool = True) -> list[dict[str, Any]]:
    """Build business profiles for every data row in a CSV file."""
    data = Path(path).read_bytes()
    df = read_csv_bytes(data)
    if len(df.columns) == 0:
        raise ValueError("CSV contains no columns")
    if len(df) == 0:
        return [build_profile(data, row_index=0, include_raw=include_raw)]
    return [build_profile(data, row_index=i, include_raw=include_raw) for i in range(len(df))]