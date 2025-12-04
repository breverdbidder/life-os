-- =====================================================
-- CLAUDE PERFORMANCE MONITORING SYSTEM
-- XGBoost-based self-improvement tracking
-- Created by: Ariel Shapira, Solo Founder
-- =====================================================

-- Table 1: Daily task/action log
CREATE TABLE IF NOT EXISTS claude_performance_log (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    task_type VARCHAR(50) NOT NULL,  -- code, deploy, analysis, document, fix
    description TEXT,
    completed BOOLEAN DEFAULT true,
    first_attempt_success BOOLEAN DEFAULT true,
    followed_pattern BOOLEAN DEFAULT true,
    value_score INTEGER DEFAULT 7 CHECK (value_score >= 1 AND value_score <= 10),
    rework_needed BOOLEAN DEFAULT false,
    mistake_type VARCHAR(100),
    lesson_learned TEXT,
    logged_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 2: Mistake pattern tracking
CREATE TABLE IF NOT EXISTS claude_mistakes (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    mistake_type VARCHAR(100) NOT NULL,
    description TEXT,
    severity INTEGER DEFAULT 5 CHECK (severity >= 1 AND severity <= 10),
    lesson_learned TEXT,
    pattern_id VARCHAR(200),
    logged_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table 3: Daily scores
CREATE TABLE IF NOT EXISTS claude_daily_scores (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    score DECIMAL(5,2) NOT NULL,
    grade VARCHAR(2) NOT NULL,
    features JSONB,
    insights JSONB,
    tasks_count INTEGER DEFAULT 0,
    mistakes_count INTEGER DEFAULT 0,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_claude_perf_date ON claude_performance_log(date DESC);
CREATE INDEX IF NOT EXISTS idx_claude_mistakes_date ON claude_mistakes(date DESC);
CREATE INDEX IF NOT EXISTS idx_claude_mistakes_type ON claude_mistakes(mistake_type);
CREATE INDEX IF NOT EXISTS idx_claude_scores_date ON claude_daily_scores(date DESC);

-- Enable RLS
ALTER TABLE claude_performance_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE claude_mistakes ENABLE ROW LEVEL SECURITY;
ALTER TABLE claude_daily_scores ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Enable all for claude_performance_log" ON claude_performance_log FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Enable all for claude_mistakes" ON claude_mistakes FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Enable all for claude_daily_scores" ON claude_daily_scores FOR ALL USING (true) WITH CHECK (true);

-- Grant access
GRANT ALL ON claude_performance_log TO anon, authenticated;
GRANT ALL ON claude_mistakes TO anon, authenticated;
GRANT ALL ON claude_daily_scores TO anon, authenticated;
GRANT USAGE, SELECT ON SEQUENCE claude_performance_log_id_seq TO anon, authenticated;
GRANT USAGE, SELECT ON SEQUENCE claude_mistakes_id_seq TO anon, authenticated;
GRANT USAGE, SELECT ON SEQUENCE claude_daily_scores_id_seq TO anon, authenticated;
