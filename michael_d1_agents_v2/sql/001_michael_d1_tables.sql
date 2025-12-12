-- Michael D1 Pathway V2.2 - Supabase Tables
-- ==========================================

-- Personal Best Times (MCP-scraped data)
CREATE TABLE IF NOT EXISTS personal_best_times (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    swimmer_name TEXT NOT NULL,
    event TEXT NOT NULL,
    time_seconds DECIMAL(10,2) NOT NULL,
    date_achieved DATE NOT NULL,
    meet_name TEXT NOT NULL,
    meet_location TEXT,
    swim_club TEXT,
    high_school TEXT,
    competition_level TEXT DEFAULT 'club',
    source TEXT DEFAULT 'swimcloud',
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    verified BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(swimmer_name, event)
);

CREATE INDEX IF NOT EXISTS idx_pb_swimmer ON personal_best_times(swimmer_name);
CREATE INDEX IF NOT EXISTS idx_pb_event ON personal_best_times(event);

-- UF 2027 Progress Tracking
CREATE TABLE IF NOT EXISTS uf_2027_progress (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    event TEXT NOT NULL UNIQUE,
    target_time DECIMAL(10,2) NOT NULL,
    current_pb DECIMAL(10,2),
    gap_seconds DECIMAL(10,2),
    pb_date DATE,
    pb_meet TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert UF targets
INSERT INTO uf_2027_progress (event, target_time, current_pb, gap_seconds, pb_date, pb_meet)
VALUES 
    ('50 Free', 20.50, 23.22, 2.72, '2025-11-15', 'Senior Champs'),
    ('100 Free', 45.00, 50.82, 5.82, '2025-11-15', 'Senior Champs'),
    ('100 Fly', 50.00, 57.21, 7.21, '2025-10-20', 'Fall Classic'),
    ('100 Back', 52.00, 61.62, 9.62, '2025-10-20', 'Fall Classic')
ON CONFLICT (event) DO UPDATE SET
    current_pb = EXCLUDED.current_pb,
    gap_seconds = EXCLUDED.gap_seconds,
    updated_at = NOW();

-- Tracked Competitors
CREATE TABLE IF NOT EXISTS tracked_competitors (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    swimmer_name TEXT NOT NULL UNIQUE,
    swim_club TEXT,
    high_school TEXT,
    graduation_year INTEGER,
    events TEXT[],
    threat_level TEXT DEFAULT 'medium',
    last_scraped TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO tracked_competitors (swimmer_name, swim_club, high_school, graduation_year, events, threat_level)
VALUES
    ('Bastian Soto', 'Brevard Aquatic Club', 'Eau Gallie HS', 2027, ARRAY['50 Free', '100 Free', '100 Fly'], 'high'),
    ('Aaron Gordon', 'Melbourne Swim Team', 'Melbourne HS', 2027, ARRAY['50 Free', '100 Free', '100 Back'], 'medium')
ON CONFLICT (swimmer_name) DO NOTHING;

-- MCP Tool Calls Log
CREATE TABLE IF NOT EXISTS mcp_tool_calls (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    server_type TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    parameters JSONB,
    result JSONB,
    success BOOLEAN DEFAULT true,
    latency_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Meet Schedule
CREATE TABLE IF NOT EXISTS michael_meet_schedule (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    meet_name TEXT NOT NULL,
    meet_date DATE NOT NULL,
    meet_location TEXT,
    events TEXT[],
    competitors TEXT[],
    prep_document_generated BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
