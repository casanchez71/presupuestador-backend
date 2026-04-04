-- Migration 002: Item-level audit trail for manual edits
-- Tracks every field-level change to budget items for accountability

CREATE TABLE IF NOT EXISTS item_audits (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    item_id UUID NOT NULL REFERENCES budget_items(id) ON DELETE CASCADE,
    budget_id UUID NOT NULL,
    org_id UUID NOT NULL,
    user_id TEXT NOT NULL,
    field TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    source TEXT DEFAULT 'manual_edit',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audits_item ON item_audits(item_id);
CREATE INDEX IF NOT EXISTS idx_audits_budget ON item_audits(budget_id);
CREATE INDEX IF NOT EXISTS idx_audits_org ON item_audits(org_id);
