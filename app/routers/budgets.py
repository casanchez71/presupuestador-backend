from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException

from app.auth import get_current_user
from app.calculations import calc_budget_summary, calc_item_totals, recalc_all_items
from app.db import get_data_db
from app.schemas import BudgetCopyRequest, BudgetCreate, BudgetItemCreate, BudgetItemUpdate
from app.tree import build_tree

router = APIRouter()


def _get_items(budget_id: str, org_id: str) -> list[dict]:
    db = get_data_db()
    result = (
        db.table("budget_items")
        .select("*")
        .eq("budget_id", budget_id)
        .eq("org_id", org_id)
        .order("sort_order")
        .execute()
    )
    return result.data or []


# ── CRUD presupuestos ────────────────────────────────────────────────────────


@router.post("")
async def create_budget(budget: BudgetCreate, user: dict = Depends(get_current_user)):
    db = get_data_db()
    result = db.table("budgets").insert({
        "org_id": user["org_id"],
        "name": budget.name,
        "description": budget.description,
        "status": "draft",
    }).execute()
    return result.data[0]


@router.get("")
async def list_budgets(user: dict = Depends(get_current_user)):
    db = get_data_db()
    result = (
        db.table("budgets")
        .select("*")
        .eq("org_id", user["org_id"])
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


@router.get("/{budget_id}")
async def get_budget(budget_id: UUID, user: dict = Depends(get_current_user)):
    db = get_data_db()
    result = (
        db.table("budgets")
        .select("*")
        .eq("id", str(budget_id))
        .eq("org_id", user["org_id"])
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(404, "Presupuesto no encontrado")
    return result.data


@router.delete("/{budget_id}")
async def delete_budget(budget_id: UUID, user: dict = Depends(get_current_user)):
    db = get_data_db()
    result = (
        db.table("budgets")
        .delete()
        .eq("id", str(budget_id))
        .eq("org_id", user["org_id"])
        .execute()
    )
    return {"deleted": bool(result.data)}


# ── Items ────────────────────────────────────────────────────────────────────


@router.post("/{budget_id}/items")
async def create_items(
    budget_id: UUID,
    items: list[BudgetItemCreate],
    user: dict = Depends(get_current_user),
):
    db = get_data_db()
    to_insert = []
    for i, item in enumerate(items):
        raw = {
            "budget_id": str(budget_id),
            "org_id": user["org_id"],
            "parent_id": str(item.parent_id) if item.parent_id else None,
            "code": item.code,
            "description": item.description,
            "unidad": item.unidad,
            "cantidad": item.cantidad,
            "mat_unitario": item.mat_unitario or 0,
            "mo_unitario": item.mo_unitario or 0,
            "indirecto_total": item.indirecto_total or 0,
            "beneficio_total": item.beneficio_total or 0,
            "notas": item.notas,
            "sort_order": i,
        }
        calculated = calc_item_totals(raw)
        to_insert.append(calculated)
    result = db.table("budget_items").insert(to_insert).execute()
    return {"inserted": len(result.data)}


@router.patch("/{budget_id}/items/{item_id}")
async def update_item(
    budget_id: UUID,
    item_id: UUID,
    payload: BudgetItemUpdate,
    user: dict = Depends(get_current_user),
):
    db = get_data_db()
    org_id = user["org_id"]
    bid = str(budget_id)
    iid = str(item_id)

    existing = (
        db.table("budget_items")
        .select("*")
        .eq("id", iid)
        .eq("budget_id", bid)
        .eq("org_id", org_id)
        .single()
        .execute()
    )
    if not existing.data:
        raise HTTPException(404, "Item no encontrado")

    update_data = payload.model_dump(exclude_unset=True)
    if "parent_id" in update_data:
        v = update_data["parent_id"]
        update_data["parent_id"] = str(v) if v else None

    # Merge existing data with updates, then recalculate totals
    merged = {**existing.data, **update_data}
    recalculated = calc_item_totals(merged)

    # Extract only the cost fields that were recalculated
    cost_fields = ("mat_total", "mo_total", "directo_total", "neto_total")
    for field in cost_fields:
        update_data[field] = recalculated[field]
    # Also ensure indirecto_total and beneficio_total are rounded
    if "indirecto_total" in update_data:
        update_data["indirecto_total"] = recalculated["indirecto_total"]
    if "beneficio_total" in update_data:
        update_data["beneficio_total"] = recalculated["beneficio_total"]

    changes = {}
    for field, new_val in update_data.items():
        old_val = existing.data.get(field)
        if old_val != new_val:
            changes[field] = {"before": old_val, "after": new_val}

    if not changes:
        return {"message": "Sin cambios", "item": existing.data}

    db.table("budget_items").update(update_data).eq("id", iid).execute()

    updated = (
        db.table("budget_items")
        .select("*")
        .eq("id", iid)
        .single()
        .execute()
    )

    db.table("audit_logs").insert({
        "org_id": org_id,
        "user_id": user["user_id"],
        "budget_id": bid,
        "item_id": iid,
        "action": "update",
        "changes": changes,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }).execute()

    return {"message": "Item actualizado", "item": updated.data}


# ── Tree ─────────────────────────────────────────────────────────────────────


@router.get("/{budget_id}/tree")
async def get_tree(budget_id: UUID, user: dict = Depends(get_current_user)):
    items = _get_items(str(budget_id), user["org_id"])
    return {"budget_id": str(budget_id), "tree": build_tree(items)}


@router.get("/{budget_id}/full")
async def get_budget_full(budget_id: UUID, user: dict = Depends(get_current_user)):
    db = get_data_db()
    bid = str(budget_id)
    org_id = user["org_id"]

    budget = (
        db.table("budgets")
        .select("*")
        .eq("id", bid)
        .eq("org_id", org_id)
        .single()
        .execute()
    )
    if not budget.data:
        raise HTTPException(404, "Presupuesto no encontrado")

    items = _get_items(bid, org_id)
    tree = build_tree(items)
    analysis = calc_budget_summary(items)

    versions = (
        db.table("budget_versions")
        .select("id")
        .eq("budget_id", bid)
        .eq("org_id", org_id)
        .execute()
    )

    return {
        "budget": budget.data,
        "tree": tree,
        "analysis": analysis,
        "versions_count": len(versions.data or []),
    }


# ── Recalculate ─────────────────────────────────────────────────────────────


@router.post("/{budget_id}/recalculate")
async def recalculate_budget(
    budget_id: UUID,
    user: dict = Depends(get_current_user),
):
    """Recalculate all item totals in a budget.

    Useful after bulk imports or price changes.
    """
    db = get_data_db()
    org_id = user["org_id"]
    bid = str(budget_id)

    items = _get_items(bid, org_id)
    if not items:
        raise HTTPException(404, "Presupuesto sin items")

    recalculated = recalc_all_items(items)

    cost_fields = (
        "mat_total", "mo_total", "directo_total",
        "indirecto_total", "beneficio_total", "neto_total",
    )
    updated_count = 0
    for original, recalc in zip(items, recalculated):
        patch = {f: recalc[f] for f in cost_fields if original.get(f) != recalc[f]}
        if patch:
            db.table("budget_items").update(patch).eq("id", original["id"]).execute()
            updated_count += 1

    summary = calc_budget_summary(recalculated)

    return {
        "items_total": len(items),
        "items_updated": updated_count,
        "summary": summary,
    }


# ── Copy ───────────────────────────────────────────────────────────────────


@router.post("/{budget_id}/copy")
async def copy_budget(
    budget_id: UUID,
    payload: BudgetCopyRequest = Body(default=BudgetCopyRequest()),
    user: dict = Depends(get_current_user),
):
    """Create a complete copy of a budget including all items and resources."""
    db = get_data_db()
    org_id = user["org_id"]
    bid = str(budget_id)

    # Fetch original budget
    original = (
        db.table("budgets")
        .select("*")
        .eq("id", bid)
        .eq("org_id", org_id)
        .single()
        .execute()
    )
    if not original.data:
        raise HTTPException(404, "Presupuesto no encontrado")

    # Create new budget
    original_name = original.data.get("name") or "Presupuesto"
    new_name = payload.name or f"{original_name} (copia)"

    new_budget = db.table("budgets").insert({
        "org_id": org_id,
        "name": new_name,
        "description": original.data.get("description"),
        "source_file": original.data.get("source_file"),
        "status": "draft",
    }).execute()
    new_budget_id = new_budget.data[0]["id"]

    # Copy items, mapping old parent_id -> new parent_id
    items = _get_items(bid, org_id)
    old_to_new_id: dict[str, str] = {}

    for item in items:
        old_id = item["id"]
        old_parent_id = item.get("parent_id")

        new_item = {
            "budget_id": new_budget_id,
            "org_id": org_id,
            "parent_id": old_to_new_id.get(old_parent_id) if old_parent_id else None,
            "code": item.get("code"),
            "description": item.get("description"),
            "unidad": item.get("unidad"),
            "cantidad": item.get("cantidad"),
            "mat_unitario": item.get("mat_unitario") or 0,
            "mo_unitario": item.get("mo_unitario") or 0,
            "mat_total": item.get("mat_total") or 0,
            "mo_total": item.get("mo_total") or 0,
            "directo_total": item.get("directo_total") or 0,
            "indirecto_total": item.get("indirecto_total") or 0,
            "beneficio_total": item.get("beneficio_total") or 0,
            "neto_total": item.get("neto_total") or 0,
            "notas": item.get("notas"),
            "sort_order": item.get("sort_order") or 0,
        }
        result = db.table("budget_items").insert(new_item).execute()
        new_id = result.data[0]["id"]
        old_to_new_id[old_id] = new_id

    # Copy item_resources for each item
    resources_copied = 0
    for old_item_id, new_item_id in old_to_new_id.items():
        resources = (
            db.table("item_resources")
            .select("*")
            .eq("item_id", old_item_id)
            .eq("org_id", org_id)
            .execute()
        )
        if not resources.data:
            continue

        for res in resources.data:
            new_res = {
                "item_id": new_item_id,
                "org_id": org_id,
                "tipo": res.get("tipo"),
                "codigo": res.get("codigo"),
                "descripcion": res.get("descripcion"),
                "unidad": res.get("unidad"),
                "cantidad": res.get("cantidad"),
                "desperdicio_pct": res.get("desperdicio_pct"),
                "cantidad_efectiva": res.get("cantidad_efectiva"),
                "precio_unitario": res.get("precio_unitario"),
                "subtotal": res.get("subtotal"),
            }
            db.table("item_resources").insert(new_res).execute()
            resources_copied += 1

    return {
        "budget_id": new_budget_id,
        "name": new_name,
        "items_copied": len(items),
        "resources_copied": resources_copied,
    }
