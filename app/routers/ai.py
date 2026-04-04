"""AI-powered plan analysis using GPT-4o Vision."""

from __future__ import annotations

import base64
import io
import json
import logging
from uuid import UUID

from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile

from app.auth import get_current_user
from app.config import get_settings
from app.db import get_data_db

router = APIRouter()
logger = logging.getLogger(__name__)

# Max image size: 4MB (after resize). GPT-4o Vision accepts up to 20MB but
# smaller is faster and cheaper.
MAX_IMAGE_BYTES = 4 * 1024 * 1024
MAX_DIMENSION = 2048  # px — resize larger images

ALLOWED_IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp")
ALLOWED_PDF_EXT = (".pdf",)
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXT + ALLOWED_PDF_EXT

SYSTEM_PROMPT = """Sos un ingeniero civil experto en presupuestos de obra en Argentina.
Analizá este plano arquitectónico y generá una lista detallada de ítems de presupuesto.

Para cada ambiente/espacio que identifiques:
1. Medí las dimensiones aproximadas
2. Calculá superficies de piso, paredes y techo
3. Identificá elementos estructurales (columnas, vigas, losas)
4. Identificá instalaciones necesarias (eléctrica, sanitaria, gas)
5. Identificá terminaciones (pisos, revestimientos, pintura)

Respondé ÚNICAMENTE con un JSON válido con esta estructura exacta:
{
  "proyecto": {
    "descripcion": "descripción breve del proyecto",
    "superficie_total_m2": number,
    "ambientes_detectados": ["living", "cocina", ...]
  },
  "secciones": [
    {
      "codigo": "1",
      "nombre": "Estructura",
      "items": [
        {
          "codigo": "1.1",
          "descripcion": "Hormigón H-30 para columnas",
          "unidad": "m³",
          "cantidad": 12.5,
          "confianza": "alta",
          "notas": "4 columnas de 30x30cm x 3m altura",
          "memoria_calculo": "4 columnas x 0.30m x 0.30m x 3.00m = 1.08 m3\\nDesperdicio 5%: 1.08 x 1.05 = 1.13 m3\\nTotal redondeado: 1.15 m3"
        }
      ]
    }
  ]
}

Secciones típicas a considerar:
- Tareas Preliminares (obrador, limpieza, replanteo)
- Movimiento de Suelos (excavación, relleno, compactación)
- Estructura (fundaciones, columnas, vigas, losas)
- Mampostería (muros exteriores, interiores, tabiques)
- Instalación Sanitaria (agua fría, caliente, desagüe, cloacal)
- Instalación Eléctrica (tablero, circuitos, bocas de luz, tomas)
- Instalación de Gas (cañería, artefactos, ventilación)
- Revoques y Revestimientos (grueso, fino, azulejos)
- Pisos y Contrapisos (contrapiso, carpeta, piso terminado)
- Carpintería (puertas, ventanas, marcos)
- Pintura (interior, exterior, impermeabilizante)
- Varios (limpieza final, conexiones a red)

Para cada item, incluí un campo "memoria_calculo" con el desglose paso a paso
de cómo calculaste la cantidad. Mostrá las dimensiones, fórmulas y operaciones
intermedias. Ejemplo: "Largo 4.50m x Ancho 3.20m = 14.40 m2".

Sé preciso con las cantidades. Usá las dimensiones del plano.
Si no podés medir algo con certeza, indicá confianza "baja".
No incluyas texto adicional, explicaciones ni markdown. Solo el JSON."""


def _get_file_ext(filename: str | None) -> str:
    """Extract lowercase file extension with dot prefix."""
    if not filename or "." not in filename:
        return ""
    return "." + filename.lower().rsplit(".", 1)[-1]


