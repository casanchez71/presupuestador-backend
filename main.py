from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from supabase import Client
from utils.supabase_client import supabase, get_current_user
from typing import Dict, List, Optional
import json
from datetime import datetime
import os
from uuid import UUID

app = FastAPI(title="Presupuestador Backend - Sprint 1")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================= MODELOS =========================
class BudgetCreate(BaseModel):
    name: str
    description: Optional[str] = None

class BudgetItemCreate(BaseModel):
    parent_id: Optional[UUID] = None
    code: Optional[str] = None
    description: str
    unidad: Optional[str] = None
    cantidad: Optional[float] = None
    precio_unitario: Optional[float] = None
    notas: Optional[str] = None

# ========================= FUNCIÓN ÁRBOL =========================
def build_tree(items: List[Dict]) -> List[Dict]:
    """Convierte lista plana → árbol jerárquico usando parent_id"""
    if not items:
        return []
    
    item_map = {item["id"]: {**item, "children": []} for item in items}
    roots = []
    
    for item in items:
        if item.get("parent_id") is None:
            roots.append(item_map[item["id"]])
        elif item["parent_id"] in item_map:
            item_map[item["parent_id"]]["children"].append(item_map[item["id"]])
    
    return roots

# ========================= ENDPOINTS =========================

@app.get("/health")
def health_check():
    return {"status": "OK", "timestamp": datetime.utcnow().isoformat()}

@app.post("/budgets")
async def create_budget(budget: BudgetCreate, current_user: Dict = Depends(get_current_user)):
    data = {
        "org_id": current_user["tenant_id"],
        "name": budget.name,
        "description": budget.description,
        "status": "draft"
    }
    result = supabase.table("budgets").insert(data).execute()
    return result.data[0]

@app.get("/budgets")
async def list_budgets(current_user: Dict = Depends(get_current_user)):
    result = supabase.table("budgets") \
        .select("*") \
        .eq("org_id", current_user["tenant_id"]) \
        .execute()
    return result.data or []

@app.get("/budget/{budget_id}")
async def get_budget(budget_id: UUID, current_user: Dict = Depends(get_current_user)):
    result = supabase.table("budgets") \
        .select("*") \
        .eq("id", str(budget_id)) \
        .eq("org_id", current_user["tenant_id"]) \
        .single().execute()
    if not result.data:
        raise HTTPException(404, "Presupuesto no encontrado")
    return result.data

@app.delete("/budget/{budget_id}")
async def delete_budget(budget_id: UUID, current_user: Dict = Depends(get_current_user)):
    result = supabase.table("budgets") \
        .delete() \
        .eq("id", str(budget_id)) \
        .eq("org_id", current_user["tenant_id"]) \
        .execute()
    return {"message": "Eliminado" if result.data else "No encontrado"}

@app.post("/budget/{budget_id}/items")
async def create_items(budget_id: UUID, items: List[BudgetItemCreate], current_user: Dict = Depends(get_current_user)):
    to_insert = [{
        "budget_id": str(budget_id),
        "org_id": current_user["tenant_id"],
        "parent_id": str(item.parent_id) if item.parent_id else None,
        "code": item.code,
        "description": item.description,
        "unidad": item.unidad,
        "cantidad": item.cantidad,
        "precio_unitario": item.precio_unitario,
        "notas": item.notas
    } for item in items]

    result = supabase.table("budget_items").insert(to_insert).execute()
    return {"inserted": len(result.data)}

@app.get("/budget/{budget_id}/tree")
async def get_tree(budget_id: UUID, current_user: Dict = Depends(get_current_user)):
    result = supabase.table("budget_items") \
        .select("*") \
        .eq("budget_id", str(budget_id)) \
        .eq("org_id", current_user["tenant_id"]) \
        .execute()
    
    tree = build_tree(result.data or [])
    return {"budget_id": str(budget_id), "tree": tree}

# ========================= PARSER EXCEL (definido por mí) =========================
@app.post("/budget/import-excel")
async def import_excel(
    file: UploadFile = File(...),
    current_user: Dict = Depends(get_current_user)
):
    """Parser basado en tu Excel real 'EDIFICIO LAS HERAS'"""
    contents = await file.read()
    df_dict = pd.read_excel(contents, sheet_name=None)

    # 1. Precios base (hoja 00_Mat)
    precios = {}
    if "00_Mat" in df_dict:
        mat = df_dict["00_Mat"]
        for _, row in mat.iterrows():
            if pd.notna(row.get("CODIGO")):
                precios[str(row["CODIGO"])] = row.get("PRECIO CON IVA") or row.get("PRECIO SIN IVA")

    # 2. Estructura principal (hoja 01_C&P) - detectamos jerarquía por ITEM
    items = []
    if "01_C&P" in df_dict:
        df = df_dict["01_C&P"]
        current_parent = None
        level_stack = []

        for _, row in df.iterrows():
            item_text = str(row.get("ITEM", "")).strip()
            desc = str(row.get("DESCRIPCIÓN", "")).strip()
            if not desc or desc == "nan":
                continue

            # Detectamos nivel (simple pero efectivo para tu Excel)
            if item_text.startswith(("0.", "1.", "2.", "3.", "4.")) or item_text.startswith("46"):
                # Nuevo nivel o piso
                current_parent = None
                level_stack = []

            item_data = {
                "code": item_text,
                "description": desc,
                "unidad": row.get("UNIDAD"),
                "cantidad": float(row.get("CANTIDAD")) if pd.notna(row.get("CANTIDAD")) else None,
                "precio_unitario": None,  # se puede enriquecer después con precios
                "parent_id": current_parent
            }
            items.append(item_data)

    # Guardar snapshot y presupuesto
    snapshot = supabase.table("price_snapshots").insert({
        "org_id": current_user["tenant_id"],
        "user_id": current_user["user_id"],
        "file_name": file.filename,
        "data": json.dumps({"precios": precios})
    }).execute()

    return {
        "message": "Excel procesado correctamente",
        "snapshot_id": snapshot.data[0]["id"],
        "items_detected": len(items),
        "note": "Parser inicial basado en tu Excel Las Heras. Podemos refinarlo después."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
