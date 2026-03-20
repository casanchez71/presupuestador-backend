from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
import pandas as pd
from utils.supabase_client import supabase, get_current_user
from typing import Dict, List, Optional
import json
from datetime import datetime
import os
import re
from uuid import UUID
from io import BytesIO
from openai import AsyncOpenAI
import base64

app = FastAPI(title="Presupuestador Backend - Sprint 3")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── OpenAI ───────────────────────────────────────────────────────────────────
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
VISION_MODEL = os.getenv("OPENAI_MODEL_VISION", "gpt-4o")

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

class BudgetItemUpdate(BaseModel):
    parent_id: Optional[UUID] = None
    code: Optional[str] = None
    description: Optional[str] = None
    unidad: Optional[str] = None
    cantidad: Optional[float] = None
    precio_unitario: Optional[float] = None
    notas: Optional[str] = None

class IndirectApplyRequest(BaseModel):
    config_id: Optional[UUID] = None

class VersionCreate(BaseModel):
    notes: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

# ── Funciones auxiliares ─────────────────────────────────────────────────────
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

def get_budget_items(budget_id: str, org_id: str) -> List[Dict]:
    result = supabase.table("budget_items") \
        .select("*") \
        .eq("budget_id", budget_id) \
        .eq("org_id", org_id) \
        .execute()
    return result.data or []

def normalize_item_code(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    raw = str(value).strip().replace(",", ".")
    raw = re.sub(r"\s+", "", raw)
    return raw.strip(".")

def safe_float(value: object) -> Optional[float]:
    if value is None or pd.isna(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        cleaned = str(value).strip().replace(".", "").replace(",", ".")
        try:
            return float(cleaned)
        except (TypeError, ValueError):
            return None

def get_parent_candidates(code: str) -> List[str]:
    if not code:
        return []
    parts = [part for part in code.split(".") if part]
    if len(parts) > 1:
        return [".".join(parts[:i]) for i in range(len(parts) - 1, 0, -1)]
    return []

def read_obj_value(obj: object, key: str) -> object:
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)

async def analyze_plan_with_vision(file_content: bytes, filename: str, prompt: str) -> List[Dict]:
    base64_image = base64.b64encode(file_content).decode('utf-8')
    name_lower = filename.lower()
    mime_type = "image/jpeg" if name_lower.endswith(('.jpg', '.jpeg')) else "image/png"
    response = await openai_client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
        ]}],
        max_tokens=2000,
        temperature=0.4
    )
    try:
        suggestions_text = response.choices[0].message.content
        suggestions = json.loads(suggestions_text)
        return suggestions if isinstance(suggestions, list) else []
    except Exception:
        return [{"description": line.strip(), "cantidad_estimada": 1.0}
                for line in suggestions_text.split("\n") if line.strip()]

