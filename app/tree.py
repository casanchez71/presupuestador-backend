"""Pure utility functions for tree building and data parsing."""

from __future__ import annotations

import re
from datetime import datetime

import pandas as pd


def build_tree(items: list[dict]) -> list[dict]:
    """Convert a flat list of items (with parent_id) into a nested tree."""
    if not items:
        return []
    item_map = {item["id"]: {**item, "children": []} for item in items}
    roots: list[dict] = []
    for item in items:
        pid = item.get("parent_id")
        if pid is None:
            roots.append(item_map[item["id"]])
        elif pid in item_map:
            item_map[pid]["children"].append(item_map[item["id"]])
    return roots


def normalize_date_code(value: object) -> str | None:
    """Convert Excel date-encoded item codes to section.item format.

    Lugones/El Encuentro Excels store codes as dates:
    day = section number, month = item within section.
    2025-01-01 -> "1.1", 2025-02-01 -> "1.2", 2025-01-02 -> "2.1"
    """
    ts = None
    if isinstance(value, pd.Timestamp):
        ts = value
    elif isinstance(value, datetime):
        ts = pd.Timestamp(value)
    elif isinstance(value, str):
        # Check if string looks like a date: "2025-01-01" or "2025-01-01 00:00:00"
        s = value.strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}", s):
            try:
                ts = pd.Timestamp(s)
            except (ValueError, OverflowError):
                return None

    if ts is None:
        return None

    section = ts.day
    item = ts.month
    return f"{section}.{item}"


def normalize_item_code(value: object) -> str:
    """Normalize item codes: handle dates, X.Y-Z format, whitespace, commas."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""

    # Try date-code conversion first (Lugones/El Encuentro format)
    date_result = normalize_date_code(value)
    if date_result is not None:
        return date_result

    raw = str(value).strip().replace(",", ".")
    raw = re.sub(r"\s+", "", raw)
    # Handle X.Y-Z format (Lugones): "3.0-1" -> "3.0.1"
    raw = re.sub(r"-(\d)", r".\1", raw)
    return raw.strip(".")


def safe_float(value: object) -> float | None:
    """Safely parse a numeric value, handling locale-specific formats."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if pd.isna(value):
            return None
        return float(value)
    cleaned = str(value).strip()
    if not cleaned:
        return None
    # Try direct parse first
    try:
        return float(cleaned)
    except ValueError:
        pass
    # Try Argentine format: dots as thousands, comma as decimal
    try:
        return float(cleaned.replace(".", "").replace(",", "."))
    except ValueError:
        return None


def get_parent_candidates(code: str) -> list[str]:
    """Given a hierarchical code like '1.2.3', return parent candidates ['1.2', '1']."""
    if not code:
        return []
    parts = [p for p in code.split(".") if p]
    if len(parts) <= 1:
        return []
    return [".".join(parts[:i]) for i in range(len(parts) - 1, 0, -1)]
