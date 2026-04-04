"""Extract real data from all 3 Terrac Excel files into JSON seed files."""
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime

EXCEL_DIR = "/Users/carlossanchez/Downloads/presupuestador-backend/branding/MODELOS DE EXCELS"
OUTPUT_DIR = "seed_data"

EXCELS = {
    "las_heras": "EDIFICIO LAS HERAS-OBRA GRIS_Computo y Presupuesto.xlsx",
    "lugones": "Copia de CASA LUGONES_Computo y Presupuesto_v1.xlsx",
    "el_encuentro": "Copia de El ENCUENTRO_Computo y Presupuesto.xlsx",
}

def clean_val(v):
    """Convert numpy/pandas types to JSON-safe Python types."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return round(float(v), 2)
    if isinstance(v, pd.Timestamp):
        return str(v)
    if isinstance(v, datetime):
        return str(v)
    return v

def safe_str(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    return str(v).strip() or None

def safe_float(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    try:
        return round(float(v), 2)
    except (ValueError, TypeError):
        return None

def normalize_date_code(v):
    """Convert date-encoded codes: day=section, month=item."""
    ts = None
    if isinstance(v, pd.Timestamp):
        ts = v
    elif isinstance(v, datetime):
        ts = pd.Timestamp(v)
    elif isinstance(v, str) and len(v) >= 10 and v[4] == '-':
        try:
            ts = pd.Timestamp(v)
        except:
            return None
    if ts:
        return f"{ts.day}.{ts.month}"
    return None

def normalize_code(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    # Try date conversion
    dc = normalize_date_code(v)
    if dc:
        return dc
    s = str(v).strip().replace(",", ".")
    # Handle X.Y-Z format
    import re
    s = re.sub(r"-(\d)", r".\1", s)
    return s.strip(".") or None

def extract_catalog(df_dict, sheet_name, tipo, header_row=1):
    """Extract catalog entries from a sheet."""
    if sheet_name not in df_dict:
        return []
    df = df_dict[sheet_name]
    entries = []
    for i in range(header_row + 1, len(df)):
        try:
            code = safe_str(df.iloc[i, 0])
            desc = safe_str(df.iloc[i, 1])
            if not code and not desc:
                continue
            entry = {
                "codigo": code,
                "descripcion": desc,
                "unidad": safe_str(df.iloc[i, 2]) if df.shape[1] > 2 else None,
                "tipo": tipo,
            }
            if tipo == "material" and df.shape[1] > 4:
                entry["precio_con_iva"] = safe_float(df.iloc[i, 3])
                entry["precio_sin_iva"] = safe_float(df.iloc[i, 4])
            elif df.shape[1] > 3:
                entry["precio"] = safe_float(df.iloc[i, 3])
            entries.append(entry)
        except (IndexError, KeyError):
            continue
    return entries

def extract_items(df_dict, sheet_name="01_C&P"):
    """Extract budget items from computation sheet."""
    if sheet_name not in df_dict:
        return []
    df = df_dict[sheet_name]
    items = []
    for i in range(7, len(df)):
        try:
            raw_code = df.iloc[i, 0] if df.shape[1] > 0 else None
            code = normalize_code(raw_code)
            desc = safe_str(df.iloc[i, 1]) if df.shape[1] > 1 else None
            cantidad = safe_float(df.iloc[i, 3]) if df.shape[1] > 3 else None

            if not code and not desc:
                continue

            item = {
                "code": code,
                "description": desc,
                "unidad": safe_str(df.iloc[i, 2]) if df.shape[1] > 2 else None,
                "cantidad": cantidad,
                "is_section": cantidad is None,
                "mat_unitario": safe_float(df.iloc[i, 4]) if df.shape[1] > 4 else None,
                "mo_unitario": safe_float(df.iloc[i, 9]) if df.shape[1] > 9 else None,
                "mat_total": safe_float(df.iloc[i, 11]) if df.shape[1] > 11 else None,
                "mo_total": safe_float(df.iloc[i, 12]) if df.shape[1] > 12 else None,
                "directo_total": safe_float(df.iloc[i, 13]) if df.shape[1] > 13 else None,
                "indirecto_total": safe_float(df.iloc[i, 16]) if df.shape[1] > 16 else None,
                "beneficio_total": safe_float(df.iloc[i, 19]) if df.shape[1] > 19 else None,
                "neto_total": safe_float(df.iloc[i, 25]) if df.shape[1] > 25 else None,
            }
            items.append(item)
        except (IndexError, KeyError):
            continue
    return items

def extract_detail_sheets(df_dict, system_sheets):
    """Extract resources from detail sheets."""
    resources = {}
    for sheet_name in df_dict:
        if sheet_name in system_sheets:
            continue
        if sheet_name.startswith("00_") or sheet_name.startswith("01_"):
            continue

        df = df_dict[sheet_name]
        code = normalize_code(sheet_name)
        if not code:
            continue

        sheet_resources = []
        current_tipo = None

        for i in range(4, len(df)):
            try:
                first = safe_str(df.iloc[i, 0])
                if not first:
                    continue
                upper = first.upper()

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
                if first.lower() in ("codigo", "código", ""):
                    continue

                desc = safe_str(df.iloc[i, 1]) if df.shape[1] > 1 else None
                if not desc:
                    continue

                sheet_resources.append({
                    "tipo": current_tipo,
                    "codigo": first,
                    "descripcion": desc,
                    "unidad": safe_str(df.iloc[i, 2]) if df.shape[1] > 2 else None,
                    "cantidad": safe_float(df.iloc[i, 3]) if df.shape[1] > 3 else None,
                    "desperdicio_pct": safe_float(df.iloc[i, 5]) if df.shape[1] > 5 else None,
                    "cantidad_efectiva": safe_float(df.iloc[i, 6]) if df.shape[1] > 6 else None,
                    "precio_unitario": safe_float(df.iloc[i, 7]) if df.shape[1] > 7 else None,
                    "subtotal": safe_float(df.iloc[i, 8]) if df.shape[1] > 8 else None,
                })
            except (IndexError, KeyError):
                continue

        if sheet_resources:
            resources[code] = sheet_resources

    return resources

def extract_indirects(df_dict):
    """Extract indirect costs from JEF+ESTR sheet."""
    for name in ["00_JEF + ESTR", "00_JEF+ESTR", "00_JEF + EST"]:
        if name in df_dict:
            df = df_dict[name]
            rows = []
            for i in range(len(df)):
                try:
                    desc = safe_str(df.iloc[i, 0])
                    val = safe_float(df.iloc[i, 1]) if df.shape[1] > 1 else None
                    if desc and val:
                        rows.append({"concepto": desc, "monto": val})
                except:
                    continue
            return rows
    return []

def process_excel(project_key, filename):
    filepath = os.path.join(EXCEL_DIR, filename)
    outdir = os.path.join(OUTPUT_DIR, project_key)
    os.makedirs(outdir, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Procesando: {project_key} ({filename})")
    print(f"{'='*60}")

    # Read all sheets
    df_dict = pd.read_excel(filepath, sheet_name=None, header=None, engine="openpyxl")
    print(f"  Hojas encontradas: {len(df_dict)}")

    system_sheets = {"ESTRUCTURA", "TIEMPOS", "01_VENTA", "01_RESUMEN VENTA",
                     "01_RESUMEN MAT.", "01_RESUMEN MAT M.O.", "01_RESUMEN SERV. M.O."}

    # 1. Catalogs
    mat = extract_catalog(df_dict, "00_Mat", "material", 1)
    mo = extract_catalog(df_dict, "00_MO", "mano_obra", 2)
    eq = extract_catalog(df_dict, "00_Eq", "equipo", 2)
    sub = extract_catalog(df_dict, "00_Sub", "subcontrato", 2)

    # 2. Items
    items = extract_items(df_dict)

    # 3. Resources from detail sheets
    resources = extract_detail_sheets(df_dict, system_sheets)

    # 4. Indirect costs
    indirects = extract_indirects(df_dict)

    # 5. Summary
    summary = {
        "proyecto": project_key,
        "archivo": filename,
        "hojas_total": len(df_dict),
        "hojas": list(df_dict.keys()),
        "materiales": len(mat),
        "mano_obra": len(mo),
        "equipos": len(eq),
        "subcontratos": len(sub),
        "items": len(items),
        "items_seccion": len([i for i in items if i.get("is_section")]),
        "items_detalle": len([i for i in items if not i.get("is_section")]),
        "hojas_detalle_con_recursos": len(resources),
        "total_recursos": sum(len(r) for r in resources.values()),
    }

    # Write files
    files = {
        "catalogo_materiales.json": mat,
        "catalogo_mano_obra.json": mo,
        "catalogo_equipos.json": eq,
        "catalogo_subcontratos.json": sub,
        "items_presupuesto.json": items,
        "recursos_por_item.json": resources,
        "costos_indirectos.json": indirects,
        "resumen_obra.json": summary,
    }

    for fname, data in files.items():
        path = os.path.join(outdir, fname)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=clean_val)
        count = len(data) if isinstance(data, (list, dict)) else 1
        print(f"  ✓ {fname}: {count} registros")

    print(f"\n  RESUMEN: {summary['materiales']} materiales, {summary['mano_obra']} MO, "
          f"{summary['equipos']} equipos, {summary['subcontratos']} sub, "
          f"{summary['items']} items, {summary['total_recursos']} recursos")

    return summary

if __name__ == "__main__":
    print("EXTRACCIÓN DE DATOS REALES DE EXCELS TERRAC")
    print("=" * 60)

    summaries = []
    for key, filename in EXCELS.items():
        try:
            s = process_excel(key, filename)
            summaries.append(s)
        except Exception as e:
            print(f"  ERROR procesando {key}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("EXTRACCIÓN COMPLETA")
    print("=" * 60)
    for s in summaries:
        print(f"  {s['proyecto']}: {s['materiales']} mat, {s['items']} items, {s['total_recursos']} recursos")
    print(f"\nArchivos en: {OUTPUT_DIR}/")
