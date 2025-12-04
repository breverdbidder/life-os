-- Life OS V3.4: XGBoost Focus Score Columns
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql

-- Add XGBoost Focus Score columns to daily_metrics
ALTER TABLE daily_metrics 
  ADD COLUMN IF NOT EXISTS focus_score INTEGER DEFAULT 50,
  ADD COLUMN IF NOT EXISTS focus_grade VARCHAR(5) DEFAULT 'C',
  ADD COLUMN IF NOT EXISTS focus_breakdown JSONB DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS average_complexity FLOAT DEFAULT 5,
  ADD COLUMN IF NOT EXISTS time_efficiency FLOAT DEFAULT 1.0,
  ADD COLUMN IF NOT EXISTS productivity_streak INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();

-- Create index for faster date lookups with focus_score
CREATE INDEX IF NOT EXISTS idx_daily_metrics_date_focus 
  ON daily_metrics(date, focus_score);

-- Verify columns were added
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'daily_metrics' 
  AND column_name IN ('focus_score', 'focus_grade', 'focus_breakdown', 'productivity_streak')
ORDER BY ordinal_position;
