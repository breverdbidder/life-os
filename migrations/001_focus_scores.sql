-- FOCUS SCORES TABLE
-- XGBoost ML-powered daily focus score tracking
-- Created by: Ariel Shapira, Solo Founder - Everest Capital USA

CREATE TABLE IF NOT EXISTS focus_scores (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL DEFAULT 1,
    date DATE NOT NULL UNIQUE,
    score DECIMAL(5,2) NOT NULL,
    grade VARCHAR(2) NOT NULL,
    features JSONB,
    insights JSONB,
    tasks_total INTEGER DEFAULT 0,
    tasks_completed INTEGER DEFAULT 0,
    interventions_count INTEGER DEFAULT 0,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    model_version VARCHAR(50) DEFAULT 'xgboost_v1.0',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast date lookups
CREATE INDEX IF NOT EXISTS idx_focus_scores_date ON focus_scores(date DESC);
CREATE INDEX IF NOT EXISTS idx_focus_scores_user ON focus_scores(user_id, date DESC);

-- Enable RLS
ALTER TABLE focus_scores ENABLE ROW LEVEL SECURITY;

-- Policy for authenticated access
CREATE POLICY "Enable all for authenticated users" ON focus_scores
    FOR ALL USING (true) WITH CHECK (true);

-- Grant access
GRANT ALL ON focus_scores TO anon, authenticated;
GRANT USAGE, SELECT ON SEQUENCE focus_scores_id_seq TO anon, authenticated;

-- Insert initial test score
INSERT INTO focus_scores (date, score, grade, features, insights, tasks_total, tasks_completed)
VALUES (
    CURRENT_DATE,
    78.5,
    'B+',
    '{"completion_rate": 0.75, "focus_quality": 0.8, "context_switches": 0.6, "intervention_response": 1.0, "productive_hours": 0.7, "streak_bonus": 0.28, "abandonment_rate": 0.85}',
    '["✅ Good task completion today!", "🔥 2-day focus streak!"]',
    8,
    6
) ON CONFLICT (date) DO UPDATE SET
    score = EXCLUDED.score,
    grade = EXCLUDED.grade,
    features = EXCLUDED.features,
    insights = EXCLUDED.insights,
    calculated_at = NOW();

-- Also update the view name to use FOCUS instead of ADHD
DROP VIEW IF EXISTS v_adhd_daily_summary;
CREATE OR REPLACE VIEW v_focus_daily_summary AS
SELECT 
    fs.date,
    fs.score,
    fs.grade,
    fs.features,
    fs.insights,
    dm.tasks_completed,
    dm.tasks_abandoned,
    dm.completion_rate,
    dm.context_switches,
    dm.intervention_count
FROM focus_scores fs
LEFT JOIN daily_metrics dm ON fs.date = dm.date::date
ORDER BY fs.date DESC;
