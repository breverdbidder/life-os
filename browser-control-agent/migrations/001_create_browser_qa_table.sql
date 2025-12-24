-- Browser QA Results Table
CREATE TABLE IF NOT EXISTS browser_qa_results (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    interactive_elements_count INTEGER,
    console_errors_count INTEGER,
    console_errors JSONB,
    checkpoints JSONB,
    ai_analysis JSONB,
    overall_status VARCHAR(20),
    accessibility_score INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_browser_qa_timestamp ON browser_qa_results(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_browser_qa_status ON browser_qa_results(overall_status);
