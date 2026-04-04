"""Analysis, indirect costs, and version management."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException

from app.auth import get_current_user
from app.calculations import calc_budget_summary, calc_item_totals
from app.db import get_data_db
from app.schemas import AnalysisResponse, IndirectApplyRequest, IndirectConfigUpdate, VersionCreate

router = APIRouter()


def _get_items(budget_id: str, org_id: str) -> list[dict]:
    db = get_data_db()
    return (
        db.table("budget_items")
        .select("*")
        .eq("budget_id", budget_id)
        .eq("org_id", org_id)
        .execute()
        .data or []
    )


# ── Indirect config CRUD ────────────────────────────────────────────────────


@router.get("/{budget_id}/indirects")
async def get_indirects(
    budget_id: UUID,
    user: dict = Depends(get_current_user),
):
    """Get indirect cost config for this org."""
    db = get_data_db()
    org_id = user["org_id"]
    result = (
        db.table("indirect_config")
        .select("*")
        .eq("org_id", org_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        # Return defaults
        return {
            "org_id": org_id,
            "estructura_pct": 0.15,
            "jefatura_pct": 0.08,
            "logistica_pct": 0.05,
            "herramientas_pct": 0.03,
            "beneficio_pct": 0.10,
        }
    return result.data[0]


@router.patch("/{budget_id}/indirects")
async def update_indirects(
    budget_id: UUID,
    payload: IndirectConfigUpdate,
    user: dict = Depends(get_current_user),
):
    """Update indirect cost percentages (upsert)."""
    db = get_data_db()
    org_id = user["org_id"]

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(400, "No hay campos para actualizar")

    existing = (
        db.table("indirect_config")
        .select("id")
        .eq("org_id", org_id)
        .limit(1)
        .execute()
    )

    if existing.data:
        result = (
            db.table("indirect_config")
            .update(update_data)
            .eq("org_id", org_id)
            .execute()
        )
    else:
        result = (
            db.table("indirect_config")
            .insert({"org_id": org_id, **update_data})
            .execute()
        )

    return result.data[0] if result.data else update_data


# ── Indirect costs (apply) ──────────────────────────────────────────────────


@router.post("/{budget_id}/indirects")
async def apply_indirects(
    budget_id: UUID,
    request: IndirectApplyRequest = Body(default=IndirectApplyRequest()),
    user: dict = Depends(get_current_user),
):
    """Apply indirect cost percentages to all items in a budget."""
    db = get_data_db()
    org_id = user["org_id"]
    bid = str(budget_id)

    # Get indirect config
    q = db.table("indirect_config").select("*").eq("org_id", org_id)
    if request.config_id:
        q = q.eq("id", str(request.config_id))
    config_result = q.limit(1).execute()
    if not config_result.data:
        raise HTTPException(404, "Configuracion de indirectos no encontrada")
    config = config_result.data[0]

    items = _get_items(bid, org_id)
    if not items:
        raise HTTPException(404, "Presupuesto sin items")

    pct_total = sum([
        config.get("estructura_pct") or 0,
        config.get("jefatura_pct") or 0,
        config.get("logistica_pct") or 0,
        config.get("herramientas_pct") or 0,
        config.get("beneficio_pct") or 0,
    ])

    total_directo = sum(i.get("directo_total") or 0 for i in items)

    # Build batch of updates — set indirecto_total, then recalculate neto_total
    updates = []
    for item in items:
        directo = item.get("directo_total") or 0
        indirecto = round(directo * pct_total, 2)
        # Merge the new indirecto_total into the item and recalculate
        merged = {**item, "indirecto_total": indirecto}
        recalculated = calc_item_totals(merged)
        updates.append({
            "id": item["id"],
            "indirecto_total": recalculated["indirecto_total"],
            "neto_total": recalculated["neto_total"],
        })

    # Update in batches (Supabase doesn't support bulk UPDATE, so we batch)
    for upd in updates:
        item_id = upd.pop("id")
        db.table("budget_items").update(upd).eq("id", item_id).execute()

    total_indirecto = sum(u.get("indirecto_total", 0) for u in updates)

    return {
        "total_directo": total_directo,
        "total_indirectos": round(total_indirecto, 2),
        "pct_applied": pct_total,
        "items_updated": len(updates),
        "config_id": config["id"],
    }


# ── Analysis ─────────────────────────────────────────────────────────────────


@router.get("/{budget_id}/analysis", response_model=AnalysisResponse)
async def get_analysis(
    budget_id: UUID,
    user: dict = Depends(get_current_user),
):
    """Get cost analysis with MAT/MO/Indirect/Benefit breakdown."""
    items = _get_items(str(budget_id), user["org_id"])
    if not items:
        raise HTTPException(404, "Presupuesto vacio o sin acceso")

    summary = calc_budget_summary(items)
    return AnalysisResponse(budget_id=str(budget_id), **summary)


# ── Versions ─────────────────────────────────────────────────────────────────


@router.post("/{budget_id}/versions")
async def create_version(
    budget_id: UUID,
    version: VersionCreate = Body(...),
    user: dict = Depends(get_current_user),
):
    """Create a snapshot of the current budget state."""
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

    # Auto-increment version number
    existing = (
        db.table("budget_versions")
        .select("version")
        .eq("budget_id", bid)
        .order("version", desc=True)
        .limit(1)
        .execute()
    )
    next_ver = (existing.data[0]["version"] + 1) if existing.data else 1

    result = db.table("budget_versions").insert({
        "budget_id": bid,
        "org_id": org_id,
        "version": next_ver,
        "data": json.dumps({
            "budget": budget.data,
            "items": items,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "notes": version.notes,
        }),
        "created_by": user["user_id"],
    }).execute()

    return {
        "version_id": result.data[0]["id"],
        "version": next_ver,
    }


@router.get("/{budget_id}/versions")
async def list_versions(
    budget_id: UUID,
    user: dict = Depends(get_current_user),
):
    db = get_data_db()
    result = (
        db.table("budget_versions")
        .select("id, version, created_at, created_by")
        .eq("budget_id", str(budget_id))
        .eq("org_id", user["org_id"])
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


@router.get("/{budget_id}/versions/{version_id}")
async def get_version(
    budget_id: UUID,
    version_id: UUID,
    user: dict = Depends(get_current_user),
):
    db = get_data_db()
    result = (
        db.table("budget_versions")
        .select("*")
        .eq("id", str(version_id))
        .eq("budget_id", str(budget_id))
        .eq("org_id", user["org_id"])
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(404, "Version no encontrada")

    return {
        "version_id": str(version_id),
        "version": result.data["version"],
        "created_at": result.data["created_at"],
        "snapshot": json.loads(result.data["data"]),
    }
