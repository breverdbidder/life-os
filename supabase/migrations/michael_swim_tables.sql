-- Michael Shapira D1 Swimming Tracker
-- Supabase Schema Migration
-- Author: Ariel Shapira, Everest Capital USA
-- Date: 2025-12-12

-- ============================================
-- TABLE: michael_swim_times
-- Stores all swim times scraped from SwimCloud
-- ============================================

CREATE TABLE IF NOT EXISTS michael_swim_times (
    id BIGSERIAL PRIMARY KEY,
    swimmer_name TEXT NOT NULL DEFAULT 'Michael Shapira',
    event TEXT NOT NULL,
    time_seconds NUMERIC(10, 2) NOT NULL,
    time_str TEXT,
    meet_name TEXT,
    meet_date DATE,
    pool_type TEXT DEFAULT 'SCY' CHECK (pool_type IN ('SCY', 'SCM', 'LCM')),
    improvement NUMERIC(6, 2) DEFAULT 0,
    is_personal_best BOOLEAN DEFAULT FALSE,
    source TEXT DEFAULT 'swimcloud',
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint to prevent duplicates
    UNIQUE(swimmer_name, event, time_seconds, meet_date)
);

-- Index for fast queries
CREATE INDEX IF NOT EXISTS idx_swim_times_event ON michael_swim_times(event);
CREATE INDEX IF NOT EXISTS idx_swim_times_date ON michael_swim_times(scraped_at DESC);

-- ============================================
-- TABLE: michael_d1_analysis
-- Stores D1 recruiting analysis snapshots
-- ============================================

CREATE TABLE IF NOT EXISTS michael_d1_analysis (
    id BIGSERIAL PRIMARY KEY,
    analysis_date DATE NOT NULL DEFAULT CURRENT_DATE,
    overall_d1_score NUMERIC(5, 1),
    recommendation TEXT,
    
    -- Event-specific data (JSON)
    event_analysis JSONB,
    
    -- Best times at analysis time
    best_50_free NUMERIC(6, 2),
    best_100_free NUMERIC(6, 2),
    best_200_free NUMERIC(6, 2),
    best_100_fly NUMERIC(6, 2),
    best_100_back NUMERIC(6, 2),
    
    -- Recruiting metrics
    power_index NUMERIC(5, 2),
    fl_zone_events_qualified INTEGER DEFAULT 0,
    d1_tier TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- One analysis per day
    UNIQUE(analysis_date)
);

-- ============================================
-- TABLE: michael_meets
-- Stores meet schedule and results
-- ============================================

CREATE TABLE IF NOT EXISTS michael_meets (
    id BIGSERIAL PRIMARY KEY,
    meet_name TEXT NOT NULL,
    meet_date DATE NOT NULL,
    meet_location TEXT,
    pool_type TEXT DEFAULT 'SCY',
    
    -- Events entered
    events_entered TEXT[],
    
    -- Results (populated after meet)
    results JSONB,
    total_time_drops NUMERIC(6, 2),
    personal_bests_achieved INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(meet_name, meet_date)
);

-- ============================================
-- TABLE: michael_recruiting
-- D1 recruiting outreach tracking
-- ============================================

CREATE TABLE IF NOT EXISTS michael_recruiting (
    id BIGSERIAL PRIMARY KEY,
    school_name TEXT NOT NULL,
    conference TEXT,
    division TEXT DEFAULT 'D1',
    coach_name TEXT,
    coach_email TEXT,
    
    -- Contact tracking
    initial_contact_date DATE,
    last_contact_date DATE,
    contact_count INTEGER DEFAULT 0,
    
    -- Status
    status TEXT DEFAULT 'prospect' CHECK (status IN (
        'prospect', 'contacted', 'responded', 'interested', 
        'visit_scheduled', 'visited', 'offer', 'committed', 'declined'
    )),
    
    -- Notes
    notes TEXT,
    
    -- Times they're looking for
    target_times JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(school_name)
);

