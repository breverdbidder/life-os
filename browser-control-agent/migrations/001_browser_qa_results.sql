-- Browser QA Results Table
-- Stores autonomous browser control checkpoints and test results

CREATE TABLE IF NOT EXISTS browser_qa_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Test context
    preview_url TEXT NOT NULL,
    test_name TEXT,
    workflow_run_id TEXT,
    
    -- Page state (from accessibility tree, NOT screenshots)
    page_title TEXT,
    interactive_elements_count INTEGER,
    accessibility_tree JSONB,
    
    -- Results
    overall_status TEXT CHECK (overall_status IN ('pass', 'fail', 'warning')),
    checkpoints JSONB,  -- Array of checkpoint results
    assertions_passed INTEGER DEFAULT 0,
    assertions_failed INTEGER DEFAULT 0,
    
    -- Errors
    console_errors JSONB,
    console_errors_count INTEGER DEFAULT 0,
    
    -- AI Analysis
    ai_health_score TEXT,  -- good, warning, critical
    ai_accessibility_score INTEGER,
    ai_issues JSONB,
    ai_recommendations JSONB
);

-- Index for querying by URL and status
CREATE INDEX idx_browser_qa_url ON browser_qa_results(preview_url);
CREATE INDEX idx_browser_qa_status ON browser_qa_results(overall_status);
CREATE INDEX idx_browser_qa_created ON browser_qa_results(created_at DESC);

-- RLS policies (if needed)
ALTER TABLE browser_qa_results ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE browser_qa_results IS 'Stores autonomous browser QA results using accessibility tree analysis (no screenshots)';
