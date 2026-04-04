"""Catalog price lookup and application to budgets."""

from __future__ import annotations

import csv
import io
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from app.auth import get_current_user
from app.db import get_data_db
from app.schemas import CatalogTipo

router = APIRouter()


# ── Upload CSV catalog ────────────────────────────────────────────────────


@router.post("/upload-csv")
async def upload_csv_catalog(
    file: UploadFile = File(...),
    tipo: CatalogTipo = Query(..., description="Tipo: material, mano_obra, equipo, subcontrato"),
    name: str = Query(None, description="Nombre del catalogo (default: nombre del archivo)"),
    user: dict = Depends(get_current_user),
):
    """Upload a CSV price list and create a catalog with entries.

    CSV must have columns: codigo, descripcion, unidad, precio_unitario
    """
    db = get_data_db()
    org_id = user["org_id"]

    # Read and parse CSV
    content = await file.read()
    try:
        text = content.decode("utf-8-sig")  # handle BOM
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))

    # Validate required columns
    required_cols = {"codigo", "descripcion", "unidad", "precio_unitario"}
    if not reader.fieldnames or not required_cols.issubset({c.strip().lower() for c in reader.fieldnames}):
        raise HTTPException(
            400,
            f"CSV debe tener columnas: {', '.join(sorted(required_cols))}. "
            f"Encontradas: {reader.fieldnames}",
        )

    # Normalize fieldnames
    field_map = {c.strip().lower(): c for c in reader.fieldnames}

    rows = []
    for row in reader:
        codigo = (row.get(field_map.get("codigo", "codigo")) or "").strip()
        descripcion = (row.get(field_map.get("descripcion", "descripcion")) or "").strip()
        unidad = (row.get(field_map.get("unidad", "unidad")) or "").strip()
        precio_raw = (row.get(field_map.get("precio_unitario", "precio_unitario")) or "").strip()

        if not codigo or not precio_raw:
            continue

        try:
            # Handle Argentine format (dot as thousands, comma as decimal)
            precio_clean = precio_raw.replace(".", "").replace(",", ".") if "," in precio_raw else precio_raw
            precio = float(precio_clean)
        except ValueError:
            continue

        rows.append({
            "codigo": codigo,
            "descripcion": descripcion,
            "unidad": unidad,
            "precio_sin_iva": precio,
            "tipo": tipo,
        })

    if not rows:
        raise HTTPException(400, "CSV sin filas validas")

    # Create catalog
    catalog_name = name or (file.filename or "catalogo").rsplit(".", 1)[0]
    catalog_result = db.table("price_catalogs").insert({
        "org_id": org_id,
        "name": catalog_name,
        "source_file": file.filename,
    }).execute()
    if not catalog_result.data:
        raise HTTPException(500, "Error al crear catalogo")
    catalog_id = catalog_result.data[0]["id"]

    # Insert entries
    entries = [
        {
            "catalog_id": catalog_id,
            "org_id": org_id,
            **row,
        }
        for row in rows
    ]
    db.table("catalog_entries").insert(entries).execute()

    return {
        "catalog_id": catalog_id,
        "name": catalog_name,
        "entries_count": len(entries),
        "tipo": tipo,
    }


# ── List catalogs ───────────────────────────────────────────────────────────


