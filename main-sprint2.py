from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from supabase import Client
from utils.supabase_client import supabase, get_current_user
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
import os
from uuid import UUID
from openai import AsyncOpenAI
import base64

app = FastAPI(title="Presupuestador Backend - Sprint 2")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── OpenAI Client ────────────────────────────────────────────────────────────
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
VISION_MODEL = os.getenv("OPENAI_MODEL_VISION", "gpt-4o")
REASONING_MODEL = os.getenv("OPENAI_MODEL_REASONING", "gpt-4o-mini")

# ── Modelos ──────────────────────────────────────────────────────────────────
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

class IndirectApplyRequest(BaseModel):
    config_id: Optional[UUID] = None

# ── Función árbol ────────────────────────────────────────────────────────────
def build_tree(items: List[Dict]) -> List[Dict]:
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

# ── Función vision ────────────────────────────────────────────────────────────
async def analyze_plan_with_vision(file_content: bytes, filename: str, prompt: str) -> List[Dict]:
    base64_image = base64.b64encode(file_content).decode('utf-8')
    name_lower = filename.lower()
    if name_lower.endswith(('.jpg', '.jpeg')):
        mime_type = "image/jpeg"
    elif name_lower.endswith('.png'):
        mime_type = "image/png"
    else:
        mime_type = "image/jpeg"  # fallback para PDF y otros

    response = await openai_client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
                ]
            }
        ],
        max_tokens=2000,
        temperature=0.4
    )
    try:
        suggestions_text = response.choices[0].message.content
        suggestions = json.loads(suggestions_text)
        if isinstance(suggestions, list):
            return suggestions
        return []
    except Exception:
        return [{"description": line.strip(), "cantidad_estimada": 1.0}
                for line in suggestions_text.split("\n") if line.strip()]

# ========================= ENDPOINTS SPRINT 0 + 1 =========================

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

@app.post("/budget/import-excel")
async def import_excel(file: UploadFile = File(...), current_user: Dict = Depends(get_current_user)):
    contents = await file.read()
    df_dict = pd.read_excel(contents, sheet_name=None)
    precios = {}
    if "00_Mat" in df_dict:
        mat = df_dict["00_Mat"]
        for _, row in mat.iterrows():
            if pd.notna(row.get("CODIGO")):
                precios[str(row["CODIGO"])] = row.get("PRECIO CON IVA") or row.get("PRECIO SIN IVA")
    items = []
    if "01_C&P" in df_dict:
        df = df_dict["01_C&P"]
        for _, row in df.iterrows():
            item_text = str(row.get("ITEM", "")).strip()
            desc = str(row.get("DESCRIPCIÓN", "")).strip()
            if not desc or desc == "nan":
                continue
            items.append({
                "code": item_text,
                "description": desc,
                "unidad": row.get("UNIDAD"),
                "cantidad": float(row.get("CANTIDAD")) if pd.notna(row.get("CANTIDAD")) else None,
                "precio_unitario": None,
                "parent_id": None
            })
    snapshot = supabase.table("price_snapshots").insert({
        "org_id": current_user["tenant_id"],
        "user_id": current_user["user_id"],
        "file_name": file.filename,
        "data": json.dumps({"precios": precios})
    }).execute()
    return {
        "message": "Excel procesado correctamente",
        "snapshot_id": snapshot.data[0]["id"],
        "items_detected": len(items)
    }

# ========================= ENDPOINTS SPRINT 2 =========================

