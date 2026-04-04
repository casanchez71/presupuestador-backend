import type {
  Budget,
  BudgetItem,
  ItemResource,
  PriceCatalog,
  CatalogEntry,
  AnalysisResponse,
  IndirectConfig,
  BudgetVersion,
  TreeNode,
} from '../types'

const BASE_URL = (import.meta.env.VITE_API_URL as string) || '/api'

function getToken(): string | null {
  return localStorage.getItem('sb-auth-token')
}

function authHeaders(): HeadersInit {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${res.status}: ${text}`)
  }
  return res.json() as Promise<T>
}

async function postFile<T>(path: string, formData: FormData): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: { ...authHeaders() },
    body: formData,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${res.status}: ${text}`)
  }
  return res.json() as Promise<T>
}

async function getBlob(path: string): Promise<Blob> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { ...authHeaders() },
  })
  if (!res.ok) throw new Error(`${res.status}`)
  return res.blob()
}

function get<T>(path: string) {
  return request<T>('GET', path)
}
function post<T>(path: string, body?: unknown) {
  return request<T>('POST', path, body)
}
function patch<T>(path: string, body?: unknown) {
  return request<T>('PATCH', path, body)
}
function del<T>(path: string) {
  return request<T>('DELETE', path)
}

// ─── Budget API ────────────────────────────────────────────────────────────────

export const budgetApi = {
  list: () => get<Budget[]>('/budgets'),
  create: (data: Partial<Budget>) => post<Budget>('/budgets', data),
  get: (id: string) => get<Budget>(`/budgets/${id}`),
  update: (id: string, data: Partial<Budget>) => patch<Budget>(`/budgets/${id}`, data),
  remove: (id: string) => del<void>(`/budgets/${id}`),

  // Items
  getItems: (id: string) => get<BudgetItem[]>(`/budgets/${id}/items`),
  createItem: (id: string, data: Partial<BudgetItem>) =>
    post<BudgetItem>(`/budgets/${id}/items`, data),
  updateItem: (budgetId: string, itemId: string, data: Partial<BudgetItem>) =>
    patch<BudgetItem>(`/budgets/${budgetId}/items/${itemId}`, data),
  deleteItem: (budgetId: string, itemId: string) =>
    del<void>(`/budgets/${budgetId}/items/${itemId}`),

  // Resources
  getItemResources: (budgetId: string, itemId: string) =>
    get<ItemResource[]>(`/budgets/${budgetId}/items/${itemId}/resources`),

  // Tree / Full
  getTree: (id: string) => get<TreeNode[]>(`/budgets/${id}/tree`),
  getFull: (id: string) => get<{ budget: Budget; tree: TreeNode[] }>(`/budgets/${id}/full`),

  // Recalculate / Copy
  recalculate: (id: string) => post<Budget>(`/budgets/${id}/recalculate`),
  copy: (id: string) => post<Budget>(`/budgets/${id}/copy`),

  // Excel import/export
  importExcel: (formData: FormData) => postFile<Budget>('/budgets/import-excel', formData),
  exportExcel: (id: string) => getBlob(`/budgets/${id}/export/excel`),
  exportPdf: (id: string) => getBlob(`/budgets/${id}/export/pdf`),

  // AI Plan analysis
  analyzePlan: (id: string, formData: FormData) =>
    postFile<{ items: BudgetItem[] }>(`/budgets/${id}/analyze-plan`, formData),
  addItemsFromAI: (id: string, items: Partial<BudgetItem>[]) =>
    post<BudgetItem[]>(`/budgets/${id}/items/from-ai`, { items }),

  // Indirects
  getIndirects: (id: string) => get<IndirectConfig>(`/budgets/${id}/indirects`),
  updateIndirects: (id: string, data: Partial<IndirectConfig>) =>
    patch<IndirectConfig>(`/budgets/${id}/indirects`, data),

  // Analysis
  getAnalysis: (id: string) => get<AnalysisResponse>(`/budgets/${id}/analysis`),

  // Versions
  getVersions: (id: string) => get<BudgetVersion[]>(`/budgets/${id}/versions`),
  createVersion: (id: string) => post<BudgetVersion>(`/budgets/${id}/versions`),
  getVersion: (id: string, vid: string) => get<BudgetVersion>(`/budgets/${id}/versions/${vid}`),
}

// ─── Catalog API ───────────────────────────────────────────────────────────────

export const catalogApi = {
  list: () => get<PriceCatalog[]>('/catalogs'),
  getEntries: (id: string) => get<CatalogEntry[]>(`/catalogs/${id}/entries`),
  search: (id: string, q: string) =>
    get<CatalogEntry[]>(`/catalogs/${id}/search?q=${encodeURIComponent(q)}`),
  apply: (budgetId: string, catalogId: string) =>
    post<{ updated: number }>(`/catalogs/apply/${budgetId}/${catalogId}`),
}
