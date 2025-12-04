-- Add XGBoost Focus Score columns to daily_metrics
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql

ALTER TABLE daily_metrics 
ADD COLUMN IF NOT EXISTS xgboost_focus_score INTEGER;

ALTER TABLE daily_metrics 
ADD COLUMN IF NOT EXISTS focus_grade TEXT;

ALTER TABLE daily_metrics 
ADD COLUMN IF NOT EXISTS focus_breakdown JSONB;

ALTER TABLE daily_metrics 
ADD COLUMN IF NOT EXISTS focus_insights JSONB;

ALTER TABLE daily_metrics 
ADD COLUMN IF NOT EXISTS productivity_streak INTEGER DEFAULT 0;

-- Verify columns were added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'daily_metrics' 
AND column_name IN ('xgboost_focus_score', 'focus_grade', 'focus_breakdown', 'focus_insights', 'productivity_streak');