# ========================= SPRINT 0+1 =========================

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!doctype html>
    <html lang="es">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Presupuestador - Vista minima</title>
        <style>
          :root {
            --bg: #f3f5f9;
            --surface: #ffffff;
            --ink: #1f2937;
            --muted: #5b6471;
            --line: #d9dee8;
            --primary: #0f6fff;
            --primary-ink: #ffffff;
            --warn: #b42318;
            --ok: #027a48;
          }
          * { box-sizing: border-box; }
          body {
            margin: 0;
            color: var(--ink);
            background:
              radial-gradient(circle at 12% 10%, #dbe9ff 0%, #eef3ff 30%, transparent 55%),
              radial-gradient(circle at 82% 0%, #ffe6cf 0%, #fff1e3 24%, transparent 52%),
              var(--bg);
            font-family: "Trebuchet MS", "Lucida Sans Unicode", "Lucida Grande", sans-serif;
          }
          .wrap {
            max-width: 1080px;
            margin: 24px auto 40px;
            padding: 0 16px;
          }
          .hero {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 18px;
            box-shadow: 0 8px 24px rgba(20, 30, 55, 0.06);
          }
          h1 {
            font-family: "Palatino Linotype", "Book Antiqua", Palatino, serif;
            margin: 0 0 8px;
            font-size: 32px;
          }
          p {
            margin: 6px 0;
            color: var(--muted);
          }
          .links {
            margin-top: 10px;
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
          }
          .links a { color: var(--primary); text-decoration: none; font-weight: 700; }
          .links a:hover { text-decoration: underline; }
          .grid {
            margin-top: 14px;
            display: grid;
            grid-template-columns: 340px 1fr;
            gap: 14px;
          }
          .card {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 14px;
          }
          .card h2 {
            margin: 0 0 12px;
            font-size: 18px;
          }
          label {
            display: block;
            margin: 10px 0 6px;
            font-weight: 700;
            font-size: 14px;
          }
          input, textarea, button {
            font: inherit;
          }
          input, textarea {
            width: 100%;
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: 10px 11px;
            background: #fff;
          }
          textarea { min-height: 88px; resize: vertical; }
          .row {
            display: flex;
            gap: 8px;
            margin-top: 10px;
            flex-wrap: wrap;
          }
          button {
            border: 0;
            border-radius: 10px;
            padding: 10px 12px;
            cursor: pointer;
            font-weight: 700;
          }
          .btn-primary {
            background: var(--primary);
            color: var(--primary-ink);
          }
          .btn-secondary {
            background: #e8eef8;
            color: #284468;
          }
          .status {
            margin-top: 10px;
            padding: 9px 10px;
            border-radius: 10px;
            font-size: 14px;
            display: none;
          }
          .status.error { display: block; background: #fdeceb; color: var(--warn); border: 1px solid #f5b9b4; }
          .status.ok { display: block; background: #ebf9f1; color: var(--ok); border: 1px solid #b2e5cb; }
          .budget-list {
            margin-top: 12px;
            border-top: 1px solid var(--line);
            padding-top: 10px;
            display: grid;
            gap: 8px;
          }
          .budget-item {
            border: 1px solid var(--line);
            background: #f9fbff;
            border-radius: 10px;
            padding: 10px;
            cursor: pointer;
          }
          .budget-item:hover { border-color: #aac4f8; }
          .budget-item strong { display: block; color: #203a5f; }
          .meta {
            margin-top: 4px;
            font-size: 13px;
            color: var(--muted);
          }
          .summary {
            display: grid;
            grid-template-columns: repeat(2, minmax(140px, 1fr));
            gap: 10px;
            margin-bottom: 12px;
          }
          .pill {
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: 10px;
            background: #fbfcff;
          }
          .pill small {
            display: block;
            color: var(--muted);
            font-size: 12px;
          }
          .pill span {
            display: block;
            margin-top: 3px;
            font-weight: 700;
          }
          .tree ul {
            margin: 6px 0 0 20px;
            padding: 0;
          }
          .tree li {
            margin: 6px 0;
            color: #2d3642;
          }
          .empty {
            color: var(--muted);
            font-style: italic;
          }
          @media (max-width: 900px) {
            .grid { grid-template-columns: 1fr; }
          }
        </style>
      </head>
      <body>
        <div class="wrap">
          <section class="hero">
            <h1>Presupuestador</h1>
            <p>Esta es una pantalla minima para probar el backend sin Swagger.</p>
            <p>Primero inicia sesion con email y contrasena. Luego ya podes operar presupuestos.</p>
            <div class="links">
              <a href="/health" target="_blank" rel="noreferrer">/health</a>
              <a href="/docs" target="_blank" rel="noreferrer">/docs</a>
            </div>
          </section>

          <section class="grid">
            <article class="card">
              <h2>Acceso y acciones</h2>
              <label for="emailInput">Email</label>
              <input id="emailInput" type="email" placeholder="tu@email.com" />
              <label for="passwordInput">Contrasena</label>
              <input id="passwordInput" type="password" placeholder="Tu contrasena" />
              <div class="row">
                <button class="btn-primary" id="loginBtn">Iniciar sesion</button>
                <button class="btn-secondary" id="loadBudgetsBtn">Cargar presupuestos</button>
              </div>
              <div id="statusBox" class="status"></div>

              <details style="margin-top: 12px;">
                <summary style="cursor: pointer; font-weight: 700;">Avanzado: token manual</summary>
                <label for="tokenInput">Token de acceso</label>
                <textarea id="tokenInput" placeholder="Pega el token aqui"></textarea>
                <div class="row">
                  <button class="btn-secondary" id="saveTokenBtn">Guardar token manual</button>
                </div>
              </details>

              <label for="budgetName">Crear presupuesto</label>
              <input id="budgetName" placeholder="Nombre" />
              <label for="budgetDesc">Descripcion (opcional)</label>
              <input id="budgetDesc" placeholder="Descripcion" />
              <div class="row">
                <button class="btn-primary" id="createBudgetBtn">Crear presupuesto</button>
              </div>

              <div class="budget-list" id="budgetList"></div>
            </article>

            <article class="card">
              <h2>Detalle de presupuesto</h2>
              <div id="budgetDetail" class="empty">Selecciona un presupuesto para ver resumen y arbol.</div>
            </article>
          </section>
        </div>

        <script>
          const emailInput = document.getElementById("emailInput");
          const passwordInput = document.getElementById("passwordInput");
          const loginBtn = document.getElementById("loginBtn");
          const tokenInput = document.getElementById("tokenInput");
          const saveTokenBtn = document.getElementById("saveTokenBtn");
          const loadBudgetsBtn = document.getElementById("loadBudgetsBtn");
          const createBudgetBtn = document.getElementById("createBudgetBtn");
          const budgetNameInput = document.getElementById("budgetName");
          const budgetDescInput = document.getElementById("budgetDesc");
          const budgetList = document.getElementById("budgetList");
          const budgetDetail = document.getElementById("budgetDetail");
          const statusBox = document.getElementById("statusBox");

          function showStatus(message, type) {
            statusBox.textContent = message;
            statusBox.className = "status " + type;
          }

          function getToken() {
            const token = tokenInput.value.trim();
            if (!token) {
              showStatus("Primero inicia sesion. Si hace falta, usa token manual en Avanzado.", "error");
              return null;
            }
            return token;
          }

          function safeText(value) {
            return String(value || "")
              .replaceAll("&", "&amp;")
              .replaceAll("<", "&lt;")
              .replaceAll(">", "&gt;")
              .replaceAll('"', "&quot;")
              .replaceAll("'", "&#039;");
          }

          async function apiFetch(path, options = {}) {
            const token = getToken();
            if (!token) {
              throw new Error("missing_token");
            }
            const headers = options.headers || {};
            headers["Authorization"] = "Bearer " + token;
            if (!headers["Content-Type"] && options.body) {
              headers["Content-Type"] = "application/json";
            }
            const response = await fetch(path, { ...options, headers });
            if (!response.ok) {
              const text = await response.text();
              throw new Error(text || ("HTTP " + response.status));
            }
            return response.json();
          }

          async function login() {
            const email = emailInput.value.trim();
            const password = passwordInput.value;
            if (!email || !password) {
              showStatus("Completa email y contrasena para iniciar sesion.", "error");
              return;
            }
            try {
              const response = await fetch("/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
              });
              if (!response.ok) {
                const text = await response.text();
                throw new Error(text || ("HTTP " + response.status));
              }
              const data = await response.json();
              if (!data.access_token) {
                throw new Error("Respuesta de login sin access_token.");
              }
              tokenInput.value = data.access_token;
              localStorage.setItem("presupuestador.jwt", data.access_token);
              localStorage.setItem("presupuestador.email", email);
              passwordInput.value = "";
              showStatus("Sesion iniciada. Ya podes cargar presupuestos.", "ok");
              await loadBudgets();
            } catch (err) {
              showStatus("No se pudo iniciar sesion: " + err.message, "error");
            }
          }

          function money(value) {
            const num = Number(value || 0);
            return num.toLocaleString("es-AR", { style: "currency", currency: "ARS", maximumFractionDigits: 2 });
          }

          function renderTree(nodes) {
            if (!nodes || !nodes.length) {
              return "<div class='empty'>Sin items.</div>";
            }
            const renderNode = (node) => {
              const label = (node.code ? ("[" + node.code + "] ") : "") + (node.description || "Sin descripcion");
              const children = node.children && node.children.length
                ? "<ul>" + node.children.map(renderNode).join("") + "</ul>"
                : "";
              return "<li>" + label + children + "</li>";
            };
            return "<ul>" + nodes.map(renderNode).join("") + "</ul>";
          }

          function renderBudgetList(items) {
            if (!items.length) {
              budgetList.innerHTML = "<div class='empty'>No hay presupuestos para este usuario.</div>";
              return;
            }
            budgetList.innerHTML = items.map((item) => {
              const name = safeText(item.name || "Sin nombre");
              const date = item.created_at ? new Date(item.created_at).toLocaleString() : "-";
              return (
                "<button class='budget-item' data-id='" + item.id + "'>" +
                  "<strong>" + name + "</strong>" +
                  "<div class='meta'>ID: " + item.id + "</div>" +
                  "<div class='meta'>Creado: " + date + "</div>" +
                "</button>"
              );
            }).join("");
          }

          function renderFullBudget(data) {
            const b = data.budget || {};
            const a = data.analysis || {};
            budgetDetail.innerHTML =
              "<div class='summary'>" +
                "<div class='pill'><small>Presupuesto</small><span>" + (b.name || "Sin nombre") + "</span></div>" +
                "<div class='pill'><small>Versiones</small><span>" + (data.versions_count || 0) + "</span></div>" +
                "<div class='pill'><small>Total directo</small><span>" + money(a.total_directo) + "</span></div>" +
                "<div class='pill'><small>Total indirectos</small><span>" + money(a.total_indirectos) + "</span></div>" +
                "<div class='pill'><small>Gran total</small><span>" + money(a.gran_total) + "</span></div>" +
                "<div class='pill'><small>Items</small><span>" + (a.items_count || 0) + "</span></div>" +
              "</div>" +
              "<h3>Arbol de items</h3>" +
              "<div class='tree'>" + renderTree(data.tree || []) + "</div>";
          }

          async function loadBudgets() {
            try {
              const data = await apiFetch("/budgets");
              renderBudgetList(data || []);
              showStatus("Presupuestos cargados.", "ok");
            } catch (err) {
              if (String(err.message || "").includes("missing_token")) {
                return;
              }
              showStatus("No se pudieron cargar los presupuestos: " + err.message, "error");
            }
          }

          async function createBudget() {
            const name = budgetNameInput.value.trim();
            const description = budgetDescInput.value.trim();
            if (!name) {
              showStatus("El nombre del presupuesto es obligatorio.", "error");
              return;
            }
            try {
              await apiFetch("/budgets", {
                method: "POST",
                body: JSON.stringify({ name, description: description || null })
              });
              budgetNameInput.value = "";
              budgetDescInput.value = "";
              showStatus("Presupuesto creado.", "ok");
              await loadBudgets();
            } catch (err) {
              if (String(err.message || "").includes("missing_token")) {
                return;
              }
              showStatus("No se pudo crear el presupuesto: " + err.message, "error");
            }
          }

          async function openBudget(id) {
            try {
              const data = await apiFetch("/budget/" + id + "/full");
              renderFullBudget(data);
              showStatus("Detalle cargado.", "ok");
            } catch (err) {
              if (String(err.message || "").includes("missing_token")) {
                return;
              }
              showStatus("No se pudo cargar el detalle: " + err.message, "error");
            }
          }

          saveTokenBtn.addEventListener("click", () => {
            const token = tokenInput.value.trim();
            if (!token) {
              showStatus("No hay token para guardar.", "error");
              return;
            }
            localStorage.setItem("presupuestador.jwt", token);
            showStatus("Token guardado en este navegador.", "ok");
          });

          loginBtn.addEventListener("click", login);
          loadBudgetsBtn.addEventListener("click", loadBudgets);
          createBudgetBtn.addEventListener("click", createBudget);

          budgetList.addEventListener("click", (event) => {
            const target = event.target.closest("button[data-id]");
            if (!target) {
              return;
            }
            openBudget(target.dataset.id);
          });

          const savedToken = localStorage.getItem("presupuestador.jwt");
          if (savedToken) {
            tokenInput.value = savedToken;
          }
          const savedEmail = localStorage.getItem("presupuestador.email");
          if (savedEmail) {
            emailInput.value = savedEmail;
          }
          if (savedToken) {
            showStatus("Sesion recordada en este navegador.", "ok");
          }
        </script>
      </body>
    </html>
    """

@app.post("/auth/login")
async def auth_login(payload: LoginRequest):
    email = payload.email.strip().lower()
    password = payload.password
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email y contrasena son obligatorios")

    try:
        auth_result = supabase.auth.sign_in_with_password({"email": email, "password": password})
    except Exception:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")

    session = read_obj_value(auth_result, "session")
    user = read_obj_value(auth_result, "user")
    access_token = read_obj_value(session, "access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="No se pudo crear sesion")

    user_id = read_obj_value(user, "id")
    user_email = read_obj_value(user, "email") or email
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user_id,
        "email": user_email
    }

@app.get("/health")
def health_check():
    return {"status": "OK", "timestamp": datetime.utcnow().isoformat()}

@app.post("/budgets")
async def create_budget(budget: BudgetCreate, current_user: Dict = Depends(get_current_user)):
    result = supabase.table("budgets").insert({
        "org_id": current_user["tenant_id"],
        "name": budget.name,
        "description": budget.description,
        "status": "draft"
    }).execute()
    return result.data[0]

@app.get("/budgets")
async def list_budgets(current_user: Dict = Depends(get_current_user)):
    result = supabase.table("budgets").select("*").eq("org_id", current_user["tenant_id"]).execute()
    return result.data or []

@app.get("/budget/{budget_id}")
async def get_budget(budget_id: UUID, current_user: Dict = Depends(get_current_user)):
    result = supabase.table("budgets").select("*") \
        .eq("id", str(budget_id)).eq("org_id", current_user["tenant_id"]).single().execute()
    if not result.data:
        raise HTTPException(404, "Presupuesto no encontrado")
    return result.data

@app.delete("/budget/{budget_id}")
async def delete_budget(budget_id: UUID, current_user: Dict = Depends(get_current_user)):
    result = supabase.table("budgets").delete() \
        .eq("id", str(budget_id)).eq("org_id", current_user["tenant_id"]).execute()
    return {"message": "Eliminado" if result.data else "No encontrado"}

@app.post("/budget/{budget_id}/items")
async def create_items(budget_id: UUID, items: List[BudgetItemCreate], current_user: Dict = Depends(get_current_user)):
    to_insert = [{
        "budget_id": str(budget_id), "org_id": current_user["tenant_id"],
        "parent_id": str(item.parent_id) if item.parent_id else None,
        "code": item.code, "description": item.description,
        "unidad": item.unidad, "cantidad": item.cantidad,
        "precio_unitario": item.precio_unitario, "notas": item.notas
    } for item in items]
    result = supabase.table("budget_items").insert(to_insert).execute()
    return {"inserted": len(result.data)}

@app.patch("/budget/{budget_id}/item/{item_id}")
async def update_item(
    budget_id: UUID,
    item_id: UUID,
    payload: BudgetItemUpdate,
    current_user: Dict = Depends(get_current_user)
):
    org_id = current_user["tenant_id"]
    budget_id_str = str(budget_id)
    item_id_str = str(item_id)

    budget = supabase.table("budgets").select("id") \
        .eq("id", budget_id_str).eq("org_id", org_id).single().execute()
    if not budget.data:
        raise HTTPException(404, "Presupuesto no encontrado")

    existing = supabase.table("budget_items").select("*") \
        .eq("id", item_id_str).eq("budget_id", budget_id_str).eq("org_id", org_id) \
        .single().execute()
    if not existing.data:
        raise HTTPException(404, "Item no encontrado")

    update_data = payload.model_dump(exclude_unset=True)
    if "parent_id" in update_data:
        update_data["parent_id"] = str(update_data["parent_id"]) if update_data["parent_id"] else None

    changes = {}
    for field, new_value in update_data.items():
        old_value = existing.data.get(field)
        if old_value != new_value:
            changes[field] = {"before": old_value, "after": new_value}

    if not changes:
        return {"message": "Sin cambios para aplicar", "item": existing.data}

    supabase.table("budget_items").update(update_data) \
        .eq("id", item_id_str).eq("budget_id", budget_id_str).eq("org_id", org_id).execute()

    updated = supabase.table("budget_items").select("*") \
        .eq("id", item_id_str).eq("budget_id", budget_id_str).eq("org_id", org_id) \
        .single().execute()

    supabase.table("audit_logs").insert({
        "org_id": org_id,
        "user_id": current_user["user_id"],
        "budget_id": budget_id_str,
        "item_id": item_id_str,
        "action": "update",
        "changes": changes,
        "timestamp": datetime.utcnow().isoformat()
    }).execute()

    return {"message": "Item actualizado", "item": updated.data}

@app.get("/budget/{budget_id}/tree")
async def get_tree(budget_id: UUID, current_user: Dict = Depends(get_current_user)):
    items = get_budget_items(str(budget_id), current_user["tenant_id"])
    return {"budget_id": str(budget_id), "tree": build_tree(items)}

@app.post("/budget/import-excel")
async def import_excel(file: UploadFile = File(...), current_user: Dict = Depends(get_current_user)):
    contents = await file.read()
    df_dict = pd.read_excel(contents, sheet_name=None)
    precios: Dict[str, float] = {}
    if "00_Mat" in df_dict:
        for _, row in df_dict["00_Mat"].iterrows():
            code = normalize_item_code(row.get("CODIGO"))
            if code:
                price = row.get("PRECIO CON IVA")
                if price is None or pd.isna(price):
                    price = row.get("PRECIO SIN IVA")
                parsed_price = safe_float(price)
                if parsed_price is not None:
                    precios[code] = parsed_price

    parsed_items: List[Dict] = []
    if "01_C&P" in df_dict:
        for _, row in df_dict["01_C&P"].iterrows():
            desc = str(row.get("DESCRIPCIÓN", "")).strip()
            if not desc or desc == "nan":
                continue
            item_code = normalize_item_code(row.get("ITEM"))
            parsed_items.append({
                "code": item_code or None,
                "normalized_code": item_code,
                "description": desc,
                "unidad": row.get("UNIDAD"),
                "cantidad": safe_float(row.get("CANTIDAD")),
                "precio_unitario": precios.get(item_code) if item_code else None,
                "notas": "Importado desde Excel"
            })

    snapshot = supabase.table("price_snapshots").insert({
        "org_id": current_user["tenant_id"], "user_id": current_user["user_id"],
        "file_name": file.filename, "data": json.dumps({"precios": precios})
    }).execute()

    items_detected = len(parsed_items)
    if items_detected == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Excel procesado sin items utilizables en hoja 01_C&P",
                "snapshot_id": snapshot.data[0]["id"],
                "items_detected": 0
            }
        )

    base_name = os.path.splitext(os.path.basename(file.filename or "presupuesto"))[0].strip()
    budget_name = base_name if base_name else f"Presupuesto {datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    budget = supabase.table("budgets").insert({
        "org_id": current_user["tenant_id"],
        "name": budget_name,
        "description": f"Importado desde {file.filename}",
        "status": "draft"
    }).execute()
    budget_id = budget.data[0]["id"]

    code_to_id: Dict[str, str] = {}
    items_inserted = 0
    for row in parsed_items:
        parent_id = None
        for candidate in get_parent_candidates(row["normalized_code"]):
            if candidate in code_to_id:
                parent_id = code_to_id[candidate]
                break

        inserted = supabase.table("budget_items").insert({
            "budget_id": budget_id,
            "org_id": current_user["tenant_id"],
            "parent_id": parent_id,
            "code": row["code"],
            "description": row["description"],
            "unidad": row["unidad"],
            "cantidad": row["cantidad"],
            "precio_unitario": row["precio_unitario"],
            "notas": row["notas"]
        }).execute()

        if inserted.data:
            inserted_id = inserted.data[0]["id"]
            items_inserted += 1
            if row["normalized_code"]:
                code_to_id[row["normalized_code"]] = inserted_id

    return {
        "message": "Excel procesado e importado",
        "snapshot_id": snapshot.data[0]["id"],
        "budget_id": budget_id,
        "budget_name": budget_name,
        "items_detected": items_detected,
        "items_inserted": items_inserted
    }

# ========================= SPRINT 2 =========================

@app.post("/budget/{budget_id}/analyze-plan")
async def analyze_plan(budget_id: UUID, file: UploadFile = File(...),
                       prompt: Optional[str] = None, current_user: Dict = Depends(get_current_user)):
    budget = supabase.table("budgets").select("id").eq("id", str(budget_id)) \
        .eq("org_id", current_user["tenant_id"]).single().execute()
    if not budget.data:
        raise HTTPException(404, "Presupuesto no encontrado")
    content = await file.read()
    default_prompt = "Analiza este plano y extrae ítems de construcción en JSON: lista con code, description, unidad, cantidad_estimada."
    suggestions = await analyze_plan_with_vision(content, file.filename, prompt or default_prompt)
    return {"budget_id": str(budget_id), "suggestions": suggestions, "message": f"{len(suggestions)} ítems sugeridos"}

@app.post("/budget/{budget_id}/items/from-ai")
async def insert_ai_suggestions(budget_id: UUID, suggestions: List[Dict] = Body(...),
                                current_user: Dict = Depends(get_current_user)):
    if not supabase.table("budgets").select("id").eq("id", str(budget_id)) \
            .eq("org_id", current_user["tenant_id"]).execute().data:
        raise HTTPException(404, "Presupuesto no encontrado")
    to_insert = [{"budget_id": str(budget_id), "org_id": current_user["tenant_id"],
                  "parent_id": sug.get("parent_id"), "code": sug.get("code"),
                  "description": sug.get("description", "Ítem IA"), "unidad": sug.get("unidad", "u"),
                  "cantidad": sug.get("cantidad_estimada", 1.0), "precio_unitario": None,
                  "notas": "Sugerido por IA"} for sug in suggestions]
    result = supabase.table("budget_items").insert(to_insert).execute()
    return {"inserted": len(result.data)}

@app.post("/budget/{budget_id}/indirects")
async def apply_indirects(budget_id: UUID, request: IndirectApplyRequest = Body(default=IndirectApplyRequest()),
                          current_user: Dict = Depends(get_current_user)):
    config_q = supabase.table("indirect_config").select("*").eq("org_id", current_user["tenant_id"])
    if request.config_id:
        config_q = config_q.eq("id", str(request.config_id))
    config_result = config_q.limit(1).execute()
    if not config_result.data:
        raise HTTPException(404, "Configuración de indirectos no encontrada")
    config = config_result.data[0]
    items = get_budget_items(str(budget_id), current_user["tenant_id"])
    if not items:
        raise HTTPException(404, "No hay ítems en el presupuesto")
    total_directo = sum((i["cantidad"] or 0) * (i["precio_unitario"] or 0) for i in items)
    total_indirectos = total_directo * sum([
        config["estructura_pct"] or 0, config["jefatura_pct"] or 0,
        config["logistica_pct"] or 0, config["herramientas_pct"] or 0
    ])
    for item in items:
        item_directo = (item["cantidad"] or 0) * (item["precio_unitario"] or 0)
        indirecto_item = (item_directo / total_directo * total_indirectos) if total_directo > 0 else 0
        supabase.table("budget_items").update({
            "indirecto": indirecto_item,
            "total_con_indirecto": item_directo + indirecto_item
        }).eq("id", item["id"]).execute()
    return {"total_directo": total_directo, "total_indirectos": total_indirectos,
            "items_updated": len(items), "config_used": config["id"]}

@app.get("/budget/{budget_id}/analysis")
async def get_analysis(budget_id: UUID, current_user: Dict = Depends(get_current_user)):
    items = get_budget_items(str(budget_id), current_user["tenant_id"])
    if not items:
        raise HTTPException(404, "Presupuesto vacío o sin acceso")
    total_directo = sum((i["cantidad"] or 0) * (i["precio_unitario"] or 0) for i in items)
    total_indirectos = sum(i.get("indirecto") or 0 for i in items)
    gran_total = sum(i.get("total_con_indirecto") or 0 for i in items)
    return {"budget_id": str(budget_id), "total_directo": total_directo,
            "total_indirectos": total_indirectos, "gran_total": gran_total, "items_count": len(items)}

@app.get("/budget/{budget_id}/full")
async def get_budget_full(budget_id: UUID, current_user: Dict = Depends(get_current_user)):
    budget_id_str = str(budget_id)
    org_id = current_user["tenant_id"]
    budget = supabase.table("budgets").select("*") \
        .eq("id", budget_id_str).eq("org_id", org_id).single().execute()
    if not budget.data:
        raise HTTPException(404, "Presupuesto no encontrado")

    items = get_budget_items(budget_id_str, org_id)
    tree = build_tree(items)
    total_directo = sum((i["cantidad"] or 0) * (i["precio_unitario"] or 0) for i in items)
    total_indirectos = sum(i.get("indirecto") or 0 for i in items)
    gran_total = sum(i.get("total_con_indirecto") or 0 for i in items)

    versions = supabase.table("budget_versions").select("id") \
        .eq("budget_id", budget_id_str).eq("org_id", org_id).execute()

    return {
        "budget": budget.data,
        "tree": tree,
        "analysis": {
            "budget_id": budget_id_str,
            "total_directo": total_directo,
            "total_indirectos": total_indirectos,
            "gran_total": gran_total,
            "items_count": len(items)
        },
        "versions_count": len(versions.data or [])
    }

# ========================= SPRINT 3 =========================

@app.get("/budget/{budget_id}/export/excel")
async def export_budget_excel(budget_id: UUID, current_user: Dict = Depends(get_current_user)):
    budget = supabase.table("budgets").select("id, name").eq("id", str(budget_id)) \
        .eq("org_id", current_user["tenant_id"]).single().execute()
    if not budget.data:
        raise HTTPException(404, "Presupuesto no encontrado")
    items = get_budget_items(str(budget_id), current_user["tenant_id"])
    if not items:
        raise HTTPException(404, "Presupuesto sin ítems")
    rows = [{
        "Código": i.get("code", ""), "Descripción": i.get("description", ""),
        "Unidad": i.get("unidad", ""), "Cantidad": i.get("cantidad", 0),
        "Precio Unitario": i.get("precio_unitario", 0),
        "Subtotal Directo": (i.get("cantidad") or 0) * (i.get("precio_unitario") or 0),
        "Indirecto": i.get("indirecto", 0),
        "Total": i.get("total_con_indirecto", 0),
        "Notas": i.get("notas", "")
    } for i in items]
    df = pd.DataFrame(rows)
    total_row = {"Código": "TOTAL", "Descripción": "", "Unidad": "", "Cantidad": "",
                 "Precio Unitario": "", "Subtotal Directo": df["Subtotal Directo"].sum(),
                 "Indirecto": df["Indirecto"].sum(), "Total": df["Total"].sum(), "Notas": ""}
    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Presupuesto")
    output.seek(0)
    filename = f"presupuesto_{budget.data['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    return StreamingResponse(output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"})

@app.post("/budget/{budget_id}/version")
async def create_version(budget_id: UUID, version: VersionCreate = Body(...),
                         current_user: Dict = Depends(get_current_user)):
    budget = supabase.table("budgets").select("id, name").eq("id", str(budget_id)) \
        .eq("org_id", current_user["tenant_id"]).single().execute()
    if not budget.data:
        raise HTTPException(404, "Presupuesto no encontrado")
    items = get_budget_items(str(budget_id), current_user["tenant_id"])
    config = supabase.table("indirect_config").select("*").eq("org_id", current_user["tenant_id"]) \
        .order("updated_at", desc=True).limit(1).execute()
    # Obtener el número de versión (autoincremental)
    existing = supabase.table("budget_versions").select("version") \
        .eq("budget_id", str(budget_id)).order("version", desc=True).limit(1).execute()
    next_version = (existing.data[0]["version"] + 1) if existing.data else 1
    result = supabase.table("budget_versions").insert({
        "budget_id": str(budget_id), "org_id": current_user["tenant_id"],
        "version": next_version,
        "data": json.dumps({"budget": budget.data, "items": items,
                            "indirect_config": config.data[0] if config.data else {},
                            "timestamp": datetime.utcnow().isoformat(), "notes": version.notes}),
        "created_by": current_user["user_id"]
    }).execute()
    return {"version_id": result.data[0]["id"], "version": next_version, "message": "Versión guardada"}

@app.get("/budget/{budget_id}/versions")
async def list_versions(budget_id: UUID, current_user: Dict = Depends(get_current_user)):
    result = supabase.table("budget_versions").select("id, version, created_at, created_by") \
        .eq("budget_id", str(budget_id)).eq("org_id", current_user["tenant_id"]) \
        .order("created_at", desc=True).execute()
    return result.data or []

@app.get("/budget/{budget_id}/version/{version_id}")
async def get_version(budget_id: UUID, version_id: UUID, current_user: Dict = Depends(get_current_user)):
    version = supabase.table("budget_versions").select("*") \
        .eq("id", str(version_id)).eq("budget_id", str(budget_id)) \
        .eq("org_id", current_user["tenant_id"]).single().execute()
    if not version.data:
        raise HTTPException(404, "Versión no encontrada")
    return {"version_id": str(version_id), "timestamp": version.data["created_at"],
            "snapshot": json.loads(version.data["data"])}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