@router.get("")
async def list_catalogs(user: dict = Depends(get_current_user)):
    """List all price catalogs for the org."""
    db = get_data_db()
    result = (
        db.table("price_catalogs")
        .select("*")
        .eq("org_id", user["org_id"])
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


# ── List catalog entries ────────────────────────────────────────────────────


@router.get("/{catalog_id}/entries")
async def list_catalog_entries(
    catalog_id: UUID,
    tipo: str | None = Query(None, description="Filtrar por tipo: material, mano_obra, equipo, subcontrato"),
    user: dict = Depends(get_current_user),
):
    """List entries in a catalog, with optional tipo filter."""
    db = get_data_db()
    org_id = user["org_id"]
    cid = str(catalog_id)

    # Verify catalog belongs to org
    catalog = (
        db.table("price_catalogs")
        .select("id")
        .eq("id", cid)
        .eq("org_id", org_id)
        .single()
        .execute()
    )
    if not catalog.data:
        raise HTTPException(404, "Catalogo no encontrado")

    q = (
        db.table("catalog_entries")
        .select("*")
        .eq("catalog_id", cid)
        .eq("org_id", org_id)
    )
    if tipo:
        q = q.eq("tipo", tipo)

    result = q.order("codigo").execute()
    return result.data or []


# ── Search catalog entries ──────────────────────────────────────────────────


@router.get("/{catalog_id}/search")
async def search_catalog_entries(
    catalog_id: UUID,
    q: str = Query(..., min_length=1, description="Texto de busqueda en descripcion"),
    user: dict = Depends(get_current_user),
):
    """Search catalog entries by description (case-insensitive)."""
    db = get_data_db()
    org_id = user["org_id"]
    cid = str(catalog_id)

    # Verify catalog belongs to org
    catalog = (
        db.table("price_catalogs")
        .select("id")
        .eq("id", cid)
        .eq("org_id", org_id)
        .single()
        .execute()
    )
    if not catalog.data:
        raise HTTPException(404, "Catalogo no encontrado")

    result = (
        db.table("catalog_entries")
        .select("*")
        .eq("catalog_id", cid)
        .eq("org_id", org_id)
        .ilike("descripcion", f"%{q}%")
        .execute()
    )
    return result.data or []


# ── Apply catalog prices to budget ──────────────────────────────────────────


@router.post("/apply/{budget_id}/{catalog_id}")
async def apply_catalog_to_budget(
    budget_id: UUID,
    catalog_id: UUID,
    user: dict = Depends(get_current_user),
):
    """Apply catalog prices to budget item_resources by matching codigo.

    For each item_resource in the budget, look up its price from the catalog
    (match by codigo) and update precio_unitario. Recalculate subtotals.
    """
    db = get_data_db()
    org_id = user["org_id"]
    bid = str(budget_id)
    cid = str(catalog_id)

    # Verify budget belongs to org
    budget = (
        db.table("budgets")
        .select("id")
        .eq("id", bid)
        .eq("org_id", org_id)
        .single()
        .execute()
    )
    if not budget.data:
        raise HTTPException(404, "Presupuesto no encontrado")

    # Verify catalog belongs to org
    catalog = (
        db.table("price_catalogs")
        .select("id")
        .eq("id", cid)
        .eq("org_id", org_id)
        .single()
        .execute()
    )
    if not catalog.data:
        raise HTTPException(404, "Catalogo no encontrado")

    # Load all catalog entries indexed by codigo
    entries_result = (
        db.table("catalog_entries")
        .select("codigo, precio_sin_iva, tipo")
        .eq("catalog_id", cid)
        .eq("org_id", org_id)
        .execute()
    )
    price_map: dict[str, float] = {}
    for entry in (entries_result.data or []):
        codigo = (entry.get("codigo") or "").strip()
        precio = entry.get("precio_sin_iva")
        if codigo and precio is not None:
            price_map[codigo] = float(precio)

    if not price_map:
        raise HTTPException(404, "Catalogo sin entradas con precios")

    # Get all budget items
    items = (
        db.table("budget_items")
        .select("id")
        .eq("budget_id", bid)
        .eq("org_id", org_id)
        .execute()
    )
    if not items.data:
        raise HTTPException(404, "Presupuesto sin items")

    item_ids = [item["id"] for item in items.data]

    # Get all item_resources for these items
    all_resources: list[dict] = []
    for item_id in item_ids:
        res = (
            db.table("item_resources")
            .select("*")
            .eq("item_id", item_id)
            .eq("org_id", org_id)
            .execute()
        )
        all_resources.extend(res.data or [])

    if not all_resources:
        raise HTTPException(404, "Presupuesto sin recursos en items")

    matched = 0
    unmatched = 0
    total_updated = 0.0

    for resource in all_resources:
        codigo = (resource.get("codigo") or "").strip()
        if codigo not in price_map:
            unmatched += 1
            continue

        new_precio = price_map[codigo]
        cantidad_eff = resource.get("cantidad_efectiva") or resource.get("cantidad") or 0
        new_subtotal = round(new_precio * float(cantidad_eff), 2)

        db.table("item_resources").update({
            "precio_unitario": new_precio,
            "subtotal": new_subtotal,
        }).eq("id", resource["id"]).execute()

        matched += 1
        total_updated += new_subtotal

    # Recalculate budget_items totals from their resources
    for item_id in item_ids:
        resources = (
            db.table("item_resources")
            .select("tipo, subtotal")
            .eq("item_id", item_id)
            .eq("org_id", org_id)
            .execute()
        )
        mat_total = 0.0
        mo_total = 0.0
        for r in (resources.data or []):
            subtotal = r.get("subtotal") or 0
            if r.get("tipo") == "material":
                mat_total += subtotal
            elif r.get("tipo") == "mano_obra":
                mo_total += subtotal

        directo_total = mat_total + mo_total
        # Preserve existing indirecto and beneficio
        item_data = (
            db.table("budget_items")
            .select("indirecto_total, beneficio_total, cantidad")
            .eq("id", item_id)
            .single()
            .execute()
        )
        if not item_data.data:
            continue

        cantidad = item_data.data.get("cantidad") or 0
        indirecto = item_data.data.get("indirecto_total") or 0
        beneficio = item_data.data.get("beneficio_total") or 0
        neto_total = directo_total + indirecto + beneficio

        mat_unitario = round(mat_total / cantidad, 2) if cantidad else 0
        mo_unitario = round(mo_total / cantidad, 2) if cantidad else 0

        db.table("budget_items").update({
            "mat_unitario": mat_unitario,
            "mo_unitario": mo_unitario,
            "mat_total": round(mat_total, 2),
            "mo_total": round(mo_total, 2),
            "directo_total": round(directo_total, 2),
            "neto_total": round(neto_total, 2),
        }).eq("id", item_id).execute()

    return {
        "items_matched": matched,
        "items_unmatched": unmatched,
        "total_updated": round(total_updated, 2),
    }