@app.post("/budget/{budget_id}/analyze-plan")
async def analyze_plan(
    budget_id: UUID,
    file: UploadFile = File(...),
    prompt: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Analiza plano (imagen) con GPT-4o Vision"""
    budget = supabase.table("budgets") \
        .select("id") \
        .eq("id", str(budget_id)) \
        .eq("org_id", current_user["tenant_id"]) \
        .single().execute()
    if not budget.data:
        raise HTTPException(404, "Presupuesto no encontrado o sin acceso")

    content = await file.read()
    default_prompt = "Analiza este plano de obra y extrae ítems de presupuesto en formato JSON: lista de objetos con campos code, description, unidad, cantidad_estimada. Usa códigos estándar argentinos (H30, LP18, etc.)."
    suggestions = await analyze_plan_with_vision(content, file.filename, prompt or default_prompt)

    return {
        "budget_id": str(budget_id),
        "suggestions": suggestions,
        "message": f"{len(suggestions)} ítems sugeridos por IA"
    }

@app.post("/budget/{budget_id}/items/from-ai")
async def insert_ai_suggestions(
    budget_id: UUID,
    suggestions: List[Dict] = Body(...),
    current_user: Dict = Depends(get_current_user)
):
    """Inserta ítems sugeridos por IA en budget_items"""
    budget_check = supabase.table("budgets") \
        .select("id") \
        .eq("id", str(budget_id)) \
        .eq("org_id", current_user["tenant_id"]) \
        .execute()
    if not budget_check.data:
        raise HTTPException(404, "Presupuesto no encontrado")

    to_insert = [{
        "budget_id": str(budget_id),
        "org_id": current_user["tenant_id"],
        "parent_id": sug.get("parent_id"),
        "code": sug.get("code"),
        "description": sug.get("description", "Ítem IA"),
        "unidad": sug.get("unidad", "u"),
        "cantidad": sug.get("cantidad_estimada", 1.0),
        "precio_unitario": None,
        "notas": "Sugerido por IA"
    } for sug in suggestions]

    result = supabase.table("budget_items").insert(to_insert).execute()
    return {"inserted": len(result.data), "message": "Ítems de IA insertados"}

@app.post("/budget/{budget_id}/indirects")
async def apply_indirects(
    budget_id: UUID,
    request: IndirectApplyRequest = Body(default=IndirectApplyRequest()),
    current_user: Dict = Depends(get_current_user)
):
    """Aplica % de indirectos a todos los ítems del presupuesto"""
    config_query = supabase.table("indirect_config") \
        .select("*") \
        .eq("org_id", current_user["tenant_id"])
    if request.config_id:
        config_query = config_query.eq("id", str(request.config_id))
    config_result = config_query.limit(1).execute()
    if not config_result.data:
        raise HTTPException(404, "Configuración de indirectos no encontrada")
    config = config_result.data[0]

    items = supabase.table("budget_items") \
        .select("id, cantidad, precio_unitario") \
        .eq("budget_id", str(budget_id)) \
        .eq("org_id", current_user["tenant_id"]) \
        .execute()
    if not items.data:
        raise HTTPException(404, "No hay ítems en el presupuesto")

    total_directo = sum(
        (item["cantidad"] or 0) * (item["precio_unitario"] or 0)
        for item in items.data
    )
    estructura = total_directo * (config["estructura_pct"] or 0)
    jefatura = total_directo * (config["jefatura_pct"] or 0)
    logistica = total_directo * (config["logistica_pct"] or 0)
    herramientas = total_directo * (config["herramientas_pct"] or 0)
    total_indirectos = estructura + jefatura + logistica + herramientas

    for item in items.data:
        item_directo = (item["cantidad"] or 0) * (item["precio_unitario"] or 0)
        indirecto_item = (item_directo / total_directo * total_indirectos) if total_directo > 0 else 0
        supabase.table("budget_items") \
            .update({"indirecto": indirecto_item, "total_con_indirecto": item_directo + indirecto_item}) \
            .eq("id", item["id"]) \
            .execute()

    return {
        "total_directo": total_directo,
        "total_indirectos": total_indirectos,
        "items_updated": len(items.data),
        "config_used": config["id"]
    }

@app.get("/budget/{budget_id}/analysis")
async def get_analysis(budget_id: UUID, current_user: Dict = Depends(get_current_user)):
    """Vista análisis: directo / indirectos / total"""
    items = supabase.table("budget_items") \
        .select("cantidad, precio_unitario, indirecto, total_con_indirecto") \
        .eq("budget_id", str(budget_id)) \
        .eq("org_id", current_user["tenant_id"]) \
        .execute()
    if not items.data:
        raise HTTPException(404, "Presupuesto vacío o sin acceso")

    total_directo = sum((i["cantidad"] or 0) * (i["precio_unitario"] or 0) for i in items.data)
    total_indirectos = sum(i["indirecto"] or 0 for i in items.data)
    gran_total = sum(i["total_con_indirecto"] or 0 for i in items.data)

    return {
        "budget_id": str(budget_id),
        "total_directo": total_directo,
        "total_indirectos": total_indirectos,
        "gran_total": gran_total,
        "items_count": len(items.data)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
