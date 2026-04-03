"""AI-powered plan analysis using GPT-4o Vision."""

from __future__ import annotations

import base64
import json
from uuid import UUID

from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile

from app.auth import get_current_user
from app.config import get_settings
from app.db import get_data_db

router = APIRouter()

SYSTEM_PROMPT = """Sos un experto en presupuestos de construccion argentina.
Analiza el plano y extrae items de presupuesto.

Responde UNICAMENTE con un JSON array. Cada elemento debe tener:
- "code": codigo del item (ej: "1.1", "2.3")
- "description": descripcion del rubro o tarea
- "unidad": unidad de medida (m2, m3, ml, gl, u, mes)
- "cantidad_estimada": cantidad estimada (numero)

Ejemplo de respuesta valida:
[
  {"code": "1.1", "description": "Columnas y tabiques H30", "unidad": "m3", "cantidad_estimada": 23},
  {"code": "1.2", "description": "Losa maciza H30", "unidad": "m3", "cantidad_estimada": 45}
]

NO incluyas texto adicional, explicaciones ni markdown. Solo el JSON array."""

ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


@router.post("/{budget_id}/analyze-plan")
async def analyze_plan(
    budget_id: UUID,
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    """Analyze a construction plan image with GPT-4o Vision."""
    settings = get_settings()
    client = settings.openai_client
    if client is None:
        raise HTTPException(503, "Analisis IA no disponible (falta OPENAI_API_KEY)")

    # Validate file type
    if not file.filename:
        raise HTTPException(400, "Archivo sin nombre")
    ext = file.filename.lower().rsplit(".", 1)[-1] if "." in file.filename else ""
    if f".{ext}" not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400,
            f"Solo imagenes ({', '.join(ALLOWED_EXTENSIONS)}). "
            "PDFs no son soportados por Vision API.",
        )

    # Validate budget exists
    db = get_data_db()
    budget = (
        db.table("budgets")
        .select("id")
        .eq("id", str(budget_id))
        .eq("org_id", user["org_id"])
        .single()
        .execute()
    )
    if not budget.data:
        raise HTTPException(404, "Presupuesto no encontrado")

    content = await file.read()
    b64 = base64.b64encode(content).decode("utf-8")
    mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"

    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL_VISION,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": SYSTEM_PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            ],
        }],
        max_tokens=2000,
        temperature=0.3,
    )

    raw = response.choices[0].message.content or ""

    # Extract JSON from response (handle markdown code blocks)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)

    try:
        suggestions = json.loads(cleaned)
        if not isinstance(suggestions, list):
            raise ValueError("Response is not a JSON array")
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(
            422,
            "La IA no devolvio un formato valido. Intenta con otra imagen mas clara.",
        )

    # Validate each suggestion has required fields
    valid = []
    for s in suggestions:
        if isinstance(s, dict) and s.get("description"):
            valid.append({
                "code": s.get("code"),
                "description": s["description"],
                "unidad": s.get("unidad", "u"),
                "cantidad_estimada": float(s.get("cantidad_estimada", 1)),
            })

    return {
        "budget_id": str(budget_id),
        "suggestions": valid,
        "count": len(valid),
    }


@router.post("/{budget_id}/items/from-ai")
async def insert_ai_suggestions(
    budget_id: UUID,
    suggestions: list[dict] = Body(...),
    user: dict = Depends(get_current_user),
):
    """Insert AI-suggested items into budget_items."""
    db = get_data_db()
    org_id = user["org_id"]

    if not db.table("budgets").select("id").eq("id", str(budget_id)).eq("org_id", org_id).execute().data:
        raise HTTPException(404, "Presupuesto no encontrado")

    to_insert = []
    for i, sug in enumerate(suggestions):
        to_insert.append({
            "budget_id": str(budget_id),
            "org_id": org_id,
            "code": sug.get("code"),
            "description": sug.get("description", "Item IA"),
            "unidad": sug.get("unidad", "u"),
            "cantidad": float(sug.get("cantidad_estimada", 1)),
            "notas": "Sugerido por IA",
            "sort_order": 1000 + i,  # after imported items
        })

    result = db.table("budget_items").insert(to_insert).execute()
    return {"inserted": len(result.data)}
