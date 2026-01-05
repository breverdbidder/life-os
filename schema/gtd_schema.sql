-- ============================================
-- GTD SYSTEM SCHEMA FOR LIFE OS
-- Integrated with existing activities tracking
-- ============================================

-- INBOX: Unprocessed items
CREATE TABLE IF NOT EXISTS gtd_inbox (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    captured_at TIMESTAMPTZ DEFAULT NOW(),
    source TEXT, -- email, voice, quick_capture, brain_dump
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMPTZ,
    notes TEXT
);

-- NEXT ACTIONS: Actionable tasks with contexts
CREATE TABLE IF NOT EXISTS gtd_next_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action TEXT NOT NULL,
    context TEXT NOT NULL, -- @computer, @phone, @home, @office, @errands, @anywhere, @people:name
    energy_level TEXT CHECK (energy_level IN ('HIGH', 'MEDIUM', 'LOW')),
    estimated_minutes INTEGER,
    priority TEXT CHECK (priority IN ('URGENT', 'HIGH', 'MEDIUM', 'LOW')),
    project_id UUID REFERENCES gtd_projects(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    domain TEXT CHECK (domain IN ('BUSINESS', 'MICHAEL', 'FAMILY', 'PERSONAL')),
    notes TEXT
);

-- PROJECTS: Multi-step outcomes
CREATE TABLE IF NOT EXISTS gtd_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    desired_outcome TEXT NOT NULL,
    domain TEXT CHECK (domain IN ('BUSINESS', 'MICHAEL', 'FAMILY', 'PERSONAL')),
    status TEXT CHECK (status IN ('ACTIVE', 'SOMEDAY', 'COMPLETED', 'ARCHIVED')) DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    next_review_date DATE,
    notes TEXT
);

-- WAITING FOR: Delegated items
CREATE TABLE IF NOT EXISTS gtd_waiting_for (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    what TEXT NOT NULL,
    who TEXT NOT NULL,
    delegated_date DATE DEFAULT CURRENT_DATE,
    follow_up_date DATE,
    received BOOLEAN DEFAULT FALSE,
    received_date TIMESTAMPTZ,
    project_id UUID REFERENCES gtd_projects(id),
    domain TEXT CHECK (domain IN ('BUSINESS', 'MICHAEL', 'FAMILY', 'PERSONAL')),
    notes TEXT
);

-- SOMEDAY/MAYBE: Future possibilities
CREATE TABLE IF NOT EXISTS gtd_someday (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idea TEXT NOT NULL,
    category TEXT, -- travel, learning, projects, experiences, etc.
    domain TEXT CHECK (domain IN ('BUSINESS', 'MICHAEL', 'FAMILY', 'PERSONAL')),
    added_at TIMESTAMPTZ DEFAULT NOW(),
    last_reviewed DATE,
    activated BOOLEAN DEFAULT FALSE,
    activated_as_project_id UUID REFERENCES gtd_projects(id),
    notes TEXT
);

-- CALENDAR: Time/date specific items
CREATE TABLE IF NOT EXISTS gtd_calendar (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    event_date DATE NOT NULL,
    event_time TIME,
    all_day BOOLEAN DEFAULT FALSE,
    event_type TEXT CHECK (event_type IN ('APPOINTMENT', 'DEADLINE', 'REMINDER', 'SHABBAT', 'HOLIDAY')),
    project_id UUID REFERENCES gtd_projects(id),
    completed BOOLEAN DEFAULT FALSE,
    notes TEXT
);

-- REFERENCE: Info to keep (non-actionable)
CREATE TABLE IF NOT EXISTS gtd_reference (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT,
    category TEXT,
    url TEXT,
    file_path TEXT,
    tags TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed TIMESTAMPTZ
);

-- CONTEXTS: User-defined contexts
CREATE TABLE IF NOT EXISTS gtd_contexts (
    context_id TEXT PRIMARY KEY,
    context_name TEXT NOT NULL,
    description TEXT,
    energy_required TEXT CHECK (energy_required IN ('HIGH', 'MEDIUM', 'LOW')),
    location TEXT,
    tools_needed TEXT[],
    active BOOLEAN DEFAULT TRUE
);

