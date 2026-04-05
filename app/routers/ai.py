"""AI-powered plan analysis using GPT-4o Vision."""

from __future__ import annotations

import base64
import io
import json
import logging
from uuid import UUID

from fastapi import APIRouter, Body, Depends, File, HTTPException, UploadFile

from app.auth import get_current_user
from app.calculations import calc_item_from_resources, calc_resource_subtotal
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

_SYSTEM_PROMPT_BASE = """Sos un ingeniero civil experto en presupuestos de obra en Argentina.
Analizá este plano arquitectónico y generá una lista detallada de ítems de presupuesto.

Para cada ambiente/espacio que identifiques:
1. Medí las dimensiones aproximadas
2. Calculá superficies de piso, paredes y techo
3. Identificá elementos estructurales (columnas, vigas, losas)
4. Identificá instalaciones necesarias (eléctrica, sanitaria, gas)
5. Identificá terminaciones (pisos, revestimientos, pintura)

{catalog_context}

Respondé ÚNICAMENTE con un JSON válido con esta estructura exacta:
{{
  "proyecto": {{
    "descripcion": "descripción breve del proyecto",
    "superficie_total_m2": number,
    "ambientes_detectados": ["living", "cocina", ...]
  }},
  "secciones": [
    {{
      "codigo": "1",
      "nombre": "Estructura",
      "items": [
        {{
          "codigo": "1.1",
          "descripcion": "Hormigón H-30 para columnas",
          "unidad": "m³",
          "cantidad": 12.5,
          "confianza": "alta",
          "notas": "4 columnas de 30x30cm x 3m altura",
          "memoria_calculo": "4 columnas x 0.30m x 0.30m x 3.00m = 1.08 m3\\nDesperdicio 5%: 1.08 x 1.05 = 1.13 m3\\nTotal redondeado: 1.15 m3",
          "recursos": {{
            "materiales": [
              {{"codigo": "H30", "descripcion": "Hormigón H-30", "unidad": "m3", "cantidad_por_unidad": 1.0, "desperdicio_pct": 10}}
            ],
            "mano_obra": [
              {{"codigo": "MO-OF", "descripcion": "Oficial", "trabajadores": 2, "dias_por_unidad": 0.33, "cargas_sociales_pct": 25}}
            ],
            "equipos": [],
            "mo_materiales": [],
            "subcontratos": []
          }}
        }}
      ]
    }}
  ]
}}

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

{recursos_instruction}

Sé preciso con las cantidades. Usá las dimensiones del plano.
Si no podés medir algo con certeza, indicá confianza "baja".
No incluyas texto adicional, explicaciones ni markdown. Solo el JSON."""

_RECURSOS_INSTRUCTION_WITH_CATALOG = """IMPORTANTE: Para cada ítem, DEBÉS incluir la composición de recursos usando los códigos del catálogo de arriba.
Cada recurso debe tener el código exacto del catálogo para poder vincular precios automáticamente.
Si no encontrás un código exacto en el catálogo, usá el más cercano o dejá el código vacío."""

_RECURSOS_INSTRUCTION_WITHOUT_CATALOG = """IMPORTANTE: Para cada ítem, incluí la composición de recursos estimada.
Usá códigos descriptivos para los recursos (ej: "H30" para hormigón H-30, "MO-OF" para oficial)."""


def _build_system_prompt(catalog_context: str) -> str:
    """Build the system prompt, injecting catalog context and matching instruction."""
    if catalog_context:
        return _SYSTEM_PROMPT_BASE.format(
            catalog_context=catalog_context,
            recursos_instruction=_RECURSOS_INSTRUCTION_WITH_CATALOG,
        )
    return _SYSTEM_PROMPT_BASE.format(
        catalog_context="",
        recursos_instruction=_RECURSOS_INSTRUCTION_WITHOUT_CATALOG,
    )


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


