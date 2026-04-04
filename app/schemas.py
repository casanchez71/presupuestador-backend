from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


# ── Budgets ──────────────────────────────────────────────────────────────────

class BudgetCreate(BaseModel):
    name: str
    description: str | None = None


class BudgetResponse(BaseModel):
    id: str
    org_id: str
    name: str
    description: str | None
    source_file: str | None
    status: str
    created_at: str
    updated_at: str


# ── Budget items ─────────────────────────────────────────────────────────────

class BudgetItemCreate(BaseModel):
    parent_id: UUID | None = None
    code: str | None = None
    description: str
    unidad: str | None = None
    cantidad: float | None = None
    mat_unitario: float | None = None
    mo_unitario: float | None = None
    mat_total: float | None = None
    mo_total: float | None = None
    directo_total: float | None = None
    indirecto_total: float | None = None
    beneficio_total: float | None = None
    neto_total: float | None = None
    notas: str | None = None


class BudgetItemUpdate(BaseModel):
    parent_id: UUID | None = None
    code: str | None = None
    description: str | None = None
    unidad: str | None = None
    cantidad: float | None = None
    mat_unitario: float | None = None
    mo_unitario: float | None = None
    mat_total: float | None = None
    mo_total: float | None = None
    directo_total: float | None = None
    indirecto_total: float | None = None
    beneficio_total: float | None = None
    neto_total: float | None = None
    notas: str | None = None


# ── Analysis ─────────────────────────────────────────────────────────────────

class IndirectApplyRequest(BaseModel):
    config_id: UUID | None = None


class AnalysisResponse(BaseModel):
    budget_id: str
    mat_total: float
    mo_total: float
    directo_total: float
    indirecto_total: float
    beneficio_total: float
    neto_total: float
    items_count: int


# ── Catalogs ────────────────────────────────────────────────────────────────

class CatalogResponse(BaseModel):
    id: str
    org_id: str
    name: str
    source_file: str | None
    created_at: str


class CatalogEntryResponse(BaseModel):
    id: str
    catalog_id: str
    tipo: str | None
    codigo: str | None
    descripcion: str | None
    unidad: str | None
    precio_con_iva: float | None
    precio_sin_iva: float | None
    referencia: str | None


class ApplyCatalogResult(BaseModel):
    items_matched: int
    items_unmatched: int
    total_updated: float


# ── Budget update ──────────────────────────────────────────────────────────

class BudgetUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None


# ── Indirect config update ──────────────────────────────────────────────────

class IndirectConfigUpdate(BaseModel):
    estructura_pct: float | None = None
    jefatura_pct: float | None = None
    logistica_pct: float | None = None
    herramientas_pct: float | None = None


# ── Budget copy ─────────────────────────────────────────────────────────────

class BudgetCopyRequest(BaseModel):
    name: str | None = None


# ── Versions ─────────────────────────────────────────────────────────────────

class VersionCreate(BaseModel):
    notes: str | None = None
