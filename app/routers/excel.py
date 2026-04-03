"""Excel import/export router.

Import understands the Las Heras format:
  - Catalog sheets: 00_Mat, 00_MO, 00_Eq, 00_Sub
  - Computation sheet: 01_C&P (multi-level header, rows 4-6, data from row 7)
  - Detail sheets: numbered (1.1, 1.2, etc.) with materials + labor breakdown
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from io import BytesIO
from uuid import UUID

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.auth import get_current_user
from app.db import get_data_db
from app.tree import get_parent_candidates, normalize_item_code, safe_float

router = APIRouter()

# Column offsets for 01_C&P (based on Las Heras Excel structure)
# Row 7+ data columns:
COL_ITEM = 0
COL_DESC = 1
COL_UNIDAD = 2
COL_CANTIDAD = 3
# Direct costs (unit prices)
COL_MAT_UNIT = 4
COL_MO_UNIT = 9  # MO total unitario
COL_DIRECTO_UNIT = 10  # General unitario directo
# Direct costs (general/total)
COL_MAT_TOTAL = 11
COL_MO_GENERAL = 12
COL_DIRECTO_GENERAL = 13
# Indirect costs (general)
COL_IND_MAT = 14
COL_IND_MO = 15
COL_IND_GENERAL = 16
# Benefits (general)
COL_BEN_MAT = 17
COL_BEN_MO = 18
COL_BEN_GENERAL = 19
# Net total (unit)
COL_NETO_UNIT_MAT = 20
COL_NETO_UNIT_MO = 21
COL_NETO_UNIT_GEN = 22
# Net total (general)
COL_NETO_MAT = 23
COL_NETO_MO = 24
COL_NETO_GENERAL = 25

# Catalog sheet config: (sheet_name, tipo, header_row)
CATALOG_SHEETS = [
    ("00_Mat", "material", 1),
    ("00_MO", "mano_obra", 2),
    ("00_Eq", "equipo", 2),
    ("00_Sub", "subcontrato", 2),
]


def _cell(df: pd.DataFrame, row: int, col: int) -> float:
    """Safely read a numeric cell from a dataframe."""
    try:
        val = df.iloc[row, col]
        return safe_float(val) or 0.0
    except (IndexError, KeyError):
        return 0.0


def _cell_str(df: pd.DataFrame, row: int, col: int) -> str:
    """Safely read a string cell."""
    try:
        val = df.iloc[row, col]
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return ""
        return str(val).strip()
    except (IndexError, KeyError):
        return ""


def _parse_catalogs(
    df_dict: dict[str, pd.DataFrame], org_id: str, catalog_id: str,
) -> list[dict]:
    """Parse all catalog sheets into catalog_entries rows."""
    entries: list[dict] = []
    for sheet_name, tipo, header_row in CATALOG_SHEETS:
        if sheet_name not in df_dict:
            continue
        df = df_dict[sheet_name]
        # The actual data starts after the header row
        for i in range(header_row + 1, len(df)):
            code = _cell_str(df, i, 0)
            if not code:
                continue
            desc = _cell_str(df, i, 1)
            if not desc:
                continue
            entries.append({
                "catalog_id": catalog_id,
                "org_id": org_id,
                "tipo": tipo,
                "codigo": code,
                "descripcion": desc,
                "unidad": _cell_str(df, i, 2),
                "precio_con_iva": safe_float(df.iloc[i, 3] if df.shape[1] > 3 else None),
                "precio_sin_iva": safe_float(df.iloc[i, 4] if df.shape[1] > 4 else None) if tipo == "material" else safe_float(df.iloc[i, 3] if df.shape[1] > 3 else None),
                "referencia": _cell_str(df, i, 4) if tipo != "material" else None,
            })
    return entries


def _parse_computation_sheet(
    df: pd.DataFrame, budget_id: str, org_id: str,
) -> list[dict]:
    """Parse the 01_C&P sheet into budget_items rows.

    Data starts at row 7 (0-indexed). Section titles have no CANTIDAD (col 3).
    """
    items: list[dict] = []
    code_to_id_placeholder: dict[str, int] = {}  # code -> index for parent lookup

    for i in range(7, len(df)):
        code_raw = _cell_str(df, i, COL_ITEM)
        desc = _cell_str(df, i, COL_DESC)
        cantidad_val = safe_float(df.iloc[i, COL_CANTIDAD] if df.shape[1] > COL_CANTIDAD else None)

        # Skip empty rows
        if not code_raw and not desc:
            continue

        # Section title (no code or no cantidad) — create as parent item
        if cantidad_val is None:
            if code_raw or desc:
                label = f"{code_raw} {desc}".strip() if desc else code_raw
                items.append({
                    "budget_id": budget_id,
                    "org_id": org_id,
                    "parent_id": None,
                    "code": normalize_item_code(code_raw) or None,
                    "description": label,
                    "unidad": None,
                    "cantidad": None,
                    "mat_unitario": 0,
                    "mo_unitario": 0,
                    "mat_total": 0,
                    "mo_total": 0,
                    "directo_total": 0,
                    "indirecto_total": 0,
                    "beneficio_total": 0,
                    "neto_total": 0,
                    "notas": "Seccion",
                    "sort_order": len(items),
                    "_code_norm": normalize_item_code(code_raw),
                })
                if code_raw:
                    code_to_id_placeholder[normalize_item_code(code_raw)] = len(items) - 1
            continue

        # Regular item with data
        code_norm = normalize_item_code(code_raw)

        # Find parent by code hierarchy
        parent_idx = None
        for candidate in get_parent_candidates(code_norm):
            if candidate in code_to_id_placeholder:
                parent_idx = code_to_id_placeholder[candidate]
                break

        mat_unit = _cell(df, i, COL_MAT_UNIT)
        mo_unit = _cell(df, i, COL_MO_UNIT)

        items.append({
            "budget_id": budget_id,
            "org_id": org_id,
            "parent_id": None,  # resolved after insert by index
            "code": code_norm or None,
            "description": desc,
            "unidad": _cell_str(df, i, COL_UNIDAD),
            "cantidad": cantidad_val,
            "mat_unitario": mat_unit,
            "mo_unitario": mo_unit,
            "mat_total": _cell(df, i, COL_MAT_TOTAL),
            "mo_total": _cell(df, i, COL_MO_GENERAL),
            "directo_total": _cell(df, i, COL_DIRECTO_GENERAL),
            "indirecto_total": _cell(df, i, COL_IND_GENERAL),
            "beneficio_total": _cell(df, i, COL_BEN_GENERAL),
            "neto_total": _cell(df, i, COL_NETO_GENERAL),
            "notas": "Importado desde Excel",
            "sort_order": len(items),
            "_code_norm": code_norm,
            "_parent_idx": parent_idx,
        })
        if code_norm:
            code_to_id_placeholder[code_norm] = len(items) - 1

    return items


def _parse_detail_sheets(
    df_dict: dict[str, pd.DataFrame],
    sheet_names: list[str],
    org_id: str,
) -> dict[str, list[dict]]:
    """Parse detail sheets (1.1, 1.2, etc.) into item_resources keyed by item code."""
    resources_by_code: dict[str, list[dict]] = {}

    for sheet_name in sheet_names:
        if sheet_name not in df_dict:
            continue
        df = df_dict[sheet_name]
        code_norm = normalize_item_code(sheet_name)
        if not code_norm:
            continue

        resources: list[dict] = []
        current_tipo: str | None = None

        for i in range(4, len(df)):
            first_cell = _cell_str(df, i, 0)
            upper = first_cell.upper()

            # Detect section headers
            if "MATERIALES" in upper and "TOTAL" not in upper:
                current_tipo = "material"
                continue
            if "MANO DE OBRA" in upper:
                current_tipo = "mano_obra"
                continue
            if "EQUIPO" in upper and "TOTAL" not in upper:
                current_tipo = "equipo"
                continue
            if "SUBCONTRAT" in upper and "TOTAL" not in upper:
                current_tipo = "subcontrato"
                continue
            if "TOTAL" in upper:
                current_tipo = None
                continue

            if current_tipo is None:
                continue

            # Skip header rows (Codigo, Descripcion, etc.)
            if first_cell.lower() in ("codigo", "código", ""):
                continue

            desc = _cell_str(df, i, 1)
            if not desc:
                continue

            cantidad = safe_float(df.iloc[i, 3] if df.shape[1] > 3 else None)
            desperdicio = safe_float(df.iloc[i, 5] if df.shape[1] > 5 else None) or 0
            cantidad_eff = safe_float(df.iloc[i, 6] if df.shape[1] > 6 else None)
            precio = safe_float(df.iloc[i, 7] if df.shape[1] > 7 else None)
            subtotal = safe_float(df.iloc[i, 8] if df.shape[1] > 8 else None)

            if cantidad is None and cantidad_eff is None:
                continue

            resources.append({
                "org_id": org_id,
                "tipo": current_tipo,
                "codigo": first_cell,
                "descripcion": desc,
                "unidad": _cell_str(df, i, 2),
                "cantidad": cantidad,
                "desperdicio_pct": desperdicio,
                "cantidad_efectiva": cantidad_eff or (cantidad * (1 + desperdicio) if cantidad else 0),
                "precio_unitario": precio,
                "subtotal": subtotal or 0,
            })

        if resources:
            resources_by_code[code_norm] = resources

    return resources_by_code


# ── Endpoints ────────────────────────────────────────────────────────────────


@router.post("/import-excel")
async def import_excel(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    """Import a construction budget Excel (Las Heras format)."""
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(400, "Solo archivos .xlsx o .xls")

    contents = await file.read()
    df_dict = pd.read_excel(BytesIO(contents), sheet_name=None, header=None)

    db = get_data_db()
    org_id = user["org_id"]

    # 1. Create price catalog
    catalog = db.table("price_catalogs").insert({
        "org_id": org_id,
        "name": f"Catalogo - {file.filename}",
        "source_file": file.filename,
    }).execute()
    catalog_id = catalog.data[0]["id"]

    # 2. Parse and insert catalog entries
    entries = _parse_catalogs(df_dict, org_id, catalog_id)
    if entries:
        # Insert in batches of 100
        for batch_start in range(0, len(entries), 100):
            batch = entries[batch_start:batch_start + 100]
            db.table("catalog_entries").insert(batch).execute()

    # 3. Create budget
    base_name = os.path.splitext(os.path.basename(file.filename))[0].strip()
    budget_name = base_name or f"Presupuesto {datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    budget = db.table("budgets").insert({
        "org_id": org_id,
        "name": budget_name,
        "description": f"Importado desde {file.filename}",
        "source_file": file.filename,
        "status": "draft",
    }).execute()
    budget_id = budget.data[0]["id"]

    # 4. Parse 01_C&P computation sheet
    items_inserted = 0
    resources_inserted = 0

    if "01_C&P" in df_dict:
        parsed_items = _parse_computation_sheet(df_dict["01_C&P"], budget_id, org_id)

        # Insert items one by one to resolve parent_id references
        idx_to_db_id: dict[int, str] = {}
        for idx, item in enumerate(parsed_items):
            # Resolve parent
            parent_idx = item.pop("_parent_idx", None)
            code_norm = item.pop("_code_norm", "")
            if parent_idx is not None and parent_idx in idx_to_db_id:
                item["parent_id"] = idx_to_db_id[parent_idx]

            result = db.table("budget_items").insert(item).execute()
            if result.data:
                db_id = result.data[0]["id"]
                idx_to_db_id[idx] = db_id
                items_inserted += 1

        # 5. Parse detail sheets and insert item_resources
        detail_sheet_names = [
            s for s in df_dict.keys()
            if s not in ("00_Mat", "00_MO", "00_Eq", "00_Sub", "00_JEF + ESTR",
                         "01_C&P", "01_VENTA", "01_RESUMEN VENTA",
                         "01_RESUMEN MAT.", "01_RESUMEN MAT M.O.",
                         "01_RESUMEN SERV. M.O.", "ESTRUCTURA")
        ]

        resources_by_code = _parse_detail_sheets(df_dict, detail_sheet_names, org_id)

        # Match resources to inserted items by code
        code_to_db_id: dict[str, str] = {}
        for idx, item in enumerate(parsed_items):
            code = item.get("code")
            if code and idx in idx_to_db_id:
                code_to_db_id[normalize_item_code(code)] = idx_to_db_id[idx]

        for code, resources in resources_by_code.items():
            item_db_id = code_to_db_id.get(code)
            if not item_db_id:
                continue
            for res in resources:
                res["item_id"] = item_db_id
            # Insert in batches
            for batch_start in range(0, len(resources), 50):
                batch = resources[batch_start:batch_start + 50]
                db.table("item_resources").insert(batch).execute()
                resources_inserted += len(batch)

    return {
        "message": "Excel importado",
        "catalog_id": catalog_id,
        "catalog_entries": len(entries),
        "budget_id": budget_id,
        "budget_name": budget_name,
        "items_inserted": items_inserted,
        "resources_inserted": resources_inserted,
    }


@router.get("/{budget_id}/export/excel")
async def export_budget_excel(
    budget_id: UUID,
    user: dict = Depends(get_current_user),
):
    """Export a budget to Excel with cost breakdown."""
    db = get_data_db()
    bid = str(budget_id)
    org_id = user["org_id"]

    budget = (
        db.table("budgets")
        .select("id, name")
        .eq("id", bid)
        .eq("org_id", org_id)
        .single()
        .execute()
    )
    if not budget.data:
        raise HTTPException(404, "Presupuesto no encontrado")

    items = (
        db.table("budget_items")
        .select("*")
        .eq("budget_id", bid)
        .eq("org_id", org_id)
        .order("sort_order")
        .execute()
    )
    if not items.data:
        raise HTTPException(404, "Presupuesto sin items")

    rows = []
    for item in items.data:
        rows.append({
            "Codigo": item.get("code") or "",
            "Descripcion": item.get("description") or "",
            "Unidad": item.get("unidad") or "",
            "Cantidad": item.get("cantidad") or "",
            "MAT Unitario": item.get("mat_unitario") or 0,
            "MO Unitario": item.get("mo_unitario") or 0,
            "MAT Total": item.get("mat_total") or 0,
            "MO Total": item.get("mo_total") or 0,
            "Directo Total": item.get("directo_total") or 0,
            "Indirecto Total": item.get("indirecto_total") or 0,
            "Beneficio Total": item.get("beneficio_total") or 0,
            "Neto Total": item.get("neto_total") or 0,
            "Notas": item.get("notas") or "",
        })

    df = pd.DataFrame(rows)

    # Add totals row
    numeric_cols = [
        "MAT Total", "MO Total", "Directo Total",
        "Indirecto Total", "Beneficio Total", "Neto Total",
    ]
    total_row = {col: "" for col in df.columns}
    total_row["Codigo"] = "TOTAL"
    for col in numeric_cols:
        total_row[col] = pd.to_numeric(df[col], errors="coerce").sum()
    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Presupuesto")
    output.seek(0)

    safe_name = (budget.data["name"] or "presupuesto").replace(" ", "_")
    filename = f"{safe_name}_{datetime.now().strftime('%Y%m%d')}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