def _resize_image_if_needed(content: bytes, ext: str) -> bytes:
    """Resize image if larger than MAX_DIMENSION in any direction."""
    try:
        from PIL import Image as PILImage

        img = PILImage.open(io.BytesIO(content))
        w, h = img.size
        if w <= MAX_DIMENSION and h <= MAX_DIMENSION and len(content) <= MAX_IMAGE_BYTES:
            return content

        # Calculate new size preserving aspect ratio
        ratio = min(MAX_DIMENSION / w, MAX_DIMENSION / h)
        new_size = (int(w * ratio), int(h * ratio))
        img = img.resize(new_size, PILImage.LANCZOS)

        buf = io.BytesIO()
        fmt = "JPEG" if ext in (".jpg", ".jpeg") else "PNG"
        img.save(buf, format=fmt, quality=85)
        return buf.getvalue()
    except ImportError:
        # Pillow not installed — send as-is
        logger.warning("Pillow not installed — skipping image resize")
        return content


def _pdf_first_page_to_image(content: bytes) -> bytes:
    """Extract first page of PDF as a PNG image."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=content, filetype="pdf")
        page = doc[0]
        # Render at 2x for detail
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)
        png_bytes = pix.tobytes("png")
        doc.close()
        return png_bytes
    except ImportError:
        raise HTTPException(
            501,
            "Soporte PDF no disponible en el servidor. "
            "Subí el plano como imagen JPG o PNG.",
        )


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
        raise HTTPException(
            503,
            "Análisis IA no disponible — OPENAI_API_KEY no está configurada.",
        )

    # Validate file type
    ext = _get_file_ext(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400,
            f"Formato no soportado. Aceptamos: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Validate budget belongs to org
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

    # Read file content
    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(400, "El archivo es muy grande. Máximo 20 MB.")

    # Handle PDF: extract first page as image
    if ext in ALLOWED_PDF_EXT:
        content = _pdf_first_page_to_image(content)
        mime = "image/png"
    else:
        # Resize large images
        content = _resize_image_if_needed(content, ext)
        mime = "image/jpeg" if ext in (".jpg", ".jpeg") else f"image/{ext.lstrip('.')}"

    b64 = base64.b64encode(content).decode("utf-8")

    # Call GPT-4o Vision with timeout
    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL_VISION,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": SYSTEM_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{b64}"},
                        },
                    ],
                }
            ],
            max_tokens=4096,
            temperature=0.2,
            timeout=60,
        )
    except Exception as e:
        logger.error("OpenAI API error: %s", str(e))
        raise HTTPException(
            502,
            "Error al comunicarse con la IA. Intentá de nuevo en unos segundos.",
        )

    raw = response.choices[0].message.content or ""
    logger.info("AI raw response length: %d chars", len(raw))
    logger.debug("AI raw response: %s", raw[:2000])

    # Extract JSON from response (handle markdown code blocks)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [line for line in lines if not line.strip().startswith("```")]
        cleaned = "\n".join(lines)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.error("Failed to parse AI response as JSON: %s", cleaned[:500])
        raise HTTPException(
            422,
            "La IA no devolvió un formato válido. Intentá con otra imagen más clara.",
        )

    # Validate structure
    if not isinstance(data, dict) or "secciones" not in data:
        # Backwards compat: if it returned a flat array, wrap it
        if isinstance(data, list):
            data = {
                "proyecto": {
                    "descripcion": "Análisis de plano",
                    "superficie_total_m2": 0,
                    "ambientes_detectados": [],
                },
                "secciones": [
                    {
                        "codigo": "1",
                        "nombre": "Items detectados",
                        "items": [
                            {
                                "codigo": s.get("code", f"1.{i+1}"),
                                "descripcion": s.get("description", ""),
                                "unidad": s.get("unidad", "u"),
                                "cantidad": float(s.get("cantidad_estimada", s.get("cantidad", 1))),
                                "confianza": "media",
                                "notas": "",
                                "notas_calculo": "",
                            }
                            for i, s in enumerate(data)
                            if isinstance(s, dict) and s.get("description")
                        ],
                    }
                ],
            }
        else:
            raise HTTPException(
                422,
                "La IA devolvió una estructura no reconocida. Intentá con otra imagen.",
            )

    # Normalize and validate sections
    proyecto = data.get("proyecto", {})
    secciones = data.get("secciones", [])

    normalized_sections = []
    for sec in secciones:
        if not isinstance(sec, dict):
            continue
        items = []
        for item in sec.get("items", []):
            if not isinstance(item, dict) or not item.get("descripcion"):
                continue
            items.append({
                "codigo": str(item.get("codigo", "")),
                "descripcion": str(item["descripcion"]),
                "unidad": str(item.get("unidad", "u")),
                "cantidad": float(item.get("cantidad", 1)),
                "confianza": item.get("confianza", "media") if item.get("confianza") in ("alta", "media", "baja") else "media",
                "notas": str(item.get("notas", "")),
                "notas_calculo": str(item.get("memoria_calculo", "")),
            })
        if items:
            normalized_sections.append({
                "codigo": str(sec.get("codigo", "")),
                "nombre": str(sec.get("nombre", "Sin nombre")),
                "items": items,
            })

    total_items = sum(len(s["items"]) for s in normalized_sections)

    return {
        "budget_id": str(budget_id),
        "proyecto": {
            "descripcion": proyecto.get("descripcion", ""),
            "superficie_total_m2": float(proyecto.get("superficie_total_m2", 0)),
            "ambientes_detectados": proyecto.get("ambientes_detectados", []),
        },
        "secciones": normalized_sections,
        "total_items": total_items,
    }


@router.post("/{budget_id}/items/from-ai")
async def insert_ai_suggestions(
    budget_id: UUID,
    items: list[dict] = Body(..., embed=True),
    user: dict = Depends(get_current_user),
):
    """Insert AI-suggested items into budget_items.

    Accepts a list of items, each with:
      - seccion_nombre: parent section name
      - seccion_codigo: parent section code
      - codigo, descripcion, unidad, cantidad, notas
    Groups items by section and creates parent items for each section.
    """
    db = get_data_db()
    org_id = user["org_id"]

    budget_result = (
        db.table("budgets")
        .select("id")
        .eq("id", str(budget_id))
        .eq("org_id", org_id)
        .single()
        .execute()
    )
    if not budget_result.data:
        raise HTTPException(404, "Presupuesto no encontrado")

    if not items:
        return {"inserted": 0, "sections_created": 0}

    # Get current max sort_order
    existing = (
        db.table("budget_items")
        .select("sort_order")
        .eq("budget_id", str(budget_id))
        .order("sort_order", desc=True)
        .limit(1)
        .execute()
    )
    base_sort = (existing.data[0]["sort_order"] + 100 if existing.data else 1000)

    # Group items by section
    sections_map: dict[str, list[dict]] = {}
    for item in items:
        sec_name = item.get("seccion_nombre", "Items IA")
        if sec_name not in sections_map:
            sections_map[sec_name] = []
        sections_map[sec_name].append(item)

    total_inserted = 0
    sections_created = 0

    for si, (sec_name, sec_items) in enumerate(sections_map.items()):
        sec_code = sec_items[0].get("seccion_codigo", str(si + 1))
        sort_base = base_sort + si * 100

        # Create parent/section item
        parent = (
            db.table("budget_items")
            .insert({
                "budget_id": str(budget_id),
                "org_id": org_id,
                "code": sec_code,
                "description": sec_name,
                "unidad": "gl",
                "cantidad": 1,
                "sort_order": sort_base,
                "notas": "Sección generada por IA",
            })
            .execute()
        )
        parent_id = parent.data[0]["id"] if parent.data else None
        sections_created += 1

        # Create child items
        children_to_insert = []
        for ii, item in enumerate(sec_items):
            row = {
                "budget_id": str(budget_id),
                "org_id": org_id,
                "code": item.get("codigo", f"{sec_code}.{ii + 1}"),
                "description": item.get("descripcion", "Item IA"),
                "unidad": item.get("unidad", "u"),
                "cantidad": float(item.get("cantidad", 1)),
                "notas": item.get("notas", "Sugerido por IA"),
                "notas_calculo": item.get("notas_calculo", ""),
                "sort_order": sort_base + ii + 1,
            }
            if parent_id:
                row["parent_id"] = parent_id
            children_to_insert.append(row)

        if children_to_insert:
            result = db.table("budget_items").insert(children_to_insert).execute()
            total_inserted += len(result.data)

    return {
        "inserted": total_inserted,
        "sections_created": sections_created,
    }
