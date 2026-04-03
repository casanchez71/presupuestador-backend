"""Pure utility functions for tree building and data parsing."""

from __future__ import annotations

import re

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


def normalize_item_code(value: object) -> str:
    """Normalize item codes: strip whitespace, replace comma with dot, clean up."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    raw = str(value).strip().replace(",", ".")
    raw = re.sub(r"\s+", "", raw)
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
