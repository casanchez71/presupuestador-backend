from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from utils.supabase_client import supabase, get_current_user
from typing import Dict
import json
from datetime import datetime
import os

app = FastAPI(title="Presupuestador Backend - Módulo Desacoplado")

# CORS restrictivo: solo orígenes autorizados (configurable por env)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BudgetCreate(BaseModel):
    name: str
    description: str | None = None


class ItemUpdate(BaseModel):
    id: str
    cantidad: float | None = None
    precio_unitario: float | None = None
    notas: str | None = None


@app.get("/health")
def health_check():
    return {"status": "OK", "timestamp": datetime.utcnow().isoformat()}


@app.post("/budget/import-excel")
async def import_excel(
    file: UploadFile = File(...),
    current_user: Dict = Depends(get_current_user)
):
    """Importa Excel y guarda snapshot de precios"""
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        raise HTTPException(400, "Solo archivos .xlsx o .xls")

    contents = await file.read()
    try:
        df_dict = pd.read_excel(contents, sheet_name=None)
    except Exception as e:
        raise HTTPException(400, f"Error leyendo Excel: {str(e)}")

    precios = []
    if "00_Mat" in df_dict:
        precios = df_dict["00_Mat"].to_dict(orient="records")

    snapshot_data = {
        "org_id": current_user["tenant_id"],
        "user_id": current_user["user_id"],
        "file_name": file.filename,
        "data": json.dumps({"precios": precios}),
        "created_at": datetime.utcnow().isoformat()
    }

    try:
        result = supabase.table("price_snapshots").insert(snapshot_data).execute()
        return {
            "message": "Excel importado y snapshot creado",
            "snapshot_id": result.data[0]["id"],
            "org_id": current_user["tenant_id"]
        }
    except Exception as e:
        raise HTTPException(500, f"Error al guardar en Supabase: {str(e)}")


@app.get("/budget/tree/{budget_id}")
async def get_tree(
    budget_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Devuelve estructura de árbol jerárquico del presupuesto"""
    # Sprint 1: esto se generará desde DB. Por ahora es un placeholder.
    tree = {
        "name": "Obra Ejemplo",
        "org_id": current_user["tenant_id"],
        "children": [
            {"name": "Piso 1", "children": [
                {"name": "Cimientos"},
                {"name": "Columnas y tabiques"},
                {"name": "Losa"},
                {"name": "Mampostería"}
            ]},
        ]
    }
    return tree


@app.post("/budget/{budget_id}/item/update")
async def update_item(
    budget_id: str,
    item: ItemUpdate,
    current_user: Dict = Depends(get_current_user)
):
    """Actualiza ítem y registra en audit_logs"""
    changes = item.model_dump(exclude_unset=True)

    audit_entry = {
        "org_id": current_user["tenant_id"],
        "user_id": current_user["user_id"],
        "budget_id": budget_id,
        "item_id": item.id,
        "action": "update",
        "changes": changes,
        "timestamp": datetime.utcnow().isoformat()
    }

    try:
        supabase.table("audit_logs").insert(audit_entry).execute()
        # Sprint 1: aquí irá la actualización real en budget_items
        return {"message": "Ítem actualizado y auditado", "changes": changes}
    except Exception as e:
        raise HTTPException(500, f"Error en Supabase: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
