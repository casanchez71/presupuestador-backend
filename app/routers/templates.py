"""
Item template library — reusable compositions for standard construction items.
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user
from app.calculations import calc_item_from_resources
from app.db import get_data_db
from app.schemas import TemplateCreate, TemplateUpdate

router = APIRouter()


@router.get("")
async def list_templates(categoria: str = None, user: dict = Depends(get_current_user)):
    """List all templates, optionally filtered by category."""
    db = get_data_db()
    org_id = user["org_id"]
    query = db.table("item_templates").select("*").eq("org_id", org_id)
    if categoria:
        query = query.eq("categoria", categoria)
    result = query.order("categoria").execute()
    return result.data or []


@router.get("/categories")
async def list_categories(user: dict = Depends(get_current_user)):
    """List distinct categories used in templates."""
    db = get_data_db()
    org_id = user["org_id"]
    result = db.table("item_templates").select("categoria").eq("org_id", org_id).execute()
    cats = sorted(set(r["categoria"] for r in (result.data or []) if r.get("categoria")))
    return cats


@router.get("/{template_id}")
async def get_template(template_id: str, user: dict = Depends(get_current_user)):
    db = get_data_db()
    org_id = user["org_id"]
    result = (
        db.table("item_templates")
        .select("*")
        .eq("id", template_id)
        .eq("org_id", org_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(404, "Template no encontrado")
    return result.data[0]


@router.post("")
async def create_template(body: TemplateCreate, user: dict = Depends(get_current_user)):
    db = get_data_db()
    org_id = user["org_id"]
    data = {
        "org_id": org_id,
        "nombre": body.nombre,
        "descripcion": body.descripcion,
        "unidad": body.unidad,
        "categoria": body.categoria,
        "recursos": json.dumps(body.recursos) if isinstance(body.recursos, list) else body.recursos,
    }
    result = db.table("item_templates").insert(data).execute()
    if not result.data:
        raise HTTPException(500, "Error al crear template")
    return result.data[0]


@router.patch("/{template_id}")
async def update_template(
    template_id: str,
    body: TemplateUpdate,
    user: dict = Depends(get_current_user),
):
    db = get_data_db()
    org_id = user["org_id"]
    updates = body.model_dump(exclude_none=True)
    if "recursos" in updates and isinstance(updates["recursos"], list):
        updates["recursos"] = json.dumps(updates["recursos"])
    if not updates:
        raise HTTPException(400, "No hay campos para actualizar")
    result = (
        db.table("item_templates")
        .update(updates)
        .eq("id", template_id)
        .eq("org_id", org_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(404, "Template no encontrado")
    return result.data[0]


@router.delete("/{template_id}")
async def delete_template(template_id: str, user: dict = Depends(get_current_user)):
    db = get_data_db()
    org_id = user["org_id"]
    db.table("item_templates").delete().eq("id", template_id).eq("org_id", org_id).execute()
    return {"ok": True}


@router.post("/{template_id}/apply/{budget_id}/items/{item_id}")
async def apply_template(
    template_id: str,
    budget_id: str,
    item_id: str,
    user: dict = Depends(get_current_user),
):
    """Apply a template's resources to an existing budget item.

    Creates item_resources based on the template composition × item quantity.
    """
    db = get_data_db()
    org_id = user["org_id"]

    # Get template
    tmpl = (
        db.table("item_templates")
        .select("*")
        .eq("id", template_id)
        .eq("org_id", org_id)
        .execute()
    )
    if not tmpl.data:
        raise HTTPException(404, "Template no encontrado")
    template = tmpl.data[0]

    # Get item
    item_result = (
        db.table("budget_items")
        .select("*")
        .eq("id", item_id)
        .eq("budget_id", budget_id)
        .execute()
    )
    if not item_result.data:
        raise HTTPException(404, "Item no encontrado")
    item = item_result.data[0]
    qty = float(item.get("cantidad") or 1)

    # Parse recursos
    recursos = template["recursos"]
    if isinstance(recursos, str):
        recursos = json.loads(recursos)

    created = []
    for r in recursos:
        tipo = r.get("tipo", "material")
        codigo = r.get("codigo", "")

        # Try to find catalog entry for pricing
        catalog_entry = None
        precio = 0.0
        if codigo:
            ce = (
                db.table("catalog_entries")
                .select("id,precio_sin_iva")
                .eq("org_id", org_id)
                .eq("codigo", codigo)
                .limit(1)
                .execute()
            )
            if ce.data:
                catalog_entry = ce.data[0]
                precio = float(catalog_entry.get("precio_sin_iva") or 0)

        if tipo == "mano_obra":
            trabajadores = float(r.get("trabajadores_por_unidad", 0)) * qty
            dias = float(r.get("dias_por_unidad", 0))
            cargas = float(r.get("cargas_sociales_pct", 25))
            cantidad_efectiva = round(trabajadores * dias * (1 + cargas / 100), 2)
            subtotal = round(cantidad_efectiva * precio, 2)

            resource_data = {
                "item_id": item_id,
                "org_id": org_id,
                "tipo": tipo,
                "codigo": codigo,
                "descripcion": r.get("descripcion", ""),
                "unidad": "jornal",
                "cantidad": 0,
                "trabajadores": trabajadores,
                "dias": dias,
                "cargas_sociales_pct": cargas,
                "desperdicio_pct": 0,
                "cantidad_efectiva": cantidad_efectiva,
                "precio_unitario": precio,
                "subtotal": subtotal,
                "catalog_entry_id": catalog_entry["id"] if catalog_entry else None,
            }
        else:
            cantidad = float(r.get("cantidad_por_unidad", 0)) * qty
            desperdicio = float(r.get("desperdicio_pct", 0))
            cantidad_efectiva = round(cantidad * (1 + desperdicio / 100), 2)
            subtotal = round(cantidad_efectiva * precio, 2)

            resource_data = {
                "item_id": item_id,
                "org_id": org_id,
                "tipo": tipo,
                "codigo": codigo,
                "descripcion": r.get("descripcion", ""),
                "unidad": r.get("unidad", ""),
                "cantidad": cantidad,
                "desperdicio_pct": desperdicio,
                "cantidad_efectiva": cantidad_efectiva,
                "precio_unitario": precio,
                "subtotal": subtotal,
                "trabajadores": 0,
                "dias": 0,
                "cargas_sociales_pct": 25,
                "catalog_entry_id": catalog_entry["id"] if catalog_entry else None,
            }

        res = db.table("item_resources").insert(resource_data).execute()
        if res.data:
            created.append(res.data[0])

    # Recalculate item from its new resources
    all_resources = (
        db.table("item_resources")
        .select("*")
        .eq("item_id", item_id)
        .execute()
    )
    updated_item = calc_item_from_resources(dict(item), all_resources.data or [])
    db.table("budget_items").update({
        "mat_unitario": updated_item["mat_unitario"],
        "mo_unitario": updated_item["mo_unitario"],
        "mat_total": updated_item["mat_total"],
        "mo_total": updated_item["mo_total"],
        "directo_total": updated_item["directo_total"],
    }).eq("id", item_id).execute()

    return {"resources_created": len(created), "item_updated": True}
