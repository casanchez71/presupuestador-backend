from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException

from app.auth import get_current_user
from app.db import get_data_db
from app.schemas import BudgetCreate, BudgetItemCreate, BudgetItemUpdate
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
        to_insert.append({
            "budget_id": str(budget_id),
            "org_id": user["org_id"],
            "parent_id": str(item.parent_id) if item.parent_id else None,
            "code": item.code,
            "description": item.description,
            "unidad": item.unidad,
            "cantidad": item.cantidad,
            "mat_unitario": item.mat_unitario or 0,
            "mo_unitario": item.mo_unitario or 0,
            "mat_total": item.mat_total or 0,
            "mo_total": item.mo_total or 0,
            "directo_total": item.directo_total or 0,
            "indirecto_total": item.indirecto_total or 0,
            "beneficio_total": item.beneficio_total or 0,
            "neto_total": item.neto_total or 0,
            "notas": item.notas,
            "sort_order": i,
        })
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

    mat_total = sum(i.get("mat_total") or 0 for i in items)
    mo_total = sum(i.get("mo_total") or 0 for i in items)
    directo = sum(i.get("directo_total") or 0 for i in items)
    indirecto = sum(i.get("indirecto_total") or 0 for i in items)
    beneficio = sum(i.get("beneficio_total") or 0 for i in items)
    neto = sum(i.get("neto_total") or 0 for i in items)

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
        "analysis": {
            "mat_total": mat_total,
            "mo_total": mo_total,
            "directo_total": directo,
            "indirecto_total": indirecto,
            "beneficio_total": beneficio,
            "neto_total": neto,
            "items_count": len(items),
        },
        "versions_count": len(versions.data or []),
    }
