"""Pure calculation functions for budget cost derivations.

All functions are side-effect free and operate on plain dicts.
Numeric safety is handled via safe_float from app.tree.
"""

from __future__ import annotations

from app.tree import safe_float


def _sf(value: object) -> float:
    """Return safe_float result, defaulting to 0.0 for None."""
    result = safe_float(value)
    return result if result is not None else 0.0


def calc_item_totals(item: dict) -> dict:
    """Derive calculated cost fields from an item dict.

    Expects keys: cantidad, mat_unitario, mo_unitario.
    Optionally reads: indirecto_total, beneficio_total (preserved if present).

    Returns a new dict with all original keys plus derived totals:
        mat_total, mo_total, directo_total, neto_total.
    """
    cantidad = _sf(item.get("cantidad"))
    mat_unitario = _sf(item.get("mat_unitario"))
    mo_unitario = _sf(item.get("mo_unitario"))
    indirecto_total = _sf(item.get("indirecto_total"))
    beneficio_total = _sf(item.get("beneficio_total"))

    mat_total = round(cantidad * mat_unitario, 2)
    mo_total = round(cantidad * mo_unitario, 2)
    directo_total = round(mat_total + mo_total, 2)
    neto_total = round(directo_total + indirecto_total + beneficio_total, 2)

    return {
        **item,
        "mat_total": mat_total,
        "mo_total": mo_total,
        "directo_total": directo_total,
        "indirecto_total": round(indirecto_total, 2),
        "beneficio_total": round(beneficio_total, 2),
        "neto_total": neto_total,
    }


def calc_budget_summary(items: list[dict]) -> dict:
    """Sum all items to produce budget-level totals.

    Returns a dict with keys:
        mat_total, mo_total, directo_total, indirecto_total,
        beneficio_total, neto_total, items_count.
    """
    mat_total = sum(_sf(i.get("mat_total")) for i in items)
    mo_total = sum(_sf(i.get("mo_total")) for i in items)
    directo_total = sum(_sf(i.get("directo_total")) for i in items)
    indirecto_total = sum(_sf(i.get("indirecto_total")) for i in items)
    beneficio_total = sum(_sf(i.get("beneficio_total")) for i in items)
    neto_total = sum(_sf(i.get("neto_total")) for i in items)

    return {
        "mat_total": round(mat_total, 2),
        "mo_total": round(mo_total, 2),
        "directo_total": round(directo_total, 2),
        "indirecto_total": round(indirecto_total, 2),
        "beneficio_total": round(beneficio_total, 2),
        "neto_total": round(neto_total, 2),
        "items_count": len(items),
    }


def recalc_all_items(items: list[dict]) -> list[dict]:
    """Recalculate totals for every item in a list.

    Returns a new list with derived fields updated.
    """
    return [calc_item_totals(item) for item in items]
