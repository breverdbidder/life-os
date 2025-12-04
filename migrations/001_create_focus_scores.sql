-- LIFE OS: XGBoost Focus Scores Table
-- Run in Supabase SQL Editor: https://supabase.com/dashboard/project/mocerqjnksmhcjzxrewo/sql
-- Created by: Ariel Shapira, Solo Founder - Everest Capital USA

-- Create focus_scores table
CREATE TABLE IF NOT EXISTS focus_scores (
    id SERIAL PRIMARY KEY,
    user_id INTEGER DEFAULT 1,
    date DATE NOT NULL,
    score FLOAT NOT NULL DEFAULT 50,
    grade VARCHAR(5) DEFAULT 'C',
    features JSONB DEFAULT '{}',
    insights JSONB DEFAULT '[]',
    tasks_total INTEGER DEFAULT 0,
    tasks_completed INTEGER DEFAULT 0,
    interventions_count INTEGER DEFAULT 0,
    calculated_at TIMESTAMP DEFAULT NOW(),
    model_version VARCHAR(50) DEFAULT 'xgboost_v1.0',
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Unique constraint on date per user
    CONSTRAINT unique_focus_score_per_day UNIQUE (user_id, date)
);

-- Create index for fast date lookups
CREATE INDEX IF NOT EXISTS idx_focus_scores_date 
    ON focus_scores(date DESC);

CREATE INDEX IF NOT EXISTS idx_focus_scores_user_date 
    ON focus_scores(user_id, date DESC);

-- Enable RLS (Row Level Security)
ALTER TABLE focus_scores ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations for authenticated users
CREATE POLICY "Allow all for authenticated" ON focus_scores
    FOR ALL USING (true) WITH CHECK (true);

-- Verify table was created
SELECT 
    column_name, 
    data_type, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'focus_scores'
ORDER BY ordinal_position;
