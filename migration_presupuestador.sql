-- =============================================================
-- MIGRACIÓN: Módulo Presupuestador
-- Ejecutar en: Supabase SQL Editor
-- NOTA: usa subquery IN (SELECT ...) porque get_my_org_ids()
--       es SETOF y no puede usarse directo en policy expressions
-- =============================================================

-- 1. price_snapshots
CREATE TABLE IF NOT EXISTS price_snapshots (
  id          uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id      uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id     uuid NOT NULL REFERENCES auth.users(id),
  file_name   text NOT NULL,
  data        jsonb NOT NULL,
  created_at  timestamptz DEFAULT now()
);

ALTER TABLE price_snapshots ENABLE ROW LEVEL SECURITY;

CREATE POLICY "price_snapshots_org_isolation"
  ON price_snapshots FOR ALL
  USING (org_id IN (SELECT public.get_my_org_ids()));

-- 2. audit_logs
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

CREATE POLICY "audit_logs_org_isolation"
  ON audit_logs FOR ALL
  USING (org_id IN (SELECT public.get_my_org_ids()));

-- 3. budgets
CREATE TABLE IF NOT EXISTS budgets (
  id          uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id      uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name        text NOT NULL,
  description text,
  status      text DEFAULT 'draft',
  created_at  timestamptz DEFAULT now(),
  updated_at  timestamptz DEFAULT now()
);

ALTER TABLE budgets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "budgets_org_isolation"
  ON budgets FOR ALL
  USING (org_id IN (SELECT public.get_my_org_ids()));

-- 4. budget_items (árbol jerárquico)
CREATE TABLE IF NOT EXISTS budget_items (
  id              uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  budget_id       uuid NOT NULL REFERENCES budgets(id) ON DELETE CASCADE,
  org_id          uuid NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  parent_id       uuid REFERENCES budget_items(id) ON DELETE SET NULL,
  code            text,
  description     text,
  unidad          text,
  cantidad        numeric,
  precio_unitario numeric,
  subtotal        numeric GENERATED ALWAYS AS (
                    COALESCE(cantidad, 0) * COALESCE(precio_unitario, 0)
                  ) STORED,
  notas           text,
  created_at      timestamptz DEFAULT now()
);

ALTER TABLE budget_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "budget_items_org_isolation"
  ON budget_items FOR ALL
  USING (org_id IN (SELECT public.get_my_org_ids()));

-- 5. budget_versions (snapshots de versiones completas)
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

CREATE POLICY "budget_versions_org_isolation"
  ON budget_versions FOR ALL
  USING (org_id IN (SELECT public.get_my_org_ids()));

-- 6. indirect_config (configuración de indirectos por organización)
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

CREATE POLICY "indirect_config_org_isolation"
  ON indirect_config FOR ALL
  USING (org_id IN (SELECT public.get_my_org_ids()));