def _load_catalog_context(db, org_id: str) -> str:
    """Load catalog entries for the org and return a formatted context string."""
    try:
        catalogs = (
            db.table("price_catalogs")
            .select("id,name")
            .eq("org_id", org_id)
            .execute()
        )
        if not catalogs.data:
            return ""

        catalog_ids = [c["id"] for c in catalogs.data]
        entries = (
            db.table("catalog_entries")
            .select("codigo,descripcion,unidad,precio_sin_iva,tipo")
            .in_("catalog_id", catalog_ids)
            .execute()
        )
        if not entries.data:
            return ""

        # Group by tipo
        by_tipo: dict[str, list[dict]] = {}
        for e in entries.data:
            tipo = e.get("tipo") or "material"
            by_tipo.setdefault(tipo, []).append(e)

        tipo_labels = {
            "material": "MATERIALES",
            "mano_obra": "MANO DE OBRA (jornal diario)",
            "equipo": "EQUIPOS (por día)",
            "subcontrato": "SUBCONTRATOS",
        }

        parts = []
        for tipo, label in tipo_labels.items():
            if tipo not in by_tipo:
                continue
            lines = []
            for e in by_tipo[tipo]:
                code = e.get("codigo") or "SIN-COD"
                desc = e.get("descripcion") or ""
                unit = e.get("unidad") or ""
                price = float(e.get("precio_sin_iva") or 0)
                lines.append(f"  - {code}: {desc}, {unit}, ${price:,.0f}")
            parts.append(f"\n{label}:\n" + "\n".join(lines))

        if not parts:
            return ""

        return "Tenés disponibles estos catálogos de precios:" + "".join(parts)
    except Exception:
        logger.warning("Failed to load catalog context", exc_info=True)
        return ""


def _normalize_recursos(raw_recursos: object) -> dict | None:
    """Normalize the recursos dict from AI response. Returns None if invalid/empty."""
    if not isinstance(raw_recursos, dict):
        return None

    normalized: dict[str, list] = {
        "materiales": [],
        "mano_obra": [],
        "equipos": [],
        "mo_materiales": [],
        "subcontratos": [],
    }

    def _safe_list(val: object) -> list:
        return val if isinstance(val, list) else []

    for mat in _safe_list(raw_recursos.get("materiales")):
        if not isinstance(mat, dict):
            continue
        normalized["materiales"].append({
            "codigo": str(mat.get("codigo") or ""),
            "descripcion": str(mat.get("descripcion") or ""),
            "unidad": str(mat.get("unidad") or "u"),
            "cantidad_por_unidad": float(mat.get("cantidad_por_unidad") or 0),
            "desperdicio_pct": float(mat.get("desperdicio_pct") or 0),
        })

    for mo in _safe_list(raw_recursos.get("mano_obra")):
        if not isinstance(mo, dict):
            continue
        normalized["mano_obra"].append({
            "codigo": str(mo.get("codigo") or ""),
            "descripcion": str(mo.get("descripcion") or ""),
            "trabajadores": float(mo.get("trabajadores") or 1),
            "dias_por_unidad": float(mo.get("dias_por_unidad") or 0),
            "cargas_sociales_pct": float(mo.get("cargas_sociales_pct") or 25),
        })

    for eq in _safe_list(raw_recursos.get("equipos")):
        if not isinstance(eq, dict):
            continue
        normalized["equipos"].append({
            "codigo": str(eq.get("codigo") or ""),
            "descripcion": str(eq.get("descripcion") or ""),
            "unidad": str(eq.get("unidad") or "día"),
            "cantidad_por_unidad": float(eq.get("cantidad_por_unidad") or 0),
            "desperdicio_pct": float(eq.get("desperdicio_pct") or 0),
        })

    for mom in _safe_list(raw_recursos.get("mo_materiales")):
        if not isinstance(mom, dict):
            continue
        normalized["mo_materiales"].append({
            "codigo": str(mom.get("codigo") or ""),
            "descripcion": str(mom.get("descripcion") or ""),
            "unidad": str(mom.get("unidad") or "u"),
            "cantidad_por_unidad": float(mom.get("cantidad_por_unidad") or 0),
            "desperdicio_pct": float(mom.get("desperdicio_pct") or 0),
        })

    for sub in _safe_list(raw_recursos.get("subcontratos")):
        if not isinstance(sub, dict):
            continue
        normalized["subcontratos"].append({
            "codigo": str(sub.get("codigo") or ""),
            "descripcion": str(sub.get("descripcion") or ""),
            "unidad": str(sub.get("unidad") or "gl"),
            "cantidad_por_unidad": float(sub.get("cantidad_por_unidad") or 0),
            "desperdicio_pct": float(sub.get("desperdicio_pct") or 0),
        })

    # Return None if all lists are empty (no point storing empty recursos)
    total = sum(len(v) for v in normalized.values())
    return normalized if total > 0 else None


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
    org_id = user["org_id"]
    budget = (
        db.table("budgets")
        .select("id")
        .eq("id", str(budget_id))
        .eq("org_id", org_id)
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

    # Load user's catalog entries to inject context into the prompt
    catalog_context = _load_catalog_context(db, org_id)
    if catalog_context:
        logger.info("Catalog context loaded (%d chars) for org %s", len(catalog_context), org_id)
    else:
        logger.info("No catalog context found for org %s — proceeding without it", org_id)

    system_prompt = _build_system_prompt(catalog_context)

    # Call GPT-4o Vision with timeout
    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL_VISION,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": system_prompt},
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
            normalized_item: dict = {
                "codigo": str(item.get("codigo", "")),
                "descripcion": str(item["descripcion"]),
                "unidad": str(item.get("unidad", "u")),
                "cantidad": float(item.get("cantidad", 1)),
                "confianza": item.get("confianza", "media") if item.get("confianza") in ("alta", "media", "baja") else "media",
                "notas": str(item.get("notas", "")),
                "notas_calculo": str(item.get("memoria_calculo", "")),
            }
            # Extract and normalize recursos if present
            recursos = _normalize_recursos(item.get("recursos"))
            if recursos is not None:
                normalized_item["recursos"] = recursos
            items.append(normalized_item)
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
        "catalog_loaded": bool(catalog_context),
    }


