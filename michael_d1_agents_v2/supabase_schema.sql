-- Michael D1 Pathway V2.2 - Supabase Schema
-- ==========================================
-- Integrated with LangGraph Orchestrator + MCP Bridge

-- Personal Best Times (MCP-Scraped)
CREATE TABLE IF NOT EXISTS personal_best_times (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    swimmer_name TEXT NOT NULL,
    event TEXT NOT NULL,
    time DECIMAL(6,2) NOT NULL,
    date_achieved DATE,
    meet_name TEXT,
    meet_location TEXT,
    swim_club TEXT,
    high_school TEXT,
    competition_level TEXT DEFAULT 'club', -- club, high_school, usa_swimming
    source TEXT DEFAULT 'swimcloud', -- swimcloud, usa_swimming, manual
    verified BOOLEAN DEFAULT true,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(swimmer_name, event)
);

-- Meet Schedule
CREATE TABLE IF NOT EXISTS michael_meets (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    meet_name TEXT NOT NULL,
    meet_date DATE NOT NULL,
    location TEXT,
    events TEXT[], -- Array of events Michael is swimming
    competitors TEXT[], -- Array of competitor names
    prep_doc_generated BOOLEAN DEFAULT false,
    prep_doc_url TEXT,
    scrape_triggered BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent Execution Log
CREATE TABLE IF NOT EXISTS agent_executions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    agent_name TEXT NOT NULL,
    query TEXT,
    context JSONB,
    response JSONB,
    mcp_servers_used TEXT[],
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- MCP Tool Calls
CREATE TABLE IF NOT EXISTS mcp_tool_calls (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    server_type TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    parameters JSONB,
    result JSONB,
    success BOOLEAN,
    error TEXT,
    latency_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- UF 2027 Progress Tracking
CREATE TABLE IF NOT EXISTS uf_progress (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    event TEXT NOT NULL,
    current_pb DECIMAL(6,2),
    uf_target DECIMAL(6,2),
    gap DECIMAL(6,2),
    projected_achievement_date DATE,
    confidence DECIMAL(3,2),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Competitor Profiles
CREATE TABLE IF NOT EXISTS competitor_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    swimmer_name TEXT NOT NULL UNIQUE,
    swim_club TEXT,
    high_school TEXT,
    graduation_year INTEGER,
    tracked BOOLEAN DEFAULT true,
    threat_level TEXT DEFAULT 'medium', -- low, medium, high
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- College Visit Plans (AI Travel Agent MCP)
CREATE TABLE IF NOT EXISTS college_visits (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    school TEXT NOT NULL,
    visit_date DATE,
    status TEXT DEFAULT 'planned', -- planned, confirmed, completed, cancelled
    itinerary JSONB,
    chabad_contact JSONB,
    coach_meeting BOOLEAN DEFAULT false,
    swim_facility_tour BOOLEAN DEFAULT false,
    academic_meeting BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Nutrition Plans (AI Nutrition MCP)
CREATE TABLE IF NOT EXISTS nutrition_plans (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    plan_date DATE NOT NULL,
    day_type TEXT NOT NULL, -- keto, shabbat
    meals JSONB,
    total_macros JSONB,
    meet_specific BOOLEAN DEFAULT false,
    meet_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Michael's Swim Times History
CREATE TABLE IF NOT EXISTS michael_swim_times (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    event TEXT NOT NULL,
    time DECIMAL(6,2) NOT NULL,
    meet_name TEXT,
    meet_date DATE,
    is_pb BOOLEAN DEFAULT false,
    splits JSONB,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_pbt_swimmer ON personal_best_times(swimmer_name);
CREATE INDEX IF NOT EXISTS idx_pbt_event ON personal_best_times(event);
CREATE INDEX IF NOT EXISTS idx_meets_date ON michael_meets(meet_date);
CREATE INDEX IF NOT EXISTS idx_agent_exec_agent ON agent_executions(agent_name);
CREATE INDEX IF NOT EXISTS idx_mcp_calls_server ON mcp_tool_calls(server_type);

-- Insert initial competitor profiles
INSERT INTO competitor_profiles (swimmer_name, swim_club, high_school, graduation_year, threat_level)
VALUES 
    ('Bastian Soto', 'Brevard Aquatic Club', 'Eau Gallie HS', 2027, 'high'),
    ('Aaron Gordon', 'Melbourne Swim Team', 'Melbourne HS', 2027, 'medium')
ON CONFLICT (swimmer_name) DO NOTHING;

-- Insert upcoming meets
INSERT INTO michael_meets (meet_name, meet_date, location, events, competitors)
VALUES 
    ('Harry Meisel Championships', '2025-12-13', 'Melbourne Aquatic Center', 
     ARRAY['100 Free', '50 Free', '100 Fly'], ARRAY['Bastian Soto', 'Aaron Gordon']),
    ('Winter Juniors', '2025-12-19', 'Austin, TX', 
     ARRAY['100 Free', '50 Free', '200 Free'], ARRAY[]),
    ('Senior Champs', '2026-01-18', 'Orlando, FL', 
     ARRAY['100 Free', '50 Free', '100 Fly', '100 Back'], ARRAY['Bastian Soto'])
ON CONFLICT DO NOTHING;

-- Insert UF targets
INSERT INTO uf_progress (event, current_pb, uf_target, gap)
VALUES 
    ('50 Free', 23.22, 20.50, 2.72),
    ('100 Free', 50.82, 45.00, 5.82),
    ('100 Fly', 57.21, 50.00, 7.21),
    ('100 Back', 61.62, 52.00, 9.62)
ON CONFLICT DO NOTHING;