-- REVIEWS: Track review completion
CREATE TABLE IF NOT EXISTS gtd_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_type TEXT CHECK (review_type IN ('DAILY', 'WEEKLY', 'MONTHLY')) NOT NULL,
    completed_at TIMESTAMPTZ DEFAULT NOW(),
    duration_minutes INTEGER,
    inbox_items_processed INTEGER,
    projects_reviewed INTEGER,
    next_actions_added INTEGER,
    stress_level INTEGER CHECK (stress_level BETWEEN 1 AND 10),
    feeling_in_control BOOLEAN,
    notes TEXT
);

-- TRIGGER LISTS: Prompt for hidden open loops
CREATE TABLE IF NOT EXISTS gtd_triggers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category TEXT NOT NULL,
    trigger_question TEXT NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER
);

-- ============================================
-- INSERT DEFAULT CONTEXTS
-- ============================================
INSERT INTO gtd_contexts (context_id, context_name, description, energy_required, location) VALUES
('@computer', 'Computer', 'Tasks requiring computer/laptop', 'MEDIUM', 'Home/Office'),
('@phone', 'Phone Calls', 'Phone calls to make', 'MEDIUM', 'Anywhere'),
('@home', 'Home', 'Tasks at home', 'MEDIUM', 'Home'),
('@office', 'Office', 'Tasks at office', 'MEDIUM', 'Office'),
('@errands', 'Errands', 'Out and about tasks', 'MEDIUM', 'Around town'),
('@anywhere', 'Anywhere', 'Can do anywhere', 'LOW', 'Any'),
('@pool', 'Pool/Training', 'Swimming training tasks', 'HIGH', 'Pool'),
('@low_energy', 'Low Energy', 'Simple admin tasks', 'LOW', 'Any')
ON CONFLICT (context_id) DO NOTHING;

-- ============================================
-- INSERT DEFAULT TRIGGER QUESTIONS
-- ============================================
INSERT INTO gtd_triggers (category, trigger_question, sort_order) VALUES
('PROFESSIONAL', 'Projects started but not completed?', 1),
('PROFESSIONAL', 'Commitments made to others?', 2),
('PROFESSIONAL', 'Communications that need responses?', 3),
('BUSINESS', 'Upcoming foreclosure auctions to analyze?', 10),
('BUSINESS', 'BidDeed.AI features to deploy?', 12),
('MICHAEL', 'Meet results to analyze?', 20),
('MICHAEL', 'Recruiting emails to send?', 21),
('PERSONAL', 'Home maintenance needed?', 30),
('PERSONAL', 'Financial tasks pending?', 31),
('FAMILY', 'Upcoming holidays/Shabbat to prepare?', 40)
ON CONFLICT DO NOTHING;

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_next_actions_context ON gtd_next_actions(context);
CREATE INDEX IF NOT EXISTS idx_next_actions_completed ON gtd_next_actions(completed);
CREATE INDEX IF NOT EXISTS idx_projects_status ON gtd_projects(status);
CREATE INDEX IF NOT EXISTS idx_inbox_processed ON gtd_inbox(processed);

-- ============================================
-- VIEWS
-- ============================================
CREATE OR REPLACE VIEW v_gtd_health AS
SELECT
    (SELECT COUNT(*) FROM gtd_inbox WHERE processed = FALSE) as inbox_count,
    (SELECT COUNT(*) FROM gtd_next_actions WHERE completed = FALSE) as active_actions,
    (SELECT COUNT(*) FROM gtd_projects WHERE status = 'ACTIVE') as active_projects,
    (SELECT COUNT(*) FROM gtd_waiting_for WHERE received = FALSE) as active_waiting,
    (SELECT MAX(completed_at) FROM gtd_reviews WHERE review_type = 'WEEKLY') as last_weekly_review;