-- ============================================
-- VIEW: michael_best_times
-- Current personal bests by event
-- ============================================

CREATE OR REPLACE VIEW michael_best_times AS
SELECT 
    event,
    MIN(time_seconds) as best_time,
    MIN(time_str) FILTER (WHERE time_seconds = (
        SELECT MIN(time_seconds) FROM michael_swim_times t2 
        WHERE t2.event = michael_swim_times.event
    )) as best_time_str,
    MAX(meet_date) as last_swam,
    COUNT(*) as total_swims
FROM michael_swim_times
WHERE swimmer_name = 'Michael Shapira'
GROUP BY event
ORDER BY event;

-- ============================================
-- FUNCTION: Calculate D1 tier for a time
-- ============================================

CREATE OR REPLACE FUNCTION calculate_d1_tier(event_name TEXT, time_seconds NUMERIC)
RETURNS TEXT AS $$
DECLARE
    a_cut NUMERIC;
    b_cut NUMERIC;
    consider_cut NUMERIC;
BEGIN
    -- D1 cuts by event (approximate mid-major standards)
    CASE event_name
        WHEN '50 Free' THEN a_cut := 20.5; b_cut := 21.5; consider_cut := 22.5;
        WHEN '100 Free' THEN a_cut := 45.0; b_cut := 47.0; consider_cut := 49.0;
        WHEN '200 Free' THEN a_cut := 100.0; b_cut := 105.0; consider_cut := 110.0;
        WHEN '100 Fly' THEN a_cut := 50.0; b_cut := 52.0; consider_cut := 54.0;
        WHEN '100 Back' THEN a_cut := 50.0; b_cut := 52.0; consider_cut := 55.0;
        ELSE RETURN 'UNKNOWN_EVENT';
    END CASE;
    
    IF time_seconds <= a_cut THEN RETURN 'TIER_1_A_CUT';
    ELSIF time_seconds <= b_cut THEN RETURN 'TIER_2_B_CUT';
    ELSIF time_seconds <= consider_cut THEN RETURN 'TIER_3_CONSIDER';
    ELSE RETURN 'TIER_4_DEVELOPING';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Insert initial data (Michael's known times)
-- ============================================

INSERT INTO michael_swim_times (swimmer_name, event, time_seconds, time_str, pool_type, source, scraped_at)
VALUES 
    ('Michael Shapira', '50 Free', 21.86, '21.86', 'SCY', 'manual', NOW()),
    ('Michael Shapira', '100 Free', 48.80, '48.80', 'SCY', 'manual', NOW()),
    ('Michael Shapira', '100 Back', 61.62, '1:01.62', 'SCY', 'manual', NOW()),
    ('Michael Shapira', '50 Fly', 25.79, '25.79', 'SCY', 'manual', NOW())
ON CONFLICT DO NOTHING;

-- Insert initial D1 analysis
INSERT INTO michael_d1_analysis (
    analysis_date,
    overall_d1_score,
    recommendation,
    best_50_free,
    best_100_free,
    best_100_back,
    d1_tier,
    fl_zone_events_qualified
)
VALUES (
    CURRENT_DATE,
    62.5,
    'D1 POTENTIAL - Focus on time drops, target mid-major D1',
    21.86,
    48.80,
    61.62,
    'TIER_3_CONSIDER',
    1  -- 50 Free qualified for FL Zone
)
ON CONFLICT (analysis_date) DO UPDATE SET
    overall_d1_score = EXCLUDED.overall_d1_score,
    recommendation = EXCLUDED.recommendation;

-- Grant permissions (for Supabase)
GRANT ALL ON michael_swim_times TO authenticated;
GRANT ALL ON michael_d1_analysis TO authenticated;
GRANT ALL ON michael_meets TO authenticated;
GRANT ALL ON michael_recruiting TO authenticated;
GRANT SELECT ON michael_best_times TO authenticated;
