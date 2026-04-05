-- 003_unit_analysis.sql
-- Adds support for unit price analysis (análisis de precio unitario)

-- 1. Add 'mo_material' tipo to item_resources (for indirect materials: nails, formwork, wire)
ALTER TABLE item_resources DROP CONSTRAINT IF EXISTS item_resources_tipo_check;
ALTER TABLE item_resources ADD CONSTRAINT item_resources_tipo_check
  CHECK (tipo IN ('material', 'mano_obra', 'equipo', 'subcontrato', 'mo_material'));

-- 2. Add labor-specific columns to item_resources
ALTER TABLE item_resources ADD COLUMN IF NOT EXISTS trabajadores numeric DEFAULT 0;
ALTER TABLE item_resources ADD COLUMN IF NOT EXISTS dias numeric DEFAULT 0;
ALTER TABLE item_resources ADD COLUMN IF NOT EXISTS cargas_sociales_pct numeric DEFAULT 25;

-- 3. Link resource to catalog entry
ALTER TABLE item_resources ADD COLUMN IF NOT EXISTS catalog_entry_id uuid REFERENCES catalog_entries(id) ON DELETE SET NULL;

-- 4. Add tax fields to indirect_config
ALTER TABLE indirect_config ADD COLUMN IF NOT EXISTS imprevistos_pct numeric DEFAULT 3;
ALTER TABLE indirect_config ADD COLUMN IF NOT EXISTS ingresos_brutos_pct numeric DEFAULT 7;
ALTER TABLE indirect_config ADD COLUMN IF NOT EXISTS imp_cheque_pct numeric DEFAULT 1.2;
ALTER TABLE indirect_config ADD COLUMN IF NOT EXISTS iva_pct numeric DEFAULT 21;

-- 5. Formalize columns added manually by Carlos
ALTER TABLE budget_items ADD COLUMN IF NOT EXISTS notas_calculo text;
ALTER TABLE indirect_config ADD COLUMN IF NOT EXISTS beneficio_pct numeric DEFAULT 10;

-- 6. Add expanded total columns to budget_items
ALTER TABLE budget_items ADD COLUMN IF NOT EXISTS impuestos_total numeric DEFAULT 0;
ALTER TABLE budget_items ADD COLUMN IF NOT EXISTS iva_total numeric DEFAULT 0;
ALTER TABLE budget_items ADD COLUMN IF NOT EXISTS total_final numeric DEFAULT 0;

-- 7. Item templates library
CREATE TABLE IF NOT EXISTS item_templates (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id uuid NOT NULL,
    nombre text NOT NULL,
    descripcion text,
    unidad text,
    categoria text,  -- estructura, albañilería, instalaciones, terminaciones, etc.
    recursos jsonb NOT NULL DEFAULT '[]',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_item_templates_org ON item_templates(org_id);
CREATE INDEX IF NOT EXISTS idx_item_templates_cat ON item_templates(org_id, categoria);
