-- =============================================================
-- MIGRACION: Presupuestador v2 — Schema completo
-- Ejecutar en: Supabase SQL Editor
-- Prerequisitos: tabla organizations(id), funcion get_my_org_ids()
-- =============================================================

-- 1. budgets
CREATE TABLE IF NOT EXISTS budgets (
  id          uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id      uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name        text NOT NULL,
  description text,
  source_file text,
  status      text DEFAULT 'draft',
  created_at  timestamptz DEFAULT now(),
  updated_at  timestamptz DEFAULT now()
);

ALTER TABLE budgets ENABLE ROW LEVEL SECURITY;
CREATE POLICY "budgets_org" ON budgets FOR ALL
  USING (org_id IN (SELECT public.get_my_org_ids()));


-- 2. budget_items (with cost breakdown)
CREATE TABLE IF NOT EXISTS budget_items (
  id              uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  budget_id       uuid NOT NULL REFERENCES budgets(id) ON DELETE CASCADE,
  org_id          uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  parent_id       uuid REFERENCES budget_items(id) ON DELETE SET NULL,
  code            text,
  description     text,
  unidad          text,
  cantidad        numeric,

  -- Direct costs
  mat_unitario    numeric DEFAULT 0,
  mo_unitario     numeric DEFAULT 0,
  mat_total       numeric DEFAULT 0,
  mo_total        numeric DEFAULT 0,
  directo_total   numeric DEFAULT 0,

  -- Indirect + benefits + net
  indirecto_total numeric DEFAULT 0,
  beneficio_total numeric DEFAULT 0,
  neto_total      numeric DEFAULT 0,

  notas           text,
  sort_order      integer DEFAULT 0,
  created_at      timestamptz DEFAULT now()
);

ALTER TABLE budget_items ENABLE ROW LEVEL SECURITY;
CREATE POLICY "budget_items_org" ON budget_items FOR ALL
  USING (org_id IN (SELECT public.get_my_org_ids()));


-- 3. item_resources (detail: materials, labor, equipment, subcontracts per item)
CREATE TABLE IF NOT EXISTS item_resources (
  id                  uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  item_id             uuid NOT NULL REFERENCES budget_items(id) ON DELETE CASCADE,
  org_id              uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  tipo                text NOT NULL CHECK (tipo IN ('material', 'mano_obra', 'equipo', 'subcontrato')),
  codigo              text,
  descripcion         text,
  unidad              text,
  cantidad            numeric,
  desperdicio_pct     numeric DEFAULT 0,
  cantidad_efectiva   numeric,
  precio_unitario     numeric,
  subtotal            numeric DEFAULT 0
);

ALTER TABLE item_resources ENABLE ROW LEVEL SECURITY;
CREATE POLICY "item_resources_org" ON item_resources FOR ALL
  USING (org_id IN (SELECT public.get_my_org_ids()));


-- 4. price_catalogs
CREATE TABLE IF NOT EXISTS price_catalogs (
  id          uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id      uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name        text NOT NULL,
  source_file text,
  created_at  timestamptz DEFAULT now()
);

ALTER TABLE price_catalogs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "price_catalogs_org" ON price_catalogs FOR ALL
  USING (org_id IN (SELECT public.get_my_org_ids()));


-- 5. catalog_entries
CREATE TABLE IF NOT EXISTS catalog_entries (
  id              uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  catalog_id      uuid NOT NULL REFERENCES price_catalogs(id) ON DELETE CASCADE,
  org_id          uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  tipo            text NOT NULL CHECK (tipo IN ('material', 'mano_obra', 'equipo', 'subcontrato')),
  codigo          text,
  descripcion     text,
  unidad          text,
  precio_con_iva  numeric,
  precio_sin_iva  numeric,
  referencia      text
);

ALTER TABLE catalog_entries ENABLE ROW LEVEL SECURITY;
CREATE POLICY "catalog_entries_org" ON catalog_entries FOR ALL
  USING (org_id IN (SELECT public.get_my_org_ids()));


-- 6. indirect_config
CREATE TABLE IF NOT EXISTS indirect_config (
  id               uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id           uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE UNIQUE,
  estructura_pct   numeric DEFAULT 0.15,
  jefatura_pct     numeric DEFAULT 0.08,
  logistica_pct    numeric DEFAULT 0.05,
  herramientas_pct numeric DEFAULT 0.03,
  updated_at       timestamptz DEFAULT now()
);

ALTER TABLE indirect_config ENABLE ROW LEVEL SECURITY;
CREATE POLICY "indirect_config_org" ON indirect_config FOR ALL
  USING (org_id IN (SELECT public.get_my_org_ids()));


-- 7. budget_versions
CREATE TABLE IF NOT EXISTS budget_versions (
  id          uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  budget_id   uuid NOT NULL REFERENCES budgets(id) ON DELETE CASCADE,
  org_id      uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  version     integer NOT NULL,
  data        jsonb NOT NULL,
  created_at  timestamptz DEFAULT now(),
  created_by  uuid REFERENCES auth.users(id)
);

ALTER TABLE budget_versions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "budget_versions_org" ON budget_versions FOR ALL
  USING (org_id IN (SELECT public.get_my_org_ids()));


-- 8. audit_logs
CREATE TABLE IF NOT EXISTS audit_logs (
  id          uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id      uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id     uuid NOT NULL REFERENCES auth.users(id),
  budget_id   uuid NOT NULL,
  item_id     text NOT NULL,
  action      text NOT NULL,
  changes     jsonb NOT NULL,
  timestamp   timestamptz DEFAULT now()
);

ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "audit_logs_org" ON audit_logs FOR ALL
  USING (org_id IN (SELECT public.get_my_org_ids()));