def _find_catalog_entry(db, org_id: str, codigo: str) -> dict | None:
    """Try to find a catalog entry by codigo across all org catalogs."""
    if not codigo:
        return None
    try:
        catalogs = (
            db.table("price_catalogs")
            .select("id")
            .eq("org_id", org_id)
            .execute()
        )
        if not catalogs.data:
            return None
        catalog_ids = [c["id"] for c in catalogs.data]
        result = (
            db.table("catalog_entries")
            .select("id,precio_sin_iva")
            .in_("catalog_id", catalog_ids)
            .eq("codigo", codigo)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception:
        logger.warning("Catalog entry lookup failed for codigo=%s", codigo, exc_info=True)
        return None


def _create_resources_for_item(
    db,
    item_id: str,
    org_id: str,
    item_cantidad: float,
    recursos: dict,
) -> list[dict]:
    """Create item_resources rows from AI-generated recursos dict.

    Returns the list of inserted resource rows (may be empty on failure).
    """
    rows: list[dict] = []

    # ── materiales ──────────────────────────────────────────────────────────
    for mat in recursos.get("materiales", []):
        codigo = mat.get("codigo", "")
        qty_por_unidad = float(mat.get("cantidad_por_unidad") or 0)
        total_qty = qty_por_unidad * item_cantidad
        desperdicio_pct = float(mat.get("desperdicio_pct") or 0)

        catalog_entry = _find_catalog_entry(db, org_id, codigo)
        precio_unitario = float(catalog_entry["precio_sin_iva"]) if catalog_entry else 0.0
        catalog_entry_id = catalog_entry["id"] if catalog_entry else None

        resource = {
            "item_id": item_id,
            "org_id": org_id,
            "tipo": "material",
            "codigo": codigo,
            "descripcion": mat.get("descripcion", ""),
            "unidad": mat.get("unidad", "u"),
            "cantidad": total_qty,
            "desperdicio_pct": desperdicio_pct,
            "precio_unitario": precio_unitario,
            "catalog_entry_id": catalog_entry_id,
            "trabajadores": 0,
            "dias": 0,
            "cargas_sociales_pct": 0,
        }
        calc_resource_subtotal(resource)
        rows.append(resource)

    # ── mano_obra ───────────────────────────────────────────────────────────
    for mo in recursos.get("mano_obra", []):
        codigo = mo.get("codigo", "")
        trabajadores = float(mo.get("trabajadores") or 1)
        dias_por_unidad = float(mo.get("dias_por_unidad") or 0)
        total_dias = dias_por_unidad * item_cantidad
        cargas_sociales_pct = float(mo.get("cargas_sociales_pct") or 25)

        catalog_entry = _find_catalog_entry(db, org_id, codigo)
        precio_unitario = float(catalog_entry["precio_sin_iva"]) if catalog_entry else 0.0
        catalog_entry_id = catalog_entry["id"] if catalog_entry else None

        resource = {
            "item_id": item_id,
            "org_id": org_id,
            "tipo": "mano_obra",
            "codigo": codigo,
            "descripcion": mo.get("descripcion", ""),
            "unidad": "día",
            "cantidad": 0,
            "desperdicio_pct": 0,
            "precio_unitario": precio_unitario,
            "catalog_entry_id": catalog_entry_id,
            "trabajadores": trabajadores,
            "dias": total_dias,
            "cargas_sociales_pct": cargas_sociales_pct,
        }
        calc_resource_subtotal(resource)
        rows.append(resource)

    # ── equipos ─────────────────────────────────────────────────────────────
    for eq in recursos.get("equipos", []):
        codigo = eq.get("codigo", "")
        qty_por_unidad = float(eq.get("cantidad_por_unidad") or 0)
        total_qty = qty_por_unidad * item_cantidad
        desperdicio_pct = float(eq.get("desperdicio_pct") or 0)

        catalog_entry = _find_catalog_entry(db, org_id, codigo)
        precio_unitario = float(catalog_entry["precio_sin_iva"]) if catalog_entry else 0.0
        catalog_entry_id = catalog_entry["id"] if catalog_entry else None

        resource = {
            "item_id": item_id,
            "org_id": org_id,
            "tipo": "equipo",
            "codigo": codigo,
            "descripcion": eq.get("descripcion", ""),
            "unidad": eq.get("unidad", "día"),
            "cantidad": total_qty,
            "desperdicio_pct": desperdicio_pct,
            "precio_unitario": precio_unitario,
            "catalog_entry_id": catalog_entry_id,
            "trabajadores": 0,
            "dias": 0,
            "cargas_sociales_pct": 0,
        }
        calc_resource_subtotal(resource)
        rows.append(resource)

    # ── mo_materiales ───────────────────────────────────────────────────────
    for mom in recursos.get("mo_materiales", []):
        codigo = mom.get("codigo", "")
        qty_por_unidad = float(mom.get("cantidad_por_unidad") or 0)
        total_qty = qty_por_unidad * item_cantidad
        desperdicio_pct = float(mom.get("desperdicio_pct") or 0)

        catalog_entry = _find_catalog_entry(db, org_id, codigo)
        precio_unitario = float(catalog_entry["precio_sin_iva"]) if catalog_entry else 0.0
        catalog_entry_id = catalog_entry["id"] if catalog_entry else None

        resource = {
            "item_id": item_id,
            "org_id": org_id,
            "tipo": "mo_material",
            "codigo": codigo,
            "descripcion": mom.get("descripcion", ""),
            "unidad": mom.get("unidad", "u"),
            "cantidad": total_qty,
            "desperdicio_pct": desperdicio_pct,
            "precio_unitario": precio_unitario,
            "catalog_entry_id": catalog_entry_id,
            "trabajadores": 0,
            "dias": 0,
            "cargas_sociales_pct": 0,
        }
        calc_resource_subtotal(resource)
        rows.append(resource)

    # ── subcontratos ────────────────────────────────────────────────────────
    for sub in recursos.get("subcontratos", []):
        codigo = sub.get("codigo", "")
        qty_por_unidad = float(sub.get("cantidad_por_unidad") or 0)
        total_qty = qty_por_unidad * item_cantidad
        desperdicio_pct = float(sub.get("desperdicio_pct") or 0)

        catalog_entry = _find_catalog_entry(db, org_id, codigo)
        precio_unitario = float(catalog_entry["precio_sin_iva"]) if catalog_entry else 0.0
        catalog_entry_id = catalog_entry["id"] if catalog_entry else None

        resource = {
            "item_id": item_id,
            "org_id": org_id,
            "tipo": "subcontrato",
            "codigo": codigo,
            "descripcion": sub.get("descripcion", ""),
            "unidad": sub.get("unidad", "gl"),
            "cantidad": total_qty,
            "desperdicio_pct": desperdicio_pct,
            "precio_unitario": precio_unitario,
            "catalog_entry_id": catalog_entry_id,
            "trabajadores": 0,
            "dias": 0,
            "cargas_sociales_pct": 0,
        }
        calc_resource_subtotal(resource)
        rows.append(resource)

    if not rows:
        return []

    try:
        result = db.table("item_resources").insert(rows).execute()
        return result.data or []
    except Exception:
        logger.warning("Failed to insert resources for item %s", item_id, exc_info=True)
        return []


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
      - recursos (optional): AI-generated resource composition
    Groups items by section and creates parent items for each section.
    After inserting resources, recalculates each item's unit prices from resources.
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
        return {"inserted": 0, "sections_created": 0, "resources_created": 0}

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
    total_resources_created = 0

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

        # Create child items, then add resources
        for ii, item in enumerate(sec_items):
            item_cantidad = float(item.get("cantidad", 1))
            row = {
                "budget_id": str(budget_id),
                "org_id": org_id,
                "code": item.get("codigo", f"{sec_code}.{ii + 1}"),
                "description": item.get("descripcion", "Item IA"),
                "unidad": item.get("unidad", "u"),
                "cantidad": item_cantidad,
                "notas": item.get("notas", "Sugerido por IA"),
                "notas_calculo": item.get("notas_calculo", ""),
                "sort_order": sort_base + ii + 1,
                "mat_unitario": 0,
                "mo_unitario": 0,
                "mat_total": 0,
                "mo_total": 0,
                "directo_total": 0,
                "neto_total": 0,
            }
            if parent_id:
                row["parent_id"] = parent_id

            result = db.table("budget_items").insert(row).execute()
            if not result.data:
                continue
            total_inserted += 1
            new_item_id = result.data[0]["id"]

            # Create resources if the item has them
            recursos = item.get("recursos")
            if isinstance(recursos, dict):
                inserted_resources = _create_resources_for_item(
                    db,
                    item_id=new_item_id,
                    org_id=org_id,
                    item_cantidad=item_cantidad,
                    recursos=recursos,
                )
                resources_count = len(inserted_resources)
                total_resources_created += resources_count

                if resources_count > 0:
                    # Recalculate item unit prices from the inserted resources
                    try:
                        calc_item_from_resources(row, inserted_resources)
                        db.table("budget_items").update({
                            "mat_unitario": row.get("mat_unitario", 0),
                            "mo_unitario": row.get("mo_unitario", 0),
                            "mat_total": row.get("mat_total", 0),
                            "mo_total": row.get("mo_total", 0),
                            "directo_total": row.get("directo_total", 0),
                            "neto_total": row.get("directo_total", 0),
                        }).eq("id", new_item_id).execute()
                    except Exception:
                        logger.warning(
                            "Failed to recalculate item %s from resources",
                            new_item_id,
                            exc_info=True,
                        )

    return {
        "inserted": total_inserted,
        "sections_created": sections_created,
        "resources_created": total_resources_created,
    }
