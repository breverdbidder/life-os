-- Life OS Shopping Lists Table
-- Migration: 20241223_create_shopping_lists.sql

CREATE TABLE IF NOT EXISTS shopping_lists (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  title TEXT NOT NULL,
  items JSONB NOT NULL DEFAULT '[]',
  instacart_url TEXT,
  store TEXT DEFAULT 'any' CHECK (store IN ('costco', 'walmart', 'any')),
  status TEXT DEFAULT 'created' CHECK (status IN ('created', 'sent', 'completed', 'cancelled')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  notes TEXT
);

-- Index for fast lookups
CREATE INDEX idx_shopping_lists_created_at ON shopping_lists(created_at DESC);
CREATE INDEX idx_shopping_lists_store ON shopping_lists(store);
CREATE INDEX idx_shopping_lists_status ON shopping_lists(status);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_shopping_lists_updated_at
  BEFORE UPDATE ON shopping_lists
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- RLS Policies (adjust based on your auth setup)
ALTER TABLE shopping_lists ENABLE ROW LEVEL SECURITY;

-- Allow all operations for authenticated users (adjust as needed)
CREATE POLICY "Allow all for service role" ON shopping_lists
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Comments for documentation
COMMENT ON TABLE shopping_lists IS 'Life OS shopping lists with Instacart integration';
COMMENT ON COLUMN shopping_lists.items IS 'JSONB array of shopping items with name, quantity, unit, brand';
COMMENT ON COLUMN shopping_lists.instacart_url IS 'Generated Instacart shopping list URL';
