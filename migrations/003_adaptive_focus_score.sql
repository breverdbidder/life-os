-- Adaptive Focus Score v2.0 - Schema Migration
-- XGBoost-Powered Life OS Scoring System

-- 1. Time Investments Table
-- Tracks HOW time is spent across domains and activities
CREATE TABLE IF NOT EXISTS time_investments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL DEFAULT 1,
    date DATE NOT NULL,
    domain VARCHAR(20) NOT NULL CHECK (domain IN ('BUSINESS', 'FAMILY', 'MICHAEL', 'PERSONAL')),
    activity_type VARCHAR(30) NOT NULL CHECK (activity_type IN (
        'DRIVING', 'DEEP_WORK', 'MEETING', 'ADMIN', 'SUPPORT', 'LEARNING', 
        'EXERCISE', 'MEAL', 'REST', 'COMMUTE', 'ERRANDS', 'SOCIAL', 'OTHER'
    )),
    minutes INTEGER NOT NULL CHECK (minutes > 0),
    description TEXT,
    location VARCHAR(100),
    value_multiplier DECIMAL(3,2) DEFAULT 1.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_time_investments_date ON time_investments(date DESC);
CREATE INDEX IF NOT EXISTS idx_time_investments_domain ON time_investments(domain);

-- 2. Daily Responsibilities Table
-- Tracks WHAT you committed to vs fulfilled
CREATE TABLE IF NOT EXISTS daily_responsibilities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL DEFAULT 1,
    date DATE NOT NULL,
    domain VARCHAR(20) NOT NULL CHECK (domain IN ('BUSINESS', 'FAMILY', 'MICHAEL', 'PERSONAL')),
    responsibility TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    fulfilled BOOLEAN DEFAULT FALSE,
    deferred BOOLEAN DEFAULT FALSE,
    time_invested INTEGER DEFAULT 0,
    notes TEXT,
    source VARCHAR(30) DEFAULT 'manual', -- 'calendar', 'claude', 'manual'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    fulfilled_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_responsibilities_date ON daily_responsibilities(date DESC);
CREATE INDEX IF NOT EXISTS idx_responsibilities_fulfilled ON daily_responsibilities(fulfilled);

-- 3. Daily Satisfaction Table
-- Training labels for XGBoost - subjective end-of-day rating
CREATE TABLE IF NOT EXISTS daily_satisfaction (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL DEFAULT 1,
    date DATE NOT NULL UNIQUE,
    satisfaction_score INTEGER CHECK (satisfaction_score BETWEEN 1 AND 10),
    energy_level INTEGER CHECK (energy_level BETWEEN 1 AND 10),
    stress_level INTEGER CHECK (stress_level BETWEEN 1 AND 10),
    day_type VARCHAR(30) CHECK (day_type IN (
        'work_day', 'travel_day', 'swim_meet', 'shabbat', 'holiday', 'rest_day', 'mixed'
    )),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_satisfaction_date ON daily_satisfaction(date DESC);

-- 4. Focus ML Models Table
-- Stores trained XGBoost models and their performance
CREATE TABLE IF NOT EXISTS focus_ml_models (
    id SERIAL PRIMARY KEY,
    model_version VARCHAR(20) NOT NULL,
    feature_importance JSONB,
    training_metrics JSONB,
    domain_weights JSONB DEFAULT '{"BUSINESS": 1.0, "FAMILY": 1.0, "MICHAEL": 1.0, "PERSONAL": 1.0}',
    activity_weights JSONB DEFAULT '{"DRIVING": 1.0, "DEEP_WORK": 1.2, "MEETING": 0.8, "SUPPORT": 1.0}',
    trained_on_days INTEGER DEFAULT 0,
    mae DECIMAL(4,2),
    r_squared DECIMAL(4,3),
    trained_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    active BOOLEAN DEFAULT FALSE
);

-- 5. Add day_type to daily_metrics if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'daily_metrics' AND column_name = 'day_type') THEN
        ALTER TABLE daily_metrics ADD COLUMN day_type VARCHAR(30);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'daily_metrics' AND column_name = 'time_invested_total') THEN
        ALTER TABLE daily_metrics ADD COLUMN time_invested_total INTEGER DEFAULT 0;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'daily_metrics' AND column_name = 'responsibilities_fulfilled') THEN
        ALTER TABLE daily_metrics ADD COLUMN responsibilities_fulfilled INTEGER DEFAULT 0;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'daily_metrics' AND column_name = 'responsibilities_total') THEN
        ALTER TABLE daily_metrics ADD COLUMN responsibilities_total INTEGER DEFAULT 0;
    END IF;
END $$;

-- Enable RLS on all new tables
ALTER TABLE time_investments ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_responsibilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_satisfaction ENABLE ROW LEVEL SECURITY;
ALTER TABLE focus_ml_models ENABLE ROW LEVEL SECURITY;

-- Create permissive policies
CREATE POLICY "Enable all on time_investments" ON time_investments FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Enable all on daily_responsibilities" ON daily_responsibilities FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Enable all on daily_satisfaction" ON daily_satisfaction FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Enable all on focus_ml_models" ON focus_ml_models FOR ALL USING (true) WITH CHECK (true);

-- Grant access
GRANT ALL ON time_investments TO anon, authenticated;
GRANT ALL ON daily_responsibilities TO anon, authenticated;
GRANT ALL ON daily_satisfaction TO anon, authenticated;
GRANT ALL ON focus_ml_models TO anon, authenticated;
GRANT USAGE, SELECT ON SEQUENCE time_investments_id_seq TO anon, authenticated;
GRANT USAGE, SELECT ON SEQUENCE daily_responsibilities_id_seq TO anon, authenticated;
GRANT USAGE, SELECT ON SEQUENCE daily_satisfaction_id_seq TO anon, authenticated;
GRANT USAGE, SELECT ON SEQUENCE focus_ml_models_id_seq TO anon, authenticated;

-- Insert initial baseline model
INSERT INTO focus_ml_models (model_version, feature_importance, training_metrics, active)
VALUES (
    'v1.0-baseline',
    '{"responsibility_rate": 0.35, "time_investment": 0.30, "task_completion": 0.20, "context_discipline": 0.15}',
    '{"type": "rule_based", "note": "Initial baseline before XGBoost training"}',
    true
);

