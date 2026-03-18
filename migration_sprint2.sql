-- MIGRACIÓN SPRINT 2
-- Ejecutar en: Supabase SQL Editor

-- Agregar columnas indirecto y total_con_indirecto a budget_items
ALTER TABLE budget_items
  ADD COLUMN IF NOT EXISTS indirecto numeric DEFAULT 0,
  ADD COLUMN IF NOT EXISTS total_con_indirecto numeric DEFAULT 0;
