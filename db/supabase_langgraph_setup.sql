-- ============================================================
-- LANGGRAPH ORCHESTRATION TABLES FOR BIDDEED.AI
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard
-- ============================================================

-- Table: orchestrated_tasks
-- Stores Task Specification Format (TSF) for Claude Code Mobile consumption
CREATE TABLE IF NOT EXISTS orchestrated_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id TEXT UNIQUE NOT NULL,
    langgraph_node TEXT NOT NULL,
    repository TEXT NOT NULL,
    priority TEXT DEFAULT 'P2' CHECK (priority IN ('P0', 'P1', 'P2', 'P3')),
    task_type TEXT DEFAULT 'code_fix' CHECK (task_type IN ('code_fix', 'feature', 'refactor', 'test', 'docs', 'deploy')),
    
    -- Task Specification Format (TSF)
    tsf JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- Execution state
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'assigned', 'in_progress', 'success', 'failed', 'blocked', 'needs_review')),
    assigned_to TEXT CHECK (assigned_to IN ('claude_code_mobile', 'claude_code_web', 'claude_code_cli', NULL)),
    
    -- Results
    pr_url TEXT,
    pr_number INTEGER,
    execution_log JSONB DEFAULT '[]'::jsonb,
    error_message TEXT,
    
    -- Dependencies
    depends_on TEXT[] DEFAULT '{}',
    blocks TEXT[] DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    assigned_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Feedback tracking
    feedback_sent BOOLEAN DEFAULT FALSE,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3
);

-- Table: langgraph_state
-- Stores workflow state for LangGraph orchestration
CREATE TABLE IF NOT EXISTS langgraph_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id TEXT UNIQUE NOT NULL,
    workflow_name TEXT NOT NULL,
    
    -- State management
    current_state JSONB NOT NULL DEFAULT '{}'::jsonb,
    current_node TEXT,
    
    -- Node tracking
    completed_nodes TEXT[] DEFAULT '{}',
    pending_nodes TEXT[] DEFAULT '{}',
    failed_nodes TEXT[] DEFAULT '{}',
    
    -- Human checkpoints
    human_checkpoints TEXT[] DEFAULT '{}',
    awaiting_human BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    total_tasks INTEGER DEFAULT 0,
    completed_tasks INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_transition_at TIMESTAMPTZ
);

-- Table: langgraph_transitions
-- Logs all state transitions for debugging
CREATE TABLE IF NOT EXISTS langgraph_transitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id TEXT NOT NULL REFERENCES langgraph_state(workflow_id),
    from_node TEXT,
    to_node TEXT NOT NULL,
    trigger TEXT NOT NULL,  -- 'success', 'failure', 'timeout', 'human_approved', 'human_rejected'
    transition_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_orchestrated_tasks_status ON orchestrated_tasks(status);
CREATE INDEX IF NOT EXISTS idx_orchestrated_tasks_priority ON orchestrated_tasks(priority);
CREATE INDEX IF NOT EXISTS idx_orchestrated_tasks_repository ON orchestrated_tasks(repository);
CREATE INDEX IF NOT EXISTS idx_langgraph_state_workflow ON langgraph_state(workflow_id);
CREATE INDEX IF NOT EXISTS idx_langgraph_transitions_workflow ON langgraph_transitions(workflow_id);

-- Enable RLS
ALTER TABLE orchestrated_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE langgraph_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE langgraph_transitions ENABLE ROW LEVEL SECURITY;

-- Policies (allow all for service role)
CREATE POLICY "Service role full access orchestrated_tasks" ON orchestrated_tasks FOR ALL USING (true);
CREATE POLICY "Service role full access langgraph_state" ON langgraph_state FOR ALL USING (true);
CREATE POLICY "Service role full access langgraph_transitions" ON langgraph_transitions FOR ALL USING (true);

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_langgraph_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for langgraph_state
DROP TRIGGER IF EXISTS update_langgraph_state_timestamp ON langgraph_state;
CREATE TRIGGER update_langgraph_state_timestamp
    BEFORE UPDATE ON langgraph_state
    FOR EACH ROW
    EXECUTE FUNCTION update_langgraph_timestamp();

-- Insert initial workflow for BidDeed.AI
INSERT INTO langgraph_state (workflow_id, workflow_name, current_state, pending_nodes)
VALUES (
    'biddeed-main-workflow',
    'BidDeed.AI Main Development Workflow',
    '{"phase": "initialization", "version": "1.0"}'::jsonb,
    ARRAY['fix_beca_antibot', 'enhance_lien_discovery', 'add_swim_tracking', 'update_landing_how_it_works', 'init_spd_discovery']
) ON CONFLICT (workflow_id) DO UPDATE SET updated_at = NOW();

SELECT 'LangGraph tables created successfully!' as result;
